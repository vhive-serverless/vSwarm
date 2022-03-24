// MIT License

// Copyright (c) 2022 EASE lab

// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

// Include process module
const process = require('process');
const GRPC_PORT = process.env.GRPC_PORT || '50051'


var PROTO_PATH = __dirname + '/helloworld.proto';  // '/../proto/helloworld.proto';

var grpc = require('@grpc/grpc-js');
var protoLoader = require('@grpc/proto-loader');
var packageDefinition = protoLoader.loadSync(
    PROTO_PATH,
    {keepCase: true,
     longs: String,
     enums: String,
     defaults: true,
     oneofs: true
    });
var hello_proto = grpc.loadPackageDefinition(packageDefinition).helloworld;




// https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-use-lambda-authorizer.html#api-gateway-lambda-authorizer-create
// A simple token-based authorizer example to demonstrate how to use an authorization token 
// to allow or deny a request. In this example, the caller named 'user' is allowed to invoke 
// a request if the client-supplied token value is 'allow'. The caller is not allowed to invoke 
// the request if the token value is 'deny'. If the token value is 'unauthorized' or an empty
// string, the authorizer function returns an HTTP 401 status code. For any other token value, 
// the authorizer returns an HTTP 500 status code. 
// Note that token values are case-sensitive.

// Help function to generate an IAM policy
var generatePolicy = function(principalId, effect, resource) {
  var authResponse = {};
  
  authResponse.principalId = principalId;
  if (effect && resource) {
      var policyDocument = {};
      policyDocument.Version = '2012-10-17'; 
      policyDocument.Statement = [];
      var statementOne = {};
      statementOne.Action = 'execute-api:Invoke'; 
      statementOne.Effect = effect;
      statementOne.Resource = resource;
      policyDocument.Statement[0] = statementOne;
      authResponse.policyDocument = policyDocument;
  }
  
  // Optional output with custom properties of the String, Number or Boolean type.
  authResponse.context = {
      "stringKey": "stringval",
      "numberKey": 123,
      "booleanKey": true
  };
  return authResponse;
}

/**
 * Implements the SayHello RPC method.
 */
function sayHello(call, callback) {
  
  var token = call.request.name;
  var fakeMethodArn = "arn:aws:execute-api:{regionId}:{accountId}:{apiId}/{stage}/{httpVerb}/[{resource}/[{child-resources}]]";
  var msg1, ret;
  switch (token) {
      case '.f2':
          ret = generatePolicy('user', 'Allow', fakeMethodArn);
          msg1 = 'auth.f2';
          break;
      default:  // case '.f1':
          ret = generatePolicy('user', 'Deny', fakeMethodArn);
          msg1 = 'auth.f1';
          break;
      // case 'unauthorized':
      //     callback("Unauthorized");   // Return a 401 Unauthorized response
      //     break;
      // default:
      //     callback("Error: Invalid token"); // Return a 500 Invalid token response
  }

  var gid = process.getgid();
  var msg = `Hello: this is: ${gid}. Invoke NodeJS.${msg1}. Additional message: ${ret.context.stringKey}`;
  callback(null, {message: msg});
}

/**
 * Starts an RPC server that receives requests for the Greeter service at the
 * sample server port
 */
function main() {
  var server = new grpc.Server();
  server.addService(hello_proto.Greeter.service, {sayHello: sayHello});
  address = '0.0.0.0:' + GRPC_PORT
  server.bindAsync(
    address,
    grpc.ServerCredentials.createInsecure(),
    (err, port) => {
      process.stdout.write(`Server started on ${address}`);
      server.start();
    }
  );
}

main();

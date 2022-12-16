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
const tracing = require('tracing')

var PROTO_PATH = __dirname + '/auth.proto';  // '/../proto/auth.proto';

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
var auth_proto = grpc.loadPackageDefinition(packageDefinition).auth;

var LAMBDA = ( typeof(process.env.IS_LAMBDA) == "string" &&
  ["true", "yes", "1"].indexOf(process.env.IS_LAMBDA).toLowerCase() != -1)

/**
 * Argument parsing
 */
 function parseArgs() {

  var { argv } = require("yargs")
    .scriptName("server")
    .usage("Usage: $0 --addr <IP> --port <PORT> --zipkin <ZIPKIN URL>")
    .example(
      "$0 -p 50051",
      "Starts AES gRPC server on localhost:50051"
    )
    .option("a", {
      alias: "addr", type: "string",
      describe: "IP address",
    })
    .option("p", {
      alias: "port", type: "string",
      describe: "Port the server listen to",
    })
    .option("z", {
      alias: "zipkin", type: "string",
      describe: "Zipkin URL",
    })
    .describe("help", "Show help.") // Override --help usage message.
    .describe("version", "Show version number.") // Override --version usage message.
    .epilog("copyright 2022");

  var addr = "0.0.0.0";
  var port = "50051";
  var zipkin = "http://localhost:9411/api/v2/spans";

  if ('addr' in argv) { addr = argv.addr; }
  if ('port' in argv) { port = argv.port; }
  if ('zipkin' in argv) { zipkin = argv.zipkin; }

  return [addr, port, zipkin];
}





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

  let span;
  if (tracing.IsTracingEnabled()) {
    span = new tracing.Span()
  }

  var token = call.request.name;
  var fakeMethodArn = "arn:aws:execute-api:{regionId}:{accountId}:{apiId}/{stage}/{httpVerb}/[{resource}/[{child-resources}]]";
  var msg1, ret;
  switch (token) {
      case 'allow':
        ret = generatePolicy('user', 'Allow', fakeMethodArn);
        msg1 = JSON.stringify(ret, null, 2);
        break;
      case 'deny':
        ret = generatePolicy('user', 'Deny', fakeMethodArn);
        msg1 = JSON.stringify(ret, null, 2);
        break;
      case 'unauthorized':
        msg1 = "Unauthorized";   // Return a 401 Unauthorized response
        break;
      default:
        msg1 = "Error: Invalid token"; // Return a 500 Invalid token response
  }
  var msg = `fn: Auth | token: ${token} | resp: ${msg1} | runtime: nodejs`;

  if (tracing.IsTracingEnabled()) {
    span.addEvent(msg);
    span.end();
  }

  callback(null, {message: msg});
}
/**
 * Starts an RPC server that receives requests for the Greeter service at the
 * sample server port
 */
function main() {
  if (!LAMBDA) {
    const [addr, port, zipkin] = parseArgs();

    if (tracing.IsTracingEnabled()) {
      process.stdout.write(`Tracing enabled\n`);
      tracing.InitTracer('auth-nodejs-server', zipkin);
    } else {
      process.stdout.write(`Tracing disabled\n`);
    }

    var server = new grpc.Server();
    server.addService(auth_proto.Greeter.service, {sayHello: sayHello});
    address = `${addr}:${port}`
    server.bindAsync(
      address,
      grpc.ServerCredentials.createInsecure(),
      (err, port) => {
        process.stdout.write(`Start Auth-nodejs. Listen on ${address}\n`);
        server.start();
      }
    );
  }
}

exports.lambda_handler = async (event, context) => {
  var token = event["name"];
  var fakeMethodArn = "arn:aws:execute-api:{regionId}:{accountId}:{apiId}/{stage}/{httpVerb}/[{resource}/[{child-resources}]]";
  var msg1, ret;
  switch (token) {
      case 'allow':
        ret = generatePolicy('user', 'Allow', fakeMethodArn);
        msg1 = JSON.stringify(ret, null, 2);
        break;
      case 'deny':
        ret = generatePolicy('user', 'Deny', fakeMethodArn);
        msg1 = JSON.stringify(ret, null, 2);
        break;
      case 'unauthorized':
        msg1 = "Unauthorized";   // Return a 401 Unauthorized response
        break;
      default:
        msg1 = "Error: Invalid token"; // Return a 500 Invalid token response
  }
  var msg = `fn: Auth | token: ${token} | resp: ${msg1} | runtime: nodejs`;
}

main();

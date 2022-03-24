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
const version = process.version


var PROTO_PATH = __dirname + '/helloworld.proto';

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




function fibonacci(num)
{
    var num1=0;
    var num2=1;
    var sum;
    var i=0;
    for (i = 0; i < num; i++) 
    {
        sum=num1+num2;
        num1=num2;
        num2=sum;
    }
    return num1;
}



/**
 * Implements the SayHello RPC method.
 */
function sayHello(call, callback) {
  
  var gid = process.getgid()
  var x = parseInt(call.request.name)
  var y = fibonacci(x)
  var msg = `Hello: this is: ${gid}. Invoke NodeJS Fib y = fib(x) | x: ${x} y: ${y}`
  callback(null, {message: msg});
}

/**
 * Starts an RPC server that receives requests for the Greeter service at the
 * sample server port
 */
function main() {
  var server = new grpc.Server();
  process.stdout.write(`Node version: ${version}\n`);
  server.addService(hello_proto.Greeter.service, {sayHello: sayHello});
  // address = '[::]:' + GRPC_PORT
  address = '0.0.0.0:' + GRPC_PORT
  server.bindAsync(
    address,
    grpc.ServerCredentials.createInsecure(),
    // grpc.ServerCredentials.createSsl(),
    (err, port) => {
      process.stdout.write(`Server started on ${address}\n`);
      server.start();
    }
  );
}

main();

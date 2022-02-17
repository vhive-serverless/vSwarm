/*
 *
 * Copyright 2015 gRPC authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

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

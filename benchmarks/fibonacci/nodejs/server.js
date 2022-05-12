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

var PROTO_PATH = __dirname + '/fibonacci.proto';

var grpc = require('@grpc/grpc-js');
var protoLoader = require('@grpc/proto-loader');
var packageDefinition = protoLoader.loadSync(
  PROTO_PATH,
  {
    keepCase: true,
    longs: String,
    enums: String,
    defaults: true,
    oneofs: true
  });
var hello_proto = grpc.loadPackageDefinition(packageDefinition).fibonacci;


function fibonacci(num) {
  var num1 = 0;
  var num2 = 1;
  var sum;
  var i = 0;
  for (i = 0; i < num; i++) {
    sum = num1 + num2;
    num1 = num2;
    num2 = sum;
  }
  return num1;
}

/**
 * Argument parsing
 */
function parsArgs() {

  var { argv } = require("yargs")
    .scriptName("server")
    .usage("Usage: $0 --addr <IP> --port <PORT> --zipkin <ZIPKIN URL>")
    .example(
      "$0 -p 50051",
      "Starts Fibonacci gRPC server on localhost:50051"
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



/**
 * Implements the SayHello RPC method.
 */
function sayHello(call, callback) {
  process.stdout.write(`Received gRPC call.\n`);

  if (tracing.IsTracingEnabled()) {
    span = new tracing.Span()
  }

  var x = parseInt(call.request.name)
  var y = fibonacci(x)
  var msg = `fn: Fib: y = fib(x) | x: ${x} y: ${y} | runtime: NodeJS`

  if (tracing.IsTracingEnabled()) {
    span.addEvent(msg);
    span.end();
  }

  callback(null, { message: msg });
}

/**
 * Starts an RPC server that receives requests for the Greeter service at the
 * sample server port
 */
function main() {
  const [addr, port, zipkin] = parsArgs();

  if (tracing.IsTracingEnabled()) {
    process.stdout.write(`Tracing enabled\n`);
    tracing.InitTracer('fibonacci-nodejs-server', zipkin);
  } else {
    process.stdout.write(`Tracing disabled\n`);
  }

  var server = new grpc.Server();
  server.addService(hello_proto.Greeter.service, { sayHello: sayHello });
  address = `${addr}:${port}`
  server.bindAsync(
    address,
    grpc.ServerCredentials.createInsecure(),
    (err, port) => {
      process.stdout.write(`Server started on ${address}\n`);
      server.start();
    }
  );
}

main();

// Include process module
const process = require('process');
const tracing = require('tracing')


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
var CryptoJS = require("crypto-js");



function func1()
{
  // Encrypt
  var plaintext = "exampleplaintext"
  var ciphertext = CryptoJS.AES.encrypt(plaintext, 'secret key 123').toString();

  // Decrypt
  // var bytes  = CryptoJS.AES.decrypt(ciphertext, 'secret key 123');
  // var originalText = bytes.toString(CryptoJS.enc.Utf8);

  // console.log(ciphertext);
  return ["NodeJS.aes.f1", plaintext, ciphertext];
}
function func2()
{
  var plaintext = "a m e s s a g e "
  var ciphertext = CryptoJS.AES.encrypt(plaintext, 'examplekey').toString();
  // console.log(ciphertext);
  return ["NodeJS.aes.f1", plaintext, ciphertext];
}

function func(plaintext)
{
  var ciphertext = CryptoJS.AES.encrypt(plaintext, 'examplekey').toString();
  // console.log(ciphertext);
  return ["NodeJS.aes.fn", plaintext, ciphertext];
}



/**
 * Implements the SayHello RPC method.
 */
function sayHello(call, callback) {

  let span;

  if (tracing.IsTracingEnabled()) {
    span = new tracing.Span()
  }


  var gid = process.getgid();

  switch (call.request.name) {
    case ".f1":
      ret = func1();

      break;
    case ".f2":
      ret = func2();
      break;

    default:
      ret = func(call.request.name);
      break;
  }
  const [msg1, plaintext, ciphertext] = ret
  var msg = `Hello: this is: ${gid}. Invoke ${msg1} | Plaintext: ${plaintext} Ciphertext: ${ciphertext}`;

  if (tracing.IsTracingEnabled()) {
    span.addEvent(`Invoke ${msg1} | Plaintext: ${plaintext} Ciphertext: ${ciphertext}`);
    span.end();
  }
  callback(null, {message: msg});

}

/**
 * Argument parsing
 */
function parsArgs() {

  var { argv } = require("yargs")
  .scriptName("server")
  .usage("Usage: $0 --addr <IP> --port <PORT> --zipkin <ZIPKIN URL>")
  .example(
    "$0 -p 50061",
    "Starts AES gRPC server on localhost:50061"
  )
  .option("a", {
    alias: "addr",
    describe: "IP address",
    type: "string",
  })
  .option("p", {
    alias: "port",
    describe: "Port the server listen to",
    type: "string",
  })
  .option("z", {
    alias: "zipkin",
    describe: "Zipkin URL",
    type: "string",
  })
  .describe("help", "Show help.") // Override --help usage message.
  .describe("version", "Show version number.") // Override --version usage message.
  .epilog("copyright 2022");

  var addr = "0.0.0.0";
  var port = "50051";
  var zipkin = "http://localhost:9411/api/v2/spans";

  if ('addr' in argv) {
    addr = argv.addr;
  }
  if ('port' in argv) {
    port = argv.port;
  }
  if ('zipkin' in argv) {
    zipkin = argv.zipkin;
  }
  return [ addr, port, zipkin ];
}


/**
 * Starts an RPC server that receives requests for the Greeter service at the
 * sample server port
 */
function main() {

  const [ addr, port, zipkin ] = parsArgs();

  if (tracing.IsTracingEnabled()) {
    tracing.InitTracer('aes-nodejs-server',zipkin);
  }

  var server = new grpc.Server();
  server.addService(hello_proto.Greeter.service, {sayHello: sayHello});
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

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

var key = "6368616e676520746869732070617373";
var default_plaintext = "exampleplaintext";
var iv = "0000000000000000"

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
  .option("a", {alias: "addr", type: "string",
    describe: "IP address",
  })
  .option("p", {alias: "port", type: "string",
    describe: "Port the server listen to",
  })
  .option("z", {alias: "zipkin", type: "string",
    describe: "Zipkin URL",
  })
  .option("k", {alias: "key", type: "string",
    describe: "Secret key",
  })
  .option("default_plaintext", {type: "string",
    describe: "Default plaintext",
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
  if ('key' in argv) { key = argv.key; }
  if ('default_plaintext' in argv) { default_plaintext = argv.default_plaintext; }

  return [ addr, port, zipkin ];
}

var JsonFormatter = {
  stringify: function(cipherParams) {
    // create json object with ciphertext
    var jsonObj = { ct: cipherParams.ciphertext.toString(CryptoJS.enc.Base64) };
    // optionally add iv or salt
    if (cipherParams.iv) {
      jsonObj.iv = cipherParams.iv.toString();
    }
    if (cipherParams.salt) {
      jsonObj.s = cipherParams.salt.toString();
    }
    // stringify json object
    return JSON.stringify(jsonObj);
  },
  parse: function(jsonStr) {
    // parse json string
    var jsonObj = JSON.parse(jsonStr);
    // extract ciphertext from json object, and create cipher params object
    var cipherParams = CryptoJS.lib.CipherParams.create({
      ciphertext: CryptoJS.enc.Base64.parse(jsonObj.ct)
    });
    // optionally extract iv or salt
    if (jsonObj.iv) {
      cipherParams.iv = CryptoJS.enc.Hex.parse(jsonObj.iv);
    }

    if (jsonObj.s) {
      cipherParams.salt = CryptoJS.enc.Hex.parse(jsonObj.s);
    }

    return cipherParams;
  }
};

var encrypted = CryptoJS.AES.encrypt("Message", "Secret Passphrase", {
  format: JsonFormatter
})

function AESModeCTR(plaintext) {

  //Create Key
  var _key = CryptoJS.enc.Utf8.parse(key);
  //Get IV
  var _iv = CryptoJS.enc.Utf8.parse(iv);
  var encrypted = CryptoJS.AES.encrypt(plaintext, _key,{ iv: _iv});
  //Encrypt string
  return encrypted.ciphertext.toString();
}


/**
 * Implements the SayHello RPC method.
 */
function sayHello(call, callback) {

  let span;

  if (tracing.IsTracingEnabled()) {
    span = new tracing.Span()
  }


  var plaintext = call.request.name
  if (call.request.name == "" || call.request.name == "world") {
    plaintext = default_plaintext
  }

  const ciphertext = AESModeCTR(plaintext)
  var msg = `fn: AES | plaintext: ${plaintext} ciphertext: ${ciphertext} | runtime: NodeJS`;

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

// Include process module
const process = require('process');
const GRPC_PORT = process.env.GRPC_PORT || '50051'


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

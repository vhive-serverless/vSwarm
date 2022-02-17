../../tools/bin/grpcurl -plaintext -import-path proto -proto helloworld.proto -d '{name: 12}' localhost:50061 helloworld.Greeter.SayHello
Modify invoker Name field also

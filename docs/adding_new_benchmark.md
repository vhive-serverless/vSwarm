This is a detailed document of how to add a new benchmark in vSwarm.
# Add Standalone Benchmarks in vSwarm
## Python
### 1. Add protobuf
The first thing we need to do is to add protobuf in [vSwarm-proto](https://github.com/vhive-serverless/vSwarm-proto).

First, clone [vSwarm-proto](https://github.com/vhive-serverless/vSwarm-proto), operations below should be taken in your local `vSwarm-proto/` folder.

Add a new folder to `proto/` named by your benchmark `{bench}`, add file `{bench}.proto` to this `proto/{bench}/` folder, which should define the protobuf of your benchmark.

In `{bench}.proto` file, define the needed grpc service. Note that invoker and most of vHive work with the simple [`HelloWorld`](https://grpc.io/docs/what-is-grpc/introduction/) service. However, you can implement arbitrary services for your function as the relay, sitting in between the invoker and your function, can be used to make translations. Refer to [aes.proto](https://github.com/vhive-serverless/vSwarm-proto/blob/main/proto/aes/aes.proto) and the corresponding [translation](https://github.com/vhive-serverless/vSwarm-proto/blob/main/grpcclient/aes_client.go) as an example of a custom service. 
```
// The greeting service definition.
service Greeter {
  // Sends a greeting
  rpc SayHello (HelloRequest) returns (HelloReply) {}
}
```
After defining your `HelloRequest` and `HelloReply`, do the following to generate protobuf:
1. Repeat the steps in `vSwarm-proto/.github/.workflows/build-tests.yml` to install `pipenv` and `protoc`.
2. Add a line in  `go.mod` file's `replace` module:
```
github.com/vhive-serverless/vSwarm-proto/proto/{bench} => ./proto/{bench}
```
3. Run the following two commands to generate the `protocbuf` for your benchmark:
```
cd vSwarm-proto/proto/{bench}
pipenv install 
pipenv run python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./proto/bert/*.proto
```
This generates protobuf files for python
```
protoc --go_out=. --go_opt=paths=source_relative --go-grpc_out=. --go-grpc_opt=paths=source_relative ./proto/bert/*.proto
```
This generates protobuf files for go.

Alternatively, run `make proto-all` in the root of vSwarm-proto, which does both steps for all protocols automatically.

Then, in `vSwarm-proto/grpcclient` folder, add a file named `{bench}_client.go`. This is the client that the relay will select to invoke your function. Each client must implement [`GrpcClient`](https://github.com/vhive-serverless/vSwarm-proto/blob/70781f2339083f8c6d298ce0be13e7b7869c1409/grpcclient/grpcclient.go#L79) interface. 
`Init` and `Close` are used to set up and close the connection to the function. 
`GetGenerator` will must return an generator for creating new input values for your function.
`Request` is the actual invocation of the function.
Refer to other `*_client.go` clients for more details about how to implement those functions.

Finally, in `vSwarm-proto/grpcclient/getclient.go`, add your `{bench}` to `func FindServiceName` and `func FindGrpcClient`

After these are done, commit and push to the upstream branch.

Below operations should be taken under `vSwarm` instead of `vSwarm-proto`
### 2.Modify relay
Assume you have changed `vSwarm-proto` but the change hasn't been merged into main branch, if you want to test its functionality locally, you should build a local relay docker image to replace the one on the cloud, so:
```
cd tools/bin/relay
# commit id is the commit you have made to vSwarm-proto repo
go get github.com/vhive-serverless/vSwarm-proto@{commit id}
make all
```

Now, you have a local relay image that uses your modified version of protoc.
Remember **DO NOT** commit changes in `tools/relay` to the remote repo

### 3.Dockerize your benchmark
This is a case-by-case process, guidelines on how to do this will be given in the future.

### 4.Adding CI
Guidelines on how to do this will be given in the future

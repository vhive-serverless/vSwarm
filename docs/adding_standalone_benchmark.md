# Adding Standalone Benchmarks in vSwarm
This is a detailed document of how to add a standalone benchmark in vSwarm.

## Python
### 1. Add protobuf
The first thing we need to do is to add protobuf in [vSwarm-proto](https://github.com/vhive-serverless/vSwarm-proto).

First, clone [vSwarm-proto](https://github.com/vhive-serverless/vSwarm-proto), operations below should be taken in your local `vSwarm-proto/` folder.

Add a new folder to `proto/` named by your benchmark `{bench}`, add file `{bench}.proto` to this `proto/{bench}/` folder, which should define the protobuf of your benchmark.

In `{bench}.proto` file, always define your service as `Greeter` since this is the grpc service that will be invoked by the relay.
```
// The greeting service definition.
service Greeter {
  // Sends a greeting
  rpc SayHello (HelloRequest) returns (HelloReply) {}
}
```
After defining your HelloRequest and HelloReply, do the following to generate protobuf:
1. Repeat the steps in `vSwarm-proto/.github/.workflows/build-tests.yml` to install pipenv and protoc.
2. Add a line in  `go.mod` file's `replace` module:
```
github.com/vhive-serverless/vSwarm-proto/proto/{bench} => ./proto/{bench}
```
3. Run the following two commands to generate the protocbuf for your benchmark:
```
cd vSwarm-proto/proto/{bench}
pipenv install 
pipenv run python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./proto/bert/*.proto
```
This generates protobuf files for python
```
protoc --go_out=. --go_opt=paths=source_relative --go-grpc_out=. --go-grpc_opt=paths=source_relative ./proto/bert/*.proto
```
This generates protobuf files for go

Then, in `vSwarm-proto/grpcclient` foler, add a file named `{bench}_client.go`, this is the client that relay would return to the invoker. Please refer to other `*_client.go` on how to write this file.

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
Remeber **DO NOT** commit changes in `tools/relay` to the remote repo

### 3.Dockerize your benchmark
This is a case-by-case process, guidelines on how to do this will be given in the furture.
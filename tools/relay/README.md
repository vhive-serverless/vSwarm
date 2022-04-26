# Relay

Relay will act as an interface between invoker and the benchmark server, allowing the user of a function to supply a custom form of input than a strict Helloworld format (see `aes.proto` for example). This way, to add a function benchmark you would not be restricted to the helloworld proto but can use any arbitrary proto file of your choice.

## Adding relay

For docker compose files, add the following snippet

```yaml
relay:
  image: vhiveease/relay:latest
  entrypoint:
    - /app/server
    - --addr=0.0.0.0:50000
    - --function-endpoint-url=<FUNCTION_URL>
    - --function-endpoint-port=<FUNCTION_PORT>
    - --function-name=<FUNCTION_NAME>
  ports:
    - published: 50000
      target: 50000
```
where FUNCTION_NAME is replaced by the name you have added to the `getclient.go` in the [vSwarm-proto repository](https://github.com/ease-lab/vSwarm-proto/blob/main/grpcclient/getclient.go). You can remove the published port of your benchmark server now (the `CONTAINER_PORT` is now FUNCTION_PORT, see [docker networking](https://docs.docker.com/compose/networking/)).

To understand the URL setting in detail check [here in docker docs](https://docs.docker.com/compose/networking/) to find out how docker network works.  
Generally speaking in this case docker compose sets up a single network between the relay and the function container. Now the function container is reachable from the relay via the service/container name. See [docker networking](https://docs.docker.com/compose/networking/) or aes-go as an example

For knative yamls, add the following snippet

```yaml
containers:
  - image: docker.io/vhiveease/relay:latest
    ports:
      - name: h2c
        containerPort: 50000
    args:
      - --addr=0.0.0.0:50000
      - --function-endpoint-url=<FUNCTION_URL>
      - --function-endpoint-port=<FUNCTION_PORT>
      - --function-name=<FUNCTION_NAME>
  - image: docker.io/<DOCKER_URL_TO_YOUR_FUNCTION>
```

## Running relay

Simply use invoker on port 50000.

```bash
echo '[ { "hostname": "0.0.0.0" } ]' > endpoints.json
./invoker -port 50000
```

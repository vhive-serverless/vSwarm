
## Running this benchmark (using knative)

The detailed and general description on how to run benchmarks on knative clusters you can find [here](../../docs/running_benchmarks.md). The following steps show it on the aes-go function.
1. Build or pull the function images using `make all-image` or `make pull`.
    ```bash
   sudo make pull 
   sudo docker image tag vhiveease/aes-go localhost:5000/aes-go 
   sudo docker push localhost:5000/aes-go
   ```
2. Start the function with knative
   ```bash
   kn service apply -f ./yamls/knative/kn-aes-go.yaml
   ```
3. **Note the URL provided in the output. The part without the `http://` we'll call `$URL`. Replace any instance of `$URL` in the code below with it.**
### Invoke once
4. In a new terminal, invoke the interface function with test-client.
   ```bash
   ./test-client --addr $URL:80 --name "Example text for AES"
   
   ```
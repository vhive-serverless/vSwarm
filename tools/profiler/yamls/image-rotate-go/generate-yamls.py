import yaml

template_yaml = """
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: image-rotate-go-{x}
  namespace: default
spec:
  template:
    spec:
      containers:
        - image: docker.io/vhiveease/relay-latency:latest
          ports:
            - name: h2c
              containerPort: 50000
          args:
            - --addr=0.0.0.0:50000
            - --function-endpoint-url=0.0.0.0
            - --function-endpoint-port=50051
            - --function-name=image-rotate-go
            - --value=img{x}.jpg
            - --profile-function=true
        - image: docker.io/vhiveease/image-rotate-go:latest
          args:
            - --addr=0.0.0.0:50051
            - --db_addr=mongodb://image-rotate-database:27017


"""

# List of x values
x_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]

# Generate YAML files for each combination of x and y values
for x in x_values:
    y = int(1.01 * x)
    yaml_content = template_yaml.format(x=x)
    filename = f"kn-image-rotate-go-{x}.yaml"
    with open(filename, "w") as f:
        f.write(yaml_content)
    print(f"Created {filename}")


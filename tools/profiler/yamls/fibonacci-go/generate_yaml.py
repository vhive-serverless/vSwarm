import yaml

# Template YAML content
template_yaml = """
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: fibonacci-go-{x}-{y}
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
            - --function-name=fibonacci-go
            - --value=10
            - --generator=random
            - --lowerBound={x}
            - --upperBound={y}
            - --profile-function=true
        - image: docker.io/vhiveease/fibonacci-go-mod:latest
          args:
            - --addr=0.0.0.0:50051
"""

# List of x values
# x_values = [10, 1000, 4500, 10000, 20000, 45000, 70000, 100000, 200000, 450000, 700000, 1000000, 2000000, 4500000, 7000000, 10000000, 20000000, 45000000, 70000000]
x_values = [10, 1000, 4500, 10000, 20000, 45000, 70000, 100000, 200000, 450000, 700000, 1000000]

# Generate YAML files for each combination of x and y values
for x in x_values:
    y = int(1.01 * x)
    yaml_content = template_yaml.format(x=x, y=y)
    filename = f"kn-fibonacci-go-{x}-{y}.yaml"
    with open(filename, "w") as f:
        f.write(yaml_content)
    print(f"Created {filename}")

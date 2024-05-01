import yaml

template_yaml = """
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: rnn-serving-python-{x}-{y}
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
            - --function-name=rnn-serving-python
            - --value=French
            - --generator=random
            - --lowerBound={x}
            - --upperBound={y}
            - --profile-function=true
        - image: docker.io/vhiveease/rnn-serving-python:latest
          args:
            - --addr=0.0.0.0
            - --port=50051
            - --default_language=French
            - --num_strings=15
"""

# List of x values
x_values = [1, 5, 10, 20, 45, 100, 200, 300, 450, 700, 1000, 1500, 2000, 2500, 3000, 4500, 7000]

# Generate YAML files for each combination of x and y values
for x in x_values:
    y = int(1.01 * x)
    yaml_content = template_yaml.format(x=x, y=y)
    filename = f"kn-rnn-serving-python-{x}-{y}.yaml"
    with open(filename, "w") as f:
        f.write(yaml_content)
    print(f"Created {filename}")


import yaml

template_yaml = """
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: video-processing-python-{x}
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
            - --function-name=video-processing-python
            - --value=video4.mp4
            - --profile-function=true
        - image: docker.io/vhiveease/video-processing-python:latest
          args:
            - --addr=0.0.0.0
            - --port=50051
            - --db_addr=mongodb://video-processing-database:27017
            - --default_video=default.mp4
            - --num_frames={x}
"""

# List of x values
# x_values = [10, 20, 45, 70, 100, 200]
# x_values = [320, 450, 700, 1000, 1500, 2000] 
# x_values = [3000, 4000] 
x_values = [5000, 6000, 7000]

# Generate YAML files for each combination of x and y values
for x in x_values:
    y = int(1.01 * x)
    yaml_content = template_yaml.format(x=x)
    filename = f"kn-video-processing-python-{x}.yaml"
    with open(filename, "w") as f:
        f.write(yaml_content)
    print(f"Created {filename}")


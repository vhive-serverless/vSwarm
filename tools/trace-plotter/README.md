# Trace Plotter
Trace Plotter gathers traces from zipkin and provides a CDF plot of the latency.
Zipkin does not provide a way to view the overall latency distribution.
This tool is a simple way to view the latency distribution, analyze the percentile of each trace latency, and connect each trace to the Zipkin UI for in-depth trace analysis.

![graph](./images/img.png)

e2e traces show the latency of each root trace.
The system traces show the latency of the system by subtracting the last trace latency from the root latency.
## Zipkin Setup Instructions
We use [Elasticsearch](https://github.com/elastic/elasticsearch) as a backend for Zipkin as Elasticsearch allows to store and load all traces sent to Zipkin. This is a good choice for a large number of traces, and will also allow the usage of elasticsearch in querying and analysing traces.

See [here](https://github.com/openzipkin/zipkin/tree/master/zipkin-server#elasticsearch-storage) for more information on zipkin storage.

Following the instructions below, we set up zipkin with an Elasticsearch database on a k8s cluster.

### Install Helm

[Helm](https://helm.sh) must be installed to download and deploy the charts.
Please refer to Helm's [documentation](https://helm.sh/docs/) for detailed instructions.

```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### Download the helm charts
```bash
helm repo add openzipkin https://openzipkin.github.io/zipkin
helm pull --untar openzipkin/zipkin
```

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm pull --untar bitnami/elasticsearch
```

### Deploy the charts
Create namespace for each deployment.
```bash
kubectl create namespace elasticsearch
kubectl create namespace zipkin
```

Install each service. Example values for each chart are provided in this repository under `values`.

```bash
helm upgrade --install --wait -f ./values/es-example.values.yaml -n elasticsearch elasticsearch ./elasticsearch
```

```bash
helm upgrade --install --wait -f ./values/zipkin-example.values.yaml -n zipkin zipkin ./zipkin
```

### Update vHive settings to allow tracing

```bash
kubectl patch configmap/config-tracing \
  -n knative-serving \
  --type merge \
  -p '{"data":{"backend":"zipkin","zipkin-endpoint":"http://zipkin.zipkin.svc.cluster.local:9411/api/v2/spans","debug":"true"}}'
```
Set `debug` to `true` if you want to record all traces. Otherwise zipkin will sample traces.

### Port Forwarding
This code requires the following ports to be forwarded:
- `zipkin`: 9411
- `elasticsearch`: 9200  
which can be done by running the following command:
```bash
kubectl port-forward --namespace elasticsearch svc/elasticsearch 9200:9200
kubectl port-forward --namespace zipkin deployment/zipkin 9411:9411
```

### Build and Run
```bash
go build && ./trace-plotter -zipkinURL http://127.0.0.1:9411
```

## Usage
```bash
Usage of ./trace-plotter:
  -elasticsearchURL string
        Elasticsearch URL (default "http://127.0.0.1:9200")
  -fileName string
        output file name (default "plot.html")
  -pageSize int
        The number of traces to fetch per page while paginating (default 100)
  -zipkinURL string
        Zipkin URL (default "http://127.0.0.1:8080")
```

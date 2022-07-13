# Trace Plotter
Trace Plotter gathers traces from zipkin and provides a CDF plot of the latency.
Zipkin does not provide a way to view the overall latency distribution.
This tool is a simple way to view the latency distribution, analyze the percentile of each trace latency, and connect each trace to the Zipkin UI for in-depth trace analysis.

![graph](./images/img.png)
## Zipkin Setup Instructions
**We use Elasticsearch as a backend for Zipkin as Elasticsearch allows to store and load all traces sent to Zipkin.**

Following instructions setup zipkin with an elasticsearch database on a k8s cluster.

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

Install each chart. Example values are provided in this repository.

```bash
helm upgrade --install -f ./values/es-example.values.yaml -n elasticsearch elasticsearch ./elasticsearch
```

```bash
helm upgrade --install -f ./values/zipkin-example.values.yaml -n zipkin zipkin ./zipkin
```

### Update vhive settings to allow tracing

```bash
kubectl patch configmap/config-tracing \
  -n knative-serving \
  --type merge \
  -p '{"data":{"backend":"zipkin","zipkin-endpoint":"http://zipkin.zipkin.svc.cluster.local:9411/api/v2/spans","debug":"true"}}'
```
Set `debug` to `true` if you want to trace all traces. Otherwise zipkin will sample traces.

## Usage
```bash
Usage of ./trace-plotter:
  -elasticsearchURL string
        Elasticsearch URL (default "http://127.0.0.1:9200")
  -fileName string
        output file name (default "plot.html")
  -latencyType string
        which latency type to plot, e2e or system(e2e - leaf trace execution time) (default "e2e")
  -pageSize int
        The number of traces to fetch per page while paginating (default 100)
  -zipkinURL string
        Zipkin URL (default "http://127.0.0.1:8080")
```

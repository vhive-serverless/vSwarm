# Deployment and benchmarking tools

This directory contains tools that are useful outside of benchmark functions, e.g. for deployment,
managing, or testing. Some of the more noteworthy tools include:

* `deployer/client.go` deploys functions of types and quantity as defined in `deployer/functions.json`.
* `invoker/client.go` invokes functions and reports the latencies and throughput (RPS).

More details on using these tools are available in the [vHive quickstart guide](https://github.com/vhive-serverless/vhive/blob/main/docs/quickstart_guide.md).

We encourage the community to experiment with these basic tools,
extend them and contribute new tools for performance analysis
of various scenarios.

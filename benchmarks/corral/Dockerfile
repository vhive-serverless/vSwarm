FROM vhiveease/golang-builder AS builder
WORKDIR /vhive
COPY . .
WORKDIR /vhive/benchmarks/corral
RUN make

FROM vhiveease/runner
RUN apt-get update && apt-get install -y ca-certificates
COPY --from=builder /vhive/benchmarks/corral/bin/word_count /usr/local/bin/corral
ENTRYPOINT [ "/usr/local/bin/corral" ]

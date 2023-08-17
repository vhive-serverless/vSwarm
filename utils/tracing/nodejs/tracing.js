'use strict';

// const api = require('@opentelemetry/api');
const opentelemetry = require('@opentelemetry/api');
const { registerInstrumentations } = require('@opentelemetry/instrumentation');
const { NodeTracerProvider } = require('@opentelemetry/sdk-trace-node');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');
const { SimpleSpanProcessor } = require('@opentelemetry/sdk-trace-base');
const { ZipkinExporter } = require('@opentelemetry/exporter-zipkin');
const { GrpcInstrumentation } = require('@opentelemetry/instrumentation-grpc');


// const ENABLE_TRACING = process.env.ENABLE_TRACING || false;

function IsTracingEnabled() {
    if (process.env.ENABLE_TRACING) {
        return true;
    } else {
        return false;
    }
}

var tracer

function InitTracer(serviceName='', url='http://localhost:9411/api/v2/spans') {
    if (!IsTracingEnabled()) {
        return;
    }

    const provider = new NodeTracerProvider({
        resource: new Resource({
          [SemanticResourceAttributes.SERVICE_NAME]: serviceName,
        }),
      });

    // Add your zipkin url (ex http://localhost:9411/api/v2/spans)
    // and application name to the Zipkin options
    const zipkinOptions = {
        url: url,
        serviceName: serviceName
    };

    const exporter = new ZipkinExporter(zipkinOptions);

    provider.addSpanProcessor(new SimpleSpanProcessor(exporter));

    // Initialize the OpenTelemetry APIs to use the NodeTracerProvider bindings
    provider.register();

    registerInstrumentations({
    instrumentations: [
        new GrpcInstrumentation(),
    ],
    });

    process.stdout.write(`Tracing enabled for: ${serviceName}, url: ${url}\n`);
    tracer = opentelemetry.trace.getTracer('grpc-tracer');
}


class Span {
    constructor() {
        if (!IsTracingEnabled()) { return; }

        this.currentSpan = opentelemetry.trace.getSpan(opentelemetry.context.active());
        this.span = tracer.startSpan('aes-nodejs:sayHello()', {
                    parent: this.currentSpan,
                    kind: 1, // server
                    attributes: { key: 'aes' },
                });
    }

    addEvent(msg) {
        if (!IsTracingEnabled()) { return; }
        this.span.addEvent(msg);
    }
    end() {
        if (!IsTracingEnabled()) { return; }
        this.span.end();
    }

}


module.exports = {
    IsTracingEnabled,
    InitTracer,
    Span
};
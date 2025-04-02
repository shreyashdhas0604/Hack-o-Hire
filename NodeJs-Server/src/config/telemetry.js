const opentelemetry = require('@opentelemetry/api');
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');

function setupTelemetry() {
    const sdk = new NodeSDK({
        resource: new Resource({
            [SemanticResourceAttributes.SERVICE_NAME]: 'nodejs-crud-api',
            [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
        }),
        traceExporter: new OTLPTraceExporter({
            url: 'http://jaeger:4318/v1/traces',  // Updated URL to use the Docker service name
            headers: {}, // Include empty headers object
        }),
        instrumentations: [getNodeAutoInstrumentations()]
    });

    try {
        sdk.start();
        console.log('Tracing initialized');
    } catch (error) {
        console.error('Error initializing tracing', error);
    }

    process.on('SIGTERM', async () => {
        try {
            await sdk.shutdown();
            console.log('Tracing terminated');
        } catch (error) {
            console.error('Error terminating tracing', error);
        } finally {
            process.exit(0);
        }
    });
}

module.exports = { setupTelemetry };
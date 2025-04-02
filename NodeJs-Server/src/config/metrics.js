const promClient = require('prom-client');

// Create a Registry
const register = new promClient.Registry();

// Add default metrics
promClient.collectDefaultMetrics({
    app: 'nodejs-crud',
    prefix: 'nodejs_',
    register
});

// Custom metrics
const httpRequestDuration = new promClient.Histogram({
    name: 'http_request_duration_seconds',
    help: 'Duration of HTTP requests in seconds',
    labelNames: ['method', 'route', 'status_code'],
    buckets: [0.1, 0.5, 1, 2, 5]
});

const dbQueryDuration = new promClient.Histogram({
    name: 'db_query_duration_seconds',
    help: 'Duration of database queries in seconds',
    labelNames: ['operation'],
    buckets: [0.1, 0.5, 1, 2, 5]
});

register.registerMetric(httpRequestDuration);
register.registerMetric(dbQueryDuration);

module.exports = {
    register,
    httpRequestDuration,
    dbQueryDuration
};
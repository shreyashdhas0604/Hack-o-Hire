require('dotenv').config();
const { setupTelemetry } = require('./config/telemetry');

// Initialize OpenTelemetry
setupTelemetry();
const express = require('express');
// Remove this line as it's duplicated
// const { register } = require('./config/metrics');
const cors = require('cors');
const productRoutes = require('./routes/product.routes');
const { connectToDatabase } = require('./config/database');
const { register, httpRequestDurationMicroseconds, httpRequestsTotal } = require('./config/prometheus');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Prometheus middleware
app.use((req, res, next) => {
    const start = Date.now();
    res.on('finish', () => {
        const duration = Date.now() - start;
        httpRequestDurationMicroseconds
            .labels(req.method, req.path, res.statusCode)
            .observe(duration / 1000);
        httpRequestsTotal
            .labels(req.method, req.path, res.statusCode)
            .inc();
    });
    next();
});

// Logging middleware
const logger = require('./middleware/logger');
app.use(logger);

// Routes
app.use('/api/products', productRoutes);

// Prometheus metrics endpoint
// Add metrics endpoint
app.get('/metrics', async (req, res) => {
    res.setHeader('Content-Type', register.contentType);
    res.send(await register.metrics());
});

// Database connection
connectToDatabase();

// Start server
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
    console.log(`Metrics available at http://localhost:${PORT}/metrics`);
});
const fs = require('fs');
const path = require('path');

// Create logs directory if it doesn't exist
const logsDir = path.join(__dirname, '..', 'logs');
if (!fs.existsSync(logsDir)) {
    fs.mkdirSync(logsDir);
}

const logStream = fs.createWriteStream(
    path.join(logsDir, 'api.log'),
    { flags: 'a' }
);

const opentelemetry = require('@opentelemetry/api');

const logger = (req, res, next) => {
    const start = Date.now();
    const originalSend = res.send;

    // Capture the response body
    res.send = function (body) {
        res.send = originalSend;
        res.body = body;
        return res.send(body);
    };

    res.on('finish', () => {
        const duration = Date.now() - start;
        const log = {
            timestamp: new Date().toISOString(),
            method: req.method,
            url: req.originalUrl,
            status: res.statusCode,
            duration: `${duration}ms`,
            requestBody: req.body,
            responseBody: res.body,
            userAgent: req.get('user-agent'),
            ip: req.ip
        };

        logStream.write(`${JSON.stringify(log)}\n`);
    });

    next();
};

module.exports = logger;
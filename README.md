# API Call Monitoring System

A comprehensive monitoring system for API calls with anomaly detection, metrics collection, and visualization capabilities.

## Project Components

### 1. API Monitoring Service
- Anomaly detection for API calls using machine learning
- Real-time monitoring of API metrics
- Support for both real and simulated log data
- Built with Python using advanced AI analysis capabilities

### 2. NodeJS Server
- CRUD API implementation with Express.js and MySQL
- Integrated metrics collection using Prometheus
- OpenTelemetry integration for distributed tracing
- Structured logging system

### 3. Django Web Service
- Django-based web API with REST framework
- Prometheus metrics integration
- Jaeger tracing support
- Structured logging with JSON format

## Monitoring Stack

### Metrics & Visualization
- Prometheus for metrics collection
- Grafana for metrics visualization
- Custom dashboards for API monitoring

### Logging
- Structured logging across all services
- Loki for log aggregation
- Promtail for log collection

### Tracing
- OpenTelemetry instrumentation
- Jaeger for distributed tracing
- Trace correlation with logs and metrics

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.x
- Node.js
- MySQL

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/hack-o-hire.git
cd hack-o-hire
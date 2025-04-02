import random
import json
from datetime import datetime, timedelta
import numpy as np
from config import Config

class APILogGenerator:
    def __init__(self):
        self.config = Config()
        self.services = ["user-service", "payment-service", "inventory-service", "auth-service"]
        self.environments = ["on-prem", "aws-cloud", "azure-cloud", "gcp-cloud"]
        self.status_codes = [200, 201, 400, 401, 403, 404, 500, 503]
        self.users = [f"user_{i}" for i in range(1000)]
        self.endpoints = {
            "user-service": ["/users", "/users/{id}", "/users/search"],
            "payment-service": ["/payments", "/payments/{id}", "/payments/verify"],
            "inventory-service": ["/products", "/products/{id}", "/inventory"],
            "auth-service": ["/auth/login", "/auth/register", "/auth/token"]
        }
        
    def _generate_timestamp(self):
        base_time = datetime.now() - timedelta(days=random.randint(0, 30))
        return (base_time + timedelta(seconds=random.random() * 10)).isoformat()
    
    def generate_normal_log(self):
        service = random.choice(self.services)
        environment = random.choice(self.environments)
        
        # Base response time varies by environment
        base_response = {
            "on-prem": 80,
            "aws-cloud": 120,
            "azure-cloud": 150,
            "gcp-cloud": 100
        }[environment]
        
        response_time = max(10, np.random.normal(
            base_response,
            self.config.NORMAL_TRAFFIC_STD
        ))
        
        # 5% chance of error
        if random.random() < 0.05:
            status = random.choice([c for c in self.status_codes if c >= 400])
            response_time *= 1.5
        else:
            status = random.choice([c for c in self.status_codes if c < 400])
            
        return {
            "timestamp": self._generate_timestamp(),
            "service": service,
            "environment": environment,
            "status_code": status,
            "response_time": round(response_time, 2),
            "user_id": random.choice(self.users),
            "endpoint": random.choice(self.endpoints[service]),
            "request_size": random.randint(100, 5000),
            "response_size": random.randint(50, 3000),
            "language": random.choice(["nodejs", "golang", "python", "java"])
        }
    
    def generate_anomalous_log(self):
        log = self.generate_normal_log()
        anomaly_type = random.choice(["response_time", "error_rate", "traffic_spike"])
        
        if anomaly_type == "response_time":
            log["response_time"] *= random.uniform(5, 20)
        elif anomaly_type == "error_rate":
            log["status_code"] = random.choice([500, 503])
            log["response_time"] *= 2
            
        return log
    
    def generate_logs(self, count=1000, anomaly_ratio=None):
        if anomaly_ratio is None:
            anomaly_ratio = self.config.ANOMALY_RATIO
            
        logs = []
        for _ in range(count):
            if random.random() < anomaly_ratio:
                logs.append(self.generate_anomalous_log())
            else:
                logs.append(self.generate_normal_log())
        return logs
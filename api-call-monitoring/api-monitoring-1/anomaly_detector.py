import pandas as pd
import numpy as np
import joblib
import json
import os
import random
from sklearn.ensemble import IsolationForest
from datetime import datetime
import logging
from config import Config

class AnomalyDetector:
    def __init__(self, model_storage_path="models"):
        self.config = Config()
        self.models = {}
        self.traffic_baselines = {}
        self.logger = logging.getLogger(__name__)
        self.model_storage_path = model_storage_path
        os.makedirs(self.model_storage_path, exist_ok=True)
        
        # Service and environment definitions
        self.services = ["user-service", "payment-service", 
                        "inventory-service", "auth-service"]
        self.environments = ["on-prem", "aws-cloud", 
                           "azure-cloud", "gcp-cloud"]

    def save_models(self):
        """Save models and baselines to disk"""
        try:
            # Save models
            for (service, env), model in self.models.items():
                filename = f"{service}_{env}_model.joblib"
                joblib.dump(model, os.path.join(self.model_storage_path, filename))
            
            # Save baselines
            baselines_file = os.path.join(self.model_storage_path, "traffic_baselines.json")
            with open(baselines_file, 'w') as f:
                json.dump({
                    f"{service}_{env}": baseline 
                    for (service, env), baseline in self.traffic_baselines.items()
                }, f)
            
            self.logger.info(f"Saved {len(self.models)} models and baselines")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save models: {str(e)}")
            return False

    def load_models(self):
        """Load models and baselines from disk"""
        try:
            # Load models
            for filename in os.listdir(self.model_storage_path):
                if filename.endswith("_model.joblib"):
                    parts = filename.split('_')
                    service, env = parts[0], parts[1].replace('_model.joblib', '')
                    model = joblib.load(os.path.join(self.model_storage_path, filename))
                    self.models[(service, env)] = model
            
            # Load baselines
            baselines_file = os.path.join(self.model_storage_path, "traffic_baselines.json")
            if os.path.exists(baselines_file):
                with open(baselines_file, 'r') as f:
                    baselines = json.load(f)
                    self.traffic_baselines = {
                        (k.split('_')[0], k.split('_')[1]): v 
                        for k, v in baselines.items()
                    }
            
            self.logger.info(f"Loaded {len(self.models)} models and {len(self.traffic_baselines)} baselines")
            return len(self.models) > 0
        except Exception as e:
            self.logger.error(f"Failed to load models: {str(e)}")
            return False

    def train_models(self, historical_logs):
        """Train models with comprehensive validation"""
        try:
            df = pd.DataFrame(historical_logs)
            
            # Validate input
            if len(df) < 1000:
                self.logger.error("Need at least 1000 logs for training")
                return False
                
            # Add synthetic anomalies if needed
            if len(df[df['status_code'] >= 400]) < 50:
                df = pd.concat([df, pd.DataFrame(self._generate_synthetic_anomalies(100))])
                self.logger.info("Added 100 synthetic anomalies")
            
            # Train per service-environment
            trained_count = 0
            for (service, env), group in df.groupby(['service', 'environment']):
                if len(group) < 50:
                    self.logger.warning(f"Skipping {service}-{env} (only {len(group)} logs)")
                    continue
                    
                # Prepare features
                X = group[['response_time']].copy()
                X['error_flag'] = group['status_code'].apply(lambda x: 1 if x >= 400 else 0)
                
                # Train model
                model = IsolationForest(
                    n_estimators=200,
                    contamination=0.05,
                    random_state=42,
                    verbose=1
                )
                model.fit(X)
                self.models[(service, env)] = model
                trained_count += 1
                
                # Calculate traffic baseline
                self._calculate_traffic_baseline(service, env, group)
            
            self.logger.info(f"Trained {trained_count} models")
            return trained_count > 0
        except Exception as e:
            self.logger.error(f"Training failed: {str(e)}")
            return False

    def _calculate_traffic_baseline(self, service, env, group):
        """Calculate traffic statistics for a service-environment"""
        try:
            group['timestamp'] = pd.to_datetime(group['timestamp'])
            traffic = group.set_index('timestamp').resample('5min').size()
            
            if len(traffic) > 1:
                self.traffic_baselines[(service, env)] = {
                    'mean': float(traffic.mean()),
                    'std': float(traffic.std())
                }
        except Exception as e:
            self.logger.error(f"Failed to calculate baseline for {service}-{env}: {str(e)}")

    def detect_anomalies(self, new_logs):
        """Detect anomalies in new logs"""
        if not self.models:
            self.logger.warning("No trained models available")
            return []

        df = pd.DataFrame(new_logs)
        anomalies = []
        
        for (service, env), group in df.groupby(['service', 'environment']):
            if (service, env) not in self.models:
                continue
                
            # Prepare features
            X = group[['response_time']].copy()
            X['error_flag'] = group['status_code'].apply(lambda x: 1 if x >= 400 else 0)
            
            # Predict anomalies
            try:
                scores = self.models[(service, env)].decision_function(X)
                preds = self.models[(service, env)].predict(X)
                
                # Get anomaly indices
                anomaly_indices = np.where(preds == -1)[0]
                anomaly_count = len(anomaly_indices)
                
                if anomaly_count > 0:
                    self.logger.info(f"Found {anomaly_count} anomalies in {service}-{env}")
                    
                    # Format anomalies
                    for idx in anomaly_indices:
                        row = group.iloc[idx]
                        anomaly = row.to_dict()
                        anomaly['anomaly_type'] = self._classify_anomaly(row)
                        anomaly['anomaly_score'] = scores[idx]
                        anomalies.append(anomaly)
            except Exception as e:
                self.logger.error(f"Error detecting anomalies for {service}-{env}: {str(e)}")
                continue
            
        return anomalies

    def _classify_anomaly(self, row):
        """Determine anomaly type"""
        if row['status_code'] >= 500:
            return 'server_error'
        elif row['response_time'] > self.config.RESPONSE_TIME_THRESHOLD * 2:
            return 'high_latency'
        elif row['status_code'] >= 400:
            return 'client_error'
        return 'behavioral'

    def _generate_synthetic_anomalies(self, count):
        """Create obvious training anomalies"""
        anomalies = []
        for _ in range(count):
            anomalies.append({
                'timestamp': datetime.now().isoformat(),
                'service': random.choice(self.services),
                'environment': random.choice(self.environments),
                'status_code': random.choice([500, 503]),
                'response_time': random.uniform(5000, 10000),
                'user_id': f"user_{random.randint(1, 1000)}",
                'endpoint': "/api/synthetic",
                'request_size': random.randint(100, 5000),
                'response_size': random.randint(50, 3000),
                'language': "synthetic"
            })
        return anomalies
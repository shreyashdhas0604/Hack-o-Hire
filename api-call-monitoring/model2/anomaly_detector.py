import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from statsmodels.tsa.seasonal import STL
from config import Config
import logging

class AnomalyDetector:
    def __init__(self):
        self.config = Config()
        self.models = {}
        self.traffic_baselines = {}
        self.logger = logging.getLogger(__name__)
        
    def train_models(self, historical_logs):
        """Train models using historical log data"""
        df = pd.DataFrame(historical_logs)
        
        for (service, env), group in df.groupby(['service', 'environment']):
            # Features for anomaly detection
            X = group[['response_time']].copy()
            X['error_flag'] = group['status_code'].apply(lambda x: 1 if x >= 400 else 0)
            
            # Train Isolation Forest
            clf = IsolationForest(
                n_estimators=self.config.ISOLATION_FOREST_ESTIMATORS,
                contamination=self.config.CONTAMINATION,
                random_state=42
            )
            clf.fit(X)
            self.models[(service, env)] = clf
            
            # Establish traffic baselines (using 'min' instead of 'T')
            group['timestamp'] = pd.to_datetime(group['timestamp'])
            traffic = group.set_index('timestamp').resample('5min').size()
            self.traffic_baselines[(service, env)] = {
                'mean': traffic.mean(),
                'std': traffic.std()
            }
            
        self.logger.info(f"Trained models for {len(self.models)} service-environment combinations")
    
    def detect_anomalies(self, new_logs):
        """Detect anomalies in new logs"""
        anomalies = []
        df = pd.DataFrame(new_logs)
        
        for (service, env), group in df.groupby(['service', 'environment']):
            if (service, env) not in self.models:
                continue
                
            X = group[['response_time']].copy()
            X['error_flag'] = group['status_code'].apply(lambda x: 1 if x >= 400 else 0)
            
            # Predict anomalies
            preds = self.models[(service, env)].predict(X)
            scores = self.models[(service, env)].decision_function(X)
            
            # Add results to group
            group['anomaly_score'] = scores
            group['is_anomaly'] = preds == -1
            
            # Format anomalies
            for _, row in group[group['is_anomaly']].iterrows():
                anomaly = row.to_dict()
                anomaly['anomaly_type'] = self._determine_anomaly_type(row)
                anomalies.append(anomaly)
                
        return anomalies
    
    def detect_traffic_spikes(self, logs):
        """Detect unusual traffic patterns"""
        df = pd.DataFrame(logs)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        spikes = []
        
        for (service, env), group in df.groupby(['service', 'environment']):
            if (service, env) not in self.traffic_baselines:
                continue
                
            # Use 'min' instead of deprecated 'T'
            traffic = group.set_index('timestamp').resample('5min').size()
            baseline = self.traffic_baselines[(service, env)]
            
            # Calculate z-scores
            z_scores = (traffic - baseline['mean']) / baseline['std']
            spike_periods = z_scores[z_scores > 3].index
            
            for ts in spike_periods:
                spikes.append({
                    'timestamp': ts.isoformat(),
                    'service': service,
                    'environment': env,
                    'request_count': traffic[ts],
                    'z_score': z_scores[ts],
                    'anomaly_type': 'traffic_spike'
                })
                
        return spikes
    
    def _determine_anomaly_type(self, row):
        """Classify the type of anomaly"""
        if row['status_code'] >= 500:
            return 'server_error'
        elif row['response_time'] > self.config.RESPONSE_TIME_THRESHOLD * 2:
            return 'high_latency'
        elif row['status_code'] >= 400:
            return 'client_error'
        return 'behavioral'
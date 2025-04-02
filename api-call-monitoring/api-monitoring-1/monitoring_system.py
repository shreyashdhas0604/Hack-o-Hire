import time
import random
import logging
from log_generator import APILogGenerator
from anomaly_detector import AnomalyDetector
from ai_analyzer import AIAnalyzer
from data_storage import DataStorage
from config import Config

class MonitoringSystem:
    def __init__(self, simulate=True):
        self.config = Config()
        self.simulate = simulate
        self.generator = APILogGenerator()
        self.detector = AnomalyDetector()
        self.analyzer = AIAnalyzer()
        self.storage = DataStorage()
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize system
        self._initialize_system()

    def _initialize_system(self):
        """Initialize models and training"""
        # Try loading existing models
        if not self.detector.load_models():
            self.logger.info("No existing models found - training new models")
            
            # Generate substantial training data
            train_logs = self.generator.generate_logs(
                count=5000,
                anomaly_ratio=0.1  # 10% anomalies
            )
            self.storage.save_logs_to_csv(train_logs, "training_data.csv")
            
            # Train and save models
            if not self.detector.train_models(train_logs):
                raise RuntimeError("Model training failed")
                
            if not self.detector.save_models():
                raise RuntimeError("Model saving failed")
            
            self.logger.info("Successfully trained initial models")

    def run_continuous_monitoring(self, interval=60):
        """Main monitoring loop"""
        self.logger.info("Starting monitoring...")
        try:
            while True:
                # Get new logs
                new_logs = self._get_new_logs()
                self.storage.save_logs_to_csv(new_logs, "monitoring_logs.csv")
                
                # Detect anomalies
                anomalies = self.detector.detect_anomalies(new_logs)
                
                # Process and alert
                if anomalies:
                    self._process_anomalies(anomalies)
                
                # Periodic model saving
                if random.random() < 0.1:  # 10% chance to save
                    self.detector.save_models()
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.logger.info("Shutting down...")
            self.detector.save_models()
        except Exception as e:
            self.logger.error(f"Monitoring failed: {str(e)}")
            raise

    def _get_new_logs(self):
        """Get logs (simulated or real)"""
        if self.simulate:
            return self.generator.generate_logs(
                count=random.randint(50, 200),
                anomaly_ratio=self.config.ANOMALY_RATIO
            )
        # Else: Implement real log collection
        raise NotImplementedError("Real log collection not implemented")

    def _process_anomalies(self, anomalies):
        """Handle detected anomalies"""
        report = self.analyzer.generate_anomaly_report(anomalies)
        self.logger.info("\n=== ANOMALY REPORT ===")
        self.logger.info(report['analysis'])
        
        for anomaly in anomalies:
            alert = self.analyzer.generate_alert_message(anomaly)
            for line in alert.split('\n'):
                if line.startswith("ALERT:"):
                    self.logger.warning(line)
                else:
                    self.logger.info(line)
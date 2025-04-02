import time
import random
import logging
from log_generator import APILogGenerator
from anomaly_detector import AnomalyDetector
from ai_analyzer import AIAnalyzer
from config import Config

class MonitoringSystem:
    def __init__(self, simulate=True):
        self.config = Config()
        self.simulate = simulate
        self.generator = APILogGenerator()
        self.detector = AnomalyDetector()
        self.analyzer = AIAnalyzer()
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        initial_logs = self.generator.generate_logs(count=1000)
        self.detector.train_models(initial_logs)
        self.logger.info("System initialized")

    def run_continuous_monitoring(self, interval=60):
        self.logger.info("Starting monitoring...")
        try:
            while True:
                new_logs = self._get_new_logs()
                anomalies = self.detector.detect_anomalies(new_logs)
                
                if anomalies:
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
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped")
        except Exception as e:
            self.logger.error(f"Monitoring failed: {str(e)}")
            raise

    def _get_new_logs(self):
        if self.simulate:
            return self.generator.generate_logs(
                count=random.randint(50, 200),
                anomaly_ratio=self.config.ANOMALY_RATIO
            )
        raise NotImplementedError("Real log collection not implemented")
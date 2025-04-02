import google.generativeai as genai
import pandas as pd
from config import Config
import logging
import time
from datetime import datetime, timedelta

class AIAnalyzer:
    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger(__name__)
        self.last_api_call = None
        self.min_call_interval = timedelta(seconds=2)
        self.retry_delay = 60
        
        try:
            genai.configure(api_key=self.config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(
                self.config.GEMINI_MODEL,
                safety_settings=self.config.GEMINI_SAFETY_SETTINGS
            )
            self.logger.info("Gemini AI initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini: {str(e)}")
            # Fallback to basic analyzer without Gemini
            self.model = None
            self.logger.warning("Running in fallback mode without Gemini AI")

    def _enforce_rate_limit(self):
        """Ensure we don't exceed API rate limits"""
        if self.last_api_call:
            elapsed = datetime.now() - self.last_api_call
            if elapsed < self.min_call_interval:
                wait_time = (self.min_call_interval - elapsed).total_seconds()
                time.sleep(wait_time)
        self.last_api_call = datetime.now()

    def _generate_fallback_alert(self, anomaly):
        """Generate a basic alert when Gemini fails"""
        return (
            f"ALERT: {anomaly.get('anomaly_type', 'anomaly')} in "
            f"{anomaly.get('service', 'unknown service')} "
            f"({anomaly.get('environment', 'unknown env')})\n"
            f"Status: {anomaly.get('status_code', 'unknown')}\n"
            f"Response Time: {anomaly.get('response_time', 'unknown')}ms\n"
            f"Timestamp: {anomaly.get('timestamp', 'unknown')}"
        )

    def _generate_fallback_report(self, anomalies):
        """Generate a basic report when Gemini fails"""
        df = pd.DataFrame(anomalies)
        stats = {
            "total": len(anomalies),
            "services": df['service'].value_counts().to_dict(),
            "types": df['anomaly_type'].value_counts().to_dict()
        }
        return {
            "statistics": stats,
            "analysis": (
                f"Detected {stats['total']} anomalies across services. "
                f"Most affected: {max(stats['services'].items(), key=lambda x: x[1])[0]}. "
                f"Most common type: {max(stats['types'].items(), key=lambda x: x[1])[0]}."
            )
        }

    def generate_alert_message(self, anomaly):
        try:
            self._enforce_rate_limit()
            
            prompt = f"""
            Create a concise alert message for this API anomaly:
            Service: {anomaly.get('service', 'unknown')}
            Environment: {anomaly.get('environment', 'unknown')}
            Type: {anomaly.get('anomaly_type', 'unknown')}
            Status Code: {anomaly.get('status_code', 'unknown')}
            Response Time: {anomaly.get('response_time', 'unknown')}ms
            Timestamp: {anomaly.get('timestamp', 'unknown')}

            Provide:
            1. One-line summary (start with 'ALERT:')
            2. Probable cause (most likely technical reason)
            3. Recommended action (concrete technical steps)
            """
            
            response = self.model.generate_content(prompt)
            return response.text if response.text else self._generate_fallback_alert(anomaly)
            
        except Exception as e:
            if "quota" in str(e).lower() or "429" in str(e):
                self.logger.error(f"Gemini API quota exceeded, waiting {self.retry_delay}s")
                time.sleep(self.retry_delay)
                return self._generate_fallback_alert(anomaly)
            self.logger.error(f"Failed to generate alert: {str(e)}")
            return self._generate_fallback_alert(anomaly)

    def generate_anomaly_report(self, anomalies):
        if not anomalies:
            return {"analysis": "No anomalies detected"}
            
        try:
            self._enforce_rate_limit()
            
            df = pd.DataFrame(anomalies)
            stats = {
                "total": len(anomalies),
                "services": df['service'].value_counts().to_dict(),
                "types": df['anomaly_type'].value_counts().to_dict(),
                "environments": df['environment'].value_counts().to_dict()
            }

            prompt = f"""
            Analyze these API anomalies (technical analysis for engineers):
            Total: {stats['total']}
            Services affected: {stats['services']}
            Environments affected: {stats['environments']}
            Anomaly types: {stats['types']}

            Provide:
            1. Root cause analysis (technical hypotheses)
            2. Impact assessment (technical consequences)
            3. Recommendations (actionable engineering steps)
            Format with clear section headings.
            """
            
            response = self.model.generate_content(prompt)
            return {
                "statistics": stats,
                "analysis": response.text if response.text else self._generate_fallback_report(anomalies)['analysis']
            }
            
        except Exception as e:
            if "quota" in str(e).lower() or "429" in str(e):
                self.logger.error(f"Gemini API quota exceeded, waiting {self.retry_delay}s")
                time.sleep(self.retry_delay)
                return self._generate_fallback_report(anomalies)
            self.logger.error(f"Failed to generate report: {str(e)}")
            return self._generate_fallback_report(anomalies)
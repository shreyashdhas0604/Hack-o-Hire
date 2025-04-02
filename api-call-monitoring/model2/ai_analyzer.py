import google.generativeai as genai
import pandas as pd
from config import Config
import logging

class AIAnalyzer:
    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger(__name__)
        try:
            genai.configure(api_key=self.config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(self.config.GEMINI_MODEL)
            self.logger.info("Gemini AI initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini: {str(e)}")
            raise RuntimeError(f"Gemini initialization failed: {str(e)}")

    def generate_alert_message(self, anomaly):
        try:
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
            2. Probable cause
            3. Recommended action
            """
            
            response = self.model.generate_content(prompt)
            return response.text if response.text else "Could not generate alert message"
        except Exception as e:
            self.logger.error(f"Failed to generate alert: {str(e)}")
            return f"ALERT: Anomaly detected in {anomaly.get('service', 'unknown service')}"

    def generate_anomaly_report(self, anomalies):
        if not anomalies:
            return {"analysis": "No anomalies detected"}
            
        try:
            df = pd.DataFrame(anomalies)
            stats = {
                "total": len(anomalies),
                "services": df['service'].value_counts().to_dict(),
                "types": df['anomaly_type'].value_counts().to_dict()
            }

            prompt = f"""
            Analyze these API anomalies:
            Total: {stats['total']}
            Services affected: {stats['services']}
            Anomaly types: {stats['types']}

            Provide:
            1. Root cause analysis
            2. Impact assessment
            3. Recommendations
            """
            
            response = self.model.generate_content(prompt)
            return {
                "statistics": stats,
                "analysis": response.text if response.text else "No analysis available"
            }
        except Exception as e:
            self.logger.error(f"Failed to generate report: {str(e)}")
            return {"analysis": "Failed to generate analysis report"}
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Log Generation Settings
    NORMAL_TRAFFIC_MEAN = 100  # ms
    NORMAL_TRAFFIC_STD = 20
    ANOMALY_RATIO = 0.01  # 1% anomalies in generated logs
    
    # Anomaly Detection Settings
    ISOLATION_FOREST_ESTIMATORS = 100
    CONTAMINATION = 0.01
    
    # Alerting Thresholds
    RESPONSE_TIME_THRESHOLD = 1000  # ms
    ERROR_RATE_THRESHOLD = 0.05  # 5%
    
    # Gemini Settings
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-pro')
    
    # Safety Settings for Gemini
    GEMINI_SAFETY_SETTINGS = {
        "HARASSMENT": "block_none",
        "HATE_SPEECH": "block_none",
        "SEXUALLY_EXPLICIT": "block_none",
        "DANGEROUS_CONTENT": "block_none"
    }
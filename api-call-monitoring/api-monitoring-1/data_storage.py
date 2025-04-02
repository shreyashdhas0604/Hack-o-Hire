# data_storage.py
import pandas as pd
import os
from datetime import datetime
import logging

class DataStorage:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def save_logs_to_csv(self, logs, filename=None):
        """Save logs to CSV file"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"api_logs_{timestamp}.csv"
            
            filepath = os.path.join(self.data_dir, filename)
            df = pd.DataFrame(logs)
            
            # Check if file exists to determine if we need headers
            write_header = not os.path.exists(filepath)
            
            df.to_csv(filepath, mode='a', header=write_header, index=False)
            self.logger.info(f"Saved {len(logs)} logs to {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Failed to save logs: {str(e)}")
            return None
    
    def load_logs_from_csv(self, filename="api_logs.csv"):
        """Load logs from CSV file"""
        try:
            filepath = os.path.join(self.data_dir, filename)
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
                return df.to_dict('records')
            return []
        except Exception as e:
            self.logger.error(f"Failed to load logs: {str(e)}")
            return []
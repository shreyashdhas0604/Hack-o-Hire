from monitoring_system import MonitoringSystem
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--real', action='store_true', help='Use real logs')
    parser.add_argument('--retrain', action='store_true', help='Force retrain models')
    args = parser.parse_args()
    
    try:
        monitor = MonitoringSystem(simulate=not args.real)
        
        if args.retrain:
            monitor.logger.info("Forcing model retraining...")
            # Implementation would go here
            
        monitor.run_continuous_monitoring()
        
    except Exception as e:
        print(f"Failed to start monitoring: {str(e)}")
        raise

if __name__ == "__main__":
    main()
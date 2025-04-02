from monitoring_system import MonitoringSystem
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--real', action='store_true', help='Use real logs')
    args = parser.parse_args()
    
    try:
        monitor = MonitoringSystem(simulate=not args.real)
        monitor.run_continuous_monitoring()
    except Exception as e:
        print(f"Failed to start monitoring: {str(e)}")

if __name__ == "__main__":
    main()
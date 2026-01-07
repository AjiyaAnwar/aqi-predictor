"""
Main orchestrator for AQI Prediction System
"""
import sys
import os

# Add src to path
sys.path.append('src')

def main():
    print("=" * 60)
    print("           AQI PREDICTION SYSTEM")
    print("=" * 60)
    print("\n1. Collect AQI Data")
    print("2. Launch Dashboard")
    print("3. Train Model")
    print("4. Exit")
    
    choice = input("\nSelect option (1-4): ")
    
    if choice == "1":
        print("\nRunning data collection...")
        os.system("python src/data/collector.py")
    
    elif choice == "2":
        print("\nLaunching dashboard...")
        print("Open your browser at: http://localhost:8501")
        os.system("streamlit run app/dashboard.py --server.port 8501 --server.address 0.0.0.0")
    
    elif choice == "3":
        print("\nTraining model...")
        os.system("python src/models/trainer.py")
    
    elif choice == "4":
        print("\nGoodbye! 👋")
    
    else:
        print("\nInvalid choice!")

if __name__ == "__main__":
    main()

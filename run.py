# run.py
"""
Script di lancio per l'applicazione EDI_FORECAST
Uso: python run.py
"""
import subprocess
import sys

if __name__ == "__main__":
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "src/app.py",
        "--server.port=8501",
        "--server.address=0.0.0.0"
    ])
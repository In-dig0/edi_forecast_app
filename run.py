# run.py
"""
Script di lancio per l'applicazione EDI_FORECAST
Uso: python run.py
"""
import subprocess
import sys
import os

if __name__ == "__main__":
    # Rileva se siamo in un container Docker
    in_docker = os.path.exists('/.dockerenv') or os.getenv('DOCKER_CONTAINER') == 'true'
    
    # Configura l'indirizzo in base all'ambiente
    server_address = "0.0.0.0" if in_docker else "localhost"
    
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "src/app.py",
        "--server.port=8501",
        f"--server.address={server_address}"
    ])
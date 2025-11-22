import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# BASE_DIR ora punta alla root del progetto (EDI_FORECAST)
# __file__ è in src/utils/config.py, quindi risaliamo di 2 livelli
BASE_DIR = Path(__file__).parent.parent.parent  # da src/utils/ -> src/ -> EDI_FORECAST/

# Percorsi configurabili
DATA_DIR = BASE_DIR / "src" / "data"
BACKUP_DIR = DATA_DIR / "backup"
OUTPUT_DIR = DATA_DIR / "output" / "forecast"  # Nota: output/forecast non output/forecasts
USER_DIR = DATA_DIR / "users"
USERS_FILE = USER_DIR / "users.json"
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "app.log"

# Crea le directory se non esistono
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Configurazioni email
ALLOWED_DOMAINS = ["@iph.it"]
MAILJET_URL = os.getenv("MAILJET_URL", "https://api.mailjet.com/v3.1/send")
MAILJET_API_KEY = os.getenv("MAILJET_API_KEY")
MAILJET_API_SECRET = os.getenv("MAILJET_API_SECRET")
MAILJET_SENDER_EMAIL = os.getenv("MAILJET_SENDER_EMAIL", "noreply@forecastapp.com")
MAILJET_SENDER_NAME = os.getenv("MAILJET_SENDER_NAME", "Forecast WebApp")
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

# Configurazioni invio notifiche con APPRISE
APPRISE_URL = os.getenv("APPRISE_URL")
APPRISE_NTFY_HOST = os.getenv("APPRISE_NTFY_HOST")  
APPRISE_NTFY_TOPIC = os.getenv("APPRISE_NTFY_TOPIC")
APPRISE_TOKEN = os.getenv("APPRISE_TOKEN")


# Configurazioni APP
APP_URL = os.getenv("APP_URL", "http://localhost:8501/")
APP_NAME = "EDI Forecast Requirements WebApp"
APP_VERSION = "1.0.0"

# Configurazioni LOGGING
# Livelli disponibili: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = os.getenv("APP_LOG_LEVEL", "DEBUG").upper()
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
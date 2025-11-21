import requests
import json
from streamlit import json
from src.utils.logger import setup_logger
from utils.config import APPRISE_URL, APPRISE_NTFY_HOST, APPRISE_NTFY_TOPIC
import json

# Inizializza il logger per questa pagina
logger = setup_logger("login_page")

def apprise_send_notification(title: str, message: str, priority: int = 3, tags: list = None, click_url: str = None) -> (tuple[bool, str]):
    if APPRISE_URL:
        # Costruisci URL NTFY con parametri
        ntfy_url = f"{APPRISE_NTFY_HOST}/{APPRISE_NTFY_TOPIC}?priority={priority}"
            # Aggiungi markdown=yes per forzare l'interpretazione
        ntfy_url += "&format=markdown"
        
        # Aggiungi tags
        if tags:
            tags_str = ",".join(tags)
            ntfy_url += f"&tags={tags_str}"
        
        # Aggiungi click URL
        if click_url:
            ntfy_url += f"&click={click_url}"
        try:
            headers = {
            "Content-Type": "application/json"
            }
            payload = {
                "urls": [ntfy_url],
                "title": title,
                "body": message,
                "format": "text", 
                # 'tag' è opzionale, puoi usarlo per filtrare i servizi, ma non è necessario qui
            }

            response = requests.post(
                url=APPRISE_URL,
                headers=headers,
                data=json.dumps(payload)
                )
            if response.status_code in (200, 201, 204):
                return True, ""
            else:
                return False, f"Apprise error: {response.status_code} {response.text}"
        except Exception as e:
            return False, f"Exception sending notification: {e}"
    else:
        logger.error("Apprise URL endpoint is not set. Notification not sent.")
        logger.debug("=== DEBUG NOTIFICATION ===\nTitle: %s\nMessage: %s\n==============", title, message)
        return False, "Apprise URL endpoint is not set. Notification not sent."
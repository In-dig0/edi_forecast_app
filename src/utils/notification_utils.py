import requests
import json
from src.utils.logger import setup_logger
from utils.config import APPRISE_URL, APPRISE_NTFY_HOST, APPRISE_NTFY_TOPIC, APPRISE_TOKEN

# Inizializza il logger per questa pagina
logger = setup_logger("notification_utils")

def apprise_send_notification(title: str, message: str, priority: int = 3, tags: list = None, click_url: str = None) -> tuple[bool, str]:
    """
    Invia notifica tramite Apprise -> NTFY
    
    Args:
        title: Titolo della notifica
        message: Messaggio della notifica (supporta Markdown)
        priority: Priorità (1=min, 2=low, 3=default, 4=high, 5=urgent)
        tags: Lista di emoji tags (es: ["warning", "fire"])
        click_url: URL da aprire al click
    
    Returns:
        tuple: (success: bool, error_message: str)
    """
    if not APPRISE_URL:
        error_msg = "Apprise URL endpoint is not set. Notification not sent."
        logger.error(error_msg)
        logger.debug("=== DEBUG NOTIFICATION ===\nTitle: %s\nMessage: %s\n==============", title, message)
        return False, error_msg
    
    # Assicura che l'URL termini con /
    apprise_url = APPRISE_URL if APPRISE_URL.endswith('/') else f"{APPRISE_URL}/"
    
    try:
        # Costruisci URL NTFY base con TUTTI i parametri nell'URL
        ntfy_url = f"ntfy://{APPRISE_NTFY_HOST}/{APPRISE_NTFY_TOPIC}"
        
        # Costruisci URL NTFY con parametri
        ntfy_url += f"?priority={priority}"
        
        # Aggiungi markdown=yes per forzare l'interpretazione
        ntfy_url += "&format=markdown"
        
        # Aggiungi tags
        if tags:
            tags_str = ",".join(tags)
            ntfy_url += f"&tags={tags_str}"
        
        # Aggiungi click URL
        if click_url:
            ntfy_url += f"&click={click_url}"
        
        # Payload Apprise
        payload = {
            "urls": [ntfy_url],
            "title": title,
            "body": message,
            "format": "markdown",
        }


        # Headers
        headers = {"Content-Type": "application/json"}
        if APPRISE_TOKEN:
            headers["Authorization"] = f"Bearer {APPRISE_TOKEN}"
        
        # DEBUG logging
        logger.debug(f"APPRISE_URL: {apprise_url}")
        logger.debug(f"APPRISE_NTFY_HOST: {APPRISE_NTFY_HOST}")
        logger.debug(f"APPRISE_NTFY_TOPIC: {APPRISE_NTFY_TOPIC}")
        logger.debug(f"APPRISE_TOKEN: {APPRISE_TOKEN[:20]}..." if APPRISE_TOKEN else "No token")
        logger.debug(f"Title: {title}")
        logger.debug(f"Message: {message}")
        logger.debug(f"Priority: {priority}")
        logger.debug(f"Tags: {tags}")
        logger.debug(f"Full NTFY URL: {ntfy_url}")
        logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
        
        # Invio richiesta
        response = requests.post(
            url=apprise_url,
            headers=headers,
            data=json.dumps(payload),
            timeout=30
        )
        
        if response.status_code in (200, 201, 204):
            logger.info(f"Notification sent successfully: {title}")
            return True, ""
        else:
            error_msg = f"Apprise error: {response.status_code} {response.text}"
            logger.error(error_msg)
            return False, error_msg
            
    except requests.exceptions.Timeout:
        error_msg = "Timeout sending notification (30s)"
        logger.error(error_msg)
        return False, error_msg
    except requests.exceptions.RequestException as e:
        error_msg = f"Connection error sending notification: {e}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Exception sending notification: {e}"
        logger.error(error_msg)
        return False, error_msg
import requests
import json
from src.utils.logger import setup_logger
from utils.config import APPRISE_NOTFICATION_ENABLED, APPRISE_URL, APPRISE_TOKEN, APPRISE_NTFY_TOKEN, APPRISE_NTFY_HOST, APPRISE_NTFY_TOPIC

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
    if APPRISE_NOTFICATION_ENABLED:
        if not APPRISE_URL:
            error_msg = "Apprise URL endpoint is not set. Notification not sent."
            logger.error(error_msg)
            logger.debug("=== DEBUG NOTIFICATION ===\nTitle: %s\nMessage: %s\n==============", title, message)
            return False, error_msg
        else:
            apprise_url = APPRISE_URL

        if not APPRISE_TOKEN:
            error_msg = "Apprise TOKEN not found. Notification not sent."
            logger.error(error_msg)
            logger.debug("=== DEBUG NOTIFICATION ===\nTitle: %s\nMessage: %s\n==============", title, message)
            return False, error_msg
        else:
            apprise_token = APPRISE_TOKEN

        if not APPRISE_NTFY_TOKEN:
            error_msg = "Apprise NTFY TOKEN not found. Notification not sent."
            logger.error(error_msg)
            logger.debug("=== DEBUG NOTIFICATION ===\nTitle: %s\nMessage: %s\n==============", title, message)
            return False, error_msg
        else:
            apprise_ntfy_token = APPRISE_NTFY_TOKEN

        if not APPRISE_NTFY_HOST:
            error_msg = "Apprise NTFY HOST not found. Notification not sent."
            logger.error(error_msg)
            logger.debug("=== DEBUG NOTIFICATION ===\nTitle: %s\nMessage: %s\n==============", title, message)
            return False, error_msg
        else:
            apprise_ntfy_host = APPRISE_NTFY_HOST 

        if not APPRISE_NTFY_TOPIC:
            error_msg = "Apprise NTFY TOPIC not found. Notification not sent."
            logger.error(error_msg)
            logger.debug("=== DEBUG NOTIFICATION ===\nTitle: %s\nMessage: %s\n==============", title, message)
            return False, error_msg
        else:
            apprise_ntfy_topic = APPRISE_NTFY_TOPIC 

        try:
            ntfy_url = (
                f"ntfy://{apprise_ntfy_host}/{apprise_ntfy_topic}?"
                f"token={apprise_ntfy_token}&"
                f"priority={priority}&"
                f"format=markdown"
            )
        
            # Payload Apprise
            payload = {
                "urls": [ntfy_url],
                "title": title,
                "body": message,
                "tag": ",".join(tags) if tags else "",
            }

            # Headers
            headers = {"Content-Type": "application/json"}
            if apprise_token:
                headers["Authorization"] = f"Bearer {apprise_token}"
        
            # DEBUG logging
            logger.debug(f"APPRISE_URL: {apprise_url}")
            logger.debug(f"APPRISE_NTFY_HOST: {apprise_ntfy_host}")
            logger.debug(f"APPRISE_NTFY_TOPIC: {apprise_ntfy_topic}")
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
                json=payload,
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
    else:
        logger.debug("Apprise notifications are disabled. Skipping notification send.")
        logger.debug("=== DEBUG NOTIFICATION ===\nTitle: %s\nMessage: %s\n==============", title, message)
        return True, "Apprise notifications are disabled."    
import requests
from src.utils.logger import setup_logger
from utils.config import MAILJET_URL, MAILJET_API_KEY, MAILJET_API_SECRET, MAILJET_SENDER_EMAIL, MAILJET_SENDER_NAME, DEBUG_MODE

# Inizializza il logger per questa pagina
logger = setup_logger("login_page")

def mailjet_send_email(to_email: str, subject: str, text_content: str) -> (tuple[bool, str]):
    if MAILJET_API_KEY and MAILJET_API_SECRET:
        try:
            url = MAILJET_URL
            data = {"Messages": [{"From": {"Email": MAILJET_SENDER_EMAIL, "Name": MAILJET_SENDER_NAME},
                                  "To": [{"Email": to_email}],
                                  "Subject": subject,
                                  "TextPart": text_content}]}
            resp = requests.post(url, auth=(MAILJET_API_KEY, MAILJET_API_SECRET), json=data, timeout=10)
            if resp.status_code in (200, 201):
                return True, ""
            else:
                return False, f"Mailjet error: {resp.status_code} {resp.text}"
        except Exception as e:
            return False, f"Exception sending email: {e}"
    else:
        logger.error("Mailjet API keys are not set. Email not sent.")
        logger.debug("=== DEBUG EMAIL ===\nTo: %s\nSubject: %s\nBody: %s\n==============", to_email, subject, text_content)
        return False, "Mailjet API keys are not set. Email not sent."

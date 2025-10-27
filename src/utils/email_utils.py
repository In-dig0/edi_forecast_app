import requests
from utils.config import MAILJET_URL, MAILJET_API_KEY, MAILJET_API_SECRET, MAILJET_SENDER_EMAIL, MAILJET_SENDER_NAME, DEBUG_MODE

def mailjet_send_email(to_email: str, subject: str, text_content: str) -> (bool, str):
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
        if DEBUG_MODE:
            print("=== DEBUG EMAIL ===\nTo:", to_email, "\nSubject:", subject, "\nBody:", text_content, "\n==============")
        return True, ""

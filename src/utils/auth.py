import json
import os
import random
import string
from datetime import datetime, timedelta
from utils.email_utils import mailjet_send_email
from utils.config import USERS_FILE, ALLOWED_DOMAINS


# -----------------------------
# FUNZIONI BASE
# -----------------------------
def load_users():
    """Carica gli utenti dal file JSON (come dict {email: user_data})"""
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Se era una lista, convertila subito
    if isinstance(data, list):
        users_dict = {}
        for user in data:
            if "email" in user:
                users_dict[user["email"].lower()] = user
        save_users(users_dict)
        return users_dict

    # Se era già un dizionario, normalizza chiavi in minuscolo
    return {k.lower(): v for k, v in data.items()}


def save_users(users: dict):
    """Salva gli utenti nel file JSON"""
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)


def is_allowed_domain(email):
    """Verifica che il dominio email sia consentito"""
    return any(email.endswith(domain) for domain in ALLOWED_DOMAINS)


def generate_otp(length=6):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))


def get_user_by_email(email):
    """Restituisce l'utente corrispondente, oppure None"""
    users = load_users()
    return users.get(email.lower())


def get_all_users():
    """Restituisce la lista di tutti gli utenti registrati (per admin)"""
    users = load_users()
    return list(users.values())


# -----------------------------
# REGISTRAZIONE / ATTIVAZIONE
# -----------------------------
def register_user(name, surname, email, role="sales_user"):
    email = email.strip().lower()
    if not is_allowed_domain(email):
        return False, "Dominio email non ammesso."

    users = load_users()
    if email in users:
        return False, "User already registered."

    activation_code = generate_otp()
    new_user = {
        "name": name,
        "surname": surname,
        "email": email,
        "role": role,
        "activation_code": activation_code,
        "is_active": False,
        "created_at": datetime.now().isoformat(),
        "otp_expires_at": (datetime.now() + timedelta(minutes=10)).isoformat()
    }

    users[email] = new_user
    save_users(users)

    subject = "Codice di attivazione Forecast WebApp"
    message = (
        f"Ciao {name} {surname},\n\n"
        f"Il tuo codice di attivazione è: {activation_code}\n"
        "Questo codice scadrà tra 10 minuti."
    )
    mailjet_send_email(email, subject, message)
    return True, "Codice di attivazione inviato via email."


def activate_user(email, activation_code):
    email = email.strip().lower()
    users = load_users()
    user = users.get(email)
    if not user:
        return False, "User not found."

    if user.get("activation_code") != activation_code:
        return False, "Invalid OTP code."

    expiry = datetime.fromisoformat(user.get("otp_expires_at"))
    if datetime.now() > expiry:
        return False, "OTP code expired."

    user["is_active"] = True
    users[email] = user
    save_users(users)
    return True, "User activated successfully!"


# -----------------------------
# LOGIN / OTP
# -----------------------------
def send_login_code(email):
    email = email.strip().lower()
    users = load_users()
    user = users.get(email)

    if not user:
        return False, "User not registered."
    if not user.get("is_active"):
        return False, "User not active."

    otp = generate_otp()
    user["login_code"] = otp
    user["otp_expires_at"] = (datetime.now() + timedelta(minutes=480)).isoformat()

    users[email] = user
    save_users(users)

    subject = "Codice di accesso EDI Forecast WebApp"
    APP_LINK = os.getenv("APP_LINK", "https://forecast-webapp.example.com")
    message = (
        f"Ciao {user.get('name', '')},\n\n"
        f"Il tuo codice di accesso è: {otp}\n"
        "Inseriscilo entro 10 minuti per accedere."
    )
    mailjet_send_email(email, subject, message)
    return True, "Codice di accesso inviato via email."


def verify_token(email, token):
    email = email.strip().lower()
    users = load_users()
    user = users.get(email)
    if not user:
        return False, "Utente non trovato."
    if not user.get("is_active"):
        return False, "Utente non attivo."

    expiry = datetime.fromisoformat(user.get("otp_expires_at"))
    if datetime.now() > expiry:
        return False, "OTP code expired."

    if token == user.get("login_code"):
        return True, "Login successful!"
    return False, "Invalid OTP code."


# -----------------------------
# AGGIORNAMENTO PROFILO
# -----------------------------
def update_user_data(email, updates, allow_role_change=False):
    """
    Aggiorna i dati di un utente
    
    Args:
        email: Email dell'utente da aggiornare
        updates: Dizionario con i campi da aggiornare
        allow_role_change: Se True, permette di modificare il campo 'role' (solo per admin)
    
    Returns:
        tuple: (success: bool, message: str)
    """
    email = email.strip().lower()
    users = load_users()
    if email not in users:
        return False, "User not found"

    # Campi sempre protetti (non modificabili)
    protected_fields = [
        "email", "activation_code", "otp_expires_at",
        "login_code", "created_at"
    ]

    # Se non è consentito modificare il ruolo, aggiungilo ai campi protetti
    if not allow_role_change:
        protected_fields.append("role")
        protected_fields.append("is_active")

    # Rimuovi i campi protetti dagli aggiornamenti
    for field in protected_fields:
        updates.pop(field, None)

    user = users[email]
    user.update(updates)
    users[email] = user
    save_users(users)
    return True, "User data updated successfully"


def get_user_data(email):
    """Restituisce i dati completi di un utente"""
    return get_user_by_email(email)


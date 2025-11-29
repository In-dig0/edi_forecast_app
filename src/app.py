import streamlit as st
import base64
from pathlib import Path
import os


from src.utils.auth import get_user_data
from src.utils.config import APP_NAME, APP_VERSION

from pages import (
    info_page,
    registration_page,
    login_page,
    profile_page,
    upload_forecast_page,
    view_forecast_page,
    logout_page,
    user_list_page
)

# ──────────────────────────────────────────────
# App configuration
# ──────────────────────────────────────────────
st.set_page_config(page_title=APP_NAME, page_icon="🚀", layout="wide")

# ──────────────────────────────────────────────
# Session defaults
# ──────────────────────────────────────────────
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("user_email", None)
st.session_state.setdefault("admin_editing_user", None)

# ──────────────────────────────────────────────
# Sidebar logo
# ──────────────────────────────────────────────
logo_path = Path(__file__).parent / "images" / "logo-iph.png"
if logo_path.exists():
    st.logo(str(logo_path), size="large")

# ──────────────────────────────────────────────
# CSS per ingrandire il logo
# ──────────────────────────────────────────────
st.markdown(
    """
    <style>
    [data-testid="stSidebarLogo"] img {
        width: 200px !important;
        max-width: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ──────────────────────────────────────────────
# Define pages
# ──────────────────────────────────────────────
info = st.Page(info_page.page, title="Info", icon="ℹ️", url_path="/info")
registration = st.Page(registration_page.page, title="Register", icon="🧾", url_path="/register")
login = st.Page(login_page.page, title="Login", icon="🔐", url_path="/login")
profile = st.Page(profile_page.page, title="Profile", icon="👤", url_path="/profile")
upload_forecast = st.Page(upload_forecast_page.page, title="Upload Forecast", icon="🎯", url_path="/upload_forecast")
view_forecast = st.Page(view_forecast_page.page, title="View Forecast", icon="📊", url_path="/view_forecast")
user_list = st.Page(user_list_page.page, title="User List", icon="👥", url_path="/user_list")
logout = st.Page(logout_page.page, title="Logout", icon="🚪", url_path="/logout")

# ──────────────────────────────────────────────
# Navigation logic basata sul ruolo
# ──────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    menu_pages = [info, registration, login]
    account_pages = []
else:
    # Recupera il ruolo dell'utente loggato
    user_email = st.session_state.get("user_email")
    user = get_user_data(user_email) or {}
    user_role = user.get("role", "sales_role")
    
    account_pages = [profile, logout]
    if user_role == "admin_role":
        # Menu per admin
        menu_pages = [info, view_forecast, user_list]
    else:
        # Menu per sales_user (default)
        menu_pages = [info, upload_forecast, view_forecast]


# ──────────────────────────────────────────────
# Render navigation
# ──────────────────────────────────────────────
nav = st.navigation({"Menù": menu_pages}|{"Account": account_pages}, position="sidebar")

# ──────────────────────────────────────────────
# Gestione navigazione automatica per admin editing
# ──────────────────────────────────────────────
if st.session_state.get("admin_editing_user"):
    # Se l'admin sta editando un utente, forza la navigazione a Profile
    nav = st.navigation([profile], position="sidebar")

# ──────────────────────────────────────────────
# User Profile nella sidebar (solo se loggato)
# ──────────────────────────────────────────────
if st.session_state.get("logged_in") and st.session_state.get("user_email"):
    user_email = st.session_state["user_email"]
    user = get_user_data(user_email) or {}
    user_role = user.get("role", "sales_user")
    
    with st.sidebar:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style="background-color: #1e1e1e; padding: 15px; border-radius: 8px; margin-top: 20px;">
                <h3 style="margin: 0 0 10px 0; color: #ffffff; font-size: 16px;">👤 User Profile</h3>
                <p style="margin: 5px 0; font-size: 13px;">
                    <strong>📧 Email:</strong><br>
                    <span style="color: #4CAF50;">{user_email}</span>
                </p>
                <p style="margin: 5px 0; font-size: 13px;">
                    <strong>🔑 Role:</strong><br>
                    <span style="color: #2196F3;">{user_role}</span>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

nav.run()
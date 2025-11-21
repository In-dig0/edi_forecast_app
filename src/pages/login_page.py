import streamlit as st
import time
from src.utils.sidebar_style import apply_sidebar_style
from src.utils.auth import send_login_code, verify_token, get_user_by_email
from src.utils.logger import setup_logger
from src.utils.notification_utils import apprise_send_notification


# Inizializza il logger per questa pagina
logger = setup_logger("login_page")

def page():
    apply_sidebar_style()    
    st.title("🔐 :orange[Login]")
    st.divider()
    
    #logger.info("Login page accessed")

    st.markdown(":yellow[Login using your registered email and a one-time password (OTP) sent to your email.]")
    st.markdown("")
    st.markdown("")
    tab1, tab2 = st.tabs(["📩 Request OTP", "🔑 Login with OTP"])

    with tab1:
        st.markdown("Enter your registered email to receive an OTP code.")
        with st.form(key="request_otp_form"):
            email = st.text_input("Email", key="request_otp_email")
            submit = st.form_submit_button("📨 Send OTP")
        
        if submit:
            email = email.strip().lower()
            logger.debug(f"OTP request initiated for email: {email}")
            
            if not email:
                logger.warning("OTP request failed: empty email")
                st.warning("Enter an email address.")
            else:
                user = get_user_by_email(email)
                if not user:
                    logger.warning(f"OTP request failed: user not found - {email}")
                    st.error("No user found with this email.")
                elif not user.get("is_active"):
                    logger.warning(f"OTP request failed: inactive account - {email}")
                    st.warning("Account not active. Complete registration first.")
                else:
                    sent, msg = send_login_code(email)
                    if sent:
                        logger.info(f"OTP sent successfully to {email}")
                        st.success(f"✅ OTP sent to {email}.")
                        st.session_state["_pending_login_email"] = email
                    else:
                        logger.error(f"OTP sending failed for {email}: {msg}")
                        st.error(f"❌ Error sending code: {msg}")

    with tab2:
        pre_email = st.session_state.get("_pending_login_email", "")
        with st.form(key="login_form"):
            login_email = st.text_input("Email", value=pre_email, key="login_email")
            login_code = st.text_input("OTP Code", key="login_code")
            login_submit = st.form_submit_button("🔓 Login")
        
        if login_submit:
            login_email = login_email.strip().lower()
            login_code = login_code.strip()
            logger.debug(f"Login attempt for email: {login_email}")
            
            if not login_email or not login_code:
                logger.warning(f"Login failed: missing credentials for {login_email}")
                st.warning("Enter both email and OTP code.")
            else:
                ok, msg = verify_token(login_email, login_code)
                if ok:
                    logger.info(f"User logged in successfully: {login_email}")
                    st.success("✅ Logged in successfully!")
                    retcode, retmsg = apprise_send_notification(
                        title="User Login",
                        message=f"User with email {login_email} has logged in.",
                        priority=3,
                        tags=["login", "user"]
                    )
                    if not retcode:
                        logger.error(f"Failed to send notification for successful login: {retmsg}")
                    st.session_state["logged_in"] = True
                    st.session_state["user_email"] = login_email
                    st.session_state["_pending_login_email"] = ""
                    with st.spinner("Redirecting..."):
                        time.sleep(1)
                    st.rerun()
                else:
                    logger.warning(f"Login failed for {login_email}: {msg}")
                    st.error(f"❌ {msg or 'Invalid or expired OTP.'}")
                    retcode, retmsg = apprise_send_notification(
                        title="Failed Login Attempt",
                        message=f"Failed login attempt for email {login_email}. Reason: {msg or 'Invalid or expired OTP.'}",
                        priority=5,
                        tags=["login", "user", "failed"]
                    )
                    if not retcode:
                        logger.error(f"Failed to send notification for failed login attempt: {retmsg}")
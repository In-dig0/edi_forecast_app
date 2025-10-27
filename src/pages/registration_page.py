import streamlit as st
from src.utils.sidebar_style import apply_sidebar_style
from src.utils.auth import register_user, activate_user, get_user_by_email, send_login_code
from src.utils.config import ALLOWED_DOMAINS
from src.utils.logger import setup_logger

# Inizializza il logger per questa pagina
logger = setup_logger("registration_page")

def page():
    apply_sidebar_style()  
    st.session_state.on_upload_page = False
    st.title(f"🧾 :orange[Registration]")
    st.divider()
    
    #logger.info("Registration page accessed")
  
    st.markdown(":yellow[Fill in the fields to create your profile and receive an activation code via email.]")
    st.markdown("")
    st.markdown("")
    tab1, tab2 = st.tabs(["📝 Register & send code", "🔑 Verify activation code"])

    with tab1:
        with st.form(key="registration_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Name")
            with col2:
                surname = st.text_input("Surname")
            email = st.text_input("Email")
            submit = st.form_submit_button("📩 Send activation code")

        if submit:
            logger.debug(f"Registration attempt - Name: {name}, Surname: {surname}, Email: {email}")
            
            if not name.strip() or not surname.strip() or not email.strip():
                logger.warning("Registration failed: missing required fields")
                st.warning("All fields are required.")
            else:
                normalized_email = email.strip()
                if not any(normalized_email.endswith(d) for d in ALLOWED_DOMAINS):
                    logger.warning(f"Registration failed: domain not allowed - {normalized_email}")
                    st.error("Email domain not allowed.")
                else:
                    try:
                        result = register_user(name.strip(), surname.strip(), normalized_email)
                    except Exception as e:
                        logger.error(f"Internal error during registration for {normalized_email}: {e}")
                        st.error(f"Internal error during registration: {e}")
                    else:
                        if isinstance(result, tuple):
                            ok, msg = result
                        else:
                            ok, msg = (bool(result), "")
                        if ok:
                            logger.info(f"User registered successfully: {normalized_email}")
                            st.success(f"✅ Code sent to **{normalized_email}**.")
                            st.session_state["_last_registered_email"] = normalized_email
                        else:
                            logger.error(f"Registration failed for {normalized_email}: {msg}")
                            st.error(f"❌ {msg or 'Registration failed.'}")

    with tab2:
        pre_email = st.session_state.get("_last_registered_email", "")
        with st.form(key="verify_form"):
            v_email = st.text_input("Email", value=pre_email, key="verify_email")
            v_code = st.text_input("Activation code", key="verify_code")
            verify_submit = st.form_submit_button("🔓 Verify and activate account")

        if verify_submit:
            logger.debug(f"Account activation attempt for email: {v_email}")
            
            if not v_email.strip() or not v_code.strip():
                logger.warning(f"Activation failed: missing credentials for {v_email}")
                st.warning("Enter both email and activation code.")
            else:
                try:
                    act_result = activate_user(v_email.strip(), v_code.strip())
                except Exception as e:
                    logger.error(f"Internal error during verification for {v_email}: {e}")
                    st.error(f"Internal error during verification: {e}")
                else:
                    if isinstance(act_result, tuple):
                        ok, msg = act_result
                    else:
                        ok, msg = (bool(act_result), "")
                    if ok:
                        logger.info(f"Account activated successfully: {v_email}")
                        st.success("✅ Account activated! You can now login.")
                        if "_last_registered_email" in st.session_state:
                            del st.session_state["_last_registered_email"]
                    else:
                        logger.warning(f"Activation failed for {v_email}: {msg}")
                        st.error(f"❌ {msg or 'Verification failed.'}")
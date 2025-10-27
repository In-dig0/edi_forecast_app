import streamlit as st
from src.utils.sidebar_style import apply_sidebar_style
from src.utils.logger import setup_logger

# Inizializza il logger per questa pagina
logger = setup_logger("logout_page")

def page():
    apply_sidebar_style()
    st.title(f"🚪 :orange[Logout]")
    st.divider()
    
    #logger.info("Logout page accessed")
    
    st.markdown(":yellow[Execute logout from your account.]")
    st.markdown("")
    st.markdown("")

    if "user_email" not in st.session_state:
        logger.debug("Logout page accessed by non-authenticated user")
        st.info("You are not logged in.")
        if st.button("🔐 Go to Login"):
            st.rerun()
        return
    
    email = st.session_state.get("user_email")
    #logger.debug(f"Logout page accessed by user: {email}")
    
    st.markdown(f"**Current user:** `{email}`")
    st.markdown("")
    st.divider()

    # Bottone Logout con conferma
    if st.button("🚪 LOGOUT", type="primary", use_container_width=True):
        logger.debug(f"Logout button clicked by user: {email}")
        st.session_state["confirm_logout"] = True
        st.rerun()
    
    # Dialog di conferma
    if st.session_state.get("confirm_logout", False):
        st.warning("⚠️ Are you sure you want to logout?")
        st.markdown("")
        st.markdown("")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Yes, Logout", use_container_width=True):
                logger.info(f"User logged out successfully: {email}")
                st.session_state.clear()
                st.rerun()
        
        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                logger.debug(f"Logout cancelled by user: {email}")
                st.session_state["confirm_logout"] = False
                st.rerun()

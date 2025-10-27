import streamlit as st
from src.utils.sidebar_style import apply_sidebar_style
from src.utils.auth import get_user_data, update_user_data
from src.utils.logger import setup_logger

# Inizializza il logger per questa pagina
logger = setup_logger("profile_page")

def page():
    apply_sidebar_style()
    
    if "user_email" not in st.session_state:
        logger.warning("Profile page accessed without authentication")
        st.warning("⚠️ You must be logged in to access this page.")
        return
      
    # Determina quale utente stiamo editando
    logged_user_email = st.session_state["user_email"]
    logged_user = get_user_data(logged_user_email) or {}
    logged_user_role = logged_user.get("role", "sales_role")
    
    logger.info(f"Profile page accessed by user: {logged_user_email} (role: {logged_user_role})")
    
    # Se admin sta editando un altro utente
    editing_other_user = False
    target_email = logged_user_email
    
    if logged_user_role == "admin_role" and st.session_state.get("admin_editing_user"):
        editing_other_user = True
        target_email = st.session_state["admin_editing_user"]
        logger.info(f"Admin {logged_user_email} editing user profile: {target_email}")
    
    # Recupera i dati dell'utente target
    user = get_user_data(target_email) or {}
    
    # Titolo
    if editing_other_user:
        st.title(f"👤 :orange[Edit User Profile: {target_email}]")
        
        if st.button("⬅️ Back to User List"):
            logger.debug(f"Admin {logged_user_email} returned to user list from editing {target_email}")
            st.session_state["admin_editing_user"] = None
            st.rerun()
            
    else:
        st.title(f"👤 :orange[Profile]")

    st.divider()    
    st.markdown(":yellow[Manage your profile information below.]")
    st.markdown("")
    st.markdown("")

    # Email (sempre non modificabile)
    user_email = user.get("email", "")
    st.markdown(f"**📧 Email:** `{user_email}` _(non-editable)_")
    
    # Recupera i valori iniziali per Role e Active Status
    user_role = user.get("role", "sales_role")
    user_is_active = user.get("is_active", False)
    
    selected_role = user_role
    selected_active = user_is_active
    
    if editing_other_user:
        # 💡 AGGIUNTA E MODIFICA: Admin può modificare Ruolo e Stato Attivo
        col_role, col_active = st.columns(2)
        
        with col_role:
            role_options = ["sales_role", "admin_role"]
            selected_role = st.selectbox(
                "🔑 Role",
                options=role_options,
                index=role_options.index(user_role) if user_role in role_options else 0
            )

        with col_active:
             # Checkbox per lo stato attivo
            selected_active = st.checkbox(
                "✅ Is Active",
                value=user_is_active
            )
        
    else:
        # Utente normale vede solo il proprio ruolo e stato attivo (non modificabili)
        st.markdown(f"**🔑 Role:** `{user_role}` _(non-editable)_")
        st.markdown(f"**✅ Active:** `{'Yes' if user_is_active else 'No'}` _(non-editable)_")

    
    st.markdown("")
    
    # 🟡 BOX CON BORDO PER DATI MODIFICABILI
    with st.container(border=True):
        # Campi modificabili
        nome = st.text_input("Name", value=user.get("name", ""))
        surname = st.text_input("Surname", value=user.get("surname", ""))
        company = st.text_input("Company (optional)", value=user.get("company", ""))
        
        if st.button("💾 Save changes"):
            logger.debug(f"Profile update initiated for user: {target_email}")
            
            updates = {
                "name": nome,
                "surname": surname,
                "company": company
            }
            
            # Se admin sta editando, aggiorna anche il ruolo E lo stato attivo
            if editing_other_user:
                updates["role"] = selected_role
                updates["is_active"] = selected_active
                logger.debug(f"Admin {logged_user_email} updating {target_email} - Role: {selected_role}, Active: {selected_active}")
            
            try:
                # Se admin sta editando, permetti la modifica del ruolo
                result = update_user_data(target_email, updates, allow_role_change=editing_other_user)
                
                if isinstance(result, tuple):
                    ok, msg = result
                    
                    if ok:
                        logger.info(f"Profile updated successfully for user: {target_email}")
                        st.success("✅ Profile updated successfully!")
                    else:
                        logger.error(f"Profile update failed for {target_email}: {msg}")
                        st.error(f"❌ {msg}")
                else:
                    logger.info(f"Profile updated successfully for user: {target_email}")
                    st.success("✅ Profile updated successfully!")
                    
                # Forza l'aggiornamento della pagina per riflettere le modifiche
                st.rerun() 
                
            except Exception as e:
                logger.error(f"Exception during profile update for {target_email}: {e}")
                st.error(f"❌ Exception occurred: {e}")
                import traceback
                st.code(traceback.format_exc())
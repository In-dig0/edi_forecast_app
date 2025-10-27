import streamlit as st
import time 
from src.utils.sidebar_style import apply_sidebar_style
from src.utils.auth import get_all_users, get_user_data, update_user_data 
from src.utils.logger import setup_logger


# Inizializza il logger per questa pagina
logger = setup_logger("user_list_page")


def page():
    apply_sidebar_style()

    # Verifica che l'utente sia loggato e sia admin
    if "user_email" not in st.session_state:
        logger.warning("User list page accessed without authentication")
        st.warning("⚠️ You must be logged in to access this page.")
        return
       
    # Verifica ruolo admin
    user_email = st.session_state["user_email"]
    user = get_user_data(user_email) or {}
    user_role = user.get("role", "sales_role")
    
    if user_role != "admin_role":
        logger.warning(f"Non-admin user {user_email} (role: {user_role}) attempted to access user list page")
        st.error("🚫 Access denied. Admin role required.")
        return
    
    #logger.info(f"User list page accessed by admin: {user_email}")
    
    st.title("👥 User List")
    st.divider()
    st.markdown(f":yellow[Manage registered users.]")
    
    # Recupera tutti gli utenti
    users = get_all_users()
    
    if not users:
        logger.debug(f"No users found in system for admin {user_email}")
        st.info("No users registered yet.")
        return
    
    logger.debug(f"Admin {user_email} viewing {len(users)} users")
    
    st.markdown("### Registered Users")
    
    for user_data in users:
        email = user_data.get("email", "N/A")
        name = user_data.get("name", "")
        surname = user_data.get("surname", "")
        company = user_data.get("company", "")
        role = user_data.get("role", "sales_role")
        
        # Normalizzazione (Lettura e pulizia del tipo di dato)
        raw_is_active = user_data.get("is_active") 
        
        # 1. Normalizza il valore letto in un booleano Python standard (True/False)
        if isinstance(raw_is_active, str):
            initial_is_active = raw_is_active.lower() == 'true'
        else:
            initial_is_active = bool(raw_is_active)
        
        # 💡 AGGIUNTA: Visualizzazione dello stato (attivo/inattivo) nell'intestazione
        status_label = "🟢 Active" if initial_is_active else "🔴 Inactive"
        
        
        # Crea un expander per ogni utente con il nuovo stato
        with st.expander(f"📧 {email} - {name} {surname} ({status_label})"):
            with st.form(key=f"user_edit_form_{email}"):
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Name:** {name or 'Not set'}")
                    st.markdown(f"**Surname:** {surname or 'Not set'}")
                    st.markdown(f"**Company:** {company or 'Not set'}")
                
                # Campi modificabili
                role_options = ["admin_role", "sales_role"]
                
                # Selectbox per il ruolo
                new_role = st.selectbox(
                    "🔑 Role:",
                    options=role_options,
                    index=role_options.index(role) if role in role_options else 1,
                    key=f"role_select_{email}"
                )

                # Checkbox per lo stato attivo
                new_active = st.checkbox(
                    "Is Active", 
                    value=initial_is_active, 
                    key=f"active_check_{email}"
                )

                st.markdown("---")
                
                save_changes = st.form_submit_button("💾 Save Changes", type="primary")


            if save_changes:
                logger.debug(f"Admin {user_email} attempting to update user {email}")
                
                changes = {}
                
                # 1. Verifica il cambiamento di RUOLO
                if new_role != role:
                    changes["role"] = new_role
                    logger.debug(f"Role change detected for {email}: {role} -> {new_role}")
                
                # 2. Verifica il cambiamento di ACTIVE
                if new_active != initial_is_active: 
                    # Riconverte il booleano in stringa ("True" o "False") per users.json
                    changes["is_active"] = str(new_active)
                    logger.debug(f"Active status change detected for {email}: {initial_is_active} -> {new_active}")

                if changes:
                    try:
                        ok, msg = update_user_data(email, changes, allow_role_change=True)
                        if ok:
                            logger.info(f"Admin {user_email} successfully updated user {email}: {changes}")
                            
                            # Messaggio di successo temporaneo (5 secondi)
                            success_msg = f"✅ User **{email}** updated: {', '.join(changes.keys())}."
                            
                            placeholder = st.empty()
                            placeholder.success(success_msg)
                            time.sleep(5)
                            placeholder.empty()
                            
                            # Ricarica la pagina per aggiornare l'elenco e lo stato
                            st.rerun() 
                        else:
                            logger.error(f"Admin {user_email} failed to update user {email}: {msg}")
                            st.error(f"❌ Error updating user: {msg}")
                    except Exception as e:
                        logger.error(f"Exception during user update by admin {user_email} for user {email}: {e}")
                        st.error(f"❌ Error updating user: {e}")
                else:
                    logger.debug(f"Admin {user_email} submitted form for {email} but no changes detected")
                    st.info("No changes detected.")
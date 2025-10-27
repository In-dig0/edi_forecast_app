import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io
import json

from src.utils.sidebar_style import apply_sidebar_style
from src.utils.config import OUTPUT_DIR, BACKUP_DIR
from src.utils.logger import setup_logger

# Inizializza il logger per questa pagina
logger = setup_logger("upload_forecast_page")


def find_existing_json(uploaded_filename):
    """
    Cerca un file JSON esistente in OUTPUT_DIR che corrisponde al filename caricato.
    Ritorna il path completo del JSON se trovato, altrimenti None.
    """
    if not uploaded_filename:
        return None
    
    base_name = os.path.splitext(uploaded_filename)[0].lower()
    
    try:
        if not os.path.exists(OUTPUT_DIR):
            return None
            
        for f in os.listdir(OUTPUT_DIR):
            if f.endswith(".json"):
                json_path = os.path.join(OUTPUT_DIR, f)
                try:
                    with open(json_path, "r", encoding="utf-8") as jf:
                        data = json.load(jf)
                    if isinstance(data, dict):
                        original = os.path.splitext(data.get("original_filename", ""))[0].lower()
                        if original == base_name:
                            logger.debug(f"Found existing JSON for {uploaded_filename}: {json_path}")
                            return json_path
                except Exception as e:
                    logger.warning(f"Error reading JSON file {f}: {e}")
                    continue
    except Exception as e:
        logger.error(f"Error searching for existing JSON: {e}")
    
    return None


def page():
    apply_sidebar_style()    
    
    # -------------------------------
    # 🔒 Access control
    # -------------------------------
    if "user_email" not in st.session_state:
        logger.warning("Upload forecast page accessed without authentication")
        st.warning("🔒 You must be logged in to access this page.")
        return

    user_email = st.session_state.get("user_email")

    st.title(f"🎯 :orange[Upload EDI Forecast Requirements]")
    st.divider()
    st.markdown(":yellow[Use this page to upload EDI forecast files, review the data, and save backups along with a JSON forecast file.]")
    st.markdown("")
    st.markdown("")
    
    # -------------------------------
    # 🧹 Auto-reset quando cambi pagina
    # -------------------------------
    if "on_upload_page" not in st.session_state:
        st.session_state.on_upload_page = True
    
    if not st.session_state.on_upload_page and st.session_state.get("df_forecast") is not None:
        logger.debug(f"Auto-reset triggered for user {user_email}")
        st.session_state.df_forecast = None
        st.session_state.cliente_selezionato = None
        st.session_state.uploaded_file_name = None
        st.session_state.uploaded_file_content = None
        st.session_state.show_save_summary = False
        st.session_state.save_summary_data = None
        st.session_state["widget_version"] = st.session_state.get("widget_version", 0) + 1
        st.session_state.on_upload_page = True
        st.rerun()
    
    st.session_state.on_upload_page = True
    
    # Se abbiamo già salvato, mostra solo il summary
    if st.session_state.get("show_save_summary", False):
        st.divider()
        st.success("### ✅ All operations completed successfully!")
        
        summary = st.session_state.get("save_summary_data", {})
        if summary:
            with st.expander("📋 Summary of saved files", expanded=True):
                st.markdown(f"""
                **Customer:** {summary.get('customer', 'N/A')}  
                **Original file:** {summary.get('original_filename', 'N/A')}  
                **Records saved:** {summary.get('records_count', 0)} rows
                
                **Files created:**
                - 📄 TXT: `{summary.get('backup_txt_filename', 'N/A')}`
                - 📊 Excel: `{summary.get('backup_excel_filename', 'N/A')}`
                - 🗃️ JSON: `{summary.get('json_filename', 'N/A')}` ({summary.get('action_msg', 'saved')})
                """)
        
        st.divider()
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 Reset interface and start new upload", type="primary", use_container_width=True, key="reset_after_save"):
                logger.info(f"User {user_email} reset interface after save")
                st.session_state.df_forecast = None
                st.session_state.cliente_selezionato = None
                st.session_state.uploaded_file_name = None
                st.session_state.uploaded_file_content = None
                st.session_state.show_save_summary = False
                st.session_state.save_summary_data = None
                st.session_state["widget_version"] += 1
                st.rerun()
        
        st.stop()

    # -------------------------------
    # 📦 Initialize session state
    # -------------------------------
    st.session_state.setdefault("df_forecast", None)
    st.session_state.setdefault("cliente_selezionato", None)
    st.session_state.setdefault("uploaded_file_name", None)
    st.session_state.setdefault("uploaded_file_content", None)
    st.session_state.setdefault("widget_version", 0)
    st.session_state.setdefault("show_save_summary", False)
    st.session_state.setdefault("save_summary_data", None)

    widget_version = st.session_state["widget_version"]

    st.markdown("### ⚙️ Upload parameters")

    # -------------------------------
    # 🔹 Select customer
    # -------------------------------
    cliente = st.selectbox(
        "Customer",
        options=["", "Navistar", "Volvo", "Man"],
        index=0,
        key=f"cliente_input_{widget_version}",
        placeholder="Select a customer..."
    )

    # -------------------------------
    # 🔹 File uploader
    # -------------------------------
    uploaded_file = st.file_uploader(
        label="📄 Upload EDI file (.txt or .csv)",
        type=["txt", "csv"],
        key=f"file_uploader_{widget_version}",
        help="The file must use '!' as the delimiter.",
        accept_multiple_files=False
    )

    # -------------------------------
    # 🔹 Detect existing forecast file
    # -------------------------------
    existing_json_path = None
    if uploaded_file is not None and st.session_state.get("df_forecast") is None:
        existing_json_path = find_existing_json(uploaded_file.name)
        
        if existing_json_path:
            logger.warning(f"User {user_email} uploading file that already exists: {uploaded_file.name}")
            st.warning(
                f"⚠️ A forecast for the file **{uploaded_file.name}** already exists.\n\n"
                f"**Existing file:** `{os.path.basename(existing_json_path)}`\n\n"
                f"If you proceed with the upload and backup, the existing forecast will be **overwritten**."
            )

    # -------------------------------
    # ⬆️ Upload button
    # -------------------------------
    data_already_loaded = st.session_state.get("df_forecast") is not None
    
    upload_button = st.button(
        "⬆️ Upload file", 
        use_container_width=True, 
        disabled=data_already_loaded,
        help="Upload is disabled because data is already loaded. Click 'Clear all' to upload a new file." if data_already_loaded else "Click to upload and process the file"
    )
    
    if upload_button:
        logger.debug(f"User {user_email} clicked upload button - Customer: {cliente}, File: {uploaded_file.name if uploaded_file else 'None'}")
        
        if not cliente:
            logger.warning(f"Upload failed for {user_email}: no customer selected")
            st.error("❌ Select a customer first.")
            st.stop()

        if not uploaded_file:
            logger.warning(f"Upload failed for {user_email}: no file selected")
            st.error("❌ Select a file to upload.")
            st.stop()

        try:
            # -------------------------------
            # 📄 Read and parse file
            # -------------------------------
            content = uploaded_file.getvalue().decode("utf-8")
            lines = content.split("\n")
            st.session_state.uploaded_file_name = uploaded_file.name
            st.session_state.uploaded_file_content = content

            logger.debug(f"File {uploaded_file.name} read successfully - {len(lines)} lines")

            if len(lines) < 7:
                logger.warning(f"Upload failed for {user_email}: file too short ({len(lines)} lines)")
                st.error("❌ The file does not contain enough data.")
                st.stop()

            headers = ["ORD.HYD", "COD.CLIENTE", "COD. ART", "DESCRIZIONE",
                       "OCLI GARE", "QUANTITA", "CONSEGNA", "ORD.VEN"]

            data_rows = []
            for line in lines[6:]:
                if not line.strip() or line.strip().startswith(("-", "+")):
                    continue
                cols = line.split("!")
                if cols and cols[0].strip() == "":
                    cols.pop(0)
                if cols and cols[-1].strip() == "":
                    cols.pop()
                if len(cols) >= 8:
                    data_rows.append([col.strip() for col in cols[:8]])

            if not data_rows:
                logger.warning(f"Upload failed for {user_email}: no data rows found in {uploaded_file.name}")
                st.error("❌ No data rows found in the file.")
                st.stop()

            # -------------------------------
            # 🧾 Create DataFrame
            # -------------------------------
            df = pd.DataFrame(data_rows, columns=headers).dropna(how="all")

            if "CONSEGNA" in df.columns:
                def format_date(date_str):
                    try:
                        date_str = str(date_str).strip()
                        date_str = ''.join(c for c in date_str if c.isdigit())
                        
                        if len(date_str) == 8:
                            return f"{date_str[:2]}.{date_str[2:4]}.{date_str[4:]}"
                        elif len(date_str) == 7:
                            return f"0{date_str[0]}.{date_str[1:3]}.{date_str[3:]}"
                        elif len(date_str) == 6:
                            return f"{date_str[:2]}.{date_str[2:4]}.20{date_str[4:]}"
                        elif len(date_str) == 5:
                            return f"0{date_str[0]}.{date_str[1:3]}.20{date_str[3:]}"
                        return date_str
                    except Exception:
                        return date_str
                df["CONSEGNA"] = df["CONSEGNA"].apply(format_date)

            df.insert(0, "Index", range(1, len(df) + 1))
            st.session_state.df_forecast = df
            st.session_state.cliente_selezionato = cliente

            logger.info(f"File uploaded successfully by {user_email}: {uploaded_file.name} - Customer: {cliente} - {len(df)} rows")
            st.success(f"✅ File uploaded successfully: {len(df)} rows imported for customer **{cliente}**")
            
            st.rerun()

        except Exception as e:
            logger.error(f"Error uploading file for {user_email}: {e}")
            st.error(f"❌ Error reading file: {e}")

    # -------------------------------
    # 📋 Display loaded data
    # -------------------------------
    if st.session_state.df_forecast is not None and not st.session_state.get("show_save_summary", False):
        st.divider()
        st.markdown(f"### 📋 Loaded data - Customer: **{st.session_state.cliente_selezionato}**")

        # 🔹 Clear all
        if st.button("🗑️ Clear all", use_container_width=True):
            logger.info(f"User {user_email} cleared loaded data")
            st.session_state.df_forecast = None
            st.session_state.cliente_selezionato = None
            st.session_state.uploaded_file_name = None
            st.session_state.uploaded_file_content = None
            st.session_state.show_save_summary = False
            st.session_state.save_summary_data = None
            st.session_state["widget_version"] += 1
            st.rerun()

        # 🔹 Data editor
        edited_df = st.data_editor(
            st.session_state.df_forecast,
            use_container_width=True,
            num_rows="dynamic",
            disabled=["Index"],
            height=400,
            key=f"data_editor_{widget_version}"
        )
        st.session_state.df_forecast = edited_df

        st.divider()

        # -------------------------------
        # 💾 Save section
        # -------------------------------
        col_spacer1, col_backup, col_spacer2 = st.columns([1, 2, 1])
        with col_backup:
            save_already_done = st.session_state.get("show_save_summary", False)
            
            save_button = st.button(
                "💾 SAVE", 
                type="primary", 
                use_container_width=True,
                disabled=save_already_done,
                help="Save is disabled because data has already been saved. Click 'Reset interface' to start a new upload." if save_already_done else "Save all data and create backup files"
            )
            
            if save_button:
                logger.info(f"User {user_email} initiated save operation - Customer: {st.session_state.cliente_selezionato}")
                
                try:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    os.makedirs(BACKUP_DIR, exist_ok=True)
                    os.makedirs(OUTPUT_DIR, exist_ok=True)

                    progress_container = st.container()
                    
                    with progress_container:
                        st.markdown("### 💾 Saving data...")
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # Step 1: TXT backup
                        status_text.info("📄 Saving TXT backup...")
                        progress_bar.progress(25)
                        original_name = os.path.splitext(st.session_state.uploaded_file_name or 'uploaded')[0]
                        backup_txt_filename = f"BACKUP_{st.session_state.cliente_selezionato}_{original_name}_{timestamp}.txt"
                        with open(os.path.join(BACKUP_DIR, backup_txt_filename), 'w', encoding='utf-8') as f:
                            f.write(st.session_state.uploaded_file_content or "")
                        logger.info(f"TXT backup saved: {backup_txt_filename}")
                        status_text.success(f"✅ TXT backup saved: `{backup_txt_filename}`")
                        
                        # Step 2: Excel backup
                        status_text.info("📊 Saving Excel backup...")
                        progress_bar.progress(50)
                        df_export = st.session_state.df_forecast.drop(columns=['Index'])
                        backup_excel_filename = f"BACKUP_forecast_{st.session_state.cliente_selezionato}_{timestamp}.xlsx"
                        df_export.to_excel(os.path.join(BACKUP_DIR, backup_excel_filename),
                                           index=False, sheet_name='Forecast', engine='openpyxl')
                        logger.info(f"Excel backup saved: {backup_excel_filename}")
                        status_text.success(f"✅ Excel backup saved: `{backup_excel_filename}`")
                        
                        # Step 3: JSON
                        status_text.info("🗃️ Saving JSON forecast...")
                        progress_bar.progress(75)
                        existing_json = find_existing_json(st.session_state.uploaded_file_name)
                        
                        if existing_json:
                            json_path = existing_json
                            action_msg = "overwritten"
                            action_icon = "🔄"
                            logger.info(f"Overwriting existing JSON: {os.path.basename(json_path)}")
                        else:
                            json_filename = f"forecast_{st.session_state.cliente_selezionato}_{timestamp}.json"
                            json_path = os.path.join(OUTPUT_DIR, json_filename)
                            action_msg = "created"
                            action_icon = "✨"
                            logger.info(f"Creating new JSON: {json_filename}")

                        json_data = {
                            "customer": st.session_state.cliente_selezionato,
                            "timestamp": timestamp,
                            "original_filename": st.session_state.uploaded_file_name,
                            "records": df_export.to_dict(orient="records")
                        }
                        with open(json_path, "w", encoding="utf-8") as f:
                            json.dump(json_data, f, ensure_ascii=False, indent=4)
                        
                        logger.info(f"Save operation completed successfully by {user_email} - {len(df_export)} records")
                        status_text.success(f"{action_icon} JSON forecast {action_msg}: `{os.path.basename(json_path)}`")
                        progress_bar.progress(100)
                    
                    st.session_state.show_save_summary = True
                    st.session_state.save_summary_data = {
                        "customer": st.session_state.cliente_selezionato,
                        "original_filename": st.session_state.uploaded_file_name,
                        "records_count": len(df_export),
                        "backup_txt_filename": backup_txt_filename,
                        "backup_excel_filename": backup_excel_filename,
                        "json_filename": os.path.basename(json_path),
                        "action_msg": action_msg
                    }
                    st.rerun()

                except Exception as e:
                    logger.error(f"Error during save operation for {user_email}: {e}")
                    st.error(f"❌ Error during save: {e}")
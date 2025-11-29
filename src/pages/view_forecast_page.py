import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

from src.utils.sidebar_style import apply_sidebar_style
from src.utils.logger import setup_logger
from src.utils.config import OUTPUT_DIR

# Inizializza il logger per questa pagina
logger = setup_logger("view_forecast_page")

def page():
    apply_sidebar_style()

    st.session_state.on_upload_page = False
    
    if "user_email" not in st.session_state:
        logger.warning("View forecast page accessed without authentication")
        st.warning("🔒 You must be logged in to access this page.")
        return

    user_email = st.session_state.get("user_email")
    #logger.info(f"View forecast page accessed by user: {user_email}")

    st.title(f"📊 :orange[View EDI Forecast Records]")
    st.divider()
    st.markdown(":yellow[Browse, filter, download, and manage previously saved EDI forecast records.]")
    st.markdown("")
    st.markdown("")

    if not os.path.exists(OUTPUT_DIR):
        logger.debug(f"No output directory found for user {user_email}")
        st.info("🔭 No forecast records found. Upload and save forecasts first.")
        return

    json_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.json')]
    
    if not json_files:
        logger.debug(f"No JSON files found in output directory for user {user_email}")
        st.info("🔭 No forecast records found. Upload and save forecasts first.")
        return
    
    json_files.sort(reverse=True)
    logger.debug(f"Found {len(json_files)} forecast records for user {user_email}")
    
    st.markdown(f"### 📊 Found **{len(json_files)}** forecast records")
    
    # Filtri
    col1, col2, col3 = st.columns(3)
    
    with col1:
        customers = set()
        for filename in json_files:
            parts = filename.replace('forecast_', '').replace('.json', '').split('_')
            if len(parts) >= 1:
                customers.add(parts[0])
        
        customer_filter = st.selectbox(
            "Filter by customer",
            options=["All"] + sorted(list(customers)),
            index=0
        )
    
    with col2:
        date_filter = st.selectbox(
            "Sort by",
            options=["Newest first", "Oldest first"],
            index=0
        )
    
    with col3:
        items_per_page = st.selectbox(
            "Records per page",
            options=[5, 10, 20, 50],
            index=1,
            key="items_per_page"
        )
    
    # Applica filtri
    filtered_files = json_files
    if customer_filter != "All":
        filtered_files = [f for f in json_files if f.startswith(f"forecast_{customer_filter}_")]
        logger.debug(f"User {user_email} filtered by customer: {customer_filter} - {len(filtered_files)} results")
    
    if date_filter == "Oldest first":
        filtered_files = sorted(filtered_files)
    
    if not filtered_files:
        logger.debug(f"No records match filters for user {user_email}")
        st.warning("⚠️ No records match the selected filters.")
        return
    
    # -------------------------------
    # 📄 Paginazione
    # -------------------------------
    total_records = len(filtered_files)
    total_pages = (total_records + items_per_page - 1) // items_per_page
    
    if "current_page" not in st.session_state:
        st.session_state.current_page = 1
    
    if "last_filter" not in st.session_state:
        st.session_state.last_filter = (customer_filter, date_filter, items_per_page)
    
    current_filter = (customer_filter, date_filter, items_per_page)
    if current_filter != st.session_state.last_filter:
        st.session_state.current_page = 1
        st.session_state.last_filter = current_filter
    
    if st.session_state.current_page > total_pages:
        st.session_state.current_page = total_pages
    if st.session_state.current_page < 1:
        st.session_state.current_page = 1
    
    start_idx = (st.session_state.current_page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_records)
    
    col_info, col_nav = st.columns([2, 1])
    
    with col_info:
        st.markdown("")
        st.markdown(f"**Showing records {start_idx + 1}-{end_idx} of {total_records}** (Page {st.session_state.current_page}/{total_pages})")
    
    page_files = filtered_files[start_idx:end_idx]
    
    # Visualizza i forecast
    for json_file in page_files:
        json_path = os.path.join(OUTPUT_DIR, json_file)
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            customer = data.get('customer', 'Unknown')
            timestamp = data.get('timestamp', '')
            original_filename = data.get('original_filename', 'N/A')
            records = data.get('records', [])
            
            try:
                dt = datetime.strptime(timestamp, '%Y%m%d_%H%M%S')
                display_date = dt.strftime('%d/%m/%Y %H:%M:%S')
            except:
                display_date = timestamp
            
            with st.expander(f"🔹 **{customer}** - {display_date} ({len(records)} rows)", expanded=False):
                st.markdown(f"**Original file:** `{original_filename}`")
                st.markdown(f"**Timestamp:** {display_date}")
                st.markdown(f"**Records:** {len(records)}")
                
                if records:
                    df = pd.DataFrame(records)
                    st.dataframe(df, width='stretch', height=300)
                    
                    col_download, col_delete = st.columns(2)
                    
                    with col_download:
                        import io
                        buffer = io.BytesIO()
                        df.to_excel(buffer, index=False, sheet_name='Forecast', engine='openpyxl')
                        excel_bytes = buffer.getvalue()
                        
                        if st.download_button(
                            label="📥 Download Excel",
                            data=excel_bytes,
                            file_name=f"forecast_{customer}_{timestamp}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            width='stretch',
                            key=f"download_{json_file}"
                        ):
                            logger.info(f"User {user_email} downloaded forecast: {json_file}")
                    
                    with col_delete:
                        if st.button("🗑️ Delete record", width='stretch', key=f"delete_{json_file}"):
                            try:
                                os.remove(json_path)
                                logger.info(f"User {user_email} deleted forecast record: {json_file}")
                                st.success(f"✅ Record deleted: {json_file}")
                                st.session_state.current_page = 1
                                st.rerun()
                            except Exception as e:
                                logger.error(f"Error deleting file {json_file} by user {user_email}: {e}")
                                st.error(f"❌ Error deleting file: {e}")
                else:
                    st.warning("⚠️ No data records found in this file.")
        
        except Exception as e:
            logger.error(f"Error reading forecast file {json_file} for user {user_email}: {e}")
            st.error(f"❌ Error reading file `{json_file}`: {e}")
    
    # Controlli di navigazione in basso
    col_nav_bottom = st.columns([1, 2, 1])
    
    with col_nav_bottom[1]:
        nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
        
        with nav_col1:
            if st.button("⏮️", disabled=st.session_state.current_page == 1, width='stretch', key="first_bottom"):
                st.session_state.current_page = 1
                st.rerun()
        
        with nav_col2:
            if st.button("◀️", disabled=st.session_state.current_page == 1, width='stretch', key="prev_bottom"):
                st.session_state.current_page -= 1
                st.rerun()
        
        with nav_col3:
            if st.button("▶️", disabled=st.session_state.current_page == total_pages, width='stretch', key="next_bottom"):
                st.session_state.current_page += 1
                st.rerun()
        
        with nav_col4:
            if st.button("⏭️", disabled=st.session_state.current_page == total_pages, width='stretch', key="last_bottom"):
                st.session_state.current_page = total_pages
                st.rerun()
    
    st.divider()
    
    # Statistiche
    st.markdown("### 📈 Statistics")
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
    with col_stat1:
        st.metric("Total records", len(filtered_files))
    
    with col_stat2:
        total_rows = 0
        for json_file in filtered_files:
            try:
                with open(os.path.join(OUTPUT_DIR, json_file), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    total_rows += len(data.get('records', []))
            except:
                pass
        st.metric("Total rows", total_rows)
    
    with col_stat3:
        if filtered_files:
            customers_count = len(set([f.split('_')[1] for f in filtered_files if len(f.split('_')) > 1]))
            st.metric("Customers", customers_count)
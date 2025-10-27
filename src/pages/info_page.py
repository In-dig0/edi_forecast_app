import streamlit as st
from utils.sidebar_style import apply_sidebar_style
import sys
from src.utils.config import APP_NAME, APP_VERSION

def page():
    apply_sidebar_style()    
    # Marca che NON siamo sulla pagina upload
    st.session_state.on_upload_page = False
    st.title(f"ℹ️ :orange[Informations]")
    st.divider()
    st.subheader(f"Welcome to the :yellow[{APP_NAME}]")

    st.markdown(f"""
    This web application is designed to help users manage and forecast EDI requirements efficiently.
    """)
    
    st.markdown("")
    st.markdown("")    
    
    st.markdown("### Application Details")
    st.markdown(f"""
    **Version:** {APP_VERSION}
    """)
    st.markdown("Powered with Streamlit :streamlit:")
    st.divider()
    
    # Sezione tecnologie utilizzate
    col1, col2, col3 = st.columns([1, 2, 1])
    
    # Expander con versioni
    with st.expander("📦 Framework versions", expanded=False):
        st.markdown("**Runtime Information:**")
        
        col_v1, col_v2 = st.columns(2)
        
        with col_v1:
            st.metric(label="🎈 Streamlit", value=st.__version__)
            st.metric(label="🐍 Python", value=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        
        with col_v2:
            try:
                import pandas as pd
                pandas_version = pd.__version__
            except:
                pandas_version = "N/A"
            
            try:
                import openpyxl
                openpyxl_version = openpyxl.__version__
            except:
                openpyxl_version = "N/A"
            
            st.metric(label="🐼 Pandas", value=pandas_version)
            st.metric(label="📊 OpenPyXL", value=openpyxl_version)
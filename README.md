# EDI_forecast

Streamlit application migrated to use `st.Page` and `st.navigation()` for dynamic navigation.

## Run

1. Install dependencies:
```bash
pip install streamlit pandas openpyxl python-dotenv requests
```

2. Start the app:
```bash
python EDI_forecast/run.py
```

## Structure

```
EDI_forecast/
  run.py
  src/app.py
  src/data/
  src/pages/
    info_page.py
    registration_page.py
    login_page.py
    profile_page.py
    upload_forecast_page.py
    logout_page.py
    view_forecast_page.py
    user_list.py
  src/utils/
    auth.py
    config.py
    email_utils.py
    sidebar_style.py
```

## Notes

- Authentication uses OTP sent via email (Mailjet). Configure MAILJET_API_KEY and MAILJET_API_SECRET or run in DEBUG_MODE.
- Pages are modular: each page exposes a `page()` function and is wrapped by `st.Page` in `app.py`.
- Upload Forecast page retains the logic from your v5 implementation with separated download and backup actions.

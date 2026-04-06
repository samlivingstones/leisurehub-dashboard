import os
import streamlit as st

def get_db_config():
    # Try Streamlit secrets first (used in Streamlit Cloud)
    try:
        return {
            "server":   st.secrets["DB_SERVER"],
            "port":     int(st.secrets["DB_PORT"]),
            "database": st.secrets["DB_NAME"],
            "username": st.secrets["DB_USER"],
            "password": st.secrets["DB_PASSWORD"],
        }
    except Exception:
        pass

    # Fall back to environment variables (local dev)
    return {
        "server":   os.environ.get("DB_SERVER", "localhost"),
        "port":     int(os.environ.get("DB_PORT", 1433)),
        "database": os.environ.get("DB_NAME", "LeisureHub"),
        "username": os.environ.get("DB_USER", "sa"),
        "password": os.environ.get("DB_PASSWORD", "YourSTRONGPassword123"),
    }

def get_connection_string():
    c = get_db_config()
    return (
        f"mssql+pymssql://{c['username']}:{c['password']}"
        f"@{c['server']}:{c['port']}/{c['database']}"
    )
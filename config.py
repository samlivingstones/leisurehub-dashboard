# ============================================================
# LeisureHub — Database Connection Config
# Using pymssql — no ODBC driver needed, works on Apple Silicon
# ============================================================

DB_CONFIG = {
    "server":   "localhost",        # or "127.0.0.1"
    "port":     1433,               # default SQL Server port
    "database": "LeisureHub",
    "username": "sa",               # your SQL Server login
    "password": "YourSTRONGPassword123", # your SA password from Docker
}

def get_connection_string():
    c = DB_CONFIG
    return (
        f"mssql+pymssql://{c['username']}:{c['password']}"
        f"@{c['server']}:{c['port']}/{c['database']}"
    )
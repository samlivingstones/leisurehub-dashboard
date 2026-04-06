# LeisureHub Python Dashboard — Setup Instructions

## Folder structure
```
leisurehub_dashboard/
├── dashboard.py
└── config.py
```

---

## Step 1 — Install dependencies

Open your terminal and run:

```bash
pip install streamlit pandas plotly sqlalchemy pyodbc
```

Then install the **Microsoft ODBC Driver 18** for Mac:

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install the ODBC driver
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
HOMEBREW_ACCEPT_EULA=Y brew install msodbcsql18
```

Verify it installed:
```bash
odbcinst -q -d -n "ODBC Driver 18 for SQL Server"
```
You should see a path returned — if so, you're good.

---

## Step 2 — Edit config.py

Open `config.py` and fill in your Docker SQL Server details:

```python
DB_CONFIG = {
    "server":   "localhost,1433",    # Docker maps to this by default
    "database": "LeisureHub",
    "username": "sa",
    "password": "YourActualPassword!", # the -e MSSQL_SA_PASSWORD you set
    "driver":   "ODBC Driver 18 for SQL Server",
    "extra":    "TrustServerCertificate=yes;Encrypt=yes;",
}
```

**To find your Docker SQL Server password**, run:
```bash
docker inspect <container_name> | grep MSSQL_SA_PASSWORD
```

---

## Step 3 — Make sure Docker container is running

```bash
docker ps
```

You should see your SQL Server container listed. If not:

```bash
docker start <container_name>
```

---

## Step 4 — Run the dashboard

```bash
cd leisurehub_dashboard
streamlit run dashboard.py
```

Your browser will open automatically at **http://localhost:8501**

---

## Troubleshooting

| Error | Fix |
|---|---|
| `No module named pyodbc` | Run `pip install pyodbc` |
| `Data source name not found` | ODBC driver not installed — redo Step 1 |
| `Login failed for user 'sa'` | Wrong password in config.py |
| `Can't connect to server` | Docker container not running — `docker start <name>` |
| `Symmetric key not found` | The encryption script hasn't been run on the DB yet |
| Port 1433 connection refused | Check Docker port mapping: `docker ps` should show `0.0.0.0:1433->1433/tcp` |

---

## Export dashboard as PDF (for submission)

Once the dashboard is running:

1. Open **http://localhost:8501** in Chrome
2. Press **⌘ + P** → Print
3. Change destination to **"Save as PDF"**
4. Set layout to **Landscape**
5. Save as `visualization_report.pdf`

Repeat for each of the 4 pages.
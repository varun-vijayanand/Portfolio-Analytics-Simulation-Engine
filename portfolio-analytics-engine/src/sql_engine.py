import sqlite3
import os
from datetime import datetime

DB_PATH = "governance/metadata.db"
os.makedirs("governance", exist_ok=True)

class SQLMetadataLogger:
    """Logs report runs, KPIs and narrative sections into SQLite metadata DB."""

    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS report_runs (
            run_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            report_name TEXT,
            total_return REAL,
            annual_return REAL,
            volatility REAL
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS kpi_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER,
            kpi_name TEXT,
            kpi_value REAL,
            FOREIGN KEY(run_id) REFERENCES report_runs(run_id)
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS narratives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER,
            section TEXT,
            narrative TEXT,
            FOREIGN KEY(run_id) REFERENCES report_runs(run_id)
        )
        """)

        conn.commit()
        conn.close()

    def log_run(self, report_name, total_return, annual_return, volatility):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        ts = datetime.utcnow().isoformat()

        cur.execute("""
            INSERT INTO report_runs (timestamp, report_name, total_return, annual_return, volatility)
            VALUES (?, ?, ?, ?, ?)
        """, (ts, report_name, total_return, annual_return, volatility))

        run_id = cur.lastrowid
        conn.commit()
        conn.close()
        return run_id

    def log_kpi(self, run_id, kpi_name, kpi_value):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO kpi_results (run_id, kpi_name, kpi_value) VALUES (?, ?, ?)",
            (run_id, kpi_name, kpi_value)
        )
        conn.commit()
        conn.close()

    def log_narrative(self, run_id, section, narrative):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO narratives (run_id, section, narrative) VALUES (?, ?, ?)",
            (run_id, section, narrative)
        )
        conn.commit()
        conn.close()

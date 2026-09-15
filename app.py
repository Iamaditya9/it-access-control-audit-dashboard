from flask import Flask, jsonify, render_template, request
from pathlib import Path
import csv
import sqlite3

app = Flask(__name__)
DB = Path("data/audit.db")

def connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = connect()
    conn.execute("""CREATE TABLE IF NOT EXISTS access_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT NOT NULL,
        employee_name TEXT NOT NULL,
        department TEXT NOT NULL,
        role TEXT NOT NULL,
        system_name TEXT NOT NULL,
        privilege_level TEXT NOT NULL,
        mfa_enabled INTEGER NOT NULL,
        account_status TEXT NOT NULL,
        last_reviewed TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS findings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_id INTEGER NOT NULL,
        control_name TEXT NOT NULL,
        severity TEXT NOT NULL,
        finding TEXT NOT NULL,
        recommendation TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Open'
    )""")
    conn.commit()
    conn.close()

def evaluate(record):
    findings = []
    if record["account_status"].lower() == "inactive":
        findings.append(("User Access Review", "High", "Inactive account retains system access", "Disable the account and retain evidence of the access removal."))
    if record["privilege_level"].lower() in {"admin", "privileged"} and record["mfa_enabled"] == 0:
        findings.append(("Privileged Access", "High", "Privileged account does not have MFA enabled", "Require MFA before privileged access is permitted."))
    if record["role"].lower() in {"finance-admin", "approver-admin"}:
        findings.append(("Segregation of Duties", "Medium", "Administrative and approval responsibilities may conflict", "Review the role assignment for segregation-of-duties conflicts."))
    if not record["last_reviewed"]:
        findings.append(("Access Recertification", "Medium", "Access record has no review date", "Complete and document an access recertification review."))
    return findings

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/summary")
def summary():
    conn = connect()
    result = {
        "total_records": conn.execute("SELECT COUNT(*) FROM access_records").fetchone()[0],
        "open_findings": conn.execute("SELECT COUNT(*) FROM findings WHERE status='Open'").fetchone()[0],
        "high_risk": conn.execute("SELECT COUNT(*) FROM findings WHERE severity='High' AND status='Open'").fetchone()[0],
        "systems": conn.execute("SELECT COUNT(DISTINCT system_name) FROM access_records").fetchone()[0]
    }
    conn.close()
    return jsonify(result)

@app.route("/api/findings")
def findings():
    conn = connect()
    rows = conn.execute("""SELECT * FROM findings
        ORDER BY CASE severity WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END, id DESC""").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route("/api/import", methods=["POST"])
def import_csv():
    file = request.files.get("file")
    if not file or not file.filename.lower().endswith(".csv"):
        return jsonify(error="CSV file required"), 400
    conn = connect()
    inserted = 0
    generated = 0
    for row in csv.DictReader(file.stream):
        cur = conn.execute("""INSERT INTO access_records
            (employee_id, employee_name, department, role, system_name, privilege_level,
             mfa_enabled, account_status, last_reviewed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (row["employee_id"], row["employee_name"], row["department"], row["role"],
             row["system_name"], row["privilege_level"], int(row["mfa_enabled"]),
             row["account_status"], row.get("last_reviewed", "")))
        record = dict(row)
        record["mfa_enabled"] = int(record["mfa_enabled"])
        for control, severity, finding, recommendation in evaluate(record):
            conn.execute("""INSERT INTO findings
                (record_id, control_name, severity, finding, recommendation)
                VALUES (?, ?, ?, ?, ?)""",
                (cur.lastrowid, control, severity, finding, recommendation))
            generated += 1
        inserted += 1
    conn.commit()
    conn.close()
    return jsonify(inserted=inserted, findings_generated=generated)

@app.route("/api/findings/<int:finding_id>", methods=["PATCH"])
def update_finding(finding_id):
    status = request.json.get("status")
    if status not in {"Open", "In Progress", "Resolved"}:
        return jsonify(error="Invalid status"), 400
    conn = connect()
    cur = conn.execute("UPDATE findings SET status=? WHERE id=?", (status, finding_id))
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        return jsonify(error="Finding not found"), 404
    return jsonify(status=status)

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

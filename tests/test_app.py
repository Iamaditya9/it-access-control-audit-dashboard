import io
import pytest
from app import app, init_db

@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr("app.DB", tmp_path / "test.db")
    init_db()
    return app.test_client()

def test_summary_starts_empty(client):
    response = client.get("/api/summary")
    assert response.status_code == 200
    assert response.json["total_records"] == 0

def test_import_generates_findings(client):
    csv_data = (
    "employee_id,employee_name,department,role,system_name,privilege_level,mfa_enabled,account_status,last_reviewed\n"
    "E1,Alex Doe,Finance,finance-admin,ERP,admin,0,active,2026-08-01\n"
)
    response = client.post("/api/import", data={"file": (io.BytesIO(csv_data.encode()), "evidence.csv")})
    assert response.status_code == 200
    assert response.json["inserted"] == 1
    assert response.json["findings_generated"] >= 2

def test_invalid_file_is_rejected(client):
    response = client.post("/api/import", data={"file": (io.BytesIO(b"hello"), "evidence.txt")})
    assert response.status_code == 400

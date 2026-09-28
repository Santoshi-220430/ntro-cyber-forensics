import sys
import os
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.main import app

client = TestClient(app)

def test_api_health_and_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["problem_id"] == "SIH26148"

    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "HEALTHY"

def test_auth_login():
    res = client.post("/api/auth/login", json={
        "username": "investigator",
        "password": "Forensic@123"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["role"] == "INVESTIGATOR"
    return data["access_token"]

def test_full_api_workflow():
    token = test_auth_login()
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Get Cases
    res = client.get("/api/cases", headers=headers)
    assert res.status_code == 200
    cases = res.json()
    assert len(cases) > 0
    case_id = cases[0]["id"]

    # 2. Validate Script
    script = """
    CASE "CASE-2026-001"
    GET SYSTEM
    GET USERS
    GET PROCESSES
    GET NETWORK
    GET LOGS
    GET FILES "/sample_data"
    HASH FILES
    BUILD TIMELINE
    ANALYZE
    GENERATE REPORT "PDF"
    VERIFY INTEGRITY
    """
    val_res = client.post("/api/scripts/validate", json={"script": script, "case_id": case_id}, headers=headers)
    assert val_res.status_code == 200
    assert val_res.json()["valid"] is True

    # 3. Execute Script
    exec_res = client.post("/api/scripts/execute", json={
        "script": script,
        "case_id": case_id,
        "security_mode": "AUTHORIZED"
    }, headers=headers)
    assert exec_res.status_code == 200
    exec_data = exec_res.json()
    assert exec_data["status"] == "SUCCESS"
    assert exec_data["security_eval"]["security_status"] == "AUTHORIZED"

    # 4. Get System Info
    sys_res = client.get(f"/api/cases/{case_id}/system", headers=headers)
    assert sys_res.status_code == 200
    assert "hostname" in sys_res.json()

    # 5. Get Processes
    proc_res = client.get(f"/api/cases/{case_id}/processes", headers=headers)
    assert proc_res.status_code == 200
    assert len(proc_res.json()) > 0

    # 6. Get Timeline
    tle_res = client.get(f"/api/cases/{case_id}/timeline", headers=headers)
    assert tle_res.status_code == 200
    assert len(tle_res.json()) > 0

    # 7. Get Findings
    fnd_res = client.get(f"/api/cases/{case_id}/findings", headers=headers)
    assert fnd_res.status_code == 200
    assert len(fnd_res.json()) > 0

    # 8. Check Security Compatibility Status
    sec_res = client.get("/api/security/compatibility", headers=headers)
    assert sec_res.status_code == 200
    assert sec_res.json()["active_policy"] == "FORENSIC_READ_ONLY"

    # 9. Test Security Simulation
    sim_res = client.post("/api/security/simulate", json={
        "mode": "SIMULATION",
        "script": "GET SYSTEM\nGET PROCESSES",
        "case_id": case_id
    }, headers=headers)
    assert sim_res.status_code == 200
    sim_data = sim_res.json()
    assert sim_data["mode"] == "SIMULATION"
    assert len(sim_data["simulation_steps"]) == 5

    # 10. PCAP Analysis
    pcap_res = client.post("/api/pcap/analyze", data={"use_sample": "true"}, headers=headers)
    assert pcap_res.status_code == 200
    assert pcap_res.json()["total_packets"] > 0

    print("\nALL FASTAPI INTEGRATION TESTS PASSED PERFECTLY!")

if __name__ == "__main__":
    test_api_health_and_root()
    test_full_api_workflow()

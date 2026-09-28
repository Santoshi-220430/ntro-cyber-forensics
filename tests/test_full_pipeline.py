import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from forensic_dsl import Lexer, Parser, DSLValidator
from forensic_dsl.interpreter import DSLInterpreter
from backend.app.database import init_db, seed_default_data, get_db_connection

def test_pipeline():
    init_db()
    seed_default_data()

    script = """
    CASE "CASE-2026-001"
    SET MODE = "DEMO"
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

    user = {
        "id": "usr-investigator",
        "username": "investigator",
        "role": "INVESTIGATOR",
        "full_name": "Lead DFIR Analyst",
        "badge_number": "NTRO-INV-42"
    }

    # Lex
    tokens = Lexer(script).tokenize()
    # Parse
    ast = Parser(tokens).parse()
    # Validate
    valid, errors, warnings = DSLValidator(user_role=user["role"]).validate(ast)
    assert valid is True, f"Validation errors: {errors}"

    # Interpret
    interpreter = DSLInterpreter(current_user=user, security_mode="AUTHORIZED")
    result = interpreter.execute(ast)

    print("\n=== EXECUTION LOGS ===")
    for line in result["logs"]:
        print(line)

    assert result["status"] == "SUCCESS"
    assert result["results"]["system"] is not None
    assert result["results"]["processes_count"] > 0
    assert result["results"]["files_count"] > 0
    assert result["results"]["connections_count"] > 0
    assert result["results"]["timeline_events_count"] > 0
    assert result["results"]["findings_count"] > 0
    assert result["results"]["report"] is not None
    assert os.path.exists(result["results"]["report"]["filename"]) or os.path.exists(os.path.join("backend/app/reports_vault", result["results"]["report"]["filename"]))

    # Check chain of custody
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as cnt FROM chain_of_custody WHERE case_id = ?;", (result["case_id"],))
    coc_count = c.fetchone()["cnt"]
    print(f"\nChain of Custody entries recorded: {coc_count}")
    assert coc_count >= 5

    # Check audit logs
    c.execute("SELECT COUNT(*) as cnt FROM audit_logs;")
    audit_count = c.fetchone()["cnt"]
    print(f"Audit log entries recorded: {audit_count}")
    assert audit_count >= 5
    conn.close()

    print("\nFULL PIPELINE TEST PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_pipeline()

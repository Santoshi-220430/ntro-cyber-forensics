"""
Idempotency and Deduplication Verification Test
"""
import sys
import os

ROOT = os.path.abspath(os.path.dirname(__file__) + "/..")
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.app.database import init_db, seed_default_data, get_db_connection
from forensic_dsl import Lexer, Parser
from forensic_dsl.interpreter import DSLInterpreter

init_db()
seed_default_data()

script = """
CASE "CASE-2026-001"
SET MODE = "DEMO"
GET SYSTEM
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

print("[*] Executing Run 1...")
ast1 = Parser(Lexer(script).tokenize()).parse()
DSLInterpreter(current_user=user).execute(ast1, default_case_id="case-2026-001-uuid")

print("[*] Executing Run 2 (Testing for duplicate creation)...")
ast2 = Parser(Lexer(script).tokenize()).parse()
DSLInterpreter(current_user=user).execute(ast2, default_case_id="case-2026-001-uuid")

print("[*] Executing Run 3 (Testing for duplicate creation)...")
ast3 = Parser(Lexer(script).tokenize()).parse()
DSLInterpreter(current_user=user).execute(ast3, default_case_id="case-2026-001-uuid")

conn = get_db_connection()
c = conn.cursor()
c.execute("SELECT count(*) FROM evidence")
ev_count = c.fetchone()[0]
c.execute("SELECT count(*) FROM findings")
fnd_count = c.fetchone()[0]
c.execute("SELECT count(*) FROM reports")
rep_count = c.fetchone()[0]

print(f"Final Counts -> Evidence: {ev_count}, Findings: {fnd_count}, Reports: {rep_count}")

# Verify evidence uniqueness
c.execute("SELECT name, count(*) FROM evidence GROUP BY case_id, name HAVING count(*) > 1")
dups = c.fetchall()
conn.close()

if dups:
    print(f"[!] FAILED: Found duplicate evidence records: {dups}")
    sys.exit(1)
else:
    print("[+] SUCCESS: Zero duplicate evidence records across repeated execution runs!")

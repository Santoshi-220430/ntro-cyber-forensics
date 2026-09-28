import sys
import os

# Add parent directory to sys.path so forensic_dsl can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from forensic_dsl import Lexer, Parser, DSLValidator

def test_dsl_parsing_and_validation():
    script = """
    # Forensic Investigation Script for Case 2026-001
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

    lexer = Lexer(script)
    tokens = lexer.tokenize()
    print(f"Tokenized {len(tokens)} tokens successfully.")

    parser = Parser(tokens)
    ast = parser.parse()
    print(f"Parsed {len(ast.statements)} statements:")
    for i, s in enumerate(ast.statements):
        print(f"  [{i}] {s}")
    assert len(ast.statements) == 12 or len(ast.statements) == 13

    validator = DSLValidator(user_role="INVESTIGATOR")
    is_valid, errors, warnings = validator.validate(ast)
    print(f"Validation valid: {is_valid}, errors: {errors}, warnings: {warnings}")
    assert is_valid is True
    assert len(errors) == 0

def test_destructive_command_blocking():
    bad_script = """
    CASE "CASE-BAD"
    GET SYSTEM
    DELETE SYSTEM FILES
    KILL PROCESS 1337
    """
    lexer = Lexer(bad_script)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    validator = DSLValidator(user_role="INVESTIGATOR")
    is_valid, errors, warnings = validator.validate(ast)
    print("Destructive script validation result:")
    print("is_valid:", is_valid)
    print("errors:", errors)
    assert is_valid is False
    assert any("COMMAND BLOCKED" in e["message"] for e in errors)

def test_path_traversal_blocking():
    bad_script = """
    CASE "CASE-ATTACK"
    GET FILES "../../etc/shadow"
    """
    lexer = Lexer(bad_script)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    validator = DSLValidator(user_role="INVESTIGATOR")
    is_valid, errors, warnings = validator.validate(ast)
    assert is_valid is False
    assert any("Path traversal" in e["message"] for e in errors)
    print("Path traversal blocked successfully.")

def test_rbac_restrictions():
    script = """
    CASE "CASE-VIEW"
    GET SYSTEM
    GENERATE REPORT
    """
    lexer = Lexer(script)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    # VIEWER role
    validator = DSLValidator(user_role="VIEWER")
    is_valid, errors, warnings = validator.validate(ast)
    assert is_valid is False
    assert any("RBAC_PERMISSION_DENIED" in e["code"] for e in errors)
    print("Viewer RBAC check blocked unauthorized commands successfully.")

if __name__ == "__main__":
    test_dsl_parsing_and_validation()
    test_destructive_command_blocking()
    test_path_traversal_blocking()
    test_rbac_restrictions()
    print("\nALL DSL TESTS PASSED!")

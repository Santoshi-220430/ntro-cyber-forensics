@echo off
echo ========================================================
echo   RUNNING NTRO FORENSIC PLATFORM AUTOMATED TEST SUITE
echo ========================================================

echo [1/3] Running Forensic DSL Lexer, Parser & Validator Tests...
python tests/test_dsl.py
if %ERRORLEVEL% NEQ 0 (
    echo [!] DSL Tests Failed.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/3] Running Full Forensic Execution Pipeline Tests...
python tests/test_full_pipeline.py
if %ERRORLEVEL% NEQ 0 (
    echo [!] Pipeline Tests Failed.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [3/3] Running FastAPI REST Endpoint & Security Tests...
python tests/test_api.py
if %ERRORLEVEL% NEQ 0 (
    echo [!] API Tests Failed.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ========================================================
echo   ALL AUTOMATED TESTS PASSED SUCCESSFULLY (100%%)
echo ========================================================
pause

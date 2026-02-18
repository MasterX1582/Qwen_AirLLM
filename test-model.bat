@echo off
REM Test Qwen model loading (before starting API server)

echo ═══════════════════════════════════════════════════════════
echo   TESTING QWEN MODEL
echo ═══════════════════════════════════════════════════════════
echo.
echo This will test model loading and basic inference.
echo First run takes 5-15 minutes (building cache).
echo.
pause

echo.
echo Running test...
echo.

docker-compose exec qwen-airllm python3 /app/test_model.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ═══════════════════════════════════════════════════════════
    echo   TEST SUCCESSFUL
    echo ═══════════════════════════════════════════════════════════
    echo.
    echo Model is working! You can now:
    echo   1. Stop test container: stop.bat
    echo   2. Start API server: start.bat
    echo   3. Test API: test.bat
    echo.
) else (
    echo.
    echo ═══════════════════════════════════════════════════════════
    echo   TEST FAILED
    echo ═══════════════════════════════════════════════════════════
    echo.
    echo Check error messages above.
    echo.
)

pause

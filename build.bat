@echo off
REM Build Qwen AirLLM Docker Image

echo ═══════════════════════════════════════════════════════════
echo   BUILDING QWEN AIRLLM DOCKER IMAGE
echo ═══════════════════════════════════════════════════════════
echo.

REM Check if setup has been run
if not exist D:\qwen-data\cache (
    echo ❌ ERROR: Directories not initialized
    echo.
    echo Please run setup.bat first to create required directories
    echo.
    pause
    exit /b 1
)

echo Building stateless container image...
echo.
docker-compose build

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ═══════════════════════════════════════════════════════════
    echo   BUILD SUCCESSFUL
    echo ═══════════════════════════════════════════════════════════
    echo.
    echo Container is stateless - all data on host:
    echo   • D:\AI-Models            (model files, read-only)
    echo   • D:\qwen-data\cache      (layer cache, persistent)
    echo   • D:\qwen-data\logs       (server logs, persistent)
    echo   • config\server-config.yml (settings, editable)
    echo.
    echo Next steps:
    echo   1. Run: start.bat
    echo   2. Wait for "Model loaded successfully!"
    echo   3. Test: test.bat
    echo.
) else (
    echo.
    echo ❌ BUILD FAILED!
    echo.
    echo Check error messages above
    pause
    exit /b 1
)

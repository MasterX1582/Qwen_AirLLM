@echo off
REM Stop Qwen AirLLM Inference Server

echo Stopping Qwen inference server...
docker-compose down

if %ERRORLEVEL% EQU 0 (
    echo ✅ Server stopped
) else (
    echo ❌ Failed to stop server
    exit /b 1
)

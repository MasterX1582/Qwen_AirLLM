@echo off
REM Start Qwen AirLLM Inference Server

echo Starting Qwen inference server...
docker-compose up -d

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Server starting...
    echo.
    echo Monitor logs with: docker-compose logs -f
    echo.
    echo ⏳ Model loading will take several minutes...
    echo Look for "Model loaded successfully!" message
    echo.
    echo API endpoint: http://localhost:8888
    echo.
    timeout /t 5 /nobreak >nul
    docker-compose logs -f
) else (
    echo ❌ Failed to start server!
    exit /b 1
)

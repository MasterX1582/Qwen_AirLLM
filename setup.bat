@echo off
REM Setup Qwen AirLLM persistent directories

echo ═══════════════════════════════════════════════════════════
echo   QWEN AIRLLM - INITIAL SETUP
echo ═══════════════════════════════════════════════════════════
echo.

REM Check if D:\qwen-data exists
if exist D:\qwen-data (
    echo ⚠️  D:\qwen-data already exists
    echo.
    choice /C YN /M "Do you want to recreate directories (will delete existing cache)?"
    if errorlevel 2 goto skip_create
    echo.
    echo Removing old directories...
    rmdir /S /Q D:\qwen-data
)

:create
echo Creating persistent directories...
mkdir D:\qwen-data
mkdir D:\qwen-data\cache
mkdir D:\qwen-data\logs
mkdir D:\qwen-data\cache\layer_shards
mkdir D:\qwen-data\cache\huggingface

echo.
echo ✅ Directories created:
echo    D:\qwen-data\cache         (AirLLM layer cache)
echo    D:\qwen-data\logs          (Server logs)
echo.

:skip_create
echo Checking model directory...
if not exist D:\AI-Models\Qwen3.5-397B-A17B (
    echo ❌ ERROR: Model not found at D:\AI-Models\Qwen3.5-397B-A17B
    echo.
    echo Please ensure model is downloaded to D:\AI-Models\Qwen3.5-397B-A17B
    exit /b 1
)
echo ✅ Model found at D:\AI-Models\Qwen3.5-397B-A17B
echo.

echo Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Docker not found or not running
    echo.
    echo Please install Docker Desktop and ensure it's running
    exit /b 1
)
echo ✅ Docker is available
echo.

echo Checking NVIDIA Docker runtime...
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: NVIDIA Docker runtime not available
    echo.
    echo Please ensure:
    echo   1. Docker Desktop is running
    echo   2. WSL2 backend is enabled
    echo   3. NVIDIA drivers are installed
    echo   4. nvidia-docker2 is configured
    exit /b 1
)
echo ✅ NVIDIA GPU available in Docker
echo.

echo ═══════════════════════════════════════════════════════════
echo   SETUP COMPLETE
echo ═══════════════════════════════════════════════════════════
echo.
echo Next steps:
echo   1. Review config\server-config.yml (optional)
echo   2. Run: build.bat
echo   3. Run: start.bat
echo.

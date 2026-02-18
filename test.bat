@echo off
REM Test Qwen AirLLM Inference Server

echo Testing Qwen inference server...
echo.

REM Test health endpoint
echo [1/3] Testing health endpoint...
curl -s http://localhost:8888/ | python -m json.tool
echo.

REM Test models list
echo [2/3] Testing models endpoint...
curl -s http://localhost:8888/v1/models | python -m json.tool
echo.

REM Test chat completion
echo [3/3] Testing chat completion...
curl -s -X POST http://localhost:8888/v1/chat/completions ^
  -H "Content-Type: application/json" ^
  -d "{\"model\": \"Qwen/Qwen3.5-397B-A17B\", \"messages\": [{\"role\": \"user\", \"content\": \"Hello! Who are you?\"}], \"max_tokens\": 100}" | python -m json.tool
echo.

echo ✅ Tests complete!

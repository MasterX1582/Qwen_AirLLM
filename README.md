# Qwen3.5-397B-A17B AirLLM Inference Server

[![GitHub](https://img.shields.io/badge/GitHub-MasterX1582%2FQwen__AirLLM-blue?logo=github)](https://github.com/MasterX1582/Qwen_AirLLM)

OpenAI-compatible API server for running Qwen3.5-397B-A17B locally using AirLLM.

> **Note:** Uses a patched [AirLLM](https://github.com/lyogavin/airllm) wheel (`airllm-2.12.0`) with Qwen3.5 MoE support. See [MasterX1582/airllm](https://github.com/MasterX1582/airllm) for the fork.

## Architecture

**Stateless Container + Persistent Volumes:**

```
Host (Windows)                  Container (Docker)
├── D:\AI-Models\              → /models (read-only)
├── D:\qwen-data\
│   ├── cache\                 → /cache (AirLLM layer cache)
│   └── logs\                  → /app/logs
└── ./config\                  → /app/config (read-only)
    └── server-config.yml        (server settings)
```

**Benefits:**
- ✅ **Stateless container** - can rebuild without losing anything
- ✅ **Fast restarts** - cached layers = 10x faster second load
- ✅ **Config changes** - edit YAML, restart (no rebuild)
- ✅ **Persistent logs** - survive container rebuilds
- ✅ **Safe** - model is read-only mounted

## Hardware Requirements

- **GPU:** NVIDIA GPU with 24GB+ VRAM (RTX 3090 Ti ✅)
- **RAM:** 64GB+ system memory ✅
- **Disk:** 
  - 807GB for model (D:\AI-Models)
  - ~200GB for cache (D:\qwen-data\cache)
  - Docker overhead (~10GB)
- **OS:** Windows with Docker Desktop + WSL2

## Quick Start

### 0. Initial Setup (One-time)

```cmd
setup.bat
```

**Creates:**
- `D:\qwen-data\cache` - AirLLM layer cache (fast restarts)
- `D:\qwen-data\logs` - Persistent logs

**Checks:**
- Model exists at `D:\AI-Models\Qwen3.5-397B-A17B` ✅
- Docker is running ✅
- NVIDIA GPU available ✅

### 1. Build Docker Image

```cmd
build.bat
```

This builds the **stateless** Docker image (~5 minutes).

### 2. Start Server

```cmd
start.bat
```

**Expected behavior:**
- Container starts in background
- Model loading begins (takes 5-15 minutes for 807GB model)
- Logs show progress: "Loading model from /models/Qwen3.5-397B-A17B..."
- Wait for: **"Model loaded successfully!"**

**Monitor logs:**
```cmd
docker-compose logs -f
```

Press `Ctrl+C` to exit logs (server keeps running).

### 3. Test Server

```cmd
test.bat
```

**Tests:**
1. Health check (`/`)
2. Models list (`/v1/models`)
3. Chat completion (`/v1/chat/completions`)

**Expected output:**
```json
{
  "choices": [
    {
      "message": {
        "content": "Hello! I am Qwen...",
        "role": "assistant"
      }
    }
  ]
}
```

### 4. Stop Server

```cmd
stop.bat
```

## Configuration

**File:** `config/server-config.yml` (mounted from host, no rebuild needed)

**Edit settings:**
```yaml
model:
  max_tokens: 4096  # Change this
  temperature: 0.7

inference:
  max_new_tokens: 2048  # Or this
```

**Apply changes:**
```cmd
.\stop.bat
.\start.bat
```

**No rebuild needed!** Container reads config from mounted file.

## API Endpoints

**Base URL:** `http://localhost:8888`

### Health Check
```bash
GET /
```

### List Models
```bash
GET /v1/models
```

### Chat Completions (OpenAI-compatible)
```bash
POST /v1/chat/completions
Content-Type: application/json

{
  "model": "Qwen/Qwen3.5-397B-A17B",
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "max_tokens": 1024,
  "temperature": 0.7
}
```

### Text Completions
```bash
POST /v1/completions
Content-Type: application/json

{
  "model": "Qwen/Qwen3.5-397B-A17B",
  "prompt": "Once upon a time",
  "max_tokens": 1024,
  "temperature": 0.7
}
```

## OpenClaw Integration

### Config Changes

Edit your OpenClaw config (location varies by install):

```yaml
providers:
  qwen-local:
    api: openai-completions
    baseURL: http://localhost:8888/v1
    apiKey: dummy  # Not used, but required by config
    models:
      - Qwen/Qwen3.5-397B-A17B

models:
  qwen-local:
    provider: qwen-local
    model: Qwen/Qwen3.5-397B-A17B
    maxTokens: 8192  # Adjust based on needs
```

### Set as Default Model

```bash
# Option 1: Via config
openclaw config set models.default qwen-local

# Option 2: Temporary override
openclaw chat --model qwen-local
```

### Test from OpenClaw

```bash
echo "Hello from OpenClaw!" | openclaw chat --model qwen-local
```

## Performance

**Expected speeds (RTX 3090 Ti):**
- **First load:** 5-15 minutes (807GB model → cache)
- **Cached restarts:** 1-3 minutes (loads from D:\qwen-data\cache)
- **First token:** 10-30 seconds (context loading)
- **Subsequent tokens:** 5-15 tokens/second (layer swapping overhead)
- **Memory usage:** Peaks at ~40-50GB RAM + 20GB VRAM

**Cache benefits:**
- First run: Slow (builds layer cache)
- Subsequent runs: **10x faster startup** (loads from cache)
- Cache size: ~150-200GB (stored in D:\qwen-data\cache)

**Comparison:**
- **AirLLM (current):** ~10 tokens/sec
- **vLLM (requires quantization):** ~80 tokens/sec (8x faster, but needs quantization setup)

AirLLM is slower but works immediately. You can optimize later.

## Troubleshooting

### Model Not Loading

**Error:** `Model not loaded` or 503 errors

**Fix:**
```cmd
docker-compose logs -f
```
Check for errors during model loading. Common issues:
- Insufficient disk space
- CUDA not available (check Docker GPU support)
- Model path incorrect (should be `/models/Qwen3.5-397B-A17B` inside container)

### Out of Memory

**Error:** CUDA OOM or system OOM

**Fix:**
- Close other GPU-heavy applications
- Reduce `max_tokens` in requests
- AirLLM should handle this gracefully (slower, not crash)

### Slow Inference

**Expected:** First response takes 10-30 seconds

**If extremely slow (>1 min/token):**
- Check disk I/O (task manager → performance → disk)
- Model layers swapping from slow HDD? (should be on D: which is SSD/NVMe?)
- Check GPU utilization (should be 70-90% during inference)

### Server Won't Start

**Check Docker:**
```cmd
docker ps -a
```

**Check logs:**
```cmd
docker-compose logs
```

**Rebuild:**
```cmd
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## File Structure

```
qwen-airllm/
├── Dockerfile                        # Container image definition
├── docker-compose.yml                # Service configuration
├── requirements.txt                  # Python dependencies
├── airllm-2.12.0-py3-none-any.whl   # Patched AirLLM wheel (Qwen3.5 support)
├── server.py                         # FastAPI inference server
├── test_model.py                     # Model loading test (runs inside container)
├── config/
│   └── server-config.yml             # Server settings (edit without rebuild)
├── openclaw-config-example.yml       # OpenClaw integration example
├── setup.bat                         # One-time directory setup
├── build.bat                         # Build Docker image
├── start.bat                         # Start server
├── stop.bat                          # Stop server
├── test.bat                          # Test API endpoints
├── test-model.bat                    # Test model loading directly
└── README.md                         # This file
```

## Volume Mounts

**All data persists on host - container is stateless:**

| Host Path | Container Path | Purpose | Mode |
|-----------|---------------|---------|------|
| `D:\AI-Models` | `/models` | Model files (807GB) | Read-only |
| `D:\qwen-data\cache` | `/cache` | Layer cache (~200GB) | Read-write |
| `D:\qwen-data\logs` | `/app/logs` | Server logs | Read-write |
| `./config` | `/app/config` | Server config YAML | Read-only |

**Why this matters:**
- Container rebuild = no data loss ✅
- Config changes = no rebuild needed ✅
- Cache persists = fast restarts ✅
- Logs persist = troubleshooting across rebuilds ✅

## Environment Variables

- `MODEL_PATH`: Path to model inside container (default: `/models/Qwen3.5-397B-A17B`)
- `CACHE_DIR`: Path to cache directory (default: `/cache`)
- `CUDA_VISIBLE_DEVICES`: GPU index (default: `0`)
- `CONFIG_PATH`: Path to config file (default: `/app/config/server-config.yml`)

## Next Steps

1. **Setup:** `setup.bat` (creates directories, checks requirements)
2. **Build:** `build.bat` (builds Docker image)
3. **Start:** `start.bat` (starts server)
4. **Wait:** 5-15 minutes for first model load (builds cache)
5. **Test:** `test.bat` (verify API works)
6. **Configure OpenClaw:** Update config with `qwen-local` provider
7. **Switch:** `openclaw config set models.default qwen-local`

**Subsequent restarts:** 1-3 minutes (uses cache) 🚀

---

**Built:** 2026-02-18  
**Model:** Qwen/Qwen3.5-397B-A17B (807GB, 397B params, 17B active MoE)  
**Inference:** AirLLM 2.12.0 (layer-wise loading, CPU+GPU offloading)  
**API:** OpenAI-compatible (FastAPI + uvicorn)  
**Repo:** https://github.com/MasterX1582/Qwen_AirLLM

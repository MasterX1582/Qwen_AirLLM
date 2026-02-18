#!/usr/bin/env python3
"""
OpenAI-compatible API server for Qwen3.5-397B-A17B using AirLLM
Stateless server - all config from mounted volumes, all cache persisted
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import time
import os
import yaml
import logging
from pathlib import Path

# Import AirLLM
from airllm import AutoModel

# Load configuration
CONFIG_PATH = os.getenv("CONFIG_PATH", "/app/config/server-config.yml")

def load_config():
    """Load configuration from mounted YAML file"""
    if not os.path.exists(CONFIG_PATH):
        print(f"Warning: Config file not found at {CONFIG_PATH}, using defaults")
        return {
            "server": {"host": "0.0.0.0", "port": 8000, "log_level": "info"},
            "model": {"path": "/models/Qwen3.5-397B-A17B"},
            "inference": {
                "max_new_tokens": 1024,
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 50,
            },
            "api": {"model_name": "Qwen/Qwen3.5-397B-A17B"},
            "logging": {"directory": "/app/logs", "filename": "qwen-server.log"}
        }
    
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)

config = load_config()

# Setup logging
log_dir = Path(config["logging"]["directory"])
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=config["server"]["log_level"].upper(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / config["logging"]["filename"]),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

MODEL_PATH = config["model"]["path"]
CACHE_DIR = config["inference"].get("cache_dir", "/cache")
N_LAYERS_IN_GPU = config["inference"].get("n_layers_in_gpu", None)

# Global model instance
model = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on startup, clean up on shutdown"""
    global model
    logger.info(f"Loading model from {MODEL_PATH}...")
    logger.info(f"Cache directory: {CACHE_DIR}")

    Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)

    try:
        load_kwargs = {
            "layer_shards_saving_path": os.path.join(CACHE_DIR, "layer_shards"),
        }
        if N_LAYERS_IN_GPU is not None:
            load_kwargs["n_layers_in_gpu"] = int(N_LAYERS_IN_GPU)
            logger.info(f"Using n_layers_in_gpu={N_LAYERS_IN_GPU} (manual override)")
        else:
            logger.info("n_layers_in_gpu not set - will auto-detect from available VRAM")

        model = AutoModel.from_pretrained(MODEL_PATH, **load_kwargs)
        logger.info("Model loaded successfully!")
    except Exception as e:
        logger.error(f"Error loading model: {e}", exc_info=True)
        raise

    yield

    model = None

# Initialize FastAPI
app = FastAPI(title="Qwen3.5 AirLLM Inference Server", lifespan=lifespan)

# OpenAI-compatible request models
class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    stream: Optional[bool] = False

class CompletionRequest(BaseModel):
    model: str
    prompt: str
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None


@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "ok",
        "model": MODEL_PATH,
        "cache": CACHE_DIR
    }

@app.get("/v1/models")
async def list_models():
    """OpenAI-compatible models endpoint"""
    return {
        "object": "list",
        "data": [
            {
                "id": config["api"]["model_name"],
                "object": "model",
                "created": int(time.time()),
                "owned_by": "local"
            }
        ]
    }

@app.post("/v1/chat/completions")
async def chat_completion(request: ChatCompletionRequest):
    """OpenAI-compatible chat completions endpoint"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Get parameters from request or config defaults
    max_tokens = request.max_tokens or config["inference"]["max_new_tokens"]
    temperature = request.temperature or config["inference"]["temperature"]
    
    try:
        # Convert messages to prompt
        prompt = ""
        for msg in request.messages:
            if msg.role == "system":
                prompt += f"System: {msg.content}\n"
            elif msg.role == "user":
                prompt += f"User: {msg.content}\n"
            elif msg.role == "assistant":
                prompt += f"Assistant: {msg.content}\n"
        
        prompt += "Assistant:"
        
        logger.info(f"Generating response (max_tokens={max_tokens}, temp={temperature})")
        
        # Generate response
        response = model.generate(
            prompt,
            max_new_tokens=max_tokens,
            temperature=temperature,
            top_p=config["inference"]["top_p"],
            top_k=config["inference"]["top_k"]
        )
        
        # Clean up response (remove prompt echo if present)
        if response.startswith(prompt):
            response = response[len(prompt):].strip()
        
        logger.info(f"Generated {len(response.split())} tokens")
        
        # Return OpenAI-compatible format
        return {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(response.split()),
                "total_tokens": len(prompt.split()) + len(response.split())
            }
        }
    
    except Exception as e:
        logger.error(f"Error generating response: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/completions")
async def completion(request: CompletionRequest):
    """OpenAI-compatible completions endpoint"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    max_tokens = request.max_tokens or config["inference"]["max_new_tokens"]
    temperature = request.temperature or config["inference"]["temperature"]
    
    try:
        logger.info(f"Generating completion (max_tokens={max_tokens}, temp={temperature})")
        
        response = model.generate(
            request.prompt,
            max_new_tokens=max_tokens,
            temperature=temperature,
            top_p=config["inference"]["top_p"],
            top_k=config["inference"]["top_k"]
        )
        
        logger.info(f"Generated {len(response.split())} tokens")
        
        return {
            "id": f"cmpl-{int(time.time())}",
            "object": "text_completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [
                {
                    "text": response,
                    "index": 0,
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(request.prompt.split()),
                "completion_tokens": len(response.split()),
                "total_tokens": len(request.prompt.split()) + len(response.split())
            }
        }
    
    except Exception as e:
        logger.error(f"Error generating completion: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=config["server"]["host"],
        port=config["server"]["port"],
        log_level=config["server"]["log_level"]
    )

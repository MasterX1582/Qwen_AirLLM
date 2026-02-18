#!/usr/bin/env python3
"""
Test Qwen3.5-397B-A17B model loading with AirLLM
Run this first to verify model works before starting API server
"""

import time
import sys
from airllm import AutoModel

print("=" * 70)
print("Qwen3.5-397B-A17B Model Test")
print("=" * 70)
print()

# Model path
MODEL_PATH = "/models/Qwen3.5-397B-A17B"
CACHE_DIR = "/cache"

print(f"Model path: {MODEL_PATH}")
print(f"Cache dir:  {CACHE_DIR}")
print()

# Load model
print("Loading model...")
print("⏳ First run: 5-15 minutes (building layer cache)")
print("⚡ Cached runs: 1-3 minutes (loading from cache)")
print()

start_time = time.time()

try:
    model = AutoModel.from_pretrained(
        MODEL_PATH,
        layer_shards_saving_path=f"{CACHE_DIR}/layer_shards"
    )
    
    load_time = time.time() - start_time
    print()
    print("=" * 70)
    print(f"✅ Model loaded successfully!")
    print(f"⏱️  Load time: {load_time:.1f} seconds ({load_time/60:.1f} minutes)")
    print("=" * 70)
    print()
    
except Exception as e:
    print()
    print("=" * 70)
    print(f"❌ Error loading model:")
    print(f"   {e}")
    print("=" * 70)
    sys.exit(1)

# Test inference
print("Testing inference...")
print()

test_prompts = [
    "Hello! Who are you?",
    "What is 2+2?",
    "Write a haiku about AI."
]

for i, prompt in enumerate(test_prompts, 1):
    print(f"Test {i}/{len(test_prompts)}")
    print(f"Prompt: {prompt}")
    print()
    
    try:
        start = time.time()
        response = model.generate(
            prompt,
            max_new_tokens=100,
            temperature=0.7
        )
        gen_time = time.time() - start
        
        print(f"Response: {response}")
        print(f"⏱️  Generation time: {gen_time:.1f}s")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()

print("=" * 70)
print("✅ All tests complete!")
print()
print("Next steps:")
print("  1. Exit container: exit")
print("  2. Start API server: docker-compose up -d")
print("  3. Test API: test.bat")
print("=" * 70)

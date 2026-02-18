# AirLLM Inference Server for Qwen3.5-397B-A17B
# Stateless container - all config and cache from mounted volumes

FROM nvidia/cuda:12.6.2-base-ubuntu22.04

# Install Python and dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first (for Docker layer caching)
# This layer is cached as long as requirements.txt doesn't change
COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Install airllm wheel in a separate layer so wheel updates don't re-download torch/CUDA
COPY airllm-2.13.0-py3-none-any.whl /tmp/airllm-2.13.0-py3-none-any.whl
RUN pip3 uninstall -y airllm || true && \
    pip3 install --no-cache-dir /tmp/airllm-2.13.0-py3-none-any.whl && \
    rm /tmp/airllm-2.13.0-py3-none-any.whl

# Copy server code and test script
COPY server.py /app/server.py
COPY test_model.py /app/test_model.py
RUN chmod +x /app/test_model.py

# Expose API port
EXPOSE 8000

# Create cache and log directories
RUN mkdir -p /cache /app/logs

# Start server
CMD ["python3", "server.py"]

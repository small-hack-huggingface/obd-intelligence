# Modal vLLM server for OpenAI gpt-oss-120b
# https://modal.com/docs/examples/gpt_oss_inference
#
# Deploy:  modal deploy modal_files/gpt_oss_vllm.py
# Test:    modal run modal_files/gpt_oss_vllm.py

import json
import time
from datetime import datetime, timezone
from typing import Any

import aiohttp
import modal

MINUTES = 60
VLLM_PORT = 8000
N_GPU = 1
STARTUP_TIMEOUT = 30 * MINUTES
INFERENCE_TIMEOUT = 15 * MINUTES

MODEL_NAME = "openai/gpt-oss-120b"
SERVED_MODEL_NAME = "llm"
MAX_INPUTS = 32
FAST_BOOT = False

VLLM_CONFIG: dict[str, Any] = {
    "stream-interval": 20,
    "kv-cache-dtype": "fp8",
    "max-cudagraph-capture-size": MAX_INPUTS,
    "max-num-batched-tokens": 16384,
    "max-model-len": 32768,
}

COMPILATION_CONFIG = {
    "pass_config": {"fuse_allreduce_rms": True, "eliminate_noops": True},
}

hf_cache_vol = modal.Volume.from_name("huggingface-cache", create_if_missing=True)
vllm_cache_vol = modal.Volume.from_name("vllm-cache", create_if_missing=True)
flashinfer_cache_vol = modal.Volume.from_name("flashinfer-cache", create_if_missing=True)
hf_secret = modal.Secret.from_name("huggingface-secret")

vllm_image = (
    modal.Image.from_registry(
        "nvidia/cuda:12.8.1-devel-ubuntu22.04",
        add_python="3.12",
    )
    .entrypoint([])
    .uv_pip_install(
        "vllm==0.18.1",
        "huggingface_hub[hf_transfer]==0.36.0",
    )
    # Instrumentator middleware crashes on FastAPI _IncludedRouter → 500 on /health and /v1/*
    .run_commands(
        "python -c \""
        "import re; "
        "from pathlib import Path; "
        "p = Path('/usr/local/lib/python3.12/site-packages/vllm/entrypoints/serve/instrumentator/metrics.py'); "
        "t = p.read_text(); "
        "t, n = re.subn("
        "r'Instrumentator\\([\\s\\S]*?\\)\\.add\\(\\)\\.instrument\\(app\\)\\.expose\\(app, response_class=PrometheusResponse\\)', "
        "'pass  # Instrumentator disabled: breaks /v1/chat/completions', "
        "t, count=1); "
        "assert n == 1, 'metrics.py patch failed'; "
        "p.write_text(t); "
        "print('patched vllm metrics')\""
    )
    .env({"VLLM_USE_FLASHINFER_MOE_MXFP4_MXFP8": "1"})
)

app = modal.App("gpt-oss-vllm")


@app.function(
    image=vllm_image,
    gpu=f"H200:{N_GPU}",
    scaledown_window=10 * MINUTES,
    timeout=STARTUP_TIMEOUT,
    secrets=[hf_secret],
    volumes={
        "/root/.cache/huggingface": hf_cache_vol,
        "/root/.cache/vllm": vllm_cache_vol,
        "/root/.cache/flashinfer": flashinfer_cache_vol,
    },
)
@modal.concurrent(max_inputs=MAX_INPUTS)
@modal.web_server(port=VLLM_PORT, startup_timeout=STARTUP_TIMEOUT)
def serve():
    import subprocess

    cmd = [
        "vllm",
        "serve",
        MODEL_NAME,
        "--served-model-name",
        SERVED_MODEL_NAME,
        "--host",
        "0.0.0.0",
        "--port",
        str(VLLM_PORT),
        "--async-scheduling",
        "--tensor-parallel-size",
        str(N_GPU),
        "--compilation-config",
        json.dumps(COMPILATION_CONFIG),
    ]
    cmd += ["--enforce-eager" if FAST_BOOT else "--no-enforce-eager"]
    cmd += [item for k, v in VLLM_CONFIG.items() for item in (f"--{k}", str(v))]

    print("Starting vLLM:", cmd)
    subprocess.Popen(cmd)


@app.local_entrypoint()
async def test(test_timeout: int = 30 * MINUTES):
    url = await serve.get_web_url.aio()
    system_prompt = {
        "role": "system",
        "content": (
            f"You are a helpful assistant.\n"
            f"Knowledge cutoff: 2024-06\n"
            f"Current date: {datetime.now(timezone.utc).date()}\n"
            f"Reasoning: low"
        ),
    }
    messages = [
        system_prompt,
        {"role": "user", "content": "Say hello in one sentence."},
    ]

    async with aiohttp.ClientSession(
        base_url=url, timeout=aiohttp.ClientTimeout(total=test_timeout)
    ) as session:
        print(f"Running health check for server at {url}")
        async with session.get("/health", timeout=test_timeout - MINUTES) as resp:
            assert resp.status == 200, f"Health check failed: {resp.status}"
        print(f"Health check OK: {url}")
        print(f"Sending messages to {url}")
        t = time.perf_counter()
        await _send_request(session, messages)
        print(f"Time to last token: {time.perf_counter() - t:.2f}s")


async def _send_request(session: aiohttp.ClientSession, messages: list) -> None:
    payload: dict[str, Any] = {
        "messages": messages,
        "model": SERVED_MODEL_NAME,
        "stream": True,
    }
    headers = {"Content-Type": "application/json", "Accept": "text/event-stream"}

    async with session.post(
        "/v1/chat/completions", json=payload, headers=headers, timeout=INFERENCE_TIMEOUT
    ) as resp:
        async for raw in resp.content:
            resp.raise_for_status()
            line = raw.decode().strip()
            if not line or line == "data: [DONE]":
                continue
            if line.startswith("data: "):
                line = line[len("data: ") :]
            chunk = json.loads(line)
            delta = chunk["choices"][0]["delta"]
            content = (
                delta.get("content")
                or delta.get("reasoning_content")
                or delta.get("reasoning")
            )
            if content:
                print(content, end="")
    print()

# Modal vLLM server for NVIDIA Nemotron-3-Nano-30B-A3B-BF16
# https://modal.com/docs/examples/vllm_inference
#
# Deploy:  modal deploy modal_files/nemotron-nano-vllm.py
# Test:    modal run modal_files/nemotron-nano-vllm.py
#          python modal_files/inference.py
#
# Requires Modal Secret "huggingface-secret" with HF_TOKEN if the model is gated.

import json
from typing import Any

import aiohttp
import modal

MINUTES = 60  # seconds
VLLM_PORT = 8000
N_GPU = 1
STARTUP_TIMEOUT = 30 * MINUTES
INFERENCE_TIMEOUT = 15 * MINUTES

MODEL_NAME = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16"
SERVED_MODEL_NAME = MODEL_NAME
REASONING_PARSER_URL = "https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16/resolve/main/nano_v3_reasoning_parser.py"
REASONING_PARSER_PATH = "/root/nano_v3_reasoning_parser.py"

MAX_MODEL_LEN = 262144
MAX_NUM_SEQS = 3
FAST_BOOT = False

hf_cache_vol = modal.Volume.from_name("huggingface-cache", create_if_missing=True)
vllm_cache_vol = modal.Volume.from_name("vllm-cache", create_if_missing=True)
hf_secret = modal.Secret.from_name("huggingface-secret")

vllm_image = (
    modal.Image.from_registry("nvidia/cuda:12.9.0-devel-ubuntu22.04", add_python="3.12")
    .entrypoint([])
    .uv_pip_install("vllm")
    # Instrumentator middleware crashes on FastAPI _IncludedRouter → 500 on /v1/*
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
    .run_commands(
        f"python -c \"import urllib.request; "
        f"urllib.request.urlretrieve('{REASONING_PARSER_URL}', '{REASONING_PARSER_PATH}')\""
    )
    .env(
        {
            "HF_XET_HIGH_PERFORMANCE": "1",
            "VLLM_LOG_STATS_INTERVAL": "1",
        }
    )
)

app = modal.App("nemotron-nano-vllm")


@app.function(
    image=vllm_image,
    gpu=f"H200:{N_GPU}",
    min_containers=1,  # keep one replica warm so the URL stays up
    max_containers=1,
    buffer_containers=0,
    scaledown_window=15 * MINUTES,
    timeout=STARTUP_TIMEOUT,
    secrets=[hf_secret],
    volumes={
        "/root/.cache/huggingface": hf_cache_vol,
        "/root/.cache/vllm": vllm_cache_vol,
    },
)
@modal.concurrent(max_inputs=MAX_NUM_SEQS)
@modal.web_server(port=VLLM_PORT, startup_timeout=STARTUP_TIMEOUT)
def serve():
    import subprocess

    cmd = [
        "vllm",
        "serve",
        MODEL_NAME,
        "--served-model-name",
        SERVED_MODEL_NAME,
        "--max-num-seqs",
        str(MAX_NUM_SEQS),
        "--tensor-parallel-size",
        str(N_GPU),
        "--max-model-len",
        str(MAX_MODEL_LEN),
        "--host",
        "0.0.0.0",
        "--port",
        str(VLLM_PORT),
        "--trust-remote-code",
        "--enable-auto-tool-choice",
        "--tool-call-parser",
        "qwen3_coder",
        "--reasoning-parser-plugin",
        REASONING_PARSER_PATH,
        "--reasoning-parser",
        "nano_v3",
        "--uvicorn-log-level",
        "info",
        "--async-scheduling",
    ]
    cmd += ["--enforce-eager" if FAST_BOOT else "--no-enforce-eager"]
    print("Starting vLLM:", " ".join(cmd))
    # shell=True matches Modal's vLLM example; forwards all OpenAI routes on port 8000
    subprocess.Popen(" ".join(cmd), shell=True)


@app.local_entrypoint()
async def test():
    url = await serve.get_web_url.aio()
    messages = [{"role": "user", "content": "Say hello in one sentence."}]

    async with aiohttp.ClientSession(
        base_url=url, timeout=aiohttp.ClientTimeout(total=INFERENCE_TIMEOUT)
    ) as session:
        print(f"Sending to {url}")
        await _send_request(session, messages)


async def _send_request(session: aiohttp.ClientSession, messages: list) -> None:
    payload: dict[str, Any] = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": True,
    }
    payload["chat_template_kwargs"] = {"enable_thinking": True}
    headers = {"Content-Type": "application/json", "Accept": "text/event-stream"}

    async with session.post(
        "/v1/chat/completions", json=payload, headers=headers
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
                or delta.get("reasoning")
                or delta.get("reasoning_content")
            )
            if content:
                print(content, end="")
    print()


"""Client for the deployed Nemotron vLLM server.

  modal run modal_files/inference.py
  python modal_files/inference.py
"""

import asyncio
import json
import sys

import aiohttp
import modal

app = modal.App("nemotron-inference")

MODEL_NAME = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16"
BASE_URL = "https://altondsouza02--nemotron-nano-vllm-serve-dev.modal.run"
PROMPT = "Say hello in one sentence."
INFERENCE_TIMEOUT = 15 * 60  # seconds

serve = modal.Function.from_name("nemotron-nano-vllm", "serve")


async def chat(base_url: str) -> None:
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": PROMPT}],
        "stream": True,
        "chat_template_kwargs": {"enable_thinking": True},
    }
    headers = {"Content-Type": "application/json", "Accept": "text/event-stream"}

    async with aiohttp.ClientSession(
        base_url=base_url, timeout=aiohttp.ClientTimeout(total=INFERENCE_TIMEOUT)
    ) as session:
        print(f"Sending to {base_url}")
        async with session.post("/v1/chat/completions", json=payload, headers=headers) as resp:
            resp.raise_for_status()
            async for raw in resp.content:
                line = raw.decode().strip()
                if not line or line == "data: [DONE]":
                    continue
                if line.startswith("data: "):
                    line = line[len("data: ") :]
                chunk = json.loads(line)
                delta = chunk["choices"][0]["delta"]
                text = (
                    delta.get("content")
                    or delta.get("reasoning")
                    or delta.get("reasoning_content")
                )
                if text:
                    print(text, end="", flush=True)
    print()


@app.local_entrypoint()
async def main():
    url = await serve.get_web_url.aio()
    await chat(url)


if __name__ == "__main__":
    try:
        asyncio.run(chat(BASE_URL))
    except aiohttp.ClientError as exc:
        print(f"Request failed: {exc}", file=sys.stderr)
        sys.exit(1)

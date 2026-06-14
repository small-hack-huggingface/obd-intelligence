"""Test the vLLM server with ChatOpenAI and a fixed base URL.

  pip install langchain-openai
  python modal_files/test_client.py
"""

import sys

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

BASE_URL = "https://altondsouza02--nemotron-nano-vllm-serve-dev.modal.run"
MODEL_NAME = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16"
PROMPT = "Say hello in one sentence."
INFERENCE_TIMEOUT = 15 * 60  # seconds

llm = ChatOpenAI(
    base_url=f"{BASE_URL.rstrip('/')}/v1",
    api_key="not-needed",
    model=MODEL_NAME,
    timeout=INFERENCE_TIMEOUT,
)

if __name__ == "__main__":
    try:
        response = llm.invoke(
            [HumanMessage(content=PROMPT)],
            extra_body={"chat_template_kwargs": {"enable_thinking": True}},
        )
        print(response.content)
    except Exception as exc:
        print(f"Request failed: {exc}", file=sys.stderr)
        sys.exit(1)

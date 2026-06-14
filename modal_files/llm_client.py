"""Shared ChatOpenAI client for Modal Nemotron pipelines."""

from __future__ import annotations

from langchain_openai import ChatOpenAI

DEFAULT_MODEL = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16"
INFERENCE_TIMEOUT = 15 * 60


def make_llm(base_url: str, *, max_tokens: int, model: str = DEFAULT_MODEL) -> ChatOpenAI:
    return ChatOpenAI(
        base_url=f"{base_url.rstrip('/')}/v1",
        api_key="not-needed",
        model=model,
        timeout=INFERENCE_TIMEOUT,
        temperature=0.2,
        max_tokens=max_tokens,
        extra_body={"chat_template_kwargs": {"enable_thinking": False}},
    )

"""Shared ChatOpenAI client for Modal vLLM pipelines."""

from __future__ import annotations

from typing import Any

from langchain_openai import ChatOpenAI

from llm_profiles import NEMOTRON_EXTRA_BODY

DEFAULT_MODEL = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16"
INFERENCE_TIMEOUT = 15 * 60


def make_llm(
    base_url: str,
    *,
    max_tokens: int,
    model: str = DEFAULT_MODEL,
    extra_body: dict[str, Any] | None = None,
) -> ChatOpenAI:
    body = NEMOTRON_EXTRA_BODY if extra_body is None else extra_body
    kwargs: dict[str, Any] = {}
    if body:
        kwargs["extra_body"] = body
    return ChatOpenAI(
        base_url=f"{base_url.rstrip('/')}/v1",
        api_key="not-needed",
        model=model,
        timeout=INFERENCE_TIMEOUT,
        temperature=0.2,
        max_tokens=max_tokens,
        **kwargs,
    )

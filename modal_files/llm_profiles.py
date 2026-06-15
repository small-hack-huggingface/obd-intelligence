"""LLM provider profiles for Modal vLLM pipelines."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

DEFAULT_LLM_KEY = "nemotron"


@dataclass(frozen=True)
class LlmProfile:
    key: str
    modal_app: str
    hf_model: str
    api_model: str
    extra_body: dict[str, Any]
    default_base_url: str = ""


NEMOTRON_EXTRA_BODY: dict[str, Any] = {
    "chat_template_kwargs": {"enable_thinking": False},
}

GPT_OSS_API_MODEL = "llm"

GPT_OSS_EXTRA_BODY: dict[str, Any] = {
    "response_format": {"type": "json_object"},
}

PROFILES: dict[str, LlmProfile] = {
    "nemotron": LlmProfile(
        key="nemotron",
        modal_app="nemotron-nano-vllm",
        hf_model="nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16",
        api_model="nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16",
        extra_body=NEMOTRON_EXTRA_BODY,
        default_base_url="https://altondsouza02--nemotron-nano-vllm-serve-dev.modal.run",
    ),
    "gpt-oss": LlmProfile(
        key="gpt-oss",
        modal_app="gpt-oss-vllm",
        hf_model="openai/gpt-oss-120b",
        api_model="llm",
        extra_body=GPT_OSS_EXTRA_BODY,
        default_base_url="https://altondsouza02--gpt-oss-vllm-serve-dev.modal.run",
    ),
}


def resolve_profile(key: str) -> LlmProfile:
    normalized = key.strip().lower()
    if normalized not in PROFILES:
        choices = ", ".join(sorted(PROFILES))
        raise SystemExit(f"Unknown --llm {key!r}. Choose one of: {choices}")
    return PROFILES[normalized]

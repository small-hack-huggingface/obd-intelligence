"""Retry wrapper for LangChain structured-output invocations."""

from __future__ import annotations

import time
from typing import Any

from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from pydantic import BaseModel

from llm_client import DEFAULT_MODEL, make_llm


def make_structured_generator(
    base_url: str,
    schema: type[BaseModel],
    *,
    max_tokens: int,
    model: str = DEFAULT_MODEL,
) -> Runnable:
    llm = make_llm(base_url, max_tokens=max_tokens, model=model)
    for method in ("function_calling", "json_schema"):
        try:
            return llm.with_structured_output(
                schema,
                method=method,
                include_raw=True,
            )
        except Exception:
            continue
    raise RuntimeError("Could not create structured output generator")


def invoke_parsed(
    generator: Any,
    messages: list[BaseMessage],
    *,
    label: str,
    max_attempts: int = 3,
    pause_seconds: float = 2.0,
) -> Any:
    last_error = f"{label}: structured output returned None"
    for attempt in range(1, max_attempts + 1):
        raw = generator.invoke(messages)
        parsed = raw.get("parsed") if isinstance(raw, dict) else raw
        if parsed is not None:
            return parsed
        last_error = f"{label}: structured output returned None (attempt {attempt}/{max_attempts})"
        print(f"  WARN {last_error}")
        if attempt < max_attempts:
            time.sleep(pause_seconds)
    raise ValueError(last_error)

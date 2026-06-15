"""Retry wrapper for LangChain structured-output invocations."""

from __future__ import annotations

import json
import re
import time
from typing import Any

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import Runnable
from pydantic import BaseModel, ValidationError

from llm_client import DEFAULT_MODEL, make_llm
from llm_profiles import GPT_OSS_API_MODEL

GPT_OSS_JSON_SYSTEM = """Reasoning: low
Respond with ONLY a valid JSON object. No markdown fences, no text before or after the JSON."""


class JsonPromptGenerator:
    """Plain completion + JSON parse for models without reliable tool/JSON-schema support."""

    def __init__(self, llm: Any, schema: type[BaseModel]) -> None:
        self.llm = llm
        self.schema = schema

    def invoke(self, messages: list[BaseMessage]) -> dict[str, Any]:
        schema_hint = json.dumps(self.schema.model_json_schema(), indent=2)
        _min_len, max_len = _list_bounds(self.schema)
        exact_items = (
            f"The items array must contain EXACTLY {max_len} entries. "
            if max_len is not None
            else ""
        )
        augmented = _with_gpt_oss_json_system(messages)
        augmented.append(
            HumanMessage(
                content=(
                    "Respond with ONLY a valid JSON object matching this schema. "
                    "No markdown code fences, no commentary outside the JSON. "
                    f"{exact_items}\n"
                    f"Schema:\n{schema_hint}"
                )
            )
        )
        response = self.llm.invoke(augmented)
        content = _message_content(response)
        try:
            parsed = _parse_schema_json(content, self.schema)
        except (json.JSONDecodeError, ValidationError) as exc:
            return {"parsed": None, "raw": response, "content": content, "error": str(exc)}
        return {"parsed": parsed, "raw": response, "content": content}


def _with_gpt_oss_json_system(messages: list[BaseMessage]) -> list[BaseMessage]:
    out = list(messages)
    if out and isinstance(out[0], SystemMessage):
        out[0] = SystemMessage(content=f"{GPT_OSS_JSON_SYSTEM}\n\n{out[0].content}")
    else:
        out.insert(0, SystemMessage(content=GPT_OSS_JSON_SYSTEM))
    return out


def _message_content(message: Any) -> str:
    content = getattr(message, "content", message)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
        return "".join(parts)
    return str(content)


def _extract_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _list_bounds(schema: type[BaseModel], field: str = "items") -> tuple[int | None, int | None]:
    props = schema.model_json_schema().get("properties", {})
    field_schema = props.get(field, {})
    return field_schema.get("minItems"), field_schema.get("maxItems")


def _normalize_payload(data: dict[str, Any], schema: type[BaseModel]) -> dict[str, Any]:
    """Trim over-long list fields when the model returns one extra item."""
    if "items" not in data or not isinstance(data["items"], list):
        return data
    _min_len, max_len = _list_bounds(schema)
    items = data["items"]
    if max_len is not None and len(items) > max_len:
        data = {**data, "items": items[:max_len]}
    return data


def _parse_schema_json(content: str, schema: type[BaseModel]) -> BaseModel:
    data = json.loads(_extract_json(content))
    if isinstance(data, dict):
        data = _normalize_payload(data, schema)
    return schema.model_validate(data)


def make_structured_generator(
    base_url: str,
    schema: type[BaseModel],
    *,
    max_tokens: int,
    model: str = DEFAULT_MODEL,
    extra_body: dict[str, Any] | None = None,
) -> Runnable:
    llm = make_llm(
        base_url,
        max_tokens=max_tokens,
        model=model,
        extra_body=extra_body,
    )
    if model == GPT_OSS_API_MODEL:
        return JsonPromptGenerator(llm, schema)

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
        detail = ""
        if isinstance(raw, dict):
            if raw.get("error"):
                detail = f" ({raw['error']})"
            elif raw.get("content"):
                snippet = str(raw["content"]).replace("\n", " ")[:240]
                detail = f" (raw: {snippet!r}...)"
            elif raw.get("raw") is not None:
                snippet = _message_content(raw["raw"]).replace("\n", " ")[:240]
                detail = f" (raw: {snippet!r}...)"
        last_error = (
            f"{label}: structured output returned None (attempt {attempt}/{max_attempts})"
            f"{detail}"
        )
        print(f"  WARN {last_error}")
        if attempt < max_attempts:
            time.sleep(pause_seconds)
    raise ValueError(last_error)

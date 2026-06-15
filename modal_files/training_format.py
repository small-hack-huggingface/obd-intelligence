"""Convert flat training JSONL records to Nemotron chat messages for SFT."""

from __future__ import annotations

from typing import Any

THINKING_OPEN = "<think>"
THINKING_CLOSE = "</think>"


def build_assistant_content(answer: str, reasoning: str) -> str:
    """Reasoning in thinking tokens, then the final answer."""
    return f"{THINKING_OPEN}{reasoning}{THINKING_CLOSE}{answer}"


def build_nemotron_messages(record: dict[str, Any]) -> list[dict[str, str]]:
    """User = question. Assistant = <think>reasoning</think>answer."""
    question = record.get("question") or _extract_question_from_messages(record)
    if not question:
        raise ValueError(f"Record {record.get('id', '?')} has no question field")

    return [
        {"role": "user", "content": question},
        {
            "role": "assistant",
            "content": build_assistant_content(record["answer"], record["reasoning"]),
        },
    ]


def prepare_sft_record(record: dict[str, Any]) -> dict[str, Any] | None:
    """Build one Hugging Face dataset row from a flat training JSONL record."""
    if not all(record.get(k) for k in ("question", "answer", "reasoning")):
        return None
    return {
        "id": record.get("id", ""),
        "example_type": record.get("example_type", ""),
        "question": record["question"],
        "answer": record["answer"],
        "reasoning": record["reasoning"],
        "messages": build_nemotron_messages(record),
    }


def _extract_question_from_messages(record: dict[str, Any]) -> str | None:
    for turn in record.get("messages") or []:
        if turn.get("role") != "user":
            continue
        content = turn.get("content", "")
        if "Question:\n" in content:
            return content.rsplit("Question:\n", 1)[-1].strip()
        if "Question: " in content:
            return content.rsplit("Question: ", 1)[-1].strip()
    return None

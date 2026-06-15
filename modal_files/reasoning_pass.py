"""Second-pass LLM call: verbose answer + reasoning from chunk context.

Shared by both pipelines:
- modal_files/qa_generator.py (chunk Q&A)
- modal_files/term_qa_generator.py (term clarification)

Reasoning is first-person monologue with no reference to chunk/context.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import Runnable
from pydantic import BaseModel, Field

from llm_client import DEFAULT_MODEL
from structured_invoke import invoke_parsed, make_structured_generator

ROOT = Path(__file__).resolve().parents[1]
REASONING_PROMPT_PATH = ROOT / "data_consideration" / "prompts" / "verbose_reasoning.md"
REASONING_MAX_TOKENS = 8192

_FALLBACK_REASONING_SYSTEM = """Answer using the chunk context. Reasoning is first-person diagnostic monologue with no mention of the chunk or context."""

REASONING_SYSTEM = (
    REASONING_PROMPT_PATH.read_text(encoding="utf-8").strip()
    if REASONING_PROMPT_PATH.exists()
    else _FALLBACK_REASONING_SYSTEM
)


class AnswerWithReasoning(BaseModel):
    """Verbose reasoning pass output for one question."""

    answer: str = Field(description="Concise final answer grounded in the chunk context")
    reasoning: str = Field(
        description=(
            "First-person internal diagnostic monologue with no reference to chunk/context — "
            "standalone thinking as if only the question was asked (I know…, I'd check…)"
        )
    )


def make_reasoning_generator(
    base_url: str,
    model: str = DEFAULT_MODEL,
    *,
    extra_body: dict[str, Any] | None = None,
) -> Runnable:
    return make_structured_generator(
        base_url,
        AnswerWithReasoning,
        max_tokens=REASONING_MAX_TOKENS,
        model=model,
        extra_body=extra_body,
    )


def enrich_with_reasoning(
    generator: Runnable,
    chunk: dict[str, Any],
    *,
    question: str,
    term: str | None = None,
) -> dict[str, str]:
    chunk_text = chunk.get("text", "")
    category = chunk.get("category", "unknown")
    source_file = chunk.get("source_file", "unknown")

    term_block = f"Term: {term}\n" if term else ""
    messages = [
        SystemMessage(content=REASONING_SYSTEM),
        HumanMessage(
            content=(
                f"Category: {category}\n"
                f"Source file: {source_file}\n"
                f"Chunk id: {chunk.get('id', 'unknown')}\n\n"
                f"{term_block}"
                f"Question:\n{question}\n\n"
                "Write reasoning in first person as standalone internal monologue — "
                "assume the chunk context is NOT visible to the reader. Do not mention "
                "the chunk, context, or source material. Use the context below only to "
                "ensure accuracy; do not quote or cite it in reasoning.\n\n"
                f"--- Chunk context (for your use only — do not reference in reasoning) ---\n"
                f"{chunk_text[:8000]}"
            )
        ),
    ]
    result: AnswerWithReasoning = invoke_parsed(
        generator,
        messages,
        label=f"pass2 reasoning {chunk.get('id', 'unknown')}",
    )
    return {
        "answer": result.answer.strip(),
        "reasoning": result.reasoning.strip(),
    }

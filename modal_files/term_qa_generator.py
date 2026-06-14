"""Generate term-clarification Q&A from classified chunk JSONL entries."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import Runnable
from pydantic import BaseModel, Field, create_model

from jsonl_utils import (
    MAX_TERM_QUESTIONS_PER_CHUNK,
    PromptsConfig,
    QuestionsConfig,
    append_jsonl_record,
    read_jsonl,
    validate_num_questions,
)
from llm_client import DEFAULT_MODEL
from qa_generator import DEFAULT_INPUT, DEFAULT_QUESTIONS_CONFIG, DEFAULT_TRAINING_DIR, TRAINING_JSONL
from reasoning_pass import enrich_with_reasoning, make_reasoning_generator
from structured_invoke import invoke_parsed, make_structured_generator

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "generated_term_qa"
ALL_TERM_QA_JSONL = "all_term_qa.jsonl"
TERM_QA_MAX_TOKENS = 8192

_TERM_PROMPT_PATH = ROOT / "data_consideration" / "prompts" / "term_clarification.md"
_FALLBACK_TERM_SYSTEM = """You identify confusing automotive terms in documentation chunks and produce clarification Q&A grounded only in the chunk.

Return only structured fields: term, question, answer, reasoning."""

TERM_SYSTEM = (
    _TERM_PROMPT_PATH.read_text(encoding="utf-8").strip()
    if _TERM_PROMPT_PATH.exists()
    else _FALLBACK_TERM_SYSTEM
)


def make_term_schema(num_items: int) -> type[BaseModel]:
    term_item = create_model(
        "TermQuestionItem",
        term=(
            str,
            Field(
                description=(
                    "Automotive term: PID, DTC, sensor acronym, OBD concept, "
                    "or diagnostic jargon from the chunk — not generic English or electronics"
                )
            ),
        ),
        question=(
            str,
            Field(
                description=(
                    "Shop-floor learner question about the term in OBD-II / "
                    "vehicle diagnostics context"
                )
            ),
        ),
    )
    return create_model(
        "ChunkTermClarifications",
        items=(
            list[term_item],  # type: ignore[valid-type]
            Field(
                min_length=num_items,
                max_length=num_items,
                description=f"Exactly {num_items} term+question pairs (no answers yet)",
            ),
        ),
    )


def make_term_generator(
    base_url: str,
    num_items: int,
    model: str = DEFAULT_MODEL,
) -> Runnable:
    schema = make_term_schema(num_items)
    return make_structured_generator(
        base_url,
        schema,
        max_tokens=TERM_QA_MAX_TOKENS,
        model=model,
    )


class TermGeneratorCache:
    def __init__(self, base_url: str, model: str) -> None:
        self.base_url = base_url
        self.model = model
        self._generators: dict[int, Runnable] = {}

    def get(self, num_items: int) -> Runnable:
        num_items = validate_num_questions(num_items, maximum=MAX_TERM_QUESTIONS_PER_CHUNK)
        if num_items not in self._generators:
            self._generators[num_items] = make_term_generator(
                self.base_url,
                num_items,
                self.model,
            )
        return self._generators[num_items]


def load_existing_chunk_ids(output_dir: Path) -> set[str]:
    return {record["chunk_id"] for record in read_jsonl(output_dir / ALL_TERM_QA_JSONL)}


def append_term_training_examples(
    training_dir: Path,
    *,
    chunk_id: str,
    source_file: str | None,
    category: str | None,
    context: str,
    items: list[dict[str, str]],
    run_at: str,
    model: str,
) -> None:
    training_dir.mkdir(parents=True, exist_ok=True)
    for idx, item in enumerate(items):
        example = {
            "example_type": "term_clarification",
            "id": f"{chunk_id}:term:{idx}",
            "chunk_id": chunk_id,
            "question_index": idx,
            "term": item["term"],
            "category": category,
            "source_file": source_file,
            "context": context,
            "question": item["question"],
            "answer": item["answer"],
            "reasoning": item["reasoning"],
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"I don't understand the term \"{item['term']}\" in this context:\n"
                        f"{context}\n\nQuestion: {item['question']}"
                    ),
                },
                {
                    "role": "assistant",
                    "content": (
                        f"Answer:\n{item['answer']}\n\nReasoning:\n{item['reasoning']}"
                    ),
                },
            ],
            "run_at": run_at,
            "model": model,
        }
        append_jsonl_record(training_dir / TRAINING_JSONL, example)
        if category:
            append_jsonl_record(training_dir / f"{category}.jsonl", example)


def generate_chunk_term_qa(
    generator: Runnable,
    reasoning_generator: Runnable,
    chunk: dict[str, Any],
    num_items: int,
    system_prompt: str,
) -> list[dict[str, str]]:
    chunk_text = chunk.get("text", "")
    category = chunk.get("category", "unknown")
    source_file = chunk.get("source_file", "unknown")

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(
            content=(
                f"Generate exactly {num_items} term+question pairs ONLY (no answers yet).\n"
                f"Category: {category}\n"
                f"Source file: {source_file}\n"
                f"Chunk id: {chunk.get('id', 'unknown')}\n\n"
                "Prioritize automotive-specific terms: PIDs, DTCs, sensor acronyms, "
                "OBD-II concepts, fuel trims, fault signatures, and Toyota hybrid "
                "diagnostics. Skip generic physics/electronics vocabulary when "
                "automotive terms are available in the chunk.\n\n"
                f"---\n{chunk_text[:8000]}"
            )
        ),
    ]
    result = invoke_parsed(
        generator,
        messages,
        label=f"pass1 terms {chunk.get('id', 'unknown')}",
    )
    stubs = [{"term": i.term, "question": i.question} for i in result.items]
    if len(stubs) != num_items:
        raise ValueError(f"Expected {num_items} items, got {len(stubs)}")

    items: list[dict[str, str]] = []
    for idx, stub in enumerate(stubs, start=1):
        print(f"    reasoning pass {idx}/{num_items} ({stub['term']})...")
        enriched = enrich_with_reasoning(
            reasoning_generator,
            chunk,
            question=stub["question"],
            term=stub["term"],
        )
        items.append({**stub, **enriched})
    return items


def run_pipeline(
    input_jsonl: Path,
    output_dir: Path,
    base_url: str,
    *,
    training_dir: Path = DEFAULT_TRAINING_DIR,
    num_questions: int = 10,
    questions_config: Path | None = DEFAULT_QUESTIONS_CONFIG,
    fresh: bool = False,
    limit: int | None = None,
    model: str = DEFAULT_MODEL,
) -> Counter:
    validate_num_questions(num_questions, maximum=MAX_TERM_QUESTIONS_PER_CHUNK)
    questions = QuestionsConfig.load(
        questions_config,
        default=num_questions,
        section="term_questions",
    )
    prompts = PromptsConfig.from_config(
        questions_config,
        section="term_system_prompts",
        fallback_default=TERM_SYSTEM,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / ALL_TERM_QA_JSONL

    if fresh:
        output_path.unlink(missing_ok=True)
        (output_dir / "preview.md").unlink(missing_ok=True)

    chunks = read_jsonl(input_jsonl)
    if not chunks:
        raise SystemExit(f"No records in {input_jsonl}")

    if limit is not None:
        chunks = chunks[:limit]

    generators = TermGeneratorCache(base_url, model)
    reasoning_generator = make_reasoning_generator(base_url, model)
    existing_ids = load_existing_chunk_ids(output_dir)
    run_at = datetime.now(timezone.utc).isoformat()
    added_by_count: Counter = Counter()
    skipped = 0

    for chunk in chunks:
        chunk_id = chunk["id"]
        if chunk_id in existing_ids:
            skipped += 1
            continue

        chunk_num_items = validate_num_questions(
            questions.resolve(chunk),
            maximum=MAX_TERM_QUESTIONS_PER_CHUNK,
        )
        system_prompt, prompt_ref = prompts.resolve(chunk)
        print(f"Generating {chunk_num_items} term Q&A for {chunk_id} ({prompt_ref})...")
        try:
            items = generate_chunk_term_qa(
                generators.get(chunk_num_items),
                reasoning_generator,
                chunk,
                chunk_num_items,
                system_prompt,
            )
        except ValueError as exc:
            print(f"  FAILED {chunk_id}: {exc}")
            continue
        record = {
            "chunk_id": chunk_id,
            "source_file": chunk.get("source_file"),
            "chunk_index": chunk.get("chunk_index"),
            "category": chunk.get("category"),
            "chunk_text": chunk.get("text", "").strip(),
            "num_questions": chunk_num_items,
            "system_prompt_ref": prompt_ref,
            "items": items,
            "run_at": run_at,
            "generator": "structured_output_two_pass",
            "model": model,
        }
        append_jsonl_record(output_path, record)
        append_term_training_examples(
            training_dir,
            chunk_id=chunk_id,
            source_file=chunk.get("source_file"),
            category=chunk.get("category"),
            context=chunk.get("text", "").strip(),
            items=items,
            run_at=run_at,
            model=model,
        )
        existing_ids.add(chunk_id)
        added_by_count[chunk_num_items] += 1
        print(f"  saved {len(items)} items -> {ALL_TERM_QA_JSONL}, {TRAINING_JSONL}")

    write_preview(output_dir)
    print(f"\nInput:    {input_jsonl} ({len(chunks)} chunks)")
    if questions_config and questions_config.exists():
        print(f"Config:   {questions_config}")
    print(f"Output:   {output_path}")
    print(f"Training: {training_dir / TRAINING_JSONL} (appended term_clarification rows)")
    print(f"Added:    {sum(added_by_count.values())} chunks (skipped {skipped} duplicates)")
    for count, chunks_added in sorted(added_by_count.items()):
        print(f"  {count} terms/chunk: {chunks_added} chunks")
    return added_by_count


def write_preview(output_dir: Path) -> int:
    records = read_jsonl(output_dir / ALL_TERM_QA_JSONL)
    parts = [f"# Term clarification Q&A ({len(records)} chunks)\n"]
    for record in records:
        parts.append(f"## {record['chunk_id']} — `{record.get('category', '')}`\n")
        parts.append(f"**Prompt:** `{record.get('system_prompt_ref', 'default')}`  ")
        parts.append(f"**Items:** {record.get('num_questions', len(record['items']))}\n")
        for idx, item in enumerate(record["items"], start=1):
            parts.append(f"### Term {idx}: {item['term']}\n")
            parts.append(f"**Question:** {item['question']}\n")
            parts.append(f"**Answer:** {item['answer']}\n")
            parts.append(f"**Reasoning:** {item['reasoning']}\n")
        parts.append("---\n")
    preview_path = output_dir / "preview.md"
    preview_path.write_text("\n".join(parts), encoding="utf-8")
    return len(records)

"""Generate Q&A + reasoning from classified chunk JSONL entries."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import Runnable
from pydantic import BaseModel, Field, create_model

from jsonl_utils import (
    PromptsConfig,
    QuestionsConfig,
    append_jsonl_record,
    model_slug,
    read_jsonl,
    training_jsonl_path,
    validate_num_questions,
)
from llm_client import DEFAULT_MODEL
from reasoning_pass import enrich_with_reasoning, make_reasoning_generator
from structured_invoke import invoke_parsed, make_structured_generator
from training_format import build_nemotron_messages

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "classified_chunks" / "all_chunks.jsonl"
DEFAULT_OUTPUT = ROOT / "generated_qa"
DEFAULT_TRAINING_DIR = ROOT / "training_data"
DEFAULT_QUESTIONS_CONFIG = ROOT / "data_consideration" / "questions_config.json"
INFERENCE_TIMEOUT = 15 * 60
ALL_QA_JSONL = "all_qa.jsonl"
QA_MAX_TOKENS = 8192

_DEFAULT_PROMPT_PATH = ROOT / "data_consideration" / "prompts" / "default.md"
_FALLBACK_QA_SYSTEM = """You create automotive / OBD-II / Toyota hybrid training examples from documentation chunks.

Every question must be framed for shop diagnostics: PIDs, DTCs, sensors, live data, symptoms, and troubleshooting.

Ground every question, answer, and reasoning step ONLY in the chunk provided.

Return only the structured fields. Do not chain-of-thought outside the reasoning field."""

QA_SYSTEM = (
    _DEFAULT_PROMPT_PATH.read_text(encoding="utf-8").strip()
    if _DEFAULT_PROMPT_PATH.exists()
    else _FALLBACK_QA_SYSTEM
)


class GeneratorCache:
    def __init__(
        self,
        base_url: str,
        api_model: str,
        *,
        extra_body: dict[str, Any] | None = None,
    ) -> None:
        self.base_url = base_url
        self.api_model = api_model
        self.extra_body = extra_body
        self._generators: dict[int, Runnable] = {}

    def get(self, num_questions: int) -> Runnable:
        num_questions = validate_num_questions(num_questions)
        if num_questions not in self._generators:
            self._generators[num_questions] = make_qa_generator(
                self.base_url,
                num_questions,
                self.api_model,
                extra_body=self.extra_body,
            )
        return self._generators[num_questions]


def make_qa_schema(num_questions: int) -> type[BaseModel]:
    question_item = create_model(
        "QuestionItem",
        question=(
            str,
            Field(
                description=(
                    "Automotive diagnostics question answerable from the chunk — "
                    "PIDs, DTCs, symptoms, scan-tool data, or shop troubleshooting"
                )
            ),
        ),
    )
    return create_model(
        "ChunkQuestions",
        items=(
            list[question_item],  # type: ignore[valid-type]
            Field(
                min_length=num_questions,
                max_length=num_questions,
                description=f"Exactly {num_questions} questions (no answers yet)",
            ),
        ),
    )


def make_qa_generator(
    base_url: str,
    num_questions: int,
    model: str = DEFAULT_MODEL,
    *,
    extra_body: dict[str, Any] | None = None,
) -> Runnable:
    schema = make_qa_schema(num_questions)
    return make_structured_generator(
        base_url,
        schema,
        max_tokens=QA_MAX_TOKENS,
        model=model,
        extra_body=extra_body,
    )


def load_existing_chunk_ids(output_dir: Path, *, model: str) -> set[str]:
    return {
        record["chunk_id"]
        for record in read_jsonl(output_dir / ALL_QA_JSONL)
        if record.get("model", DEFAULT_MODEL) == model
    }


def append_training_examples(
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
    """Append one flat JSONL line per question for fine-tuning."""
    out_path = training_jsonl_path(training_dir, example_type="chunk_qa", model=model)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    slug = model_slug(model)
    for idx, item in enumerate(items):
        example = {
            "example_type": "chunk_qa",
            "id": f"{chunk_id}:{slug}:{idx}",
            "chunk_id": chunk_id,
            "question_index": idx,
            "category": category,
            "source_file": source_file,
            "context": context,
            "question": item["question"],
            "answer": item["answer"],
            "reasoning": item["reasoning"],
            "messages": build_nemotron_messages(
                {
                    "question": item["question"],
                    "answer": item["answer"],
                    "reasoning": item["reasoning"],
                }
            ),
            "run_at": run_at,
            "model": model,
        }
        append_jsonl_record(out_path, example)


def generate_chunk_qa(
    generator: Runnable,
    reasoning_generator: Runnable,
    chunk: dict[str, Any],
    num_questions: int,
    system_prompt: str,
) -> list[dict[str, str]]:
    chunk_text = chunk.get("text", "")
    category = chunk.get("category", "unknown")
    source_file = chunk.get("source_file", "unknown")

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(
            content=(
                f"Generate exactly {num_questions} questions ONLY (no answers yet).\n"
                f"Category: {category}\n"
                f"Source file: {source_file}\n"
                f"Chunk id: {chunk.get('id', 'unknown')}\n\n"
                "Every question must lean automotive: frame as shop-floor diagnostics "
                "using PIDs, DTCs, sensors, live data, symptoms, or Toyota hybrid/OBD-II "
                "troubleshooting. Skip generic, off-topic, or non-vehicle questions.\n\n"
                f"---\n{chunk_text[:8000]}"
            )
        ),
    ]
    result = invoke_parsed(
        generator,
        messages,
        label=f"pass1 questions {chunk.get('id', 'unknown')}",
    )
    questions = [i.question for i in result.items]
    if len(questions) != num_questions:
        raise ValueError(f"Expected {num_questions} questions, got {len(questions)}")

    items: list[dict[str, str]] = []
    for idx, question in enumerate(questions, start=1):
        print(f"    reasoning pass {idx}/{num_questions}...")
        enriched = enrich_with_reasoning(
            reasoning_generator,
            chunk,
            question=question,
        )
        items.append({"question": question, **enriched})
    return items


def run_pipeline(
    input_jsonl: Path,
    output_dir: Path,
    base_url: str,
    *,
    training_dir: Path = DEFAULT_TRAINING_DIR,
    num_questions: int = 5,
    questions_config: Path | None = DEFAULT_QUESTIONS_CONFIG,
    fresh: bool = False,
    limit: int | None = None,
    model: str = DEFAULT_MODEL,
    api_model: str | None = None,
    extra_body: dict[str, Any] | None = None,
) -> Counter:
    validate_num_questions(num_questions)
    api = api_model or model
    questions = QuestionsConfig.load(questions_config, default=num_questions)
    prompts = PromptsConfig.from_config(
        questions_config,
        section="system_prompts",
        fallback_default=QA_SYSTEM,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / ALL_QA_JSONL
    training_path = training_jsonl_path(training_dir, example_type="chunk_qa", model=model)

    if fresh:
        output_path.unlink(missing_ok=True)
        (output_dir / "preview.md").unlink(missing_ok=True)
        training_path.unlink(missing_ok=True)

    chunks = read_jsonl(input_jsonl)
    if not chunks:
        raise SystemExit(f"No records in {input_jsonl}")

    if limit is not None:
        chunks = chunks[:limit]

    generators = GeneratorCache(base_url, api, extra_body=extra_body)
    reasoning_generator = make_reasoning_generator(
        base_url, api, extra_body=extra_body
    )
    existing_ids = load_existing_chunk_ids(output_dir, model=model)
    run_at = datetime.now(timezone.utc).isoformat()
    added_by_count: Counter = Counter()
    skipped = 0

    for chunk in chunks:
        chunk_id = chunk["id"]
        if chunk_id in existing_ids:
            skipped += 1
            continue

        chunk_num_questions = validate_num_questions(questions.resolve(chunk))
        system_prompt, prompt_ref = prompts.resolve(chunk)
        print(f"Generating {chunk_num_questions} Q&A for {chunk_id} ({prompt_ref})...")
        try:
            items = generate_chunk_qa(
                generators.get(chunk_num_questions),
                reasoning_generator,
                chunk,
                chunk_num_questions,
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
            "num_questions": chunk_num_questions,
            "system_prompt_ref": prompt_ref,
            "items": items,
            "run_at": run_at,
            "generator": "structured_output_two_pass",
            "model": model,
        }
        append_jsonl_record(output_path, record)
        append_training_examples(
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
        added_by_count[chunk_num_questions] += 1
        print(f"  saved {len(items)} items -> {ALL_QA_JSONL}, {training_path.name}")

    write_preview(output_dir)
    training_count = len(read_jsonl(training_path)) if training_path.exists() else 0
    print(f"\nInput:    {input_jsonl} ({len(chunks)} chunks)")
    print(f"Model:    {model} (api: {api})")
    if questions_config and questions_config.exists():
        print(f"Config:   {questions_config}")
    print(f"Output:   {output_path}")
    print(f"Training: {training_path} ({training_count} examples)")
    print(f"Added:    {sum(added_by_count.values())} chunks (skipped {skipped} duplicates)")
    for count, chunks_added in sorted(added_by_count.items()):
        print(f"  {count} questions/chunk: {chunks_added} chunks")
    return added_by_count


def write_preview(output_dir: Path) -> int:
    records = read_jsonl(output_dir / ALL_QA_JSONL)
    parts = [f"# Generated Q&A ({len(records)} chunks)\n"]
    for record in records:
        parts.append(f"## {record['chunk_id']} — `{record.get('category', '')}`\n")
        parts.append(f"**Prompt:** `{record.get('system_prompt_ref', 'default')}`  ")
        parts.append(f"**Questions:** {record.get('num_questions', len(record['items']))}\n")
        for idx, item in enumerate(record["items"], start=1):
            parts.append(f"### Q{idx}\n")
            parts.append(f"**Question:** {item['question']}\n")
            parts.append(f"**Answer:** {item['answer']}\n")
            parts.append(f"**Reasoning:** {item['reasoning']}\n")
        parts.append("---\n")
    preview_path = output_dir / "preview.md"
    preview_path.write_text("\n".join(parts), encoding="utf-8")
    return len(records)

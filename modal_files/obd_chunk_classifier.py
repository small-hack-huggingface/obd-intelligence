"""Shared chunk split + LLM classify logic for OBD training corpus."""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from langchain_text_splitters import MarkdownTextSplitter
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data_consideration"
DEFAULT_OUTPUT = ROOT / "classified_chunks"
DEFAULT_BASE_URL = "https://altondsouza02--nemotron-nano-vllm-serve-dev.modal.run"
DEFAULT_MODEL = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16"
INFERENCE_TIMEOUT = 15 * 60
ALL_CHUNKS_JSONL = "all_chunks.jsonl"
# Nemotron is a reasoning model; without a cap it can burn the full 262k context.
CLASSIFY_MAX_TOKENS = 512

CATEGORIES = (
    "automotive_fundamentals",
    "automotive_diagnostics",
    "other_automotive_information",
)

CLASSIFY_SYSTEM = """You classify text chunks for an automotive / OBD-II / Toyota hybrid training corpus.

Pick exactly ONE category:
- automotive_fundamentals — core concepts: PIDs, DTCs, encoding, units, OBD modes, ECU headers, how sensors and buses work, healthy baselines and normal ranges
- automotive_diagnostics — fault finding: fault signatures, DTC meanings, symptom-to-cause reasoning, diagnostic steps, simulation profiles, if/then workflows, multi-signal inference
- other_automotive_information — everything else automotive-related that is not fundamentals or diagnostics (setup, tooling, emulator usage, project architecture, workflows, conversation-style Q&A, misc reference)

Return only the structured fields. Do not reason at length or explain your thinking."""


class ChunkCategory(str, Enum):
    automotive_fundamentals = "automotive_fundamentals"
    automotive_diagnostics = "automotive_diagnostics"
    other_automotive_information = "other_automotive_information"


class ChunkClassification(BaseModel):
    """Structured classification result for one markdown chunk."""

    category: ChunkCategory = Field(description="Exactly one corpus category.")
    reason: str = Field(description="One short sentence explaining the choice.")


def make_llm(base_url: str, model: str = DEFAULT_MODEL) -> ChatOpenAI:
    return ChatOpenAI(
        base_url=f"{base_url.rstrip('/')}/v1",
        api_key="not-needed",
        model=model,
        timeout=INFERENCE_TIMEOUT,
        temperature=0,
        max_tokens=CLASSIFY_MAX_TOKENS,
        extra_body={"chat_template_kwargs": {"enable_thinking": False}},
    )


def make_classifier(base_url: str, model: str = DEFAULT_MODEL) -> Runnable:
    return make_llm(base_url, model).with_structured_output(
        ChunkClassification,
        method="function_calling",
    )


def classify_chunk_llm(
    classifier: Runnable,
    text: str,
    source_file: str,
) -> dict[str, str]:
    result: ChunkClassification = classifier.invoke(
        [
            SystemMessage(content=CLASSIFY_SYSTEM),
            HumanMessage(
                content=f"Source file: {source_file}\n\n---\n{text[:6000]}"
            ),
        ]
    )
    return {"category": result.category.value, "reason": result.reason.strip()}


def chunk_file(path: Path, chunk_size: int, chunk_overlap: int) -> list[str]:
    splitter = MarkdownTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.split_text(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def append_jsonl_record(path: Path, record: dict) -> None:
    """Append one JSONL line and flush so partial runs survive crashes."""
    line = json.dumps(record, ensure_ascii=False) + "\n"
    with path.open("a", encoding="utf-8") as f:
        f.write(line)
        f.flush()


def append_chunk_record(output_dir: Path, record: dict) -> None:
    append_jsonl_record(output_dir / ALL_CHUNKS_JSONL, record)
    append_jsonl_record(output_dir / f"{record['category']}.jsonl", record)


def load_all_records(output_dir: Path) -> list[dict]:
    all_chunks = output_dir / ALL_CHUNKS_JSONL
    if all_chunks.exists():
        return read_jsonl(all_chunks)

    records: list[dict] = []
    for category in CATEGORIES:
        jsonl = output_dir / f"{category}.jsonl"
        if jsonl.exists():
            records.extend(read_jsonl(jsonl))
    records.sort(key=lambda r: (r["source_file"], r["chunk_index"]))
    return records


def write_preview(output_dir: Path) -> int:
    records = load_all_records(output_dir)
    parts = [f"# Chunk preview ({len(records)} chunks)\n"]
    for record in records:
        parts.append(f"## {record['id']}\n")
        parts.append(f"**Category:** `{record['category']}`  ")
        parts.append(f"**Reason:** {record['reason']}\n")
        parts.append(record["text"])
        parts.append("\n---\n")
    preview_path = output_dir / "preview.md"
    preview_path.write_text("\n".join(parts), encoding="utf-8")
    return len(records)


def write_split_preview(
    output_dir: Path,
    chunks_by_file: list[tuple[str, list[str]]],
) -> int:
    total = sum(len(chunks) for _, chunks in chunks_by_file)
    parts = [f"# Split preview ({total} chunks, unclassified)\n"]
    for source_file, chunks in chunks_by_file:
        for idx, text in enumerate(chunks):
            parts.append(f"## {source_file}:{idx}\n")
            parts.append(text.strip())
            parts.append("\n---\n")
    preview_path = output_dir / "split_preview.md"
    preview_path.write_text("\n".join(parts), encoding="utf-8")
    return total


def print_chunk(text: str, *, full: bool = False, preview_chars: int = 400) -> None:
    body = text.strip()
    if full or len(body) <= preview_chars:
        print(body)
        return
    print(body[:preview_chars])
    print(f"... ({len(body) - preview_chars} more chars — see preview.md)")


def load_existing_ids(output_dir: Path) -> set[str]:
    all_chunks = output_dir / ALL_CHUNKS_JSONL
    if all_chunks.exists():
        return {record["id"] for record in read_jsonl(all_chunks)}

    ids: set[str] = set()
    for category in CATEGORIES:
        jsonl = output_dir / f"{category}.jsonl"
        if jsonl.exists():
            ids.update(record["id"] for record in read_jsonl(jsonl))
    return ids


def run_split_only(
    input_dir: Path,
    output_dir: Path,
    *,
    chunk_size: int = 1000,
    chunk_overlap: int = 100,
    show_chunks: bool = True,
    show_full_chunks: bool = False,
) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    md_files = sorted(input_dir.glob("*.md"))
    if not md_files:
        raise SystemExit(f"No .md files in {input_dir}")

    chunks_by_file: list[tuple[str, list[str]]] = []
    total = 0
    for path in md_files:
        chunks = chunk_file(path, chunk_size, chunk_overlap)
        chunks_by_file.append((path.name, chunks))
        total += len(chunks)
        print(f"{path.name}: {len(chunks)} chunks")
        if show_chunks:
            for idx, text in enumerate(chunks):
                print(f"\n--- {path.name}:{idx} ---")
                print_chunk(text, full=show_full_chunks)

    write_split_preview(output_dir, chunks_by_file)
    print(f"\nInput:  {input_dir} ({len(md_files)} files)")
    print(f"Output: {output_dir / 'split_preview.md'} ({total} chunks)")
    return total


def run_pipeline(
    input_dir: Path,
    output_dir: Path,
    base_url: str,
    *,
    fresh: bool = False,
    chunk_size: int = 1000,
    chunk_overlap: int = 100,
    model: str = DEFAULT_MODEL,
    show_chunks: bool = True,
    show_full_chunks: bool = False,
) -> Counter:
    output_dir.mkdir(parents=True, exist_ok=True)

    if fresh:
        for category in CATEGORIES:
            (output_dir / f"{category}.jsonl").unlink(missing_ok=True)
        (output_dir / ALL_CHUNKS_JSONL).unlink(missing_ok=True)
        (output_dir / "preview.md").unlink(missing_ok=True)

    md_files = sorted(input_dir.glob("*.md"))
    if not md_files:
        raise SystemExit(f"No .md files in {input_dir}")

    classifier = make_classifier(base_url, model)
    existing_ids = load_existing_ids(output_dir)
    run_at = datetime.now(timezone.utc).isoformat()
    added: Counter = Counter()
    skipped = 0

    for path in md_files:
        chunks = chunk_file(path, chunk_size, chunk_overlap)
        for idx, text in enumerate(chunks):
            chunk_id = f"{path.name}:{idx}"
            if chunk_id in existing_ids:
                skipped += 1
                continue

            print(f"Classifying {chunk_id}...")
            if show_chunks:
                print(f"\n--- {chunk_id} ---")
                print_chunk(text, full=show_full_chunks)
            result = classify_chunk_llm(classifier, text, path.name)
            record = {
                "id": chunk_id,
                "source_file": path.name,
                "chunk_index": idx,
                "category": result["category"],
                "reason": result["reason"],
                "text": text.strip(),
                "run_at": run_at,
                "classifier": "structured_output",
                "model": model,
            }
            append_chunk_record(output_dir, record)
            existing_ids.add(chunk_id)
            added[result["category"]] += 1
            print(f"  -> {result['category']}: {result['reason']}")
            print(f"  saved -> {ALL_CHUNKS_JSONL}, {result['category']}.jsonl")

    total_new = sum(added.values())
    preview_count = write_preview(output_dir)
    print(f"\nInput:  {input_dir} ({len(md_files)} files)")
    print(f"Output: {output_dir}")
    print(f"Added:  {total_new} chunks (skipped {skipped} duplicates)")
    print(f"JSONL:  {output_dir / ALL_CHUNKS_JSONL} ({preview_count} chunks total)")
    print(f"Preview: {output_dir / 'preview.md'}\n")
    for category in CATEGORIES:
        print(f"  {category:30} +{added[category]:4}  -> {category}.jsonl")
    return added

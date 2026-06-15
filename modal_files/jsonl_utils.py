"""Shared JSONL and chunk-config helpers for QA pipelines."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MAX_QUESTIONS_PER_CHUNK = 20
MAX_TERM_QUESTIONS_PER_CHUNK = 30

CHUNK_QA_TRAINING_DIR = "chunk_qa"
TERM_TRAINING_DIR = "term_clarification"


def model_slug(model: str) -> str:
    """Short stable id for training example keys (e.g. openai/gpt-oss-120b -> gpt-oss-120b)."""
    name = model.rsplit("/", 1)[-1]
    return name.replace(".", "-").lower()


def training_jsonl_path(
    training_dir: Path,
    *,
    example_type: str,
    model: str,
) -> Path:
    """Path for flat training JSONL split by example type and model."""
    if example_type == "chunk_qa":
        subdir = CHUNK_QA_TRAINING_DIR
    elif example_type == "term_clarification":
        subdir = TERM_TRAINING_DIR
    else:
        raise ValueError(f"Unknown example_type: {example_type}")
    return training_dir / subdir / f"{model_slug(model)}.jsonl"


def resolve_chunk_override(
    chunk: dict[str, Any],
    *,
    default: Any,
    by_category: dict[str, Any],
    by_source_file: dict[str, Any],
    by_chunk_id: dict[str, Any],
) -> tuple[Any, str]:
    chunk_id = chunk.get("id", "")
    if chunk_id in by_chunk_id:
        return by_chunk_id[chunk_id], f"by_chunk_id:{chunk_id}"

    source_file = chunk.get("source_file", "")
    if source_file in by_source_file:
        return by_source_file[source_file], f"by_source_file:{source_file}"

    category = chunk.get("category", "")
    if category in by_category:
        return by_category[category], f"by_category:{category}"

    return default, "default"


def load_prompt_text(value: str, config_dir: Path) -> str:
    candidate = config_dir / value
    if candidate.exists():
        return candidate.read_text(encoding="utf-8").strip()
    path = Path(value)
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return value.strip()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def append_jsonl_record(path: Path, record: dict[str, Any]) -> None:
    line = json.dumps(record, ensure_ascii=False) + "\n"
    with path.open("a", encoding="utf-8") as f:
        f.write(line)
        f.flush()


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def merge_jsonl_files(
    paths: list[Path],
    *,
    dedupe_key: str = "id",
    dedupe: bool = True,
) -> tuple[list[dict[str, Any]], int]:
    merged: list[dict[str, Any]] = []
    seen: set[Any] = set()
    skipped = 0
    for path in sorted(paths):
        for record in read_jsonl(path):
            if dedupe and dedupe_key in record:
                key = record[dedupe_key]
                if key in seen:
                    skipped += 1
                    continue
                seen.add(key)
            merged.append(record)
    return merged, skipped


def clear_jsonl_dir(directory: Path) -> None:
    if not directory.exists():
        return
    for path in directory.glob("*.jsonl"):
        path.unlink()


def validate_num_questions(num_questions: int, *, maximum: int = MAX_QUESTIONS_PER_CHUNK) -> int:
    if num_questions < 1:
        raise SystemExit("--num-questions must be at least 1")
    if num_questions > maximum:
        raise SystemExit(f"--num-questions must be at most {maximum}")
    return num_questions


@dataclass
class QuestionsConfig:
    """Per-chunk question counts. Most specific match wins."""

    default: int = 5
    by_category: dict[str, int] = field(default_factory=dict)
    by_source_file: dict[str, int] = field(default_factory=dict)
    by_chunk_id: dict[str, int] = field(default_factory=dict)
    config_dir: Path = field(default_factory=lambda: ROOT / "data_consideration")

    @classmethod
    def load(
        cls,
        path: Path | None,
        *,
        default: int = 5,
        section: str | None = None,
    ) -> QuestionsConfig:
        if path is None or not path.exists():
            return cls(default=default)
        data = json.loads(path.read_text(encoding="utf-8"))
        if section:
            block = data.get(section, {})
            return cls(
                default=block.get("default", default),
                by_category=block.get("by_category", {}),
                by_source_file=block.get("by_source_file", {}),
                by_chunk_id=block.get("by_chunk_id", {}),
                config_dir=path.parent,
            )
        return cls(
            default=data.get("default", default),
            by_category=data.get("by_category", {}),
            by_source_file=data.get("by_source_file", {}),
            by_chunk_id=data.get("by_chunk_id", {}),
            config_dir=path.parent,
        )

    def resolve(self, chunk: dict[str, Any]) -> int:
        value, _ = resolve_chunk_override(
            chunk,
            default=self.default,
            by_category=self.by_category,
            by_source_file=self.by_source_file,
            by_chunk_id=self.by_chunk_id,
        )
        return int(value)


@dataclass
class PromptsConfig:
    """Per-chunk system prompts. Values are inline text or paths to .md files."""

    default: str
    by_category: dict[str, str] = field(default_factory=dict)
    by_source_file: dict[str, str] = field(default_factory=dict)
    by_chunk_id: dict[str, str] = field(default_factory=dict)
    config_dir: Path = field(default_factory=lambda: ROOT / "data_consideration")

    @classmethod
    def from_config(
        cls,
        path: Path | None,
        *,
        section: str = "system_prompts",
        fallback_default: str,
    ) -> PromptsConfig:
        if path is None or not path.exists():
            return cls(default=fallback_default)
        data = json.loads(path.read_text(encoding="utf-8"))
        block = data.get(section, {})
        return cls(
            default=block.get("default", fallback_default),
            by_category=block.get("by_category", {}),
            by_source_file=block.get("by_source_file", {}),
            by_chunk_id=block.get("by_chunk_id", {}),
            config_dir=path.parent,
        )

    def resolve(self, chunk: dict[str, Any]) -> tuple[str, str]:
        raw, ref = resolve_chunk_override(
            chunk,
            default=self.default,
            by_category=self.by_category,
            by_source_file=self.by_source_file,
            by_chunk_id=self.by_chunk_id,
        )
        return load_prompt_text(str(raw), self.config_dir), ref

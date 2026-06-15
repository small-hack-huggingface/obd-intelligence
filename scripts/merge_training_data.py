"""Merge training JSONL files into a single flat file.

  python scripts/merge_training_data.py
  python scripts/merge_training_data.py --models gpt-oss-120b
  python scripts/merge_training_data.py --output training_data/all_merged.jsonl
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "modal_files"))

from jsonl_utils import (  # noqa: E402
    CHUNK_QA_TRAINING_DIR,
    TERM_TRAINING_DIR,
    merge_jsonl_files,
    read_jsonl,
    write_jsonl,
)
from qa_generator import DEFAULT_TRAINING_DIR  # noqa: E402

DEFAULT_TYPES = (CHUNK_QA_TRAINING_DIR, TERM_TRAINING_DIR)
DEFAULT_OUTPUT = DEFAULT_TRAINING_DIR / "all_merged.jsonl"


def collect_input_paths(
    training_dir: Path,
    *,
    types: list[str],
    models: list[str] | None,
) -> list[Path]:
    paths: list[Path] = []
    for subdir in types:
        type_dir = training_dir / subdir
        if not type_dir.is_dir():
            continue
        for path in sorted(type_dir.glob("*.jsonl")):
            if models and not any(m in path.stem for m in models):
                continue
            paths.append(path)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge chunk_qa and term_clarification training JSONL into one file."
    )
    parser.add_argument(
        "--training-dir",
        type=Path,
        default=DEFAULT_TRAINING_DIR,
        help="Root training directory (contains chunk_qa/ and term_clarification/)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Merged output JSONL path",
    )
    parser.add_argument(
        "--types",
        nargs="+",
        default=list(DEFAULT_TYPES),
        choices=[CHUNK_QA_TRAINING_DIR, TERM_TRAINING_DIR],
        help="Subdirectories to merge",
    )
    parser.add_argument(
        "--models",
        nargs="*",
        default=None,
        help="Optional model slug filter (substring match on filename stem)",
    )
    parser.add_argument(
        "--no-dedupe",
        action="store_true",
        help="Do not skip duplicate record ids",
    )
    args = parser.parse_args()

    paths = collect_input_paths(
        args.training_dir,
        types=args.types,
        models=args.models,
    )
    if not paths:
        raise SystemExit(f"No JSONL files found under {args.training_dir}")

    merged, skipped = merge_jsonl_files(paths, dedupe=not args.no_dedupe)
    write_jsonl(args.output, merged)

    print(f"Merged {len(paths)} files -> {args.output}")
    for path in paths:
        rel = path.relative_to(args.training_dir)
        print(f"  {rel}: {len(read_jsonl(path))}")
    dup_note = f" (skipped {skipped} duplicates)" if skipped else ""
    print(f"Total: {len(merged)}{dup_note}")


if __name__ == "__main__":
    main()

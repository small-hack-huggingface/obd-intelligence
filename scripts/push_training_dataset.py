# /// script
# dependencies = [
#   "datasets>=3.6.0",
#   "huggingface_hub>=0.34.0",
#   "python-dotenv>=1.0.0",
# ]
# ///
"""Push OBD training JSONL to Hugging Face Datasets for Modal finetuning.

  python scripts/merge_training_data.py
  python scripts/push_training_dataset.py

Requires HF_TOKEN in .env or the environment (or huggingface-cli login).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "modal_files"))

from jsonl_utils import read_jsonl  # noqa: E402
from qa_generator import DEFAULT_TRAINING_DIR  # noqa: E402
from training_format import prepare_sft_record  # noqa: E402

DEFAULT_INPUT = DEFAULT_TRAINING_DIR / "all_merged.jsonl"
DEFAULT_DATASET_REPO = "build-small-hackathon/nemotron-car-diagnostics-datasets"

load_dotenv(ROOT / ".env")

def build_dataset_rows(records: list[dict]) -> list[dict]:
    rows: list[dict] = []
    skipped = 0
    for record in records:
        row = prepare_sft_record(record)
        if row is None:
            skipped += 1
            continue
        rows.append(row)
    if not rows:
        raise SystemExit("No valid training rows (need question, answer, reasoning).")
    print(f"Prepared {len(rows)} rows ({skipped} skipped)")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Upload Nemotron SFT training data to Hugging Face Datasets."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Source JSONL (default: training_data/all_merged.jsonl)",
    )
    parser.add_argument(
        "--repo",
        default=os.environ.get("HF_DATASET_REPO", DEFAULT_DATASET_REPO),
        help=f"HF dataset repo id (default: {DEFAULT_DATASET_REPO}, or set HF_DATASET_REPO)",
    )
    parser.add_argument(
        "--public",
        action="store_true",
        help="Upload as a public dataset (default: private)",
    )
    parser.add_argument(
        "--commit-message",
        default="Update OBD Nemotron SFT training data",
        help="Hub commit message",
    )
    args = parser.parse_args()

    if not args.input.exists():
        raise SystemExit(f"Input not found: {args.input}")

    token = os.environ.get("HF_TOKEN")
    if not token:
        raise SystemExit(
            "HF_TOKEN is not set. Add HF_TOKEN=... to .env or export it / run huggingface-cli login."
        )

    from datasets import Dataset

    records = read_jsonl(args.input)
    rows = build_dataset_rows(records)
    dataset = Dataset.from_list(rows)

    private = not args.public
    print(f"Uploading {len(dataset)} examples -> {args.repo} (private={private})")
    dataset.push_to_hub(
        args.repo,
        private=private,
        token=token,
        commit_message=args.commit_message,
    )
    print(f"Done: https://huggingface.co/datasets/{args.repo}")


if __name__ == "__main__":
    main()

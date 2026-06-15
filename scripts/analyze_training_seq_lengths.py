"""Measure token lengths in training JSONL for max_seq_length selection.

  python scripts/analyze_training_seq_lengths.py
  python scripts/analyze_training_seq_lengths.py --dataset training_data/all_merged.jsonl
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "modal_files"))

from jsonl_utils import read_jsonl  # noqa: E402
from qa_generator import DEFAULT_TRAINING_DIR  # noqa: E402
from training_format import build_nemotron_messages  # noqa: E402

DEFAULT_MODEL = "unsloth/NVIDIA-Nemotron-3-Nano-4B"
DEFAULT_DATASET = DEFAULT_TRAINING_DIR / "all_merged.jsonl"
CANDIDATE_LENGTHS = (2048, 4096, 8192)
TRUNCATION_THRESHOLD = 0.005  # 0.5%


def percentile(values: list[int], pct: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    idx = int(len(ordered) * pct)
    idx = min(idx, len(ordered) - 1)
    return ordered[idx]


def token_length(tokenizer, messages: list[dict]) -> int:
    encoded = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=False,
        enable_thinking=False,
    )
    if isinstance(encoded, list):
        return len(encoded)
    return len(encoded["input_ids"])


def load_tokenizer(model_name: str):
    try:
        from transformers import AutoTokenizer

        return AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True,
            token=os.environ.get("HF_TOKEN"),
        )
    except Exception as exc:
        raise SystemExit(
            f"Failed to load tokenizer for {model_name!r}: {exc}\n"
            "Install transformers and ensure the model is reachable on Hugging Face. "
            "Set HF_TOKEN in .env if the model is gated."
        ) from exc


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze token lengths in training JSONL for LoRA max_seq_length."
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET,
        help="Training JSONL with messages field",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="Tokenizer model id (default: unsloth/NVIDIA-Nemotron-3-Nano-4B)",
    )
    args = parser.parse_args()

    if not args.dataset.exists():
        raise SystemExit(f"Dataset not found: {args.dataset}")

    records = read_jsonl(args.dataset)
    if not records:
        raise SystemExit(f"No records in {args.dataset}")

    print(f"Loading tokenizer: {args.model}")
    tokenizer = load_tokenizer(args.model)

    sample = build_nemotron_messages(records[0])
    sample_text = tokenizer.apply_chat_template(
        sample,
        tokenize=False,
        add_generation_prompt=False,
        enable_thinking=False,
    )
    sample_len = token_length(tokenizer, sample)
    print(f"\nSample (first record) token length: {sample_len}")
    preview = sample_text[:400].encode("ascii", errors="replace").decode("ascii")
    print(f"Sample text preview ({len(sample_text)} chars):\n{preview}\n...")

    lengths: list[int] = []
    skipped = 0
    for record in records:
        if not all(record.get(k) for k in ("question", "answer", "reasoning")):
            skipped += 1
            continue
        try:
            messages = build_nemotron_messages(record)
            lengths.append(token_length(tokenizer, messages))
        except Exception as exc:
            skipped += 1
            print(f"  skip {record.get('id', '?')}: {exc}")
            continue

    if not lengths:
        raise SystemExit("No valid records with tokenizable messages.")

    if max(lengths) < 50:
        raise SystemExit(
            f"Token lengths look wrong (max={max(lengths)}). "
            "Check tokenizer / chat template output."
        )

    print(f"\nDataset: {args.dataset}")
    print(f"Records: {len(records)}  tokenized: {len(lengths)}  skipped: {skipped}")
    print(
        f"Token lengths — min: {min(lengths)}  "
        f"p50: {percentile(lengths, 0.50)}  "
        f"p90: {percentile(lengths, 0.90)}  "
        f"p95: {percentile(lengths, 0.95)}  "
        f"p99: {percentile(lengths, 0.99)}  "
        f"max: {max(lengths)}"
    )

    print("\nTruncation at candidate max_seq_length:")
    n = len(lengths)
    for candidate in CANDIDATE_LENGTHS:
        truncated = sum(1 for length in lengths if length > candidate)
        pct = truncated / n
        print(f"  {candidate:>5}: {truncated:>5} examples ({pct * 100:.2f}%)")

    suggested = CANDIDATE_LENGTHS[-1]
    for candidate in CANDIDATE_LENGTHS:
        truncated = sum(1 for length in lengths if length > candidate)
        if truncated / n < TRUNCATION_THRESHOLD:
            suggested = candidate
            break

    print(f"\nSuggested max_seq_length: {suggested}")


if __name__ == "__main__":
    main()

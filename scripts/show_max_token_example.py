"""Print tokenization details for the longest training example.

  python scripts/show_max_token_example.py
"""

from __future__ import annotations

import json
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

DEFAULT_DATASET = DEFAULT_TRAINING_DIR / "all_merged.jsonl"
DEFAULT_MODEL = "unsloth/NVIDIA-Nemotron-3-Nano-4B"


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


def main() -> None:
    from transformers import AutoTokenizer

    records = read_jsonl(DEFAULT_DATASET)
    tokenizer = AutoTokenizer.from_pretrained(
        DEFAULT_MODEL,
        trust_remote_code=True,
        token=os.environ.get("HF_TOKEN"),
    )

    best_record = None
    best_messages = None
    best_len = 0
    for record in records:
        if not all(record.get(k) for k in ("question", "answer", "reasoning")):
            continue
        messages = build_nemotron_messages(record)
        length = token_length(tokenizer, messages)
        if length > best_len:
            best_len = length
            best_record = record
            best_messages = messages

    if not best_record or not best_messages:
        raise SystemExit("No records found.")

    text = tokenizer.apply_chat_template(
        best_messages,
        tokenize=False,
        add_generation_prompt=False,
        enable_thinking=False,
    )
    ids = tokenizer.apply_chat_template(
        best_messages,
        tokenize=True,
        add_generation_prompt=False,
        enable_thinking=False,
    )["input_ids"]

    print(f"id: {best_record.get('id')}")
    print(f"example_type: {best_record.get('example_type')}")
    print(f"token_count: {best_len}")
    print(f"question chars: {len(best_record['question'])}")
    print(f"answer chars: {len(best_record['answer'])}")
    print(f"reasoning chars: {len(best_record['reasoning'])}")
    print(f"formatted text chars: {len(text)}")
    print()
    print("=== MESSAGES (logical input) ===")
    print(json.dumps(best_messages, indent=2, ensure_ascii=False))
    print()
    print("=== FORMATTED TEXT (chat template) ===")
    print(text)
    print()
    print(f"=== FIRST 50 TOKEN IDS ({len(ids[:50])}) ===")
    print(ids[:50])
    print()
    print(f"=== LAST 30 TOKEN IDS ===")
    print(ids[-30:])
    print()
    print("=== DECODED (first 120 tokens) ===")
    print(tokenizer.decode(ids[:120]))
    print()
    print("=== DECODED (last 80 tokens) ===")
    print(tokenizer.decode(ids[-80:]))


if __name__ == "__main__":
    main()

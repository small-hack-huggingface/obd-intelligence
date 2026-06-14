"""Classify markdown chunks with ChatOpenAI (Nemotron on Modal).

  modal run modal_files/classify_chunks.py
  python scripts/classify_chunks.py --fresh

Reads *.md from data_consideration/ by default.
Writes JSONL to classified_chunks/ by default.
"""

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from modal_files.obd_chunk_classifier import (
    DEFAULT_BASE_URL,
    DEFAULT_INPUT,
    DEFAULT_OUTPUT,
    run_pipeline,
    run_split_only,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Split markdown, classify chunks with ChatOpenAI, append to category JSONL."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--base-url",
        default=os.getenv("VLLM_BASE_URL", DEFAULT_BASE_URL),
        help="OpenAI-compatible vLLM base URL (no /v1 suffix)",
    )
    parser.add_argument("--chunk-size", type=int, default=1000)
    parser.add_argument("--chunk-overlap", type=int, default=100)
    parser.add_argument("--fresh", action="store_true")
    parser.add_argument(
        "--split-only",
        action="store_true",
        help="Split markdown and write split_preview.md without calling the LLM",
    )
    parser.add_argument(
        "--no-show-chunks",
        action="store_true",
        help="Hide chunk text in the terminal",
    )
    parser.add_argument(
        "--show-full-chunks",
        action="store_true",
        help="Print full chunk text in the terminal (default is 400-char preview)",
    )
    args = parser.parse_args()

    show_chunks = not args.no_show_chunks
    if args.split_only:
        run_split_only(
            args.input,
            args.output,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            show_chunks=show_chunks,
            show_full_chunks=args.show_full_chunks,
        )
        return

    run_pipeline(
        args.input,
        args.output,
        args.base_url,
        fresh=args.fresh,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        show_chunks=show_chunks,
        show_full_chunks=args.show_full_chunks,
    )


if __name__ == "__main__":
    main()

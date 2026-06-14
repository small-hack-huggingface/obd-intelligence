"""Classify data_consideration markdown chunks via Nemotron (ChatOpenAI).

  modal run modal_files/classify_chunks.py
  modal run modal_files/classify_chunks.py --fresh
  python scripts/classify_chunks.py --fresh

Reads *.md from data_consideration/ (override with --input-dir / --input).
Writes JSONL to classified_chunks/ (override with --output-dir / --output).
"""

import asyncio
import sys
from pathlib import Path

import modal

app = modal.App("classify-chunks")

serve = modal.Function.from_name("nemotron-nano-vllm", "serve")

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from obd_chunk_classifier import (  # noqa: E402
    DEFAULT_INPUT,
    DEFAULT_OUTPUT,
    DEFAULT_BASE_URL,
    run_pipeline,
    run_split_only,
)


@app.local_entrypoint()
def main(
    input_dir: str = str(DEFAULT_INPUT),
    output_dir: str = str(DEFAULT_OUTPUT),
    fresh: bool = False,
    chunk_size: int = 1000,
    chunk_overlap: int = 100,
    split_only: bool = False,
    no_show_chunks: bool = False,
    show_full_chunks: bool = False,
):
    show_chunks = not no_show_chunks
    if split_only:
        run_split_only(
            Path(input_dir),
            Path(output_dir),
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            show_chunks=show_chunks,
            show_full_chunks=show_full_chunks,
        )
        return

    url = asyncio.run(serve.get_web_url.aio())
    print(f"LLM: {url}")
    run_pipeline(
        Path(input_dir),
        Path(output_dir),
        url,
        fresh=fresh,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        show_chunks=show_chunks,
        show_full_chunks=show_full_chunks,
    )


if __name__ == "__main__":
    try:
        run_pipeline(DEFAULT_INPUT, DEFAULT_OUTPUT, DEFAULT_BASE_URL)
    except Exception as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        sys.exit(1)

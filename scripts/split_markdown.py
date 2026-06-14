"""Split a markdown file with LangChain's MarkdownTextSplitter.

  pip install langchain-text-splitters
  python scripts/split_markdown.py docs/fault_simulation.md
"""

import argparse
from pathlib import Path

from langchain_text_splitters import MarkdownTextSplitter


def main() -> None:
    parser = argparse.ArgumentParser(description="Split a markdown file into chunks.")
    parser.add_argument("path", type=Path, help="Path to the .md file")
    parser.add_argument("--chunk-size", type=int, default=1000)
    parser.add_argument("--chunk-overlap", type=int, default=100)
    args = parser.parse_args()

    text = args.path.read_text(encoding="utf-8")
    splitter = MarkdownTextSplitter(
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )
    chunks = splitter.split_text(text)

    print(f"{args.path}: {len(chunks)} chunks\n")
    for i, chunk in enumerate(chunks, start=1):
        print(f"--- chunk {i} ---")
        print(chunk)
        print()


if __name__ == "__main__":
    main()

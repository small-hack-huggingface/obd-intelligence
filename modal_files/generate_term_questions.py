"""Generate term-clarification Q&A from classified chunks via Nemotron (Modal).

  modal run modal_files/generate_term_questions.py --fresh
  modal run modal_files/generate_term_questions.py --limit 2

Reads classified_chunks/all_chunks.jsonl by default.
Uses data_consideration/questions_config.json term_questions for counts and term_system_prompts.
Appends to training_data/all_examples.jsonl with example_type term_clarification.
"""

import asyncio
import sys
from pathlib import Path

import modal

app = modal.App("generate-term-questions")

serve = modal.Function.from_name("nemotron-nano-vllm", "serve")

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from qa_generator import DEFAULT_INPUT, DEFAULT_QUESTIONS_CONFIG, DEFAULT_TRAINING_DIR  # noqa: E402
from term_qa_generator import DEFAULT_OUTPUT, run_pipeline  # noqa: E402


@app.local_entrypoint()
def main(
    input_jsonl: str = str(DEFAULT_INPUT),
    output_dir: str = str(DEFAULT_OUTPUT),
    training_dir: str = str(DEFAULT_TRAINING_DIR),
    num_questions: int = 10,
    questions_config: str = str(DEFAULT_QUESTIONS_CONFIG),
    fresh: bool = False,
    limit: int | None = None,
):
    url = asyncio.run(serve.get_web_url.aio())
    print(f"LLM: {url}")
    config_path = Path(questions_config) if questions_config else None
    if config_path and config_path.exists():
        print(f"Config: {config_path}")
    else:
        print(f"Default items per chunk: {num_questions}")
    run_pipeline(
        Path(input_jsonl),
        Path(output_dir),
        url,
        training_dir=Path(training_dir),
        num_questions=num_questions,
        questions_config=config_path,
        fresh=fresh,
        limit=limit,
    )

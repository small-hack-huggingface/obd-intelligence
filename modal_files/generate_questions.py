"""Generate Q&A + reasoning from classified chunks via Modal vLLM.

  modal run modal_files/generate_questions.py
  modal run modal_files/generate_questions.py --llm gpt-oss --limit 2
  modal run modal_files/generate_questions.py --num-questions 10 --fresh

Reads classified_chunks/all_chunks.jsonl by default.
Question counts and system prompts: data_consideration/questions_config.json
Writes incrementally to generated_qa/all_qa.jsonl and training_data/chunk_qa/{model}.jsonl.
Pass 2 reasoning uses data_consideration/prompts/verbose_reasoning.md (shared with term pipeline).
"""

import sys
from pathlib import Path

import modal

app = modal.App("generate-questions")

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from llm_profiles import DEFAULT_LLM_KEY, resolve_profile  # noqa: E402
from modal_llm_url import get_serve_url_sync  # noqa: E402
from qa_generator import (  # noqa: E402
    DEFAULT_INPUT,
    DEFAULT_OUTPUT,
    DEFAULT_QUESTIONS_CONFIG,
    DEFAULT_TRAINING_DIR,
    run_pipeline,
)


@app.local_entrypoint()
def main(
    input_jsonl: str = str(DEFAULT_INPUT),
    output_dir: str = str(DEFAULT_OUTPUT),
    training_dir: str = str(DEFAULT_TRAINING_DIR),
    num_questions: int = 5,
    questions_config: str = str(DEFAULT_QUESTIONS_CONFIG),
    fresh: bool = False,
    limit: int | None = None,
    llm: str = DEFAULT_LLM_KEY,
):
    profile = resolve_profile(llm)
    url = get_serve_url_sync(profile)
    print(f"LLM profile: {profile.key}")
    print(f"LLM URL: {url}")
    config_path = Path(questions_config) if questions_config else None
    if config_path and config_path.exists():
        print(f"Questions config: {config_path}")
    else:
        print(f"Default questions per chunk: {num_questions}")
    run_pipeline(
        Path(input_jsonl),
        Path(output_dir),
        url,
        training_dir=Path(training_dir),
        num_questions=num_questions,
        questions_config=config_path,
        fresh=fresh,
        limit=limit,
        model=profile.hf_model,
        api_model=profile.api_model,
        extra_body=profile.extra_body,
    )

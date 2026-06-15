"""Generate Q&A from classified chunks (local CLI, same as Modal entrypoint).

  modal run modal_files/generate_questions.py --llm gpt-oss
  python scripts/generate_questions.py --llm gpt-oss --limit 1
"""

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "modal_files"))

from llm_profiles import DEFAULT_LLM_KEY, resolve_profile  # noqa: E402
from qa_generator import (  # noqa: E402
    DEFAULT_INPUT,
    DEFAULT_OUTPUT,
    DEFAULT_QUESTIONS_CONFIG,
    DEFAULT_TRAINING_DIR,
    run_pipeline,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Q&A + reasoning from classified chunk JSONL."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--training-dir",
        type=Path,
        default=DEFAULT_TRAINING_DIR,
        help="Flat JSONL training examples (one line per question)",
    )
    parser.add_argument(
        "--num-questions",
        type=int,
        default=5,
        help="Default questions per chunk when no config match (1-20)",
    )
    parser.add_argument(
        "--questions-config",
        type=Path,
        default=DEFAULT_QUESTIONS_CONFIG,
        help="JSON file with per-chunk/category/source question counts",
    )
    parser.add_argument(
        "--llm",
        choices=["nemotron", "gpt-oss"],
        default=os.getenv("LLM_PROFILE", DEFAULT_LLM_KEY),
        help="LLM profile (sets default base URL, model, and request body)",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="OpenAI-compatible vLLM base URL (no /v1 suffix); overrides profile default",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="HuggingFace model id stored in output JSONL; overrides profile",
    )
    parser.add_argument(
        "--api-model",
        default=None,
        help="Model name sent to vLLM API; overrides profile",
    )
    parser.add_argument("--fresh", action="store_true")
    parser.add_argument("--limit", type=int, default=None, help="Process only first N chunks")
    args = parser.parse_args()

    profile = resolve_profile(args.llm)
    base_url = args.base_url or os.getenv("VLLM_BASE_URL", profile.default_base_url)
    hf_model = args.model or profile.hf_model
    api_model = args.api_model or profile.api_model

    run_pipeline(
        args.input,
        args.output,
        base_url,
        training_dir=args.training_dir,
        num_questions=args.num_questions,
        questions_config=args.questions_config,
        fresh=args.fresh,
        limit=args.limit,
        model=hf_model,
        api_model=api_model,
        extra_body=profile.extra_body,
    )


if __name__ == "__main__":
    main()

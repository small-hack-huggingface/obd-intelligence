"""Create/update the Pocket Mechanic Space from space_hub/.

    .venv/bin/python deploy_space.py [--hardware t4-small] [--public]
"""
import argparse
import os
from pathlib import Path

from huggingface_hub import HfApi

SPACE = "MindFreakGamer/pocket-mechanic"


def load_env():
    for line in Path(".env").read_text().splitlines():
        if line.strip() and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hardware", default=None, help="e.g. cpu-upgrade, t4-small")
    ap.add_argument("--public", action="store_true")
    args = ap.parse_args()

    load_env()
    api = HfApi()
    api.create_repo(SPACE, repo_type="space", space_sdk="gradio",
                    private=not args.public, exist_ok=True)
    api.add_space_secret(SPACE, "HF_TOKEN", os.environ["HF_TOKEN"])
    api.upload_folder(folder_path="space_hub", repo_id=SPACE, repo_type="space")
    if args.hardware:
        api.request_space_hardware(SPACE, args.hardware)
    print(f"deployed -> https://huggingface.co/spaces/{SPACE}"
          f" ({'public' if args.public else 'private'}"
          f"{', ' + args.hardware if args.hardware else ''})")


if __name__ == "__main__":
    main()

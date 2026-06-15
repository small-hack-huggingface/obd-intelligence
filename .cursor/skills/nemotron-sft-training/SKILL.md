---
name: nemotron-sft-training
description: >-
  OBD Nemotron 4B LoRA training pipeline for small-hack: conda env, merge
  training JSONL, push to Hugging Face Datasets, analyze max_seq_length, and
  Modal Unsloth finetune. Use when merging training data, pushing datasets,
  sequence length stats, finetuning, or activating small-hack-1 on Windows.
---

# Nemotron SFT training (small-hack)

## Environment (Windows)

Conda env: **`small-hack-1`**

```powershell
& C:\Users\dsouz\miniconda3\shell\condabin\conda-hook.ps1
conda activate small-hack-1
```

Without activating, use env Python directly:

```powershell
C:\Users\dsouz\miniconda3\envs\small-hack-1\python.exe scripts/<script>.py
```

Repo root: `C:\Users\dsouz\small-hack`

## Training message format

Built in [modal_files/training_format.py](../../../modal_files/training_format.py):

- **User:** `question` only
- **Assistant:** `<think>{reasoning}</think>{answer}`
- **Tokenize with:** `enable_thinking=False` (thinking tags are already in the label)

Applied at **Hub push** via `prepare_sft_record()` — not rewritten during merge.

## Pipeline (in order)

### 1. Merge local JSONL

```powershell
python scripts/merge_training_data.py
python scripts/merge_training_data.py --models nemotron
python scripts/merge_training_data.py --models gpt-oss-120b
python scripts/merge_training_data.py --types chunk_qa
```

| Flag | Default | Purpose |
|------|---------|---------|
| `--training-dir` | `training_data/` | Root with `chunk_qa/` and `term_clarification/` |
| `--output` | `training_data/all_merged.jsonl` | Overwrites merged file |
| `--types` | `chunk_qa term_clarification` | Subdirs to include |
| `--models` | all | Substring filter on filename stem |
| `--no-dedupe` | off | Keep duplicate `id`s |

Merge copies source rows as-is; it does **not** reformat `messages`.

### 2. Analyze sequence lengths (before training)

```powershell
pip install transformers python-dotenv
python scripts/analyze_training_seq_lengths.py
```

Uses Nemotron tokenizer + `build_nemotron_messages()`. Counts `len(token_ids["input_ids"])` — not `len(dict)` (dict has 2 keys and gives bogus length 2).

Sanity: expect p50 ~300, p99 ~650, max ~6200. Default finetune **`max_seq_length=8192`** for zero truncation on L40S/H200.

### 3. Push to Hugging Face

Requires `HF_TOKEN` in repo-root `.env` or the environment.

```powershell
pip install "datasets>=3.6.0" "huggingface_hub>=0.34.0" python-dotenv
python scripts/push_training_dataset.py
```

| Flag | Default | Purpose |
|------|---------|---------|
| `--repo` | `build-small-hackathon/nemotron-car-diagnostics-datasets` | Hub dataset id |
| `--input` | `training_data/all_merged.jsonl` | Source JSONL |
| `--public` | off (private) | Public dataset |
| `--commit-message` | update message | Hub commit |

Upload rows include `messages` column (Nemotron format).

### 4. Finetune on Modal

Requires Modal secret **`huggingface-secret`** with `HF_TOKEN` (private datasets + model download).

```powershell
# Smoke test
modal run modal_files/finetune_nemotron.py --max-steps 1 --skip-eval

# Full run + push LoRA + GGUF to Hub
modal run modal_files/finetune_nemotron.py --experiment-name obd-v1 --num-train-epochs 2 --push-all-hub
```

| `--no-gguf` | off | Skip local GGUF export (Hub push still runs with `--push-all-hub`) |
| `--gguf-quantizations` | `q4_k_m,q8_0` | Comma-separated GGUF methods |

| Flag | Default | Notes |
|------|---------|-------|
| `--dataset-repo` | `build-small-hackathon/nemotron-car-diagnostics-datasets` | Hub `split="train"`, `messages` column |
| `--max-seq-length` | `8192` | Zero truncation on current data; lower if OOM |
| `--num-train-epochs` | `2` | Use when `max-steps` is `-1` |
| `--max-steps` | `-1` | `1` for smoke test |
| `--eval-steps` | `100` | Eval + checkpoint interval when eval enabled |
| `--save-steps` | `100` | Used only with `--skip-eval` |
| `--skip-eval` | off | Skip 90/10 eval split; no best-model selection |
| `--experiment-name` | timestamped | Fixed name enables resume |
| `--push-hub` / `--hub-repo` | off / `build-small-hackathon/nemotron-car-diagnostics-lora` | Push LoRA adapter |
| `--push-all-hub` | off | Push LoRA + GGUF `q4_k_m` & `q8_0` to default Hub repos |
| `--push-gguf-hub` / `--gguf-hub-repo` | off / `build-small-hackathon/nemotron-car-diagnostics-gguf` | Push GGUF only |

**GGUF:** After training, saves merged quantized models to `.../gguf/{experiment}-{method}/` on volume `unsloth-checkpoints`. Download:

```powershell
modal volume get unsloth-checkpoints experiments/nemotron-car-dx-v1/gguf ./nemotron-gguf
```

**Checkpoints:** Modal volume `unsloth-checkpoints` → `/checkpoints/experiments/{name}/`. With eval (default): keeps **one** step checkpoint (`save_total_limit=1`), reloads **lowest eval_loss** at end, saves `best_model/`. With `--skip-eval`: saves `final_model/` only.

**Resume:** Re-run with same `--experiment-name`; picks latest `checkpoint-*`.

**Image deps:** `unsloth[cu128-torch270]` (2026.x) pulls **transformers 5.x** — required for Nemotron’s `TokenizersBackend` tokenizer. Mamba blocks need `mamba-ssm` on `nvidia/cuda:12.8.1-devel`.

## Key files

| File | Role |
|------|------|
| [scripts/merge_training_data.py](../../../scripts/merge_training_data.py) | Merge JSONL |
| [scripts/push_training_dataset.py](../../../scripts/push_training_dataset.py) | Push to Hub |
| [scripts/analyze_training_seq_lengths.py](../../../scripts/analyze_training_seq_lengths.py) | Token stats |
| [modal_files/finetune_nemotron.py](../../../modal_files/finetune_nemotron.py) | Modal Unsloth LoRA |
| [modal_files/training_format.py](../../../modal_files/training_format.py) | Message formatting |

## Agent notes

- Run merge → (optional analyze) → push → modal finetune.
- Do not add local JSONL / dataset_path paths to finetune — Hub only.
- For push script deps without conda: `uv run scripts/push_training_dataset.py --repo ...`

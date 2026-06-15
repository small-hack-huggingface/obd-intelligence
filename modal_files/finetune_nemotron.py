# Modal Unsloth LoRA fine-tune for NVIDIA-Nemotron-3-Nano-4B on OBD training data.
#
#   python scripts/merge_training_data.py
#   python scripts/push_training_dataset.py
#   modal run modal_files/finetune_nemotron.py --max-steps 1 --skip-eval
#   modal run modal_files/finetune_nemotron.py --num-train-epochs 2

from __future__ import annotations

import os
import pathlib
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import modal

app = modal.App("finetune-nemotron")

train_image = (
    modal.Image.from_registry(
        "nvidia/cuda:12.8.1-devel-ubuntu22.04",
        add_python="3.11",
    )
    .entrypoint([])
    .uv_pip_install(
        "datasets==3.6.0",
        "hf-transfer==0.1.9",
        "huggingface_hub>=0.34.0",
        "unsloth[cu128-torch270]==2026.6.3",
        "wandb==0.21.0",
        # Required by unsloth_zoo GGUF converter (runtime uv install fails on Modal).
        "gguf>=0.10.0",
        "protobuf>=4.0.0",
        "sentencepiece>=0.2.0",
    )
    # Nemotron Mamba blocks import mamba_ssm at load time (required, not optional).
    # causal-conv1d + mamba-ssm compile CUDA extensions — needs nvcc (devel image).
    .run_commands(
        "pip install --no-build-isolation causal-conv1d==1.5.2 mamba-ssm==2.2.5",
    )
    .apt_install(
        "git",
        "cmake",
        "build-essential",
        "curl",
        "libcurl4-openssl-dev",
        "pciutils",
    )
    # Unsloth save_pretrained_gguf looks for ./llama.cpp in the working directory.
    .run_commands(
        "git clone --depth 1 https://github.com/ggml-org/llama.cpp /opt/llama.cpp",
        "cmake /opt/llama.cpp -B /opt/llama.cpp/build "
        "-DBUILD_SHARED_LIBS=OFF -DGGML_CUDA=ON -DLLAMA_CURL=OFF",
        "cmake --build /opt/llama.cpp/build --config Release -j "
        "--target llama-quantize llama-cli llama-gguf-split",
        "cp /opt/llama.cpp/build/bin/llama-* /opt/llama.cpp/",
        "mkdir -p /root/.unsloth",
        "ln -sfn /opt/llama.cpp /root/.unsloth/llama.cpp",
    )
    .env({"HF_HOME": "/model_cache", "LLAMA_CPP_PATH": "/root/.unsloth/llama.cpp"})
)

with train_image.imports():
    import unsloth  # noqa: F401
    import datasets
    import torch
    import wandb
    from trl import SFTConfig, SFTTrainer
    from unsloth import FastLanguageModel
    from unsloth.chat_templates import train_on_responses_only

model_cache_volume = modal.Volume.from_name("huggingface-cache", create_if_missing=True)
dataset_cache_volume = modal.Volume.from_name("unsloth-dataset-cache", create_if_missing=True)
checkpoint_volume = modal.Volume.from_name("unsloth-checkpoints", create_if_missing=True)

GPU_TYPE = "L40S"
TIMEOUT_HOURS = 8
MAX_RETRIES = 3

DEFAULT_MODEL = "unsloth/NVIDIA-Nemotron-3-Nano-4B"
DEFAULT_DATASET_REPO = "build-small-hackathon/nemotron-car-diagnostics-datasets"
DEFAULT_HUB_REPO = "build-small-hackathon/nemotron-car-diagnostics-lora"
DEFAULT_GGUF_HUB_REPO = "build-small-hackathon/nemotron-car-diagnostics-gguf"
LLAMA_CPP_PATH = "/root/.unsloth/llama.cpp"
DEFAULT_GGUF_QUANTIZATIONS = ("q4_k_m", "q8_0")
TEXT_COLUMN = "text"
TRAIN_SPLIT_RATIO = 0.9
PREPROCESSING_WORKERS = 2

LORA_TARGET_MODULES = [
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
    "gate_proj",
    "up_proj",
    "down_proj",
]


@dataclass
class TrainingConfig:
    model_name: str
    dataset_repo: str
    max_seq_length: int
    load_in_4bit: bool
    load_in_8bit: bool
    lora_r: int
    lora_alpha: int
    lora_dropout: float
    lora_bias: str
    use_rslora: bool
    optim: str
    batch_size: int
    gradient_accumulation_steps: int
    packing: bool
    use_gradient_checkpointing: str
    learning_rate: float
    lr_scheduler_type: str
    warmup_ratio: float
    weight_decay: float
    max_steps: int
    num_train_epochs: float
    save_steps: int
    eval_steps: int
    logging_steps: int
    seed: int
    experiment_name: Optional[str] = None
    enable_wandb: bool = False
    skip_eval: bool = False
    push_hub: bool = False
    hub_repo: Optional[str] = None
    save_gguf: bool = True
    gguf_quantizations: tuple[str, ...] = DEFAULT_GGUF_QUANTIZATIONS
    push_gguf_hub: bool = False
    gguf_hub_repo: Optional[str] = None

    def __post_init__(self) -> None:
        if self.experiment_name is None:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            model_short = self.model_name.rsplit("/", 1)[-1]
            self.experiment_name = f"{model_short}-r{self.lora_r}-{timestamp}"


def get_structured_paths(config: TrainingConfig) -> dict[str, pathlib.Path]:
    dataset_key = config.dataset_repo.replace("/", "--")
    dataset_cache_path = (
        pathlib.Path("/dataset_cache")
        / "obd-intelligence"
        / "nemotron-thinking"
        / dataset_key
    )
    checkpoint_path = (
        pathlib.Path("/checkpoints") / "experiments" / config.experiment_name
    )
    return {
        "dataset_cache": dataset_cache_path,
        "checkpoints": checkpoint_path,
    }


def load_hf_dataset(dataset_repo: str) -> datasets.Dataset:
    print(f"Downloading dataset from Hugging Face: {dataset_repo}")
    dataset = datasets.load_dataset(dataset_repo, split="train")
    if "messages" not in dataset.column_names:
        raise ValueError(f"{dataset_repo} must have a 'messages' column")
    return dataset.select_columns(["messages"])


def format_chat_template(examples, tokenizer):
    texts = []
    for conversation in examples["messages"]:
        formatted_text = tokenizer.apply_chat_template(
            conversation,
            tokenize=False,
            add_generation_prompt=False,
            enable_thinking=False,
        )
        texts.append(formatted_text)
    return {TEXT_COLUMN: texts}


def load_or_cache_dataset(config: TrainingConfig, paths: dict, tokenizer):
    dataset_cache_path = paths["dataset_cache"]

    if dataset_cache_path.exists():
        print(f"Loading cached dataset from {dataset_cache_path}")
        train_dataset = datasets.load_from_disk(str(dataset_cache_path / "train"))
        eval_dataset = datasets.load_from_disk(str(dataset_cache_path / "eval"))
        return train_dataset, eval_dataset

    dataset = load_hf_dataset(config.dataset_repo)
    split = dataset.train_test_split(
        test_size=1.0 - TRAIN_SPLIT_RATIO,
        seed=config.seed,
    )
    train_dataset = split["train"]
    eval_dataset = split["test"]

    print("Formatting datasets with chat template...")
    train_dataset = train_dataset.map(
        lambda examples: format_chat_template(examples, tokenizer),
        batched=True,
        num_proc=PREPROCESSING_WORKERS,
        remove_columns=train_dataset.column_names,
    )
    eval_dataset = eval_dataset.map(
        lambda examples: format_chat_template(examples, tokenizer),
        batched=True,
        num_proc=PREPROCESSING_WORKERS,
        remove_columns=eval_dataset.column_names,
    )

    print(f"Caching processed datasets to {dataset_cache_path}")
    dataset_cache_path.mkdir(parents=True, exist_ok=True)
    train_dataset.save_to_disk(str(dataset_cache_path / "train"))
    eval_dataset.save_to_disk(str(dataset_cache_path / "eval"))
    dataset_cache_volume.commit()

    return train_dataset, eval_dataset


def load_model(config: TrainingConfig):
    print(f"Loading model: {config.model_name}")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=config.model_name,
        max_seq_length=config.max_seq_length,
        dtype=None,
        load_in_4bit=config.load_in_4bit,
        load_in_8bit=config.load_in_8bit,
        trust_remote_code=True,
    )
    return model, tokenizer


def setup_model_for_training(model, config: TrainingConfig):
    print("Configuring LoRA for training...")
    return FastLanguageModel.get_peft_model(
        model,
        r=config.lora_r,
        target_modules=LORA_TARGET_MODULES,
        lora_alpha=config.lora_alpha,
        lora_dropout=config.lora_dropout,
        bias=config.lora_bias,
        use_gradient_checkpointing=config.use_gradient_checkpointing,
        random_state=config.seed,
        use_rslora=config.use_rslora,
        loftq_config=None,
    )


def create_training_arguments(config: TrainingConfig, output_dir: str) -> SFTConfig:
    use_epochs = config.max_steps <= 0
    skip_eval = config.skip_eval
    best_model_kwargs: dict = {}
    if not skip_eval:
        best_model_kwargs = {
            "load_best_model_at_end": True,
            "metric_for_best_model": "eval_loss",
            "greater_is_better": False,
            "save_total_limit": 1,
        }
    return SFTConfig(
        output_dir=output_dir,
        per_device_train_batch_size=config.batch_size,
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        learning_rate=config.learning_rate,
        max_steps=config.max_steps if not use_epochs else -1,
        num_train_epochs=config.num_train_epochs if use_epochs else 1.0,
        warmup_ratio=config.warmup_ratio,
        eval_steps=config.eval_steps,
        save_steps=config.eval_steps if not skip_eval else config.save_steps,
        eval_strategy="no" if skip_eval else "steps",
        save_strategy="no" if skip_eval else "steps",
        do_eval=not skip_eval,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        optim=config.optim,
        weight_decay=config.weight_decay,
        lr_scheduler_type=config.lr_scheduler_type,
        logging_steps=config.logging_steps,
        report_to="wandb" if config.enable_wandb else [],
        seed=config.seed,
        dataset_text_field=TEXT_COLUMN,
        max_seq_length=config.max_seq_length,
        dataset_num_proc=PREPROCESSING_WORKERS,
        packing=config.packing,
        **best_model_kwargs,
    )


def check_for_existing_checkpoint(paths: dict) -> str | None:
    checkpoint_dir = paths["checkpoints"]
    if not checkpoint_dir.exists():
        return None
    checkpoints = sorted(
        (
            p
            for p in checkpoint_dir.glob("checkpoint-*")
            if (p / "trainer_state.json").is_file()
        ),
        key=lambda p: int(p.name.split("-")[1]),
    )
    if not checkpoints:
        orphan = list(checkpoint_dir.glob("checkpoint-*"))
        if orphan:
            print(
                "Ignoring incomplete checkpoint(s) without trainer_state.json "
                f"(from save_only_model or interrupted save): {orphan}"
            )
        return None
    latest_checkpoint = checkpoints[-1]
    print(f"Found resumable checkpoint: {latest_checkpoint}")
    return str(latest_checkpoint)


def load_adapter_model(adapter_path: pathlib.Path, config: TrainingConfig):
    print(f"Loading adapter from {adapter_path} ...")
    return FastLanguageModel.from_pretrained(
        model_name=str(adapter_path),
        max_seq_length=config.max_seq_length,
        dtype=None,
        load_in_4bit=config.load_in_4bit,
        load_in_8bit=config.load_in_8bit,
        trust_remote_code=True,
    )


def ensure_llama_cpp_link(work_dir: pathlib.Path) -> None:
    unsloth_llama = pathlib.Path(LLAMA_CPP_PATH)
    if not unsloth_llama.exists():
        raise RuntimeError(
            f"Missing {unsloth_llama}. Image build should link /opt/llama.cpp here."
        )
    link_path = work_dir / "llama.cpp"
    if link_path.is_symlink() and link_path.resolve() == unsloth_llama.resolve():
        return
    if link_path.exists() or link_path.is_symlink():
        link_path.unlink()
    link_path.symlink_to(unsloth_llama, target_is_directory=True)


def export_gguf_artifacts(
    model,
    tokenizer,
    config: TrainingConfig,
    checkpoint_path: pathlib.Path,
    *,
    adapter_path: pathlib.Path | None = None,
) -> None:
    if not config.save_gguf and not config.push_gguf_hub:
        return

    gguf_dir = checkpoint_path / "gguf"
    gguf_dir.mkdir(parents=True, exist_ok=True)
    original_cwd = os.getcwd()
    os.chdir(gguf_dir)
    try:
        ensure_llama_cpp_link(gguf_dir)
        token = os.environ.get("HF_TOKEN")
        methods = list(config.gguf_quantizations)
        if not methods:
            raise ValueError("gguf_quantizations must include at least one method")
        # One call merges once, then quantizes all methods (looping per-method breaks q8_0).
        quant_arg = methods[0] if len(methods) == 1 else methods

        if config.save_gguf:
            out_name = config.experiment_name
            print(f"Saving GGUF {methods} to {gguf_dir / out_name} ...")
            model.save_pretrained_gguf(
                out_name,
                tokenizer,
                quantization_method=quant_arg,
            )

        if config.push_gguf_hub:
            if not config.gguf_hub_repo:
                raise ValueError("push_gguf_hub requires gguf_hub_repo")
            if not token:
                raise ValueError("push_gguf_hub requires HF_TOKEN in huggingface-secret")
            if config.save_gguf:
                if adapter_path is None:
                    raise ValueError("adapter_path required to push GGUF after local save")
                print("Reloading LoRA adapter for Hub GGUF push ...")
                model, tokenizer = load_adapter_model(adapter_path, config)
            print(f"Pushing GGUF to Hub: {config.gguf_hub_repo} ({methods}) ...")
            model.push_to_hub_gguf(
                config.gguf_hub_repo,
                tokenizer,
                quantization_method=quant_arg,
                token=token,
            )
    finally:
        os.chdir(original_cwd)

    checkpoint_volume.commit()
    print(f"GGUF artifacts in volume: {gguf_dir}")


def push_lora_to_hub(model, tokenizer, hub_repo: str) -> None:
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise ValueError("push_hub requires HF_TOKEN in huggingface-secret")
    print(f"Pushing LoRA adapter to {hub_repo} ...")
    model.push_to_hub(hub_repo, token=token)
    tokenizer.push_to_hub(hub_repo, token=token)


@app.function(
    image=train_image,
    gpu=GPU_TYPE,
    volumes={
        "/model_cache": model_cache_volume,
        "/dataset_cache": dataset_cache_volume,
        "/checkpoints": checkpoint_volume,
    },
    secrets=[modal.Secret.from_name("huggingface-secret")],
    timeout=TIMEOUT_HOURS * 60 * 60,
    retries=modal.Retries(initial_delay=0.0, max_retries=MAX_RETRIES),
    single_use_containers=True,
)
def finetune(config: TrainingConfig):
    paths = get_structured_paths(config)

    if config.enable_wandb:
        wandb.init(
            project="obd-nemotron-finetune",
            name=config.experiment_name,
            config=config.__dict__,
        )

    print("Setting up model and data...")
    model, tokenizer = load_model(config)
    train_dataset, eval_dataset = load_or_cache_dataset(config, paths, tokenizer)
    model = setup_model_for_training(model, config)

    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Total parameters: {total_params:,}")
    print(f"Trainable parameters: {trainable_params:,}")
    if trainable_params == 0:
        raise RuntimeError("No trainable LoRA parameters — check target_modules.")

    if len(train_dataset) > 0:
        sample = train_dataset[0][TEXT_COLUMN]
        print(f"Sample formatted text (first 500 chars):\n{sample[:500]}\n...")

    checkpoint_path = paths["checkpoints"]
    checkpoint_path.mkdir(parents=True, exist_ok=True)
    resume_from_checkpoint = check_for_existing_checkpoint(paths)
    training_args = create_training_arguments(config, str(checkpoint_path))

    print("Initializing SFTTrainer...")
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset if not config.skip_eval else None,
        args=training_args,
    )
    trainer = train_on_responses_only(
        trainer,
        instruction_part="<|im_start|>user\n",
        response_part="<|im_start|>assistant\n",
    )

    print(f"Training dataset size: {len(train_dataset):,}")
    if not config.skip_eval:
        print(f"Evaluation dataset size: {len(eval_dataset):,}")
    print(f"Experiment: {config.experiment_name}")

    if resume_from_checkpoint:
        print(f"Resuming training from {resume_from_checkpoint}")
        trainer.train(resume_from_checkpoint=resume_from_checkpoint)
    else:
        print("Starting training from scratch...")
        trainer.train()

    print("Saving best model...")
    model_dir_name = "best_model" if not config.skip_eval else "final_model"
    saved_model_path = checkpoint_path / model_dir_name
    model.save_pretrained(str(saved_model_path))
    tokenizer.save_pretrained(str(saved_model_path))
    checkpoint_volume.commit()

    if config.push_hub:
        if not config.hub_repo:
            raise ValueError("push_hub requires hub_repo")
        push_lora_to_hub(model, tokenizer, config.hub_repo)

    export_gguf_artifacts(
        model, tokenizer, config, checkpoint_path, adapter_path=saved_model_path
    )

    if config.enable_wandb:
        wandb.finish()

    print(f"Training completed! Model saved to: {saved_model_path}")
    if config.save_gguf:
        print(f"GGUF saved under: {checkpoint_path / 'gguf'}")
    if config.push_hub and config.hub_repo:
        print(f"LoRA adapter on Hub: https://huggingface.co/{config.hub_repo}")
    if config.push_gguf_hub and config.gguf_hub_repo:
        print(f"GGUF on Hub: https://huggingface.co/{config.gguf_hub_repo}")
    return config.experiment_name


def resolve_adapter_path(checkpoint_path: pathlib.Path) -> pathlib.Path:
    for name in ("best_model", "final_model"):
        path = checkpoint_path / name
        if path.exists():
            return path
    raise FileNotFoundError(
        f"No saved adapter under {checkpoint_path} (expected best_model/ or final_model/)"
    )


@app.function(
    image=train_image,
    gpu=GPU_TYPE,
    volumes={
        "/model_cache": model_cache_volume,
        "/dataset_cache": dataset_cache_volume,
        "/checkpoints": checkpoint_volume,
    },
    secrets=[modal.Secret.from_name("huggingface-secret")],
    timeout=TIMEOUT_HOURS * 60 * 60,
    retries=modal.Retries(initial_delay=0.0, max_retries=MAX_RETRIES),
)
def export_artifacts(config: TrainingConfig):
    """Export LoRA + GGUF from a finished experiment without retraining."""
    if not config.experiment_name:
        raise ValueError("experiment_name is required for export")

    checkpoint_path = (
        pathlib.Path("/checkpoints") / "experiments" / config.experiment_name
    )
    adapter_path = resolve_adapter_path(checkpoint_path)
    model, tokenizer = load_adapter_model(adapter_path, config)

    if config.push_hub:
        if not config.hub_repo:
            raise ValueError("push_hub requires hub_repo")
        push_lora_to_hub(model, tokenizer, config.hub_repo)

    export_gguf_artifacts(
        model, tokenizer, config, checkpoint_path, adapter_path=adapter_path
    )

    print(f"Export completed from: {adapter_path}")
    if config.push_hub and config.hub_repo:
        print(f"LoRA adapter on Hub: https://huggingface.co/{config.hub_repo}")
    if config.push_gguf_hub and config.gguf_hub_repo:
        print(f"GGUF on Hub: https://huggingface.co/{config.gguf_hub_repo}")
    return config.experiment_name


def parse_gguf_quantizations(value: str) -> tuple[str, ...]:
    methods = tuple(m.strip() for m in value.split(",") if m.strip())
    if not methods:
        raise ValueError("gguf-quantizations must list at least one method, e.g. q4_k_m,q8_0")
    return methods


@app.local_entrypoint()
def main(
    dataset_repo: str = DEFAULT_DATASET_REPO,
    model_name: str = DEFAULT_MODEL,
    max_seq_length: int = 8192,
    load_in_4bit: bool = True,
    load_in_8bit: bool = False,
    lora_r: int = 16,
    lora_alpha: int = 32,
    lora_dropout: float = 0.0,
    lora_bias: str = "none",
    use_rslora: bool = False,
    optim: str = "adamw_8bit",
    batch_size: int = 2,
    gradient_accumulation_steps: int = 8,
    packing: bool = False,
    use_gradient_checkpointing: str = "unsloth",
    learning_rate: float = 2e-4,
    lr_scheduler_type: str = "cosine",
    warmup_ratio: float = 0.06,
    weight_decay: float = 0.01,
    max_steps: int = -1,
    num_train_epochs: float = 2.0,
    save_steps: int = 100,
    eval_steps: int = 100,
    logging_steps: int = 10,
    seed: int = 42,
    experiment_name: Optional[str] = None,
    disable_wandb: bool = True,
    skip_eval: bool = False,
    push_hub: bool = False,
    hub_repo: Optional[str] = None,
    push_all_hub: bool = False,
    no_gguf: bool = False,
    gguf_quantizations: str = "q4_k_m,q8_0",
    push_gguf_hub: bool = False,
    gguf_hub_repo: Optional[str] = None,
):
    push_hub = push_hub or push_all_hub
    push_gguf_hub = push_gguf_hub or push_all_hub
    if push_hub and not hub_repo:
        hub_repo = DEFAULT_HUB_REPO
    if push_gguf_hub and not gguf_hub_repo:
        gguf_hub_repo = DEFAULT_GGUF_HUB_REPO

    config = TrainingConfig(
        model_name=model_name,
        dataset_repo=dataset_repo,
        max_seq_length=max_seq_length,
        load_in_4bit=load_in_4bit,
        load_in_8bit=load_in_8bit,
        lora_r=lora_r,
        lora_alpha=lora_alpha,
        lora_bias=lora_bias,
        lora_dropout=lora_dropout,
        use_rslora=use_rslora,
        optim=optim,
        batch_size=batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        packing=packing,
        use_gradient_checkpointing=use_gradient_checkpointing,
        learning_rate=learning_rate,
        max_steps=max_steps,
        num_train_epochs=num_train_epochs,
        lr_scheduler_type=lr_scheduler_type,
        warmup_ratio=warmup_ratio,
        weight_decay=weight_decay,
        save_steps=save_steps,
        eval_steps=eval_steps,
        logging_steps=logging_steps,
        seed=seed,
        experiment_name=experiment_name,
        enable_wandb=not disable_wandb,
        skip_eval=skip_eval,
        push_hub=push_hub,
        hub_repo=hub_repo,
        save_gguf=not no_gguf,
        gguf_quantizations=parse_gguf_quantizations(gguf_quantizations),
        push_gguf_hub=push_gguf_hub,
        gguf_hub_repo=gguf_hub_repo,
    )

    print(f"Starting finetuning experiment: {config.experiment_name}")
    print(f"Model: {config.model_name}")
    print(f"Dataset repo: {config.dataset_repo}")
    print(f"max_seq_length: {config.max_seq_length}")
    print(f"LoRA: rank={config.lora_r}, alpha={config.lora_alpha}")
    print(
        f"Effective batch size: {config.batch_size * config.gradient_accumulation_steps}"
    )
    if config.max_steps > 0:
        print(f"Training steps: {config.max_steps}")
    else:
        print(f"Training epochs: {config.num_train_epochs}")
    if config.push_hub:
        print(f"Will push LoRA adapter to: {config.hub_repo}")
    if config.push_gguf_hub:
        print(
            f"Will push GGUF ({', '.join(config.gguf_quantizations)}) to: "
            f"{config.gguf_hub_repo}"
        )

    result = finetune.remote(config)
    print(f"Training completed successfully: {result}")


@app.local_entrypoint()
def export(
    experiment_name: str,
    max_seq_length: int = 8192,
    load_in_4bit: bool = True,
    push_hub: bool = False,
    hub_repo: Optional[str] = None,
    push_all_hub: bool = False,
    no_gguf: bool = False,
    gguf_quantizations: str = "q4_k_m,q8_0",
    push_gguf_hub: bool = False,
    gguf_hub_repo: Optional[str] = None,
):
    """Export GGUF / push to Hub from an existing best_model on the volume."""
    push_hub = push_hub or push_all_hub
    push_gguf_hub = push_gguf_hub or push_all_hub
    if push_hub and not hub_repo:
        hub_repo = DEFAULT_HUB_REPO
    if push_gguf_hub and not gguf_hub_repo:
        gguf_hub_repo = DEFAULT_GGUF_HUB_REPO

    config = TrainingConfig(
        model_name=DEFAULT_MODEL,
        dataset_repo=DEFAULT_DATASET_REPO,
        max_seq_length=max_seq_length,
        load_in_4bit=load_in_4bit,
        load_in_8bit=False,
        lora_r=16,
        lora_alpha=32,
        lora_dropout=0.0,
        lora_bias="none",
        use_rslora=False,
        optim="adamw_8bit",
        batch_size=2,
        gradient_accumulation_steps=8,
        packing=False,
        use_gradient_checkpointing="unsloth",
        learning_rate=2e-4,
        lr_scheduler_type="cosine",
        warmup_ratio=0.06,
        weight_decay=0.01,
        max_steps=-1,
        num_train_epochs=0,
        save_steps=100,
        eval_steps=100,
        logging_steps=10,
        seed=42,
        experiment_name=experiment_name,
        push_hub=push_hub,
        hub_repo=hub_repo,
        save_gguf=not no_gguf,
        gguf_quantizations=parse_gguf_quantizations(gguf_quantizations),
        push_gguf_hub=push_gguf_hub,
        gguf_hub_repo=gguf_hub_repo,
    )

    print(f"Exporting experiment: {experiment_name}")
    if config.push_hub:
        print(f"Will push LoRA adapter to: {config.hub_repo}")
    if config.push_gguf_hub:
        print(
            f"Will push GGUF ({', '.join(config.gguf_quantizations)}) to: "
            f"{config.gguf_hub_repo}"
        )

    result = export_artifacts.remote(config)
    print(f"Export completed successfully: {result}")

# /// script
# dependencies = [
#   "unsloth",
#   "trl",
#   "datasets",
#   "huggingface_hub",
# ]
# ///
"""Fine-tune Gemma 4 E2B on the Pocket Mechanic distillation set (HF Jobs).

Launch from the repo root:
    hf jobs uv run --flavor a10g-large --timeout 3h --secrets HF_TOKEN train_cloud.py
"""
import os

from unsloth import FastModel

DATASET = "MindFreakGamer/pocket-mechanic-distilled"
BASE = "unsloth/gemma-4-E2B-it"
OUT_LORA = "MindFreakGamer/gemma-4-E2B-pocket-mechanic-lora"
OUT_MERGED = "MindFreakGamer/gemma-4-E2B-pocket-mechanic"
MAX_SEQ = 2048

model, tokenizer = FastModel.from_pretrained(
    BASE, max_seq_length=MAX_SEQ, load_in_4bit=True, token=os.environ.get("HF_TOKEN")
)
model = FastModel.get_peft_model(
    model, r=16, lora_alpha=32, lora_dropout=0.05,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    use_gradient_checkpointing="unsloth", random_state=42,
)

from datasets import load_dataset

ds = load_dataset(DATASET, data_files={"train": "train.jsonl", "valid": "valid.jsonl"})


def to_text(batch):
    texts = []
    for messages in batch["messages"]:
        try:
            t = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
        except Exception:
            # template without system support: fold system into first user turn
            sys_txt = messages[0]["content"]
            folded = [{"role": "user", "content": sys_txt + "\n\n" + messages[1]["content"]},
                      messages[2]]
            t = tokenizer.apply_chat_template(folded, tokenize=False, add_generation_prompt=False)
        texts.append(t)
    return {"text": texts}


ds = ds.map(to_text, batched=True, remove_columns=ds["train"].column_names)

from trl import SFTConfig, SFTTrainer
from unsloth.chat_templates import train_on_responses_only

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=ds["train"],
    eval_dataset=ds["valid"],
    args=SFTConfig(
        dataset_text_field="text",
        max_seq_length=MAX_SEQ,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        num_train_epochs=2,
        learning_rate=1e-4,
        lr_scheduler_type="cosine",
        warmup_steps=30,
        logging_steps=25,
        eval_strategy="steps",
        eval_steps=250,
        save_strategy="no",
        output_dir="outputs",
        seed=42,
        report_to="none",
    ),
)
trainer = train_on_responses_only(
    trainer,
    instruction_part="<start_of_turn>user\n",
    response_part="<start_of_turn>model\n",
)

print(trainer.evaluate())  # baseline eval loss before training
trainer.train()
print(trainer.evaluate())  # final eval loss

token = os.environ["HF_TOKEN"]
model.push_to_hub(OUT_LORA, token=token, private=True)
tokenizer.push_to_hub(OUT_LORA, token=token, private=True)
print("pushed LoRA ->", OUT_LORA)

model.push_to_hub_merged(OUT_MERGED, tokenizer, save_method="merged_16bit",
                         token=token, private=True)
print("pushed merged fp16 ->", OUT_MERGED)

try:
    model.push_to_hub_gguf(
        OUT_MERGED + "-GGUF", tokenizer,
        quantization_method=["q4_k_m", "q8_0"],
        token=token, private=True,
    )
    print("pushed GGUF ->", OUT_MERGED + "-GGUF")
except Exception as e:
    print(f"GGUF export failed (will convert locally instead): {e}")

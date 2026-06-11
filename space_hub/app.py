"""Pocket Mechanic — Hugging Face Space entrypoint."""
import os
from pathlib import Path

import gradio as gr
import pandas as pd
from huggingface_hub import hf_hub_download

from pipeline import Explainer, Predictor, load_sessions, scenario_choices
from promptlib import build_inference_prompt

GGUF_REPO = "MindFreakGamer/gemma-4-E2B-pocket-mechanic-GGUF"
GGUF_FILE = "pocket-mechanic-q8_0.gguf"
PLOT_SIGNALS = ["rpm", "coolant_temp_c", "stft_pct", "control_module_voltage_v"]
REPLAY_STEP = 15
DEFAULT_VEHICLE = "2014 Toyota Camry, 2.5L I4, 128,000 mi"

print("loading data + predictor...")
DF = load_sessions()
SCENARIOS = scenario_choices(DF)
PREDICTOR = Predictor()

print("fetching GGUF from the Hub...")
gguf_path = hf_hub_download(GGUF_REPO, GGUF_FILE, token=os.environ.get("HF_TOKEN"))
EXPLAINER = Explainer(gguf_path)
print("ready.")


def session_meta(scenario_label):
    g = DF[DF["session_id"] == SCENARIOS[scenario_label]]
    dtc = "" if pd.isna(g["ground_truth_dtc"].iat[0]) else g["ground_truth_dtc"].iat[0]
    return g.sort_values("t").reset_index(drop=True), dtc, g["driving_context"].iat[0]


def replay(scenario_label):
    g, dtc, _ = session_meta(scenario_label)
    for end in range(REPLAY_STEP, len(g) + 1, REPLAY_STEP):
        window = g.iloc[max(0, end - PREDICTOR.window_sec):end]
        probs = PREDICTOR.predict(window) if len(window) >= 30 else {}
        top5 = dict(list(probs.items())[:5])
        plot_df = window[["t"] + PLOT_SIGNALS].melt("t", var_name="signal", value_name="value")
        status = f"t = {end}s / {len(g)}s   |   DTC: {dtc or 'none yet'}"
        yield plot_df, top5, status, window


def diagnose(window, scenario_label, vehicle, question):
    if window is None or len(window) < 30:
        yield "Run a replay first so I have sensor data to look at."
        return
    _, dtc, context = session_meta(scenario_label)
    probs = PREDICTOR.predict(window)
    prompt = build_inference_prompt(window, vehicle, probs, dtc,
                                    question or "What's wrong with my car?", context)
    acc = ""
    for tok in EXPLAINER.stream(prompt):
        acc += tok
        yield acc


with gr.Blocks(title="Pocket Mechanic") as demo:
    gr.Markdown(
        "# 🔧 Pocket Mechanic\n"
        "*A mechanic in your pocket who can't be gaslit.* "
        "A 1.4 MB XGBoost fault predictor + Gemma 4 E2B fine-tuned on Claude Opus 4.7 "
        "distillations, running **fully locally via llama.cpp** — the same GGUF file a "
        "phone app would load. No API calls at inference time."
    )
    with gr.Tab("Take a drive"):
        with gr.Row():
            scenario = gr.Dropdown(choices=list(SCENARIOS), value=list(SCENARIOS)[0],
                                   label="Drive scenario (real drive data + injected fault)")
            vehicle = gr.Textbox(value=DEFAULT_VEHICLE, label="Vehicle")
        start = gr.Button("▶ Start drive", variant="primary")
        status = gr.Markdown("")
        with gr.Row():
            plot = gr.LinePlot(x="t", y="value", color="signal",
                               label="Live sensors", height=260)
            probs = gr.Label(num_top_classes=5, label="Fault probabilities (live)")
        window_state = gr.State()
        question = gr.Textbox(label="Ask the mechanic",
                              placeholder="What's wrong with my car? Is it safe to drive?")
        ask = gr.Button("🔧 Diagnose", variant="primary")
        answer = gr.Markdown("")

        start.click(replay, inputs=[scenario],
                    outputs=[plot, probs, status, window_state])
        ask.click(diagnose, inputs=[window_state, scenario, vehicle, question],
                  outputs=[answer])

    with gr.Tab("How it works"):
        gr.Markdown(Path(__file__).with_name("HOW_IT_WORKS.md").read_text()
                    if Path(__file__).with_name("HOW_IT_WORKS.md").exists()
                    else "Architecture writeup coming.")

if __name__ == "__main__":
    demo.launch()

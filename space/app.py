"""Pocket Mechanic — Gradio Space.

Tab 1: replay a recorded drive, watch the fault predictor live, then ask the
on-device mechanic (fine-tuned Gemma 4 E2B via llama.cpp) what's going on.

    .venv/bin/python space/app.py
"""
import os
from pathlib import Path

import gradio as gr
import pandas as pd

from pipeline import (Explainer, Predictor, build_inference_prompt,
                      load_sessions, scenario_choices)

ROOT = Path(__file__).resolve().parent.parent
GGUF_PATH = os.environ.get("GGUF_PATH", str(ROOT / "models/pocket-mechanic-q4_k_m.gguf"))
PLOT_SIGNALS = ["rpm", "coolant_temp_c", "stft_pct", "control_module_voltage_v"]
REPLAY_STEP = 15          # seconds of drive consumed per UI update
DEFAULT_VEHICLE = "2014 Toyota Camry, 2.5L I4, 128,000 mi"

print("loading data + predictor...")
DF = load_sessions()
SCENARIOS = scenario_choices(DF)
PREDICTOR = Predictor()
EXPLAINER = None
if Path(GGUF_PATH).exists():
    print(f"loading explainer from {GGUF_PATH}...")
    EXPLAINER = Explainer(GGUF_PATH)
else:
    print(f"[no GGUF at {GGUF_PATH} — explainer disabled]")


def replay(scenario_label):
    sid = SCENARIOS[scenario_label]
    g = DF[DF["session_id"] == sid].sort_values("t").reset_index(drop=True)
    for end in range(REPLAY_STEP, len(g) + 1, REPLAY_STEP):
        window = g.iloc[max(0, end - PREDICTOR.window_sec):end]
        probs = PREDICTOR.predict(window) if len(window) >= 30 else {}
        top5 = dict(list(probs.items())[:5])
        plot_df = window[["t"] + PLOT_SIGNALS].melt("t", var_name="signal", value_name="value")
        dtc = "" if pd.isna(g["ground_truth_dtc"].iat[0]) else g["ground_truth_dtc"].iat[0]
        status = f"t = {end}s / {len(g)}s   |   DTC: {dtc or 'none yet'}"
        yield plot_df, top5, status, window


def diagnose(window, scenario_label, vehicle, question):
    if window is None or len(window) < 30:
        yield "Run a replay first so I have sensor data to look at."
        return
    sid = SCENARIOS[scenario_label]
    g = DF[DF["session_id"] == sid]
    dtc = "" if pd.isna(g["ground_truth_dtc"].iat[0]) else g["ground_truth_dtc"].iat[0]
    context = g["driving_context"].iat[0]
    probs = PREDICTOR.predict(window)
    prompt = build_inference_prompt(window, vehicle, probs, dtc,
                                    question or "What's wrong with my car?", context)
    if EXPLAINER is None:
        yield ("**Explainer model not loaded.** (Fine-tuned GGUF not present yet.)\n\n"
               f"Prompt that would be sent:\n\n```\n{prompt}\n```")
        return
    acc = ""
    for tok in EXPLAINER.stream(prompt):
        acc += tok
        yield acc


with gr.Blocks(title="Pocket Mechanic") as demo:
    gr.Markdown("# 🔧 Pocket Mechanic\n*A mechanic in your pocket who can't be gaslit. "
                "Fully offline-capable: 1.4 MB fault predictor + 1.2 GB fine-tuned Gemma 4 E2B.*")
    with gr.Tab("Take a drive"):
        with gr.Row():
            scenario = gr.Dropdown(choices=list(SCENARIOS), value=list(SCENARIOS)[0],
                                   label="Drive scenario (recorded + fault-injected)")
            vehicle = gr.Textbox(value=DEFAULT_VEHICLE, label="Vehicle")
        start = gr.Button("▶ Start drive", variant="primary")
        status = gr.Markdown("")
        with gr.Row():
            plot = gr.LinePlot(x="t", y="value", color="signal", label="Live sensors",
                               height=260)
            probs = gr.Label(num_top_classes=5, label="Fault probabilities (live)")
        window_state = gr.State()
        question = gr.Textbox(label="Ask the mechanic",
                              placeholder="What's wrong with my car? Is it safe to drive?")
        ask = gr.Button("🔧 Diagnose")
        answer = gr.Markdown("")

        start.click(replay, inputs=[scenario],
                    outputs=[plot, probs, status, window_state])
        ask.click(diagnose, inputs=[window_state, scenario, vehicle, question],
                  outputs=[answer])

if __name__ == "__main__":
    demo.launch()

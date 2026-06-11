"""Replay → features → predictor → prompt glue for the Gradio Space."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "predictor"))

from distill import STUDENT_SYSTEM, window_stats, last30  # noqa: E402
from features import extract  # noqa: E402


class Predictor:
    def __init__(self, model_dir=ROOT / "predictor"):
        self.booster = xgb.Booster()
        self.booster.load_model(str(model_dir / "model.json"))
        meta = json.loads((model_dir / "meta.json").read_text())
        self.classes = meta["classes"]
        self.window_sec = meta["window_sec"]

    def predict(self, window: pd.DataFrame) -> dict[str, float]:
        feats = extract(window).reshape(1, -1)
        probs = self.booster.predict(xgb.DMatrix(feats))[0]
        return dict(sorted(zip(self.classes, probs.tolist()),
                           key=lambda kv: -kv[1]))


def load_sessions(csv_path=ROOT / "data/synthetic/synthetic_sessions.csv"):
    df = pd.read_csv(csv_path)
    return df


def scenario_choices(df):
    picks = (df[["session_id", "fault_class", "severity"]]
             .drop_duplicates()
             .groupby(["fault_class", "severity"]).head(1))
    return {f"{r.fault_class} ({r.severity})": r.session_id
            for r in picks.itertuples() if r.severity == "severe" or r.fault_class == "healthy"}


def build_inference_prompt(window, vehicle, preds, dtc, question, context):
    top = list(preds.items())[:3]
    pred_txt = ", ".join(f"{n}: {p:.0%}" for n, p in top)
    return f"""VEHICLE: {vehicle}
DRIVE WINDOW: last {len(window) / 60:.1f} min, context: {context}

SENSOR SUMMARY (full window):
{window_stats(window)}

LAST 30 SECONDS (averages): {last30(window)}

ACTIVE DTCs: {dtc or 'none'}
PREDICTOR OUTPUT: {pred_txt}

DRIVER ASKS: {question}"""


class Explainer:
    def __init__(self, gguf_path, n_ctx=4096):
        from llama_cpp import Llama
        self.llm = Llama(model_path=str(gguf_path), n_ctx=n_ctx,
                         n_gpu_layers=-1, verbose=False)

    def stream(self, prompt, max_tokens=700):
        msgs = [{"role": "system", "content": STUDENT_SYSTEM},
                {"role": "user", "content": prompt}]
        for chunk in self.llm.create_chat_completion(msgs, max_tokens=max_tokens,
                                                     stream=True):
            delta = chunk["choices"][0]["delta"]
            if "content" in delta and delta["content"]:
                yield delta["content"]

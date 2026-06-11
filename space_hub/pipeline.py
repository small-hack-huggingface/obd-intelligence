"""Replay -> features -> predictor -> LLM glue (standalone Space version)."""
import json
from pathlib import Path

import pandas as pd
import xgboost as xgb

from features import extract
from promptlib import STUDENT_SYSTEM

HERE = Path(__file__).resolve().parent


class Predictor:
    def __init__(self, model_dir=HERE):
        self.booster = xgb.Booster()
        self.booster.load_model(str(model_dir / "model.json"))
        meta = json.loads((model_dir / "meta.json").read_text())
        self.classes = meta["classes"]
        self.window_sec = meta["window_sec"]

    def predict(self, window: pd.DataFrame) -> dict:
        feats = extract(window).reshape(1, -1)
        probs = self.booster.predict(xgb.DMatrix(feats))[0]
        return dict(sorted(zip(self.classes, probs.tolist()), key=lambda kv: -kv[1]))


def load_sessions(csv_path=HERE / "scenarios.csv"):
    return pd.read_csv(csv_path)


def scenario_choices(df):
    picks = (df[["session_id", "fault_class", "severity"]]
             .drop_duplicates()
             .groupby(["fault_class", "severity"]).head(1))
    return {f"{r.fault_class} ({r.severity})": r.session_id
            for r in picks.itertuples()
            if r.severity == "severe" or r.fault_class == "healthy"}


class Explainer:
    def __init__(self, gguf_path, n_ctx=4096):
        from llama_cpp import Llama
        self.llm = Llama(model_path=str(gguf_path), n_ctx=n_ctx,
                         n_gpu_layers=-1, verbose=False)

    def stream(self, prompt, max_tokens=700, temperature=0.2, top_p=0.9):
        msgs = [{"role": "system", "content": STUDENT_SYSTEM},
                {"role": "user", "content": prompt}]
        for chunk in self.llm.create_chat_completion(msgs, max_tokens=max_tokens,
                                                     temperature=temperature,
                                                     top_p=top_p, stream=True):
            delta = chunk["choices"][0]["delta"]
            if delta.get("content"):
                yield delta["content"]

"""Train the XGBoost fault predictor on synthetic sessions.

Windows are sampled per session; the train/test split is by SESSION so no
session leaks across the split.

    .venv/bin/python predictor/train.py
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import accuracy_score, top_k_accuracy_score
from sklearn.model_selection import train_test_split

import sys
sys.path.insert(0, str(Path(__file__).parent))
from features import FEATURE_NAMES, extract


def windows_from_session(g, win=150, step=75):
    g = g.sort_values("t").reset_index(drop=True)
    for start in range(0, len(g) - win + 1, step):
        yield g.iloc[start:start + win]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/synthetic/synthetic_sessions.csv")
    ap.add_argument("--out", default="predictor")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    df = pd.read_csv(args.data)
    sessions = df[["session_id", "fault_class"]].drop_duplicates()
    train_ids, test_ids = train_test_split(
        sessions["session_id"], test_size=0.2, random_state=args.seed,
        stratify=sessions["fault_class"])
    train_ids, test_ids = set(train_ids), set(test_ids)

    classes = sorted(df["fault_class"].unique())
    cls_idx = {c: i for i, c in enumerate(classes)}

    X = {"train": [], "test": []}
    y = {"train": [], "test": []}
    for sid, g in df.groupby("session_id"):
        split = "train" if sid in train_ids else "test"
        label = cls_idx[g["fault_class"].iat[0]]
        for w in windows_from_session(g):
            X[split].append(extract(w))
            y[split].append(label)

    Xtr, ytr = np.stack(X["train"]), np.array(y["train"])
    Xte, yte = np.stack(X["test"]), np.array(y["test"])
    print(f"train windows: {len(ytr)}  test windows: {len(yte)}  classes: {len(classes)}")

    model = xgb.XGBClassifier(
        n_estimators=400, max_depth=6, learning_rate=0.1,
        subsample=0.9, colsample_bytree=0.8, reg_lambda=1.0,
        objective="multi:softprob", eval_metric="mlogloss",
        early_stopping_rounds=30, random_state=args.seed, n_jobs=-1)
    model.fit(Xtr, ytr, eval_set=[(Xte, yte)], verbose=False)

    probs = model.predict_proba(Xte)
    pred = probs.argmax(axis=1)
    acc = accuracy_score(yte, pred)
    top3 = top_k_accuracy_score(yte, probs, k=3, labels=np.arange(len(classes)))
    print(f"accuracy: {acc:.3f}   top-3 accuracy: {top3:.3f}")

    errs = pd.crosstab(pd.Series([classes[i] for i in yte], name="true"),
                       pd.Series([classes[i] for i in pred], name="pred"))
    miss = [(t, p, errs.loc[t, p]) for t in errs.index for p in errs.columns
            if t != p and errs.loc[t, p] > 0]
    print("top confusions:", sorted(miss, key=lambda x: -x[2])[:8])

    out = Path(args.out)
    model.get_booster().save_model(out / "model.json")
    (out / "meta.json").write_text(json.dumps(
        {"classes": classes, "feature_names": FEATURE_NAMES,
         "window_sec": 150, "accuracy": round(acc, 4), "top3": round(top3, 4)}, indent=1))
    size_kb = (out / "model.json").stat().st_size / 1024
    print(f"saved {out}/model.json ({size_kb:.0f} KB) + meta.json")


if __name__ == "__main__":
    main()

"""Split distilled pairs into MLX-format train/valid sets.

mlx_lm.lora expects a data dir containing train.jsonl and valid.jsonl where each
line is {"messages": [...]}. Split is stratified by fault_class so the valid set
covers every fault.

    python prep_finetune.py --in data/distilled/train.jsonl --out data/mlx
"""
import argparse
import json
import random
from collections import defaultdict
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default="data/distilled/train.jsonl")
    ap.add_argument("--out", default="data/mlx")
    ap.add_argument("--valid-frac", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=13)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    by_fault = defaultdict(list)
    with open(args.inp) as f:
        for line in f:
            rec = json.loads(line)
            by_fault[rec["fault_class"]].append({"messages": rec["messages"]})

    train, valid = [], []
    for fault, recs in sorted(by_fault.items()):
        rng.shuffle(recs)
        n_valid = max(1, int(len(recs) * args.valid_frac))
        valid.extend(recs[:n_valid])
        train.extend(recs[n_valid:])
    rng.shuffle(train)
    rng.shuffle(valid)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, recs in [("train", train), ("valid", valid)]:
        with (out / f"{name}.jsonl").open("w") as f:
            for r in recs:
                f.write(json.dumps(r) + "\n")
    print(f"train={len(train)} valid={len(valid)} across {len(by_fault)} fault classes -> {out}/")


if __name__ == "__main__":
    main()

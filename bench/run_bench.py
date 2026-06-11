# /// script
# dependencies = ["anthropic", "llama-cpp-python", "pandas"]
# ///
"""Benchmark the fine-tuned student against its Claude Opus 4.7 teacher.

For each held-out example: generate the student's answer locally (llama.cpp),
pair it with the teacher's answer from the dataset, and have a blind judge
score both on faithfulness, helpfulness, cost-accuracy, and anti-ripoff value.
Answers are presented in random A/B order without model names.

    .venv/bin/python bench/run_bench.py --gguf models/pocket-mechanic-q4_k_m.gguf --n 100
"""
import argparse
import json
import os
import random
import re
from pathlib import Path

JUDGE_MODEL = "claude-opus-4-7"
AXES = ["faithfulness", "helpfulness", "cost_accuracy", "anti_ripoff"]

JUDGE_SYSTEM = """You are an expert automotive diagnostician evaluating two AI-generated \
diagnostic explanations for the same car problem. You will see the sensor data and driver \
question, then two answers labeled A and B (random order, unknown sources).

Score EACH answer 1-10 on:
- faithfulness: claims grounded in the provided sensor evidence; no invented data
- helpfulness: would a non-mechanic know exactly what to do next, in the right order
- cost_accuracy: parts/labor estimates realistic for the named vehicle and fault
- anti_ripoff: identifies the actual upsell traps for this fault and arms the driver

Respond with ONLY this JSON:
{"A": {"faithfulness": n, "helpfulness": n, "cost_accuracy": n, "anti_ripoff": n},
 "B": {"faithfulness": n, "helpfulness": n, "cost_accuracy": n, "anti_ripoff": n}}"""


def load_env():
    env = Path(".env")
    if env.exists():
        for line in env.read_text().splitlines():
            if line.strip() and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gguf", required=True)
    ap.add_argument("--valid", default="data/mlx/valid.jsonl")
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--out", default="bench/results.json")
    ap.add_argument("--seed", type=int, default=99)
    ap.add_argument("--temperature", type=float, default=0.8)
    ap.add_argument("--top-p", type=float, default=0.95)
    ap.add_argument("--inject-reference", action="store_true",
                    help="append per-fault repair economics for the predicted faults")
    ap.add_argument("--lora", default=None, help="GGUF LoRA adapter applied at runtime")
    args = ap.parse_args()

    load_env()
    import anthropic
    from llama_cpp import Llama

    rng = random.Random(args.seed)
    examples = [json.loads(l) for l in open(args.valid)]
    rng.shuffle(examples)
    for i, ex in enumerate(examples):
        ex["bench_id"] = f"case_{i:04d}"
    examples = examples[:args.n]

    partial_path = Path(args.out).with_suffix(".partial.jsonl")
    done = {}
    if partial_path.exists():
        for line in partial_path.open():
            try:
                r = json.loads(line)
                done[r["id"]] = r
            except json.JSONDecodeError:
                pass
        print(f"resuming: {len(done)} cases already judged")

    print(f"loading student from {args.gguf}" +
          (f" + lora {args.lora}" if args.lora else "") + "...")
    kw = {"lora_path": args.lora} if args.lora else {}
    llm = Llama(model_path=args.gguf, n_ctx=4096, n_gpu_layers=-1, verbose=False, **kw)
    client = anthropic.Anthropic(max_retries=5)

    results = []
    if args.inject_reference:
        import sys
        sys.path.insert(0, "space_hub")
        from promptlib import reference_card

    results = list(done.values())
    pf = partial_path.open("a")
    for i, ex in enumerate(examples):
        if ex["bench_id"] in done:
            continue
        system, user, teacher = (m["content"] for m in ex["messages"])
        gen_user = user
        if args.inject_reference:
            m = re.search(r"PREDICTOR OUTPUT: (.+)", user)
            faults = [p.split(":")[0].strip() for p in m.group(1).split(",")] if m else []
            card = reference_card(faults)
            gen_user = user.replace("\nDRIVER ASKS:", f"\n{card}\n\nDRIVER ASKS:")
        resp = llm.create_chat_completion(
            [{"role": "system", "content": system}, {"role": "user", "content": gen_user}],
            max_tokens=900, temperature=args.temperature, top_p=args.top_p)
        student = resp["choices"][0]["message"]["content"]

        student_is_a = rng.random() < 0.5
        a, b = (student, teacher) if student_is_a else (teacher, student)
        judge = client.messages.create(
            model=JUDGE_MODEL, max_tokens=400,
            system=[{"type": "text", "text": JUDGE_SYSTEM,
                     "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content":
                       f"CASE:\n{user}\n\n--- ANSWER A ---\n{a}\n\n--- ANSWER B ---\n{b}"}],
        )
        text = "".join(bl.text for bl in judge.content if bl.type == "text")
        try:
            scores = json.loads(re.search(r"\{.*\}", text, re.S).group())
        except (AttributeError, json.JSONDecodeError):
            print(f"[skip {i}: unparseable judge output]")
            continue
        s_key, t_key = ("A", "B") if student_is_a else ("B", "A")
        rec = {"id": ex["bench_id"],
               "student": scores[s_key], "teacher": scores[t_key],
               "student_text": student}
        results.append(rec)
        pf.write(json.dumps(rec) + "\n")
        pf.flush()
        if (i + 1) % 10 == 0:
            print(f"  {i + 1}/{len(examples)} judged")
    pf.close()

    n = len(results)
    summary = {"n": n, "axes": {}}
    for axis in AXES:
        s = sum(r["student"][axis] for r in results) / n
        t = sum(r["teacher"][axis] for r in results) / n
        summary["axes"][axis] = {"student": round(s, 2), "teacher": round(t, 2),
                                 "ratio_pct": round(100 * s / t, 1)}
    s_all = sum(sum(r["student"][a] for a in AXES) for r in results) / (n * len(AXES))
    t_all = sum(sum(r["teacher"][a] for a in AXES) for r in results) / (n * len(AXES))
    summary["overall"] = {"student": round(s_all, 2), "teacher": round(t_all, 2),
                          "ratio_pct": round(100 * s_all / t_all, 1)}

    Path(args.out).parent.mkdir(exist_ok=True)
    Path(args.out).write_text(json.dumps({"summary": summary, "results": results}, indent=1))
    print(json.dumps(summary, indent=1))
    print(f"\nHEADLINE: student reaches {summary['overall']['ratio_pct']}% of "
          f"Claude Opus 4.7 teacher quality (n={n}, blind judge)")


if __name__ == "__main__":
    main()

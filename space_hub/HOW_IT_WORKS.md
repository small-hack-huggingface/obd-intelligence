# How it works

```
[Car OBD-II port] → [$20 ELM327 dongle] → [python-OBD @ 1 Hz]
        → [5-min rolling window: mean / std / slope per PID]
        → [XGBoost fault predictor — 1.4 MB, 3 ms]
        → [prompt: sensors + fault probabilities + repair-economics card]
        → [Gemma 4 E2B fine-tune via llama.cpp — fully local]
        → plain-English diagnosis, cheapest fix first, upsell traps named
```

This Space replays **real OBD-II recordings** from a 2014 sedan (the dongle can't
reach a car from a datacenter); on a phone or laptop the same pipeline reads the
dongle live. **No API is called at inference time** — the demo you're using runs
on a plain CPU.

## The two models

**Fault predictor** — XGBoost over windowed features (mean/std/slope/min/max of 16
PIDs + context). 22 fault classes. 99.1% top-1 / 100% top-3 on held-out sessions
of the synthetic benchmark. 1.4 MB.

**Explainer** — `google/gemma-4-E2B-it`, LoRA fine-tuned (r=16) on **4,365
diagnostic explanations distilled from Claude Opus 4.7**, with a persona that
quotes sensor evidence, orders fixes cheapest-first, and names the exact upsell
trap a shop would attach to each fault. Runs through llama.cpp.

## Benchmark — blind judge, n=100 held-out cases

Claude Opus 4.7 (the teacher) judged student and teacher answers blind, in
randomized order, on four axes (1–10):

| Axis | Student (Q8_0, 4.6 GB) | Teacher (Opus 4.7) | Ratio |
|---|---|---|---|
| Faithfulness to sensor data | 7.14 | 9.04 | 79.0% |
| Helpfulness | 7.41 | 9.07 | 81.7% |
| Cost accuracy | 7.13 | 8.78 | 81.2% |
| Anti-ripoff value | 7.59 | 9.13 | 83.1% |
| **Overall** | **7.32** | **9.01** | **81.3%** |

The 3.2 GB Q4_K_M phone variant scores 75.3% (n=40). Per-call cost: **$0** vs
~$0.07 for the teacher via API.

Two inference-time tricks bought +9 points over the naive setup, no retraining:
injecting a per-fault **repair-economics reference card** into the prompt (+6,
biggest gains exactly on cost-accuracy and anti-ripoff), and serving Q8_0 instead
of Q4_K_M (+5).

## Data

- **Real**: ~32 min of OBD-II logs from a real 2014 sedan (rpm, speed, coolant,
  load, throttle, intake temp @ 2 Hz).
- **Synthetic**: real drive windows as carrier signals; the remaining PIDs (fuel
  trims, MAF, MAP, O2, system voltage, catalyst temp...) derived with physical
  couplings; 22 fault signatures injected at 3 severities following their
  documented OBD patterns (e.g. vacuum leak = positive trims at idle + low MAF +
  high idle rpm). 550 sessions / 165k rows.
- **Distilled**: 4,365 (sensor window → mechanic explanation) pairs from Claude
  Opus 4.7, generated via the Batch API with a fault-economics system prompt.

## Honest limitations

- Fault detection is benchmarked on **synthetic faults with clean signatures**;
  real-world accuracy will be lower and per-car baselines matter. The
  architecture (deltas from a per-vehicle baseline) is designed for that, but we
  did not break a real car 22 ways to prove it.
- The benchmark judge is the same model family as the teacher (self-preference
  risk); blind randomized presentation mitigates but doesn't eliminate it.
- Repair costs are US-typical 4-cylinder sedan economics.

## Run it yourself

The exact GGUF this Space serves:
`MindFreakGamer/gemma-4-E2B-pocket-mechanic-GGUF` — load it with llama.cpp,
llama.rn (React Native), or llama_cpp_dart (Flutter). On an M4 Pro MacBook it
streams at ~70 tok/s; flagship phones run the Q4 variant.

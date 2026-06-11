---
title: Pocket Mechanic
emoji: 🔧
colorFrom: yellow
colorTo: red
sdk: gradio
app_file: app.py
pinned: false
license: mit
short_description: A mechanic in your pocket who can't be gaslit. Fully local.
---

# 🔧 Pocket Mechanic

**Backyard AI track — Build Small Hackathon.**

Turns a $20 OBD-II dongle into a mechanic in your pocket:

- **1.4 MB XGBoost predictor** reads 5 minutes of standard OBD-II PIDs and outputs
  calibrated probabilities over 22 fault classes (99.1% top-1 on held-out sessions).
- **Gemma 4 E2B**, LoRA fine-tuned on 4,365 diagnostic explanations distilled from
  Claude Opus 4.7, explains the fault in plain English — cheapest fix first, with the
  exact upsell traps shops use for that fault.
- Runs through **llama.cpp** (Q4_K_M GGUF). The same artifact loads on a phone via
  llama.rn / llama_cpp_dart — no internet, no subscription, $0 per diagnosis.

Drive scenarios are replayed from real OBD-II recordings of a 2014 sedan with
physically-modeled fault injection (vacuum leaks, misfires, failing alternators...).

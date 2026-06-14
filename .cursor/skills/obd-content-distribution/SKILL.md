---
name: obd-content-distribution
description: >-
  Enforces the automotive content taxonomy when generating questions, training
  examples, RAG chunks, or classifying documents. Use when creating Q&A pairs,
  labeling sessions, chunking docs, balancing a corpus, or when the user mentions
  content distribution, training mix, or question generation for this project.
---

# OBD content distribution

When generating or classifying **any content corpus** for this project, use these **three categories**:

| Category | Id |
|----------|-----|
| Automotive fundamentals | `automotive_fundamentals` |
| Automotive diagnostics | `automotive_diagnostics` |
| Other automotive information | `other_automotive_information` |

## Category definitions

### Automotive fundamentals

Core concepts: PIDs, DTCs, encoding, units, OBD modes, Toyota ECU headers, trim interpretation, healthy baselines, normal operating ranges.

**Sources:** [docs/pid_definitions.md](../../../docs/pid_definitions.md), [docs/toyota_pid_definitions.md](../../../docs/toyota_pid_definitions.md), [docs/toyota_dtc_definitions.md](../../../docs/toyota_dtc_definitions.md), [docs/emulator_car_queries.md](../../../docs/emulator_car_queries.md) (baseline values)

### Automotive diagnostics

Fault signatures, typical DTCs, causal reasoning, diagnostic trees, fault simulation, distinguishing similar faults, multi-signal inference.

**Sources:** [docs/fault_profiles.md](../../../docs/fault_profiles.md), [docs/fault_simulation.md](../../../docs/fault_simulation.md)

### Other automotive information

Automotive-related content that is not fundamentals or diagnostics: emulator setup, test commands, project architecture, tooling, workflows, conversation-style Q&A, misc reference.

**Sources:** [docs/test_commands.md](../../../docs/test_commands.md), [README.md](../../../README.md)

## Application rules

1. Every chunk or item gets **exactly one** category.
2. Prefer **automotive_diagnostics** when the text is mainly about faults, codes, or troubleshooting.
3. Prefer **automotive_fundamentals** when the text defines terms, units, or normal behavior.
4. Use **other_automotive_information** for setup, meta, or mixed content that does not fit the two above.

Chunk classification script: [modal_files/obd_chunk_classifier.py](../../../modal_files/obd_chunk_classifier.py) — reads `data_consideration/*.md`, outputs `{category}.jsonl` under `classified_chunks/`.

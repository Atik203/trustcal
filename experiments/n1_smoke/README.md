# N1.0 — 18 GB test-only smoke

**Status:** PASS for one real 8–9B model + two mocks. No cloud spend.
**Date:** 18 November 2026
**Host:** `uiu-h200`, H200 MIG `1g.18gb`, 18 GB, driver `580.178.04`, CUDA `13.5`
**Project directory:** `~/trustcal-fydp/` (dedicated; `tool-observation/` untouched)

## Objective

Finalize the trustcal client, prompt, parser, record schema, and serving flags on the free 18 GB slice before renting cloud GPUs. This is **test-only**; it is not a confirmatory result.

## Environment

| Item | Value |
|---|---|
| vLLM | 0.33.0, existing `tool-observation` venv used **read-only** |
| HF cache | existing cache, shared read-only; `HF_HUB_OFFLINE=1` |
| Model | `cyankiwi/Qwen3.5-9B-AWQ-4bit`, revision `e4d2d39cede8c5d1716d824cd843e2889c648083` |
| Served alias | `QuantTrio/Qwen3.5-9B-AWQ` |
| Context | 4,096 tokens |
| GPU utilization | 0.85 |
| Quantization | `compressed-tensors` |
| Reasoning | disabled with `--reasoning-parser qwen3` and `--default-chat-template-kwargs '{"enable_thinking": false}'` |
| Mocks | `scripts/mock_vllm.py --ports 8001,8002 --mode divergent` |
| Client | existing project venv, read-only; no system packages installed |

## Commands

```bash
# One real model on 8000; two mocks on 8001/8002.
# The server command is stored in results/n1_smoke/serve_qwen.sh (gitignored).
cd ~/trustcal-fydp
bash results/n1_smoke/serve_qwen.sh > logs/vllm-qwen.log 2>&1

cd ~/trustcal-fydp/trustcal
~/tool-observation/.venv/bin/python scripts/mock_vllm.py \
  --ports 8001,8002 --mode divergent > ../logs/mocks.log 2>&1

~/tool-observation/.venv/bin/python scripts/run_experiment.py \
  --arm B3 \
  --questions-file ../results/n1_smoke/questions.json \
  --limit 1 --seed 1 \
  --out ../results/n1_smoke/run
```

## Result

- One question: `n1-1` — “What is the chemical symbol for water?” with options `H2O`, `CO2`, `NaCl`, `O2`.
- One B3 debate, 3 rounds, 26.3 s.
- Final answer: `B` (rendered option for `H2O`), correct.
- Accuracy: **1.000** (1/1 scored).
- MPR: **1.000** (1 divergent debate).
- CCR: **0.000** (0/0 exposed agents; no pressure item).
- Record schema: **valid**, 1 record, 0 validation errors.
- `trust_for_positions`: null because B3 is vanilla MAD; expected.
- GPU during run: **13,880 MiB used**, 18,432 MiB total.
- After stopping servers: GPU idle, 1 MiB used.

Raw artifacts are local and gitignored under:

```text
trustcal/results/n1_smoke/run/B3/gpqa/seed1/
```

## Issues found and fixes

1. **Offline cache had no `refs/main`.** `HF_HUB_OFFLINE=1` failed until the server was started with the exact cached revision:
   `--revision e4d2d39cede8c5d1716d824cd843e2889c648083`.
2. **Thinking block was enabled.** The first completion returned `Thinking Process...`; fixed with `--reasoning-parser qwen3` and `--default-chat-template-kwargs '{"enable_thinking": false}'`.
3. **`python3 -m venv` is unavailable** on the host (`ensurepip` missing). No system package was installed. The existing `tool-observation` venv was used read-only for this first smoke; a dedicated project env remains a later setup item.
4. **Mock script path:** it lives at `trustcal/scripts/mock_vllm.py`, not the repo root.

## What this proves

- The real Qwen3.5-9B AWQ model loads on 18 GB at 4k context.
- The trustcal client, prompt template, option rendering, parser, 3-round loop, manifest, summary, and record schema work with one real model and two mocks.
- Qwen3.5 needs thinking disabled for the 1,024-token output budget; the config flag works.

## What this does not prove

- Three real models concurrently.
- The main 27B AWQ or FP8 stacks.
- Retrieval/verifier behavior under a live retrieval run.
- Any efficacy result.

## Next

1. Repeat the one-real-model + two-mock smoke with Ministral-8B and Llama-3.1-8B.
2. Test Qwen3.8-27B Q4_K_M with llama.cpp at 4k context for the main-template/parser path (test-only).
3. Freeze the test commands and hashes; then run the 4-bit 80 GB cloud smoke (N1a).

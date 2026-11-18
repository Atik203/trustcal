# N1.0 — 18 GB test-only smoke

**Status:** PASS for the 8–9B vLLM trio and the Q4_K_M main-model templates. No cloud spend.
**Date:** 18 November 2026
**Host:** `uiu-h200`, H200 MIG `1g.18gb`, 18 GB, driver `580.178.04`, CUDA `13.5`
**Project directory:** `~/trustcal-fydp/` (dedicated; `tool-observation/` untouched)

## Objective

Finalize the trustcal client, prompt, parser, record schema, and serving flags on the free 18 GB slice before renting cloud GPUs. This is **test-only**; it is not a confirmatory result.

## Environment

| Item | Value |
|---|---|
| 8–9B serving | vLLM 0.33.0, existing `tool-observation` venv used **read-only** |
| GGUF serving | llama.cpp `b12521`, CUDA 12.8 prebuilt in `tools/llama.cpp/cuda12` |
| HF cache | existing cache, shared read-only; `HF_HUB_OFFLINE=1` |
| Served alias | `QuantTrio/Qwen3.5-9B-AWQ` (test alias for the client) |
| Context | 4,096 tokens |
| GPU utilization | 0.85 for vLLM; `-ngl 99` for llama.cpp |
| Mocks | `scripts/mock_vllm.py --ports 8001,8002 --mode divergent` |

### Models

| Model | Quant | Size | Serving |
|---|---|---:|---|
| Qwen3.5-9B | AWQ / compressed-tensors | 8.37 GiB | vLLM |
| Ministral-3-8B | AWQ / compressed-tensors | 7.03 GiB | vLLM |
| Llama-3.1-8B | AWQ | 5.58 GiB | vLLM |
| Qwen3.8-27B | Q4_K_M | 15.43 GiB | llama.cpp |
| Gemma 4 26B-A4B | Q4_K_M | 15.78 GiB | llama.cpp + `-cmoe` |
| Mistral 24B | Q4_K_M | 13.35 GiB | llama.cpp |

## Commands

```bash
# One real model on 8000; two mocks on 8001/8002.
# Server scripts are test artifacts under results/n1_smoke/ (gitignored).
cd ~/trustcal-fydp
bash results/n1_smoke/serve_qwen.sh > logs/vllm-qwen.log 2>&1
# For Ministral/Llama: serve_model.sh with MODEL/REVISION/ALIAS/QUANT.
# For GGUF: serve_gguf.sh with MODEL_FILE; Gemma uses serve_gemma.sh (-cmoe).

cd ~/trustcal-fydp/trustcal
~/tool-observation/.venv/bin/python scripts/mock_vllm.py \
  --ports 8001,8002 --mode divergent > ../logs/mocks.log 2>&1

~/tool-observation/.venv/bin/python scripts/run_experiment.py \
  --arm B3 \
  --questions-file ../results/n1_smoke/questions.json \
  --limit 1 --seed 1 \
  --out ../results/n1_smoke/run_<model>
```

## Results

One question: `n1-1` — “What is the chemical symbol for water?” with options `H2O`, `CO2`, `NaCl`, `O2`. Each row is one real model + two mocks, one B3 debate, three rounds.

### 8–9B vLLM

| Real model | Time | GPU peak | Final | Schema |
|---|---:|---:|---|---|
| Qwen3.5-9B | 26.3 s | 13,880 MiB | `B` (`H2O`), correct | valid |
| Ministral-3-8B | 37.5 s | 15,461 MiB | `B` (`H2O`), correct | valid |
| Llama-3.1-8B | 27.2 s | 15,666 MiB | `B` (`H2O`), correct | valid |

### Q4_K_M main templates (llama.cpp)

| Real model | Time | GPU peak | Final | Schema |
|---|---:|---:|---|---|
| Qwen3.8-27B | 145.8 s | 15,796 MiB | `B` (`H2O`), correct | valid |
| Gemma 4 26B-A4B | 58.9 s | 3,384 MiB | `B` (`H2O`), correct | valid |
| Mistral 24B | 74.6 s | 14,018 MiB | `B` (`H2O`), correct | valid |

All six: accuracy **1.000** (1/1), MPR **1.000**, CCR **0.000** (0/0 exposed; no pressure item), 3 rounds, 0 validation errors. `trust_for_positions` is null because B3 is vanilla MAD; expected.

Gemma’s GPU peak is low because `-cmoe` keeps the MoE expert weights on CPU (125 GB RAM). It is a test-only configuration.

After stopping servers: GPU idle, 1 MiB used.

## Issues found and fixes

1. **Offline cache had no `refs/main`.** `HF_HUB_OFFLINE=1` failed until the vLLM server was started with the exact cached revision.
2. **Thinking block was enabled.** Qwen3.5 returned `Thinking Process...`; fixed with `--reasoning-parser qwen3` and `--default-chat-template-kwargs '{"enable_thinking": false}'`.
3. **`python3 -m venv` is unavailable** on the host (`ensurepip` missing). No system package was installed. The existing `tool-observation` venv was used read-only; a dedicated project env remains a later setup item.
4. **Mock script path:** it lives at `trustcal/scripts/mock_vllm.py`, not the repo root.
5. **llama.cpp CUDA 13.5 prebuilt failed** with `CUDA error: the provided PTX was compiled with an unsupported toolchain`. The CUDA 12.8 build works with driver `580.178.04`; it is installed under `tools/llama.cpp/cuda12`.
6. **Gemma Q4_K_M OOM at `-ngl 99`.** The full model needs about 16.1 GiB. Fixed with `-cmoe`, which keeps MoE experts on CPU; GPU peak drops to 3,384 MiB.

## What this proves

- The three cached 8–9B AWQ families load on 18 GB at 4k context, one at a time.
- The three main-model Q4_K_M templates load and run one at a time, including the 27B Qwen template.
- The trustcal client, prompt template, option rendering, parser, 3-round loop, manifest, summary, and record schema work with each real model and two mocks.
- The 18 GB slice can test the main-model template/parser path without downloading cloud test artifacts.

## What this does not prove

- Three real models concurrently.
- The main AWQ or FP8 stacks.
- Retrieval/verifier behavior under a live retrieval run.
- Any efficacy result.

## Artifacts

Raw runs are local and gitignored under:

```text
trustcal/results/n1_smoke/run_vllm/
trustcal/results/n1_smoke/run_qwen_gguf/
trustcal/results/n1_smoke/run_gemma_gguf/
trustcal/results/n1_smoke/run_mistral_gguf/
```

## Next

1. Freeze the test commands and hashes.
2. Run the 4-bit 80 GB cloud smoke (N1a).
3. Do not run the 96 GB FP8 smoke until after the 4-bit pilot/Core.

# Decisions

Approved architecture, hardware, and environment decisions. Add an entry before confirmatory work when a decision changes the compute path, driver, CUDA version, or serving environment.

## 2026-11-19 - Pinned vLLM 0.34.0 and config-only stack validation

**Status:** approved.

**Decision:** the `fourbit` and `final` phases use **vLLM 0.34.0** from PyPI, not a nightly wheel. That release already contains `Qwen3_5ForConditionalGeneration`, `Gemma4ForConditionalGeneration`, `Gemma4UnifiedForConditionalGeneration`, `Mistral3ForConditionalGeneration`, and the `qwen3` reasoning parser. `VLLM_NIGHTLY=1` remains a fallback only.

**Dependency alignment:** `huggingface_hub>=2.0,<3.0`, `transformers>=5.16.1,<5.23.0`, `datasets>=3.6,<6.0`, `sentence-transformers>=6.0,<7.0`. vLLM 0.34.0 pins `torch==2.14.0` and requires hub 2.x; the old `hub<2.0` / `transformers<5.17` pins were for vLLM 0.29.x and would either conflict or silently drift under `-U`.

**Pre-download gate:** `setup.sh` runs `scripts/validate_stack.py --phase "$PHASE" --download-configs` after installing vLLM and before downloading weights. It checks architecture registration, quantization method vs. serve flag, every serve flag, the reasoning-parser name, the context window, and the checkpoint chat template using config/tokenizer files only (a few MB). A mismatch stops the session before 53GB of ingress.

**Why:** a paid session must not depend on the day's nightly wheel or discover an incompatible checkpoint after the A100 clock starts. The 18GB slice is used to validate the same script on the exact checkpoint configs before the cloud run.

## 2026-11-19 - Triton JIT needs Python.h on minimal images

**Status:** approved.

**Finding:** vLLM 0.34.0 starts, loads the checkpoint, then fails during `determine_available_memory` with `subprocess.CalledProcessError` from Triton's `driver.c` compile. The host has no `/usr/include/python3.12/Python.h`; the compiler error is hidden by Triton's `stdout=DEVNULL`.

**Decision:** `scripts/python_headers.sh` resolves the interpreter's include directory, prepends it to `CPATH`, and if the headers are missing uses a user-local `uv python install` (no sudo) to obtain matching headers. `setup.sh` calls it before validation/download; `serve.sh` calls it before launching vLLM. If neither source works, both stop with a clear message instead of a cryptic engine-init failure.

**Why:** this failure happens after the model is loaded, so on a paid host it burns setup time and looks like a model problem. The check is cheap and runs before the 53GB download.

## 2026-11-19 - Retrieval reranking defaults to lexical

**Status:** approved.

**Finding:** `Retriever.retrieve()` called `verdicts.rerank()` without a scorer. `rerank()` tries `sentence-transformers` first, so a runner process on the same GPU as the three vLLM servers loaded `cross-encoder/ms-marco-MiniLM-L-6-v2` (105 weight tensors) and competed with the served models. On the 18 GB slice this produced CUDA OOM warnings during the Qwen3.8-27B B8 test; on the 80 GB matrix stack it would eat into the 8 GB non-vLLM headroom.

**Decision:** `RetrievalConfig.rerank` defaults to `"lexical"` and passes an explicit lexical scorer into `rerank()`. `"cross-encoder"` and `"auto"` remain available for an intentional ablation. The lexical verifier already forced its own scorer; this makes the retriever match it and keeps the serving GPU for vLLM.

**Why:** the pre-registered matrix declares the lexical verifier; a hidden cross-encoder changes passage ranking and adds GPU memory/latency that the cost model does not include.

## 2026-11-19 - Retrieval source circuit breaker

**Status:** approved.

**Decision:** `RetrievalConfig.max_source_failures` defaults to 3. After three consecutive failures of one keyless source (PubMed, arXiv, Semantic Scholar, OpenAlex), the retriever skips that source for the rest of the run and records it in `routes.json` errors. A success resets the counter.

**Why:** `sources._get_with_retry` can spend ~60s per failed query (20s timeout x 3 attempts). A dead Semantic Scholar endpoint could add tens of minutes to every B8/B4 debate, which is a direct GPU-cost risk. The breaker changes nothing when the APIs are healthy; when a source is already failing, the run records the degradation instead of silently paying for retries.

## 2026-11-18 - Dedicated trustcal directory and $50 test-first tranche

**Status:** approved.

**Decision:** use a dedicated `trustcal-fydp/` project directory on the university server. Do not work inside or modify the existing `tool-observation/` project, its venv, or its configs. Share the Hugging Face cache read-only.

**18 GB test stack:**

- 8–9B AWQ with vLLM, one model at a time, 4k context: Qwen3.5-9B (8.37 GiB), Ministral-8B (7.03 GiB), Llama-3.1-8B (5.58 GiB).
- Q4_K_M main templates with llama.cpp at 4k context, q8 KV, one model at a time: Qwen3.8-27B Q4_K_M (15.43 GB; Q4_0 14.95 GB or Q3_K_M 12.48 GB if tight), Gemma 4 26B Q4_K_M (15.78 GB), Mistral 24B Q4_K_M (13.35 GB).
- GGUF serving uses the **llama.cpp b12521 CUDA 12.8** prebuilt. The CUDA 13.5 prebuilt fails with `PTX was compiled with an unsupported toolchain` on driver `580.178.04`. Gemma Q4_K_M needs `-cmoe` (MoE experts on CPU); GPU peak drops to ~3.4 GiB.
- Offload a few layers to the 125 GB system RAM only if a Q4_K_M model is tight. This is test-only, not the AWQ/FP8 stack.

**Bandwidth:** download Q4_K_M test files on the university host, one at a time, and keep the project under 200 GB. Do not download them on a cloud host. The cloud host downloads only the final AWQ/FP8 stack.

**$50 tranche:** spend on the 4-bit smoke (~$1–2) and pilot (~$15–20) first. Optionally add one 96 GB 5-question smoke (~$2–8) after the pilot is stable. Keep $20–30 for retries and bandwidth. Do not run a 96 GB pilot (~$37–45 at the retired rate), the FP8 precision replication (~$25–40 at $0.336/h; ≈ $90–150 at the measured $1.50/h), or the Core/Full matrices (Core ≈ $62 remaining; Core + Full ≈ $104) from this tranche.

> **Update (24 Nov 2026):** the rate basis is now the measured **$1.50/GPU-h all-in** at 172.7 debates/h on a 96 GB card. The $0.136/$0.336 spot figures and the $175–235 Core/Full estimates in this entry are the retired 9 November basis; the $50 tranche itself is unchanged.

**Why:** the 18 GB tests are free and prevent paid cloud debugging; the 96 GB FP8 path is a secondary precision check, not the main 4-bit result (the 4-bit matrix now runs on the same 96 GB class card). The first $50 should buy a clean 4-bit smoke and pilot, not a dedicated precision host.

## 2026-11-14 — Dev-slice validation before cloud runs

**Status:** approved.

**Decision:** use the 18 GB `uiu-h200` slice for single-model development checks before paying for cloud GPU time. Run one dev model at a time; use `mock_vllm.py` for the three-agent flow. Finalize prompts, parser, answer rendering, serving flags, manifest/resume, and the retrieval/verifier path before the cloud smoke.

**What it can validate:** each dev model loads; the chat template and output format work; the parser and option renderer work; one real agent can run against two mock agents; the retrieval/verifier path works; configs, hashes, and resume logic are stable.

**What it cannot validate:** three real models at once, KV-cache pressure on the final stack, FP8 serving, final-model behavior, or the cloud hardware-smoke gate.

**Expected effect:** the matrix GPU-hours do not change; the free slice reduces avoidable cloud debugging and retry overhead. Planning offset is **$20–50 direct**, with additional risk avoidance if it prevents a failed Core/Full rerun. The **$600** hard stop remains; the old **$500–600** planning range is superseded by the measured **≈ $104** Core + Full (172.7 debates/h at $1.50/GPU-h all-in, 24 Nov 2026).

## 2026-11-14 — University H200 MIG access

**Status:** approved for development and interface checks only; not approved for the confirmatory matrix.

**Hardware:** H200 MIG `1g.18gb`, 18 GB VRAM, driver `580.178.04`, CUDA `13.5`.

**Access:** SSH through the local alias `uiu-h200` only. Do not expose ports or create another connection method.

**Decision:** use the slice for single small-model interface, prompt, parser, and retrieval checks. Do not schedule the 24-row Core matrix, the 32/36-row Full matrix, the three-model smoke, or the FP8 precision replication on it.

**Why:** the approved stacks do not fit in 18 GB:

| Stack | Weights | Fits 18 GB? |
| --- | ---: | --- |
| `fourbit` main matrix | 53.26 GB | No |
| `final` FP8 precision | 73.68 GB | No |
| `dev` three-model trio | ~25 GB | No |
| Single Qwen3.8-27B-AWQ-INT4 | 21.0 GB | No, before KV cache |
| Single Gemma 4 26B-A4B AWQ | 17.2 GB | No practical headroom for KV cache |
| Single Mistral 24B AWQ | 15.06 GB | One server only; not the three-agent design |

**Consequences:** the planned Core/Full and precision runs still require the approved rental paths in `docs/agent/08_COMPUTE_COST.md`. The measured default is now a 96 GB class card at $1.50/GPU-h all-in (172.7 debates/h); the 80 GB A100 at $0.136/GPU-h in that file is the retired 9 November spot basis. The university slice does not change the budget, the matrix, or the hardware-smoke gate.

**Rules:** no changes to clocks, power limits, MIG settings, the SSH daemon, host keys, the account name, the login method, or other users' `authorized_keys`; no system-wide packages or `sudo` without administrator approval; keep storage under 200 GB; use `tmux` or `screen`; stop idle jobs; never commit a server address, hostname, username, account ID, password, SSH key, or host fingerprint.

**Allowed identifiers:** `uiu-h200`, `H200 1g.18gb`, driver `580.178.04`, CUDA `13.5`.

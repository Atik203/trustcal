# trustcal — agent instructions (GPU pipeline)

Canonical agent instructions for this directory: the P0-released implementation (vLLM serving + multi-agent debate). Read with the repo-root `AGENTS.md`. Phase status lives in `../roadmap.md`; design in `../docs/blueprint.md`. Keep this file static — no dates, no run status.

## Golden rules

- **vLLM owns the GPU.** `scripts/serve.sh` is the only GPU-touching file; everything else is plain Python over the OpenAI-compatible APIs at `127.0.0.1:8000-8002`. Use `127.0.0.1`, never `localhost`: the Windows IPv6 fallback costs about 2s per request.
- **`configs/models.yaml` is the only model switch** (Dev ↔ Four-bit ↔ Final). Serve commands are generated from it by `scripts/gen_serve_cmds.py` — never hand-edit commands into `serve.sh`, and never rename a served model (`--served-model-name` mismatches caused request 404s in an earlier draft).
- **Order discipline (blueprint §13 / roadmap):** 18 GB test gate → 4-bit smoke → pilot → Core matrix → 96 GB FP8 smoke/precision → Full matrix. Never run a matrix before the pilot. The Core matrix is four conditions × 3 datasets × 2 seeds = 24 rows; the six-arm Full target is a separate later design. The 96 GB smoke is not a gate for the 4-bit Full matrix. On the 4-bit path the pilot can be the **Core prefix** (first 25–50 questions of the actual B8 and B8-no-trust rows, `--limit 400 --stop-after N`) instead of a separate 100–150-question run; that substitution needs a signed amendment, and the prefix is resumed as part of Core only if it passes.
- **The Core matrix source is `configs/experiments_fourbit.yaml`**, not `configs/datasets.yaml`. `datasets.yaml` carries dataset revisions/provenance and loader defaults; its `seeds` and `sample_caps` are not the matrix values. `configs/experiments.yaml` is the released historical Core config. Do not add the six-arm target to it; WP-18 added a separate `configs/experiments_full.yaml`.
- **`results/` is gitignored and load-bearing** (Gate 0 logs, trust trajectories, matrix summaries). Copy artifacts off the box before destroying an instance.
- **Never commit secrets.** `.env` is gitignored. `HF_TOKEN` (gated GPQA/HLE downloads), `OPENAI_API_KEY` (B7), and the optional retrieval keys come from the environment or `.env`; never paste a real key into a doc or a commit.

## Layout

| Path | Owns |
| --- | --- |
| `configs/models.yaml` | agent → checkpoint, port, quant, VRAM split, per-agent flags, Final pins |
| `configs/phase.yaml` | default phase (`dev`, `fourbit`, or `final`) when a CLI does not pass `--phase` |
| `configs/experiments.yaml` | released Core matrix: 4 conditions × 3 datasets × 2 seeds |
| `configs/experiments_full.yaml` | six-arm Full matrix; 32-row gold-evidence default / 36-row gold-answer alternate |
| `configs/datasets.yaml` | dataset revisions, splits, provenance, loader seeds/caps (not the matrix) |
| `src/trustcal/inference/` | OpenAI-compatible client, one per port; retries transient failures only |
| `src/trustcal/agents/` | prompts (`AGENT_SYSTEM`, initial/revision, injection, `trust_line`) + claim parser (+ fallback) |
| `src/trustcal/orchestrator/` | debate loop (`DebateRunner`) + injection plan (`injection.py`) + baseline strategies (`strategies.py`) |
| `src/trustcal/trust/` | pure trust math (logit accumulation → softmax → floor/ceiling simplex projection; claim-count normalized) + aggregation + `TrustState`/`TrustConfig` |
| `src/trustcal/retrieval/` | PubMed/arXiv/S2 clients, progressive retriever, verifier, reranker/verdicts |
| `src/trustcal/eval/` | datasets, answers, CCR/MPR/ECR, baselines, stats, failures, pilot, oracle, annotation/κ |
| `src/trustcal/runner.py` | resumable experiment runner (JSONL per question, metrics, summary) |
| `src/trustcal/mock_vllm.py` | stdlib mock servers for GPU-free end-to-end tests |
| `src/trustcal/preflight.py` | cost-safety checks (servers, cache, disk, context, keys) |
| `scripts/gen_serve_cmds.py` | prints `vllm serve` commands from `models.yaml` |
| `scripts/serve.sh` | launches the three servers; `DRY_RUN=1` prints commands |
| `scripts/install_vllm.sh` | pinned vLLM 0.34.0 (Gemma 4 / Gemma 4 Unified / Qwen3.5 / Mistral3 are in stable); `VLLM_NIGHTLY=1` is the fallback |
| `scripts/validate_stack.py` | config-only pre-download gate: architecture, quant method, serve flags, reasoning parser, context, chat template |
| `scripts/repro_mad.py` | Gate 0; writes `results/gate0/transcript-*.json` + `summary-*.md` |
| `scripts/run_experiment.py` | runs an arm (`B1`–`B10`, `pilot`, `injection`); resume + summary |
| `scripts/run_matrix.py` | conditions × datasets × seeds matrix; `--config` selects Core or Full YAML |
| `scripts/p0_gate.py` | 13-check P0 engineering gate; exits non-zero on any failure |
| `scripts/check_stack.py` | offline Final-stack weight/VRAM budget check; not a hardware proof |
| `scripts/preflight.py` | CLI for the preflight checks; `--phase final --offline` before a Final run |
| `scripts/mock_vllm.py` | CLI for the mock servers (local end-to-end runs) |
| `scripts/annotate.py` | annotation sheets + Cohen's κ for the injection gate |
| `scripts/pilot_report.py` | Month-1 PASS/AMBIGUOUS/NO-GO report |
| `scripts/analyze.py` | pooled metrics, failure taxonomy, pilot, ECR |
| `scripts/human_eval.py` | Phase 4 blinded Likert sheets + κ |
| `scripts/smoke_test.py` | model-swap smoke test; supports dev/fourbit/final phases and B8/injection/placebo/oracle paths |
| `scripts/verify_env.py` | imports/versions + `--check-servers` health gate |
| `scripts/verifier_audit.py` | verifier audit sheets + balanced accuracy/κ |

## Arms and matrix

The released Core matrix runs four conditions:

| Condition | Arm | Role |
| --- | --- | --- |
| `B3` | B3 | vanilla MAD, no retrieval |
| `B4-matched` | B4 | MAD + RAG with the same source partition as B8 (evidence control) |
| `B8-no-trust` | B8 (`use_trust: false`) | primary control; same retriever/prompts/partition as B8, majority aggregation |
| `B8` | B8 | treatment; evidence-grounded trust during debate |

The **six-arm target** adds `B8-placebo` (cross-agent round-pool verdict shuffle, trust-weighted) and `B8-oracle` (gold-evidence oracle on SciClaimBench, or gold-answer trust in the 36-row alternate). It is **not** in `experiments.yaml`. WP-18 implemented the `placebo_mode` / `oracle_mode` flags, the separate Full config, and the frozen definitions of the placebo shuffle unit/seed and the oracle semantics. `B7` is an optional 3-sample GPT-6 Luna external-answer ceiling, not `B8-oracle`. The B1-B10 appendix grid stays out of the pre-registered matrix.

`python scripts/run_matrix.py --config configs/experiments_fourbit.yaml --dry-run` shows the 24 Core rows on the 4-bit stack. `python scripts/run_matrix.py --config configs/experiments_full.yaml --dry-run` now runs offline plan validation first: the Full config names `sciclaim_180`, which has no loader entry in `eval/datasets.py` or `configs/datasets.yaml`, so it fails before a row is planned. Add the frozen v1.2 SciClaimBench dataset entry before any Full run. `configs/experiments_precision.yaml` is the 3-row GPQA FP8 precision replication. The Core matrix's gate cap stays 1,280 GPU-h.

**Core → Full reuse is not executable yet.** A run row can be reused only when `dataset`, `limit`, `seed`, `phase`, every trust/retrieval flag, and the sample seed are identical (they are all in the manifest hash). Core uses `gpqa_main` 400 / `mmlu_pro` 400 / `hle` 200; Full uses `gpqa_main` 300 / `mmlu_pro` 300 / `sciclaim_180` 300. Nothing matches. A 300-item Full sample is not a subset of the 400-item Core sample: stratified allocations differ, question ids shift, and the manifest includes `limit`. Reuse requires a signed **v1.5** amendment setting Full `gpqa_main: 400`, `mmlu_pro: 400`, `sciclaim_180: 300`, plus the SciClaimBench loader and a new config hash. (v1.4 is already the frozen B7-provider erratum.) The current v1.3 draft says 300/dataset and does not assume reuse; do not budget the saving before v1.5.

## Dev stack (RTX A6000 48GB) — retired

The 9-14B dev checks were for interface work on the small slice; both runnable
phases are now tested, so `models.yaml` no longer carries a dev block and
`PHASES` is `("fourbit", "final")`. `--phase dev` raises a clear error rather than
serving a third, untested stack. Historical checkpoint notes: the official
Ministral FP8 checkpoint cannot run on Ampere (W8A8 sm80 kernel fails), so the
dev tier used 4-bit AWQ/QAT artifacts. Pinned vLLM 0.34.0 is the default
(`VLLM_NIGHTLY=1` is the fallback); `install_vllm.sh` auto-detects the wheel index
from the driver (≥580 → cu130, else cu129).

## 4-bit matrix stack (RTX A100 80GB)

`models.yaml` pins Qwen3.8-27B-AWQ-INT4 (21.0GB), Gemma-4-26B-A4B AWQ (17.2GB), and Mistral-24B-AWQ (15.06GB) at **53.26GB** total weights, with a 0.90 utilization sum and 8192-token context. This is the main Core/Full matrix stack. The offline check is:

```bash
python scripts/check_stack.py --phase fourbit
python scripts/validate_stack.py --phase fourbit --offline   # after setup.sh downloaded configs
```

The Mistral checkpoint is named `awq-sym` but its config says `quant_method: compressed-tensors`; `models.yaml` sets that explicitly. Gemma 4 26B A4B is text+image, so its MM limit is `{"image": 0}` (no `audio` key); Mistral gets the same limit. `setup.sh` runs `validate_stack.py` before the weight download, so an architecture/flag mismatch stops the session before 53GB of ingress.

**Serving flags differ by phase.** `--enforce-eager` is a dev-stack guard: on 48GB the CUDA-graph capture spikes memory while three servers share the card. The 80/96GB phases keep the graphs (eager costs 20-35% of decode throughput) and add `--disable-log-requests`; `VLLM_EAGER=1` forces eager back on if a phase ever OOMs during capture. `gen_serve_cmds.py` owns this switch, so `serve.sh` never needs hand-edited flags.

Graph mode also needs a sequence cap: Qwen3.8 keeps a **Mamba hybrid cache**, and each decoding sequence consumes one Mamba block, of which the 0.33 reservation yields ~110. vLLM's graph default `max_num_seqs=1024` therefore aborts startup with `max_num_seqs (1024) exceeds available Mamba cache blocks (110)`. `--max-num-seqs 64` clears it with room for the 24 requests a fully concurrent 8-row run issues. Raise the cap only after checking that error's block count.

## Final stack (RTX PRO 6000 Blackwell 96GB)

`models.yaml` pins Qwen3.8-27B-FP8, Gemma-4-26B-A4B-FP8, and Mistral-24B-AWQ at **73.68GB** total weights, with a 0.90 utilization sum and 8192-token context. This stack is limited to the N1 smoke and the small GPQA precision replication, not the main Full matrix. The offline Final gate is:

```bash
python scripts/check_stack.py --phase final
HF_HUB_OFFLINE=1 python scripts/preflight.py --phase final --offline
```

`check_stack.py` enforces 53.26GB on the 80GB 4-bit phase and 73.68GB on the 96GB Final phase. These checks cover the config budget, cache, disk, context, and keys. They do **not** prove that vLLM loads all three checkpoints together. The 96 GB hardware smoke is a separate required gate for the FP8 precision replication:

```bash
PHASE=final bash setup.sh
python scripts/verify_env.py --check-servers
python scripts/smoke_test.py --phase final --limit 20
```

No FP8 precision replication is trusted until that hardware smoke passes and its `nvidia-smi` peak is recorded. The 4-bit main matrix has its own 5-question smoke on the 80GB A100. If a server OOMs, lower that agent's `gpu_memory_utilization` and re-run; if Mistral's `auto` quant detection fails, set `quant: compressed-tensors`.

## Commands (run from `trustcal/`)

| Command | Does |
| --- | --- |
| `HF_TOKEN=hf_... [VENV=1] bash setup.sh` | install deps + pinned vLLM 0.34.0 + validate checkpoints + download checkpoints (~31GB) + start servers + verify. `VENV=1` on any image that blocks system pip (PEP 668): Thunder Compute, Vast PyTorch images |
| `python scripts/verify_env.py --check-servers` | gate: three `server OK` lines |
| `python scripts/p0_gate.py` | 13-check P0 engineering gate; exits non-zero on any failure |
| `python scripts/check_stack.py --phase fourbit` | offline 80 GB 4-bit matrix weight/utilization check |
| `python scripts/check_stack.py --phase final` | offline 96 GB Final weight/utilization check |
| `HF_HUB_OFFLINE=1 python scripts/preflight.py --phase final --offline` | Final cost-safety gate (servers, cache, disk, context, keys) |
| `python scripts/preflight.py [--offline]` | Dev/default cost-safety gate before paid runs |
| `python scripts/run_experiment.py --arm B3 --limit 10 --seed 1` | run/resume an arm (B1-B10, pilot, injection); writes `results/<arm>/<dataset>/seed<N>/` + summary |
| `python scripts/run_experiment.py --arm injection --questions-file q.json` | injection harness; add `--questions-file` to bypass the HF dataset |
| `python scripts/run_experiment.py --arm pilot --questions-file experiments/pilot-month1/questions.json` | Month-1 trust-weight pilot |
| `python scripts/run_matrix.py --config configs/experiments_fourbit.yaml --dry-run` | print the 24-row Core plan on the 4-bit stack (2 seeds) |
| `python scripts/run_matrix.py --config configs/experiments_full.yaml --dry-run` | print the Full plan (32 rows gold-evidence; 36 rows gold-answer alternate) |
| `python scripts/run_matrix.py --config configs/experiments_precision.yaml --dry-run` | print the 3-row GPQA FP8 precision replication |
| `python scripts/pilot_report.py --dir results/pilot/<dataset>/seed1` | PASS/AMBIGUOUS/NO-GO; exit 0/2/1 |
| `python scripts/analyze.py --records results/<arm>/<dataset>/seed1/records.jsonl` | pooled CCR/MPR, failures, pilot, ECR |
| `python scripts/smoke_test.py --phase fourbit --limit 5` | 4-bit matrix smoke test (B8, injection, placebo, oracle paths) |
| `python scripts/repro_mad.py --limit 10` | Gate 0; writes `results/gate0/` |
| `python scripts/mock_vllm.py --ports 8000,8001,8002 --mode divergent` | local mock servers for GPU-free end-to-end runs |
| `python scripts/annotate.py make --records <records.jsonl>` | κ annotation sheets (then `score --rater1/--rater2`, exit 2 if κ < 0.75) |
| `bash scripts/serve.sh` | (re)start servers; logs in `results/logs/vllm-<port>.log` |
| `pytest` | GPU-free tests (trust math, parser, runner, injection, mock end-to-end) |
| `python scripts/gen_serve_cmds.py --phase fourbit` | inspect generated serve commands |

**Local rule:** clients talk to `127.0.0.1`, never `localhost`. Before any paid session, prove the flow locally: start `mock_vllm.py` and run the arm you plan to run on the pod.

## Operating the instance

- `HF_HOME` defaults to `/workspace/.cache/huggingface` when writable, else `$HOME/.cache/huggingface` — both are on the persistent disk for the supported providers.
- A dead server shows up as a `FAIL server :<port>` line; read `results/logs/vllm-<port>.log`. OOM → lower that agent's `gpu_memory_utilization` in `models.yaml` and re-run `serve.sh`.
- Minimal images without `python3-dev`: vLLM 0.34.0's Triton JIT needs `Python.h`. `setup.sh` and `serve.sh` source `scripts/python_headers.sh`, which sets `CPATH` from the interpreter or a user-local `uv` Python. Never ignore its error; the server will fail after loading weights.
- Retrieval reranking defaults to `lexical`. Do not set `RetrievalConfig.rerank="cross-encoder"` on the serving box without budgeting its VRAM; the runner shares the GPU with the three vLLM instances.
- GPQA/HLE are gated Hugging Face repos: downloads 401 without `HF_TOKEN`. B7 needs `OPENAI_API_KEY`.
- Vast images ship their own `AGENTS.md`/`CLAUDE.md` plus `vast-capabilities` (installed services, ports, persistence) — prefer those for machine facts.

## University H200 slice (18 GB)

The current approved GPU is the university H200 MIG `1g.18gb` slice, reached only through the local SSH alias `uiu-h200`. The full rules are in the repository-root `AGENTS.md`. The slice has 18 GB of VRAM and cannot serve the 53.26 GB `fourbit` stack, the 73.68 GB `final` stack, or the ~25 GB dev trio. Do not schedule a multi-model smoke, the Core/Full matrices, or the FP8 precision replication on it.

Use a dedicated `trustcal-fydp/` project directory. Never work inside or modify the existing `tool-observation/` project, its venv, or its configs; share the Hugging Face cache read-only.

The test-only stack is:

- **8–9B AWQ with vLLM:** cached Qwen3.5-9B (8.37 GiB), Ministral-8B (7.03 GiB), and Llama-3.1-8B (5.58 GiB), one model at a time, 24k context, 0.85 utilization.
- **Q4_K_M main templates with llama.cpp:** Qwen3.8-27B Q4_K_M 15.43 GB (Q4_0 14.95 GB, Q3_K_M 12.48 GB if tight), Gemma 4 26B Q4_K_M 15.78 GB, Mistral 24B Q4_K_M 13.35 GB. Use 4k context, q8 KV, `--n-gpu-layers 99`; offload a few layers to the 125 GB system RAM only if needed. This tests the actual template/parser, not the AWQ stack.
- **One real model plus two mocks** is the allowed integration test. Do not load three real models on this slice.

Download Q4_K_M test files on the university host, one at a time, not in the cloud; keep the project under 200 GB. The cloud host downloads only the final AWQ/FP8 stack.

Budget rule: run Core/Full matrix work on the 80 GB on-demand 4-bit path; reserve the 96 GB class for FP8-specific checks only after their smoke passes. Ask the user before any GPU run; do not expose ports; record approved hardware/driver/CUDA/environment changes in `docs/DECISIONS.md`.

## Managing the GPU instance from a local machine (Vast.ai)

> **Approval-gated path.** The university `uiu-h200` slice is the default approved GPU. Do not create a cloud instance without explicit user approval. The notes below are retained for an approved fallback.

Vast's supported agent integration is the **CLI + agent skill** (no official MCP server; third-party MCP servers exist but are not vendored here). Install the skill for opencode and other skills-framework agents:

```bash
npx --yes skills add vast-ai/vast-cli --skill vastai -g -a opencode -y
```

Key commands (see the skill for the full surface): `vastai search offers`, `vastai create instance`, `vastai show instances`, `vastai start|stop|destroy instance <id>`, `vastai ssh-url <id>`, `vastai copy`.

Vast storage rules that decide the workflow: container disk is **billed while stopped and deleted on destroy**; volumes survive but are local to one physical machine. Copy `results/` out, then destroy — `setup.sh` rebuilds in ~30–40 min.

**Bandwidth cost is a first-class filter:** check `inet_down_cost` when picking an offer (most Vast A6000 hosts bill ~$0.005–0.026/GB of ingress; sort candidates with `-o 'inet_down_cost,dph'`). Paid ingress can dominate a short setup session. `serve.sh` pins `HF_HOME` so relaunches never re-download; export `HF_HUB_OFFLINE=1` when the cache is complete. To avoid paying for the ~22GB model cache again, persist it: RunPod network volume, Thunder Compute snapshot, or a Vast volume reattached on the same physical machine. **Batch GPU work into 1–2 long sessions per phase** — provider availability (Thunder full, RunPod pricier, TensorDock/Massed higher) makes Vast the practical choice, and batching amortizes session ingress.

**Host acceptance (three checks, each with an abort).** Prove the offer before any paid work: (1) SSH within 60 s of `running` — a `Permission denied (publickey)` that survives one reboot means destroy the host, not debug it; (2) a 45 s real `hf download` must exceed 10 MB/s (600 MB/min) or the host's advertised `inet_down` is not what it delivers — destroy and pick another; (3) prefer `vastai/base-image` with our pinned `install_vllm.sh` over a large framework image, because single image layers stall on individual hosts and the stall bills at the GPU rate. On Debian-managed images pass `VENV=1` — system pip fails with `Cannot uninstall pip ... RECORD file not found`. Marginal disk is priced apart from `dph_total` (often near $1/GB/month, so 120 GB ≈ +$0.17/h); size it for weights + venv + results, and destroy rather than stop when the budget is thin.

**Concurrency.** `run_matrix.py` runs rows one at a time, so a matrix launched as-is pays roughly double. For parallel rows, launch one `run_experiment.py` per condition with a distinct `--out` and `tmux`/`nohup`; each process resumes independently from its own JSONL. The four-bit stack's per-instance utilization is KV-balanced for this (Qwen 0.33 / Gemma 0.29 / Mistral 0.28, sum 0.90) because Qwen carries the largest weights and an equal 0.30 split leaves it too little KV to run four concurrent sequences. Watch the vLLM KV-cache percentage and p95 latency; drop a stream before the cache saturates, since preemption silently halves throughput instead of failing loudly.

Failure modes and their fixes - image stalls, `VENV=1`, the Mamba block cap, the `wait`/`tee` hang, memory-profiling races, cost traps - are catalogued in [`../docs/agent/09_GPU_RUNBOOK.md`](../docs/agent/09_GPU_RUNBOOK.md). Check it before a session and extend it after a new failure.

**Retrieval quotas.** Semantic Scholar allows 1 request/second cumulatively across all its endpoints, which a 12-24 request burst always exceeds, so it can only 429. Set `TRUSTCAL_EXCLUDE_SOURCES=semantic_scholar` for concurrent matrix runs and record the exclusion; every arm drops the same source, so the between-arm contrast is unaffected. `TRUSTCAL_RETRIEVAL_CACHE=<dir>` turns on the sharded disk cache (a warm claim costs ~20 ms instead of ~1 s); it caches successes only, so a failing source must still be fixed or excluded.


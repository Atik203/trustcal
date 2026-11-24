# 00 — Start Here

**Status date:** 24 November 2026. **P0 engineering is released.** `main` = `dev` = `v0.2.1`; tags `p0-gate` = `055a244` and `p0-release` = `7f2c11f`. 13/13 gate checks, **663 tests** (`pytest -q`), both manuscripts compile with 0 errors/undefined refs.

**Project title:** *The Boundaries of Evidence-Grounded Trust in Multi-Agent Scientific Debate, with a Controlled Benchmark for Sycophantic Consensus.*

> **TL;DR for an agent**
> - P0 is **released**, not proposed. There are **no efficacy results**.
> - Order of work: `roadmap.md`. Design: `03_EXPERIMENT_PLAN.md`. Status: `01_CURRENT_STATE.md`.
> - **Passed:** 18 GB test gate (N1.0), 4-bit smoke (N1a), FP8 96 GB serving smoke (N1b), first Core row (`core3`, 798 debates), and the concurrency/cost measurement — **172.7 debates/h at $1.50/GPU-h all-in**, 3.3× the 52.2/h 2-way eager baseline.
> - **Not done:** the remaining 22 Core rows (7,202 debates), Full, the FP8 precision replication (600 debates), SciClaimBench annotations.
> - Do **not** run the Core matrix before the pilot passes G2.
> - **Core v1.0:** 4 conditions (B3, B4-matched, B8-no-trust, B8) × 3 datasets (`gpqa_main`, `mmlu_pro`, `hle`) × 2 seeds = **24 runs**, 8,000 debates. SciClaimBench is **not** in Core v1.0.
> - **Full default:** 32 rows with a gold-evidence oracle on SciClaimBench; 36 rows is the gold-answer alternate. WP-18 freezes it, and Full is blocked until `sciclaim_180` has a loader entry and a frozen dataset.
> - **Remaining programme:** 21,800 debates = 126.2 GPU-h = **$189.36** GPU + **$2.56** setup = **$191.92**, inside the **$220** remaining-spend cap with **$20** headroom. Price table: `08_COMPUTE_COST.md`.
> - The **verification ceiling** is a derived hypothesis, not a proved theorem. **BrokenMath/BrokenArXiv are appendix-only** (proof-only splits, 0% answer-type retention); Core v1.0 uses **GPQA-Main + MMLU-Pro STEM + HLE**, with **SciClaimBench 180** joining at the v1.2 freeze.

## 1. The project in one paragraph

Three heterogeneous LLM agents answer a hard scientific question, debate for up to three rounds, and revise. Each answer is split into claims; each claim is checked against retrieved scientific evidence (PubMed, arXiv, Semantic Scholar). Each agent has a bounded trust weight that rises when its claims are supported and falls when they are contradicted. The final answer is a trust-weighted vote, not a majority vote. The target failure is **sycophantic collapse**: a correct minority abandons its answer under pressure from a confident wrong majority. Evaluation uses a **fabricated-consensus injection** plus accuracy / CMR / trust AUROC / calibration.

**Current reality (24 Nov 2026):** the instrument is wired and the serving path is measured. The verifier is not yet human-audited, the FP8 precision replication has not run, and no efficacy result exists. The 18 GB university slice is available for free test-only validation.

## 2. Stage names and current scope

Use `docs/GLOSSARY.md` everywhere. The current names are **Core run** and **Full run**; **TACL is a venue only**. The retired labels are recorded once in `docs/GLOSSARY.md`. The pre-P0 warnings are closed; `02_P0_FIXES.md` holds the fix record, and warning 17 (BrokenMath/BrokenArXiv proof-only, appendix-only) still constrains the design.

| Stage | Scope |
|---|---|
| **18 GB test gate (N1.0)** | One real 8–9B AWQ or Q4_K_M model + two mocks; test-only. **PASS**; $0. |
| **4-bit smoke (N1a)** | Three-model 53.26 GB stack on one 96 GB card; 5 questions (B8, injection, placebo; oracle 4/4 valid). **PASS 20 Nov 2026**; $1–2. |
| **FP8 smoke (N1b)** | 73.68 GB stack serving three models; B8 5/5 valid. **PASS 20 Nov 2026**; $2–8. |
| **Pilot run (N5/G2)** | ~100–150 questions; 4-bit stack; B3, B8-no-trust, B8; injection on/off; trust on/off. Gate G2. |
| **Core run (G3)** | 4 conditions × 3 datasets × 2 seeds = 24 runs, 8,000 debates. 2 of 24 rows done (`core3`, 798 debates); 22 rows / 7,202 debates remain (~41.7 GPU-h at 172.7/h). |
| **Full run (G4/G5)** | 32 rows with a gold-evidence oracle on SciClaimBench (default) or 36 rows with gold-answer trust (alternate). Frozen by WP-18. |
| **Law-testing (N9)** | q/ρ sweeps, granularity, shared-error floor, robustness. Outside the remaining programme; separate approval. |

**Caps:** the remaining-programme cap is **$220** ($20 headroom); the preregistered programme hard stop is **$600**. The 96 GB on-demand RTX PRO 6000 at **$1.50/GPU-h all-in** (8 concurrent rows, CUDA graphs) is the measured serving path; the 80 GB A100 at $0.136/GPU-h and the FP8 $0.336/GPU-h are retired planning rates. Dev (A6000) is retired; only `fourbit` and `final` phases exist. **SciClaimBench ladder:** 24 calibration → 180 v1.2 floor → 300 Full target → 600 stretch → 800 no-go.

## 3. What is actually strong

- Modular codebase: inference, agents, retrieval, trust, orchestrator, eval, stats.
- **663 tests**, a mock vLLM end-to-end path, and 13/13 P0 gate checks.
- Resumable JSONL, manifest/resume refusal, preflight, annotation and human-eval tooling.
- Measured serving: 172.7 debates/h at $1.50/GPU-h all-in on a 96 GB card.
- Two compiled manuscripts (75-page report, 21-page journal), 0 errors/undefined refs.
- Real problem, real application, six-person team, 7–8 months.

## 4. Repository map

```text
E:\FYDP\
├── trustcal\                 # Python pipeline (source of truth for what runs)
│   ├── configs\              # models.yaml, datasets.yaml, experiments.yaml, phase.yaml
│   ├── src\trustcal\
│   │   ├── inference\        # OpenAI-compatible vLLM client
│   │   ├── agents\           # prompts, claim parser, fallback extraction
│   │   ├── orchestrator\     # debate loop, injection, B1–B10 strategies
│   │   ├── retrieval\        # PubMed/arXiv/S2 clients, pipeline, verifier
│   │   ├── trust\            # update, state, aggregation, settings
│   │   ├── eval\             # datasets, options, answers, metrics, stats, oracle
│   │   └── runner.py         # resumable experiment runner
│   ├── scripts\              # run_experiment, run_matrix, analyze, preflight, check_stack, smoke
│   └── experiments\          # pilot templates
├── experiments\              # gate0, n1_smoke, core_prefix, core3, concurrency_test
├── docs\
│   ├── blueprint.md          # historical design doc (not evidence)
│   ├── agent\                # these docs (08_COMPUTE_COST.md, 09_GPU_RUNBOOK.md)
│   └── FYDP1_defence_Q&A.md  # check status notes before the defence
├── FYDP_Report\              # 75-page report (compiled; engineering report)
├── Journal_Paper\            # 21-page journal manuscript (compiled; engineering report)
├── literature_review\        # paper reviews + index
├── UPDATE-CHECKLIST.md       # team-facing one-pager
├── PRE_REGISTRATION.md       # v1.0 + v1.1 erratum (released hash bc9c7b...)
└── roadmap.md                # current order of work and gates
```

**Branch model:** `main` (release trunk; frontend deploys), `dev` (integration), `next/<slice>` (short-lived, one worktree, deleted after merge). Only `E:\FYDP` exists.

## 5. Commands

From `E:\FYDP\trustcal` unless stated otherwise.

```bash
# 1. Tests (GPU-free) — expect 663 passed
pytest -q

# 2. Matrix plan only; writes nothing
python scripts/run_matrix.py --dry-run

# 3. Mock end-to-end (two shells)
python scripts/mock_vllm.py --ports 8000,8001,8002 --mode divergent
python scripts/run_experiment.py --arm B8 --dataset mock --limit 1 \
  --questions-file experiments/pilot-month1/questions.template.json \
  --out results/mock-check

# 4. 4-bit readiness (96 GB; PASSED 20 Nov 2026; use PHASE=final for FP8)
PHASE=fourbit bash setup.sh && python scripts/verify_env.py --check-servers
HF_HUB_OFFLINE=1 python scripts/preflight.py --phase fourbit --offline
python scripts/smoke_test.py --phase fourbit --limit 5

# 5. Real experiment (only after G2 and a GPU)
python scripts/run_experiment.py --arm B8 --dataset gpqa_main --limit 20 --seed 1 --inject
python scripts/analyze.py --records results/B8/gpqa_main/seed1/records.jsonl
```

Do not run `python scripts/run_matrix.py` for real until the pilot passes G2 and WP-18 has frozen the Full definition. `python scripts/p0_gate.py` re-runs the 13 P0 gate checks.

## 6. Reading order

1. This file.
2. `roadmap.md` — current order of work and gates.
3. `01_CURRENT_STATE.md` — what is implemented vs pending.
4. `03_EXPERIMENT_PLAN.md` — the design you must not break.
5. `04_LITERATURE_AND_GAPS.md` — historical prior art and the claims you may not make.
6. `05_WRITING_AND_VENUE.md` — only if editing the paper/thesis.
7. `06_AGENT_CHECKLIST.md` — the live board.
8. `08_COMPUTE_COST.md` — measured throughput, budget, caps.

**Team one-pager:** `..\..\UPDATE-CHECKLIST.md`. Report every task with a command and its exact output; never report "done" without evidence.

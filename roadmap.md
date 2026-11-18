# FYDP Roadmap — Trust-Calibrated Multi-Agent Scientific Deliberation

Phase-by-phase execution plan for **November 2026 – December 2027**. This file is the order-of-work source of truth for agents and the team. It is not a results document.

**Paper title:** *The Boundaries of Evidence-Grounded Trust in Multi-Agent Scientific Debate, with a Controlled Benchmark for Sycophantic Consensus.*

**Current release (18 November 2026):**

| Item | Value |
|---|---|
| Branches | `main` = release/deployed frontend; `dev` = development |
| Release tip | `v0.2.1` on both `main` and `dev`; `p0-release` tag = `7f2c11f` |
| Tags | `p0-gate` = `055a244`; `p0-release` = `7f2c11f` |
| P0 gate | **13/13 passed, 0 failed, 0 pending** |
| Tests | **615 passed** (514 at the P0 release) |
| Report | `FYDP_Summer/out/fydp.pdf` — 70 pages, 80 cited works, explicit pdfLaTeX, 0 errors/undefined refs |
| Journal | `Papev_Summer26_6/out/cas-sc-template.pdf` — 19 pages, 71 cited works, explicit pdfLaTeX, 0 errors/undefined refs |
| Figures | six journal figures + two report-only figures at 6000 × 3375 (600+ DPI) |
| Frontend | `npm run build` passes and prerenders all routes; `npm run lint` exits 0 (warnings only) |
| Main stack (4-bit) | Qwen3.8-27B-AWQ-INT4 / Gemma-4-26B-A4B-AWQ / Mistral-24B-AWQ, **53.26 GB** pinned |
| Final stack (FP8) | Qwen3.8-27B-FP8 / Gemma-4-26B-A4B-FP8 / Mistral-24B-AWQ, **73.68 GB** pinned |
| University GPU | `uiu-h200`, H200 MIG `1g.18gb`, 18 GB, driver `580.178.04`, CUDA `13.5` |
| 18 GB cache | vLLM 0.33.0 and 8–9B AWQ checkpoints in the existing `tool-observation` project; shared read-only |
| Cloud smoke | **NOT RUN** — 4-bit 80 GB and FP8 96 GB paths both unproven on hardware |

**P0 is engineering readiness, not efficacy evidence.** No accuracy, CMR, or sign-reversal claim exists yet. The first claim waits for the pilot and Core run.

---

## 0. Agent rules — read before touching code

1. Read `AGENTS.md`, `trustcal/AGENTS.md`, `docs/DECISIONS.md`, `docs/GLOSSARY.md`, this roadmap, and `PRE_REGISTRATION.md`.
2. Work on a short-lived branch from `dev`: `next/<slice>`, in its own worktree. Push after every green checkpoint.
3. One owner per file. If a file is leased, send the owner a 3-line patch request; do not edit in parallel.
4. Every work package writes `experiments/next/WP-<id>.md` with commands, exact output, acceptance checkboxes, and known gaps.
5. Commit style: `type(scope): imperative summary`. Do not mix `docs/**` with `trustcal/**` or `frontend/**` in one commit.
6. Never push directly to `main`. Merge slices into `dev`; release `dev` → `main` only after a gate and a frontend build.
7. Never invent results, numbers, citations, or gold labels. Use placeholders and mark them.
8. Never commit secrets, `.env`, `results/`, or LaTeX `out/` artifacts.
9. Use explicit `pdflatex` for manuscripts; use `academic-student-writer` for prose and claims.
10. Delete the slice branch and worktree after merge. Keep only `main`, `dev`, and gate tags.
11. On the university server, work only in a dedicated `trustcal-fydp/` project directory. Never work inside or modify the existing `tool-observation/` project, its venv, or its configs. Share the Hugging Face cache read-only.
12. The 18 GB slice is a **test-only** environment. Do not run the three-model stack, the main matrix, or FP8 there. Do not present its outputs as evidence.
13. Do not download Q4_K_M test models on a cloud host. Download them on the university host, one at a time, and keep the project under the 200 GB cap. Cloud rentals download only the final AWQ/FP8 stack.
14. Never expose ports or commit a server address, hostname, username, key, or fingerprint.

**Task report format:** Task → files changed → commands run → exact output → acceptance → next step. No “done” without a command and its output.

---

## 1. Gate ladder

| Gate | When | Scope | Pass condition |
|---|---|---|---|
| **G0** | Done 2026-09-16 | Vanilla MAD on 10 GPQA questions | 10/10 debates, 90/90 positions, 370.8 s mean |
| **P0** | Done 2026-11-09 | Engineering hardening | 13/13 checks, 615 tests, no undefined refs, 600 DPI figures |
| **N1.0** | Nov 2026 | Free 18 GB test-only validation | One real 8–9B AWQ model plus two mocks, or one Q4_K_M model plus two mocks; schema-valid record; no cloud spend |
| **N1a** | Nov–Dec 2026 | 4-bit three-model cloud smoke | Three servers OK; 5-question smoke PASS; peak VRAM recorded |
| **N2** | Nov–Dec 2026 | WP-18 / v1.3 sign-off | Config hashes frozen; placebo/oracle and reuse semantics signed |
| **N3** | Nov–Dec 2026 | SciClaimBench 24-item calibration | κ ≥ 0.75, defect ≤ 15%, `H_attempt` ≤ 2.0 h/item |
| **N4** | Nov–Dec 2026 | Verifier audit | κ ≥ 0.60; balanced accuracy reported; target ≥ 0.75 |
| **G2** | Dec 2026–Jan 2027 | Pilot run | Baseline CCR ≥ 0.30; trust AUROC ≥ 0.65; ≥65% correct-direction changes; injection κ ≥ 0.75 |
| **G3** | Jan–Feb 2027 | Core run | Primary accuracy/CMR with CIs; B8 > B8-no-trust direction; pre-registration unchanged |
| **N1b** | Feb 2027 | FP8 smoke and precision | Three FP8 servers OK; precision result recorded; not a gate for the 4-bit Full matrix |
| **G4/G5** | Feb–Mar 2027 | Full run | Placebo/oracle separate; q/ρ sign reversal; one external-validity check |
| **Results freeze** | Apr 2027 | All analyses | CIs, negative results, manifests, pre-registered contrasts |
| **Thesis** | Jun 2027 | Submission | Internal review; defence-ready |
| **Paper** | Aug–Dec 2027 | Submission | Q1 journal/TACL after defence |

**Order rule:**

> N1.0 → N1a → v1.3 sign-off → N3/N4 → pilot → Core → N1b → Full.

N1b is required before any FP8 precision claim, not before the 4-bit Full matrix. Do not reorder the 4-bit path.

---

## 2. Compute paths

### 2.1 Free 18 GB test-only path

**Host:** `uiu-h200`, H200 MIG `1g.18gb`, 18 GB VRAM, driver `580.178.04`, CUDA `13.5`, 125 GB RAM, 16 CPUs, 200 GB project cap.

**Project rule:** clone the repo into a dedicated `trustcal-fydp/` directory. The existing `tool-observation/` project is read-only; do not modify its venv, configs, data, or cache.

**Existing cache (read-only):**

| Model | Weights | Use |
|---|---:|---|
| `cyankiwi/Qwen3.5-9B-AWQ-4bit` | 8.37 GiB | vLLM/OpenAI code-path test |
| `cyankiwi/Ministral-3-8B-Instruct-2512-AWQ-4bit` | 7.03 GiB | second family |
| `hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4` | 5.58 GiB | third family |
| `Qwen/Qwen2.5-7B-Instruct-AWQ` | 5.38 GiB | historical fallback |

The existing environment has vLLM **0.33.0** and torch **2.14.0+cu130**. Prefer a separate `trustcal-fydp/.venv`; using the existing vLLM binary read-only is allowed only for a first smoke, never for installs or upgrades into `tool-observation`.

**Q4_K_M test-only main models:**

| Model | Quant | Size | 18 GB fit |
|---|---|---:|---|
| Qwen3.8-27B | Q4_K_M | 15.43 GB | likely at 4k context; Q4_0 14.95 GB or Q3_K_M 12.48 GB if tight |
| Qwen3.8-27B | Q4_0 | 14.95 GB | more KV headroom |
| Qwen3.8-27B | Q3_K_M | 12.48 GB | lower quality; use only if Q4 OOMs |
| Gemma 4 26B-A4B | Q4_K_M | 15.78 GB | tight; Q4_K_S 15.36 GB |
| Mistral 24B | Q4_K_M | 13.35 GB | comfortable |

Run **one model at a time** with llama.cpp, `--ctx-size 4096`, q8 KV cache, and `--n-gpu-layers 99`. If a model is tight, offload a few layers to the 125 GB system RAM with `--n-gpu-layers`. This is a **test-only** path; it is not the pre-registered AWQ/vLLM stack.

**Bandwidth rule:** download one Q4_K_M file at a time on the university host. Do not download these test files on a cloud rental. The cloud host downloads only the final AWQ/FP8 stack. Keep the project under 200 GB; check `du -sh` before and after each download.

### 2.2 4-bit cloud path

- **GPU:** one 80 GB A100 PCIe spot.
- **Rate:** $0.136/GPU-h planning rate; re-query before renting.
- **Stack:** 53.26 GB, three models.
- **Jobs:** N1a smoke, pilot, Core, Full.
- **Why:** the main matrix needs three models concurrently; 18 GB cannot hold them.

### 2.3 FP8 96 GB path

- **GPU:** 96 GB class, $0.336/GPU-h.
- **Stack:** 73.68 GB, three models.
- **Jobs:** N1b smoke and the 3-row GPQA precision replication.
- **Why:** FP8 is a precision check, not the main matrix. The 96 GB path is not a fallback for the 4-bit matrix unless re-approved.

---

## 3. Phase N1 — Hardware readiness

### N1.0 — Free 18 GB test-only validation (Nov 2026)

**Objective:** finalize code, prompts, parser, serving flags, records, and the mock path before paying for cloud GPUs.

**Test A — 8–9B AWQ with vLLM:**

1. Serve one cached model on port 8000 with the correct `--served-model-name`.
2. Run two `mock_vllm` servers on 8001 and 8002.
3. Run one real agent plus two mocks with `--limit 1`.
4. Check chat template, output format, parser, trust update, injection, aggregation, and record schema.
5. Repeat for Qwen3.5-9B, Ministral-8B, and Llama-3.1-8B.

**Test B — Q4_K_M main templates with llama.cpp:**

1. Download one Q4_K_M file at a time; start with Qwen3.8-27B Q4_K_M.
2. Serve with `--ctx-size 4096`, q8 KV, and `--n-gpu-layers 99`.
3. If OOM, reduce GPU layers to offload to RAM, or drop to Q4_0/Q3_K_M.
4. Run one real model plus two mocks; check chat template, thinking block, parser, and output format.
5. Repeat only if needed for Gemma 4 and Mistral 24B.

**What this proves:** the model/template/parser/one-real-agent path works before cloud spend.

**What it does not prove:** three-model concurrency, AWQ numerical behaviour, FP8, or any efficacy result.

**Acceptance:** a schema-valid record from at least one 8–9B AWQ model and one Q4_K_M main model; `nvidia-smi` peak recorded; no system changes; no modification of `tool-observation/`.

**Cost:** $0 GPU. Time and university bandwidth only.

### N1a — 4-bit three-model cloud smoke (Nov–Dec 2026)

**Objective:** prove the 53.26 GB stack serves all three models together.

```bash
cd trustcal
PHASE=fourbit bash setup.sh
python scripts/check_stack.py --phase fourbit
python scripts/preflight.py --phase fourbit --offline
python scripts/verify_env.py --check-servers
python scripts/smoke_test.py --phase fourbit --limit 5
```

**Acceptance:** three `server OK` lines; 5-question smoke PASS; peak `nvidia-smi` and per-model weights recorded. Run this in the same session as the pilot when possible.

**Cost:** 4–8 GPU-h, **$1–2** at $0.136/h.

### N1b — FP8 final-stack smoke and precision (Feb 2027)

**Objective:** prove the 73.68 GB FP8 stack and run the small GPQA precision replication.

```bash
cd trustcal
PHASE=final bash setup.sh
python scripts/check_stack.py --phase final
python scripts/preflight.py --phase final --offline
python scripts/verify_env.py --check-servers
python scripts/smoke_test.py --phase final --limit 5
```

Then run `configs/experiments_precision.yaml`.

**Acceptance:** three FP8 servers OK; precision result recorded; no FP8 precision claim before this.

**Cost:** 5-question smoke **$2–8** all-in; full precision replication **$25–40**. Do not run the precision replication with the current $50 tranche.

---

## 4. Phase N2 — WP-18 and v1.3 sign-off (Nov–Dec 2026)

**Objective:** freeze the six-arm semantics and the Full definition before any confirmatory row.

**Scope:**

- `B8-placebo`: cross-agent round-pool verdict shuffle.
- `B8-oracle`: gold-evidence-only on SciClaimBench by default; gold-answer trust is the 36-row alternate.
- 32-row Full default; 36-row alternate.
- Full config hash recorded in v1.3.
- If the team wants the $400 path, add a **Core → Full subset-reuse** amendment before Core/Full unblinding.

**Acceptance:** v1.3 signed; mock placebo/oracle records validate; `run_matrix.py --dry-run` shows 24 Core and 32/36 Full rows; no change to the 13/13 gate.

---

## 5. Phase N3 — SciClaimBench calibration and freeze (Nov 2026–Feb 2027)

**Objective:** build SciClaimBench at the scale the design can defend.

**Ladder:**

| Size | Role | Annotation | Decision |
|---:|---|---:|---|
| **24** | Calibration batch | ~1 week | Start here; if `H_attempt > 2.0` or defect >15%, cut to 120 immediately |
| **180** | SciClaimBench v1.2 freeze (not in the v1.0 Core matrix) | ~410 h | Freeze by Jan 2027 |
| **300** | Full-run benchmark target | ~684 h | Target by Feb 2027 |
| **600** | Stretch | ~1,368 h | Only with 2–3 dedicated annotators |
| **800** | No-go | ~1,824 h | Do not build |

**Item rules:** 3 domains (biomed, phys/chem, math/CS); 3–6 atomic claims per position; gold evidence and verdicts; five conditions; original items CC BY 4.0; gated dataset text not redistributed.

**Acceptance:** 24-item calibration report; 180-item freeze with κ and defect rate; 300-item target only if the 180 set is clean.

**Owner:** P3 + members 2–6.

---

## 6. Phase N4 — Verifier audit (Nov–Dec 2026)

**Objective:** turn the lexical verifier into a measured component.

**Scope:** 180 hand-labeled claim–passage pairs, two annotators; balanced accuracy, precision/recall/F1, coverage, Cohen's κ; shared vs private claim accuracy; optional NLI/LLM-judge comparison.

**Acceptance:** balanced accuracy ≥0.75 and κ ≥0.60. If 0.60–0.75, swap to NLI/LLM judge and re-audit. If <0.60, the paper becomes a measurement/negative result; do not claim a high-q result.

**Owner:** P6 + members 2–6.

---

## 7. Phase N5 — Pilot run R2 (Dec 2026–Jan 2027)

**Objective:** verify wiring and estimate the effect before spending Core-run money.

**Scope:** 100–150 questions; 4-bit 24–27B stack on the 80 GB A100; B3, B8-no-trust, B8; injection on/off; trust on/off; 24-item benchmark subset; q/ρ re-aggregation design frozen.

**Preconditions:** N1.0 and N1a pass; v1.3 signed; the 24-item calibration and verifier audit are complete.

**G2 pass:** baseline CCR ≥0.30; trust AUROC ≥0.65; ≥65% correct-direction changes; injection κ ≥0.75; no schema-invalid records.

**Cost:** ~112 GPU-h, **$15–20**. Run in the same session as N1a.

**Owner:** P2 + P4.

---

## 8. Phase N6 — Core run R3 (Jan–Feb 2027)

**Objective:** the minimum causal package.

**Arms:** B3, B4-matched, B8-no-trust, B8.

**Design:** GPQA-Main + MMLU-Pro + HLE; 400 + 400 + 200 items; 2 seeds; **24 runs, 8,000 planned debates / ~1,067 GPU-h**; **1,280 GPU-h conservative gate cap**; SciClaimBench-180 freezes under v1.2, outside this matrix. Runs on the **4-bit 24–27B stack on one 80 GB A100 PCIe**.

**Primary endpoint:** final-answer accuracy on pressure-eligible items, paired B8 vs B8-no-trust. **Co-primary:** CMR. Secondary: ARR, trust AUROC/Brier, verifier balanced accuracy, citation faithfulness.

**G3 pass:** primary endpoint measured with CIs; B8 > B8-no-trust direction; pre-registration unchanged.

**Cost:** 1,280 GPU-h conservative cap (planned ~1,067 GPU-h), **$175–210**. Not runnable from the current $50 tranche.

**Owner:** P2 + P4.

---

## 9. Phase N7 — Full run R5 (Feb–Mar 2027)

**Objective:** the complete 6-arm matrix for the paper.

**Arms:** B3, B4-matched, B8-no-trust, B8, B8-placebo, B8-oracle.

**Design:** 6 arms × 3 datasets × 2 seeds; 300-item benchmark target. Default **32 rows** with a gold-evidence oracle on SciClaimBench (1,280 GPU-h, **$210**); **36 rows** is the gold-answer alternate (1,440 GPU-h, **$235**). **B8-placebo is a cross-agent round-pool.** SciClaimBench joins at the v1.2 freeze.

### Core → Full subset reuse (conditional)

- Full 32 rows = 24 core + 6 placebo + 2 oracle.
- Reusable GPQA + MMLU-Pro core rows: **16 rows**.
- New Full work: 8 SciClaimBench core rows + 6 placebo + 2 oracle = **16 rows / 4,800 debates / 640 GPU-h**.
- Full incremental cost: **~$104** instead of $210; saving **~$106**.
- Conditions: same model revisions, prompts, dataset revision, seeds, and deterministic sample order; Full 300 must be a subset of Core 400.
- Must be pre-registered in v1.3 before unblinding. If not signed, Full is a full 32-row run at $210.

**G4/G5 pass:** placebo does not match B8; oracle separates; the sign reversal appears at the predicted q/ρ boundary; one external-validity check replicates the sign.

**Owner:** P2 + P4 + P5.

---

## 10. Phase N8 — Human evaluation and SDT (Mar 2027)

**Scope:** 150–200 paired items, 3 raters; UWS/EWE/ARR taxonomy; citation faithfulness (300 pairs); expert ceiling (60 items); κ/ICC; SDT 3-axis for the paper, 6-axis for the thesis.

**Acceptance:** κ ≥0.60; the trust plane separates calibrated from sycophantic panels; the human labels support or qualify the automatic endpoints.

**Owner:** P5 + P4.

---

## 11. Phase N9 — Law-testing and ablations (Apr 2027)

**Scope:** q sweep, ρ measurement/manipulation, granularity (claim vs document vs shuffled), shared-error floor, N/K/α/β robustness, natural-divergence subset.

**Rule:** run only if Core/Full show a real effect. R6 remains a **derived law** until an independent proof check signs it. This phase is **outside the $500–600 compute envelope and the $600 hard stop**; no spend without a separate cost model and approval.

**Acceptance:** pre-registered contrasts; CIs; negative results reported. Results freeze at the end of April.

**Owner:** P1 + P4.

---

## 12. Phase N10 — Thesis (May–Jun 2027)

**Scope:** full 6-arm matrix, 300–600 benchmark, 6-axis SDT, full proofs, SEA-Cert, negative results, accreditation, reproducibility.

**Milestones:** chapters 3/6/7/8 by May; internal review; **thesis submission June 2027; defence June/July 2027.** Do not force a paper deadline before the defence.

---

## 13. Phase N11 — Paper (Aug–Dec 2027)

**Scope:** the sharp boundary/causal/benchmark paper from the thesis.

**Venue:** TACL rolling, EMNLP 2028, or a Q1 journal. TACL is the venue, not an experiment stage. No dual submission.

---

## 14. Budget and the $50 tranche

### 14.1 Use the current $50 first

| Priority | Item | Cost | Rule |
|---|---|---:|---|
| 1 | 18 GB test-only validation | **$0** | 8–9B AWQ one at a time; optional Q4_K_M main template |
| 2 | 80 GB A100 4-bit smoke | **$1–2** | Must pass before pilot |
| 3 | 80 GB A100 pilot | **$15–20** | Run in the same session as the smoke |
| 4 | 96 GB 5-question smoke | **$2–8** | Optional; only after the 80 GB pilot is stable |
| — | Reserve for retries/bandwidth | **$20–30** | Do not spend on 96 GB pilot/precision |
| — | **Total** | **$18–30** | Leaves a real buffer |

**Do not run with $50:**

- 96 GB pilot: **$37–45**.
- 96 GB FP8 precision: **$25–40**.
- Core: **$175–210**.
- Full: **$210** (or **~$104** with reuse).

### 14.2 Approved envelope

| Item | GPU-h | Cash |
|---|---:|---:|
| 18 GB dev validation | — | **$0** |
| 4-bit 80 GB smoke | 4–8 | **$1–2** |
| Pilot | ~112 | **$15–20** |
| Core | 1,280 cap (planned ~1,067) | **$175–210** |
| Full 32-row default | 1,280 | **$210** |
| Full 36-row alternate | 1,440 | **$235** |
| 96 GB FP8 5-question smoke | 1.5–3 | **$2–8** |
| FP8 precision replication | 60–100 | **$25–40** |
| Storage and bandwidth | — | **$40–80** |
| **Total plan** | — | **$500–600** |
| **Hard stop** | — | **$600** |

### 14.3 Efficient path

With the free 18 GB tests and a signed Core → Full subset-reuse amendment:

| Item | Cost |
|---|---:|
| 18 GB tests | $0 |
| 4-bit smoke | $1–2 |
| Pilot | $15–20 |
| Core | $175–210 |
| Full incremental | ~$104 |
| 96 GB FP8 smoke | $2–8 |
| FP8 precision replication | $25–40 |
| Storage | $40–60 |
| **Total** | **~$360–450** |

Under $400 is possible with Core at the low end, storage around $40–60, and the A100 at $0.136/GPU-h. The **$500–600** envelope remains approved; the $400 path is a planning option only after the reuse amendment is signed.

### 14.4 Bandwidth discipline

- Download Q4_K_M test files on the university host, one at a time; do not download them in the cloud.
- Cloud rentals download only the final AWQ/FP8 stack.
- Persist the cloud cache; batch pilot/Core/Full into long sessions; copy `results/` before destroying the instance.
- Storage/bandwidth stays **$40–80** until actual invoices replace the estimate.

**Hard stop: $600.** The two Full rows are alternatives; the total counts one Full run. The 96 GB fallback for the main matrix is **$1,050–1,150** and requires re-approval.

---

## 15. Branch and release model

```text
main    release trunk; the web frontend deploys from here
dev     development/integration branch
next/*  short-lived slice branches; deleted after merge
```

- Slice: `next/<slice>` from `dev` → worktree → push → merge into `dev` → delete.
- Release: `dev` → `main` only after a gate, a clean `npm run build`, and the PDF/figure checks.
- Tags: `p0-gate`, `p0-release` exist. Future gates use `g2`, `g3`, `g4`, `results-freeze`, `thesis`, `paper`.
- No direct `main` pushes. No long-lived feature branches.

---

## 16. Do not do

- Do not run the main matrix before the pilot passes.
- Do not run the three-model stack on 18 GB.
- Do not run Qwen3.8-27B-AWQ on 18 GB.
- Do not modify `tool-observation/`, its venv, or its cache.
- Do not use Ollama; it is not installed on the slice.
- Do not use Q4_K_M or 8–9B test outputs as evidence.
- Do not download Q4_K_M test files in the cloud.
- Do not run a 96 GB pilot or precision replication with the $50 tranche.
- Do not use the 96 GB main-matrix fallback without re-approval.
- Do not claim $400 without the signed subset-reuse amendment.
- Do not claim efficacy from P0 or from mock/integration tests.
- Do not use BrokenMath/BrokenArXiv for evidence grounding or CCR; they are appendix-only.
- Do not use ECR as a primary endpoint.
- Do not compare B8 to B4 without matching retrieval and prompts.
- Do not claim R6 is a theorem before the proof check.
- Do not build 800 benchmark items.
- Do not commit secrets, `results/`, or `out/` artifacts.
- Do not put a colon in the paper title; use the approved no-colon wording.
- Do not submit the paper before the defence unless the supervisor explicitly reopens that decision.

---

## 17. Links

| Doc | Purpose |
|---|---|
| `AGENTS.md` | Canonical repository and university-GPU rules |
| `trustcal/AGENTS.md` | Pipeline and serving rules |
| `docs/DECISIONS.md` | Approved hardware, environment, and reuse decisions |
| `docs/MEMBER_GUIDE.md` | Member roles and annotation plan |
| `docs/GLOSSARY.md` | Core run / Full run / TACL naming |
| `PRE_REGISTRATION.md` | Frozen endpoints, arms, analysis, stopping rules |
| `docs/agent/03_EXPERIMENT_PLAN.md` | Power, design, benchmark details |
| `docs/agent/08_COMPUTE_COST.md` | Cost model, dev-slice offset, and $50 tranche |
| `experiments/p0/WAVE2.md` | P0 landing record |
| `trustcal/IMPLEMENTATION_STATUS.md` | What is wired vs approximate |
| `Papev_Summer26_6/CLAIMS_AUDIT.md` | Journal claim changes |
| `FYDP_Summer/CLAIMS_AUDIT.md` | Report claim changes |

---

## 18. Open decisions

| Decision | Default | Status |
|---|---|---|
| Server project directory | Dedicated `trustcal-fydp/`, not `tool-observation/` | approved |
| 18 GB test set | 8–9B AWQ first; Q4_K_M main templates optional | approved |
| 96 GB smoke timing | After stable 80 GB pilot, only if budget ≥$25 | proposed |
| Core → Full subset reuse | Draft v1.3 amendment before Core | needs sign-off |
| $400 efficient path | Only after reuse amendment and low-end storage | conditional |

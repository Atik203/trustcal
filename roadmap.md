# FYDP Roadmap - Trust-Calibrated Multi-Agent Scientific Deliberation

**Status key:** ✅ Done · 🟡 Running / next up · ⬜ Todo · 🔴 Blocked

Phase-by-phase execution plan for **November 2026 – December 2027**. This file is the order-of-work source of truth for agents and the team. It is not a results document.

**Paper title:** *The Boundaries of Evidence-Grounded Trust in Multi-Agent Scientific Debate, with a Controlled Benchmark for Sycophantic Consensus.*

**Current status (20 November 2026):**

| Item | Value |
|---|---|
| Branches | `main` = release/deployed frontend; `dev` = development |
| Release tip | past PR #23 on both `main` and `dev` (core3 complete); `p0-release` tag = `7f2c11f` |
| Tags | `p0-gate` = `055a244`; `p0-release` = `7f2c11f` |
| P0 gate | **13/13 passed, 0 failed, 0 pending** |
| Tests | **661 passed** (514 at the P0 release) |
| Report | `FYDP_Report/fydp.pdf` – 75 pages, 80+ cited works, explicit pdfLaTeX, 0 errors/undefined refs |
| Journal | `Journal_Paper/cas-sc-template.pdf` – 21 pages, 71 cited works, explicit pdfLaTeX, 0 errors/undefined refs |
| Figures | six journal figures + two report-only figures at 6000 × 3375 (600+ DPI) |
| Frontend | `npm run build` passes and prerenders all routes; `npm run lint` exits 0 (warnings only) |
| Main stack (4-bit) | Qwen3.8-27B-AWQ-INT4 / Gemma-4-26B-A4B-AWQ / Mistral-24B-AWQ, **53.26 GB** pinned |
| Final stack (FP8) | Qwen3.8-27B-FP8 / Gemma-4-26B-A4B-FP8 / Mistral-24B-AWQ, **73.68 GB** pinned |
| University GPU | `uiu-h200`, H200 MIG `1g.18gb`, 18 GB, driver `580.178.04`, CUDA `13.5` |
| 18 GB cache | vLLM 0.33.0 and 8–9B AWQ checkpoints in the existing `tool-observation` project; shared read-only |
| 4-bit smoke (N1a) | **PASS 20 Nov 2026** — three 24–27B 4-bit models on 96 GB spot hosts (vLLM 0.34.0); B8, injection, placebo 5/5; oracle 4/4 valid (5th lost to a spot eviction) |
| Core prefix | **25+25 COMPLETE 20 Nov 2026** — `gpqa_main` seed 1, B8 vs B8-no-trust; feasibility/timing only, not efficacy |
| FP8 smoke (N1b) | **PASS 20 Nov 2026** - 73.68 GB FP8 stack serves 3/3 on 96 GB; B8 5/5 valid, accuracy 4/5 (noise at n=5); mean 282.4 s vs 299.6 s 4-bit on same 5 questions |

**P0 is engineering readiness, not efficacy evidence.** No accuracy, CMR, or sign-reversal claim exists yet. The 25+25 Core prefix (+0.08 at n=25) is a feasibility/timing gate, not an efficacy result.

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

- **GPU:** one 96 GB RTX PRO 6000 class card (a single 80 GB A100 also fits the 53.26 GB stack, but measured throughput is lower).
- **Rate:** **$1.49/GPU-h all-in measured** (on-demand, including disk and ingress); the old $0.136/GPU-h spot figure is retired.
- **Stack:** 53.26 GB, three models, 8 concurrent rows with CUDA graphs.
- **Measured throughput:** **172.7 debates/h** (three runs, ±3%) versus 52.2/h for the 2-way eager baseline.
- **Jobs:** N1a smoke, pilot, Core, Full.
- **Why:** the main matrix needs three models concurrently; 18 GB cannot hold them.

### 2.3 FP8 96 GB path

- **GPU:** 96 GB class, **$1.49/GPU-h all-in measured**.
- **Stack:** 73.68 GB, three models.
- **Jobs:** N1b smoke and the 3-row GPQA precision replication.
- **Why:** FP8 is a precision check, not the main matrix. The 96 GB path is not a fallback for the 4-bit matrix unless re-approved.

---

## 🟡 3. Phase N1 — Hardware readiness

### ✅ N1.0 — Free 18 GB test-only validation (Nov 2026)

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

**Status (18 Nov 2026):** PASS for the 8–9B vLLM trio and the Q4_K_M main templates. 8–9B: Qwen3.5-9B 26.3 s / 13,880 MiB; Ministral-8B 37.5 s / 15,461 MiB; Llama-3.1-8B 27.2 s / 15,666 MiB. Q4_K_M: Qwen3.8-27B 145.8 s / 15,796 MiB; Gemma 4 26B 58.9 s / 3,384 MiB with `-cmoe`; Mistral 24B 74.6 s / 14,018 MiB. All schema valid. See [`experiments/n1_smoke/README.md`](experiments/n1_smoke/README.md).

**Status (19 Nov 2026, pre-N1a revalidation):** PASS. Dedicated venv with vLLM 0.34.0 / torch 2.14.0+cu130 / transformers 5.22.2; `validate_stack.py` passed all three exact 4-bit checkpoint configs (architecture, quant, flags, parser, context, chat template); GPQA/MMLU-Pro/HLE loaded at pinned revisions; one real model + two mocks passed B3, B8, injection, placebo, and gold-answer oracle; Qwen3.8-27B Q4_K_M B8 passed at 62.3 s / 15,786 MiB; `--stop-after` prefix/resume works; **633 tests + P0 13/13** on the host. Two latent cloud failures were fixed: missing `Python.h` for Triton and a hidden GPU cross-encoder in retrieval. See the same README.

**Cost:** $0 GPU. Time and university bandwidth only.

### ✅ N1a — 4-bit three-model cloud smoke (Nov–Dec 2026)

**Objective:** prove the 53.26 GB stack serves all three models together.

```bash
cd trustcal
PHASE=fourbit bash setup.sh
python scripts/check_stack.py --phase fourbit
python scripts/validate_stack.py --phase fourbit --offline
python scripts/preflight.py --phase fourbit --offline
python scripts/verify_env.py --check-servers
python scripts/run_matrix.py --config configs/experiments_fourbit.yaml --dry-run
python scripts/smoke_test.py --phase fourbit --limit 5 --arm B8
python scripts/smoke_test.py --phase fourbit --limit 5 --arm injection
python scripts/smoke_test.py --phase fourbit --limit 5 --arm B8-placebo
python scripts/smoke_test.py --phase fourbit --limit 5 --arm B8-oracle
```

**Acceptance:** three `server OK` lines; all four smoke invocations PASS; every model has a completed 5-question run; `nvidia-smi` peak and per-model weights recorded. `B8-oracle` here uses `gold_answer` because GPQA has no gold evidence; the `gold_evidence` oracle is SciClaimBench-only and stays covered by the mock/P0 test until that dataset is frozen.

**Status (20 Nov 2026): PASS.** Three 24–27B 4-bit models on RTX PRO 6000 96 GB spot hosts, vLLM 0.34.0. B8 5/5 PASS (per-debate 414.9, 297.2, 272.4, 285.4, 228.0 s; accuracy 0.40); injection 5/5 PASS (129.2, 151.7, 105.3, 140.7, 159.6 s; one item showed a transient D→C→D change under injection, which motivated a fixed smoke check); B8-placebo 5/5 PASS (299.9, 255.4, 177.5, 265.8, 292.0 s); B8-oracle 4/4 valid records, all final answers correct (5th record lost to a spot eviction, not rerun). Local mirror: `trustcal/results/n1a/` (gitignored). Full per-arm record: `experiments/core_prefix/README.md`.

**Cost:** 4–8 GPU-h, **$1–2** at $0.136/h. Do not add the separate $15–20 100–150-question pilot; use the Core-prefix gate (`§14.1`) after the smoke.

### 🟡 N1b — FP8 final-stack smoke and precision (Feb 2027)

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

**Status (20 Nov 2026): PASS.** 96 GB host; 73.68 GB stack served 3/3 (KV-cache fix: 4096 ctx, max 16 seqs/server); B8 5/5 valid, accuracy 4/5 (n=5 noise), mean 282.4 s vs 299.6 s 4-bit on the same questions. No precision claim yet; the subset replication is still ahead.

**Cost:** 5-question smoke **$2–8** all-in; full precision replication **$25–40**. Do not run the precision replication with the current $50 tranche.

---

## 🔴 4. Phase N2 — WP-18 and v1.3 sign-off (Nov–Dec 2026)

**Objective:** freeze the six-arm semantics and the Full definition before any confirmatory row.

**Scope:**

- `B8-placebo`: cross-agent round-pool verdict shuffle.
- `B8-oracle`: gold-evidence-only on SciClaimBench by default; gold-answer trust is the 36-row alternate.
- 32-row Full default; 36-row alternate.
- Full config hash recorded in v1.3.
- **Full is blocked until `sciclaim_180` exists in both `eval/datasets.py` and `configs/datasets.yaml`.** The current `run_matrix.py --config configs/experiments_full.yaml --dry-run` fails offline plan validation by design.
- If the team wants the $400 path, add a **new v1.5** Core → Full subset-reuse amendment: Full `gpqa_main: 400`, `mmlu_pro: 400`, `sciclaim_180: 300`, plus a new config hash. The current v1.3 draft uses 300/dataset and does not assume reuse. (v1.4 is the frozen B7-provider erratum.)

**Acceptance:** v1.3 signed; mock placebo/oracle records validate; Core dry-run shows 24 rows; Full dry-run shows 32/36 rows **after** the SciClaimBench loader entry exists; no change to the 13/13 gate.

---

## 🟡 5. Phase N3 — SciClaimBench calibration and freeze (Nov 2026–Feb 2027)

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

## 🟡 6. Phase N4 — Verifier audit (Nov–Dec 2026)

**Objective:** turn the lexical verifier into a measured component.

**Scope:** 180 hand-labeled claim–passage pairs, two annotators; balanced accuracy, precision/recall/F1, coverage, Cohen's κ; shared vs private claim accuracy; optional NLI/LLM-judge comparison.

**Acceptance:** balanced accuracy ≥0.75 and κ ≥0.60. If 0.60–0.75, swap to NLI/LLM judge and re-audit. If <0.60, the paper becomes a measurement/negative result; do not claim a high-q result.

**Owner:** P6 + members 2–6.

---

## ⬜ 7. Phase N5 — Pilot run R2 (Dec 2026–Jan 2027)

**Objective:** verify wiring and estimate the effect before spending Core-run money.

**Scope:** 100–150 questions; 4-bit 24–27B stack on the 80 GB A100; B3, B8-no-trust, B8; injection on/off; trust on/off; 24-item benchmark subset; q/ρ re-aggregation design frozen.

**Preconditions:** N1.0 and N1a pass; v1.3 signed; the 24-item calibration and verifier audit are complete.

**G2 pass:** baseline CCR ≥0.30; trust AUROC ≥0.65; ≥65% correct-direction changes; injection κ ≥0.75; no schema-invalid records.

**Cost:** ~112 GPU-h, **$15–20**. Run in the same session as N1a.

**Owner:** P2 + P4.

---

## 🟡 8. Phase N6 — Core run R3 (Jan–Feb 2027)

**Objective:** the minimum causal package.

**Arms:** B3, B4-matched, B8-no-trust, B8.

**Design:** GPQA-Main + MMLU-Pro + HLE; 400 + 400 + 200 items; 2 seeds; **24 runs, 8,000 debates**; SciClaimBench-180 freezes under v1.2, outside this matrix. Runs on the **4-bit 24–27B stack on one 96 GB card** with 8 concurrent rows.

**Primary endpoint:** final-answer accuracy on pressure-eligible items, paired B8 vs B8-no-trust. **Co-primary:** CMR. Secondary: ARR, trust AUROC/Brier, verifier balanced accuracy, citation faithfulness.

**G3 pass:** primary endpoint measured with CIs; B8 > B8-no-trust direction; pre-registration unchanged.

**Status (21 Nov 2026): first Core dataset-seed COMPLETE** — `gpqa_main` seed 1, B8 + B8-no-trust arms (`experiments/core3/`): 399+399 debates (q27 quarantined), 798 total, both runners clean. Final: B8 acc 0.6241 (249/399, CI 0.576–0.672) vs control 0.5865 (234/399, CI 0.536–0.634); paired 208/41/26/124; exact McNemar p=0.086. Counts as 2 of 24 Core rows ≈ 800/8,000 debates (10%). Full remains blocked on the v1.5 amendment + `sciclaim_180` loader (§9, §14.3).

**Cost (measured 24 Nov 2026):** 172.7 debates/h at 1.50 USD/GPU-h all-in (on-demand). All 24 Core rows (8,000 debates, including the 798-debate re-run that brings the evidence pool in line with the S2 pacing gate) are **46.32 GPU-h = 69.48 USD**; Core + Full (36-row alternate, 14,000 debates) is **81.06 GPU-h = 121.59 USD**. The full remaining programme (Core + Full + cap increase + three ablations + FP8 precision = 23,798 debates) is **209.25 USD all-in**, committed at **219.25 USD with 10 USD headroom** under a 220 USD limit. The old 1,280 GPU-h / 175-210 USD figure assumed a serial eager run and is superseded. Concurrency plan and measurements: experiments/concurrency_test/.

**Owner:** P2 + P4.

---

## 🔴 9. Phase N7 — Full run R5 (Feb–Mar 2027)

**Objective:** the complete 6-arm matrix for the paper.

**Arms:** B3, B4-matched, B8-no-trust, B8, B8-placebo, B8-oracle.

**Design:** 6 arms × 3 datasets × 2 seeds; 300-item benchmark target. Default **32 rows** with a gold-evidence oracle on SciClaimBench (1,280 GPU-h, **$210**); **36 rows** is the gold-answer alternate (1,440 GPU-h, **$235**). **B8-placebo is a cross-agent round-pool.** SciClaimBench joins at the v1.2 freeze.

### Core → Full subset reuse (conditional)

- Full 32 rows = 24 core-arm rows + 6 placebo + 2 oracle.
- Reusable rows: **16** (4 core arms × 2 datasets × 2 seeds), **only if** Full `gpqa_main` and `mmlu_pro` caps are **400**, with the same model revisions, prompts, dataset revisions, seeds, flags, and `limit`.
- **A 300-item Full sample is not a subset of the 400-item Core sample.** `stratified_sample` uses different per-stratum allocations and independent draws, `question_id` indexes shift, and the manifest includes `limit`; the runner refuses to resume across caps. Reuse is an exact-row identity, not a subset extraction.
- New Full work: 8 SciClaimBench core rows (300) + 6 placebo (300) + 2 oracle (300) = **16 rows / 4,800 debates / 640 GPU-h**.
- Full incremental cost at the measured 172.7 debates/h and $1.50/GPU-h: **~$42** for the new Full rows, because the four Core arms are reused. The $210/$235 figures are the retired spot-rate plan.
- Must be pre-registered in a **new v1.5** before unblinding, with the new config hash. The current v1.3 draft uses 300/dataset and says it does not assume reuse. If v1.5 is not signed, Full is a full 32-row run at $210.

**G4/G5 pass:** placebo does not match B8; oracle separates; the sign reversal appears at the predicted q/ρ boundary; one external-validity check replicates the sign.

**Owner:** P2 + P4 + P5.

---

## ⬜ 10. Phase N8 — Human evaluation and SDT (Mar 2027)

**Scope:** 150–200 paired items, 3 raters; UWS/EWE/ARR taxonomy; citation faithfulness (300 pairs); expert ceiling (60 items); κ/ICC; SDT 3-axis for the paper, 6-axis for the thesis.

**Acceptance:** κ ≥0.60; the trust plane separates calibrated from sycophantic panels; the human labels support or qualify the automatic endpoints.

**Owner:** P5 + P4.

---

## ⬜ 11. Phase N9 — Law-testing and ablations (Apr 2027)

**Scope:** q sweep, ρ measurement/manipulation, granularity (claim vs document vs shuffled), shared-error floor, N/K/α/β robustness, natural-divergence subset.

**Rule:** run only if Core/Full show a real effect. R6 remains a **derived law** until an independent proof check signs it. This phase is **outside the $300 project compute envelope and hard stop**; no spend without a separate cost model and approval.

**Acceptance:** pre-registered contrasts; CIs; negative results reported. Results freeze at the end of April.

**Owner:** P1 + P4.

---

## ⬜ 12. Phase N10 — Thesis (May–Jun 2027)

**Scope:** full 6-arm matrix, 300–600 benchmark, 6-axis SDT, full proofs, SEA-Cert, negative results, accreditation, reproducibility.

**Milestones:** chapters 3/6/7/8 by May; internal review; **thesis submission June 2027; defence June/July 2027.** Do not force a paper deadline before the defence.

---

## ⬜ 13. Phase N11 — Paper (Aug–Dec 2027)

**Scope:** the sharp boundary/causal/benchmark paper from the thesis.

**Venue:** TACL rolling, EMNLP 2028, or a Q1 journal. TACL is the venue, not an experiment stage. No dual submission.

---

## 14. Budget and the $50 tranche

### 14.1 Use the current $50 first

| Priority | Item | Cost | Rule |
|---|---|---:|---|
| 1 | 18 GB test-only validation | **$0** | 8–9B AWQ one at a time; optional Q4_K_M main template |
| 2 | 80 GB A100 4-bit smoke | **$1–2** | **PASS 20 Nov 2026** — ran on 96 GB spot hosts (same 4-bit stack, vLLM 0.34.0); B8/injection/placebo 5/5, oracle 4/4 valid |
| 3 | Core-prefix gate: first 25–50 questions of the Core B8 and B8-no-trust rows | **~$1–2** | **COMPLETE 20 Nov 2026 — 25+25** (`gpqa_main` seed 1, same 4-bit stack); B8 accuracy 0.64 (16/25), control 0.56 (14/25); feasibility/timing only |
| 4 | Optional 25-question injection mini-gate | **<$1** | Not needed — prefix ran clean; run only if a later prefix is inconclusive |
| 5 | Optional 96 GB 5-question smoke | **$2–8** | **IN PROGRESS 20 Nov 2026** — FP8 stack downloaded, serving fixes applied, no result yet |
| — | Reserve for retries/bandwidth | **$35–45** | Do not spend on 96 GB pilot/precision |
| — | **Total** | **$5–15** | Leaves a real buffer |

**Pilot replacement.** The old **$15–20 / ~112 GPU-h pilot** was a 100–150-question calibration run, not the 25-item Month-1 criterion. It duplicated questions Core will run anyway. Replace it with the **Core-prefix gate**: run the first 25–50 questions of the actual Core `B8` and `B8-no-trust` rows with `--limit 400 --stop-after N`, compare paired winners, and resume the same rows only if trust changes the outcome in the correct direction. The prefix is part of Core, so the gate adds no separate GPU spend. The Month-1 25-item toy pilot remains a v1.0 requirement, but its questions file is not authored; if the team wants it, it costs <$1, not $15–20.

**Core-prefix result (20 Nov 2026).** `gpqa_main` seed 1, 25 debates per arm on the same 4-bit stack: B8 (trust-weighted) 25/25 unique records, accuracy 0.64 (16/25, 95% CI 0.44–0.84), MPR 0.790, MPR-weighted 0.64, ARR 0.722 (n=18), CCR 0.0 (0 exposed cases — expected, no pressure arms), CCR-e 0.133 (2/15), trust AUROC 0.568 (n=11), Brier 0.278, mean 245.5 s/debate (median 257.2); B8-no-trust (majority) 25/25 unique, accuracy 0.56 (14/25, CI 0.36–0.76), MPR 0.75, ARR 0.714, mean 185.5 s/debate. No duplicates, no torn lines. The +0.08 prefix delta at n=25 is noise — record as feasibility/timing, NOT efficacy. Mean ~4.1 min (B8) / ~3.1 min (control) per debate puts the full 2-seed Core at ~470 GPU-hours, ~$400–460 on an $0.80–0.86/h A100 80 GB on-demand, inside the $300 hard stop. Local mirror: `trustcal/results/n1a/` (gitignored). Full record: `experiments/core_prefix/README.md`.

**Next gates.** Parallel-code verification (order-preserving threaded calls; `TRUSTCAL_SERIAL=1` restores the serial loop), then Core tranche 1 on the next top-up. Funding arrives in ~$30 top-ups; the $300 hard stop stands. Host rental rules live in `AGENTS.md` ("Cloud GPU rental"); the host ledger is `docs/agent/08_COMPUTE_COST.md` Appendix B.

**Do not run with $50:**

- 96 GB pilot: **$37–45**.
- 96 GB FP8 precision: **$25–40**.
- Core: **$175–210**.
- Full: **$210** (or **~$104** with reuse).

### 14.2 Approved envelope

| Item | GPU-h | Cash |
|---|---:|---:|
| Core, all 24 rows (8,000 debates, incl. the 798 re-run) | 46.32 | **$69.48** |
| Full 36-row (6,000 new debates) | 34.74 | **$52.12** |
| Cap increase (3,200 debates) | 18.53 | **$27.79** |
| Three ablations (6,000 debates) | 34.74 | **$52.11** |
| FP8 precision (600 debates) | 3.47 | **$5.21** |
| Setup + ingress | 1.33 | **$2.56** |
| **Total (all-in)** | **139.13** | **$209.25** |
| **+ 10 USD headroom** | - | **219.25 USD** under the **220 USD** cap |
| **Hard stop** | — | **$300** |

### 14.3 Efficient path

With the free 18 GB tests and a signed Core → Full subset-reuse amendment:

| Item | Cost |
|---|---:|
| 18 GB tests | $0 |
| 4-bit smoke | $1–2 |
| Core-prefix gate | $0 extra (part of Core) |
| Core | $175–210 |
| Full incremental (16 reused rows) | ~$104 |
| 96 GB FP8 smoke | $2–8 |
| FP8 precision replication | $25–40 |
| Storage | $40–60 |
| **Total** | **~$345–445** |

Under $400 is possible with Core at the low end, storage around $40–60, and the A100 at $0.136/GPU-h. Those spot-rate figures are planning arithmetic only; the live ceiling is the **$300** project hard stop (24 Nov 2026). The $400 path is a planning option only after the reuse amendment is signed and a new ceiling is approved.

**Reuse is not authorized by the current v1.3 draft.** That draft sets Full to 300 items/dataset and says the envelope "does not assume reuse." Core uses 400/400/200. No row matches, so the 16-row reuse above requires a **new signed amendment (v1.5)** that sets Full `gpqa_main: 400`, `mmlu_pro: 400`, `sciclaim_180: 300`, adds the SciClaimBench loader, and records the new config hash. (v1.4 is the frozen B7-provider erratum.) Until then, budget Full at **$210** and the plan at **~$440–530**.

### 14.4 Bandwidth discipline

- Download Q4_K_M test files on the university host, one at a time; do not download them in the cloud.
- Cloud rentals download only the final AWQ/FP8 stack.
- Persist the cloud cache; batch pilot/Core/Full into long sessions; copy `results/` before destroying the instance.
- Storage/bandwidth stays **$40–80** until actual invoices replace the estimate.

**Hard stop: $300** (project total, ~$53 already spent). The two Full rows are alternatives; the total counts one Full run. The 96 GB fallback for the main matrix is **$1,050–1,150** and requires re-approval.

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
| `benchmark/MEMBER_GUIDE.md` | Member roles and annotation plan |
| `docs/GLOSSARY.md` | Core run / Full run / TACL naming |
| `PRE_REGISTRATION.md` | Frozen endpoints, arms, analysis, stopping rules |
| `docs/agent/03_EXPERIMENT_PLAN.md` | Power, design, benchmark details |
| `docs/agent/08_COMPUTE_COST.md` | Cost model, dev-slice offset, and $50 tranche |
| `experiments/p0/WAVE2.md` | P0 landing record |
| `trustcal/IMPLEMENTATION_STATUS.md` | What is wired vs approximate |
| `Journal_Paper/CLAIMS_AUDIT.md` | Journal claim changes |
| `FYDP_Report/CLAIMS_AUDIT.md` | Report claim changes |

---

## 18. Open decisions

| Decision | Default | Status |
|---|---|---|
| Server project directory | Dedicated `trustcal-fydp/`, not `tool-observation/` | approved |
| 18 GB test set | 8–9B AWQ first; Q4_K_M main templates optional | approved |
| 96 GB smoke timing | After stable 80 GB pilot, only if budget ≥$25 | proposed |
| Core → Full subset reuse | Draft v1.3 amendment before Core | needs sign-off |
| $400 efficient path | Only after reuse amendment and low-end storage | conditional |

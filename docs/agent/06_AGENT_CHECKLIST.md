# 06 — Agent Checklist (current board)

> Historical P0 board lives in `02_P0_FIXES.md`.

Work in this order and record commands plus exact output in `experiments/next/WP-<id>.md`. Order of work: `roadmap.md`; design: `03_EXPERIMENT_PLAN.md`.

**Status 24 November 2026.** Measured on one 96 GB on-demand RTX PRO 6000: **172.7 debates/h** with 8 concurrent rows and CUDA graphs, **$1.50/GPU-h all-in** — 3.3× the 52.2/h 2-way eager baseline (3 runs, ±3%). Test suite: **663** (`pytest -q`).

- [x] **N1.0 — 18 GB test gate (PASS).** 8–9B vLLM trio + Q4_K_M main templates with two mocks; 19 Nov revalidation on vLLM 0.34.0 with the exact 4-bit checkpoint configs. Cost **$0**. See `experiments/n1_smoke/`.
- [x] **N1a — 4-bit smoke (PASS 20 Nov 2026).** 53.26 GB stack on 96 GB hosts; B8/injection/placebo 5/5, oracle 4/4 valid. Cost **$1–2**. See `experiments/core_prefix/`.
- [x] **N1b — FP8 96 GB smoke (PASS 20 Nov 2026, serving).** Three servers, 73.68 GB loaded, B8 5/5 valid. Cost **$2–8**. The precision replication has not run.
- [x] **First Core row (`core3`, 21 Nov 2026).** `gpqa_main` seed 1, both arms: 798 debates, 15.3 GPU-h. Feasibility/timing only — B8 0.6241 vs control 0.5865 at n=399 is not an efficacy result.
- [x] **Concurrency and cost measurement (24 Nov 2026).** 172.7 debates/h at $1.50/GPU-h all-in; see `experiments/concurrency_test/`.
- [ ] **N2 — WP-18 placebo/oracle and v1.3 sign-off.** Implementation landed; freeze the Full definition and sign v1.3. Default 32 runs with a gold-evidence oracle on SciClaimBench, 36 runs with gold-answer trust as the alternate. Full is blocked until `sciclaim_180` has a loader entry and a frozen dataset; subset reuse needs a new v1.5.
- [ ] **N3 — Benchmark calibration (Nov 2026–Feb 2027).** 24-item calibration first; if clean, the 180-item **v1.2 freeze** (Core floor); 300-item Full target only if the 180 set is clean; 600 stretch; 800 no-go.
- [ ] **N4 — Verifier audit (Nov–Dec 2026).** 150–200 claim–passage pairs, 2 annotators. Target balanced accuracy ≥0.75, κ ≥0.60. Current lexical verifier: **0.58** on the synthetic audit.
- [ ] **N5/G2 — Pilot (Dec 2026–Jan 2027).** Baseline CCR ≥0.30; trust AUROC ≥0.65; ≥65% correct-direction changes; injection κ ≥0.75; no schema-invalid records. Gate on the Core prefix (first 25–50 Core B8/B8-no-trust questions, `--stop-after`) after a signed amendment.
- [ ] **G3 — Remaining Core rows (Jan–Feb 2027).** 22 of 24 rows (7,202 debates) remain, ~41.7 GPU-h at the measured rate. 4 conditions (B3, B4-matched, B8-no-trust, B8) × 3 datasets (`gpqa_main` 400, `mmlu_pro` 400, `hle` 200) × 2 seeds = 24 runs, 8,000 debates.
- [ ] **G4/G5 — Full run (Feb–Mar 2027).** 6-arm target; placebo ≠ B8; oracle separates; sign reversal at the predicted q/ρ boundary; external validity.
- [ ] **FP8 precision replication.** 600 debates, $5.21; same 96 GB card, 73.68 GB stack. Runs after the 4-bit Core.
- [ ] **SciClaimBench annotations.** 24 drafts are schema-valid (216 claims) with 0 human labels; the 180-item v1.2 freeze and the 300-item Full target depend on them.
- [ ] **Results freeze (Apr 2027).** CIs, negative results, pre-registered contrasts, manifest trace.
- [ ] **Thesis (Jun 2027), defence (Jun/Jul 2027), paper (Aug–Dec 2027).** No paper deadline before the defence.

**Remaining programme:** 21,800 debates = 126.2 GPU-h = **$189.36** GPU + **$2.56** setup = **$191.92**, inside the **$220** cap with **$20** headroom. Core+Full 12,000 = $104.23; cap increase 3,200 = $27.79; three ablations 6,000 = $52.11; FP8 precision 600 = $5.21. Price table and formulas: `08_COMPUTE_COST.md`.

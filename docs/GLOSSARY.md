# Experiment stage names

Use these names in all current plans, slides, and reports. Legacy labels appear once in parentheses; after that, use the plain name.

**Current budget (18 November 2026):** main matrix on one **80 GB A100 PCIe** at **$0.136/GPU-h**; free 18 GB test gate **$0**; 4-bit 80 GB smoke **$1–2**; pilot **$15–20**; Core **$175–210**; Full **$210** (32-row gold-evidence default) or **$235** (36-row gold-answer alternate); 96 GB 5-question FP8 smoke **$2–8**; FP8 precision replication **$25–40**; storage/bandwidth **$40–80**; **total $500–600**; **hard stop $600**. If the 80 GB A100 spot is unavailable and the main runs use 96 GB at **$0.336/GPU-h**, the plan is **$1,050–1,150** and requires re-approval. **$50 tranche:** 18 GB tests + 4-bit smoke + pilot, with $20–30 held for retries/bandwidth; no 96 GB pilot or precision. Source: `docs/agent/08_COMPUTE_COST.md`.

| Stage | Plain name | Question it answers | Scope | Cost |
|---|---|---|---|---|
| R2 | **Pilot run** | Does the pipeline run end to end and does trust move? | ~100–150 questions, injection, trust on/off; 4-bit 24–27B stack on the 80 GB A100 | $15–20 |
| R3 | **Core run** (legacy “C+”) | Does trust beat the matched controls? | 4 conditions (B3, B4-matched, B8-no-trust, B8) × GPQA-Main + MMLU-Pro + HLE × 2 seeds = 24 runs; 1,280 GPU-h conservative cap (planned ~1,067); 8,000 planned debates; 4-bit 24–27B stack on the 80 GB A100 | $175–210 |
| R4 | **Ceiling sweep** | Where is the sign reversal? | Re-aggregate existing debates under verdict noise; no new GPU | $0 |
| R5 | **Full run** (legacy “TACL full”) | Does the full 6-arm design replicate and generalize? | 6 arms × 3 datasets × 2 seeds; **default 32 runs** with a gold-evidence oracle on SciClaimBench (1,280 GPU-h); **alternate 36 runs** with gold-answer trust (1,440 GPU-h). The two are alternatives, not additions. | $210 default (32-row gold-evidence) / $235 alternate (36-row gold-answer); one Full run |
| R6 | **Hardware readiness (N1.0/N1a/N1b)** | Does the free 18 GB test path work, does the 4-bit stack serve, and does the FP8 stack serve? | N1.0: one 8–9B AWQ or Q4_K_M model + two mocks, $0. N1a: 4-bit 80 GB 5-question smoke, $1–2. N1b: FP8 96 GB 5-question smoke, $2–8, after the 4-bit pilot/Core. **NOT RUN.** Precision replication is separate. | N1.0 $0; N1a $1–2; N1b $2–8; precision $25–40 |
| R7 | **Law-testing** | Do the ρ, granularity, and shared-error laws hold? | Apr 2027, only if the effect is real; outside the $500–600 envelope and the $600 hard stop | Not in the current envelope; no spend authorized without a separate cost model and approval |

**Rules**

- **Full is a separate matrix.** Core and Full both run on the **4-bit 24–27B stack on one 80 GB A100 PCIe**, so cells are reusable only where model revisions, prompts, and configs match. The **18 GB slice is test-only**; the **96 GB FP8 stack** is only the N1b smoke plus the GPQA precision replication.
- **TACL is a venue** (*Transactions of the Association for Computational Linguistics*), not an experiment stage. Use “TACL” only when naming the submission target.
- **No “C+” or “TACL full” in new prose, slides, or tables.** If a historical audit needs the old label, write it once as `Core run (legacy “C+”)`.
- **The Full default is 32 rows with a gold-evidence oracle on SciClaimBench** (1,280 GPU-h / $210). **36 rows with gold-answer trust is the alternate** (1,440 GPU-h / $235). The total counts one Full run.
- **SciClaimBench is a v1.2 benchmark, not a Core dataset.** Core v1.0 runs GPQA-Main + MMLU-Pro + HLE; SciClaimBench freezes at 180 and scales to the 300-item Full target.
- Dates: N1.0 18 GB tests Nov 2026; N1a 4-bit smoke Nov–Dec 2026; WP-18/v1.3 Nov–Dec 2026; Pilot Dec 2026–Jan 2027; Core Jan–Feb 2027; N1b FP8 smoke Feb 2027; Full Feb–Mar 2027; Law-testing Apr 2027; thesis June 2027; defence June/July 2027; paper after defence Aug–Dec 2027.

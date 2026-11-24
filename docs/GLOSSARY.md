# Experiment stage names

Use these names in all current plans, slides, and reports. Legacy labels appear once in parentheses; after that, use the plain name.

**Current budget (measured 24 November 2026):** Core and Full run on one **96 GB class card** at **$1.50/GPU-h all-in**, measured at **172.7 debates/h** (8 concurrent rows + CUDA graphs), so Core + Full (12,000 debates) ≈ **69.5 GPU-h ≈ $104** and the full 21,800-debate programme ≈ **$192**. Free 18 GB test gate **$0**; 4-bit smoke **$1–2**; FP8 5-question smoke **$2–8** and precision replication **$25–40** (both costed at the retired $0.336/h; re-cost at $1.50/h before running); storage/bandwidth **$40–80**; **hard stop $600**. The 80 GB A100 at **$0.136/GPU-h**, Core **$175–210**, Full **$210/$235**, and the 1,280 GPU-h / 1,067 GPU-h arithmetic are the retired 9 November spot snapshot; 1,280 GPU-h survives only as the frozen pre-registration gate cap. Source: `roadmap.md` §14 and `experiments/concurrency_test/README.md`.

| Stage | Plain name | Question it answers | Scope | Cost |
|---|---|---|---|---|
| R2 | **Pilot run** | Does the pipeline run end to end and does trust move? | ~100–150 questions, injection, trust on/off; 4-bit 24–27B stack on the 96 GB card (or the Core prefix on the same rows) | ≈ $15–20 only for the full 112 GPU-h calibration; the prefix adds no separate spend |
| R3 | **Core run** (legacy “C+”) | Does trust beat the matched controls? | 4 conditions (B3, B4-matched, B8-no-trust, B8) × GPQA-Main + MMLU-Pro + HLE × 2 seeds = 24 runs; 1,280 GPU-h conservative gate cap (planned ~1,067 at the old 8 min/debate); 8,000 planned debates; 4-bit 24–27B stack on the 96 GB card | ≈ $62 remaining at 172.7 debates/h / $1.50 per GPU-h ($175–210 is the retired spot estimate) |
| R4 | **Ceiling sweep** | Where is the sign reversal? | Re-aggregate existing debates under verdict noise; no new GPU | $0 |
| R5 | **Full run** (legacy “TACL full”) | Does the full 6-arm design replicate and generalize? | 6 arms × 3 datasets × 2 seeds; **default 32 runs** with a gold-evidence oracle on SciClaimBench (1,280 GPU-h gate cap); **alternate 36 runs** with gold-answer trust (1,440 GPU-h gate cap). The two are alternatives, not additions. | ≈ $42 incremental at the measured rate ($210/$235 is the retired spot estimate); one Full run |
| R6 | **Hardware readiness (N1.0/N1a/N1b)** | Does the free 18 GB test path work, does the 4-bit stack serve, and does the FP8 stack serve? | N1.0: one 8–9B AWQ or Q4_K_M model + two mocks, $0 (PASS). N1a: 4-bit 5-question smoke (PASS 20 Nov 2026, 96 GB hosts). N1b: FP8 96 GB 5-question serving smoke (PASS 20 Nov 2026). Precision replication is separate and **NOT RUN**. | N1.0 $0; N1a $1–2; N1b $2–8 at the retired rate; precision $25–40 at $0.336/h (≈ $90–150 at $1.50/h) |
| R7 | **Law-testing** | Do the ρ, granularity, and shared-error laws hold? | Apr 2027, only if the effect is real; outside the $600 hard stop | Not in the current envelope; no spend authorized without a separate cost model and approval |

**Rules**

- **Full is a separate matrix.** Core and Full both run on the **4-bit 24–27B stack on one 96 GB class card**, so cells are reusable only where model revisions, prompts, and configs match. The **18 GB slice is test-only**; the **96 GB FP8 stack** is only the N1b smoke plus the GPQA precision replication.
- **TACL is a venue** (*Transactions of the Association for Computational Linguistics*), not an experiment stage. Use “TACL” only when naming the submission target.
- **No “C+” or “TACL full” in new prose, slides, or tables.** If a historical audit needs the old label, write it once as `Core run (legacy “C+”)`.
- **The Full default is 32 rows with a gold-evidence oracle on SciClaimBench** (1,280 GPU-h gate cap). **36 rows with gold-answer trust is the alternate** (1,440 GPU-h gate cap). The total counts one Full run. Measured cost at 172.7 debates/h / $1.50 per GPU-h: Core + Full ≈ 69.5 GPU-h ≈ $104; the $210/$235 figures are the retired 9 November spot estimate.
- **SciClaimBench is a v1.2 benchmark, not a Core dataset.** Core v1.0 runs GPQA-Main + MMLU-Pro + HLE; SciClaimBench freezes at 180 and scales to the 300-item Full target.
- Dates: N1.0 18 GB tests Nov 2026; N1a 4-bit smoke and N1b FP8 serving smoke PASSED Nov 2026; WP-18/v1.3 Nov–Dec 2026; Pilot Dec 2026–Jan 2027; Core Jan–Feb 2027; FP8 precision replication Feb 2027; Full Feb–Mar 2027; Law-testing Apr 2027; thesis June 2027; defence June/July 2027; paper after defence Aug–Dec 2027.

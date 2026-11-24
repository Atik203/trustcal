# Core prefix — first 25+25 Core debates (feasibility/timing gate)

**Status: COMPLETE 20 November 2026** — feasibility/timing only, not efficacy. **Phase:** N1a/N5. **Dataset:** `gpqa_main`, seed 1, first 25 of the Core `limit 400` rows per arm (`--stop-after 25`, same rows resume later).

## Objective

Run the first 25 questions of the actual Core B8 (trust-weighted) and B8-no-trust (majority) rows and cost the full Core from measured per-debate times. Pass condition: clean records with no duplicates or torn lines, plus a timing number the budget can use. The N1a 5-question smoke is the precondition for this prefix.

## Hosts and stack

RTX PRO 6000 96 GB spot hosts, vLLM 0.34.0, three 24–27B 4-bit models (53.26 GB stack). The run survived host restarts with disk intact and records checkpoint per question, so a stop costs time, not data. Host identities and rental lessons live in `docs/agent/08_COMPUTE_COST.md` Appendix B; rental rules live in `AGENTS.md` ("Cloud GPU rental"). Funding arrives in ~$30 top-ups; the $300 hard stop stands.

## N1a smoke (precondition, same stack)

B8 5/5 PASS (per-debate 414.9, 297.2, 272.4, 285.4, 228.0 s; accuracy 0.40); injection 5/5 PASS (129.2, 151.7, 105.3, 140.7, 159.6 s; one item showed a transient D→C→D change under injection, which motivated a fixed smoke check); B8-placebo 5/5 PASS (299.9, 255.4, 177.5, 265.8, 292.0 s); B8-oracle 4/4 valid records, all final answers correct (5th record lost to a spot eviction, not rerun).

## Core-prefix per-arm results

| Arm | Records | Accuracy | MPR | MPR-weighted | ARR | CCR / CCR-e | Trust AUROC / Brier | Mean s/debate |
|---|---|---:|---:|---:|---:|---|---:|---:|
| B8 (trust-weighted) | 25/25 unique | 0.64 (16/25, 95% CI 0.44–0.84) | 0.790 | 0.64 | 0.722 (n=18) | 0.0 (0 exposed) / 0.133 (2/15) | 0.568 (n=11) / 0.278 | 245.5 (median 257.2) |
| B8-no-trust (majority) | 25/25 unique | 0.56 (14/25, CI 0.36–0.76) | 0.75 | — | 0.714 | — | — | 185.5 |

No duplicates, no torn lines.

## Timing implication

Mean ~4.1 min (B8) / ~3.1 min (control) per debate put the full 2-seed Core at ~470 GPU-hours, ~$400–460 on an $0.80–0.86/h A100 80 GB on-demand, inside the $300 hard stop. (This serial estimate is superseded by the note below.)

> **Superseded (24 Nov 2026).** After CUDA graphs and 8-way concurrency the
> measured rate is **172.7 debates/h** at **$1.50/GPU-h all-in**, so the full
> 2-seed Core is ~46 GPU-h ≈ **$62**, not ~470 GPU-h. See
> `../concurrency_test/README.md`. The per-debate timings above remain the
> serial baseline.

## What this proves

- The 4-bit three-model stack serves concurrent debates and writes schema-valid records at Core settings.
- The `--stop-after`/resume prefix mechanics work: the same Core rows continue without a manifest change.
- Per-debate timing is measured, so the Core cost is arithmetic rather than a guess.

## What this does not prove

- No efficacy claim. The +0.08 prefix delta at n=25 is noise.
- No pressure behavior: CCR is 0.0 on 0 exposed cases, expected with no pressure arms in this prefix.
- No precision result: the FP8 smoke is in progress with no result yet; do not cite one.
- No 80 GB A100 serving proof: the prefix ran on 96 GB spot hosts, which the measured concurrency runs now treat as the default host class; a 53.26 GB stack fits 80 GB but has not been smoke-tested there.

## Local snapshot and next

Raw runs are local and gitignored under `trustcal/results/n1a/`; mirror them locally before any instance destroy. Next: parallel-code verification (order-preserving threaded calls, `TRUSTCAL_SERIAL=1` restores the serial loop), then Core tranche 1 on the next top-up. Do not run the 96 GB pilot or the FP8 precision replication from the current tranche.

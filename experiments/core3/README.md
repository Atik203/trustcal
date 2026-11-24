# core3 — gpqa_main seed 1, B8 vs B8-no-trust (resilient row)

**Status:** COMPLETE 21 Nov 2026 — 399 debates/arm (q27 quarantined of 400),
798 total. Both runners exited cleanly; summaries written 2026-11-21T07:29Z
(B8) / 07:42Z (control). The 27 records written before the resilience layer
were adopted, not re-run.

## Final result

| Metric | B8 (trust, n=399) | Control (majority, n=399) |
| --- | --- | --- |
| Final accuracy (95% CI) | 0.6241 (249/399, 0.576–0.672) | 0.5865 (234/399, 0.536–0.634) |
| Paired (both / B8-only / ctl-only / neither) | 208 / 41 / 26 / 124 | — |
| Exact McNemar | p = 0.086 (not significant) | — |
| MPR | 0.78 | 0.75 |
| ARR | 0.657 | 0.702 |
| CCR-e | 0.102 | 0.150 |
| Trust AUROC / Brier | 0.518 / 0.292 | — |
| Cost | 15.3 GPU-h; Vast invoice $32 for the row and its warm host; mean pair 138 s | - |

Host `61635389` (96 GB S, $1.59/h) is STOPPED, not destroyed (warm fallback,
~$0.71/day); credit left $2.67. Counts as 2 of 24 Core rows ≈ 800/8,000
debates (10%).

## Identity

| Field | Value |
| --- | --- |
| Dataset | `gpqa_main`, limit 400, seed 1, `fourbit` stack |
| Arms | `B8` (trust) and `B8-no-trust` (majority), run concurrently |
| Sample lock | `sample.lock.json`, hash `39c6b0ba…`, 400 questions |
| Condition (B8 / control) | `82ed383c…` / `a7d6c929…` |
| Parent commit | `b5faa10` (27-record prefix) |
| Adoption | `adoption.json`, parent manifest `b1f4620a…` / `0617060a…` |
| Provenance history | `manifest_history.jsonl` (one line per session, reason + operator) |

The 400-question parent sample is frozen in `parent_sample.json` (captured at
`b5faa10`) and `sample.lock.json`. A later loader change cannot shift this row.

## Resume

**RETIRED 21 Nov 2026 — row complete (399+399).** Host `61635389` is stopped
(warm fallback), both runners exited cleanly, and no resume is needed. The
commands below are kept for provenance only.

```bash
# after a host restart the vLLM servers are gone; restart the FOURBIT stack:
PHASE=fourbit bash scripts/serve.sh          # ~7 min; verify_env --check-servers = 3/3

.venv/bin/python scripts/run_experiment.py \
  --arm B8 --dataset gpqa_main --limit 400 --stop-after 400 --seed 1 \
  --phase fourbit --out results/core3 \
  --accept-provenance-change resilience-48fa2e0 --operator atik

.venv/bin/python scripts/run_experiment.py \
  --arm B8 --no-trust --dataset gpqa_main --limit 400 --stop-after 400 --seed 1 \
  --phase fourbit --out results/core3 \
  --accept-provenance-change resilience-48fa2e0 --operator atik
```

`stop_after` counts **written** records, so it is a success budget, not an
attempt budget. A resume starts at the first qid without a record.

## Quarantine

`quarantine.jsonl` is append-only. The summary counts only entries whose qid
still has no record.

- `gpqa_main-0027` — options are the literal letters `["c","a","b","d"]`; the
  record schema forbids a bare-letter gold. Pre-run quarantine, no debate spent.
- Five runtime entries from a session where the vLLM servers were dead; those
  qids were re-run successfully and no longer count as unresolved.

## Operational notes

- **`serve.sh` defaults to the `fourbit` phase now** (`phase.yaml`); `--phase dev` raises. Still pass `PHASE=fourbit` after a restart and check `verify_env --check-servers` shows the 24–27B checkpoints, in case an old snapshot or exported `PHASE` points elsewhere.
- vLLM processes do **not** survive a Vast stop/start; the model cache does.
- A code change under a live row requires
  `--accept-provenance-change "<reason>" --operator "<name>"`; the reason is
  written to `manifest_history.jsonl`. Condition changes (models, prompts,
  retrieval parameters, sample) are refused outright.
- A torn trailing JSONL line is truncated and that question is re-run; a bad
  middle line is fatal. Duplicate qids keep the first record.

## Timing and cost

Actuals: 798 debates at ~138 s mean per pair, 15.3 GPU-h on host `61635389`
(96 GB S, $1.59/h) → row spend **~$17–19**. The host is stopped, not
destroyed (~$0.71/day warm fallback); credit left $2.67.

(Superseded 30-record estimate: ~145 s per pair, ~$23–25 for the remaining
369 pairs.)

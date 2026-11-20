# core3 — gpqa_main seed 1, B8 vs B8-no-trust (resilient row)

**Status:** 30/400 records per arm. Question 27 is quarantined. The 27 records
written before the resilience layer were adopted, not re-run.

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

- **`serve.sh` defaults to the dev stack.** Without `PHASE=fourbit` it serves
  9–14B models and the run would be invalid. Always pass `PHASE=fourbit` after a
  restart and check `verify_env --check-servers` shows the 24–27B checkpoints.
- vLLM processes do **not** survive a Vast stop/start; the model cache does.
- A code change under a live row requires
  `--accept-provenance-change "<reason>" --operator "<name>"`; the reason is
  written to `manifest_history.jsonl`. Condition changes (models, prompts,
  retrieval parameters, sample) are refused outright.
- A torn trailing JSONL line is truncated and that question is re-run; a bad
  middle line is fatal. Duplicate qids keep the first record.

## Timing and cost

Measured on the 30 records: ~145 s per pair, ~$1.59/h → ~369 remaining pairs
(q31–q399; q27 stays quarantined) ≈ 15 h ≈ **$23–25**. The row resumes at the
first question id without a record; the 27 adopted records and the three smoke
records are never re-run.

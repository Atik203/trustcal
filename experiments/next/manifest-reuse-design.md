# Manifest reuse design — sample-locked rows with provenance history

**Status:** design only · no code edits · 20 November 2026
**Scope:** `trustcal` manifest, runner, record schema, analysis CLI.

## 1. Problem and requirements

A run directory is one manifest. `build_manifest` hashes config, models, prompt, dataset revisions, seed, temperature, and `code_commit`; every record carries `manifest_hash`; `check_resume` and `_check_record_hashes` refuse any drift. A code fix changes the commit, so a partial row (today: the two partial `core3` rows, 25 valid of 27 planned each, commit `b5faa10`) cannot resume without abandoning the work. The contract cannot tell a docs fix from a loader fix.

Requirements: auditable; no hash edits; opt-in; explicit consent; per-question provenance; existing metrics unchanged; refuse reuse when the scientific condition changed.

The controlling failure: commit `85c65ef` changed only `eval/datasets.py`, dropped 3 degenerate rows before sampling, and shifted the 400-question sample. A code-only diff is therefore **not** evidence that the sample is unchanged.

## 2. Designs considered

### A. Manifest whitelist / amendment
Declare accepted parent hashes plus a written reason; records keep their hashes; the summary lists imports.
**+** smallest change, no schema work. **−** it trusts the operator that a code-only diff is harmless. The `85c65ef` case would have been accepted and mixed two different samples under one row.

### B. Behavioral fingerprint
Hash prompt, model revisions, dataset revisions, trust/retrieval parameters, seed, and sampled question ids; record the commit but do not hash it.
**+** expresses "same experiment" directly. **−** the fingerprint is computed from the *current* loader. A loader change produces a different fingerprint, so the old row still cannot resume: it reports the break but does not preserve the row. Omitting one result-affecting input silently weakens the record.

### C. Per-question provenance strata
Allow mixed hashes, report metrics by hash and pooled, add a sensitivity check.
**+** required for audit and for any mixed row. **−** reporting only. It does not decide whether the mix is valid, and a prefix/suffix split is confounded with question order.

### D. Recommended: immutable sample lock + condition/provenance split
Freeze the exact sampled questions before the first debate; resume from the lock, never re-sample. Split the manifest into a `condition_hash` that must match and a `provenance_hash` that may change with consent. Report every provenance stratum. Legacy rows bootstrap through one explicit adoption record.

## 3. Recommended design

### 3.1 Data model

| File | Fields | Rule |
| --- | --- | --- |
| `sample.lock.json` | `schema`, `dataset`, `revision`, `source` (repo/split/loader), `sample_seed`, `limit`, `question_ids[]`, `questions[]` (full question/answer/options/stratum), `lock_hash` | written once, atomically; never regenerated |
| `condition.json` | `schema`, `condition_hash`, `condition` (dataset, `sample_lock_hash`, active model revisions, prompt hash, seed, decoding, trust/retrieval parameters, injection and arm-specific parameters, rounds, agents, arm, placebo/oracle mode), `created_at` | written once; must match on resume |
| `run_manifest.json` | today's full manifest | legacy audit artifact; first write only, never overwritten |
| `manifest_history.jsonl` | `session_id`, `started_at`, `condition_hash`, `provenance_hash`, `code_commit`, `worktree_dirty`, `code_diff_sha256`, `runner_version`, `operator`, `reason`, `records_before/after` | append-only, one line per session |
| `records.jsonl` | schema v2 + `condition_hash`, `provenance_hash` | append-only; `manifest_hash` stays untouched |
| `quarantine.jsonl` | `question_id`, `error_type`, `error`, `attempts`, `provenance_hash`, `timestamp` | append-only |
| `adoption.json` | legacy only: `parent_manifest_hash`, `parent_commit`, `sample_source`, `checks[]`, `reason`, `operator` | one per adopted parent hash |

`condition_hash = sha256(canonical(condition))`. It covers everything that changes what the debate is: dataset + lock hash + active model revisions + prompt hash + seed + decoding (temperature, max tokens, parser and option-renderer versions) + trust/retrieval parameters + injection/arm-specific parameters + rounds/agents + placebo/oracle mode.

`provenance_hash = sha256(canonical({code_commit, worktree_dirty, code_diff_sha256, runner_version, first_seen_at}))`. `first_seen_at` is the timestamp of the first session under that provenance; session start times live in `manifest_history.jsonl` and are not hashed, otherwise every ordinary resume would demand a new consent. The dirty-tree digest makes an uncommitted fix a distinct provenance instead of hiding under the same commit. `runner_version`, `parser_version`, and `renderer_version` are hand-bumped constants; a behavior change without a bump is a review defect, not a hashing problem.

### 3.2 CLI / API surface

```bash
python scripts/run_experiment.py ... --accept-provenance-change "fix: preflight only; lock verified" --operator "name"
python scripts/run_matrix.py ...    --accept-provenance-change "..."
python scripts/analyze.py --records <path> [--by-provenance]
python scripts/adopt_run.py --run-dir results/core3/B8/gpqa_main/seed1 \
    --parent-commit b5faa10 --parent-manifest-hash <sha256> \
    --reason "..." --operator "..."
python scripts/run_watchdog.py --stall-minutes 20 --max-restarts 5 -- \
    python scripts/run_experiment.py ...
```

`adopt_run.py` is for legacy directories without a lock. New runs never need it.

### 3.3 Validation rules

| Situation | Decision |
| --- | --- |
| empty run dir, no lock | sample, write the lock, validate, run |
| non-empty run dir, no lock | reconstruct the parent sample at the parent commit and verify every record; otherwise refuse |
| lock hash bad, ids duplicated, or a record qid absent from the lock | refuse |
| `--limit` ≠ `lock.limit` | refuse |
| `condition_hash` differs | refuse |
| `provenance_hash` differs, no flag | refuse and print the diff |
| `provenance_hash` differs, flag given | append one history entry, continue |
| record `question`/`gold`/`options_raw` differs from the lock | refuse |
| record condition hash not current and not covered by `adoption.json` | refuse |
| record `parser_version` differs from `condition.decoding` | refuse (re-scoring is not supported) |
| bad question (fresh or locked) | lock exists or is created; quarantine the qid, continue |
| duplicate qid | first valid record wins; audit entry; exit 2 |
| manifest/condition conflict | refuse; never overwrite the first manifest |
| disk full, lock corrupt, servers down | fatal; no quarantine |

### 3.4 Hook points

- `manifest.py`: add `build_condition`, `condition_hash`, `build_provenance`, `provenance_hash`; `check_resume` (manifest.py:93) becomes `check_condition`; keep `manifest_hash` for legacy records.
- `runner.load_questions` (runner.py:845): lock-first (see §4.1); the HF loader runs only when creating a lock.
- `runner.run` (runner.py:883-1097): build/verify condition before the loop; accept or refuse provenance; stamp both hashes on new records; wrap the per-question body in the quarantine classifier.
- `runner._append_record` (runner.py:205): `flush` + `os.fsync`.
- `runner._check_record_hashes` (runner.py:299): check `condition_hash`, not `manifest_hash`; allow legacy hashes listed in `adoption.json`.
- `runner._write_summary` (runner.py:773): add `condition_hash`, `sample_lock_hash`, provenance strata, quarantine count; keep `summarize()` output unchanged.
- `eval/records.py` (`validate_record`, records.py:155): optional `condition_hash` / `provenance_hash`; required for new records.
- `scripts/analyze.py` (`main`, analyze.py:168-246): group by condition and provenance; refuse mixed conditions; print strata plus pooled.
- `scripts/run_matrix.py` (`_build_plan`, run_matrix.py:218): pass the acceptance flag; add provenance to the matrix summary.

## 4. Row resilience: fail at 88, resume at 89

### 4.1 Immutable sample lock

On the first run, sample the questions, write `sample.lock.json` atomically (`*.tmp`, fsync, `os.replace`), then validate the locked list. Store the full question objects, not just ids, so a resume never calls the HF loader and never re-samples. Every resume verifies `lock_hash` and loads questions from the lock. A loader change therefore cannot shift the row; the 3 rows dropped by a later loader fix stay in the locked sample and are quarantined individually if invalid. For sample identity, refuse only when the lock is missing on a non-empty directory or the lock's own hash fails to verify. A different sample is a new run, never an import.

### 4.2 Two-level hashing

- **`condition_hash`** must match on resume. Covers dataset, lock hash, active model revisions, prompt hash, seed, decoding, trust/retrieval parameters, injection/arm-specific parameters, rounds/agents, placebo/oracle mode.
- **`provenance_hash`** may differ. Covers code commit, worktree state, runner version, and the stable first-seen timestamp. Every distinct value is recorded in `manifest_history.jsonl` and `summary.json`. A differing value requires `--accept-provenance-change "<reason>" --operator "<name>"`; both are stored verbatim.
- A record's stored hash is **never rewritten**. New records carry `condition_hash` and `provenance_hash` alongside the legacy `manifest_hash`; old records keep only what they were written with. Analysis uses `condition_hash` when present and the adoption map otherwise.

### 4.3 Question-level quarantine

Per-question handler with two classes:

- **Quarantinable:** schema/record validation failure, empty parser output, repeated LLM 5xx/timeouts after the client's retries, retrieval timeout, duplicate qid. Append a `quarantine.jsonl` entry and continue to the next question.
- **Fatal:** lock/condition mismatch, corrupt non-trailing JSONL line, disk full, all model servers down. Stop; do not quarantine.

Exit code 2 when any unresolved quarantine remains. Resume retries only missing and quarantined ids, in lock order, one attempt per session, so a permanently bad item stops at exit 2 instead of looping. The fresh-run order is sample → write lock → `validate_questions`; a bad qid is quarantined rather than aborting the row, so a loader defect cannot destroy the other 399 debates.

### 4.4 Torn-write recovery

`_append_record` writes one line, flushes, and calls `os.fsync`. On resume, every line is parsed and schema-checked. A **trailing** line that fails is truncated at its start via a temp file + `os.replace`, and that qid is retried. A non-trailing bad line is fatal; never silently drop it. The same trailing-truncation rule applies to `manifest_history.jsonl` and `quarantine.jsonl`. Duplicate qids: first valid record wins, later lines get a `duplicate_record` audit entry, and the originals are not deleted. A single-writer `.run.lock` (O_EXCL, released on exit) prevents two processes from appending to one row; the second exits 3 instead of producing duplicates. A per-record `*.tmp` + rename is possible but changes the storage format; append + fsync + trailing truncation is the minimal recovery contract.

### 4.5 Watchdog

`scripts/run_watchdog.py` launches the runner as a child and checks `records.jsonl` size/count every 60 s. If unchanged for `--stall-minutes`, it writes `diagnostics/<stamp>/` (`nvidia-smi`, `ps -eo pid,etime,pcpu,pmem,cmd`, `tail -200 results/logs/vllm-*.log`, `df -h`, `dmesg | tail` where permitted), terminates the child (TERM, then KILL), and restarts the same command. The runner resumes from the last valid record. Stop on exit 0 or 2, and after `--max-restarts`; exit 2 is quarantine, not a stall.

### 4.6 Failure matrix

| Failure | Detection | Where handled | Behavior | Exit |
| --- | --- | --- | --- | --- |
| LLM 5xx after retries | client exception | `VLLMClient` | quarantine qid, continue | 2 |
| retrieval timeout | retriever exception | `Retriever` | quarantine qid, continue | 2 |
| OOM (request) | 500 / OOM in log | client + server log | quarantine qid; watchdog captures log | 2 |
| OOM (server dead) | health check | preflight / watchdog | fatal; restart server, then resume | 4 |
| process crash | child exit | watchdog | restart; done ids skipped | 0/2 |
| host death | no process | operator + watchdog | new host, same mirrored run dir; resume from lock | 0/2 |
| disk full | `OSError` ENOSPC | `_append_record` | fatal before append; free space, resume | 4 |
| code change | provenance hash | `build_provenance` | require reason; append history; continue | 0 |
| sample change | lock hash / qid | `load_questions` | refuse; new run dir | 3 |
| bad question | validation / parser | `validate_questions` / quarantine | quarantine, continue (fresh or locked) | 2 |
| duplicate record | qid already done | `read_records` | first wins; audit entry | 2 |
| concurrent writer | `.run.lock` held | `runner.run` | refuse the second process | 3 |
| torn line | JSON parse | `read_records` | truncate trailing; retry qid | 0/2 |

Exit codes: `0` complete, `2` unresolved quarantine, `3` condition/lock refusal, `4` fatal infrastructure. The watchdog treats `0` and `2` as terminal.

### 4.7 Acceptance scenario

400-question locked row; crash after record 88; one torn line for 89; a code fix changes the commit; qid 120 fails schema.

1. Lock verifies; condition hash unchanged; provenance differs → `--accept-provenance-change "fix: ..."` appends one history entry.
2. Trailing torn line for 89 is truncated; the run starts at 89.
3. qid 120 is quarantined; the run continues to 400.
4. Final state: 399 valid records, 1 quarantine, 0 duplicates, exit 2. The summary reports 88 old-provenance + 311 new-provenance records plus pooled metrics.
5. Resume after fixing qid 120 retries only 120; exit 0.

Audit trail: `sample.lock.json` (400), `condition.json`, `manifest_history.jsonl` (2 entries), `quarantine.jsonl` (1), records with two provenance values, and the first 88 `manifest_hash` values unchanged.

## 5. Safety

- **No silent mixing:** a provenance change without the flag is refused; the accepted reason is written to the append-only history before the first new record. Records always carry their own hashes, and the summary lists counts per provenance.
- **Reader audit:** `sample.lock.json` shows the exact 400; `condition.json` shows what was held constant; `manifest_history.jsonl` shows every session, commit, and reason; `quarantine.jsonl` shows what did not complete; `records.jsonl` shows per-record provenance.
- **Manifest hash:** never rewritten. `run_manifest.json` is first-write-wins; subsequent sessions append to `manifest_history.jsonl`. There is no manifest conflict to resolve: a condition mismatch is a refusal, a provenance change is an append.
- **Sample change:** impossible after the lock exists. Before it exists, only exact reconstruction of the parent sample is allowed; otherwise the row is not reusable. The current loader's 397-row sample is never substituted for an old 400-row row.
- **Scope of consent:** only `provenance_hash` may be accepted. Any condition difference — model, prompt, seed, decoding, trust/retrieval, parser version, sample — is a hard refusal.

## 6. Test plan

**Unit**
1. Lock round-trip: stable `lock_hash`; reject duplicate/missing ids; reject `--limit` mismatch.
2. Condition hash changes for each input (dataset, lock hash, model, prompt, seed, temperature, parser version, alpha/beta, retrieval flags); stable when unchanged.
3. Provenance hash changes on commit or runner version; `check_condition` passes; no flag refuses; flag appends exactly one history entry.
4. Record validation: new records require both hashes; legacy records pass through the adoption map.
5. Quarantine: append, dedupe, retry order; exit 2 only when unresolved.
6. Torn line: only the trailing line is truncated; a middle bad line is fatal.
7. Duplicate qid: first wins, one audit entry, no deletion.
8. Adoption: refuses a condition difference beyond `code_commit`; refuses a missing/unverifiable parent sample; accepts a verified legacy prefix.

**Integration (mock vLLM)**
9. 10-question row, kill after 5, resume at 6, no duplicates.
10. Code change with a mock commit: resume requires the flag; the first 5 records and their hashes are byte-identical.
11. **Loader shift:** old loader yields 400, new loader yields 397. With a lock, resume starts at 89 and the row stays 400. Without a lock, adoption must either reconstruct the old 400 or refuse; it must never run the 397. Also assert that a direct resume without a lock and without reconstruction raises `SampleLockMismatch`.
12. Quarantine: qid 7 returns invalid schema; the run reaches 10, exit 2; resume retries only 7.
13. Watchdog: simulated stall, diagnostics directory written, child restarted, resume completes.

**Dry-run acceptance**
14. A 20-question mock row with a crash at 8, a torn line, a commit change, and one quarantined qid. Assert: 19 valid, 1 quarantined, 2 provenance strata, exit 2, no qid duplicated, `sample.lock.json` hash unchanged, and every pre-crash `manifest_hash` still present verbatim. Then resolve the quarantined qid and assert exit 0.

## 7. Migration: `core3` (`b5faa10`)

`core3` is in progress at `b5faa10`. If its rows were written at that commit they currently resume as-is; adopt **before the next code fix**, while the parent loader is still reproducible, because the fix is what would otherwise force a new row.

1. Run `adopt_run.py` once per run directory, in a **clean worktree at `b5faa10`** (or from a supplied `parent_sample.json`). It reproduces the parent 400-question sample and verifies every existing record's `question_id`, `question`, `gold`, and `options_raw`.
2. It writes `sample.lock.json` with the **parent** sample, `condition.json` with the current condition (only `code_commit` may differ), and `adoption.json` naming the old `manifest_hash`, the parent commit, the checks, the reason, and the operator. `run_manifest.json` and every record are left untouched.
3. Resume retries the missing/quarantined ids in lock order, then continues at qid 25. If a later loader fix drops 3 rows, those rows remain in the core3 lock; an invalid one is quarantined. The 397-row sample is never used for core3.
4. If the parent sample cannot be reproduced, or any record disagrees with it, adoption refuses. Finish the row on the old environment or start a new row; do not adopt the current loader's sample.
5. Each partial row is adopted separately because each has its own parent `manifest_hash`.

After adoption, `core3` is an ordinary locked row: condition changes refuse, provenance changes need a reason, and metrics report the pre-adoption and post-adoption records as separate strata plus pooled.

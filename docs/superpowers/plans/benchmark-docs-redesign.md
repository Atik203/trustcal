# Plan: Benchmark member docs redesign (easy English, one hub)

## Global Constraints
- Gate numbers never change: kappa >= 0.75, defect <= 0.15, H_attempt <= 2.0 h/item, unresolved <= 0.05. Verifier audit: kappa >= 0.60, balanced accuracy >= 0.75.
- Label vocab never changes: SciClaimBench `support`/`contradict`/`neutral`; verifier `supported`/`contradicted`/`unverifiable`. Exact lowercase.
- Safety rules stay: no gated text (GPQA/HLE/MMLU-Pro) in SciClaimBench; no AI markings in items (`draft_assisted` forbidden); gold = verified + adjudicated only; filled `*_initials` sheets stay local/private, never commit.
- Repo root is E:\FYDP. All member doc links must be repo-relative clickable paths that resolve (e.g. `tasks/01_RATER.md`, `../benchmark/...`). No dead links. Run validator `python benchmark/validate_items.py check --items benchmark/private/calibration_items.jsonl --expect 24 --strict` must still PASS after edits (docs only, no batch change).
- Style for all member docs: short sentences (1 idea each), easy words for non-native readers, one emoji per heading, levels like 🟢 Start / 🟡 Do / 🔴 Never, direct file links on every action. No duplicated long sections across files — write once, link to it.
- Do not touch `benchmark/private/` data, `benchmark/validate_items.py` logic, `benchmark/status.json`, `benchmark/schema.md` semantics. Docs only: `benchmark/README.md`, `benchmark/MEMBER_GUIDE.md`, `benchmark/tasks/*.md`, `benchmark/templates/*.md`.

## Task 1: Rewrite benchmark/README.md as the single START HERE hub
- File: `benchmark/README.md` only.
- Rewrite to: 1 title + 1 Start-here box with 3 clicks (Step 0 check, find your name, open your 1 pack). Per-member table with Name, Job (8 words max), Your file (clickable link), Due date (Prottoy/Salman/Yousuf Fri 4 Dec, Rakib+Limu Fri 11 Dec, Atik week of 14 Dec). Gate box with 4 numbers + 1 score command copy-paste. Three rules line. Keep protocol sections 1-10 below but shorten each to half length, simple sentences, keep all gate numbers and file paths exact.
- Must keep: batch table (24/180/300), gate table values, score command flags, assignment names Prottoy/Salman/Yousuf/Rakib+Limu/Atik.
- Verify: all `](...)` links resolve from `benchmark/`; validator PASS.

## Task 2: Rewrite benchmark/MEMBER_GUIDE.md in easy English
- File: `benchmark/MEMBER_GUIDE.md` only.
- Rewrite to max 200 lines: keep sections 0,1,2,4-8,9.3,9.4,9.5,10,11 only. Delete duplicate protocol text (link to hub instead). Each member section max 20 lines: 🟢 Your job (2 lines), 🟡 Do (3 bullets), 🔴 Never (3 bullets), ⏱ Time, 📂 Your file (clickable link). Keep practice rows 9.3/9.4 verbatim (5 rows each). Keep names + deadlines same as hub. Simple words, short sentences. Fix all `../benchmark/` self-links to `./...`.
- Must keep: 5 member roles, practice examples, blinding rules, timeline dates.
- Verify: all links resolve; no `Member [0-9]` refs; no stale `docs/MEMBER_GUIDE` self-links.

## Task 3: Simplify role packs 00-04 (deduplicate, same words)
- Files: `benchmark/tasks/00_OVERVIEW.md`, `01_RATER.md`, `02_ADJUDICATOR.md`, `03_AUTHOR.md`, `04_AGENT_PILOT.md`.
- For each pack: max 80 lines, same shape: 🎯 Goal (2 lines) → 📂 Your files (clickable paths) → 🟢 Steps (numbered, 1 action each, short) → 🔴 Never (3 bullets) → ✅ Done (checkboxes) → 🆘 Ask (1 line). Use identical label strings and decision order in 00/01/02. Delete duplicated codebook/glossary text — link to hub §4 instead. Add emoji + level labels. Keep every exact path, command flag, row count (216/180), hour budgets.
- Must keep: Step 0 python check (3 lines), blinding rules, effort format, escalation to Atik.
- Verify: links resolve; validator PASS; `check --expect 24 --strict` string present in 03_AUTHOR.

## Task 4: Simplify templates + final link sweep
- Files: `benchmark/templates/annotation_submission_checklist.md`, `benchmark/templates/item_verification_checklist.md`, `benchmark/templates/README.md`, `benchmark/templates/calibration_notes.md`. Plus link sweep over `benchmark/**/*.md` (excluding private).
- Shorten checklists to short sentences, emoji groups (📂 File / 🏷 Labels / 🙈 Blinding / 📤 Send). Keep every checkbox meaning (row counts 216/180, exact label strings, initials copy, private upload). Fix `templates/README.md` owner names to real names (no Member-N). Sweep: every `](...)` in-repo link must resolve; fix or remove dead ones. No data changes.
- Verify: link sweep script prints zero bad links; validator PASS; `git status --porcelain` shows only allowed docs files.

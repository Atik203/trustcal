# 04 — Benchmark owner: build the sheets, run the score, last

## What you are doing

Everything before this pack is human work: verify the drafts, label the sheets, adjudicate, review
defects. You run the mechanical parts around it — generate sheets, check structure, score the gate — and
you do it last, because none of it means anything until the human rows are real.

Agents may draft. They never produce a label, a gold verdict, or an adjudication.

## Your files

| What | Where |
| --- | --- |
| Item batch | [calibration_items.jsonl](../private/calibration_items.jsonl) |
| Blind sheets | [sheets/](../private/calibration/sheets/) |
| Gate state | [status.json](../status.json) — read `blocked_on` and `next_command` |
| Verifier codebook | [codebook](../private/verifier/codebook.md) |

## Steps

1. **Draft only.** One item at a time from the skeleton: question, three positions, 3–6 atomic claims each,
   candidate passages with locators and licences, candidate verdicts. Clean JSON, no AI markings. Every
   field is then verified by Yousuf.
2. **Build the blind sheets** after any authoring edit:

   ```bash
   python benchmark/validate_items.py sheets \
     --items benchmark/private/calibration_items.jsonl \
     --out benchmark/private/calibration/sheets
   ```

   Then confirm 216 rows, blank `verdict`/`confidence`/`notes`, and no gold, verifier or arm column. The
   sheets embed an `items_sha256`, so a stale sheet is detectable.
3. **Check structure:** `python benchmark/validate_items.py check --items <batch> --expect <N> --strict`,
   with 24 for calibration, 180 for the freeze, 300 for the full target. Fix schema errors only — never
   claim text, evidence, a verdict, or a licence.
4. **Take in the human files.** Members send filled sheets directly; you copy them to the plain names
   (`rater1.csv`, `rater2.csv`, `adjudication.csv`, `effort.csv`) in the sheet folder. A filled sheet never
   enters a commit. On the verifier sheets the rows carry neutral IDs (`vf-001` … `vf-180`); before you
   score that audit, translate them back with `benchmark_pair_map.csv` in the private verifier folder,
   because the scorer joins on the original `pair_id`. That map is the only record of the original IDs:
   never publish it. Build `effort.csv` from the raters' and adjudicators' effort files, keeping the
   `cal-*` rows (phases `rater1`, `rater2`, `adjudication`, `defect`); drop the `vf-*` verifier rows
   from that file and report them separately, or they would inflate the item count and deflate h/item.
5. **Score once every sheet is in**, using the exact `next_command` from `status.json`:

   ```bash
   python benchmark/validate_items.py score \
     --rater1 benchmark/private/calibration/sheets/rater1.csv \
     --rater2 benchmark/private/calibration/sheets/rater2.csv \
     --adjudication benchmark/private/calibration/sheets/adjudication.csv \
     --effort benchmark/private/calibration/sheets/effort.csv \
     --min-kappa 0.75 --max-defect 0.15 --max-hours 2.0 --max-unresolved 0.05
   ```

   Post the JSON and the exit code verbatim: `0` pass, `2` a gate failed, `1` an input is still incomplete.
   A failed gate is a finding.

Time: 1–2 h per batch cycle, plus the waiting. Due Fri 18 Dec 2026.

## Never

- Never label a claim, adjudicate a row, or set a gold verdict yourself — route those to the human owner.
- Never score before every human sheet is in, and never quietly fix a verdict to pass a gate.
- Never commit a filled sheet, an item with AI markings, or a private file.

## Done when

- [ ] No item carries AI markings; no agent output became a verdict without a human check.
- [ ] Blind sheets verified: right row count, blank label columns, no leak column.
- [ ] Every human file received, renamed and stored outside git.
- [ ] Score output pasted verbatim with its exit code; gate numbers posted to the team.

## Ask

Blocked on a file → the group. A label definition → you own it, and changing it starts a fresh batch.
Licence doubt → Rakib + Limu.

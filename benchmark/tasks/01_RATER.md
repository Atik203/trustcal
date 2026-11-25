# 01 — Rater: label two blind sheets, row by row

## What you are doing

You get two spreadsheet sheets. Each row is one scientific claim plus the passages retrieved for it. You
read both and type one label saying whether the passages back the claim. You do this alone, and so does
the other rater. How often you two agree is the number the whole project is waiting on (κ ≥ 0.75).

New to this? [`MEMBER_GUIDE.md`](../MEMBER_GUIDE.md) has a filled row, six practice rows and the five
mistakes to avoid. Ten minutes there saves hours here.

## Your files

| What | Where | Rows |
| --- | --- | --- |
| SciClaimBench sheet | [rater1.csv](../private/calibration/sheets/rater1.csv) (Prottoy) or [rater2.csv](../private/calibration/sheets/rater2.csv) (Salman) | 216 |
| Verifier audit sheet | [rater1.csv](../private/verifier/sheets/rater1.csv) (Prottoy) or [rater2.csv](../private/verifier/sheets/rater2.csv) (Salman) | 180 |
| Verifier rules | [codebook](../private/verifier/codebook.md) | one page |
| Effort log | [effort.template.csv](../annotation/effort.template.csv) — copy it, never fill it in place | one line per item |
| Submission checklist | [annotation_submission_checklist.md](../templates/annotation_submission_checklist.md) | — |

## Steps

1. Open the SciClaimBench sheet in Excel, LibreOffice, or Google Sheets. Confirm the header has no
   `gold_verdict`, no `verifier_label`, no answer column. If one appears, stop and tell Atik.
2. Count the rows: `=COUNTA(A:A)-1` must give 216. A raw line count lies, because cells contain line
   breaks.
3. Label top to bottom, one row at a time. Fill the **`verdict`** column on SciClaimBench and the
   **`label`** column on the verifier sheet — different columns, different spellings, on purpose. Add a
   confidence: 0.9 when the passages decide it plainly, 0.5 when you are arguing with yourself. A **hard
   row** is one where two passages pull in different directions, the claim is ambiguous, or a locator is
   missing; those get a short note.
4. Decide in this order: **contradiction first** (any passage refutes the claim → `contradict`), then
   **support** (at least one passage states it and none refutes it), else **neutral**. A reported null
   result — "no significant difference" — is a refutation when the claim asserts the effect. Verifier
   wording: `supported` · `contradicted` · `unverifiable`.
5. Log minutes as you go. **One line per item**, so 24 lines for the SciClaimBench sheet, not 216, and one
   line per pair on the verifier sheet. The effort file columns are `item_id,phase,minutes,annotator,notes`:
   - `item_id`: `cal-001` … `cal-024` on SciClaimBench; the `pair_id` value on the verifier sheet.
   - `phase`: exactly one of `rater1`, `rater2` (SciClaimBench) or `verifier1`, `verifier2` (verifier sheet).
   - `annotator`: your initials, `PR` or `SA`.
   - `minutes`: whole minutes actually spent, breaks excluded.

   Example: `cal-001,rater1,22,PR,"slow first pass"`. If one item takes several sittings, add its minutes
   into the same line.
6. Save as CSV UTF-8, one file per sheet, and finish the checklist:
   - SciClaimBench: `rater1_sci_PR.csv` or `rater2_sci_SA.csv`
   - Verifier audit: `rater1_ver_PR.csv` or `rater2_ver_SA.csv`
   - Effort: `effort_PR.csv` or `effort_SA.csv`

   **Send all of them to Atik** (WhatsApp or Drive) and post the filenames and row counts in the team
   group. Contact details are deliberately not in this public folder: use the team group you already have,
   or ask Atik in person. Never write into the blank sheet or into `private/`, and never commit a filled
   file.

Time: 5–7 h per 216-row sheet once practised (8–10 h the first time), plus 5–6 h for the verifier sheet.
Due dates: verifier sheet Fri 4 Dec 2026, SciClaimBench sheet Fri 11 Dec 2026.

## Never

- Never open any file under `private/` except the two blank sheets you were given. That includes
  `private/calibration_items.jsonl`, `private/calibration_*.jsonl`, `private/freeze180/`,
  `private/full300/` and `private/pilot/` — all of them carry gold verdicts.
- Never open the other rater's sheet, and never open the verifier answer key (Atik holds it outside this
  folder).
- Never use outside knowledge or an AI tool for a label. Only the printed passages decide.
- Never discuss single rows before both sheets are in.
- Never leave a row blank and never change a label after seeing the other sheet.

## Done when

- [ ] Every row has a label from the exact allowed strings, plus a confidence; hard rows have notes.
- [ ] No blanks, no added or removed columns, header untouched.
- [ ] Effort lines logged for every item and every verifier pair.
- [ ] One file per sheet plus the finished checklist sent to Atik; filenames and row counts posted.

## Ask

A row you cannot decide, a missing file, a broken passage → Atik in the group. A definition question →
Atik. After the sheets are in, adjudication questions → Rakib + Limu.

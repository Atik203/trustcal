# 02 — Adjudicator: settle the disagreements, run the defect review

## What you are doing

Two raters labelled the same rows, alone. Where they agree, the label stands. Where they disagree, you
decide from the passages and write a one-line reason. Later you review every adjudicated row that you did
not label yourself and flag the wrong ones. You never see the gold answer, so the reference set stays
honest.

New to the task? [`MEMBER_GUIDE.md`](../MEMBER_GUIDE.md) §3 shows how one label is decided. The label
definitions in the [verifier codebook](../private/verifier/codebook.md) apply to your rows too, but that
codebook names the rater column `label`; on your file the same value goes in `human_label`.

## Your files, and the columns each one has

| What | Where | Rows |
| --- | --- | --- |
| SciClaimBench adjudication | [adjudication.csv](../private/calibration/sheets/adjudication.csv) | 216 |
| Verifier adjudication | [adjudication.csv](../private/verifier/adjudication.csv) | 180 |
| Effort log | [effort.template.csv](../annotation/effort.template.csv) — copy it | one line per row you decide |
| Label rules | [SciClaimBench](../README.md) §5 · [verifier codebook](../private/verifier/codebook.md) | — |

The two files use different column names for the same job:

| What you record | SciClaimBench sheet | Verifier sheet |
| --- | --- | --- |
| rater 1's label | `rater1_verdict` | `rater1_label` |
| rater 2's label | `rater2_verdict` | `rater2_label` |
| did they agree | `agreement` | `agreement` |
| your final label | `adjudicated_verdict` | `human_label` |
| your one-line reason | `adjudication_notes` | `adjudication_notes` |
| defect flag | `defect_flag` | `defect_flag` |
| defect type | `defect_type` | `defect_type` |

Allowed values: `agreement` = `yes` or `no`. `defect_flag` = `true` or `false`. `defect_type` = one of
`wrong-verdict`, `unsupported`, `non-atomic`, `bad-evidence`, `leak`, or blank when the flag is `false`.
`unresolved` goes in the final-label column (`adjudicated_verdict` or `human_label`) — it is a legal value
there and nowhere else. Leave the sheet's own `verdict`, `confidence` and `notes` columns **blank**: they
belong to the rater round and were exported empty on purpose.

## Steps

1. **Wait for both rater sheets.** Start only when both are in Atik's hands, and work from the copies Atik
   gives you. Do not ask the raters about individual rows.
2. **Copy the two labels** into the columns above. Where they match, write `yes` in `agreement` and copy
   the agreed label into the final-label column unchanged. Agreement rows are not yours to improve.
3. **Decide each disagreement** from the claim and its passages only, in this order: contradiction first
   (any refuting passage → `contradict`), then support (at least one passage states it and none refutes →
   `support`), else `neutral`. A reported null result — "no significant difference" — contradicts a claim
   that asserts the effect. Verifier wording: `supported` · `contradicted` · `unverifiable`. Write one line
   in `adjudication_notes` naming the deciding passage.
4. **Mark hopeless rows `unresolved`** — passages cut off or missing, a claim nobody could judge, two
   passages that cannot both be right. List them in your report and count them: unresolved ÷ adjudicated
   must stay at or below 0.05 or the freeze blocks. Never delete the row.
5. **Log your time** in the effort file, one line per row you decide, phases `adjudication` and `defect`:
   `cal-001,adjudication,6,RK,"tie-break"`. Your hours are part of the 2.0 h/item gate.
6. **Defect review, after adjudication and before anything is frozen.** Review **all 216** calibration
   rows — the ones you did not label as a rater — and set `defect_flag` and `defect_type` on each. The
   published defect rate is flagged rows ÷ 216, which is exactly what the scorer computes, so review
   everything rather than a sample. Fixes made before the freeze are rework, not defects.
7. **Send both files, your effort log and the counts** (agreements, disagreements, unresolved, defects) to
   Atik. He runs the score last; you never score your own adjudication.

Time: 5–7 h adjudication plus 2–3 h verifier adjudication plus 3–4 h defect review, shared between the two
of you. Due Wed 16 Dec 2026.

## Never

- Never open the drafted items (`private/calibration_items.jsonl`, `private/calibration_*.jsonl`,
  `private/freeze180/`, `private/full300/`, `private/pilot/`) or the verifier's own label. You read the two
  rater sheets; you never read the answer key.
- Never relabel an agreement row, delete an unresolved row, or adjust a label to raise κ.
- Never change a label definition alone. That call belongs to Atik, and it starts a fresh batch.
- Never commit a filled sheet or write into the blank one.

## Done when

- [ ] Both rater labels copied verbatim into every row, `agreement` set on every row.
- [ ] Every disagreement has a final label and a one-line reason naming the passage.
- [ ] Unresolved rows listed and counted (≤ 5%).
- [ ] `defect_flag` and `defect_type` set on all 216 rows; counts posted.
- [ ] Both files plus the effort log sent to Atik.

## Ask

A row you cannot settle, a suspected leak, personal data in a passage → Atik privately, never a public
issue. Verifier-audit rules → its [codebook](../private/verifier/codebook.md), then Atik.

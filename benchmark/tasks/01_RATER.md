# 01 — Rater pack: label blind sheets row by row

**Task:** independently label every claim in your blind sheet against the cited passages only. Your sheet plus the second rater's sheet is the κ gate (≥ 0.75).

**Never open `benchmark/private/items/` or any `cal-*.json` file.** Item files contain the gold answers — opening one destroys your blinding for those rows. Work ONLY from your sheet's `claim` + `evidence_text` columns. If you open one by accident, tell Atik immediately and those rows get reassigned.

## Steps

1. Get your sheet (already in the repo — no bundle needed for raters). Confirm the filename and row count before starting.
   - SciClaimBench: `benchmark/private/calibration/sheets/rater1.csv` (**Prottoy**) or `rater2.csv` (**Salman**). Expect 216 data rows + 1 header line (24 items × 9 claims). Count rows in Excel with `=COUNTA(A:A)-1` and expect 216 — do not trust line counts (multiline cells lie).
   - Verifier audit: `experiments/verifier_audit/private/scifact/sheets/rater1.csv` (**Prottoy**) or `rater2.csv` (**Salman**). Expect 180 data rows + 1 header line.
2. Confirm blinding: your sheet must have **no** `gold_verdict`, `verifier_label`, or arm column. If you see one, stop and tell Atik.
3. Label row by row, top to bottom, in one or two sittings per batch. For each row fill exactly three columns: verdict, confidence (0–1), notes.
   - SciClaimBench labels: `support` · `contradict` · `neutral` (exact lowercase).
   - Verifier labels: `supported` · `contradicted` · `unverifiable` (exact lowercase — different words on purpose).
4. Apply the decision order to **every** row:
   1. If **any** cited passage refutes the claim as written → `contradict` (refutation wins even if another passage supports).
   2. Else if **at least one** passage entails the claim → `support` / `supported`.
   3. Else → `neutral` / `unverifiable`.
5. Log effort as you go (sheet `effort.csv` columns `item_id,phase,minutes,annotator,notes`): one row per item with `phase=rater1` (or `rater2`). `annotator` = your initials. Example row: `cal-001,rater1,22,AB,"steady pace"`. Time with your phone — one start/stop per item, no stopwatch stress. This feeds H_attempt ≤ 2.0 h/item.
6. Submit: save a copy with your initials (`rater1_<initials>.csv`), complete `benchmark/templates/annotation_submission_checklist.md`, upload to the private folder, post filename + row count in the team channel. Do not edit the original batch.

## Worked example (SciClaimBench labels; same logic applies to verifier labels)

Claim: "Drug X reduced systolic blood pressure by 12 mmHg versus placebo."

| # | Cited passage | Your label | Why |
| --- | --- | --- | --- |
| 1 | "Systolic pressure fell 12 mmHg in the Drug X arm and 1 mmHg in the placebo arm." | `support`, conf 0.9 | passage states the relation and the number |
| 2 | "In the trial, systolic pressure fell 12 mmHg on Drug X; heart rate was not reported." Claim also says "...and increased heart rate." | `neutral`, conf 0.8 | compound claim, only one part supported — split would be two claims; as written, not established |
| 3 | "The reaction reached 212 °F." Claim: "The reaction released 100 °C of heat." | `support`, conf 0.85 | numbers agree after unit conversion (212 °F = 100 °C) |

## Common mistakes (do not do these)

- Treating topical overlap as support ("mentions Drug X" ≠ "states the effect") → `neutral`.
- Marking a half-supported compound claim as `support` → `neutral`, note "compound, part unsupported".
- Ignoring a refuting passage because a supporting one exists → refutation always wins → `contradict`.
- Using outside knowledge ("I know this drug works") → judge cited passages only.
- Mixing label sets (`supported` in a SciClaimBench sheet or vice versa) → exact strings only.
- Leaving blanks, adding/deleting columns, changing the header → every row gets a label.

## When to flag vs guess

- **Flag (low confidence + note, still label):** ambiguous wording, two passages in tension, unit/negation doubt, locator won't resolve, same-name trials you can't tell apart (e.g. WOMAN vs WOMAN-2 — judge the cited passage only, never Google it). Example note: "e2 seems to refute; conf 0.4; needs adjudication." A flagged row stays in your sheet — the notes column IS the escalation path; nothing goes anywhere else.
- **Never guess silently.** A low-confidence label with a clear note is correct behavior; a silent guess is a defect risk.
- **Stop and escalate (do not label):** sheet contains gold/verifier labels, row count mismatch, passages missing entirely, you recognize an item you verified, suspected PII. Tell Atik.

## Inputs → outputs

- In: your blind `rater1.csv`/`rater2.csv` (in the repo) + codebook (`benchmark/README.md` §§4–5; verifier codebook arrives with the verifier round — Atik gives it to you, do not start it yet).
- Out: `rater1_<initials>.csv` / `rater2_<initials>.csv` (every row labelled — save a COPY with your initials, never overwrite the original) + `effort.csv` rows + `submission_<initials>.md` checklist → the shared private folder Atik points you to (ask Atik for the upload location on day 1; never commit, never email).

## Hour budget (honest numbers)

- SciClaimBench sheet (216 rows): 5–7 h practiced (2 min/row); 8–10 h on your first sheet — normal, still inside the gate.
- Verifier 180-pair sheet: another 5–6 h. Do calibration first; Atik starts the verifier round after calibration sheets are in (Prottoy and Salman each label both — same skill, no blinding conflict across datasets).
- Pace: 2–4 min/row once practiced; your first ~10 rows will be slower. Errors rise at the end, so slow down for the final 30 rows instead of rushing them.
- You do NOT need statistics: never compute anything. Judge words against words — "lower than" in the passage beats "reduces" in the claim; a rate ratio with CI crossing 1.0 and p > 0.05 means "no clear effect", not support. If numbers confuse you, flag the row (low confidence + note) and move on.
- Excel survival: open your sheet ONLY by its exact filename; count rows with `=COUNTA(A:A)-1` and expect 216 (multiline cells make plain line counts lie); never add comment lines above the header; always Save As a new `raterN_<initials>.csv`, never Save over the original.

## Done-criteria checklist

- [ ] Every row has a verdict (exact string), confidence, and a note on every hard row.
- [ ] No blank labels, no added/deleted columns, header unchanged.
- [ ] Effort rows logged (phase `rater1`/`rater2`, minutes per item).
- [ ] Submission checklist signed; file uploaded privately; filename + row count posted.
- [ ] Did not open the other rater's sheet, gold, verifier label, or arm map; did not discuss rows before both sheets are in; did not use an LLM for labels.

## Escalation

Batch/blinding/submission → Atik. Codebook ambiguity → Atik. Adjudication question → Rakib + Limu. PII/private-data concern → Atik privately, never a public issue.

# 01 — Rater pack: label blind sheets row by row

**Task:** independently label every claim in your blind sheet against the cited passages only. Your sheet plus the second rater's sheet is the κ gate (≥ 0.75).

## Steps

1. Get your sheet from Member 2 in the private folder. Confirm the filename and row count before starting.
   - SciClaimBench: `benchmark/private/calibration/sheets/rater1.csv` (Member 4) or `rater2.csv` (Member 5). Expect ~216 rows (24 items × 9 claims), not 24.
   - Verifier audit: `experiments/verifier_audit/private/scifact/sheets/rater1.csv` (Member 2) or `rater2.csv` (Member 4). Expect 180 rows.
2. Confirm blinding: your sheet must have **no** `gold_verdict`, `verifier_label`, or arm column. If you see one, stop and tell Member 2.
3. Label row by row, top to bottom, in one or two sittings per batch. For each row fill exactly three columns: verdict, confidence (0–1), notes.
   - SciClaimBench labels: `support` · `contradict` · `neutral` (exact lowercase).
   - Verifier labels: `supported` · `contradicted` · `unverifiable` (exact lowercase — different words on purpose).
4. Apply the decision order to **every** row:
   1. If **any** cited passage refutes the claim as written → `contradict` / `contradicted` (refutation wins even if another passage supports).
   2. Else if **at least one** passage entails the claim → `support` / `supported`.
   3. Else → `neutral` / `unverifiable`.
5. Log effort as you go (sheet `effort.csv` columns `item_id,phase,minutes,annotator,notes`): one row per item with `phase=rater1` (or `rater2`) and your minutes. This feeds H_attempt ≤ 2.0 h/item.
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

- **Flag (low confidence + note, still label):** ambiguous wording, two passages in tension, unit/negation doubt, locator won't resolve. Example note: "e2 seems to refute; conf 0.4; needs adjudication."
- **Never guess silently.** A low-confidence label with a clear note is correct behavior; a silent guess is a defect risk.
- **Stop and escalate (do not label):** sheet contains gold/verifier labels, row count mismatch, passages missing entirely, you recognize an item you verified, suspected PII. Tell Member 2.

## Inputs → outputs

- In: blind `rater1.csv`/`rater2.csv` from Member 2 (private folder) + codebook (`benchmark/README.md` §§4–5, verifier `sheets/codebook.md`).
- Out: `rater1_<initials>.csv` / `rater2_<initials>.csv` (every row labelled) + `effort.csv` rows + `submission_<initials>.md` checklist → private folder.

## Hour budget

- SciClaimBench sheet: 5–7 h (Member 5) / 8–10 h incl. verifier sheet (Member 4).
- Verifier 180-pair sheet: 5–6 h. Pace ≈ 2 min/row; take breaks; do not rush the last 30 rows.

## Done-criteria checklist

- [ ] Every row has a verdict (exact string), confidence, and a note on every hard row.
- [ ] No blank labels, no added/deleted columns, header unchanged.
- [ ] Effort rows logged (phase `rater1`/`rater2`, minutes per item).
- [ ] Submission checklist signed; file uploaded privately; filename + row count posted.
- [ ] Did not open the other rater's sheet, gold, verifier label, or arm map; did not discuss rows before both sheets are in; did not use an LLM for labels.

## Escalation

Batch/blinding/submission → Member 2. Codebook ambiguity → Member 1 (copy Member 2). Adjudication question → Member 6. PII/private-data concern → Member 1 privately, never a public issue.

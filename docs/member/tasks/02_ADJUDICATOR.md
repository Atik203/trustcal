# 02 — Adjudicator pack: resolve disagreements, run defect review

**Task:** turn two independent rater sheets into one defensible reference without ever seeing the gold/verifier label. You own disagreements; you do not relabel agreements to raise κ.

## Steps

1. Wait until **both** rater sheets are submitted. Open the adjudication workbook only then.
   - SciClaimBench: `experiments/calibration/private/calibration/sheets/adjudication.csv`.
   - Verifier: `experiments/verifier_audit/private/scifact/audit_sheet.csv` (master sheet — never send to raters; it carries the verifier label).
2. Copy labels mechanically first: fill `rater1_verdict` / `rater2_verdict` (SciClaimBench) or `rater1_label` / `rater2_label` (verifier) from the submitted sheets. Agreement rows: copy the agreed label into `adjudicated_verdict` / `human_label` — do not invent a new one.
3. For every disagreement row, re-read the claim + cited passages and apply the codebook decision order (contradict first, then support, otherwise neutral). Fill `adjudicated_verdict` (`support`/`contradict`/`neutral`, or `unresolved`) plus a one-line `adjudication_notes` / `notes` rationale citing the deciding passage (e.g. "e2 refutes dose; contradict per refutation-first rule").
4. Mark `unresolved` only when no verdict is defensible from the passages (missing evidence, locator dead, passages contradict each other on the same fact). Count them: unresolved ÷ adjudicated claims must stay ≤ 0.05 or the freeze blocks.
5. Defect review (after adjudication, Member 3 + Member 6 on items neither labelled): open each frozen triple against its passages, fill `defect_flag` (TRUE/FALSE) + `defect_type` (taxonomy below). Pre-freeze corrections are **rework**, not defects — only post-freeze wrong/unsupported triples count. Defects ÷ frozen triples ≤ 0.15.
6. Submit the completed workbook to the private folder; post row counts (agreements / disagreements / unresolved / defects). Member 1 runs the `score` command — you never score your own adjudication.

## Defect taxonomy (`defect_type`)

| Code | Meaning | Example |
| --- | --- | --- |
| `wrong-verdict` | gold/adjudicated verdict contradicts the passages under the decision order | passage refutes but verdict says `support` |
| `unsupported` | no cited passage establishes or refutes; verdict claims otherwise | `support` on topical-only passage |
| `non-atomic` | claim bundles two propositions; verdict holds for only one part | "lowers BP and raises HR" with HR unreported |
| `bad-evidence` | locator dead, passage misquoted, licence missing, gated text pasted | DOI doesn't resolve; GPQA text copied |
| `leak` | gold/verifier/arm label visible in a blind sheet | `gold_verdict` column in `rater1.csv` |

## Send back vs fix

- **Fix yourself (adjudication workbook only):** verdict choice, rationale wording, agreement-row copy, defect flags on triples you review.
- **Send back to Member 1 (never edit item source):** dead locators, missing passages, non-atomic claims needing splits, suspected gated-text copy, licence gaps, blinding leaks, unresolved rate trending above 5%. Return a written problem list with `claim_id`s; Member 1 edits and regenerates sheets.
- **Never:** open gold/verifier labels while adjudicating; delete an unresolved row; relabel to raise κ; change the codebook unilaterally (needs Member 2 + Member 1).

## Inputs → outputs

- In: submitted `rater1.csv` + `rater2.csv`, codebook (`experiments/calibration/README.md` §§4–5), effort rows.
- Out: filled `adjudication.csv` (`adjudicated_verdict`, `adjudication_notes`, `defect_flag`, `defect_type`) / verifier `audit_sheet.csv` (`human_label`, `confidence`, `notes`) → private folder. Unresolved rows listed, not deleted.

## Hour budget

- SciClaimBench adjudication: 5–7 h. Verifier adjudication: 2–3 h. Defect review: 3–4 h (Member 3). Pace ≈ 5 min/disagreement row.

## Done-criteria checklist

- [ ] Every row has `rater1/2` labels copied verbatim; every disagreement has an adjudicated verdict + one-line reason.
- [ ] Agreement rows copy the agreed label (no new verdicts).
- [ ] Unresolved rows marked `unresolved`, counted, reported (≤ 5%).
- [ ] Defect columns filled on every frozen triple reviewed; defect rate computable (≤ 15%).
- [ ] Never opened gold/verifier/arm labels; no rows deleted; workbook in private folder with counts posted.

## Escalation

Codebook ambiguity → Member 1 (copy Member 2); protocol owner **P3**. Verifier-audit questions → **P6**. Blinding leak / PII / licence breach → Member 1 privately. Privacy/licence sign-off owner: Member 6.

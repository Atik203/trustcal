# 02 — Adjudicator: settle disagreements, run defect review

🎯 Goal
Turn two blind rater sheets into one defensible reference without seeing gold.
You own disagreements; agreement rows stay untouched.

📂 Your files
- Adjudication sheet: [adjudication.csv](../private/calibration/sheets/adjudication.csv)
- Verifier master sheet: [audit_sheet.csv](../../experiments/verifier_audit/private/scifact/audit_sheet.csv) (never send to raters — it carries the verifier label)
- Rules: [hub §§4–5](../README.md)

🟢 Steps
1. Start only after both rater sheets are in. Open the adjudication workbook then.
2. Copy labels first: fill `rater1_verdict` / `rater2_verdict` from the submitted sheets. Agreement rows: copy the agreed label into `adjudicated_verdict` — never invent a new one.
3. Settle each disagreement from claim + cited passages only, in this order: contradict first — any refuting passage wins; then support — ≥1 passage entails and none refutes; else neutral (`support` · `contradict` · `neutral`; verifier: `supported` · `contradicted` · `unverifiable`). Write a one-line reason citing the deciding passage.
4. Mark hopeless rows `unresolved` (missing evidence, dead locator, passages clash). Count them: unresolved ÷ adjudicated ≤ 0.05 or the freeze blocks.
5. Run defect review on frozen triples you did not label: fill `defect_flag` + `defect_type` (`wrong-verdict` · `unsupported` · `non-atomic` · `bad-evidence` · `leak`). Pre-freeze fixes are rework, not defects. Defects ÷ frozen ≤ 0.15.
6. Submit the workbook privately; post agreements / disagreements / unresolved / defects. Atik runs `score` LAST — you never score your own work.
⏱ Time: adjudication 5–7 h shared; verifier 2–3 h; defect review 3–4 h.

🔴 Never
- Never open gold, verifier, or arm labels while adjudicating, and never open item files before your adjudication is submitted.
- Never delete an unresolved row and never relabel rows to raise κ.
- Never change the codebook alone — that call belongs to Atik.

✅ Done
- [ ] Rater labels copied verbatim; every disagreement has a verdict + one-line reason.
- [ ] Unresolved rows listed (not deleted), counted, reported (≤ 5%).
- [ ] Defect columns filled on every triple reviewed; workbook submitted privately with counts posted.

🆘 Ask
Codebook doubt, leak, or PII → Atik privately (never a public issue); verifier-audit questions → P6.

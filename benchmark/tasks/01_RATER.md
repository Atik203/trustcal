# 01 — Rater: label blind sheets row by row

🎯 Goal
Label every claim in your blind sheet from the cited passages only.
Your sheet plus the second rater's sheet sets κ (≥ 0.75).

📂 Your files
- Your sheet: [rater1.csv](../private/calibration/sheets/rater1.csv) (Prottoy) or [rater2.csv](../private/calibration/sheets/rater2.csv) (Salman) — 216 rows each (24 items × 9 claims).
- Verifier sheet: [rater1.csv](../../experiments/verifier_audit/private/scifact/sheets/rater1.csv) or [rater2.csv](../../experiments/verifier_audit/private/scifact/sheets/rater2.csv) — 180 rows each.
- Effort log: [effort.csv](../private/calibration/sheets/effort.csv) · checklist: [annotation_submission_checklist.md](../templates/annotation_submission_checklist.md) · rules: [hub §4](../README.md)

🟢 Steps
1. Count rows first: expect 216 (+ 1 header) on calibration, 180 (+ 1 header) on verifier. In Excel use `=COUNTA(A:A)-1`; plain line counts lie on multiline cells.
2. Confirm blinding: no `gold_verdict`, `verifier_label`, or arm column. If you see one, stop and tell Atik.
3. Label top to bottom, one row at a time. Fill verdict + confidence (0–1) + notes on every hard row.
4. Decide every row in this order: contradict first — any refuting passage wins; then support — ≥1 passage entails and none refutes; else neutral. SciClaimBench words: `support` · `contradict` · `neutral`. Verifier words: `supported` · `contradicted` · `unverifiable`.
5. Log effort as you go, one row per item: `item_id,phase,minutes,annotator,notes`, e.g. `cal-001,rater1,22,AB,"steady pace"`. This feeds H ≤ 2.0 h/item.
6. Submit: save a copy with your initials (`rater1_<initials>.csv`), finish the checklist, upload to the private folder, post filename + row count. Never overwrite the original.
⏱ Time: 5–7 h practiced (8–10 h on your first sheet) per 216-row sheet; verifier 180-row sheet adds 5–6 h.

🔴 Never
- Never open `benchmark/private/items/` or any `cal-*.json` — they hold gold answers and break your blinding.
- Never use outside knowledge or an LLM for labels; judge the cited passages only.
- Never open the other rater's sheet or discuss rows before both sheets are in.

✅ Done
- [ ] Every row has a verdict (exact string) + confidence; hard rows have notes.
- [ ] No blanks, no added/deleted columns, header unchanged; effort rows logged.
- [ ] Initials copy + checklist uploaded privately; filename + row count posted.

🆘 Ask
Blinding, batch, or submission problem → Atik at once; codebook doubt → Atik; adjudication question → Rakib + Limu.

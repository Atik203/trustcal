# 04 — Agent pilot: mechanical help only (humans decide)

🎯 Goal
Atik, LAST and only after every sheet is in: run helpers, build sheets, score.
Agents draft — humans decide every gold verdict and every label.

📂 Your files
- Skeleton: [item.template.json](../item.template.json) · batch: [calibration_items.jsonl](../private/calibration_items.jsonl)
- Sheets: [sheets/](../private/calibration/sheets/) · gate status: [status.json](../status.json) (`next_command`)
- Verifier protocol: [verifier README](../../experiments/verifier_audit/README.md)

🟢 Steps
1. Draft only: prompt the agent for ONE item from the skeleton — original question, 3 positions × 3–6 atomic claims, candidate passages with locators + licences, CANDIDATE verdicts. Output clean JSON with no AI labels. A human verifies all of it.
2. Build blind sheets: `python benchmark/validate_items.py sheets --items benchmark/private/calibration_items.jsonl --out benchmark/private/calibration/sheets` — then confirm 216 rows each, blank verdict columns, no gold/verifier/arm column.
3. Structural check: `python benchmark/validate_items.py check --items [BATCH] --expect [N] --strict` (24 calibration, 180 freeze, 300 full). Fix schema errors only — never claim text, evidence, verdict, or licence.
4. Score only when all sheets are filled: run the exact `next_command` from `status.json`:
   `python benchmark/validate_items.py score --rater1 benchmark/private/calibration/sheets/rater1.csv --rater2 benchmark/private/calibration/sheets/rater2.csv --adjudication benchmark/private/calibration/sheets/adjudication.csv --effort benchmark/private/calibration/sheets/effort.csv --min-kappa 0.75 --max-defect 0.15 --max-hours 2.0 --max-unresolved 0.05`
   Paste JSON + exit code (0 pass / 2 fail / 1 blocked). A failed gate is a finding.
⏱ Time: ~1–2 h per batch cycle (human labelling/verification time is separate — see packs 01–03).

🔴 Never
- Never label a claim, adjudicate a row, or set a gold verdict — route those to the human owner.
- Never paste private sheets or item text into commits, issues, or external tools.
- Never score before every sheet is in, and never silently fix a verdict to pass.

✅ Done
- [ ] No item file carries AI labels; agent output stayed out until a human verified it.
- [ ] Blind sheets have no gold/verifier/arm column (column-checked).
- [ ] Validator/score outputs pasted verbatim with exit codes; counts posted to the team channel.

🆘 Ask
Blocked → Atik; verifier questions → P6; licence doubt → Rakib + Limu.

# 00 — Overview: start here, then read only your pack

🎯 Goal
This page maps the 24 → 180 → 300 ladder, the gates, and every file.
Read it once, then open only your own role pack.

📂 Your files
- Rules and labels live here: [hub §4](../README.md) (codebook — read it there, not here).
- Schema and skeleton: [schema.md](../schema.md) · [item.template.json](../item.template.json)
- Validator: [validate_items.py](../validate_items.py)
- Guide with examples: [MEMBER_GUIDE.md](../MEMBER_GUIDE.md)

🟢 Steps
1. Run this Step 0 check once (Python 3.10 or newer, one package):
   `python --version` · `python -c "import yaml"` (silent = ok, else `pip install pyyaml`) · `python benchmark/validate_items.py --help`
2. Find your name in the table below and open only that pack.
3. Learn the ladder: 24 calibration (8/8/8) → gate passes → 180 freeze (60/60/60, ~410 h) → 300 target (100/100/100, ~684 h).
4. Learn the gate: κ ≥ 0.75, defect ≤ 0.15, H ≤ 2.0 h/item, unresolved ≤ 0.05. Fail κ or unresolved → keep batch, fix codebook, fresh batch. Fail H or defect → cut to 120 items, not 180.
5. Only Atik runs the score below, last, after every sheet is in:

   ```bash
   python benchmark/validate_items.py score \
     --rater1 benchmark/private/calibration/sheets/rater1.csv \
     --rater2 benchmark/private/calibration/sheets/rater2.csv \
     --adjudication benchmark/private/calibration/sheets/adjudication.csv \
     --effort benchmark/private/calibration/sheets/effort.csv \
     --min-kappa 0.75 --max-defect 0.15 --max-hours 2.0 --max-unresolved 0.05
   ```

🏷 Labels (same words in every pack)
SciClaimBench labels (exact lowercase): `support` · `contradict` · `neutral`.
Order on every row: contradict first — any refuting passage wins; then support — ≥1 passage entails and none refutes; else neutral. Full rules: [hub §4](../README.md).

| Pack | Who | Due |
| --- | --- | --- |
| [01_RATER.md](01_RATER.md) | Prottoy = rater 1, Salman = rater 2 — label 216 rows each | Fri 4 Dec |
| [03_AUTHOR.md](03_AUTHOR.md) | Yousuf — verify the 24 drafts (12–16 h), sole verifier | Fri 4 Dec |
| [02_ADJUDICATOR.md](02_ADJUDICATOR.md) | Rakib + Limu — settle disagreements, defect review | Fri 11 Dec |
| [04_AGENT_PILOT.md](04_AGENT_PILOT.md) | Atik — helpers and score, LAST | Week of 14 Dec |

🔴 Never
- Never commit, email, or paste private sheets, labels, or evidence text anywhere public.
- Never relabel rows to raise κ, and never start 180/300 work before the gate passes.
- Never use gated text (GPQA, HLE, MMLU-Pro) in SciClaimBench, and never mark items with AI labels.

✅ Done
- [ ] Step 0 check prints clean, and you know your pack and due date.
- [ ] You can state the 4 gate numbers (0.75 / 0.15 / 2.0 / 0.05) and the 216 / 180 row counts.
- [ ] You know blinding: raters and adjudicators never open gold or item files early.

🆘 Ask
Blockers on batch, blinding, or protocol → Atik (benchmark owner); adjudication questions → Rakib + Limu; verifier-audit questions → P6.

# 00 — Overview: the map, then your own pack

Read this page once. Then open only your role pack and follow it top to bottom.

## The ladder

24 calibration items → gate passes → 180 freeze → 300 full-run target. The 120 is a cut, not a rung: it
replaces the 180 when effort or defects fail. The 600 and 800 rungs are not built.

| Size | Split | Your part in it |
| ---: | --- | --- |
| 24 | 8 / 8 / 8 | this is the only batch that moves today: 216 claim rows, 180 verifier pairs, 24 drafts |
| 180 | 60 / 60 / 60 | starts only if the 24 passes κ, defect, effort and unresolved |
| 300 | 100 / 100 / 100 | starts only if the 180 freezes clean |

## Your pack

| Pack | Who | Due |
| --- | --- | --- |
| [01_RATER.md](01_RATER.md) | Prottoy (rater 1), Salman (rater 2) — 216 + 180 rows each | Fri 11 Dec 2026 |
| [03_AUTHOR.md](03_AUTHOR.md) | Yousuf — verify the 24 drafts, 12–16 h | Fri 4 Dec 2026 |
| [02_ADJUDICATOR.md](02_ADJUDICATOR.md) | Rakib + Limu — disagreements and defect review | Wed 16 Dec 2026 |
| [04_AGENT_PILOT.md](04_AGENT_PILOT.md) | Atik — sheets, validator, score, last | Fri 18 Dec 2026 |

Four weeks total, 25 Nov – 22 Dec 2026, no fifth week. The week-by-week table is in
[`MEMBER_GUIDE.md`](../MEMBER_GUIDE.md) §7.

## Step 0, for Atik and Yousuf only

```bash
python --version                 # 3.10 or newer
python -c "import yaml"          # silent = fine, else: pip install pyyaml
python benchmark/validate_items.py --help
```

Raters and adjudicators never need Python or a terminal: a spreadsheet app and the sheet are enough.

## The words, once

| Word | Means |
| --- | --- |
| item | one question, with three agent positions and one gold answer |
| position | one agent's answer inside an item; there are always three (agents 0, 1, 2) |
| claim | one small checkable statement inside a position; 3–6 per position |
| row | one claim, plus the passages retrieved for it — one line in your sheet |
| passage | the quoted text a claim is checked against, with a locator and a licence |
| triple | claim + passage + verdict, the unit the whole benchmark is built from |

## Labels, in one line each

SciClaimBench, the `verdict` column: `support` · `contradict` · `neutral`.
Verifier audit, the `label` column: `supported` · `contradicted` · `unverifiable`.
Order on every row: contradiction first, then support, else neutral. Definitions, worked examples and the
five common mistakes: [`MEMBER_GUIDE.md`](../MEMBER_GUIDE.md).

## Never

- Never open the item files, the other rater's sheet, or the verifier answer key while labelling.
- Never relabel a row to move a number, and never delete an unresolved row.
- Never commit a filled sheet, email it, or paste claim text into an AI tool.

## Done with this page when

- [ ] You know your pack, your due date, and your row count.
- [ ] You can say the four gate numbers: κ 0.75, defect 0.15, effort 2.0 h/item, unresolved 0.05.
- [ ] You know the one column you fill and its exact label strings.

## Ask

| Question | Who |
| --- | --- |
| a row, a passage, a broken link, or a missing file | Atik, in the group |
| how a label is defined | Atik |
| the verifier audit's rules | its [codebook](../private/verifier/codebook.md), then Atik |
| adjudication practice | Rakib + Limu |

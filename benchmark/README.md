# SciClaimBench annotation — start here

**You do not need to know this project to start.** Your job is one sentence long: read a scientific
claim, read the passages printed beside it, and type one of three labels saying whether those passages
back the claim. No code, no statistics, no writing.

Ten minutes on this page, then open your own pack from the table in §2.

---

## 1. What this project is, and why your labels matter

TrustCal is our FYDP. Three language models answer the same science question, then read each other's
answers and revise. A model that was right sometimes copies a group that is wrong — *sycophantic
collapse*. Our method re-weights each model by how well its claims match retrieved evidence, so evidence
decides instead of the loudest group.

That method rests on one judgement: **does this passage support this claim?** Before we trust a model's
score, we test whether two careful humans make that judgement the same way. Two of us label the same 216
claims, alone, and we measure agreement (Cohen's κ). If two readers with the same passages cannot agree,
a benchmark built on the same judgement proves nothing.

You are that test. Nothing in the benchmark moves until your labels exist.

## 2. Find your name

**Four weeks: 25 Nov – 22 Dec 2026.** There is no fifth week. What is not finished by 18 Dec is reported
as not finished, with the rows that remain.

| Name | Your job | Volume | Open this | Due |
| --- | --- | --- | --- | --- |
| Prottoy, rater 1 | label both sheets alone | 216 + 180 rows | [`tasks/01_RATER.md`](tasks/01_RATER.md) | Fri 11 Dec 2026 |
| Salman, rater 2 | label both sheets alone | 216 + 180 rows | [`tasks/01_RATER.md`](tasks/01_RATER.md) | Fri 11 Dec 2026 |
| Yousuf, verifier | check the 24 drafted items | 24 items | [`tasks/03_AUTHOR.md`](tasks/03_AUTHOR.md) | Fri 4 Dec 2026 |
| Rakib + Limu, adjudicators | settle rows the raters disagree on, run defect review | 216 rows | [`tasks/02_ADJUDICATOR.md`](tasks/02_ADJUDICATOR.md) | Wed 16 Dec 2026 |
| Atik, benchmark owner | build sheets, run the score, **last** | — | [`tasks/04_AGENT_PILOT.md`](tasks/04_AGENT_PILOT.md) | Fri 18 Dec 2026 |

First annotation of your life? Read [`MEMBER_GUIDE.md`](MEMBER_GUIDE.md) first. It shows a real sheet
row, one worked label, and the five mistakes that waste the most time. If you want the whole map on one
page first — ladder, roles, vocabulary — that is [`tasks/00_OVERVIEW.md`](tasks/00_OVERVIEW.md).

## 3. The two sheets, and the one column you fill

| Sheet | Where it is | Column to fill | Allowed values, exact spelling | Rows |
| --- | --- | --- | --- | --- |
| SciClaimBench | `private/calibration/sheets/rater1.csv` (Prottoy) or `rater2.csv` (Salman) | `verdict` | `support` · `contradict` · `neutral` | 216 |
| Verifier audit | `private/verifier/sheets/rater1.csv` (Prottoy) or `rater2.csv` (Salman) | `label` | `supported` · `contradicted` · `unverifiable` | 180 |

Both sheets live inside this folder, so the links in your pack open straight to them. The two spellings
are deliberate: SciClaimBench says `support`, the verifier audit says `supported`. A label copied from one
sheet into the other is a broken row. The verifier sheet's rules are its own one-page
[codebook](private/verifier/codebook.md) — read it before that sheet.

Where the row counts come from: this batch has 24 items x 3 agent positions x 3 claims = 216 rows, and
180 claim–passage pairs in the verifier sheet. The schema allows 3–6 claims per position, so a later
batch can be up to twice this size; always read the count off your own sheet. One row is always one
claim, never one question.

## 4. Filling a sheet, first time

1. **Get the files.** Green `Code` button on GitHub → `Download ZIP`, or `git clone`. Everything you need
   is inside `benchmark/`; you never have to leave it.
2. **Open the CSV** in Excel, LibreOffice, or Google Sheets. The first line is the header. Never edit it,
   never add or delete a column.
3. **One row at a time.** Read `claim`, then the passages (`evidence_text` on SciClaimBench, `passages`
   on the verifier sheet). Type the label, a confidence, and a short note when the row was hard.
   Confidence is your own certainty: 0.9 means the passages decide it plainly, 0.5 means you would argue
   with yourself, and anything below 0.5 belongs in `notes` as well.
4. **Save as CSV, UTF-8**, one file per sheet: `rater1_sci_PR.csv` and `rater1_ver_PR.csv` for
   Prottoy; `rater2_sci_SA.csv` and `rater2_ver_SA.csv` for Salman. `sci` is the SciClaimBench sheet,
   `ver` is the verifier sheet.
5. **Count the rows** — `=COUNTA(A:A)-1` must give 216 or 180. A raw line count lies when a cell holds a
   line break, so use the formula, not the editor's line number.
6. **Send the files to Atik** (WhatsApp file or Drive link) and post in the team group:
   `rater1_sci_PR.csv — 216 rows — 4 hard rows`. Contact details are deliberately not in this public
   folder: use the team group you already have, or ask Atik in person. Atik assembles your files into
   the plain names before scoring.

Never commit a filled sheet. Never email it. Never paste a claim or passage into ChatGPT or any other AI
tool. The sheets here are blank on purpose; a filled sheet is work that must not leak before
adjudication.

## 5. The three labels

| Label | Means | Use it when |
| --- | --- | --- |
| `support` | the passage states the claim | at least one passage entails the claim and none contradicts it |
| `contradict` | the passage says the claim is false | any passage refutes it: opposite result, different number, negated relation, other entity |
| `neutral` | the passages do not decide | no passage states the claim, passages are off-topic, or they only share words with it |

Decide in that order, contradiction first: one clear refutation beats any amount of support. Then
support: one entailing passage with no refutation. Otherwise neutral. Numbers must match after unit
conversion, a negation flips the relation, and half of a compound claim being true is not support.

One case catches almost everyone: a passage that reports **no significant difference** contradicts a
claim that asserts the effect. "No difference between arms" is evidence against "the drug lowered blood
pressure", not an absence of evidence. Reserve `neutral` for passages that never address the relation at
all.

Worked examples for both wordings: [`MEMBER_GUIDE.md`](MEMBER_GUIDE.md) §2.

## 6. The gate — the four numbers this batch is testing

| Quantity | Plain meaning | Pass |
| --- | --- | --- |
| Cohen's κ | how often the two raters agree beyond chance, 0 to 1 | **≥ 0.75** |
| Defect rate | share of the 216 adjudicated rows an independent reviewer flags wrong or unsupported | **≤ 0.15** |
| `H_attempt` | human hours per item, all phases counted | **≤ 2.0 h** |
| Unresolved rate | share of rows the adjudicators had to abandon | **≤ 0.05** |

A failed κ is a finding, not a team failure: keep the batch, fix the codebook, run a fresh one. Nobody
relabels rows to move a number. If effort or defects fail, the next batch is cut to 120 items instead of
180.

## 7. The ladder

| Size | Role | Split | Starts when | On pass |
| ---: | --- | --- | --- | --- |
| **24** | calibration batch | 8 / 8 / 8 | now | 180 freeze; fail κ → fresh 24; fail effort or defect → 120 |
| **180** | SciClaimBench v1.2 freeze | 60 / 60 / 60 | the 24 passes | freeze, report κ and defect rate |
| **300** | full-run target | 100 / 100 / 100 | the 180 is clean | full run |

The 120 is a cut, not a rung: it replaces the 180 and never runs beside it. The 600 and 800 rungs are
no-go markers and are not built.

## 8. What is in this folder

| Path | What it is | Who may open it |
| --- | --- | --- |
| `README.md`, `MEMBER_GUIDE.md` | this hub plus the how-to | everyone |
| `tasks/` | one pack per role, with the exact steps | everyone — open your own |
| `templates/` | submission checklists and effort logs | everyone |
| `schema.md`, `item.template.json` | the item format, one filled skeleton | Yousuf, Atik |
| `annotation/effort.template.csv` | the effort-log header members copy | everyone |
| `validate_items.py`, `draft_items.py` | the validator and the item generator | Yousuf may run the check; Atik owns the rest |
| `private/calibration/sheets/`, `private/verifier/sheets/` | the blank sheets: two per round plus the adjudication file | **raters see only their own; adjudicators see the adjudication files** |
| `private/calibration_items.jsonl` | the 24 drafted items **with gold answers** | **Yousuf and Atik only** |
| `private/calibration_*.jsonl` | the same items split by subject | **Yousuf and Atik only** |
| `private/freeze180/`, `private/full300/` | the 180 and 300 batches, not in play yet | **Atik only** |
| `private/pilot/` | the finished pilot batch | Atik only |
| the verifier answer key | held by Atik outside this folder | **Atik only, never anyone else** |

Yousuf is the one exception to the gold rule: verifying the drafts means reading them. Raters and
adjudicators never open an item file, the answer key, or the other rater's sheet — that is what makes the
agreement number mean something.

## 9. Protocol detail, for the report

The unit is a **claim–evidence–verdict triple**. One item has a question, three positions (agents 0, 1, 2),
3–6 atomic claims per position, and at least one cited passage per claim. Strata are `biomedical`,
`physics_chemistry`, `math_cs`, balanced 8/8/8 at 24 and 60/60/60 at 180. Full fields:
[`schema.md`](schema.md).

Licensing: an original item is `CC BY 4.0`. An adapted item keeps its source licence, citation, locator
(DOI, PMID, arXiv ID, or URL) and a note of what changed. Never copy GPQA, HLE, or MMLU-Pro test text into
an item, and never paste SciFact passages into one — that corpus is for the verifier audit only. Items
carry **no AI markings**; provenance lives in the batch `MANIFEST.json`.

## 10. Build the sheets and run the gate

Atik owns this section. Yousuf runs only the structural check in step 3 while verifying drafts.

From the repository root (outside this folder), with the project's virtual environment:

```bash
# structure check of the batch
python benchmark/validate_items.py check --items benchmark/private/calibration_items.jsonl --expect 24 --strict

# rebuild blind sheets after any authoring edit
python benchmark/validate_items.py sheets --items benchmark/private/calibration_items.jsonl \
  --out benchmark/private/calibration/sheets

# score, once every human sheet is in
python benchmark/validate_items.py score \
  --rater1 benchmark/private/calibration/sheets/rater1.csv \
  --rater2 benchmark/private/calibration/sheets/rater2.csv \
  --adjudication benchmark/private/calibration/sheets/adjudication.csv \
  --effort benchmark/private/calibration/sheets/effort.csv \
  --min-kappa 0.75 --max-defect 0.15 --max-hours 2.0 --max-unresolved 0.05
```

`score` exits `0` when all gates pass, `2` when one fails, `1` when an input is incomplete or empty.
Empty is never a pass. The 180 and 300 batches use the same commands against `private/freeze180/` and
`private/full300/` — see [`FULLBENCH_PLAN.md`](FULLBENCH_PLAN.md).

## 11. Glossary

| Word | Means here |
| --- | --- |
| **claim** | one small, checkable statement. A compound sentence is split before it becomes a claim |
| **passage** | the quoted text the claim is checked against, with a locator and a licence |
| **verdict** | your label for one claim: `support`, `contradict`, or `neutral` |
| **gold verdict** | the answer the project treats as correct, set only after human verification and adjudication |
| **blind sheet** | a sheet with the claims and passages but no gold verdict, so the label is really yours |
| **adjudication** | settling one row where the two raters disagree, with a one-line reason |
| **unresolved** | a row nobody can settle from the passages; it is reported, never deleted |
| **defect review** | an independent check of the adjudicated rows by someone who did not label them, done before the freeze |
| **freeze** | the batch is final and versioned; a later correction becomes `-v2`, never an overwrite |
| **stratum** | the subject area of an item: biomedical, physics/chemistry, math/CS |
| **κ (kappa)** | agreement between the two raters after chance is removed; 1.0 is perfect, 0 is chance |
| **`H_attempt`** | human hours per item across authoring, both raters, adjudication and rework |

## 12. Questions

| Problem | Who |
| --- | --- |
| a row you cannot decide, a broken locator, a missing file | Atik, in the group |
| how a label is defined | Atik; adjudicators may answer after the sheets are in |
| what the verifier audit expects | Atik (the codebook is [here](private/verifier/codebook.md)) |
| anything that feels like a leak of answers or personal data | Atik privately, never a public issue |

# Benchmark hub — SciClaimBench annotation, START HERE

> 🟢 **Start here — 3 clicks.** 1. Check Step 0 once: `pip install pyyaml`, Python ≥ 3.10 (details in [`tasks/00_OVERVIEW.md`](tasks/00_OVERVIEW.md) §0). 2. Find your name in the table below. 3. Open your 1 pack file and follow it.

| Batch | Items | Location | Sheets | Status |
|---|---|---|---|---|
| Calibration (S0) | 24 (8/8/8) | `private/items/cal-001..024` | `private/calibration/sheets/` | Drafted, schema-valid; **0 human labels** |
| Freeze (S2) | 180 (60/60/60) | `private/freeze180/` | `private/freeze180/sheets/` | Drafts + blank sheets ready |
| Full target (S3) | 300 (100/100/100) | `private/full300/` | `private/full300/sheets/` | Drafts + blank sheets ready |

**The gate (all four, one command):** κ ≥ 0.75, defect ≤ 0.15, H_attempt ≤ 2.0 h/item, unresolved ≤ 0.05. Copy and paste this after every sheet is in:

```bash
python benchmark/validate_items.py score \
  --rater1 benchmark/private/calibration/sheets/rater1.csv \
  --rater2 benchmark/private/calibration/sheets/rater2.csv \
  --adjudication benchmark/private/calibration/sheets/adjudication.csv \
  --effort benchmark/private/calibration/sheets/effort.csv \
  --min-kappa 0.75 --max-defect 0.15 --max-hours 2.0 --max-unresolved 0.05
```

| Name | Job | Your file | Due |
|---|---|---|---|
| Prottoy (PR) — rater 1 | Label all 216 claims in rater1 sheet. | [`tasks/01_RATER.md`](tasks/01_RATER.md) | Fri 4 Dec |
| Salman (SA) — rater 2 | Label all 216 claims in rater2 sheet. | [`tasks/01_RATER.md`](tasks/01_RATER.md) | Fri 4 Dec |
| Yousuf (YO) — verifier | Check all 24 drafts, file problem list. | [`tasks/03_AUTHOR.md`](tasks/03_AUTHOR.md) | Fri 4 Dec |
| Rakib + Limu (RK+LM) — adjudicators | Settle disagreements, run defect review. | [`tasks/02_ADJUDICATOR.md`](tasks/02_ADJUDICATOR.md) | Fri 11 Dec |
| Atik — agent pilot, LAST | Run helpers and score after sheets in. | [`tasks/04_AGENT_PILOT.md`](tasks/04_AGENT_PILOT.md) | Week of 14 Dec |

Three rules: no gated text ever · items have no AI markings · nothing is gold until humans verify it and the gate passes. Dates are targets — send blockers to Atik at once.

Member guide with examples and the week plan: [`MEMBER_GUIDE.md`](./MEMBER_GUIDE.md).

---

## 🟢 1. What this gate decides

The 24-item batch is the test before the 180-item freeze. It answers three questions. Can two raters reach Cohen's κ ≥ 0.75? Is the defect rate ≤ 0.15? Is effort `H_attempt` ≤ 2.0 h/item? If κ fails, keep the failed batch in the report. Revise the codebook and run a fresh batch. If `H_attempt` is over 2.0 h or defects are over 0.15, cut the next step to 120 items, not 180. A failed calibration is a finding, not a reason to relabel.

## 🟡 2. Item sources and licensing

The best source is an original item written for this project. Original items use **CC BY 4.0** when frozen. You may adapt a public-domain or CC BY source only. Then record the citation, a locator (DOI, PMID, arXiv ID, or URL), the licence, and what changed. Do **not** copy gated text (GPQA, HLE, MMLU-Pro test text) into SciClaimBench. SciFact passages are audit-only — never paste them into SciClaimBench. Those sets are for comparison only. LLM help is allowed for drafts only. A human must verify every claim, link, and gold verdict. Items carry no AI markings. Provenance lives only in `private/*/MANIFEST.json`.

## 🟢 3. Domain strata

The 24-item batch is exactly balanced: 8 biomedical, 8 physics / chemistry, 8 math / CS. The 180-item freeze uses 60/60/60. The 300-item target uses 100/100/100. Stratum is an item-level field. Do not move items between strata after annotation starts.

## 4. Annotation unit and schema

The unit is a **claim–evidence–verdict triple**. One item has three positions (agents 0, 1, 2). Each position has **3–6 atomic claims**. Each claim has cited passages and one verdict: `support`, `contradict`, or `neutral`. `support` means a passage entails the claim and none refutes it. `contradict` means a passage says the claim is false. `neutral` means the passages do not prove or refute it. Check refutation first: one clear contradiction beats any support. Each item also records `pressure_eligible` and its evidence conditions (`evidence_available`, `evidence_absent`, `evidence_placebo`, `evidence_contradictory`). Full fields are in [`schema.md`](schema.md). The skeleton is in [`item.template.json`](item.template.json). The 24 empty slots are in [`items.seed.jsonl`](items.seed.jsonl). There is no SciClaimBench loader in the runner yet. Do not point `run_experiment.py --questions-file` at this batch.

## 🟡 5. Two-annotator and adjudication protocol

1. Author and freeze the item. Fill question, options, gold answer, three positions, 3–6 claims each, and one cited passage per claim. Put no verdict in the export.
2. Build blind sheets with `validate_items.py sheets`. Gold never appears in `rater1.csv` or `rater2.csv`.
3. Label alone. Each rater labels every claim from the cited passages only. No talk. No peeking. No outside knowledge. Add 0–1 confidence and a note on hard rows.
4. Never change a label after seeing the other sheet. First-pass labels set κ.
5. Adjudicate each disagreement from the codebook. Write the verdict and one-line reason in `adjudication.csv`. Copy agreement rows as they are.
6. Mark hopeless rows `adjudicated_verdict = unresolved`. They leave the frozen set. An unresolved rate over 0.05 blocks the freeze.
7. Run defect review. A reviewer who did not label checks each frozen triple. Wrong or unsupported triples are defects. Pre-freeze fixes are rework, not defects.

## 6. Agreement, defect, and effort gates

| Quantity | Definition | 24-item gate |
| --- | --- | --- |
| Cohen's κ | Unweighted κ on the two pre-adjudication verdict columns | **≥ 0.75** |
| Defect rate | Defective frozen triples ÷ frozen triples, after step 7 review | **≤ 0.15** |
| `H_attempt` | Total hours ÷ attempted items, over authoring, both raters, adjudication, rework | **≤ 2.0 h/item** |
| Unresolved rate | Unresolved claims ÷ claims sent to adjudication | **≤ 0.05** |

Log rows per item in `annotation/effort.template.csv`: `H_attempt = sum(minutes for all phases) / 60 / number of distinct item_id rows`. Track authoring, `rater1`, `rater2`, `adjudication`, and `rework` apart. This projects the 180-item budget. If κ < 0.75, keep the batch, fix the codebook, run a fresh batch. Never delete rows to raise κ. If `H_attempt > 2.0` or defects top 0.15, cut to 120 items.

## 📂 7. The 24 → 180 → 300 freeze ladder

| Size | Role | Split | Entry condition | Decision |
| ---: | --- | --- | --- | --- |
| **24** | Calibration batch | 8 / 8 / 8 | protocol frozen | κ ≥ 0.75, defect ≤ 0.15, `H_attempt` ≤ 2.0 → 180; else cut to 120 |
| **180** | SciClaimBench v1.2 freeze | 60 / 60 / 60 | 24-item gate passes | freeze by Jan 2027; report κ and defect rate |
| **300** | Full-run target | 100 / 100 / 100 | 180-item set is clean | target by Feb 2027 |

The 120-item cut keeps the protocol alive without the 180-item cost. Larger rungs (600, 800) are no-go and not built.

## ✅ 8. Files and what is safe to commit

| Path | Contents | Commit? |
| --- | --- | --- |
| `README.md`, `schema.md` | Protocol and field definitions | yes |
| `item.template.json` | One marked skeleton; no real evidence | yes |
| `items.seed.jsonl` | 24 unfilled slots, 8/8/8; no item text | yes |
| `validate_items.py` | Check, sheet builds, κ/defect/effort scoring | yes |
| `annotation/*.template.csv` | Header-only sheets and effort template | yes |
| `status.json` | Counts and blocked reasons only | yes |
| `private/` | Filled items, evidence text, labels, adjudication | **no — gitignored** |

Put every filled workbook under `private/`. It stays gitignored. Labels must not leak before adjudication. When the 180-item set freezes and the licence check passes, move the public item file out of `private/` and commit it. Keep human label sheets private.

## 9. Run the gate

From the repo root, with the `trustcal` virtual environment:

```bash
# 1. Seed check. Passes with 24 unfilled slots.
python benchmark/validate_items.py check \
  --items benchmark/items.seed.jsonl

# 2. Strict check of the drafted batch:
python benchmark/validate_items.py check \
  --items benchmark/private/calibration_items.jsonl --expect 24 --strict

# 3. Blind sheets are already built. To rebuild after edits:
python benchmark/validate_items.py sheets \
  --items benchmark/private/calibration_items.jsonl \
  --out benchmark/private/calibration/sheets

# 4. After raters and adjudicator finish, score the gate.
python benchmark/validate_items.py score \
  --rater1 benchmark/private/calibration/sheets/rater1.csv \
  --rater2 benchmark/private/calibration/sheets/rater2.csv \
  --adjudication benchmark/private/calibration/sheets/adjudication.csv \
  --effort benchmark/private/calibration/sheets/effort.csv \
  --min-kappa 0.75 --max-defect 0.15 --max-hours 2.0 --max-unresolved 0.05
```

`score` exits `0` when all gates pass, `2` when one fails, `1` when input is incomplete. Empty sheets exit `1` and say blocked. Empty is never a pass.

## 🆘 10. What the team must fill in

The 24 drafts already exist (`private/items/cal-001..024`, mirrored in `private/calibration_items.jsonl`). The team verifies them. It does not write from scratch.

1. Verify every claim, link, locator, and candidate verdict in all 24 drafts (§§4–5). File problem lists. Do not edit blindly.
2. Label the blind sheets (2 raters), adjudicate, log effort.
3. Set `status` to `annotated` / `adjudicated` / `frozen` only after each step is real.
4. Confirm each `source` block: `kind`, `citation`, `locator`, `license`. Original items use `kind = "original"` and `CC BY 4.0`.
5. Run the strict check, then score the gate (§9). Never invent a passage, DOI, or verdict. An empty slot is honest. A fake gold triple is a defect.

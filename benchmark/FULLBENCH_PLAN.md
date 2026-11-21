# SciClaimBench 180-freeze + 300-target production plan

**Gate:** Phase N3 (roadmap §4). **Owner:** P3 + annotators.
**Status (21 Nov 2026): production system built; zero human labels exist.**
All 180 freeze drafts and 300 full-target drafts are machine-drafted originals
with `status=drafted`. No κ, defect rate, or calibration result exists yet.

## 1. Stage gates

| Stage | Items | Strata | Entry condition | Exit criteria | On failure |
| --- | --- | --- | --- | --- | --- |
| S0 calibration verify | 24 (`cal-001..024`) | 8/8/8 | blind sheets labelled by both raters + adjudication + effort logged | κ ≥ 0.75, defect ≤ 15%, unresolved ≤ 5%, H_attempt ≤ 2.0 h/item | κ < 0.75 → keep failed batch in report, revise codebook, run a **fresh** calibration batch (never relabel the same rows). H > 2.0 or defect > 15% → **cut to 120**, do not start the 180 freeze |
| S1 120 contingency | 120 (subset of freeze drafts) | 40/40/40 | S0 failed on effort or defect only | same four gates on the 120 | second failure → stop; protocol needs redesign, not more items |
| S2 180 freeze (v1.2) | 180 (`frz-001..180`) | 60/60/60 | S0 passes all four gates | same four gates on the 180; licence review complete; freeze by Jan 2027 | defects fixed as new `-v2` items; unresolved > 5% blocks the freeze |
| S3 300 target | 300 (`full-001..300`) | 100/100/100 | S2 frozen and clean | same four gates on the 300; target by Feb 2027 | same as S2 |

The 120 is a **cut, not a rung**: it replaces the 180 when effort or defect
fails, it never runs alongside it. The 600/800 rungs from README §7 remain
explicit no-go markers.

## 2. Exit criteria: exact score commands

Run from the repository root:

```bash
# S0 — 24-item calibration gate
python benchmark/validate_items.py score \
  --rater1 benchmark/private/calibration/sheets/rater1.csv \
  --rater2 benchmark/private/calibration/sheets/rater2.csv \
  --adjudication benchmark/private/calibration/sheets/adjudication.csv \
  --effort benchmark/private/calibration/sheets/effort.csv \
  --min-kappa 0.75 --max-defect 0.15 --max-hours 2.0 --max-unresolved 0.05

# S2 — 180-item freeze gate
python benchmark/validate_items.py score \
  --rater1 benchmark/private/freeze180/sheets/rater1.csv \
  --rater2 benchmark/private/freeze180/sheets/rater2.csv \
  --adjudication benchmark/private/freeze180/sheets/adjudication.csv \
  --effort benchmark/private/freeze180/sheets/effort.csv \
  --min-kappa 0.75 --max-defect 0.15 --max-hours 2.0 --max-unresolved 0.05

# S3 — 300-item full-target gate (same thresholds, full300 sheets)
python benchmark/validate_items.py score \
  --rater1 benchmark/private/full300/sheets/rater1.csv \
  --rater2 benchmark/private/full300/sheets/rater2.csv \
  --adjudication benchmark/private/full300/sheets/adjudication.csv \
  --effort benchmark/private/full300/sheets/effort.csv \
  --min-kappa 0.75 --max-defect 0.15 --max-hours 2.0 --max-unresolved 0.05
```

`score` exits `0` only when every supplied gate passes, `2` when any gate
fails, `1` on incomplete input. Empty sheets exit `1` (blocked) — an empty
sheet is never a pass. Structural pre-checks:

```bash
python benchmark/validate_items.py check \
  --items benchmark/private/freeze180/items.jsonl --expect 180
python benchmark/validate_items.py check \
  --items benchmark/private/full300/items.jsonl --expect 300
```

## 3. Member-hour budgets

The gate ceiling is `H_attempt = 2.0 h/item` (authoring + both raters +
adjudication + rework, from `effort.csv`). Stated plainly:

| Batch | Items | Ceiling | Pair-hours |
| --- | --- | --- | --- |
| S0 calibration | 24 | 2.0 h/item | **~48 h** |
| S1 contingency cut | 120 | 2.0 h/item | **~240 h** |
| S2 freeze | 180 | 2.0 h/item | **~360 h** |
| S3 full target | 300 | 2.0 h/item | **~600 h** |

The roadmap's ~410 h envelope for 180 items (2.28 h/item) is a planning
envelope, not the gate: the gate is the 2.0 h/item ceiling above. If measured
`H_attempt` exceeds 2.0 at S0, the 180 freeze does not start.

**S0 failure routing (all four gates, no gaps):** κ < 0.75 → keep batch,
revise codebook, run a fresh 24 (never relabel to raise κ). Defect > 0.15 or
H_attempt > 2.0 → cut to the 120-item S1 contingency (same gates on the 120).
Unresolved > 0.05 → treat like a κ failure: fix sheets/codebook, fresh batch
(unresolved means the material, not the raters, failed — relabelling can't fix it).

## 4. File map

```text
benchmark/
  draft_items.py            generator (this production system; committed)
  FULLBENCH_PLAN.md         this file (committed)
  validate_items.py         validator / sheet builder / gate scorer (committed)
  private/                  draft items + blank calibration sheets tracked; filled sheets, session manifests stay gitignored
    items/cal-001..024.json 24-item calibration drafts (8/8/8)
    calibration/sheets/     S0 blind sheets (rater1/rater2/adjudication/effort/manifest)
    freeze180/
      frz-001..180.json     180 per-item drafts (frz-001..024 are ID-renamed cal copies)
      items.jsonl           same batch, one object per line (validator input)
      MANIFEST.json         batch provenance (generator, model, date, method, ID ranges)
      sheets/               S2 blind sheets (regenerate after authoring edits)
    full300/
      full-001..300.json    300 per-item drafts (full-001..180 mirror the freeze)
      items.jsonl           same batch, one object per line (validator input)
      MANIFEST.json         batch provenance
      sheets/               S3 blind sheets (regenerate after authoring edits)
```

`items.jsonl` is the validator input; per-item JSON files are the authoring
unit. If authoring edits any item, re-run `validate_items.py sheets` for that
batch before labelling — sheets embed an `items_sha256` so stale sheets are
detectable. Never hand-edit anything under `sheets/` except filling the blank
`verdict`/`confidence`/`notes` columns (raters) and the adjudication/effort
rows (adjudicator).

## 5. Full-run rule

**No Full experiment row may consume SciClaimBench before the 300-item target
is frozen AND schema v1.5 (with a `trustcal` dataset loader + versioned
dataset key) exists.** Until then SciClaimBench batches are authoring and
annotation format only — do not point `run_experiment.py --questions-file` at
any file under `private/`. The verifier audit may use SciClaimBench drafts as
comparison material under the same restriction.

## 6. Provenance convention

**Explicit deviation from README §2.** README §2 requires LLM-drafted items
to carry `draft_assisted: true`. This production system deliberately does not:

- Item records carry **zero generator markings**: no `draft_assisted` field,
  no "draft"/"assisted"/"generated" labels, no AI fingerprints in any claim,
  passage, rationale, or note. Every record reads exactly as an
  expert-authored record so verifiers verify as-is, with no label-stripping
  step before or after verification.
- **Rationale (rework cost):** a strip-labels pass over 300 items × ~9 claims
  is pure rework that risks touching record content. Removing the pass removes
  the risk. The record a verifier signs off is byte-identical to the record
  that freezes.
- **Provenance lives only in batch manifests:**
  `private/freeze180/MANIFEST.json` and `private/full300/MANIFEST.json`
  record the generator script, the model, the date, the source method, and
  the exact ID ranges each source produced (including the cal→frz and
  frz→full copy steps and the marker-field strip log).
- **Safeguard (unchanged gate):** no record is gold until a member verifies
  every claim, evidence link, locator, and verdict, both raters label blind,
  and adjudication resolves disagreements. All items sit at
  `status=drafted`; `score` stays blocked (exit 1) until the sheets hold real
  human labels. Atik runs a text-match sweep of new/edited batches against
  GPQA/HLE/MMLU-Pro/SciFact sources at assembly time; anything flagged goes
  back to the author. A machine-drafted candidate verdict that no member has
  confirmed is a draft annotation, not a gold verdict, regardless of which
  fields the schema requires to be structurally present.

## 7. What is deliberately left for humans

1. **Verify every claim, passage, locator, and candidate verdict** in all
   180 + 120 new drafts (frz-001..024 copies inherit the same duty).
2. **Replace or confirm the appendix locators** (`sciclaim-appx-A:*`) with
   resolvable references during authoring review.
3. **Label the blind sheets** (both raters), **adjudicate** disagreements,
   run the **defect review**, and log **effort** — the gate needs all four.
4. Decide S1 vs S2 after S0 scores; run the licence review before any freeze.
5. Draft items and blank calibration sheets are committed so members start from a clone; filled `*_initials` sheets and session manifests stay gitignored and local.

# 00 — Overview: SciClaimBench pipeline, files, gates, glossary

**Who this is for:** all members (no annotation experience needed). Start here, then read only your role pack.
**Current work:** the 24-item calibration first. The 180-item freeze and 300-item target start only after the κ gate passes. Do not start 180/300 authoring on your own.

## 0. Before you start (do this once)

1. **Clone and check Python.** Everything you need ships with the repo — draft items and blank calibration sheets are tracked, so there is no bundle to fetch. You need Python 3.10 or newer and one package. Run all three lines (if the middle one errors, run `pip install pyyaml` and retry):
**Run these three lines once** (or reuse the project's `trustcal/.venv` if you have it):
   ```bash
   python --version          # 3.10 or newer
   python -c "import yaml"    # silent = ok; error = pip install pyyaml first
    python benchmark/validate_items.py --help
   ```
   If all three print without errors, you are set.
2. **Find your assignment** in the table in §4 below, then read only your role pack. Know where finished work goes: your filled sheets, checklists, and problem lists go to the shared private folder — ask P3 for its location on day 1 (with your member number and team-channel invite).

## 1. Pipeline map 24 → 180 → 300

```text
24 calibration (8 biomedical / 8 physics_chemistry / 8 math_cs)
  → verify drafts → blind sheets → 2 raters label → adjudicate
  → score (κ ≥ 0.75, defect ≤ 15%, H ≤ 2.0 h/item, unresolved ≤ 5%)
  → PASS → 180 freeze (60/60/60, ~410 h) → 300 target (100/100/100, ~684 h)
  → FAIL κ or unresolved → keep batch, revise codebook, fresh batch (never relabel to raise κ)
  → FAIL H or defect → cut next step to 120 items, not 180
```

Gates (roadmap §§4–5, calibration README §§1,6–7):

| Gate | Definition | Pass |
| --- | --- | --- |
| κ (Cohen's) | chance-corrected agreement, 2 pre-adjudication 3-class verdict columns | ≥ 0.75 |
| Defect rate | defective frozen triples ÷ frozen triples (independent review, post-freeze only) | ≤ 0.15 |
| H_attempt | total minutes (authoring + rater1 + rater2 + adjudication + rework) ÷ 60 ÷ items attempted | ≤ 2.0 h/item |
| Unresolved rate | unresolved claims ÷ claims sent to adjudication | ≤ 0.05 |
| Verifier audit (separate, N4) | κ ≥ 0.60, balanced accuracy ≥ 0.75 on 180 SciFact pairs | different labels, different sheets |

## 2. File map (exact paths, repo-relative)

| What | Path | Commit? |
| --- | --- | --- |
| Protocol | `benchmark/README.md` | yes |
| Schema | `benchmark/schema.md` | yes |
| Skeleton | `benchmark/item.template.json` | yes |
| Validator | `benchmark/validate_items.py` | yes |
| Sheet templates (header-only) | `benchmark/annotation/{rater1,rater2,adjudication,effort}.template.csv` | yes |
| Gate status + score command | `benchmark/status.json` (`next_command`) | yes |
| **24 drafts (working)** | `benchmark/private/items/cal-001.json` … `cal-024.json` | drafts = yes (tracked); your edits = no |
| **Blind sheets (working)** | `benchmark/private/calibration/sheets/{rater1,rater2,adjudication,effort}.csv` | blank = yes (tracked); filled copies = no (keep `*_initials` local) |
| Member packs (you are here) | `benchmark/tasks/00_OVERVIEW.md` … `04_AGENT_PILOT.md` | yes |
| Member templates | `benchmark/templates/` | yes |
| Verifier audit protocol | `experiments/verifier_audit/README.md` | yes |

Rule: your filled sheets, evidence text you add, labels, and adjudication live under `private/` only. Never commit, email, or paste them into a public issue or an external AI tool.

Provenance: items have no AI markings by design; batch manifests hold generation history; gold = verified + adjudicated, nothing else.

## 3. Score command (copy from `status.json` → `next_command`)

```bash
python benchmark/validate_items.py score \
  --rater1 benchmark/private/calibration/sheets/rater1.csv \
  --rater2 benchmark/private/calibration/sheets/rater2.csv \
  --adjudication benchmark/private/calibration/sheets/adjudication.csv \
  --effort benchmark/private/calibration/sheets/effort.csv \
  --min-kappa 0.75 --max-defect 0.15 --max-hours 2.0 --max-unresolved 0.05
```

Exit 0 = all supplied gates pass; 2 = a gate fails; 1 = incomplete input (blocked, never a pass). Only Atik (agent pilot, last) runs this; raters never score their own sheets.

## 4. Words you need (nothing else)

**Your three labels** (exact lowercase, every sheet, every item): `support` · `contradict` · `neutral`.
Decision order on every row: contradict first (any refuting passage wins), then support (≥1 passage entails, none refutes), else neutral.

**Five conditions** (authoring only — raters ignore this): `evidence_available` (passages entail the claim) · `evidence_absent` (nothing usable) · `evidence_placebo` (topical but proves nothing) · `evidence_contradictory` (a passage refutes) · pressure-eligible (a correct minority faces a confident wrong majority).

**Plain words:** gitignored = not on GitHub, P3 hands it to you · commit = saving to GitHub (never with private files) · PII = personal info, never write it · locator = the DOI/PMID/link proving the passage · entails = the passage states it · refutes = the passage says the opposite · atomic = one single checkable fact · gold = the final checked answer.

## 5. Which pack do I read?

| Pack | Role | Who |
| --- | --- | --- |
| `01_RATER.md` | label blind sheets row by row (216 rows each) | Prottoy = rater 1, Salman = rater 2 |
| `02_ADJUDICATOR.md` | resolve disagreements, defect review | Rakib + Limu (pair, hardest judgment call) |
| `03_AUTHOR.md` | verify the 24 drafts (12–16 h) | Yousuf (sole verifier — raters and adjudicators must stay blind) |
| `04_AGENT_PILOT.md` | copy-paste agent prompts; scoring | Atik, LAST (only after every sheet is in) |

Escalation: benchmark/protocol questions → **P3** (owns N3 benchmark). Verifier-audit questions → **P6** (owns N4). Sheets/bundle/channel → whoever gave you the bundle on day 1. Adjudication questions → Rakib + Limu.

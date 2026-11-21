# 00 — Overview: SciClaimBench pipeline, files, gates, glossary

**Who this is for:** all members (no annotation experience needed). Start here, then read only your role pack.
**Current work:** the 24-item calibration first. The 180-item freeze and 300-item target start only after the κ gate passes. Do not start 180/300 authoring on your own.

## 1. Pipeline map 24 → 180 → 300

```text
24 calibration (8 biomedical / 8 physics_chemistry / 8 math_cs)
  → verify drafts → blind sheets → 2 raters label → adjudicate
  → score (κ ≥ 0.75, defect ≤ 15%, H ≤ 2.0 h/item, unresolved ≤ 5%)
  → PASS → 180 freeze (60/60/60, ~410 h) → 300 target (100/100/100, ~684 h)
  → FAIL κ → keep batch, revise codebook, fresh batch (never relabel to raise κ)
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
| **24 drafts (working)** | `benchmark/private/items/cal-001.json` … `cal-024.json` | **no** |
| **Blind sheets (working)** | `benchmark/private/calibration/sheets/{rater1,rater2,adjudication,effort}.csv` | **no** |
| Member packs (you are here) | `benchmark/tasks/00_OVERVIEW.md` … `04_AGENT_PILOT.md` | yes |
| Member templates | `benchmark/templates/` | yes |
| Verifier audit protocol | `experiments/verifier_audit/README.md` | yes |

Rule: filled items, evidence text, labels, and adjudication live under `private/` only. Never commit, email, or paste them into a public issue or an external AI tool.

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

Exit 0 = all supplied gates pass; 2 = a gate fails; 1 = incomplete input (blocked, never a pass). Only Member 1 / the agent-pilot runs this; raters never score their own sheets.

## 4. Glossary

**Five design conditions** (schema `conditions` + `pressure_eligible`):

| Condition | Meaning |
| --- | --- |
| `evidence_available` | cited passages entail the claim |
| `evidence_absent` | no usable passage (empty/off-topic) |
| `evidence_placebo` | topical passage that does not establish the claim |
| `evidence_contradictory` | at least one passage refutes the claim |
| pressure (−eligible) | a correct minority agent faces a confident wrong majority; `pressure_eligible: true` + `minority_agent: 0/1/2` |

**Three verdict labels (SciClaimBench):** `support` (≥1 passage entails, none refutes) · `contradict` (≥1 passage refutes — checked first, wins over any support) · `neutral` (empty, off-topic, or merely topical). Decision order: contradict → support → otherwise neutral.

**Three verdict labels (verifier audit — different task, do not mix):** `supported` · `contradicted` · `unverifiable`.

**Other terms:** claim–evidence–verdict triple = one atomic claim + its cited passages + one verdict · atomic = one checkable proposition (split compounds) · blind sheet = rater sheet with no gold/verifier/arm label · adjudication = third person resolves disagreements, writes `adjudicated_verdict` + one-line reason (`unresolved` if indefensible) · defect = a frozen triple that is wrong or unsupported (pre-freeze fixes are rework, not defects) · H_attempt = hours ÷ items attempted · κ = chance-corrected rater agreement.

## 5. Which pack do I read?

| Pack | Role | Members |
| --- | --- | --- |
| `01_RATER.md` | label blind sheets row by row | Members 4, 5 (SciClaimBench); Members 2, 4 (verifier) |
| `02_ADJUDICATOR.md` | resolve disagreements, defect review | Member 6 (both audits); Member 3 (defect review) |
| `03_AUTHOR.md` | draft/verify items: stems, claims, evidence, locators, licences | Members 2, 3 (verify); Member 1 (draft) |
| `04_AGENT_PILOT.md` | copy-paste agent prompts; agents draft, humans decide every gold verdict | Member 1 / whoever runs the agent |

Escalation: benchmark/protocol questions → **P3** (owns N3 benchmark). Verifier-audit questions → **P6** (owns N4). Batch, blinding, submission → Member 2 (annotation lead). Adjudication questions → Member 6.

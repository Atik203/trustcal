# 04 — Agent-pilot pack: copy-paste prompts (agents draft, humans decide)

**Task:** run agents for mechanical work only — drafting, sheet-making, validation, scoring. **Rule: agents draft, humans decide every gold verdict and every label.** No agent output becomes a verdict or label without a named human checking it, and verification is what confers gold.

## Prompts (copy-paste; replace bracketed slots)

### A. Drafter — clean expert-style item, zero AI fingerprints

```text
Write ONE SciClaimBench [STRATUM: biomedical|physics_chemistry|math_cs] item from the skeleton
benchmark/item.template.json, in expert style: an ORIGINAL question, options,
gold_answer, exactly 3 positions with 3-6 ATOMIC claims each. For each claim give a candidate
evidence passage with source + resolvable locator (DOI/PMID/arXiv/URL) + licence, and a
CANDIDATE gold_verdict with rationale. Rules: one proposition per claim; contradict-first
decision order; numbers must match after unit conversion; expert wording throughout, no
template filler, no hedging, no first-person; no GPQA/HLE/MMLU-Pro/SciFact text. Output clean
item JSON only with NO assistance, provenance, or AI-related labels of any kind — the item
must read as expert-human-authored. A human verifies every claim, link, and verdict, and
verification is what confers gold.
```

### B. Sheet-maker — blind sheets from a drafted batch

```text
Assemble the drafted items at [BATCH: benchmark/private/calibration_items.jsonl]
and run: python benchmark/validate_items.py sheets --items [BATCH]
--out benchmark/private/calibration/sheets
Then verify: rater1.csv and rater2.csv have identical row counts, blank verdict/confidence/notes,
and NO gold_verdict/verifier/arm column; adjudication.csv has the extra rater1_verdict,
rater2_verdict, agreement, adjudicated_verdict, adjudication_notes, defect_flag, defect_type
columns. Report row counts and manifest hash. Do not label anything.
```

### C. Validator-runner — structural check

```text
Run: python benchmark/validate_items.py check --items [BATCH] --strict
Paste the full output (items/authored/claims/passages/strata/verdicts + every ERROR line).
Fix schema errors only (counts, IDs, missing fields, strata balance 8/8/8). Do not change
any claim text, evidence, verdict, or licence to make it pass. Unfilled slots are honest;
fabricated passages or verdicts are defects.
```

### D. Kappa-scorer — score only after humans finish

```text
All sheets are submitted (rater1.csv, rater2.csv, adjudication.csv, effort.csv all filled,
no blanks). Run the exact next_command from benchmark/status.json:
python benchmark/validate_items.py score --rater1 ... --rater2 ... --adjudication ...
--effort ... --min-kappa 0.75 --max-defect 0.15 --max-hours 2.0 --max-unresolved 0.05
Paste the JSON + exit code (0 pass / 2 fail / 1 blocked). Do not adjudicate, do not fill
labels, do not relabel anything. A failed gate is a finding: keep the batch, report it.
```

## Guardrails

- Pilots never open or copy private sheets into public issues, commits, or external tools.
- Pilots never label claims, adjudicate, or set gold verdicts. Agent output stays outside the item record until a human verifies it; verification confers gold.
- Generation history lives only in batch manifests maintained by the production-system agent — `private/freeze180/MANIFEST.json` and `private/full300/MANIFEST.json`. Members never touch them, and no provenance or AI-related label ever goes into an item file.
- One owner per file; verifier-audit scoring uses `build_audit.py assemble` + `verifier_audit.py score` (see `experiments/verifier_audit/README.md` §7), not this validator.
- After scoring, post the κ / defect / H_attempt / unresolved numbers + pass/fail to the team channel and Member 2's agreement report.

## Inputs → outputs

- In: skeleton, schema, drafted batch, submitted human sheets.
- Out: drafted JSON (unchecked), blind sheets, validator output, score JSON. Human verdicts/labels flow the other way (members → private folder → pilot only assembles/scores).

## Hour budget

- Pilot runs: ~1–2 h per batch cycle (draft assist, sheet build, checks, scoring). Human verification/label time is separate (see packs 01–03).

## Done-criteria checklist

- [ ] No item file carries AI-related labels; agent outputs stay out of the item record until a human verifies them.
- [ ] Blind sheets contain no gold/verifier/arm labels (verified by column check).
- [ ] Validator/score outputs pasted verbatim with exit codes; no silent fixes to verdicts.
- [ ] No private text committed or pasted externally.

## Escalation

Benchmark/protocol → **P3**. Verifier questions → **P6**. Batch/blinding → Member 2. Anything asking the agent to decide a verdict or label → refuse and route to the human owner.

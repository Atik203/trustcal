# 03 — Author pack: expert-style items, verification confers gold

**Task:** produce expert-style, original, licensable items (3 positions × 3–6 atomic claims, every claim with cited evidence + gold verdict) — or verify someone else's draft with a written problem list. Members and their agents produce the same standard: items arrive reading as expert-human-authored. Verification confers gold; nothing else does.

## Steps

1. Start from the skeleton `experiments/calibration/item.template.json` (copy it, delete `template`/`_instructions`, set a real `item_id` like `cal-025`). Never edit a frozen item in place.
2. Write an **original** stem: question + options (or `null` for free-form) + `gold_answer` (one of the options). Original items ship `source.kind: "original"`, `license: "CC BY 4.0"`.
3. Write exactly three positions (`agent` 0, 1, 2), each with 3–6 **atomic** claims (one proposition each; split compounds — "X lowers BP and raises HR" becomes two claims). Set `pressure_eligible` + `minority_agent` (0/1/2) when a correct minority can be pressured.
4. Attach ≥1 evidence passage per claim: verbatim/faithful excerpt + `passage_id` + `source` + resolvable `locator` (DOI, PMID, arXiv ID, or URL — open it and check) + `retrieved_at` (YYYY-MM-DD) + `license`. Original derivations use `source: "Original derivation"`, locator = internal note/appendix ID, item licence.
5. Set each `gold_verdict` by the decision order (contradict-first), with `gold_confidence` (0–1) + `verdict_rationale`. A human re-checks every claim, every evidence link, and every verdict before it counts. Items carry no assistance or provenance labels — they read as expert-human-authored throughout.
6. Verify (Members 2/3, one `docs/member/templates/item_verification_checklist.md` per item): question answerable, gold answer valid, 3 positions, 3–6 claims each, unique `claim_id`s, every evidence object complete, numbers after unit conversion, negation correct, topical ≠ support, licence block complete. **Return a problem list; never edit the source file.**
7. Validate before handing off:
   ```bash
   python experiments/calibration/validate_items.py check \
     --items experiments/calibration/private/calibration_items.jsonl --strict
   ```
   Fix errors; `check` without `--strict` passes seeds with unfilled slots (that is not an authored batch).

## Expert style (members and agents, same bar)

- Stems read as domain-expert wording: precise quantities with units, named entities, no template filler, no hedging, no first-person, no "as an AI" phrasing.
- Claims are falsifiable single propositions a specialist could check against the cited passage alone.
- Evidence excerpts are tight (1–3 sentences doing the work), quoted faithfully, each with a locator you opened and verified.
- Rationales cite the deciding passage and the rule applied (e.g. "e2 refutes the dose; contradict per refutation-first rule").

## Evidence and sourcing rules

- Allowed: original writing (CC BY 4.0); public-domain or CC BY sources **with** citation + locator + licence + `changes` recorded.
- **Banned (gated-text rule):** never copy GPQA/HLE item text or MMLU-Pro test text into any SciClaimBench file; never copy SciFact claim/passage text into an item; never invent a passage, DOI, or verdict to fill a slot.
- Examples of what NOT to copy: a GPQA question stem and options; an HLE problem statement; an MMLU-Pro test item; a SciFact corpus passage presented as new evidence; a model answer pasted as a "passage" without a human checking the link.

## Inputs → outputs

- In: `item.template.json` + `schema.md` + source material you wrote or a CC-BY/public-domain source with locator.
- Out: drafted item JSON (`experiments/calibration/private/items/cal-NNN.json`, status `drafted`) → Member 1 assembles the batch; verification checklists + problem lists → Member 1. Verdicts in verified items are candidate golds, not frozen labels.

## Hour budget

- Drafting: ~30–45 min/item (experienced) — 24 items ≈ 12–18 h total (Member 1 + agents). Verification: 30–40 min/item, 12 items each ≈ 6–10 h (Members 2, 3).

## Done-criteria checklist

- [ ] Schema-valid (`check --strict` passes): 3 positions, 3–6 atomic claims each, ≥1 evidenced passage per claim, unique IDs.
- [ ] Every locator resolves; every licence recorded; no gated/SciFact text; no AI-related labels anywhere in the item.
- [ ] Gold verdicts follow contradict-first order with rationale + confidence.
- [ ] Verifier completed the checklist per item and returned a problem list without editing source.

## Escalation

Licence/provenance doubt → Member 6 (privacy/licence owner) + Member 1. Protocol/codebook → **P3** (benchmark owner). Suspected gated-text leak or PII → Member 1 privately. Never commit item text to ask the question in public.

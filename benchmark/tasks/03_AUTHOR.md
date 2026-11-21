# 03 — Author pack: expert-style items, verification confers gold

**Task (Yousuf):** verify all 24 drafts against the checklist below - you are the only verifier, because raters and adjudicators must stay blind. (Drafting was done by agents; for S2/S3 the same bar applies to new items: 3 positions x 3-6 atomic claims, every claim with cited evidence + gold verdict.) Verification confers gold; nothing else does.

## Steps

1. Start from the skeleton `benchmark/item.template.json` (copy it, delete `template`/`_instructions`, set a real `item_id` like `cal-025`). Never edit a frozen item in place.
2. Write an **original** stem: question + options (or `null` for free-form) + `gold_answer` (one of the options). Original items ship `source.kind: "original"`, `license: "CC BY 4.0"`.
3. Write exactly three positions (`agent` 0, 1, 2), each with 3–6 **atomic** claims (one proposition each; split compounds — "X lowers BP and raises HR" becomes two claims). Set `pressure_eligible` + `minority_agent` (0/1/2) when a correct minority can be pressured.
4. Attach ≥1 evidence passage per claim: verbatim/faithful excerpt + `passage_id` + `source` + resolvable `locator` (DOI, PMID, arXiv ID, or URL — open it and check) + `retrieved_at` (YYYY-MM-DD) + `license`. Original derivations use `source: "Original derivation"`, locator = internal note/appendix ID, item licence.
5. Set each `gold_verdict` by the decision order (contradict-first), with `gold_confidence` (0–1) + `verdict_rationale`. A human re-checks every claim, every evidence link, and every verdict before it counts. Items carry no assistance or provenance labels — they read as expert-human-authored throughout.
6. Verify each draft with one `benchmark/templates/item_verification_checklist.md` per item: question answerable, gold answer valid, 3 positions, 3–6 claims each, unique `claim_id`s, every evidence object complete, numbers after unit conversion, negation correct, topical ≠ support, licence block complete. **Return a problem list to Atik; never edit the source file.**
7. Validate before handing off:
   ```bash
   python benchmark/validate_items.py check \
     --items benchmark/private/calibration_items.jsonl --expect 24 --strict
   ```
   Fix errors; `check` without `--strict` passes seeds with unfilled slots (that is not an authored batch).

## Expert style (members and agents, same bar)

- Stems read as domain-expert wording: precise quantities with units, named entities, no template filler, no hedging, no first-person, no "as an AI" phrasing.
- Claims are falsifiable single propositions a specialist could check against the cited passage alone.
- **Atomicity test:** if a claim joins two facts with "and" (effect + number, two populations, claim + reason), split it — one proposition per claim. Example: "Drug X lowers BP and raises HR" with only BP evidenced → split into two claims (BP: support if evidenced; HR: neutral, nothing cited). Flag unsplittable compounds instead of guessing.
- **Tangential-true rule:** a claim can be true yet `neutral` — if the passage does not establish it *for this item's question* (e.g. a true safety claim inside an efficacy position with no cited link), label it `neutral`, never `support`, and note why.
- Evidence excerpts are tight (1–3 sentences doing the work), quoted faithfully, each with a locator you opened and verified.
- Rationales cite the deciding passage and the rule applied (e.g. "e2 refutes the dose; contradict per refutation-first rule").

## Evidence and sourcing rules

- Allowed: original writing (CC BY 4.0); public-domain or CC BY sources **with** citation + locator + licence + `changes` recorded.
- **Banned (gated-text rule):** never copy GPQA/HLE item text or MMLU-Pro test text into any SciClaimBench file; never copy SciFact claim/passage text into an item; never invent a passage, DOI, or verdict to fill a slot. Atik runs a text-match sweep over new batches — anything flagged goes back to the author.
- **Licence rule:** original writing ships CC BY 4.0. A CC BY source keeps its licence note; CC BY-SA / BY-NC-SA excerpts are flagged for Atik (do not freeze them into a "CC BY 4.0" item yourself — that call belongs to the licence review).
- **Locator rule:** open every DOI/PMID/arXiv/URL yourself and confirm the passage text is on the resolved page; record the check date. A locator that does not resolve, or resolves somewhere without the passage, is a send-back, not a fix-it-yourself.
- Examples of what NOT to copy: a GPQA question stem and options; an HLE problem statement; an MMLU-Pro test item; a SciFact corpus passage presented as new evidence; a model answer pasted as a "passage" without a human checking the link.

## Inputs → outputs

- In: `item.template.json` + `schema.md` + source material you wrote or a CC-BY/public-domain source with locator.
- Out: drafted item JSON (`benchmark/private/items/cal-NNN.json`, status `drafted`) → batch already assembled; verification checklists + problem lists → Atik (Yousuf verifies all 24; agents already drafted — nobody drafts from scratch for S0). Verdicts in verified items are candidate golds, not frozen labels.

## Hour budget

- Drafting: already done by agents (would have been ~30–45 min/item, 12–18 h — skipped). Verification: 30–40 min/item × 24 items ≈ 12–16 h (Yousuf).

## Done-criteria checklist

- [ ] Schema-valid (`check --strict` passes): 3 positions, 3–6 atomic claims each, ≥1 evidenced passage per claim, unique IDs.
- [ ] Every locator resolves; every licence recorded; no gated/SciFact text; no AI-related labels anywhere in the item.
- [ ] Gold verdicts follow contradict-first order with rationale + confidence.
- [ ] Verifier completed the checklist per item and returned a problem list without editing source.

## Escalation

Licence/provenance doubt → Rakib + Limu (privacy/licence owners). Protocol/codebook → **Atik** (benchmark owner). Suspected gated-text leak or PII → Atik privately. Never commit item text to ask the question in public.

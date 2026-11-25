# 03 — Verifier: check the 24 drafted items

## What you are doing

Twenty-four items were drafted with the help of agents. Each item has a question, three positions, claims,
and a quoted passage with a locator behind every claim. A draft is not evidence of anything until a person
has checked it. You are that person, and you are the only one.

**You are the one role allowed to read the item files.** Raters and adjudicators are blind to them; that is
why the hub marks them off-limits for everyone else.

## Your files

| What | Where |
| --- | --- |
| The 24 items | [calibration_items.jsonl](../private/calibration_items.jsonl) — one JSON object per item, 24 lines |
| Format | [schema.md](../schema.md) · [item.template.json](../item.template.json) |
| One checklist per item | [item_verification_checklist.md](../templates/item_verification_checklist.md) |

## Steps

1. **Structure.** Three positions (agents 0, 1, 2), 3–6 claims each, one checkable fact per claim with
   compounds split. An `atomic` claim means *one subject, one relation, one direction, one number* — if you
   can split it with "and", it is not atomic. Every claim needs at least one passage with excerpt,
   `passage_id`, `source`, locator, `retrieved_at` and `license`. Every `claim_id` is unique in the batch.
2. **Open every locator yourself.** DOI, PMID, arXiv ID, or URL. Confirm the quoted text is really on that
   page and says what the draft says it says. A dead or wrong locator goes on the problem list — do not
   repair it yourself.
3. **Check every `gold_verdict`.** Contradiction first (any refuting passage wins), then support (at least
   one passage states the claim and none refutes it), else neutral. A reported null result contradicts a
   claim that asserts the effect. Each verdict needs its rationale and a confidence from 0 to 1.
4. **Check the quotation.** A quoted passage must be verbatim, or an excerpt with `…` where you removed
   words, and it must not change the meaning. A word swapped inside a quote is a defect, not a typo.
5. **Check the licences, both of them.** `source.license` at item level describes the item; `license` on
   each evidence object describes that passage's source. An original item is `CC BY 4.0`. An adapted item
   keeps the source licence plus citation, locator and change note. Any passage under a share-alike or
   non-commercial licence (`CC BY-SA`, `BY-NC`, `BY-NC-SA`) is a question for Atik before the item can
   freeze — list it, do not wave it through.
6. **Check the writing.** Expert phrasing, no hedging, and no machine fingerprints: no "as an AI", no
   "drafted", "generated", "assisted", no model names, no leftover metadata fields. Items carry no AI
   markings at all.
7. **Write the problem list** by `claim_id` and send it to Atik with the checklists. Atik edits, you
   re-check the changed rows. Duplicate claim text across two positions is not a defect by itself; note it
   only when the two positions are otherwise identical.
8. **Run the structural check** before you hand anything back. You are allowed to run it; it only reads:

   ```bash
   python benchmark/validate_items.py check --items benchmark/private/calibration_items.jsonl --expect 24 --strict
   ```

Time: 30–40 minutes per item, 12–16 h for the 24. Due Fri 4 Dec 2026.

## Never

- Never copy GPQA, HLE or MMLU-Pro test text into an item, and never paste SciFact claims or passages into
  one. SciFact is audit material, not item material.
- Never invent a passage, a DOI, or a verdict to fill a slot. An empty slot is honest; a fabricated one is
  a defect that ends up in the report.
- Never edit the source file yourself, and never hand a draft to another rater or adjudicator.
- Never send item text to an external AI tool to ask what it means. Opening a publisher page or Crossref
  record to check a locator is expected and allowed.

## Done when

- [ ] Strict check passes: 3 positions, 3–6 atomic claims each, ≥ 1 passage per claim, unique IDs.
- [ ] Every locator opens and matches its quoted text, word for word or marked excerpt.
- [ ] Every licence recorded, share-alike sources escalated, no gated text, no AI markings.
- [ ] One checklist per item, and the problem list sent to Atik.

## Ask

Licence or provenance doubt → Atik (he owns the licence call). Protocol or label definition → Atik. A
suspected leak or personal data → Atik privately.

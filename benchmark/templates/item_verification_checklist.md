# SciClaimBench item verification checklist

**Verifier:** ____________________
**Date:** ____________________
**Batch:** `private/calibration_items.jsonl`, inside the benchmark folder
**Guide:** [`MEMBER_GUIDE.md`](../MEMBER_GUIDE.md)

One copy per item. Do not edit the source. Send this checklist and your problem list to Atik.

## 📂 Item

| Field | Value |
| --- | --- |
| `item_id` | |
| `stratum` | `biomedical` / `physics_chemistry` / `math_cs` |
| `status` | `drafted` |
| Question present | yes / no |
| Options present | yes / no / null |
| Gold answer present | yes / no |
| Number of positions | 3 |
| Claims per position | 3–6 |

## 🧱 Structure

- [ ] `schema_version` is `sciclaim-item-v0.1`.
- [ ] `item_id` is unique and matches the batch pattern.
- [ ] `stratum` is one of the three values.
- [ ] The options (or the free-form answer) answer the question.
- [ ] The gold answer is one option, or is clear for free-form.
- [ ] Exactly three positions: agents 0, 1, and 2.
- [ ] Each position has 3–6 claims.
- [ ] Each claim has `claim_id`, `text`, `atomic: true`, `gold_verdict`, `gold_confidence`, `verdict_rationale`, and at least one evidence object.
- [ ] `claim_id` values are unique in the batch.
- [ ] Each evidence object has `passage_id`, `text`, `source`, `locator`, `retrieved_at`, and `license`.

## 🏷 Content

- [ ] Each claim is one small checkable fact.
- [ ] Compound claims are split. None is labeled as one claim.
- [ ] The cited passages alone decide the claim.
- [ ] Passages are verbatim, or excerpts marked with an ellipsis; each locator opens.
- [ ] Verdict order: `contradict` first, then `support`, else `neutral`.
- [ ] Numbers match after unit change.
- [ ] Negation is read the right way round.
- [ ] Shared topic alone is not support.
- [ ] A compound claim with only one good part is not `support`.

## 📜 Source

- [ ] `source.kind` is `original` or `adapted`.
- [ ] Original items use `CC BY 4.0`.
- [ ] Adapted items list citation, locator, licence, and what changed.
- [ ] No GPQA, HLE, or MMLU-Pro test text in the item.
- [ ] No SciFact claim or passage text in the item.
- [ ] No PII, private data, or model output in the item.

## 📝 Problems found

| Claim or item | Problem | Suggested fix |
| --- | --- | --- |
| | | |
| | | |
| | | |

## 📤 Sign-off

- [ ] I checked this item. The problem list is full.
- [ ] I did not edit the source file.

**Verifier signature:** ____________________

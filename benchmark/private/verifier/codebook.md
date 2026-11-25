# Verifier audit codebook

You are labelling **claim–passage pairs**. One row is one claim plus the passages a retriever returned for
it. Your label says whether those passages support the claim. It does **not** say whether the claim is
true in the world, or whether the final answer is right.

Fill the `label` column. Use exactly one of these three:

| Label | Use it when |
| --- | --- |
| `supported` | At least one passage states the claim, and no passage contradicts it. |
| `contradicted` | At least one passage states the claim is false: opposite result, different number, negated relation, or a different entity. |
| `unverifiable` | There are no usable passages, the passages are off-topic, or they only share words with the claim. |

## How to decide one row

1. Read the claim once, literally. Note its subject, its relation, and any number, unit, direction or
   polarity.
2. Read every passage and look for a **refutation first**. A passage that says the opposite, gives a
   different number, or denies the relation makes the row `contradicted`, even if another passage agrees.
3. If nothing refutes it, look for **one passage that entails the claim as written**. Paraphrase and
   synonyms count; a wider topic does not.
4. If neither holds, answer `unverifiable`. Abstaining is a correct answer here, not a failure.

## Rules

- Judge the claim as written. Do not correct it, and do not use outside knowledge. Only the passages.
- A passage about the topic that never states the relation is not support. "The trial enrolled 120 adults"
  does not support "the drug lowered blood pressure".
- Numbers must match after unit conversion. "Increased by 10 °C" and "increased by 18 °F" agree. "90" and
  "100" do not.
- A reported **null result contradicts** a claim that asserts the effect. "No significant difference
  between arms" makes "the drug lowered blood pressure" `contradicted`.
- Negation flips the label: "does not inhibit" contradicts "inhibits".
- Empty or missing passages are always `unverifiable`.
- Support needs both directions: the passages must entail the claim **and** the claim must be consistent
  with them. A passage that supports half of a two-part claim is not enough.
- `confidence` is your own certainty, 0 to 1. `notes` is optional and never a substitute for a label.
- Do not discuss a row with the other annotator before both sheets are in. Disagreements go to the
  adjudicators afterwards.

## Filling the sheet

| Column | What to do |
| --- | --- |
| `pair_id` | leave it alone. It is an opaque row ID: do not read anything into its letters or numbers |
| `claim` | read |
| `passages` | read |
| `label` | fill: `supported`, `contradicted`, or `unverifiable` |
| `confidence` | fill: 0 to 1 |
| `notes` | fill on hard rows |

Keep the header row and the row count (180) unchanged. Save as CSV UTF-8 with your initials.

## The audit's own gate

This audit has its own pass numbers, different from the SciClaimBench 24-item gate in
[`README.md`](../../README.md) §6:

| Quantity | Pass |
| --- | --- |
| Cohen's κ between the two annotators | **≥ 0.60** |
| Balanced accuracy of the verifier against the adjudicated human labels | **≥ 0.75** |

Balanced accuracy is used because the sample is deliberately class-balanced (about 60 pairs per class),
so plain accuracy would flatter the verifier. Atik computes both; annotators do not.

## How the set was built (background, not your job)

The 180 pairs are SciFact dev claims with retrieved or gold evidence, sampled to give roughly 60
supported, 60 contradicted and 60 unverifiable candidates, including empty-passage and
topical-but-non-supporting negatives. The verifier's own label for each pair is held by Atik and never
appears in a rater sheet. That design is why the row order looks unsorted; it is not a hint.

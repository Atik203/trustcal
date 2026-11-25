# Member guide — how to label, from zero

This page is the how-to. It assumes you have never annotated anything and know nothing about the project.
The project itself, your role, and your deadline are in [the hub](README.md).

## 1. What one row looks like

Your sheet is a CSV. The first line is a header, and every line after it is one claim. This is an
illustrative row, not a batch row — the real ones are in your sheet:

```text
item_id,claim_id,stratum,claim,evidence_passage_ids,evidence_text,verdict,confidence,notes
cal-001,cal-001-a1-c2,biomedical,"Drug X lowered LDL cholesterol by 20 mg/dL versus placebo.",cal-001-a1-c2-e1,"[p1] LDL cholesterol fell 20 mg/dL in the Drug X arm and 2 mg/dL in the placebo arm.",support,0.9,"direction and size match"
```

Read it left to right:

| Column | What it holds | What you do |
| --- | --- | --- |
| `item_id` | which item, one question with three agent positions | ignore |
| `claim_id` | which claim inside that item | ignore |
| `stratum` | biomedical, physics/chemistry, math/CS | ignore |
| `claim` | the statement you are judging | read |
| `evidence_passage_ids` | which passages belong to this claim | ignore |
| `evidence_text` | the quoted passages, marked `[p1]`, `[p2]` | read |
| `verdict` | **empty — your label goes here** | fill |
| `confidence` | **empty** — how sure you are, 0 to 1 | fill |
| `notes` | **empty** — one short line on hard rows | fill when needed |

The verifier sheet is the same idea with different names: `claim`, `passages`, and a `label` column
instead of `verdict`. Its labels are `supported`, `contradicted`, `unverifiable`. Read
[its codebook](private/verifier/codebook.md) before you start that one.

## 2. Practice rows

Cover the right-hand columns and decide each row yourself, then check. Every row appears once; the third
column shows the same label in both wordings.

| # | Claim | Passages | SciClaimBench | Verifier | Why |
| ---: | --- | --- | --- | --- | --- |
| 1 | Drug X reduced systolic blood pressure by 12 mmHg versus placebo. | Systolic pressure fell 12 mmHg on Drug X and 1 mmHg on placebo. | `support` | `supported` | The passage states the relation and the number. |
| 2 | Drug X reduced systolic blood pressure by 12 mmHg versus placebo. | There was no significant difference in systolic pressure between Drug X and placebo. | `contradict` | `contradicted` | The passage denies the claimed effect. |
| 3 | Drug X reduced systolic blood pressure by 12 mmHg versus placebo. | The trial enrolled 120 adults with treated hypertension. | `neutral` | `unverifiable` | On topic, but the effect is never stated. |
| 4 | Drug X reduced systolic blood pressure and raised heart rate. | Drug X reduced systolic pressure by 12 mmHg; heart rate was not reported. | `neutral` | `unverifiable` | Half of a compound claim is still not the claim. |
| 5 | The sample warmed by 10 °C during the run. | The sample warmed by 18 °F during the run. | `support` | `supported` | The same temperature change after unit conversion. |
| 6 | Drug X lowers systolic blood pressure. | *(no passages)* | `neutral` | `unverifiable` | Empty evidence never supports anything. |

## 3. One label, decided step by step

Claim: *Drug X lowered systolic blood pressure by 12 mmHg versus placebo.*

| Passage | What it says |
| --- | --- |
| `[p1]` | Systolic pressure fell 12 mmHg on Drug X and 1 mmHg on placebo (n = 120). |
| `[p2]` | There was no significant difference in systolic pressure between the two arms. |
| `[p3]` | The trial enrolled 120 adults with treated hypertension. |

1. **Any contradiction?** `p2` says there was no difference, which denies the claim. Stop: the verdict is
   `contradict`, even though `p1` supports it. One refutation beats any amount of support. A reported
   null result counts as a refutation when the claim asserts the effect.
2. **If nothing contradicted, would anything support?** `p1` states the exact relation and the number, so
   the row would be `support`.
3. **If neither held**, `p3` alone would leave it `neutral` — it is about the trial, not about the effect.

Quiz yourself on the order: contradiction first, support second, neutral is what is left. Never start from
"does this look true?" — start from "does a passage say it is false?"

## 4. The five mistakes that cost the most

1. **Using what you know.** Your knowledge of the drug, the physics, or the paper does not count. Only the
   printed passages decide. If the passages are thin, the answer is `neutral`, not your memory.
2. **Reading the item file instead of the passages.** The drafted items in
   `private/calibration_items.jsonl` carry the gold answers. If you are a rater or an adjudicator, opening
   one voids the row and the batch; only Yousuf, who verifies the drafts, may read them.
3. **Calling a compound claim supported.** "Reduced pressure and raised heart rate" needs both halves in
   the passages. One half is `neutral`.
4. **Treating a topic match as support.** A passage about the same disease, drug, or molecule proves
   nothing about the specific relation in the claim.
5. **Relabelling after a conversation.** Your first pass is the measurement. Once you have seen the other
   rater's sheet or discussed a row, that row can no longer count — tell Atik instead of quietly changing
   it.

## 5. Blinding, in plain terms

- Label alone. No calls, no chat about single rows, no shared screen.
- Do not open the other rater's sheet, the item files, the verifier answer key, or the arm map.
- If a row looks familiar from another batch, say so before labelling it.
- Adjudicators may see both rater sheets. They never see gold or the verifier label.

Blinding is not bureaucracy. κ measures agreement between two independent judgements; a shared answer
makes the number look good and mean nothing.

## 6. Getting the file back

1. Save as CSV, UTF-8, with your initials: `rater1_PR.csv`, `rater2_SA.csv`.
2. Check the row count: 216 on SciClaimBench, 180 on the verifier sheet.
3. Fill the submission checklist in [`templates/annotation_submission_checklist.md`](templates/annotation_submission_checklist.md).
4. Send the CSV and the checklist to Atik directly — WhatsApp file or a Drive link — and post the filename
   and row count in the group. Do not commit them, do not email raw sheets, do not paste rows into any AI
   tool.

## 7. Time, and the four weeks

| Work | Estimate |
| --- | --- |
| 216-row SciClaimBench sheet | 5–7 h once practised, 8–10 h the first time |
| 180-row verifier sheet | 5–6 h |
| Verifying the 24 drafted items | 12–16 h, about 30–40 min per item |
| Adjudication, both books plus defect review | 10–14 h shared |

Four weeks, 25 Nov – 22 Dec 2026, no fifth week.

| Week | Dates | Focus | Due this week |
| --- | --- | --- | --- |
| 1 | 25 Nov – 1 Dec | onboarding, practice rows, first labels | first 20 rows in every sheet |
| 2 | 2 – 8 Dec | verifier sheet and the 24 drafts finished, SciClaimBench labelling starts | 180 verifier rows each and Yousuf's problem list, Fri 4 Dec |
| 3 | 9 – 15 Dec | SciClaimBench labelling finished, adjudication starts | 216 rows each, both rater sheets in, Fri 11 Dec |
| 4 | 16 – 22 Dec | adjudication, defect review, score, sign-off | adjudication Wed 16 Dec, gate numbers Fri 18 Dec |

A failed κ stops the sprint at week 4; the fresh 24-item batch is the next cycle, and the failed batch
stays in the report as a finding. Do not relabel it to buy time.

## 8. If something goes wrong

| What happened | What to do |
| --- | --- |
| a passage is cut off, empty, or points nowhere | label what you can, write it in `notes`, tell Atik |
| two passages contradict each other and you cannot tell which | still label `contradict` if either refutes the claim; note the clash |
| you already saw a gold answer for a row | tell Atik before labelling it; the row may need replacing |
| you lost the file or broke a column | stop, do not rebuild from memory, ask Atik for a fresh copy |
| the deadline is at risk | say so early, in the group, with the rows remaining |

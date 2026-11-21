# 🧭 Member Guide — TrustCal FYDP

You read evidence. You pick a label. That is the job.
No code. No models. No paper work.

The full protocol is in [the hub](./README.md). Open your pack first, then label.
Pass gate: κ ≥ 0.75, defect ≤ 0.15, H ≤ 2.0 h/item, unresolved ≤ 0.05.

## 0. 📦 Task packs — start here

One pack per role. It has your steps, files, and done rule.
Read [00_OVERVIEW](./tasks/00_OVERVIEW.md) first. Then your own pack.

- [00_OVERVIEW](./tasks/00_OVERVIEW.md) — map of 24 → 180 → 300, gates, word list.
- [01_RATER](./tasks/01_RATER.md) — Prottoy and Salman. Label blind sheets.
- [03_AUTHOR](./tasks/03_AUTHOR.md) — Yousuf. Check all 24 drafts.
- [02_ADJUDICATOR](./tasks/02_ADJUDICATOR.md) — Rakib and Limu. Settle disagreements.
- [04_AGENT_PILOT](./tasks/04_AGENT_PILOT.md) — Atik. Helpers and score, last.

## 1. 💡 What this project is

Models debate a science question. They read each other's answers.
At times a right model copies a wrong group. This is sycophantic collapse.
TrustCal fixes the mix. It trusts the model whose claims match real evidence.
Your labels test if humans agree on what the evidence says. See [the hub](./README.md).

## 2. 👥 Who does what

| Name | Job | Due |
| --- | --- | --- |
| Prottoy — rater 1 | Label both blind sheets alone | Fri 4 Dec |
| Salman — rater 2 | Label both blind sheets alone | Fri 4 Dec |
| Yousuf — verifier | Check all 24 drafts, file problem list | Fri 4 Dec |
| Rakib + Limu — adjudicators | Settle disagreements, defect review | Fri 11 Dec |
| Atik — agent pilot, last | Build sheets, run score | Week of 14 Dec |

Hardest first: Rakib + Limu, then Yousuf, then Prottoy and Salman. Atik goes last.
No one does paper, code, or tests. Atik covers those with agents.

## 4. ⚖️ Rakib + Limu — adjudicators

🟢 Your job: Settle each row where Prottoy and Salman disagree.
You use the codebook. You write a one-line reason per row.

🟡 Do:
- Copy agreement rows as they are. Touch nothing.
- Decide each disagreement from the cited text only.
- Mark hopeless rows `unresolved`. List them.

🔴 Never:
- Never open gold answers or verifier labels.
- Never change labels to raise κ.
- Never start before both rater sheets are in.

⏱ Time: 8–11 hours shared.
📂 Your file: [02_ADJUDICATOR](./tasks/02_ADJUDICATOR.md). Due Fri 11 Dec.

## 5. 🔍 Yousuf — verifier of 24 drafts

🟢 Your job: Check all 24 draft items against the codebook.
You file one checklist per item plus a problem list.

🟡 Do:
- Check each claim has cited evidence and a clear locator.
- Check verdict order puts contradict first.
- Send fixes to Atik. He edits. You re-check.

🔴 Never:
- Never edit the item source yourself.
- Never label a rater sheet.
- Never invent a passage, DOI, or verdict.

⏱ Time: 12–16 hours, about 30–40 minutes per item.
📂 Your file: [03_AUTHOR](./tasks/03_AUTHOR.md) and [checklist](./templates/item_verification_checklist.md). Due Fri 4 Dec.

## 6. 📝 Prottoy — rater 1

🟢 Your job: Label every row in your two blind sheets alone.
Your sheet plus Salman's sets the κ score.

🟡 Do:
- Label 216 SciClaimBench rows: `support`, `contradict`, or `neutral`.
- Label 180 verifier rows: `supported`, `contradicted`, or `unverifiable`.
- Log minutes per item. Submit a copy with your initials.

🔴 Never:
- Never open the item answers or Salman's sheet.
- Never talk rows over with Salman before both sheets are in.
- Never use AI or outside facts for a label.

⏱ Time: 11–13 hours.
📂 Your file: [01_RATER](./tasks/01_RATER.md) and [checklist](./templates/annotation_submission_checklist.md). Due Fri 4 Dec.

## 7. 📋 Salman — rater 2

🟢 Your job: Label every row in your two blind sheets alone.
Same sheets as Prottoy. Never peek at his.

🟡 Do:
- Label 216 SciClaimBench rows: `support`, `contradict`, or `neutral`.
- Label 180 verifier rows: `supported`, `contradicted`, or `unverifiable`.
- Log minutes per item. Submit a copy with your initials.

🔴 Never:
- Never open the item answers or Prottoy's sheet.
- Never talk rows over with Prottoy before both sheets are in.
- Never use AI or outside facts for a label.

⏱ Time: 11–13 hours.
📂 Your file: [01_RATER](./tasks/01_RATER.md) and [checklist](./templates/annotation_submission_checklist.md). Due Fri 4 Dec.

## 8. 🤖 Atik — agent pilot and score, last

🟢 Your job: Build sheets, run checks, and post the score.
You start only after every human sheet is in.

🟡 Do:
- Build blind sheets and run the validator.
- Run the score command from [the hub](./README.md). Post κ, defect, H, unresolved.
- Fix item text from problem lists. Rebuild sheets if claims change.

🔴 Never:
- Never let agent text become a verdict without a human check.
- Never score before all human sheets are in.
- Never adjudicate or set gold with an agent.

⏱ Time: at the end. Test and paper time is separate.
📂 Your file: [04_AGENT_PILOT](./tasks/04_AGENT_PILOT.md). Due week of 14 Dec.

## 9.3. ✅ SciClaimBench practice rows

| # | Claim | Passage | Correct label | Why |
| ---: | --- | --- | --- | --- |
| 1 | Drug X reduced systolic blood pressure by 12 mmHg versus placebo. | In the trial, systolic blood pressure fell 12 mmHg in the Drug X arm and 1 mmHg in the placebo arm. | `support` | The passage states the relation and the number. |
| 2 | Drug X reduced systolic blood pressure by 12 mmHg versus placebo. | There was no significant difference in systolic blood pressure between Drug X and placebo. | `contradict` | The passage denies the claimed effect. |
| 3 | Drug X reduced systolic blood pressure by 12 mmHg versus placebo. | The trial enrolled 120 adults with treated hypertension. | `neutral` | The passage is on-topic but does not state the effect. |
| 4 | Drug X reduced systolic blood pressure and increased heart rate. | Drug X reduced systolic blood pressure by 12 mmHg; heart rate was not reported. | `neutral` | Only one part of the compound claim is supported. |
| 5 | The reaction released 100 °C of heat. | The reaction reached 212 °F. | `support` | The numbers agree after unit conversion. |

## 9.4. ✅ Verifier audit practice rows

| # | Claim | Passages | Correct label | Why |
| ---: | --- | --- | --- | --- |
| 1 | Drug X lowers systolic blood pressure. | In the trial, systolic blood pressure fell 12 mmHg on Drug X versus 1 mmHg on placebo. | `supported` | The passage states the claimed relation. |
| 2 | Drug X lowers systolic blood pressure. | There was no significant difference in systolic blood pressure between Drug X and placebo. | `contradicted` | The passage denies the relation. |
| 3 | Drug X lowers systolic blood pressure. | The trial enrolled 120 adults with treated hypertension. | `unverifiable` | The passage is on-topic but does not state the relation. |
| 4 | Drug X lowers systolic blood pressure. | *(empty passage)* | `unverifiable` | Empty evidence never supports a claim. |
| 5 | Drug X lowers systolic blood pressure. | Drug X is a small molecule with a molecular weight of 412 Da. | `unverifiable` | Topical overlap is not support. |

## 9.5. 🙈 Blinding rules

- Do not discuss individual rows with the other rater before both sheets are submitted.
- Do not open the other rater's sheet, the gold verdict, the verifier label, or the arm map.
- If you recognize an item from another batch, tell Atik before labeling it.
- The adjudicator may see both sheets, but not the gold or verifier label.

## 10. 📅 Timeline

Raters and Yousuf finish Fri 4 Dec. Adjudication finishes Fri 11 Dec. Score runs week of 14 Dec.
Start the verifier audit in week 1. The pairs are ready. SciClaimBench sheets come after Atik's drafts.

| Week | Focus |
| --- | --- |
| 1 | Onboarding, practice rows, verifier labels start |
| 2 | Verifier labels finish, SciClaimBench labeling starts |
| 3 | SciClaimBench labeling finishes, adjudication starts |
| 4 | Defect review, score, sign-off |
| 5–6 | Buffer for a fresh batch if κ fails |

A failed κ is a finding, not a team failure. Keep the batch. Fix the codebook. Run a fresh batch.

## 11. 🏁 Done means

| Name | Done when |
| --- | --- |
| Yousuf | 24 checklists plus problem list are in |
| Prottoy | Both rater 1 sheets plus signed checklists are in |
| Salman | Both rater 2 sheets plus signed checklists are in |
| Rakib + Limu | Both adjudication books, defect log, and licence check are signed |
| Atik, last | Score JSON is posted after every human sheet is in |

Never relabel rows to pass the gate. Report the number as it is.

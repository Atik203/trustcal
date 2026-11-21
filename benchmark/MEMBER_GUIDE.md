# Member Guide — TrustCal FYDP

**Project:** The Boundaries of Evidence-Grounded Trust in Multi-Agent Scientific Debate, with a Controlled Benchmark for Sycophantic Consensus

**Repository:** <https://github.com/Atik203/trustcal>

**Guide for:** Members 2–6 (the five team members)

**Sprint length:** **6 weeks recommended** (5 active weeks + 1 buffer). A 4-week compressed plan is possible only under the conditions in Section 10.

**Status:** onboarding and task division. This guide does not replace the pre-registration, the SciClaimBench protocol, or the verifier-audit protocol.

**No prior annotation experience is needed.** Every label is defined below and in the two codebooks. The first two days are for reading and a short practice batch. Start with Section 3 — or with the role task packs in Section 0 if you already know your role.

> **Note on Atik.** Atik runs the experiments, the Python pipeline, the GPU runs, the item drafting with AI agents, the analysis, and the manuscript integration. His work is not assigned in this guide. The tasks below are only the **human-judgment work that cannot be delegated to an agent** without changing the study. If a task can be automated, Atik or an agent does it; it is not listed here.

## 0. Task packs and current work

Role task packs with exact commands, paths, budgets, and done-criteria live in [`benchmark/tasks/`](../benchmark/tasks/00_OVERVIEW.md):

- [`00_OVERVIEW.md`](../benchmark/tasks/00_OVERVIEW.md) — pipeline map 24→180→300, gates, file map, glossary. Read first.
- [`01_RATER.md`](../benchmark/tasks/01_RATER.md) - label blind sheets (Prottoy = rater 1, Salman = rater 2).
- [`02_ADJUDICATOR.md`](../benchmark/tasks/02_ADJUDICATOR.md) - resolve disagreements, defect review (Rakib + Limu, paired).
- [`03_AUTHOR.md`](../benchmark/tasks/03_AUTHOR.md) - verify the 24 drafts (Yousuf).
- [`04_AGENT_PILOT.md`](../benchmark/tasks/04_AGENT_PILOT.md) - copy-paste agent prompts; agents draft, humans decide every gold verdict (Atik, LAST).

**Current work (Nov 2026): verify the 24-item calibration first** — drafts at `benchmark/private/items/cal-001..024.json`, blind sheets at `benchmark/private/calibration/sheets/`, validator `benchmark/validate_items.py`, score command in `benchmark/status.json` under `next_command`. The 180-item freeze and 300-item target start only after the κ ≥ 0.75 / defect ≤ 15% / H ≤ 2.0 h gate passes. The 4/6-week plan in Section 10 is unchanged.

> **Note on Atik.** Atik runs the experiments, the Python pipeline, the GPU runs, the item drafting with AI agents, the analysis, and the manuscript integration. His work is not assigned in this guide. The tasks below are only the **human-judgment work that cannot be delegated to an agent** without changing the study. If a task can be automated, Atik or an agent does it; it is not listed here.

---

## 1. What this project is, in plain language

A multi-agent debate asks several language models the same scientific question, lets them read each other's answers for a few rounds, and then combines their final answers. The failure we study is **sycophantic collapse**: a correct minority agent abandons the right answer because a confident wrong majority pushes back.

TrustCal changes the combination rule. Instead of counting votes equally, it gives each agent a **trust weight** based on how well that agent's claims hold up against retrieved scientific evidence. An agent whose claims are supported by the evidence keeps influence; an agent whose claims are contradicted loses influence.

The project has two human-labeling gates. They are small in count but central to the thesis:

| Gate | What it tests | Why it matters |
| --- | --- | --- |
| **SciClaimBench 24-item calibration** | Can two humans apply the claim–evidence–verdict codebook with Cohen's κ ≥ 0.75, a defect rate ≤ 15%, and at most 2.0 hours per item? | It decides whether the team can build the 180-item gold-evidence benchmark without wasting ~410 hours. |
| **Verifier audit (180 SciFact pairs)** | Does the lexical verifier agree with human judgement at κ ≥ 0.60 and balanced accuracy ≥ 0.75? | The trust signal is only as good as the verifier. If the verifier is weak, the trust arm cannot be interpreted. |

Both gates are currently blocked on human work:

- SciClaimBench: **24 of 24 drafted, 0 human labels yet** — verification starts now.
- Verifier audit: **180 real pairs ready**, 0 human labels.

You are not being asked to run models, write code, build the literature review, or check the paper. You are being asked to read evidence carefully, apply a short codebook, and record a label with confidence and a note.

---

## 2. Who does what (5 members + Atik, hardest first)

Atik runs experiments, GPU, drafting agents, analysis, and manuscripts — and pilots the annotation agents LAST, after all human sheets are in. He is not assigned annotation work. The five members below do the human-judgment work only, hardest first: Rakib (with Limu) → Yousuf → Prottoy → Salman → Limu (with Rakib).

| Member | Role | The human work only you can do | Main deliverables |
| --- | --- | --- | --- |
| **Rakib + Limu (pair)** | **Adjudicators** | Settle every disagreement, run defect review, sign licence check | Adjudicated workbooks, defect log |
| **Yousuf** | **Item verifier** | Check all 24 drafts against the codebook | 24 checklists + problem list |
| **Prottoy** | **Rater 1** | Label all 216 SciClaimBench claims + all 180 verifier pairs | Two completed rater sheets |
| **Salman** | **Rater 2** | Same sheets, independently (never peek at rater 1) | Two completed rater sheets (own copies) |
| **Atik** | **Agent pilot, LAST** | Drafting helpers, sheet builds, validation runs, scoring | Score JSON, verification logs |

### Who rates what

| Audit | Raters | Adjudicator | Independent review |
| --- | --- | --- | --- |
| SciClaimBench 24-item | Prottoy, Salman | Rakib + Limu | Yousuf verifies all 24 against the codebook (he rates nothing) |
| Verifier audit 180 | Prottoy, Salman | Rakib + Limu | Atik checks sheet integrity and blinding |

### Workload

| Member | Total | 6-week pace | 4-week pace |
| --- | ---: | ---: | ---: |
| Yousuf | 12–16 h | 2–3 h/week | 3–4 h/week |
| Prottoy | 11–13 h | 2–2.5 h/week | 3–3.5 h/week |
| Salman | 11–13 h | 2–2.5 h/week | 3–3.5 h/week |
| Rakib + Limu (pair) | 8–11 h shared | 1.5–2 h/week each | 2–3 h/week each |
| Atik (agents, last) | 2–4 h | at the end | at the end |

These are planning estimates, not ledger numbers. Atik's agent piloting and experiment time are separate (he works last).

**No member is assigned paper support, number checking, citation checking, literature search, code, or experiments.** Atik covers those with agents. The only exception is a privacy/licence sign-off for Rakib + Limu, because private data and licences require named human owners.

---

## 3. Before you start

### Read these documents first

| Order | File | Why |
| ---: | --- | --- |
| 1 | [`README.md`](../README.md) | Project status, claim boundary, repository map |
| 2 | [`FYDP_Report/fydp.pdf`](../FYDP_Report/fydp.pdf) | The full report; read the abstract, Chapter 3, and Chapter 4 |
| 3 | [`PRE_REGISTRATION.md`](../PRE_REGISTRATION.md) | Endpoints, hypotheses, exclusions, stopping rules |
| 4 | [`benchmark/README.md`](../benchmark/README.md) | SciClaimBench protocol, κ/defect/effort gates, 24 → 180 → 300 ladder |
| 5 | [`benchmark/schema.md`](../benchmark/schema.md) | Item, position, claim, evidence, and verdict fields |
| 6 | [`experiments/verifier_audit/README.md`](../experiments/verifier_audit/README.md) | 180-pair audit, blind sheets, κ and balanced accuracy |
| 7 | [`docs/GLOSSARY.md`](GLOSSARY.md) | Terms and metric names |
| 8 | This guide | Your role, examples, deadlines, and submission rules |

You do **not** need to read the full literature review, the entire 75-page report, or the Python code. If you already know your role from `benchmark/README.md`, read your ONE role pack first and use the eight documents above as reference only. If a term is missing, check the glossary before asking.

### Direct links

Use these links directly. Do not search the repository for the files.

| Resource | Link |
| --- | --- |
| Repository | <https://github.com/Atik203/trustcal> |
| Project README | <https://github.com/Atik203/trustcal/blob/main/README.md> |
| Full report PDF | <https://github.com/Atik203/trustcal/blob/main/FYDP_Report/fydp.pdf> |
| Journal PDF | <https://github.com/Atik203/trustcal/blob/main/Journal_Paper/cas-sc-template.pdf> |
| Pre-registration | <https://github.com/Atik203/trustcal/blob/main/PRE_REGISTRATION.md> |
| Roadmap and gates | <https://github.com/Atik203/trustcal/blob/main/roadmap.md> |
| SciClaimBench protocol | <https://github.com/Atik203/trustcal/blob/main/benchmark/README.md> |
| SciClaimBench schema | <https://github.com/Atik203/trustcal/blob/main/benchmark/schema.md> |
| SciClaimBench validator | <https://github.com/Atik203/trustcal/blob/main/benchmark/validate_items.py> |
| SciClaimBench sheet templates | <https://github.com/Atik203/trustcal/tree/main/benchmark/annotation> |
| Verifier audit protocol | <https://github.com/Atik203/trustcal/blob/main/experiments/verifier_audit/README.md> |
| Verifier audit builder | <https://github.com/Atik203/trustcal/blob/main/experiments/verifier_audit/build_audit.py> |
| Verifier audit master template | <https://github.com/Atik203/trustcal/blob/main/experiments/verifier_audit/audit_sheet.template.csv> |
| Member templates | <https://github.com/Atik203/trustcal/tree/main/benchmark/templates> |
| Glossary | <https://github.com/Atik203/trustcal/blob/main/docs/GLOSSARY.md> |
| Claims audit (report) | <https://github.com/Atik203/trustcal/blob/main/FYDP_Report/CLAIMS_AUDIT.md> |
| Defence Q&A | <https://github.com/Atik203/trustcal/blob/main/docs/FYDP1_defence_Q&A.md> |
| Compute and cost model | <https://github.com/Atik203/trustcal/blob/main/docs/agent/08_COMPUTE_COST.md> |
| Private annotation folder | Atik posts the link in the team channel before Day 1. It is not in this public repository. |

### How to use these links

1. Click the link and read it in the browser.
2. For a CSV, click **Raw** or **Download**, then save a copy in the private folder.
3. Do not click **Fork**, **Pull request**, or **Commit** unless Atik asks.
4. If a link is broken, tell Atik in the team channel. Do not search for a replacement alone; the wrong version of a protocol is worse than a delay.
5. Do not paste private sheets, raw SciFact text, or model outputs into a public issue or an external AI tool.

### Access checklist

- [ ] GitHub account (the repository is public, so read access is enough).
- [ ] Access to the shared private folder for annotation sheets. Atik will post the link.
- [ ] Google Sheets or Excel, and a PDF reader.
- [ ] The team communication channel and the weekly meeting invite.
- [ ] Agreement not to copy private data, PII, or model outputs into public tools.
- [ ] Roughly **2–4 hours per week** for five weeks, or **4–5 hours per week** for the compressed four-week plan.

### Day 1–2 onboarding

| Day | Task | Output |
| ---: | --- | --- |
| 1 | Read the eight documents above; complete the access checklist | Notes and questions |
| 2 | 30-minute walkthrough; label the practice rows in Sections 9.3 and 9.4; compare labels | Practice notes and calibration discussion |

Do not start a real batch until the practice rows are discussed. The first batch is for calibration, not for the final data.

---

## 4. Rakib + Limu — adjudicators (pair)

**Role:** paired adjudicators for both audits — you settle every disagreement and run defect review. Hardest judgment call on the team.

**Pack:** [`02_ADJUDICATOR.md`](../benchmark/tasks/02_ADJUDICATOR.md) — exact columns, defect taxonomy, done-criteria. This section is only a pointer.

**Only you two do:**

1. Adjudicate every disagreement (SciClaimBench `adjudication.csv`, verifier `audit_sheet.csv`): copy agreement rows verbatim, decide disagreements from the codebook with a one-line rationale each.
2. Run defect review on the frozen triples: fill `defect_flag` + `defect_type`. Pre-freeze corrections are rework, not defects.
3. Sign the privacy/licence check (named human owners): private-folder handling, SciFact CC BY-NC terms, no gated text, no PII.
4. Open the adjudication workbook only after BOTH rater sheets are submitted.

**Time:** **8–11 h shared** (adjudication 5–7 h + defect review 3–4 h; licence sign-off inside that envelope).

**What not to do:**

- Never open the gold verdict or verifier label while adjudicating.
- Never relabel an agreement row to raise κ; never delete an unresolved row — mark `unresolved` and report it (over 5% blocks the freeze).
- Never change the codebook unilaterally; never label rater rows yourselves.

---

## 5. Yousuf — sole verifier of all 24 drafts

**Role:** the only person who checks the 24 calibration drafts against the codebook — verification confers gold.

**Pack:** [`03_AUTHOR.md`](../benchmark/tasks/03_AUTHOR.md); one [`item_verification_checklist.md`](../benchmark/templates/item_verification_checklist.md) per item.

**Only you do:**

1. Verify all 24 drafts (`benchmark/private/items/cal-001..024`): answerable question, 3 positions × 3–6 atomic claims, every claim with cited evidence + resolvable locator, contradict-first verdict order, complete licence block, no gated text.
2. File one checklist per item plus a written problem list. Never edit the item source — Atik fixes, you re-check.
3. Stay off the rater sheets entirely: you rate nothing, so your verification cannot leak into κ.

**Time:** **12–16 h** (about 30–40 min per item).

**What not to do:**

- Never label a rater or adjudication row; never peek at blind sheets.
- Never invent a passage, DOI, or verdict to fill a slot; never use an LLM to generate a verdict.

---

## 6. Prottoy — rater 1

**Role:** independent rater 1 for both audits — your sheet plus Salman's is the κ gate.

**Pack:** [`01_RATER.md`](../benchmark/tasks/01_RATER.md); sign [`annotation_submission_checklist.md`](../benchmark/templates/annotation_submission_checklist.md) for each sheet.

**Only you do:**

1. Label all 216 SciClaimBench rows (`support` / `contradict` / `neutral`) in your blind `rater1.csv` — claim + cited passages only.
2. Label all 180 verifier pairs (`supported` / `contradicted` / `unverifiable`) in your verifier `rater1.csv`.
3. Log effort per item (`effort.csv`, phase `rater1`); submit a copy as `rater1_<initials>.csv` and post filename + row count.

**Time:** **11–13 h** (SciClaimBench 5–7 h + verifier 5–6 h).

**What not to do:**

- Never open `benchmark/private/items/` (gold answers live there), Salman's sheet, or any gold/verifier label.
- Never discuss rows with Salman before both sheets are in; never use an LLM for labels; never use outside knowledge.

---

## 7. Salman — rater 2

**Role:** independent rater 2 for both audits — same sheets as Prottoy, labelled independently. Never peek at his.

**Pack:** [`01_RATER.md`](../benchmark/tasks/01_RATER.md); sign [`annotation_submission_checklist.md`](../benchmark/templates/annotation_submission_checklist.md) for each sheet.

**Only you do:**

1. Label all 216 SciClaimBench rows (`support` / `contradict` / `neutral`) in your blind `rater2.csv` — claim + cited passages only.
2. Label all 180 verifier pairs (`supported` / `contradicted` / `unverifiable`) in your verifier `rater2.csv`.
3. Log effort per item (`effort.csv`, phase `rater2`); submit a copy as `rater2_<initials>.csv` and post filename + row count.

**Time:** **11–13 h** (SciClaimBench 5–7 h + verifier 5–6 h).

**What not to do:**

- Never open `benchmark/private/items/` (gold answers live there), Prottoy's sheet, or any gold/verifier label.
- Never discuss rows with Prottoy before both sheets are in; never use an LLM for labels; never use outside knowledge.

---

## 8. Atik — agent pilot + scoring, LAST

**Role:** runs the experiments, the Python pipeline, the GPU runs, the analysis, and the manuscript integration — and pilots annotation agents only after all human sheets are in.

**Pack:** [`04_AGENT_PILOT.md`](../benchmark/tasks/04_AGENT_PILOT.md) — copy-paste prompts for mechanical work only.

**Only he does, after every human sheet is submitted:**

1. Blind-sheet builds, validator runs, and results assembly.
2. The score command from `benchmark/status.json` (`next_command`); posts κ / defect / `H_attempt` / unresolved + exit code.
3. Item-source fixes from Yousuf's and the adjudicators' problem lists; regenerates sheets if claim text changes.

**Time:** agent piloting happens at the end (experiment, GPU, and manuscript time is separate and not bounded here).

**Rule for everyone:** no agent output becomes a verdict or label without a named human checking it. Agents never adjudicate and never set gold.

---

## 9. Shared rules and examples

### 9.1 The two label sets are different

| Audit | Labels |
| --- | --- |
| SciClaimBench | `support`, `contradict`, `neutral` |
| Verifier audit | `supported`, `contradicted`, `unverifiable` |

Do not mix them. The wording is different on purpose.

### 9.2 SciClaimBench decision order

1. If any cited passage contradicts the claim as written, use `contradict`.
2. Otherwise, if at least one cited passage entails the claim, use `support`.
3. Otherwise, use `neutral`.

### 9.3 SciClaimBench practice rows

| # | Claim | Passage | Correct label | Why |
| ---: | --- | --- | --- | --- |
| 1 | Drug X reduced systolic blood pressure by 12 mmHg versus placebo. | In the trial, systolic blood pressure fell 12 mmHg in the Drug X arm and 1 mmHg in the placebo arm. | `support` | The passage states the relation and the number. |
| 2 | Drug X reduced systolic blood pressure by 12 mmHg versus placebo. | There was no significant difference in systolic blood pressure between Drug X and placebo. | `contradict` | The passage denies the claimed effect. |
| 3 | Drug X reduced systolic blood pressure by 12 mmHg versus placebo. | The trial enrolled 120 adults with treated hypertension. | `neutral` | The passage is on-topic but does not state the effect. |
| 4 | Drug X reduced systolic blood pressure and increased heart rate. | Drug X reduced systolic blood pressure by 12 mmHg; heart rate was not reported. | `neutral` | Only one part of the compound claim is supported. |
| 5 | The reaction released 100 °C of heat. | The reaction reached 212 °F. | `support` | The numbers agree after unit conversion. |

### 9.4 Verifier audit practice rows

| # | Claim | Passages | Correct label | Why |
| ---: | --- | --- | --- | --- |
| 1 | Drug X lowers systolic blood pressure. | In the trial, systolic blood pressure fell 12 mmHg on Drug X versus 1 mmHg on placebo. | `supported` | The passage states the claimed relation. |
| 2 | Drug X lowers systolic blood pressure. | There was no significant difference in systolic blood pressure between Drug X and placebo. | `contradicted` | The passage denies the relation. |
| 3 | Drug X lowers systolic blood pressure. | The trial enrolled 120 adults with treated hypertension. | `unverifiable` | The passage is on-topic but does not state the relation. |
| 4 | Drug X lowers systolic blood pressure. | *(empty passage)* | `unverifiable` | Empty evidence never supports a claim. |
| 5 | Drug X lowers systolic blood pressure. | Drug X is a small molecule with a molecular weight of 412 Da. | `unverifiable` | Topical overlap is not support. |

### 9.5 Blinding

- Do not discuss individual rows with the other rater before both sheets are submitted.
- Do not open the other rater's sheet, the gold verdict, the verifier label, or the arm map.
- If you recognize an item from another batch, tell Atik before labeling it.
- The adjudicator may see both sheets, but not the gold or verifier label.

### 9.6 Human labels only

- Do not use an LLM to generate labels, annotations, or citations.
- Items carry no AI markings: do NOT set `draft_assisted` (deprecated 21 Nov 2026, see `benchmark/schema.md`). Provenance lives only in batch manifests; gold = verified + adjudicated, nothing else.
- Atik may use an LLM to draft SciClaimBench item text, but a human (Yousuf) must verify every claim, evidence link, and gold verdict before it counts.
- Do not paste private data or model outputs into an external AI tool.

### 9.7 Files and submission

- Do not edit the original batch. Save a copy with your initials.
- Fill every row. Do not add or delete columns.
- Use the exact label strings. A blank cell is not a label.
- Put a short note on every hard row; a low-confidence label with a clear note is better than a silent guess.
- Upload to the private folder and post the filename and row count in the team channel.
- Atik copies the per-person sheets to the canonical names before scoring.

### 9.8 When to ask

Ask Atik for batch, blinding, submission, or protocol questions that cannot wait. Ask Rakib + Limu for adjudication questions. A question is cheaper than a bad label.

---

## 10. Timeline

### Recommended: 6 weeks

The six-week plan has five active weeks and one buffer week. The verifier audit starts immediately because the 180 pairs are built. The SciClaimBench track waits for Atik's drafts.

| Week | Yousuf (verifier) | Prottoy (rater 1) | Salman (rater 2) | Rakib + Limu (adjudicators) |
| --- | --- | --- | --- | --- |
| **1** | Read docs; verification starts | Onboarding; verifier labels start | Onboarding; verifier labels start | Onboarding; set up adjudication log |
| **2** | Verification finishes; problem list to Atik | Verifier labels finish; SciClaimBench labels start | Verifier labels finish; SciClaimBench labels start | Prepare adjudication workbook |
| **3** | Rechecks after Atik's fixes | SciClaimBench labels | SciClaimBench labels | Verifier adjudication |
| **4** | Final checks | SciClaimBench labels finish | SciClaimBench labels finish | SciClaimBench adjudication; defect review starts |
| **5** | Final checks | Final checks | Final checks | Defect review finish; privacy/licence check |
| **6** | Buffer | Buffer | Buffer | Buffer |

Atik's deliverables are dependencies, not rows in this table: draft items by Day 5, blind sheets by end of Week 2, score output after both sheets are complete.

### Compressed: 4 weeks

Only choose this if **all** of the following are true:

- Atik delivers the 24 draft items by **Day 5**.
- Every member can commit **4–5 hours per week**.
- The verifier audit starts in Week 1, in parallel with item verification.
- No one travels or has an exam during the four weeks.
- The team accepts that a κ failure leaves no buffer for a fresh batch.

| Week | Focus |
| --- | --- |
| **1** | Onboarding, practice, verifier labels start, SciClaimBench items frozen by Day 5 |
| **2** | Verifier labels finish and adjudicate; SciClaimBench sheets generated and labeling starts |
| **3** | SciClaimBench labeling finishes; adjudication; defect review starts |
| **4** | Defect review, score, privacy/licence check, sign-off |

**Recommendation:** set the member deadline at **6 weeks from kickoff**, with internal checkpoints at the end of Weeks 2, 3, and 4. A 4-week deadline is feasible for the annotation work alone, but it is fragile because the SciClaimBench items are not authored yet. The critical path is **item drafting → verification → blind sheets → labels → adjudication**, not the 180-pair verifier audit.

---

## 11. Definition of done

| Member | Done when |
| --- | --- |
| Yousuf | 24 item verification checklists + problem list delivered |
| Prottoy | SciClaimBench rater 1 sheet + verifier rater 1 sheet complete; submission checklists signed |
| Salman | SciClaimBench rater 2 sheet + verifier rater 2 sheet complete; submission checklists signed |
| Rakib + Limu | Both adjudication workbooks complete; unresolved rows listed; defect log + privacy/licence checklist signed |
| Atik (LAST) | Blind sheets built; score JSON posted — only after every human sheet is in |

A failed κ or balanced-accuracy gate is a **finding**, not a failure of the team. Keep the batch, report the number, revise the codebook, and run a fresh batch. Do not relabel the same rows to make the number pass.

---

## 12. Glossary

| Term | Meaning |
| --- | --- |
| **Sycophantic collapse** | A correct minority agent abandons its answer under pressure from a confident wrong majority. |
| **Trust weight** | The bounded influence assigned to an agent from evidence-grounded claim support. |
| **Claim–evidence–verdict triple** | One atomic claim, the cited passages, and the gold verdict. |
| **Support** | A passage entails the claim as written and no passage refutes it. |
| **Contradict** | A passage asserts the claim is false. |
| **Neutral / unverifiable** | The passages do not establish or refute the claim. |
| **SciClaimBench** | The team-built gold-evidence benchmark; 24-item calibration, 180-item freeze, 300-item target. |
| **Verifier audit** | The 180-pair SciFact audit of the lexical verifier against human labels. |
| **Cohen's κ** | Chance-corrected agreement between two raters. |
| **Balanced accuracy** | Mean per-class recall; used because the three classes are balanced. |
| **`H_attempt`** | Annotation hours divided by attempted items; the 24-item gate cap is 2.0 h/item. |
| **Pressure-eligible** | An item where a correct minority can be pressured by a wrong majority. |
| **B8** | The trust-weighted debate arm; `B8-no-trust` is its majority-vote control. |
| **Private folder** | The shared, non-public location for filled items, evidence, labels, and adjudication. |
| **Blind sheet** | A rater sheet with no gold, verifier, or arm label. |

---

## 13. Ready-to-send message

> We are finishing the human-labeling part of the TrustCal FYDP. Atik handles the experiments, code, item drafting, analysis, and paper integration with agents. Your work is only the human-judgment part: verifying the 24 SciClaimBench calibration items, labeling claims against evidence, auditing the verifier, and adjudicating disagreements.
>
> Please read `docs/MEMBER_GUIDE.md` and the eight documents in Section 3 before our first meeting. You do not need to know the domain in advance. We will do a short practice batch together. The recommended sprint is six weeks, with a four-week compressed option if the draft items are ready by Day 5.
>
> Guide: https://github.com/Atik203/trustcal/blob/main/docs/MEMBER_GUIDE.md
> Templates: https://github.com/Atik203/trustcal/tree/main/benchmark/templates
>
> Rakib + Limu: adjudicators — settle every disagreement, defect review, licence sign-off (both audits).
> Yousuf: sole verifier of all 24 calibration drafts.
> Prottoy: rater 1 — 216 SciClaimBench rows + 180 verifier rows.
> Salman: rater 2 — same sheets, independently.
> Atik: agent pilot + scoring, LAST after all sheets are in.

---

## 14. All links in one place

| What | Where |
| --- | --- |
| Repository | <https://github.com/Atik203/trustcal> |
| README | <https://github.com/Atik203/trustcal/blob/main/README.md> |
| Report PDF | <https://github.com/Atik203/trustcal/blob/main/FYDP_Report/fydp.pdf> |
| Journal PDF | <https://github.com/Atik203/trustcal/blob/main/Journal_Paper/cas-sc-template.pdf> |
| Pre-registration | <https://github.com/Atik203/trustcal/blob/main/PRE_REGISTRATION.md> |
| Roadmap | <https://github.com/Atik203/trustcal/blob/main/roadmap.md> |
| SciClaimBench protocol | <https://github.com/Atik203/trustcal/blob/main/benchmark/README.md> |
| SciClaimBench schema | <https://github.com/Atik203/trustcal/blob/main/benchmark/schema.md> |
| SciClaimBench validator | <https://github.com/Atik203/trustcal/blob/main/benchmark/validate_items.py> |
| SciClaimBench templates | <https://github.com/Atik203/trustcal/tree/main/benchmark/annotation> |
| Verifier protocol | <https://github.com/Atik203/trustcal/blob/main/experiments/verifier_audit/README.md> |
| Verifier builder | <https://github.com/Atik203/trustcal/blob/main/experiments/verifier_audit/build_audit.py> |
| Verifier master template | <https://github.com/Atik203/trustcal/blob/main/experiments/verifier_audit/audit_sheet.template.csv> |
| Member templates | <https://github.com/Atik203/trustcal/tree/main/benchmark/templates> |
| Glossary | <https://github.com/Atik203/trustcal/blob/main/docs/GLOSSARY.md> |
| Report claims audit | <https://github.com/Atik203/trustcal/blob/main/FYDP_Report/CLAIMS_AUDIT.md> |
| Defence Q&A | <https://github.com/Atik203/trustcal/blob/main/docs/FYDP1_defence_Q&A.md> |
| Compute and cost model | <https://github.com/Atik203/trustcal/blob/main/docs/agent/08_COMPUTE_COST.md> |

# IDEA 1 — RESEARCH MASTER BLUEPRINT

**Trust-Calibrated Multi-Agent Scientific Deliberation** — a bounded, evidence-grounded trust score that re-weights each agent's influence during a multi-agent debate, so a correct minority is not talked out of its answer by a confidently wrong majority.

**Paper title:** *The Boundaries of Evidence-Grounded Trust in Multi-Agent Scientific Debate, with a Controlled Benchmark for Sycophantic Consensus.*

> [!NOTE]
> **Scope.** This is the design record: problem, mechanism, arms, trust math, evaluation plan, threats to validity. The plan of record is [`docs/agent/03_EXPERIMENT_PLAN.md`](agent/03_EXPERIMENT_PLAN.md); gates and dates are in [`roadmap.md`](../roadmap.md); compute workings are in [`docs/agent/08_COMPUTE_COST.md`](agent/08_COMPUTE_COST.md); component status is in [`trustcal/IMPLEMENTATION_STATUS.md`](../trustcal/IMPLEMENTATION_STATUS.md). Where they disagree with this file, they win.
>
> **Design history.** P0 superseded two parts of the original design: the trust operator is logit accumulation → one softmax → floor/ceiling simplex projection (not clamp-then-renormalise), and retrieval routes by claim domain, not by agent identity. P0 (2026-11-09) is engineering readiness, not efficacy evidence.

> [!IMPORTANT]
> **Current evidence.** The only efficacy data so far is a 798-debate B8 comparison: **62.41% vs 58.65%**, McNemar **p = 0.086** (not significant). Every other number below is a projection until the Core run.

**Contents.** §0 design decisions · §1 summary · §2 motivation · §3 problem and hypotheses · §4 system overview · §5 pipeline · §6 data flow · §7 models and tools · §8 datasets · §9 evaluation · §10 edge cases · §11 risks · §12 roadmap pointer · §13 build order · §14 supervisor pitch · §15 beginner walkthrough · §16 expected outcome · §17 extensions · §18 critical review.

---

### Section 0 — Research Design Decisions & Assumptions

**Why this problem.** Multi-agent debate (MAD) is widely used to improve LLM reasoning, but agents abandon correct answers under social pressure from a confident wrong majority. In scientific QA a confidently wrong consensus is worse than an honest "uncertain", and the failure is silent — it looks like agreement.

**Why current solutions are insufficient.** Diagnosis exists (Yao et al., preprint), post-hoc correction exists (Minority Sentinel, workshop), efficiency gating exists (iMAD, AAAI 2026), static aggregation exists (MoA, ICLR 2025). None re-weights agent trust *during* a debate from external evidence.

**Why multi-agent rather than one stronger model.** A single model has no adversarial critique. Debate supplies it — but only if aggregation is not majority vote, because majority vote is the mechanism that produces sycophantic collapse.

**Core assumptions, by risk:**

1. Debate claims decompose into checkable atomic propositions (moderate risk).
2. PubMed/arXiv/Semantic Scholar retrieval can support or contradict a claim inside the debate's time budget (moderate risk).
3. **Trust weights behaviourally change the final answer, not just the context (highest risk — Challenge C).** The mechanism lives or dies here, so the pilot tests it before any Core spend.
4. Heterogeneous families reduce, but do not remove, correlated hallucination (named limitation, not assumed away).

**Rejected alternatives.** Post-hoc classifier (does not intervene in-loop) · fine-tuning agents to be less sycophantic (compute cost, poor cross-family transfer, conflates sycophancy with grounding) · confidence-only re-weighting (self-reported confidence comes from the same context the injected pressure manipulates). The chosen design is the only candidate that ties influence to something external to the debate's social dynamics — the causal lever needed to break collapse, not merely detect it.

---

### Section 1 — Executive Summary (for a new team member, zero AI background)

Three AI "reviewers" answer a hard science question. Normally, two who agree outvote the third — and two confident-but-wrong reviewers can talk a correct third out of its answer. Our fix: after each round, every reviewer's claims are fact-checked against retrieved scientific papers; reviewers whose claims hold up gain say, reviewers whose claims are contradicted lose say, even if they are the majority. The final answer is an evidence-weighted vote, not a headcount. We also build a controlled way to inject fake "expert consensus" pressure, so we can measure whether the system resists it better than existing approaches.

---

### Section 2 — Research Motivation

Sycophancy is cited as an open problem in 50+ peer-reviewed papers since 2023. In multi-agent systems it undermines the reason debate is used at all: if the answer collapses to whichever position sounds most confident, the extra agents add cost without reliability.

**Verified state of the literature (mid-2026):**

- **Diagnosis only** — Yao et al. (unpublished preprint, submitted to ICLR 2026 and withdrawn) defines and measures collapse; He et al. 2026 quantifies it (correct minority in ~1/4 of disagreements).
- **Closest published mitigation: ConsensAgent** (Pitre, Ramakrishnan & Wang, Findings of ACL 2025, pp. 22112–22133) — reduces sycophancy by static/dynamic prompt refinement. Textual intervention, no numeric trust, no external retrieval, no adversarial injection.
- **Closest mechanism: DebUnc** (Yoffe, Amayuelas & Wang, Findings of EMNLP 2025, pp. 23299–23315) — re-weights in-loop influence from *internal*, self-reported uncertainty (token entropy / TokenSAR). Its own diagnostic "Ground Truth" oracle, which weights agents by actual correctness, beats every deployable metric (up to +10% average accuracy) but cannot be deployed. Our score is the deployable instantiation of that oracle.
- **Theory** — Estornell & Liu (NeurIPS 2024) prove majority-convergence ("tyranny of the majority") and propose pruning interventions, but build no evidence-grounded system.
- **Also positioned against** — MoA (ICLR 2025 Poster, static aggregation), iMAD (AAAI 2026 Oral, decides *whether* to debate), Minority Sentinel (AgentSearch @ SIGIR 2026, post-hoc).

**Gap, one sentence.** No framework re-weights agent influence *within* an active debate from real-time verifiability of its claims against external evidence, with a formally bounded numeric trust score. Prompt refinement, self-reported uncertainty and theoretical pruning each address an adjacent problem; none ties influence to evidence verification.

**Contributions.** C1: the trust-calibrated, evidence-grounded aggregation mechanism. C2: an open, reproducible sycophancy-stress harness (injection protocol + accuracy/CMR/trust-calibration metrics) that is reusable without adopting C1. State novelty as the *mechanism* — external, numeric, formally bounded, injection-tested — never as "first to mitigate sycophancy".

---

### Section 3 — Problem Statement

**Problem.** In multi-agent LLM debate, a confidently wrong majority can make a correct minority abandon its position with no new evidence presented, and majority-vote aggregation then locks in the wrong answer. No existing mechanism ties an agent's influence to whether its claims are supported by evidence, rather than to how confidently they were stated.

**Hypothesis (H1).** If agent influence is re-weighted during debate by external evidence verification, sycophantic collapse decreases relative to standard majority-vote debate, without fine-tuning.

**Secondary hypotheses.** H2: trust scores rank agents by correctness (AUROC above chance, Brier below the constant 1/3 predictor). H3: gains are largest on pressure-eligible items and near zero on easy, agreed questions.

**Objectives.** (1) specify a bounded trust-update mechanism; (2) build a reproducible injection protocol that induces collapse under control; (3) estimate the effect across **B3, B4-matched, B8-no-trust and B8**, with **B8-placebo** and **B8-oracle** added under WP-18; (4) establish early that trust re-weighting causally changes output, not just context.

---

### Section 4 — Complete System Overview

```
Question
  → confidence gate ── confident ──→ direct answer → output
  → [uncertain] Round 0: three heterogeneous agents answer independently
  → claim decomposition: each answer → atomic, tagged propositions
  → claim-domain retrieval: bio/clinical → PubMed + S2; physics/chem, math/CS → arXiv + S2
  → evidence scoring: cross-encoder rerank → supported / contradicted / unverifiable / contested
  → trust update: logit accumulation → one softmax → floor/ceiling simplex projection
  → [stress runs only: fabricated expert consensus injected between rounds 1 and 2]
  → revision: agents see peer outputs, evidence and own trust standing
  → repeat retrieval → trust → revision to K = 3
  → trust-weighted aggregation: argmax over Σ(Tᵢ × positionᵢ), not majority vote
  → output: answer, evidence citations, trust trajectory, per-agent reasoning
```

**Why each stage exists.** The gate avoids paying for debate on easy items; independent Round 0 gives the baseline needed to show that a position *changed*; claim-level tags make per-claim scoring possible; domain routing keeps the evidence signal independent of speaker identity; the weighted argmax is what lets a correct, evidence-backed minority outvote two unsupported agents.

> [!IMPORTANT]
> **Frozen design invariants.** Logit accumulation → one softmax → floor/ceiling simplex projection · K = 3 rounds · N = 3 heterogeneous agents · claim-domain routed retrieval · inference only, no fine-tuning.

---

### Section 5 — Detailed Multi-Agent Pipeline

#### Agent 0 — Confidence Estimator (gatekeeper, not a debate participant)

Single-pass gate: self-reported confidence, or agreement across three quick independent answers. Output is debate / no-debate plus the direct answer if no-debate. It trades compute, not correctness — a false "easy" only limits coverage, and evaluation sets are pre-filtered to divergent cases anyway. If the gate proves unreliable, run debate on everything (~9 forward passes instead of ~1 on easy questions).

#### Agents 1–3 — Debate Agents

Three model families, inference only, identical pipeline regardless of which checkpoints occupy the slots:

- **Agent 1** — Qwen3.8-27B, 4-bit AWQ-INT4 (~21.0 GB)
- **Agent 2** — Gemma-4-26B-A4B, 4-bit AWQ (~17.2 GB)
- **Agent 3** — Mistral-24B, AWQ (15.06 GB)

Per round an agent receives the question, its own prior answer, evidence for its own claims, peer positions (post-injection where applicable) and its own current trust value. It returns a position, a reasoning trace and tagged atomic claims (`<claim id="c1">…</claim>`), which is what makes claim-level scoring possible. Agents never see each other's prompts, only peer *outputs*, preventing cross-family prompt leakage. N = 3 is primary because it is the minimum that creates a genuine 1-vs-2 minority, which is the phenomenon under test.

#### Retrieval and verifier (shared infrastructure, not an agent)

- **Route by claim domain, not by agent:** bio/clinical → PubMed + Semantic Scholar; physics/chem and math/CS → arXiv + Semantic Scholar; Semantic Scholar/OpenAlex is the shared fallback. An agent cannot win by owning an easier slice of the literature.
- **Verifier:** cross-encoder rerank (ms-marco-MiniLM) plus a citation-count floor (>10) and domain-restricted abstracts, then classify each claim as supported, contradicted, unverifiable or contested. A judgment claim normally returns unverifiable and is excluded — trust only moves on checkable claims.
- **Sparse evidence:** broaden the query first, then mark the claim abstained; abstention neither rewards nor penalises. Results are stratified by retrieval-success rate, so sparsity becomes a measured boundary rather than a hidden bias.
- **Rate limits:** disk cache of prior retrievals, retry with exponential backoff, OpenAlex fallback.

#### Trust update

Each round, an agent's claim verdicts accumulate into one logit: supported claims add, contradicted claims subtract, abstentions contribute nothing; the sum is normalised by claim count so a verbose agent gains nothing by volume. One softmax over the three accumulated logits produces weights, then a floor/ceiling simplex projection clamps them into [0.1, 0.9] while preserving Σ Sᵢ = 1.

- α (support) and β (contradiction) are the only free parameters; defaults 0.5 / 0.3 with a planned sensitivity sweep over the grid.
- The operator order is fixed. Clamp-then-renormalise was the original design and is forbidden: renormalisation pushed weights back below the floor (P0-5, `trust/update.py`). Unit-test the trust function in isolation before wiring it into the loop.
- Boundedness (Proposition 1) is verified computationally on thousands of synthetic score sequences — min ≥ floor, sum = 1, max ≤ effective ceiling — before it is trusted inside the larger system. Propositions 2–3 are design properties about trust trajectory behaviour, not global convergence theorems.

#### Orchestrator

Plain-Python state machine: round sequencing, injection at t = 1→2, trust updates, final aggregation, a K = 3 cap and a per-agent retry cap of 3. The LangGraph port is not implemented, and the B9 iMAD baseline is an approximation rather than a faithful port.

---

### Section 6 — Complete Data Flow

The §4 flow is the data flow. Three intermediates must be logged because the evaluation consumes them: per-round `{agent_id, answer, reasoning_trace, trust}`, which is the trajectory that checks Propositions 2–3 empirically; per-claim `{evidence_verdict, passage, relevance_score}`, which feeds trust calibration and the verifier audit; and the final `argmax Σ(Tᵢ × positionᵢ)` with citations. Ground truth is visible to the harness only, never to the agents.

---

### Section 7 — Models & Tools

| Role | Model | Notes |
| --- | --- | --- |
| Agent 1 | Qwen3.8-27B AWQ-INT4 | dense 27B, 262K context, Apache 2.0, ~21.0 GB |
| Agent 2 | Gemma-4-26B-A4B AWQ | MoE, 3.8B active, 256K context; all params resident, ~17.2 GB |
| Agent 3 | Mistral-24B AWQ | third family; FP8 variants enlarge the stack, so AWQ is pinned for the matrix, 15.06 GB |
| Reranker | ms-marco-MiniLM cross-encoder | fast and standard; upgrade to SciBERT if evidence quality demands |
| B7 ceiling | GPT-6 Luna, three calls per question | appendix-only external-answer reference; never in the Core or Full matrix, never given gold |

**Serving facts (measured 2026-11-24).** The 4-bit trio totals ~53.3 GB and runs on **one 96 GB on-demand card** at **$1.50/GPU-h all-in**. With **8 concurrent rows and CUDA graphs** the pipeline sustains **172.7 debates/h**, against 52.2/h for the old 2-way eager baseline.

**Budget.** Core + Full 12,000 debates = **$104.23**. Programme total 21,800 debates = **$191.92** against a **$220 cap**, leaving about **$20** of headroom. No paid run starts without approval, and the chosen offer and cost go in the run notes.

**Precision replication.** The FP8 variant (Qwen3.8-27B-FP8 29.95 GB, Gemma-4-26B-A4B-FP8 28.67 GB, Mistral-24B-AWQ 15.06 GB; 73.68 GB at 0.90 utilisation) runs on the same 96 GB class card as a 5-question smoke plus a small GPQA replication, after the 4-bit Core. It is not the matrix host, and the hardware smoke has not run — only the offline size check passes.

**Historical (2026-09, Phase 0/1).** P0 engineering ran on an RTX A6000 48 GB with a 9B/12B/14B dev trio at 4-bit (~28 GB). vLLM's W8A8 FP8 kernel failed on Ampere (`cutlass_scaled_mm_sm80_epilogue`), so the dev Ministral used an AWQ-4bit artefact of the same checkpoint. Dev behaviour, versions and costs: `experiments/gate0/README.md`.

**Build difficulty, easiest first.** vLLM multi-model serving → retrieval and reranking → claim decomposition and tagging → trust update and state machine (operator order is the risk) → B9 iMAD reimplementation (~10 working days, the highest single-component risk, because it reconstructs a method from a paper description).

---

### Section 8 — Dataset Plan

| Dataset | Role | Source | License / access | Known limitation |
| --- | --- | --- | --- | --- |
| **BrokenMath** | appendix adversarial stress | `INSAIT-Institute/BrokenMath`; arXiv:2510.04721 | CC BY-NC-SA 4.0 (non-commercial) | math-only; no evidence grounding |
| **BrokenArXiv** | appendix adversarial, monthly refresh | `MathArena/brokenarxiv`; arXiv:2605.00674 | CC BY-SA 4.0 | cite the exact snapshot used |
| **HLE** | hard scientific ceiling | `cais/hle`; Nature 649, 1139–1146 (2026) | MIT, click-through approval | approval lead time — apply in Phase 0 |
| **GPQA** | Core stable comparison (GPQA-Main) | `Idavidrein/gpqa`; COLM 2024 | CC BY 4.0, terms acceptance | not adversarial — accuracy comparability only |
| **MMLU-Pro** | Core stable comparison | `TIGER-Lab/MMLU-Pro`; NeurIPS 2024 D&B | MIT | same role as GPQA |

All five are official author releases from HuggingFace or the project site; none come from Kaggle. Licenses verified 2026-09-15. Preprocessing is the divergent-answer filter (≈60–70% retention); results on BrokenMath/BrokenArXiv are framed as adversarial worst-case behaviour, not average-case deployment.

**SciClaimBench ladder.** SciClaimBench is the team-built gold-evidence benchmark, not a Core v1.0 dataset. Core v1.0 runs GPQA-Main + MMLU-Pro + HLE. SciClaimBench freezes at **180 items** (v1.2: 60 biomed, 60 phys/chem, 60 math/CS) and scales to the **300-item Full target**; 600 is stretch (2–3 dedicated annotators), 800 is no-go. A 24-item calibration batch starts the ladder and is cut to 120 if `H_attempt > 2.0` or defect >15%.

**Unavailability fallbacks.** HLE denied or delayed → GPQA-Diamond subset under the same injection protocol (lower ceiling, same design). BrokenArXiv discontinued → freeze the last snapshot and document the cutoff. Semantic Scholar unusable → OpenAlex, pre-approved now rather than discovered mid-project.

---

### Section 9 — Evaluation Strategy

**Arms and design.** The Core matrix is exactly **B3, B4-matched, B8-no-trust and B8** × GPQA-Main + MMLU-Pro + HLE × 2 seeds = 24 runs. The Full target adds **B8-placebo** and **B8-oracle** (WP-18 conditional). B8-placebo is a cross-agent round-pool control; B8-oracle supplies gold-answer trust, or gold-evidence-only on SciClaimBench (32-row gold-evidence default). B1/B2/B5–B7/B9/B10 are comparison and appendix arms, not Core cells.

| Metric | Measures | Role |
| --- | --- | --- |
| **Accuracy** | correctness of the aggregated answer on pressure-eligible items | primary endpoint |
| **CMR** (Correct-Minority Retention) | whether a round-0 correct minority still holds gold at round K | co-primary mechanism endpoint |
| **ARR** | whether agents revise in the evidence-supported direction | secondary; separates revision from collapse |
| **Trust AUROC** | within-debate ranking of trust against correctness | secondary calibration (replaces ECR for ranking) |
| **Trust Brier** | squared error of trust against correctness | secondary calibration; penalises overconfidence |
| **CCR / MPR** | collapse rate and minority survival under injection | diagnostics and manipulation checks |
| **Human eval (Likert, κ)** | factual grounding and hallucination severity | automated metrics miss reasoning quality |

ECR is deprecated. **Ablations.** Four conditions isolate which component drives any gain: no trust calibration, no progressive retrieval, no claim-domain routing, no adaptive triggering. Without them the result is a black box, not a systems contribution. **Error analysis** uses the project failure taxonomy: correlated hallucination, evidence sparsity, trust collapse, adversarial 2-vs-1 consensus.

**Statistics.** 2 seeds, 95% CI, paired bootstrap, McNemar/Holm, Cohen's d. Single-run comparisons are a standing reviewer criticism of the MAD literature; this pre-empts it. Three seeds are deliberately not used — more questions at two seeds is the better trade (`PRE_REGISTRATION.md` §3). Additional runs: N-scaling at N ∈ {2,3,5} on a 100-question subset, and human evaluation on 150–200 paired items with 3 κ-validated raters.

---

### Section 10 — Edge Cases & Failure Handling

| Failure | Detection | Handling |
| --- | --- | --- |
| Retrieval returns no evidence | zero passages above threshold | broaden the query, then abstain (no reward/penalty); stratify results by retrieval-success rate |
| Contradictory evidence | conflicting verdicts at >0.75 relevance | flag "contested", report separately, annotate as its own human-eval category |
| All agents hallucinate alike | homogeneous-vs-heterogeneous comparison | partial mitigation only; reported as a scope boundary |
| Trust collapse toward the floor | trust variance across rounds | structurally prevented by the simplex floor; verified empirically, not assumed |
| Claim extraction fails | tag schema validation fails | fallback LLM extraction; if that also fails, exclude the turn from that round's update |
| API rate limit / downtime | HTTP errors, timeouts | cache, exponential backoff, OpenAlex fallback |
| Context overflow | token count before each round | K = 3 cap; truncate oldest round detail, keep the numeric trajectory |
| Inference timeout | request timeout | retry once, then mark the agent `INCONCLUSIVE` for that round and continue |

---

### Section 11 — Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Trust signal does not behaviourally change output (Challenge C) | medium | **critical** | pilot before Core — the whole point of the gate |
| Reviewers read this as incremental over MoA/iMAD | low-medium | moderate | B4-matched and B8-no-trust controls; headline is B8 vs B8-no-trust, not a CCR delta over iMAD |
| Novelty erosion after ConsensAgent (Findings of ACL 2025) | medium | moderate | sharpen the mechanism line: evidence-grounded, numeric, bounded, injection-tested; add B10 comparison |
| Propositions 2–3 fail empirically | medium | moderate | already framed as design properties, not theorems — honest framing absorbs the result |
| Retrieval noise degrades evidence quality | medium | moderate | reranker + citation floor + contested category |
| Compute ceiling under matrix × datasets × seeds | medium | moderate | 96 GB on-demand path at $1.50/GPU-h all-in; $104.23 Core+Full, $191.92 remaining, $220 cap |
| Timeline overload before the pilot | **high** | high | keep the gate order; WP-18 is the only pre-run design addition |

---

### Section 12 — Month-by-Month Roadmap

The calendar, gates G2–G5 and the pilot gate live in [`roadmap.md`](../roadmap.md) and are not duplicated here. The order is: 18 GB test gate → 4-bit 96 GB smoke → v1.3/WP-18 → 24-item calibration → verifier audit → pilot (G2) → Core (G3) → Full (G4/G5), with the FP8 smoke and precision replication only after the 4-bit Core.

---

### Section 13 — Implementation Order

Dependency reasoning only; dates and gates are in `roadmap.md`.

1. **vLLM serving** — nothing else is testable without it.
2. **Vanilla MAD reproduction (Du et al. 2023)** — Gate 0; validates the base loop so later bugs isolate to our additions.
3. **Injection protocol (§5.4)** — before trust math, because calibration is meaningless without a validated stress test.
4. **Pilot run** — the highest-risk assumption tested on 100–150 questions before Core money is spent.
5. **Claim decomposition + claim-domain retrieval** — the trust inputs are outputs of retrieval; mocked data cannot validate trust.
6. **Trust update function** — implement and unit-test the exact operator order in isolation, then integrate the debate loop once steps 1–5 are validated.
7. **Baselines** — B1–B4 first (they reuse steps 1 and 5), then B5–B6 in parallel with B9–B10, which come last because iMAD and ConsensAgent are the hardest components.
8. **Hardware readiness** — 18 GB test gate, then the 4-bit 96 GB smoke (`PHASE=fourbit`), then the FP8 smoke (`PHASE=final`) after the 4-bit Core. Check: claim tags parse, injection affects all three models, no NaNs in the trust math, K = 3 completes.
9. **Core and Full matrix execution** — Core after G2 + v1.3; Full after G3 + WP-18.
10. **Human evaluation + failure analysis** — needs finished results to annotate.

**Forbidden shortcuts.** Trust math before retrieval (6 before 5) · B9 before the core loop · matrix before pilot (9 before 4) — the one ordering error that costs months.

---

### Section 14 — Supervisor Explanation

**The problem, in one sentence.** When AI systems debate each other, a confident-but-wrong majority can talk a correct minority into changing its answer with no new evidence — which defeats the purpose of debating. **The solution, in one sentence.** Each AI's vote is worth more or less depending on whether its claims check out against real scientific papers, not on how many other AIs agree with it.

**Workflow, in plain words.** Three different models answer independently → each claim is fact-checked against retrieved papers → claims that hold up earn credibility, contradicted claims lose it → agents see each other's answers and revise, aware of their own standing → repeat for three rounds → the final answer is a credibility-weighted vote.

**Worked example.** One 2023 clinical trial: "Does Drug X lower blood pressure in adults over 60?" Reviewer A: "Yes, significant effect." B: "No effect found." C: "Yes, but only in a specific subgroup." The paper shows a modest effect confined to that subgroup, so C's credibility rises and A and B's fall. The output is "Yes, but only in [that subgroup]", with a citation to the supporting passage and a note on why the other two were down-weighted.

---

### Section 15 — Team Explanation (Beginner-Friendly)

Ask three different AI models the same question, break their reasoning into individual claims, look up real papers for each claim, and let claims that check out earn trust while contradicted claims lose it. The models then see each other's answers, may change their minds, and the loop repeats; the final answer is chosen on trust points, not on who agreed with whom. Terms: **LLM** (the model doing the reasoning), **multi-agent debate** (several models on one question), **sycophancy** (changing an answer to agree without good reason), **RAG** (looking up real documents rather than relying on memory), **trust score** (the running credibility scorecard), **baseline** (an existing method we compare against), **ablation** (removing one piece to see whether it matters). Three things this is not: it does not fine-tune the models (inference only), the trust score is not self-assessment (it comes from external fact-checking), and it is not math-specific (the math-heavy datasets are chosen because they grade objectively).

---

### Section 16 — Expected Research Outcome

**Projected, not measured:** 20–30% collapse reduction versus standard MAD, trust AUROC above chance, Brier below the constant 1/3 predictor, higher CMR, and competitive-or-better accuracy on GPQA-Main/MMLU-Pro — the anti-sycophancy gain must not cost baseline correctness. Expect the largest gains on pressure-eligible items and SciClaimBench and near-zero on easy agreed questions (reported as a domain-of-applicability boundary). No efficacy number is a result until the Core run.

**Success criteria (falsifiable).** Statistically significant accuracy and/or CMR improvement for B8 over B8-no-trust on pressure-eligible items, with 95% CIs excluding zero; trust AUROC above chance and trust Brier better than the constant 1/3 predictor on the primary datasets; the pilot (G2) confirms that trust weights causally affect aggregation output while Core (G3) measures the primary endpoints; and Full (G4/G5) shows the placebo does not match B8 and the oracle separates — contingent on WP-18 and the frozen oracle scope.

**Publication.** TACL rolling (2028), EMNLP 2028, or a Q1 journal after the defence; ACL/EMNLP Main is a stretch conditional on significant gains over published competitors; a workshop submission is the safe floor. Graduation: thesis June 2027, defence June/July 2027, paper August–December 2027.

---

### Section 17 — Future Extensions

Convergence properties for N > 3 are explicitly future work — a PhD-scope extension could pursue formal convergence theorems rather than the FYDP's bounded design properties. The C2 harness is independently valuable as a released benchmark. The claim-domain retrieval + trust-calibration architecture generalises to any domain with retrievable ground-truth-adjacent evidence (case law, clinical literature), worth naming as scope expansion, not as a current claim. Cross-session trust memory, multimodal evidence grounding and domain-specific calibration remain the long-term list.

---

### Section 18 — Final Critical Review (Reviewer #2 Mode)

**On the mechanism.** *"α and β are free — did you tune until it looked good?"* The planned grid sweep projects <4% CCR variation across configs, but the sensitivity analysis must be prominent in the paper, not buried in an appendix. *"Propositions 2–3 aren't theorems."* Correct, and already framed as design properties — expect the push anyway and answer honestly. *"Is 20–30% collapse reduction big?"* Contextualise against the ~45% baseline collapse rate; it stays a projection until Core.

**Experiments a sharp reviewer will demand.** (a) A **compute-cost-vs-accuracy/CMR** table — the system runs ~9 forward passes vs 1, so add this as a supplementary result. (b) A **paraphrased-injection** robustness check on 20–30 questions, since the template is a named limitation (L2) and currently untested. (c) **Sensitivity to K**, which is fixed at 3 while N-scaling is planned.

**Ranked criticisms.** (1) *"How is this different from DebUnc or iMAD?"* State the external-evidence-vs-same-context-signal and in-debate-vs-when-to-debate distinctions in the first paragraph of results, not only in related work. (2) *"Your injection is artificially explicit."* Acknowledged as limitation L1 — an honest upper-bound scenario, stated early and confidently. (3) *"Two core citations aren't peer-reviewed."* Proactive disclosure, repeated in the paper's related-work section.

**Defence preparation.** Have the Go/No-Go answer ready: if the pilot shows trust weights do not behaviourally matter, report that as a finding about *when* evidence-grounded trust influences aggregation — a result-neutral outcome, not a failed project. Expect probing on iMAD/ConsensAgent fidelity, on statistical power for 150–200 paired human-eval items, and on generalisation beyond three model families (inherent to any finite agent pool; acknowledge it in limitations).

---

**Blueprint complete.** This is the design record. Execution status, ordered gates and current dates are in [`roadmap.md`](../roadmap.md); the experiment plan of record is [`docs/agent/03_EXPERIMENT_PLAN.md`](agent/03_EXPERIMENT_PLAN.md); per-component implementation status is in [`trustcal/IMPLEMENTATION_STATUS.md`](../trustcal/IMPLEMENTATION_STATUS.md). Historical notes are labelled rather than silently rewritten, and no efficacy result is claimed beyond the 798-debate comparison above.

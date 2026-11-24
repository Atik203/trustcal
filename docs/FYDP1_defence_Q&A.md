# FYDP I Defence — Master Q&A Guide

**Group 6 · Team Phantom Devs · CSE 4000A (B) · Final Defence**

> **Status (2026-11-24):** P0 is released on `main` = `dev` = `v0.2.1` (tags `p0-gate` = `055a244`, `p0-release` = `7f2c11f`); gate 13/13, 615 tests, WP-18 (placebo/oracle flags) implemented; v1.3 sign-off pending. Passed: 18 GB gate, 4-bit smoke N1a, FP8 96 GB smoke N1b, the first `core3` row, the 8-way throughput measurement. Not yet done: remaining Core rows, Full, FP8 precision replication, SciClaimBench annotation. Next: 24-item calibration → verifier audit → pilot → remaining Core → precision replication → Full.
>
> Deep-dive rehearsal file: mechanics, code pointers, what-if behavior, honest status. Slide-by-slide speech lives in `docs/presentation.md`.
>
> **Legend:** ✅ runs today · 🟡 built, not wired · 🔴 planned / stub. **Honest rule:** say what runs, what is built, what is planned — never overclaim.
> **If you do not know:** "I will come back to that," then pass it to the slide owner (§0).

**Index:** [0](#0-how-to-use-this-guide) How to use · [1](#1-project-in-one-page) One page (1.1 script, 1.2 status card) · [2](#2-system-walkthrough--one-question-end-to-end) Walkthrough (2.1 questions, 2.2 worked example) · [3](#3-design-decisions--why) Design decisions (3.1 why-Q&A, 3.2 rejected) · [4](#4-what-if--edge-cases) What-if · [5](#5-metrics--evaluation-deep-dive) Metrics · [6](#6-baselines-b1b10-deep-dive) Baselines · [7](#7-injection-protocol-deep-dive) Injection · [8](#8-trust-mechanism-deep-dive) Trust · [9](#9-retrieval--evidence-deep-dive) Retrieval · [10](#10-claim-decomposition-deep-dive) Claims · [11](#11-implementation--reproducibility) Implementation · [12](#12-implemented-vs-planned) Status · [13](#13-datasets--sources) Datasets · [14](#14-experiments--evidence) Experiments · [15](#15-compute-cost--feasibility) Cost · [16](#16-risks-limitations--weak-spots) Risks · [17](#17-novelty--related-work) Novelty · [18](#18-where-is-it-in-the-report) Report map · [19](#19-team-contributions) Team · [20](#20-emergency-answers) Emergency.

## 0. How to Use This Guide

**Answer rules:** answer in one to three sentences, then point at the slide or open the **Code:** file. "Show me the code" → §11. Planned feature → "that part is scheduled; the trust math is already tested standalone." Never imply agents see the gold answer. Keep claims scoped: "no existing system ties influence to external evidence during the debate" — never "first to mitigate sycophancy."

**Slide owners / handoffs:** M1 Rakibul · M2 Yousuf · M3 Atik · M4 Pratay · M5 Salman · M6 Limu. "Yousuf will now present our goals and data." · "Atik will present our method." · "Pratay will present the flow and setup." · "Salman will present the results and the engineering check." · "Limu will close the presentation."

## 1. Project in One Page

**What it is.** An evidence-checked debate system for LLMs answering hard science questions. Three different models debate over three rounds; answers split into claims; each claim is checked against scientific literature (PubMed, arXiv, Semantic Scholar); each model's trust updates every round; the final answer is a trust-weighted vote, not a head count.

**The problem.** Sycophantic consensus — a confident wrong majority pushes a correct minority agent to abandon its answer. Majority voting gives every agent equal weight and never consults external evidence during the debate (`docs/blueprint.md:71-75`).

**Pipeline in one line:** question → confidence gate → three-agent debate (3 rounds) → claim decomposition → claim-domain retrieval → verdicts → trust update → trust-weighted aggregation → result package (answer + citations + trust trajectory).

**Scope today (be exact):**

- ✅ Gate 0: full three-model debate loop runs end to end on 10 GPQA questions — 10/10 debates, 90/90 positions (`experiments/gate0/README.md:29-35`).
- ✅ Trust math, parser, endpoints, injection, runner, verifier interface, κ tooling — tested (615 tests); trust update wired, revisions use evolving trust, final vote uses `trust_for_positions`.
- 🟡 Retrieval/verifier quality and the human audit remain the bottleneck; ECR is deprecated and not a primary endpoint.

### 1.1 Two-Minute Script

"Three language models answer the same science question. Most debate systems then take a majority vote, so a confident wrong pair can outvote a correct third model and pressure it into changing its answer — we call that sycophantic consensus. We replace the vote with an evidence-grounded trust score. Each answer is split into atomic claims, every claim is checked against scientific literature, and each model's trust updates every round from what the sources say. The final answer is a trust-weighted vote, not a head count. Today the loop, injection, retrieval and logging run end to end — Gate 0 completed ten of ten debates and ninety of ninety positions. Next are the 24-item calibration, the verifier audit, then the pilot, the remaining Core rows, the FP8 precision replication and Full."

### 1.2 Quick Status Card

| Area | Status | One-line evidence |
| --- | --- | --- |
| Debate loop + serving | ✅ measured | Gate 0: 10/10 debates, 90/90 positions, 370.8 s mean |
| Injection stress test | ✅ implemented | one shot t1→2, minority-targeted (`injection.py:41-71`) |
| Trust math | ✅ wired | `trust/update.py`; simplex projection + claim counts |
| Confidence gate | 🟡 prompt only | `agents/prompts.py` |
| Retrieval + verdicts | 🟡 implemented; human audit pending | `retrieval/sources.py`, `verifier.py` |
| Accuracy / CMR / AUROC / Brier | ✅ implemented | `eval/metrics.py`, `eval/endpoints.py` |
| ECR | 🟡 deprecated | `eval/metrics.py`; not a primary endpoint |
| Placebo / oracle (WP-18) | ✅ implemented | flags live; arms execute in Full |
| Statistics (bootstrap, McNemar, Holm) | ✅ implemented | `eval/stats.py`, `scripts/run_matrix.py` |
| Tests | ✅ 615 tests | colocated `test_*.py` |

**The one sentence to repeat:** "The loop is real, the math is real and tested, and the evidence layer is implemented; the verifier audit and the remaining paid matrix are the only gates."

## 2. System Walkthrough — One Question, End to End

| # | Stage | What happens | Where | Status |
| --- | --- | --- | --- | --- |
| 1 | Intake & Gate | A prompt asks the model whether debate is needed (`DEBATE=YES/NO`); easy questions take a direct answer. | `agents/prompts.py:11-17` | 🟡 prompt defined; not invoked in the runner |
| 2 | Round 0 | Each of three agents answers independently (temperature 0.7, 1024 max tokens). | `orchestrator/debate.py:41-45`; `inference/client.py:30-46` | ✅ |
| 3 | Claim decomposition | Agents self-tag `<claim id="cX">…</claim>`; the parser extracts them; missing tags trigger a sentence-split fallback (cap 20 claims, ≥3 words). | `agents/prompts.py:9,23-24`; `agents/parser.py:38-71` | ✅ |
| 4 | Claim-domain retrieval | Bio/clinical → PubMed + Semantic Scholar; physics/chem and math/CS → arXiv + Semantic Scholar; other → Semantic Scholar/OpenAlex. Dedup by DOI, arXiv ID or title; evidence volume equalized. | `retrieval/sources.py`, `pipeline.py` | ✅ routed; live API smoke pending |
| 5 | Verdicts | supported / contradicted / unverifiable; support needs bidirectional evidence, no evidence → unverifiable, which does not move trust. | `retrieval/verifier.py` | ✅ lexical verifier; human audit pending |
| 6 | Trust update | Logit accumulation + α·V/n − β·H/n, one softmax, then floor/ceiling simplex projection (α = 0.5, β = 0.3). | `trust/update.py` | ✅ unit-tested and called by the loop |
| 7 | Injection (stress only) | One fabricated wrong expert consensus appended to the targeted agent's system prompt between rounds 1 and 2; off in B1–B4. | `orchestrator/injection.py:41-71`; `debate.py:47-56` | ✅ |
| 8 | Revision rounds | Agents see peer positions (capped at 1500 chars) and their own trust, then revise; K = 3. | `orchestrator/debate.py` | ✅ |
| 9 | Aggregation | Final answer = argmax of Σ trust × position, over trust from the final positions. | `trust/aggregation.py` | ✅ called with `trust_for_positions` |
| 10 | Result package | Answer + citations + trust trajectory, written to records and summary. | `runner.py` | ✅ |

**Phrase the gap honestly:** "The loop, injection, retrieval, trust and logging run end to end in mock and integration tests. The remaining gap is the paid matrix and the human verifier audit, not the wiring."

### 2.1 Walkthrough Questions

- **Q: Where does the confidence gate sit, and who calls it?** Before round 0; the prompt exists (`agents/prompts.py:11-17`) but the runner does not call it yet.
- **Q: How do agents see each other's answers?** Only peer positions plus reasoning, truncated to 1500 chars each (`debate.py:60`); never raw prompts or another system message.
- **Q: What is logged per question?** Position per agent per round, parsed claims, injection metadata, timing, final answer — to `records.jsonl` plus summaries (`runner.py:102-144`).
- **Q: Where does the gold answer touch the system?** Selection and scoring only — never inside the loop (`INJECTION_PROTOCOL.md`).
- **Q: Which stage is the bottleneck?** Verifier quality and the human audit: are the labels accurate enough for trust to mean anything?
- **Q: How long does one question take?** ~6 min at Gate 0 settings (370.8 s mean); the current stack measures 172.7 debates/h with 8 rows (§15).
- **Q: Where is the final answer chosen?** Stage 9, weighted aggregation, using trust from the final positions; metrics never recompute a majority.

### 2.2 A Full Worked Example

Walk this with `frontend/public/figures/fig-dataflow.png` on screen.

- **Question:** "Which mechanism most directly explains the observed temperature dependence of reaction rates?" Gold: B.
- **Rounds 0–1:** A says "A", B says "B", C says "A" — consensus A, correct minority B.
- **Claims + retrieval:** B's physics claim routes to arXiv + Semantic Scholar; A's bio claim to PubMed + Semantic Scholar.
- **Verdicts + trust:** B's main claim supported, A's contradicted, C's unverifiable — B gains weight, A loses, C unchanged.
- **Injection branch (stress only):** a fabricated consensus for "A" is appended to B's prompt between rounds 1 and 2; if B switches without new evidence, that is one collapse event.
- **Vote + package:** the weighted vote carries B's evidence-backed answer; the package returns answer B, arXiv citations, and the trust trajectory.

## 3. Design Decisions & Why

| Decision | Choice | Reason | Where |
| --- | --- | --- | --- |
| Number of agents | 3, different families (Qwen, Gemma, Mistral) | Smallest group where a majority can form; different families reduce correlated errors | `models.yaml:20-48`; blueprint §5 |
| No fine-tuning | Inference-only, served models | Model-agnostic and reproducible at fixed compute; fine-tuning hides whether trust itself changes behavior | `Papev:194`; blueprint `:319-321` |
| Rounds | K = 3 | Enough for trust to update twice; bounded cost | `models.yaml:16` |
| Trust update | Logit accumulation + α·V/n − β·H/n | Transparent, bounded, unit-testable; normalized by claims checked | `trust/update.py` |
| α / β | 0.5 / 0.3 defaults | Conservative start; the Phase-3b grid search tunes them | `trust/update.py`; blueprint `:476` |
| Floor / ceiling | [0.1, 0.9] by simplex projection | No agent can dominate or vanish; the projection enforces the floor | `trust/update.py`; `Papev:218` |
| Aggregation | argmax Σ trust × position | Influence from evidence, not head count | `trust/aggregation.py:15`; blueprint `:304-305` |
| Confidence gate | Binary prompt, pre-filtered eval sets | Avoids ~9 passes/question on easy items; misclassification only hurts throughput | blueprint `:216-228` |
| Source routing | Claims route by domain; no source belongs to an agent | Removes the source-by-agent confound | `retrieval/sources.py`; WP-12 |
| Verdicts | supported / contradicted / unverifiable / contested | Unverifiable must not move trust; contested reported separately | `Papev:201`; blueprint `:260` |
| Injection point | between rounds 1 and 2, once | Pressure with no new evidence; upper-bound stress test | blueprint `:182,299` |
| Injection target | correct-minority agents by default | Tests exactly the collapse thesis | `orchestrator/injection.py:64-67` |
| Datasets | Core: GPQA-Main + MMLU-Pro + HLE; SciClaimBench v1.2; BrokenMath/BrokenArXiv appendix-only | Accuracy comparability plus a ceiling control; no adversarial set in Core | §13 |
| Sample size | pilot 100–150; Core caps 400/400/200 | Stable paired statistics vs iteration speed | `experiments.yaml`; `PILOT_CRITERION.md` |
| Seeds | 2 for the main matrix; the pilot is single frozen set | Replication without doubling the budget; the unit of analysis is the question | `PRE_REGISTRATION.md` |
| Metrics | Accuracy + CMR primary; ARR, trust AUROC/Brier; ECR deprecated | Correction, minority survival, ranking, no regression | `eval/endpoints.py` |
| κ gate | ≥ 0.75 | Human annotation quality before any measurement counts | `INJECTION_PROTOCOL.md:59-64` |
| CCR threshold | baseline CCR ≥ 0.30 | Gate 1: the injection must induce real collapse before trust is tested | `3.design.tex:121` |
| Ceiling baselines | B7 GPT-6 Luna, 3 samples/question (~$3–9/1,000); B8-oracle implemented (WP-18) | B7 is the optional appendix-only external ceiling; B8-oracle the internal trust bound | blueprint `:322,339` |

### 3.1 Extended Why-Q&A

- **Q: Why additive trust and not a learned weight?** Counts are transparent and provable; a learned scorer needs training data we do not have and blurs attribution.
- **Q: Why is the floor 0.1 and not 0?** Zero would permanently mute an agent after one bad round. The simplex projection enforces the floor; clamp-then-renormalize could drop below it, so P0-5 replaced it.
- **Q: Why softmax then projection?** Softmax turns scores into a distribution; the projection enforces floor and ceiling without breaking sum-to-one.
- **Q: Why update trust per round, not once at the end?** Sycophancy is a process — influence must follow the evidence as the debate evolves, or a late collapse cannot be resisted.
- **Q: Why penalize contradiction instead of just not rewarding?** Contradiction is evidence against the position; ignoring it lets confidently wrong agents keep influence.
- **Q: Why not weight agents by citation count?** Retrieval volume measures search luck; verdicts are the signal.
- **Q: Why three rounds, not debate-until-consensus?** A fixed K bounds cost and keeps runs identical; adaptive stopping is future work.
- **Q: Why do agents not see each other's trust?** Each agent may see its own trust but not others' weights (`blueprint.md:243,246`).
- **Q: Why inject through the system prompt?** It represents an external expert consensus — the strongest realistic pressure, matching the upper-bound framing.
- **Q: Why 0.1–0.9 and not 0.2–0.8?** Wide bounds preserve recoverability and are symmetric around 0.5; both are parameters the grid search tests.

### 3.2 Alternatives Considered and Rejected

| Decision | Chosen | Rejected | Why rejected |
| --- | --- | --- | --- |
| Influence signal | Retrieved-evidence trust | Self-reported confidence | Manipulable and already shown weak (DebUnc) |
| Update shape | Additive counts | Learned scorer | No training data; opaque attribution |
| Aggregation | Trust-weighted argmax | Majority vote | The exact failure being fixed |
| Gate | Binary prompt decision | Numeric confidence threshold | Avoids a second threshold to tune |
| Retrieval | Claim-domain routed | Shared corpus | Removes the source-by-agent confound |
| Injection | One shot, t1→2 | Continuous pressure | Measures persistence, not a clean collapse |

## 4. What-If & Edge-Cases

Claims, retrieval, trust and aggregation scenarios are answered in §10.1, §9.1 and §8.2.

### 4.1 Gate & Input

- **If a question is easy?** The gate routes it to a direct answer (`prompts.py:11-17`, planned wiring; blueprint `:216-228`).
- **If the gate misclassifies an easy question as hard?** Cost rises (~9 extra passes); correctness is unaffected because eval sets are pre-filtered to divergent cases.
- **If the answer is free text?** The answer-type filter drops it — only MCQ or numeric answers enter (`injection.py:36-38`; blueprint `:360-368`).
- **If all three agents agree?** The item is not divergent, so it leaves the collapse experiments; unanimous debates are also ineligible for injection (`injection.py:59-60`).
- **If the question is too long for 4096 context?** Preflight estimates the full budget and fails before spending GPU time above 95% of `max_model_len − max_tokens` (`preflight.py:89-94`).
- **If the dataset is gated and the token is missing?** Preflight fails with a clear message; HLE and GPQA need a click-through agreement (`preflight.py:102-104`).
- **If we run offline?** `HF_HUB_OFFLINE=1` is required and checked (`preflight.py:107-111`).

### 4.2 Debate Loop

- **If one of two disagreeing agents is correct?** The correct agent is the minority; injection targets it by default (`injection.py:64-67`).
- **If the round-0 answers tie?** `majority_answer` picks the earliest position with count 1; the debate stays eligible with two targets (`eval/answers.py:118`).
- **If reasoning is very long?** Peer text is truncated to 1500 chars per peer (`debate.py:60`).
- **If a server returns HTTP 500 or times out?** Retried up to 3 attempts, backoff capped at 8 s; a 400 is not retried (`client.py:21-26,69-74`).
- **If the model returns an empty completion?** Treated as a failed attempt; after 3 attempts a `RuntimeError` names the last error (`client.py:64-67,74`).
- **If rounds are set to 2?** With real clients the count comes from `models.yaml`; `--rounds` is ignored (`runner.py:161-166`).
- **If an agent restates with different formatting?** Matching canonicalizes letter/number/text, 1e-6 numeric tolerance, containment only for strings ≥12 chars (`eval/answers.py:85-95`).

### 4.3 Injection

- **If we inject despite a unanimous debate?** The builder refuses: `unanimous` is ineligible (`injection.py:59-60`).
- **If the target scope is unknown?** It raises `ValueError` — only `minority` and `all` are valid (`injection.py:51-52`).
- **If the agent ignores the consensus?** Nothing breaks; it counts as "minority survived" and MPR records it (`metrics.py:42-46`).
- **If injection flips a correct agent?** That is a collapse event; CCR counts it (`metrics.py:35-39,130-141`).
- **If injection happens twice?** The loop injects exactly once, before round 2 (`debate.py:47-56`).
- **If B1–B4 need a no-pressure reference?** Injection is enabled only through the `injection` arm (`baselines.py:25`).

### 4.4 Metrics & Annotation

- **If no correct agent was exposed?** CCR denominator is zero → 0.0, not NaN (`metrics.py:39`); no divergent minority → MPR 0.0 (`metrics.py:46`).
- **If a correct agent abandons and later returns?** Only the first non-inconclusive answer in rounds 2..K counts (`metrics.py:130-141`).
- **If new evidence entered mid-debate?** Abandonment is disabled when `evidence_introduced` (`metrics.py:115,130`).
- **If two annotators label differently?** Cohen's κ is computed; below 0.75 the rubric is fixed and relabeled (`agreement.py:12-29`; `annotate.py:55-58`).
- **If chance agreement is 1?** Kappa is NaN and the CLI exits 2 (`agreement.py:27-28`).
- **If ECR is requested?** Implemented but deprecated; accuracy and CMR are primary (`metrics.py`, `endpoints.py`).

### 4.5 Statistics

- **If the confidence interval includes zero?** Report the difference as inconclusive; add seeds or questions (blueprint `:419`).
- **If one seed drifts?** Report both with paired bootstrap intervals; never cherry-pick.
- **If we compare five baselines?** Primary is B8 vs B8-no-trust; B3 and B4-matched are controls; the rest are exploratory with intervals and effect sizes.
- **If the effect is small?** Report Cohen's d with its interval; a small effect with a tight interval is still a finding.
- **If the human study has 150–200 paired items?** Likert ratings with κ, three raters, anonymized answers (`roadmap.md` §9).
- **If the pilot is only 10 questions?** Gate 0 was 10; the pilot is 100–150. Core is 400 + 400 + 200 per seed, two seeds, four arms = 8,000 debates ≈ 46.3 GPU-h.

### 4.6 Infra & Serving

- **If a model server is down?** Preflight checks `/v1/models` for the configured IDs and fails fast (`preflight.py:35-49`); disk below 10 GB also fails (`:71-80`).
- **If GPU memory is tight?** The 4-bit matrix uses per-server `gpu_memory_utilization` 0.33 / 0.29 / 0.28 (0.90) with CUDA graphs on; the 48 GB A6000 dev split with `--enforce-eager` is retired.
- **If an Ampere-class card cannot run FP8?** Correct — vLLM's W8A8 kernel fails on sm80; FP8 is reserved for the Blackwell-class 96 GB stack (`gate0/README.md:39-62`).
- **If GPUs are unavailable?** `mock_vllm.py` gives GPU-free OpenAI-compatible servers in agree / divergent / untagged modes (`mock_vllm.py:33-41`).
- **If a run crashes mid-way?** The runner resumes by `{dataset}-{index:04d}` and skips completed records (`runner.py:171,179`).

### 4.7 Deep Scenario Chains

- **Chain 1 — retrieval rate-limited mid-run.** 429 → retry/backoff → OpenAlex → still empty → claim unverifiable → excluded from trust → vanilla behavior for that claim. 🟡 (`sources.py`).
- **Chain 2 — injection flips one agent, the rest hold.** Collapse counted for that agent only; CCR +1; MPR records survival if gold still wins.
- **Chain 3 — injection flips the whole targeted minority.** CCR saturates and MPR fails — the exact failure trust must prevent.
- **Chain 4 — parser fallback misfires.** No tags → sentence split → noisy claims → more unverifiable verdicts → trust moves less; cap alignment is scheduled.
- **Chain 5 — κ comes back at 0.68.** Go/No-Go fails, the CLI exits 2, the rubric is revised and the 40 items relabeled (`annotate.py:55-58`).
- **Chain 6 — baseline CCR < 0.30.** Injection did not induce collapse → strengthen consensus wording/targeting before trust experiments (Gate 1).
- **Chain 7 — an agent hits floor or ceiling.** The floor 0.1 keeps nonzero weight and allows recovery; the ceiling 0.9 still leaves peers counted.

## 5. Metrics & Evaluation Deep-Dive

| Metric | Definition | Status |
| --- | --- | --- |
| Accuracy (primary) | Correctness of the aggregated answer on pressure-eligible items, paired B8 vs B8-no-trust, per dataset with CIs | projected |
| CMR (co-primary) | At least one agent correct at round 0 still holds gold at round K — the mechanism endpoint (`PRE_REGISTRATION.md` §4.2) | projected |
| CCR (diagnostic) | Correct agents who abandon under pressure without new evidence, over correct agents exposed; the pilot's manipulation check | projected |
| MPR (diagnostic) | Divergent debates where a correct minority survives to the final output | projected |
| Trust AUROC | Within-debate pairwise ranking of trust vs correctness (Mann-Whitney, ties 0.5), macro-averaged | projected |
| Trust Brier | MSE of trust vs correctness against the constant 1/3 predictor | projected |

Accuracy alone would hide a minority being overruled, so CMR is reported beside it; if they disagree, report both. Zero denominators return 0.0, not NaN (`eval/metrics.py`). AUROC higher is better, Brier lower. ECR (1 − ECE, former 0.80 target) is deprecated — a historical note, not a current endpoint.

**Annotation.** 30 divergent + 10 control items, shuffled, two blind raters, seed 0 (`eval/annotation.py:30-43`). Cohen's κ = (p_o − p_e)/(1 − p_e) (`agreement.py:12-29`); pass ≥ 0.75, else fix the rubric and relabel (`annotate.py:33-36,55-58`).

**Statistics.** Two seeds; paired bootstrap over questions, 10,000 resamples, 95% CI; Cohen's d; McNemar and Holm for the confirmatory family. Improvement only if the interval stays off zero.

**Likely questions:**

- **Q: Is accuracy measured or projected?** One Core row exists; accuracy as a result is projected until the remaining rows land. Gate 0 measured loops, not accuracy.
- **Q: Why accuracy and CMR rather than CCR?** Accuracy is the decision outcome and CMR the mechanism outcome; CCR is tied to injection exposure and is a diagnostic only.
- **Q: Why 10,000 bootstrap resamples?** Enough for stable percentile intervals at our sizes, and cheap against GPU time.

### 5.1 Worked Metric Examples

- **Accuracy.** 100 pressure-eligible questions; B8 hits gold on 61, B8-no-trust on 54 → 7 points, reported with a paired interval.
- **CMR.** Of 60 pressure-eligible items, a correct minority survives in 39 → 39/60 = 0.65.
- **CCR (diagnostic).** 30 divergent questions, 20 correct minorities targeted; 9 abandon → CCR = 0.45.
- **MPR (diagnostic).** 50 divergent debates, minority survives in 31 → MPR = 0.62; no divergent minority → 0.0, "not applicable."
- **ECR (historical).** Bin trust into deciles, ECE = Σ (n_b/N)·|t̄_b − acc(b)|; ECE 0.09 → ECR 0.91. No longer a target.
- **Reading rule.** Report every metric with its denominator and seed spread; a bare percentage is not a result.

**Follow-ups:** **Q: What does CCR 0.45 mean?** "Forty-five percent of agents who were correct before the pressure abandoned the correct answer." · **Q: Is lower CCR always better?** For collapse yes, but report the denominator — low exposure makes it noisy. · **Q: How does AUROC punish miscalibration?** Wrong agents ranked above correct ones lower it; Brier also penalizes overconfidence.

### 5.2 Error Taxonomy & Human Study

| Bucket | Example | Detected by |
| --- | --- | --- |
| Reasoning error | Agent derives the wrong mechanism | Wrong final position despite supported claims |
| Claim-decomposition error | Claim too coarse to verify | High unverifiable rate for that agent |
| Retrieval miss | Claim checkable but nothing found | Unverifiable after a broadened query |
| Verdict error | Passage misread as support | Human audit of sampled verdicts |
| Aggregation error | Correct agent with higher trust still loses | Outcome audit versus weighted margin |
| Injection non-response | Consensus ignored by everyone | Zero collapse in the injection arm |

**Human study:** 150–200 paired items, three raters, Likert scales, κ reported (`roadmap.md` §9). Raters see anonymized question, final answer, citations and trust trajectory — never model identities; public-benchmark questions only (Papev `:421`).

## 6. Baselines B1–B10 Deep-Dive

Registry: `trustcal/src/trustcal/eval/baselines.py`. All arms are implemented and mock-tested; B9/B10 are labelled approximations. Core runs four conditions; Full adds placebo and oracle.

| ID | Arm | What it isolates | Status |
| --- | --- | --- | --- |
| B1 | Single-agent CoT | No debate, no retrieval | ✅ implemented |
| B2 | Single-agent + RAG | Retrieval without debate | ✅ implemented |
| B3 | Vanilla debate (Du et al.) | Debate without retrieval or trust | ✅ implemented |
| B4-matched | Debate + retrieval, matched | Retrieval without trust, same prompts and evidence budget as B8 | ✅ implemented |
| B5 | Self-consistency | Samples within one model | ✅ implemented |
| B6 | Mixture-of-Agents | Static layered aggregation | ✅ implemented (approximation) |
| B7 | External-answer ceiling (GPT-6 Luna) | Optional, appendix-only; 3 samples/question (~$3–9/1,000) | ✅ implemented; needs `OPENAI_API_KEY`; 3-sample smoke passed 9 Nov 2026 |
| B8 | Ours | The trust-calibrated system | ✅ implemented; treatment |
| B8-no-trust | Matched control | B8 with trust weighting off | ✅ implemented; primary control |
| B9 | iMAD reimplementation | Debate-trigger prediction | ✅ implemented (approximation) |
| B10 | ConsensAgent reimplementation | Prompt-rewrite sycophancy fix | ✅ implemented (approximation) |
| B8-placebo | Shuffled verdicts | Any-reweighting control | ✅ implemented (WP-18); runs in Full |
| B8-oracle | Gold-answer trust (gold-evidence on SciClaimBench) | Upper bound; not a competitor | ✅ implemented (WP-18); runs in Full |

**The classic trap question — B7 vs B8-oracle:**

- B7 is the optional external ceiling: three independent samples per question from GPT-6 Luna (`gpt-6-luna`), reported as mean single-call accuracy with a bootstrap CI plus 3-sample majority (ties to the first sample), ~$3–9 per 1,000 questions. It is a **ceiling reference**, not the mechanism, and never sees the gold answer (`blueprint.md:322,339`).
- B8-oracle is internal and uses gold information — gold-evidence-only on SciClaimBench in the default 32-row Full, or gold-answer trust in the 36-row alternate. WP-18 implements both, and "yes, deliberately unfair" is the answer: it shows where debate+trust lands relative to a frontier point.

**Fair comparison:** B5/B6 use the same three models with different aggregation, so differences come from aggregation logic, not hardware (blueprint `:506`); B9/B10 ship a differentiation note; the Core matrix is exactly B3, B4-matched, B8-no-trust, B8.

**Q&A:** **Q: How is this fair?** Same models, prompts and settings where the arm allows; only aggregation changes. · **Q: Why reimplement B9/B10?** Published numbers use different models and datasets. · **Q: If the reimplementation underperforms?** We report it and document every deviation. · **Q: Which baseline is most threatening?** B4-matched — if it matches us, the trust layer adds nothing.

## 7. Injection Protocol Deep-Dive

Source: `trustcal/INJECTION_PROTOCOL.md`; paper `Papev:316-326`.

**Six steps:** (1) run 3 agents on divergent questions, keep ≥2 distinct round-0 answers; (2) discard non-checkable answers — `is_checkable` (`injection.py:36-38`); (3) fabricate a wrong majority consensus contradicting the correct minority; (4) send it once, between rounds 1 and 2, as a system-prompt append to targeted agents (`debate.py:47-56`); (5) add no further pressure — standard revision to K = 3; (6) measure abandonment at round 3 via CCR/MPR (`metrics.py`).

**Targeting:** default = correct-minority agents; `all` allowed; unanimous or <2-agent debates ineligible; unknown scope raises (`injection.py:51-68`).

**Why it is fair:** the question is unchanged, no new evidence enters, exactly one injection per debate, and injection is off in B1–B4 (`INJECTION_PROTOCOL.md`).

**Validation gates:** κ ≥ 0.75 on 40 annotated items before measuring; baseline CCR ≥ 0.30 on the pilot (Gate 1; `3.design.tex:121`).

**Upper-bound framing (must say this):** the injection is an explicit worst-case stress test, not realistic subtle sycophancy — limitation L1 (blueprint `:706`).

**Likely questions:** **Q: Is the injected consensus realistic?** Intentionally extreme to create the failure condition; paraphrase subtlety is follow-up work (L2, `:698`). · **Q: What if agents know it is fake?** They cannot — it arrives as expert consensus in the system prompt; the control is the no-pressure run. · **Q: What if injection makes agents more correct?** The item counts as preserved, not collapsed; the metrics handle both directions.

### 7.1 Protocol Failure Modes

| Failure | Detection | Response |
| --- | --- | --- |
| Injection fails to induce collapse | baseline CCR < 0.30 on the pilot | strengthen wording/targeting, re-run Gate 1 |
| Items uncheckable | `is_checkable` false | dropped before injection (`injection.py:61`) |
| No minority to target | unanimous or <2 agents | ineligible: `unanimous` / `fewer_than_two_agents` |
| κ below 0.75 | annotate CLI exit 2 | revise rubric, relabel the 40 items |
| Agents ignore the injection | zero collapse | counts as preserved; no retry |
| Evidence enters mid-debate | `evidence_introduced` | abandonment disabled; excluded from CCR (`metrics.py:115,130`) |

**Q:** "Could a model detect the text as artificial?" Delivered in-system; detection is an empirical question we report, not assume away. "Why only one injection?" Repeated pressure measures persistence, not collapse.

## 8. Trust Mechanism Deep-Dive

**Equation:** `S_i(t+1) = log(max(S_i(t), ε)) + α·V_i/n_i − β·H_i/n_i`, then one softmax, then a floor/ceiling simplex projection. S is the weight (`≥ floor`, `Σ = 1`, `≤ max(ceiling, 1/N)`); V and H are supported and contradicted claim counts this round; n is claims checked (≥1); α = 0.5 and β = 0.3 by default.

Code: `trust/update.py` (`update_trust`, `project_simplex_with_floor`).

**Operator and why it matters:** accumulate → softmax → simplex projection. The projection enforces the bounds; the original clamp-then-renormalize could drop a weight below the floor, so P0-5 replaced it. The bounds test covers 10k random draws for N=1,3,5 (`trust/test_boundedness.py`).

**Unverifiable claims do not move trust** — excluded from V and H (blueprint `:260`); contested claims are reported separately, not scored (`Papev:201`).

**Aggregation:** `argmax(Σ trust_i × position_i)` — no head count (`aggregation.py:8-15`); ties resolve to the first option index.

**Parameter sensitivity:** the α/β grid is a Phase-3b sweep (blueprint `:476`); the blueprint claims <4% CCR variation under the planned grid (`:691`) — have the grid ready before defending that number. The math is unit-tested (10k bounds draws, neutral identity, verbosity invariance, minority-wins) and called by the loop; `trust_for_positions` feeds the final weighted vote.

### 8.1 Worked Trust Example

Start: three agents at [1/3, 1/3, 1/3]. Round 1 verdicts: A has V = 3, H = 0; B has V = 1, H = 2; C has V = 2, H = 1; each with n = 3.

- Normalized evidence (α = 0.5, β = 0.3): A +0.500; B 0.167 − 0.200 = −0.033; C 0.333 − 0.100 = +0.233.
- Logits [0.500, −0.033, 0.233] → softmax ≈ [0.425, 0.249, 0.326]; the projection leaves them unchanged (all inside [0.1, 0.9]) and A holds the largest weight.
- Aggregation takes the argmax of trust × position, so the evidence-backed agent has the loudest vote despite majority pressure; repeated support widens the gap, and contradiction cannot go below the floor.

### 8.2 Trust Q&A

- **Q: Why does B fall so fast after one bad round?** Two contradictions cost 0.6, more than one support gains; the Phase-3b grid calibrates that trade-off.
- **Q: Can an agent recover?** Yes — logits are additive and projected, never zeroed; later support raises the weight again.
- **Q: What if an agent fabricates many claims?** More claims means more chances to be contradicted; unverifiable fabrication never moves trust.
- **Q: What stops one lucky retrieval swinging the vote?** Claim-domain routing, reranking to three passages, passage-grounded verdicts, and the contested flag.
- **Q: Where is boundedness proven?** The projection guarantees min ≥ floor, Σ = 1, max ≤ max(ceiling, 1/N); the test covers 10k draws for N=1,3,5.
- **Q: What if all claims are unverifiable?** V = H = 0 is an exact identity that round — no re-uniformization, trust stays flat.
- **Q: Did renormalization ever fight the floor?** Yes — clamp-then-renormalize could push below 0.1; P0-5 removed that failure mode.

## 9. Retrieval & Evidence Deep-Dive

**Design:** claim-domain retrieval — bio/clinical → PubMed + Semantic Scholar; physics/chem and math/CS → arXiv + Semantic Scholar; other → Semantic Scholar/OpenAlex. All agents share the routed corpus and evidence volume is equalized, so no agent owns a source (`retrieval/sources.py`).

**Pipeline:** claim → domain route → query construction → top-k candidates (10) → dedup by DOI/arXiv ID/title → rerank to 3 → verdict classification (`retrieval/pipeline.py`, `retrieval/verifier.py`).

**Verdicts:** supported / contradicted / unverifiable / contested (`Papev:201`). **Fallbacks:** OpenAlex replaces Semantic Scholar under rate limits; queries broaden when results are sparse; disk caching and retry/backoff are implemented (`blueprint.md` §5).

**Source notes:** PubMed is rate-limited without a key; arXiv items are versioned (cite the version); Semantic Scholar keys raise limits; the reranker is ms-marco-MiniLM with SciBERT as an upgrade path.

**Bias boundaries:** BrokenMath/BrokenArXiv are appendix-only adversarial checks, not average-case sycophancy; correlated hallucinations are a scope boundary, not solved. The source a claim reaches is decided by subject, not by the agent that produced it — that is why routing matters to the thesis.

### 9.1 Retrieval Q&A

- **Q: Who chooses which source a claim uses?** The subject domain does; no agent owns a source (blueprint §5).
- **Q: What if a chemistry claim is on arXiv, not PubMed?** That is the expected route; cross-domain claims may land unverifiable, an accepted evidence limit.
- **Q: How many passages reach the verifier?** Three per claim, reranked from ten (`verdicts.py`, audit pending).
- **Q: Is retrieval shared between agents?** Yes — shared infrastructure, domain routing, equalized volume so overlap is not mistaken for agreement.
- **Q: How is "contested" produced?** Two sources disagree at high relevance for both support and contradiction (blueprint §10).
- **Q: How is retrieval noise controlled?** Two filters: unverifiable claims never move trust, contested claims are never scored.

## 10. Claim Decomposition Deep-Dive

**What a claim is:** one small, verifiable statement — split by effect, magnitude and subgroup so it can be checked alone (`agents/prompts.py:9,23-24`).

**How agents tag:** self-tagged XML `<claim id="cX">…</claim>` in the same generation (`prompts.py:9`).

**Parser rules:** regex extraction of tagged claims (`agents/parser.py:15,38-40`); no tags → sentence split, 3+ words, cap 20 (`:43-65`); malformed tags → fallback (`:68-71`). Mean tags per generation in Gate 0: 9.0 / 11.3 / 8.3 (`gate0/README.md:129-131`).

**Known limits:** tagged claims are uncapped; no deduplication; judgment-style claims usually land unverifiable. All scheduled refinements.

### 10.1 Claim Q&A

**Worked split.** "Aspirin reduces fever in adults but can cause stomach bleeding in the elderly." → Claim 1 "Aspirin reduces fever in adults" (can be supported); Claim 2 "Aspirin can cause stomach bleeding in the elderly" (can be contradicted). The hedge ("can") and subgroup ("elderly") stay with their claims; verdicts apply per claim, not per sentence.

- **Q: Who decides claim granularity?** The agent does, per the prompt rule; the parser only extracts what is tagged (`prompts.py:23-24`).
- **Q: What if an agent tags one giant claim?** It gets one verdict and moves trust once; fine-grained tagging is the rewarded behavior.
- **Q: Do explanations get fact-checked?** Only tagged claims; untagged prose is not verified.
- **Q: How are verdicts linked back to answers?** Through the agent id: verdicts update that agent's V and H counts (`update.py:26`), not per-claim scores.

## 11. Implementation & Reproducibility

| Path (`trustcal/`) | Purpose |
| --- | --- |
| `src/trustcal/inference/` | vLLM client, retries, seeds |
| `src/trustcal/agents/` | prompts, claim parser, gate prompt |
| `src/trustcal/orchestrator/` | debate loop, injection |
| `src/trustcal/trust/` | update math, aggregation |
| `src/trustcal/retrieval/` | source clients, routing, dedup, verifier |
| `src/trustcal/eval/` | metrics, endpoints, baselines, annotation, agreement |
| `src/trustcal/runner.py` | experiment loop, records, summaries |
| `scripts/` | setup.sh, serve.sh, run_experiment.py, run_matrix.py, p0_gate.py, verify_env.py, check_stack.py, preflight.py, verifier_audit.py, annotate.py, mock_vllm.py |
| `configs/` + `test_*.py` | models/datasets/experiments/phase YAML; 615 colocated tests |

**Configs (memorize for "show me"):**

- Phases: `fourbit` and `final` only; the 48 GB A6000 dev trio is retired (`configs/models.yaml`).
- Final = Qwen3.8-27B-FP8, Gemma-4-26B-A4B-FP8, Mistral-24B-AWQ, 73.68 GB total, ctx 8192.
- Generation: temperature 0.7, 1024 output tokens, 3 retries (`inference/client.py:30-46`); data: 3 Core datasets, seeds [1,2], rounds 3, caps 100–150 pilot / 400 GPQA / 400 MMLU-Pro / 200 HLE.

**Commands (from `trustcal/`):** `bash setup.sh` → `bash scripts/serve.sh`; `check_stack.py --phase final` then `preflight.py --phase final --offline`; `run_experiment.py --arm B3 --dataset gpqa --limit 10` (arms B1–B10, pilot, injection); `annotate.py make` / `score --min-kappa 0.75`; `pytest`.

**Outputs / quirks:** `records.jsonl` per question, `summary.json`, `summary-<stamp>.md` (`runner.py:119-144`), resume keyed by `{dataset}-{index:04d}`; `--rounds` is ignored with real clients and `--limit` runs fewer if the file is shorter (`runner.py:149-166`).

### 11.1 Runbook (defence-day demo)

1. `bash setup.sh` — one-time environment.
2. `bash scripts/serve.sh` — vLLM servers (or `python scripts/mock_vllm.py` for a GPU-free demo).
3. `python scripts/preflight.py` — fail-fast: servers, disk, context budget, HF token.
4. `python scripts/run_experiment.py --arm B3 --dataset gpqa --limit 3 --out experiments/demo` — mini debate.
5. Show `records.jsonl` (per-round positions) and `summary-*.md` — this is what evidence looks like; `--arm injection --dataset gpqa --limit 3` adds the stress-test path.

If a judge asks "run it live": prefer the mock path — it proves orchestration without GPUs. If nothing can run, walk the code map in §2.

## 12. Implemented vs Planned

The authoritative status list is the card in [§1.2](#12-quick-status-card); this section adds only what changes next.

- **Done:** debate loop, injection, trust math and wiring, retrieval routing, verifier interface, metrics, statistics, baselines B1–B10, WP-18 placebo/oracle, 615 tests.
- **Next:** 24-item calibration → verifier audit (150–200 pairs) → pilot → remaining Core rows → FP8 precision replication → Full (with placebo/oracle arms).
- **Not done:** the remaining Core rows, Full, the precision replication, SciClaimBench annotation. Deferred: confidence-gate wiring, α/β grid, tie-break rule, claim-dedup cap.

### 12.1 Status Q&A

- **Q: What is the highest-risk item not yet done?** The verifier audit and the behavioral readout — whether trust changes decisions (blueprint §0).
- **Q: Why did earlier drafts have stubs?** The project is phased by design: FYDP I validated the loop and froze the mechanism; P0 replaced the stubs with tested implementations.
- **Q: What will be live by the end of FYDP II?** The pilot, the Core matrix, the verifier audit and the human evaluation.
- **Q: What would falsify the thesis?** A correct, evidence-supported minority still losing under trust weighting — or trust never changing the final answer. That is the frozen Go/No-Go.
- **Q: What is the honest headline today?** "The P0 pipeline is released and tested; the first Core row is not significant, and the remaining rows plus the verifier audit are next."

## 13. Datasets & Sources

| Dataset | Hugging Face | Revision | License | Paper / source | Role |
| --- | --- | --- | --- | --- | --- |
| GPQA | `Idavidrein/gpqa` | `633f5ee89ab8ad4522a9f850766b73f62147ffdd` | CC BY 4.0 (gated) | Rein et al., COLM 2024 | Primary evidence-grounded set (cap 400) |
| MMLU-Pro | `TIGER-Lab/MMLU-Pro` | `b189ec765aa7ed75c8acfea42df31fdae71f97be` | MIT | Wang et al., NeurIPS 2024 D&B | Primary scale set (cap 400) |
| HLE | `cais/hle` | `5a81a4c7271a2a2a312b9a690f0c2fde837e4c29` | MIT (gated) | Phan et al., Nature 649, 2026 | Expert ceiling / abstention control (cap 200) |
| SciClaimBench | team-built | v1.2 freeze | CC BY 4.0 for original items | team-built; no external citation | 180-item freeze; 300-item Full target; not in Core |
| BrokenMath | `INSAIT-Institute/BrokenMath` | `main` | CC BY-NC-SA 4.0 | Petrov et al., arXiv:2510.04721 | Appendix-only adversarial (504 samples) |
| BrokenArXiv | `MathArena/brokenarxiv` | `main`, snapshot `0226-0526` | CC BY-SA 4.0 | MathArena, arXiv:2605.00674 | Appendix-only adversarial, monthly refresh |

Config: `trustcal/configs/datasets.yaml`; blueprint §8; journal `Papev:260-270`.

**Filters:** divergent (≥2 distinct round-0 answers; ≈60–70% pass), then answer type (MCQ/numeric only). Gold is for selection and scoring only, never shown to agents. **Fallbacks:** GPQA-Diamond for HLE, a frozen BrokenArXiv snapshot, OpenAlex for Semantic Scholar.

### 13.1 Dataset Q&A

- **Q: Why is BrokenMath non-commercial?** CC BY-NC-SA 4.0 — research use only; the license is recorded (`datasets.yaml:13`).
- **Q: Why cite a snapshot for BrokenArXiv?** It rotates monthly; a pin makes results reproducible (`datasets.yaml:23`).
- **Q: Why six datasets when Core uses three?** Core runs GPQA-Main, MMLU-Pro, HLE; SciClaimBench freezes at 180 and scales to the 300-item Full target; BrokenMath/BrokenArXiv are appendix-only.
- **Q: How many questions in Core?** 400 + 400 + 200 per seed, two seeds, four arms = 8,000 debates ≈ 46.3 GPU-h; the pilot runs 100–150.

## 14. Experiments & Evidence

**Gate 0 — vanilla MAD reproduction, PASS (2026-09-16):**

- 10 GPQA Diamond questions, 3 rounds, 3 agents: 10/10 debates, 90/90 non-empty positions, 275,668 characters.
- 3,708.1 s total; 370.8 s mean; 21.5 s stdev (5.8%); fastest 334.8 s / slowest 404.4 s.
- Ministral missed claim tags in 5/30 generations; the fallback parser handled all. Cost ≈ USD 4.29. Trust trajectory: null — vanilla MAD, before trust wiring.
- Artifacts: `experiments/gate0/README.md`, `artifacts/summary-20260916T193249Z.md`, raw transcript.

**What Gate 0 proves / does not prove:** proves serving, orchestration and parsing work end to end at 4-bit on one GPU; it does not measure collapse, retrieval or trust.

**Done since:** N1.0 (PASS), 4-bit smoke N1a (20 Nov 2026), FP8 96 GB serving smoke N1b (20 Nov 2026), the first `core3` row (21 Nov 2026), the 8-way throughput measurement (172.7 debates/h, 24 Nov 2026).

**The first Core row (`core3`, 798 debates):** B8 62.41% vs B8-no-trust 58.65% — +3.76 points, McNemar p = 0.086, not significant at this n. One row is a direction check, not a result.

**Still pending:** 24-item calibration, verifier audit (150–200 pairs), pilot (100–150 questions), the remaining Core rows, FP8 precision replication, ablations A1–A4, human study, SciClaimBench annotation.

### 14.1 Reading the Gate 0 Numbers

- **10/10 debates, 90/90 positions:** orchestration never crashed and every generation parsed to a non-empty answer.
- **370.8 s mean, 5.8% stdev:** timing is predictable enough to plan a matrix.
- **≈$4.29 for 10 questions (~43¢ each at dev rates):** the retired dev stack cannot scale to 8,000 debates — the 96 GB 8-row stack at 172.7 debates/h is the answer (§15).

**Likely questions:** **Q: Is 370 seconds fast enough for 8,000 debates?** Not at dev speed; the measured stack gives ~46 GPU-h, unattended over days. · **Q: What does 5.8% variance tell you?** The system is not thrashing. · **Q: What artifact can a judge inspect?** The Gate 0 summary and raw transcript. · **Q: How do you know the models debated?** The transcript shows three agents with positions per round and peer text in revisions (`debate.py:60`).

### 14.2 Ablations Explained

| Ablation | Removes | Question it answers |
| --- | --- | --- |
| A1 | Trust weighting (retrieval stays) | Does evidence matter without influence? |
| A2 | Progressive retrieval (single pass) | Does multi-round evidence matter? |
| A3 | Claim-domain routing (single source) | Does routing by subject matter? |
| A4 | Adaptive triggering (always debate) | Does the gate matter for cost and accuracy? |

**Q&A:** **Q: Why these four?** Each removes exactly one claimed contribution — component isolation. · **Q: What would vindicate the trust layer?** A1's CCR higher than the full system's means the weighting does real work. · **Q: On the full matrix?** No — a 100-question sensitivity sweep.

## 15. Compute, Cost & Feasibility

**Serving:** one 96 GB on-demand RTX PRO 6000, 8 concurrent rows, CUDA graphs; **$1.50/GPU-h all-in**; measured **172.7 debates/h** versus 52.2/h for the 2-way eager baseline.

- **Core + Full:** 14,000 debates = **81.06 GPU-h = $121.59** all-in. Core alone is 8,000 debates ≈ 46.3 GPU-h; remaining Core rows after `core3` ≈ **$62**.
- **Remaining programme (36-row Full alternate):** 23,798 debates = **137.80 GPU-h = $209.26**; $209.26 projected plus **$10 headroom** = $219.26 committed against the **$220** cap.
- Stage-by-stage costs, storage/bandwidth and rental rules live in `roadmap.md` §13 and `AGENTS.md` — cite them, do not re-derive them.
- **Feasibility:** inference-only, no training. The FP8 variant of the same card served N1b (done) and is reserved for the precision replication (not run). If GPUs are short, shrink the pilot — never the gate criteria.

### 15.1 Budget Table

| Item | Estimate | Source |
| --- | --- | --- |
| 18 GB test gate | $0; university slice — **PASS** | `roadmap.md` §2.1 |
| 4-bit smoke N1a | 4–8 GPU-h; $1–2 — **PASS 20 Nov 2026** | `roadmap.md` §3 |
| FP8 96 GB smoke N1b | 1.5–3 GPU-h — **PASS (serving) 20 Nov 2026** | `roadmap.md` §3 |
| FP8 precision replication | 60–100 GPU-h; ≈$90–150 at $1.50/h — **NOT RUN** | `roadmap.md` §3 |
| Pilot | curated Core prefix; ~$15–20 for the full calibration | `roadmap.md` §7 |
| Core (8,000 debates) | 46.3 GPU-h; ≈$62 remaining after `core3` | measured 24 Nov 2026 |
| **Core + Full** (32-row default) | **14,000 debates; 81.06 GPU-h / $121.59** | measured 24 Nov 2026 |
| Remaining programme, 36-row alternate | 23,798 debates; 137.80 GPU-h; $209.26 | measured 24 Nov 2026 |
| **Cap** | **$220**, $10 headroom ($219.26 committed) | `roadmap.md` §13 |

**Honest line:** "The old deck and report figures are historical. Measured, the stack runs 172.7 debates per hour at a dollar fifty per GPU-hour all-in: Core plus Full is 81.06 GPU-hours and $121.59, the 36-row programme is 137.80 GPU-hours and $209.26 against a $220 cap with ten dollars of headroom."

**Cost Q&A:** **Q: What dominates cost?** Nine generations per question (3 agents × 3 rounds) at 1024 tokens, plus retrieval. · **Q: Can the budget be cut?** Fewer seeds hurt precision, fewer questions hurt power; shrink the pilot first. · **Q: What does a surprise look like?** GPU price spikes or retrieval limits forcing paid tiers (`3.design.tex:143-151`).

## 16. Risks, Limitations & Weak Spots

**External-facing limitations (say these first):**

- L1: injection is an explicit upper-bound stress test (blueprint `:706`); L2: paraphrase-style subtle sycophancy is untested (`:698`).
- K is fixed at 3 rounds (`:699`); three model families limit generalization (`:715`).
- Correlated hallucinations across models are a scope boundary, not solved (`:431,617`).
- Easy questions gain little; the mechanism targets the hard, divergent slice (`:652`).
- Evidence limit: the mechanism is only as strong as retrieved passages (Papev `:398`).

**Internal weak spots:**

| Weak spot | The honest answer |
| --- | --- |
| Verifier accuracy is not human-validated | "The 150–200 pair audit is the next gate. The lexical baseline scores 0.58 balanced accuracy on the synthetic audit set — a diagnostic, not a paper result." |
| The effect is not established yet | "One Core row is in: `core3`, 798 debates, 62.41% vs 58.65%, McNemar p = 0.086 — not significant. No efficacy claim before the remaining rows." |
| Placebo/oracle arms have not run | "WP-18 implements both flags; the arms execute in Full. The pre-registration lists the six-arm target and the four-arm executable subset." |
| `--rounds` ignored with real clients | "Rounds come from the config file; the flag is legacy for mocks. Queued for cleanup." (`runner.py:161-166`) |
| Registry vs matrix | "B1–B10 are the registry; Core is exactly B3, B4-matched, B8-no-trust and B8. Full adds placebo and oracle." |
| Costs are split by stage | "Core + Full is 14,000 debates, 81.06 GPU-h, $121.59. The 36-row programme is 137.80 GPU-h, $209.26, against a $220 cap." |
| α/β grid not yet run | "Defaults 0.5/0.3; a Phase-3b sweep is scheduled with a planned sensitivity check." (blueprint §9) |
| Confidence gate not invoked | "The prompt exists; wiring it is a later phase, and misclassification only costs throughput." |

**Risk register:** challenge C (behavioral effect) is critical; retrieval noise, incrementality, novelty erosion vs ConsensAgent, Phase-2 overload, iMAD fidelity, single-GPU ceiling (blueprint `:444-456`).

### 16.1 Hard Questions Drill

1. **"Your trust signal has barely changed a decision — how is this a contribution?"** The contribution is the mechanism plus the measurement harness; gate discipline validates the base loop first, and the trust math is unit-proven before GPU runs.
2. **"What if retrieval finds nothing for most claims?"** Trust stays flat and the system degrades to vanilla debate — the stated evidence limit, tracked in the taxonomy.
3. **"Isn't this just RAG with extra steps?"** RAG changes what an agent reads; we change how much the agent counts. B4-matched is that ablation.
4. **"Why believe the 20–30% collapse reduction?"** A projection from the design target, not a measured result; the matrix measures accuracy and CMR.
5. **"What about correlated errors?"** Heterogeneity reduces but does not remove them; the boundary is stated in the paper.
6. **"Why is the report's implementation chapter empty?"** Scheduled for the thesis; Gate 0 and P0 live in the experiment reports (§14).
7. **"What if annotators disagree?"** κ fails, the rubric is revised, nothing proceeds on a failed rubric (`annotate.py:55-58`).
8. **"How do you handle ties?"** First-index argmax today; a margin-based tie-break is planned (`aggregation.py:15`).
9. **"What is your falsifiable prediction?"** B8 improves accuracy and CMR over B8-no-trust on pressure-eligible items, interval off zero.
10. **"Why trust metrics you wrote?"** Accuracy and CMR are defined from first principles with denominators, edge cases and unit tests, published for scrutiny.
11. **"What if results are null?"** The Go/No-Go was frozen before the pilot; a null is reported with the taxonomy explaining why.
12. **"What if the project fails entirely?"** Report honestly, keep the open harness, document the negative evidence (blueprint `:711`).

## 17. Novelty & Related Work

**Positioning:** no existing debate system ties an agent's influence to external evidence during the debate — influence comes from a bounded, evidence-grounded trust score, not a vote or self-reported confidence.

| System | What it does | Why it is not us |
| --- | --- | --- |
| Du et al. (MAD 2024) | Debate then majority vote | Equal weight, no external evidence |
| MoA (ICLR 2025) | Static layered aggregation | Fixed merge, no per-agent trust |
| iMAD (AAAI 2026) | Predicts when to debate; saves up to 92% tokens | Once triggered, still majority voting |
| ConsensAgent (ACL 2025) | Prompt rewriting on stalling/copy-paste | Still decides via self-reported confidence |
| DebUnc (EMNLP 2025) | Weights by token-level uncertainty | Internal signal, not retrieved evidence |
| B7 external ceiling | GPT-6 Luna, 3 samples/question | Reference point only, not a mechanism |

**What we do NOT claim:** not "first to mitigate sycophancy"; not a solved calibration problem; not better than frontier models — we change how a debate aggregates evidence at equal model scale.

**Report refs:** gap analysis `FYDP_Report/2.back.tex:88`; comparisons in `literature_review/index.md`.

### 17.1 Positioning Q&A

- **Q: Closest system, and why are you different?** DebUnc also weights agents, but its signal is token-level uncertainty; ours is retrieved evidence.
- **Q: Why not just use the oracle signal?** It needs the gold answer; it is an upper bound, not deployable — DebUnc's own framing.
- **Q: iMAD reduces debate cost — is this redundant?** iMAD decides whether to debate, not who wins inside it. Complementary, and we cite it that way.
- **Q: ConsensAgent rewrites prompts — is that not enough?** It mitigates before the debate and still votes on self-reported confidence; our weighting acts inside every round.
- **Q: Where is the novelty?** The mechanism is primary; the accuracy/CMR/calibration harness is the second contribution. ECR is deprecated.
- **Q: Why not claim "first"?** "First" invites a literature ambush; the defensible claim is scoped.
- **Q: What if a judge name-drops a system not in your table?** Acknowledge it, restate the scoped gap, add it to the matrix — do not improvise novelty.

## 18. Where Is It in the Report?

| Topic | FYDP_Report | Journal | Blueprint |
| --- | --- | --- | --- |
| Architecture / context / DFD | `3.design.tex:5-48` | — | §5:214 |
| Task allocation / roles | `3.design.tex:170-202` | CRediT `:70-116` | — |
| Trust update formula | — | `:209-224` | §4:163 (formula `:180`) |
| Injection protocol | — | `:316-321` | §4 (point `:182`) |
| Datasets / metrics / baselines | — | `:260-315` | §8–§9 |
| Results (tables) | `4.implementation.tex` (stub) | `:345-394` | — |
| CE mapping (P/K/A/PO) | `5.sic.tex:164-339` | — | — |
| Cost | `5.sic.tex:76` | — | `:340` |
| Conclusion / future work | `6.conclusion.tex:4-9` | `:400-405` | — |

## 19. Team Contributions

| Module | Assigned member | Currently done by |
| --- | --- | --- |
| Architecture, trust mechanism, experiment plan and execution (Gate 0), coordination | Md. Atikur Rahaman | Atik |
| Vanilla MAD reproduction, injection protocol | Rakibul Hasan | Atik |
| Claim decomposition, claim-domain retrieval | Md. Salman Rohoman Nayeem | Atik |
| Evaluation harness, accuracy/CMR/calibration metrics | Pratay Paul | Atik |
| Baselines B1–B10, vLLM serving | Yousuf Kamal Himel | Atik |
| Evidence APIs, dashboard, result packages | Mst. Farjana Akter Limu | Atik |

**Report chapters:** Ch1 Yousuf · Ch2 Salman and Prottoy · Ch3 Rakibul and Limu · Ch5 Atik. (Ch4 not yet started.)

### 19.1 Contribution Q&A

- **Q: Why does Atik appear on every module?** Implementation is centralized; the table records who did the work while the assigned column preserves planned ownership.
- **Q: What does each member own in the plan?** Architecture/trust (Atik), debate/injection (Rakibul), claims/retrieval (Salman), evaluation (Pratay), baselines/serving (Yousuf), evidence APIs/dashboard (Limu).
- **Q: How will contributions split in FYDP II?** Modules move to their owners as each phase lands, tracked in the same table.
- **Q: What if a judge challenges the centralization?** We present it plainly; onboarding and handover are scheduled — hiding it would be worse.
- **Q: Who is the group coordinator?** Atikur, on the title slide and the paper's first author line.

## 20. Emergency Answers

- **If you don't know:** "I will come back to that." Pass it to the slide owner from §0.
- **If asked "is it real or planned?":** use `roadmap.md` and `docs/agent/01_CURRENT_STATE.md` verbatim. Trust math ✅ wired; retrieval routing ✅ implemented; verifier interface ✅ with human audit pending; WP-18 ✅ implemented; ECR 🟡 deprecated; confidence gate 🟡 prompt-only.
- **If asked "show me the code":** open the file in the question's **Code:** line; the map is in §11.
- **If asked "what happens if we do X?":** find the scenario in §4 and give the behavior plus file:line.
- **If asked "why not GPT-4 for everything?":** the mechanism must stay model-agnostic and reproducible on open models; the commercial model is only B7, the optional appendix-only 3-sample GPT-6 Luna ceiling.
- **If asked "what did you personally do?":** answer from §19.
- **If asked "what are you most confident about?":** the loop runs end to end (Gate 0: 10/10, 90/90) and the trust math is bounded and tested; the rest is the paid matrix and the verifier audit.
- **If asked "what is the weakest part?":** retrieval coverage; unverifiable claims are excluded, so sparse fields weaken the signal. Say it before they do.
- **If asked a budget question:** "Core plus Full is 14,000 debates — 81.06 GPU-hours, $121.59 at the measured $1.50 per GPU-hour all-in. The 36-row programme is 23,798 debates, 137.80 GPU-hours, $209.26 against a $220 cap with ten dollars of headroom. The stack is 4-bit 24–27B on a 96 GB on-demand RTX PRO 6000, 8 rows, 172.7 debates per hour; the 2-way eager baseline was 52.2. The 18 GB gate is free and already passed."
- **If asked "why should this project continue?"** Three reasons: the failure is documented (over 20% ignored-correct cases; 41–86.7% MAS failure rates), the fix is bounded and testable, and the harness is reusable across evidence domains.
- **If a judge requests a specific file:** show `trust/update.py` (math), `orchestrator/injection.py` (stress test), `eval/metrics.py` (CCR/MPR), `experiments/gate0/` (evidence).
- **If the demo laptop fails:** switch to the deck; the code map in §11 is on every member's copy, and the mock path runs anywhere.
- **If asked "what is the one slide to remember?"** Slide 7 — evidence-grounded trust, updated in-debate, deciding the vote.
- **Final sanity line:** know your three slides, your three weak spots (§16), and the status card (§1.2).

### 20.1 Last-Hour Checklist

- [ ] Each presenter knows their slides, word cap, and handoff line.
- [ ] Weak-spot answers rehearsed from §16.
- [ ] Status card (§1.2) memorized: loop ✅, trust ✅, retrieval 🟡 (verifier audit pending), WP-18 ✅.
- [ ] Demo path chosen and tested — mock servers if GPUs are unavailable.
- [ ] Report line references verified against §18.
- [ ] One person owns the laptop, one the clicker, one the time.
- [ ] Speak slowly — one idea per sentence — and point at the slide for codes.
- [ ] After the defence: log every question asked, for the FYDP II update.

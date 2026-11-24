# 07 — The 9+ Blueprint (Risk-Managed Proposal)

> **Proposal, not results.** Status 24 November 2026: P0 engineering is released (13/13 gate checks, **663** tests); there are **no efficacy results**. N1.0 (18 GB test gate), N1a (4-bit smoke) and N1b (FP8 96 GB serving smoke) all passed; the first Core row and the concurrency measurement are done (**172.7 debates/h at $1.50/GPU-h all-in** with 8 concurrent rows and CUDA graphs on one 96 GB on-demand card — 3.3× the 2-way eager baseline). Order of work: `roadmap.md`. Design source of truth: `03_EXPERIMENT_PLAN.md`.

**Fixed project title:** *The Boundaries of Evidence-Grounded Trust in Multi-Agent Scientific Debate, with a Controlled Benchmark for Sycophantic Consensus.*

**Premise:** the goal is 9+, but the standing instruction is *do not suggest things that will fail.* **Honest verdict:** 9+ is a low-probability option, not a plan. Secure the 8.3–8.6 core first, then attempt the 9+ layer as a call option; if the layer fails, the thesis still succeeds. The earlier score projections, probability tables and week-by-week schedule were 8 Nov 2026 judgments that duplicated `roadmap.md` and `03_EXPERIMENT_PLAN.md`; they are not repeated here.

## 1. What 9+ requires

A 9+ thesis is not "a better mechanism." It is **a new law + a new measurement + a surprising causal result**, at a scale a reviewer trusts.

| Layer | 8+ version | 9+ version |
|---|---|---|
| Theory | A threshold condition for 3 agents | A phase-transition law with sufficiency, necessity, a finite-sample bound, plus a dependence/adversarial extension |
| Method | Bounded trust update | Value-of-information verification with a near-optimality guarantee; risk-controlled abstention |
| Benchmark | 180-item SciClaimBench | 300–500 items, 3 domains, 5 conditions, verifier-quality labels, human-validated |
| Causal study | 2×2 with a few arms | 6-arm Full target + ceiling/granularity sweeps + mediation + claim-level vs document-level + evidence-supports-majority |
| Human eval | 60 Likert items | 150–200 binary judgments, 2 blinded annotators, κ/ICC, citation faithfulness |

The paper must answer a question the field did not know how to answer: *when does evidence-grounded trust work, when does it amplify conformity, and how many verified claims are needed?*

## 2. The 9+ stack

**Headline claim (derived hypothesis, not proved).** Evidence-grounded trust reduces sycophantic collapse only when verifier accuracy and coverage exceed a threshold \(q^\star\); below \(q^\star\), trust amplifies noise and can increase conformity. We derive \(q^\star\), check a finite-sample bound, and release a gold-evidence stress benchmark that measures the boundary.

1. **Theory (derived, proof check required):** a threshold law for a correct minority under a wrong majority, with claim dependence and adversarial evidence bias.
2. **Method (proposal):** value-of-information verification under a fixed budget with a submodular near-optimality guarantee; abstention when evidence is insufficient.
3. **Benchmark:** SciClaimBench-300, gold-evidence items across biomed, physics/chemistry, and math/CS, with five pressure/evidence conditions.
4. **Causal study:** the 6-arm Full target plus ceiling/granularity sweeps isolating evidence *information* from evidence *influence*. The 6-arm core alone is 8+, not 9+.
5. **Human evaluation:** 150–200 binary judgments of unwarranted switch and citation faithfulness.

## 3. Theory and math: derived, not proved

> **Proposal status.** These are derived sketches. No independent proof check has signed them. Do not present \(q^\star\), Theorem 1–3, or the finite-sample bound as proved until that check exists.

### 3.1 The model

- 3 agents, binary answer: one correct minority, two wrong majority.
- Each agent makes \(m\) claims.
- Verifier sensitivity/specificity \(q > 1/2\), coverage \(v\).
- Trust update \(S_i = \alpha V_i - \beta H_i\); softmax weight \(T_i \propto e^{S_i}\).
- Trust-weighted vote: correct if \(T_1 > T_2 + T_3\).

### 3.2 Theorem 1 — threshold law (independent claims)

The expected trust margin is

\[
\Delta = m(2q-1)(\alpha+\beta).
\]

The correct minority wins if \(m(2q-1)(\alpha+\beta) > \log 2\), so the threshold is

\[
q^\star = \frac{1}{2} + \frac{\log 2}{2m(\alpha+\beta)}.
\]

**Interpretation:** more verified claims lower the accuracy needed; stronger trust updates lower it; a 2-1 majority needs a log-2 margin. This is testable with a verdict-noise sweep.

### 3.3 Theorem 2 — claim dependence

With intra-class correlation \(\rho\), the effective sample size is

\[
m_{\text{eff}} = \frac{m}{1+(m-1)\rho},
\qquad
q^\star(\rho) = \frac{1}{2} + \frac{\log 2}{2m_{\text{eff}}(\alpha+\beta)}.
\]

**Interpretation:** redundant claims do not help; the trust signal saturates. This explains why verbose agents do not automatically gain trust, and it is a novel, testable prediction.

### 3.4 Theorem 3 — adversarial evidence bias

If the verifier has a bias \(b\) toward the majority (authority bias), the minority's effective accuracy is \(q-b\) and the majority's is \(q+b\). If

\[
b > q - \frac{1}{2} - \frac{\log 2}{2m(\alpha+\beta)},
\]

trust weighting **amplifies conformity**: evidence makes the wrong majority stronger. This is the "evidence can hurt" result, and it is 9+ material because it contradicts the field's assumption.

### 3.5 Finite-sample bound

To identify the correct minority with error \(\delta\),

\[
m \ge \frac{\log(1/\delta)}{2(q-1/2)^2}.
\]

This tells a practitioner how many verified claims are needed. It is a Hoeffding/Chernoff argument, not a deep minimax theory.

### 3.6 What not to attempt

- A general \(N\)-agent theorem with arbitrary claim dependence: too hard for 7–8 months.
- A distribution-free guarantee under arbitrary distribution shift: too hard and likely standard.
- A deep minimax lower bound for correlated claims: only with a math-heavy collaborator and supervisor.
- A theorem that assumes independent claims and ignores dependence: a reviewer will call it unrealistic.

**Minimum 9+ theory:** Theorem 1 + Theorem 2 + Theorem 3 + the finite-sample bound. That is 3–5 pages of proofs, tractable for a strong undergraduate with supervision.

### 3.7 The killer empirical result: the conformity trap

The strongest 9+ result is not "trust helps." It is **"evidence can hurt."**

- Manipulate the evidence so that it supports the **wrong majority** instead of the correct minority.
- If the verifier is biased toward the majority, trust weighting **amplifies the wrong majority**; accuracy falls below plain majority vote.
- Theorem 3 predicts the crossover; the experiment measures it.
- This is a direct response to **Authority Bias (NeurIPS 2026)**, which shows external source attribution can increase conformity.

**Prediction:** on items where the evidence supports the majority, B8 (trust) will be **worse** than B8-no-trust (majority), and the gap will grow with verifier accuracy. If confirmed, this is the 9+ headline.

## 3A. The stronger theory result: the double-counting phase boundary (derived, not proved)

> **Proposal status.** The \(\rho^\star\) boundary and the likelihood-ratio ceiling are derived claims awaiting an independent proof check. They are a research target, not a result.

The simple threshold in §3 is the pedagogical special case. The actual 9+ result is **claim double-counting**.

### 3A.1 Parameters

- \(q\): verifier accuracy; \(g = 2q-1\) (discrimination).
- \(\tau^+\): probability a true claim is verified supported; \(\tau^-\): probability a false claim is verified supported.
- \(d = \tau^+ - \tau^-\) (claim-truth separation); \(s = \tau^+ + \tau^-\) (claim mass).
- \(v\): coverage (fraction of claims with evidence).
- \(\rho\): claim overlap/dependence (the same proposition cited by multiple agents).
- \(N\): number of agents; \(k\): minority size; \(\pi = P(\text{majority correct})\); \(\delta\): confidence.

### 3A.2 The law

The number of **verified** claims needed is

\[
n^\star_{\text{verified}} = \Theta\!\left(\frac{s\log(N/\delta)}{g^2 d^2}\right),
\]

and the number of **emitted** claims is \(n^\star_{\text{emitted}} = n^\star_{\text{verified}}/[v(1-\rho)]\). Inverted, the verifier-accuracy threshold is

\[
q^\star = \frac{1}{2} + \frac{1}{2}\sqrt{\frac{s\log(N/\delta)}{n\,v\,d^2\,(1-\rho)}}.
\]

### 3A.3 The exact ceiling

Define the likelihood ratio

\[
D(q) = \frac{P(\text{favours minority}\mid H_1)}{P(\text{favours minority}\mid H_0)}.
\]

Trust weighting beats majority **iff** \(D(q) > \pi/(1-\pi)\). Below the ceiling, the expected accuracy of trust weighting is

\[
E[\mathrm{Acc}_{TW}] = \pi - \kappa(2\pi-1) < \pi,
\]

where \(\kappa = P(\text{weights favour the minority})\). \(D(q)\) is monotone in \(q\) by coupling, so \(q^\star\) is a unique root.

### 3A.4 The killer: double counting and \(\rho^\star\)

Each shared proposition contributes \((m_c - 1)\log \mathrm{LR}(V_c)\) of spurious log-odds, where \(m_c\) is the number of agents citing it. The critical overlap is

\[
\rho^\star = 1 - \frac{n^\star_{\text{verified}}}{n v}.
\]

**Above \(\rho^\star\), no verifier accuracy rescues the correct minority.** The failure is not verifier noise; it is **evidence redundancy**. More agents citing the same proposition make the wrong majority look more supported.

### 3A.5 Corollaries

- **Adversarial budget:** \(\varepsilon^\star = (q-q^\star)/(2q-1) \to 0\) at the ceiling.
- **Credulous bias:** a bias \(\beta\) shifts \(q^\star\) by exactly \(\beta/2\) and **reverses** the mechanism when \(\beta > 2q-1\).
- **Headroom:** \(\le 1-\pi\).

### 3A.6 Novelty ledger

| Result | Status |
|---|---|
| Softmax trust ≡ log-linear pool with Nitzan–Paroush weights (R1) | Known; use as grounding, do not claim |
| Identical claim sets ⇒ exactly majority (R2) | One-line degeneracy; useful sanity check |
| Exact likelihood-ratio ceiling (R4) | New in this application |
| Double counting and \(\rho^\star\) (R6) | **The killer result** |
| Chernoff–Stein sample complexity, design-effect dependence, naive-Bayes double counting | Known ingredients; the combination and the \(\rho^\star\) boundary are new |

**Minimum 9+ set:** R2 (degeneracy) + R4 (exact ceiling) + R6 (double counting/\(\rho^\star\)). R3/R5 are support, not the contribution.

### 3A.7 The empirical prediction

Measure \(\rho\) on real debates (fraction of claims shared across agents / evidence passages reused).

- **If \(\rho > 0.4\):** the \(\rho^\star\) boundary is the 9+ headline. Show that real multi-agent debates are **redundancy-bound**, not verifier-bound.
- **If \(\rho < 0.3\):** R6's punchline collapses; the thesis is a solid 8 (correct, well-verified, not surprising).
- **If \(\rho \approx 0.4\):** the result is a boundary condition; report it honestly.

**This is the single most important empirical measurement in the thesis. Start it early, not after the main runs.**

## 3B. The causal 9+ result: sign reversal and granularity moderator

The 9+ claim is not "trust helps." It is **"evidence can backfire, and the sign depends on attribution granularity."**

- **Below \(q^\star\):** calibrated trust **increases** wrong-majority conformity; accuracy falls below majority.
- **Above \(q^\star\):** trust reduces collapse.
- **Moderator:** document-level trust raises \(q^\star\); claim-level trust lowers it. This is the direct test of Verify, Then Argue: if claim-level attribution is epiphenomenal, document-level trust will match or beat it.
- **Mediator:** trust margin; selection vs persuasion; silent dissent.
- **Replication:** a second model family and a second domain.

**6-arm vs 9+ resolution:** the 6-arm matrix is the **8+ core** and is the Full run. The 9+ layer is **8 arms + the ceiling sweep (S3) + the granularity/backfire manipulation (S4) + mediation (S5) + replication (S6)** — not a different 6-arm count. Do not describe the 6-arm Full target as a 9+ design, and do not fold 9+ sweeps into the Full envelopes (1,280 GPU-h default; 1,440 alternate). The layer adds sweeps beyond those envelopes; it is not budgeted and is not part of the Core/Full plan. Pre-register the four primary contrasts and the three-way interaction **before** the main runs.

**Why this is 9+:** it predicts a **sign reversal** that no current paper reports.

## 4. Method: SEA-Cert (proposal, not proved)

> **Proposal status.** SEA-Cert is a design proposal; its theorems are derived sketches, not proved. It is not part of Core v1.0 and is not funded.

**Do not use conformal trust calibration (CTC).** It is preempted by Wang et al., *Conformal Social Choice for Safe Multi-Agent Deliberation* (EMNLP 2026 SAC Highlight), and its coverage guarantee is invariant to the trust weights: calibrating weights cannot improve validity, only set size.

**Idea.** The deployment question is not "does the answer have coverage?" but "what is the error rate among the claims we act on?" Let \(S\) be the **shared-error event** (all agents inherit the same wrong premise), \(\rho=P(S=1)\), and let the verifier accept with \(a_1=P(V=\text{accept}\mid S=1)\), \(a_0=P(V=\text{accept}\mid S=0)\).

- **Flat risk–coverage curve.** If \(V\perp S\), selective risk \(\mathrm{SR}(t)=P(Y=\text{wrong}\mid V=\text{accept})=\rho\) at every threshold. If real debates have \(\rho\approx0.2\)–\(0.3\), no independent verifier can certify a 5% error rate.
- **Phase transition.** Certifying \(\mathrm{SR}\le\beta\) at acceptance \(\ge s\) with an \(S\)-independent verifier is possible **iff \(\beta\ge\rho\)**. Below that the verifier must be negatively associated with \(S\): \(a_1/a_0\le r^\star(\beta,\rho)=\beta(1-\rho)/[\rho(1-\beta)]\).
- **Non-identification.** Marginal ROC does not identify \((a_1,a_0)\) or \(\mathrm{SR}\). Verifier accuracy is the wrong statistic; the \(S\)-conditional likelihood ratio is the right one.
- **Cluster design effect.** With intra-cluster correlation \(\rho_{\text{ICC}}\) and mean cluster size \(\bar m\), \(\mathrm{DE}=1+(\bar m-1)\rho_{\text{ICC}}\); a claim-level audit is anti-conservative by \(\sqrt{\mathrm{DE}}\). Optimal design: audit breadth, not depth.

**Algorithm.** Sample \(G_{\text{audit}}\) claim clusters and audit claims against human gold; estimate \(\hat\rho\), \(\widehat{\text{ICC}}\), \(\widehat{\text{DE}}\); for each threshold on a grid, compute a Clopper–Pearson FDP upper bound and an acceptance lower bound; choose the threshold maximizing certified acceptance subject to FDP \(\le\beta\); if none is feasible, return `CANNOT_CERTIFY`. The guarantee is a PAC-style bound on the realized false-discovery proportion of the accepted set, cluster-robust — not a marginal coverage statement. CTC is demoted to an estimator inside SEA-Cert.

**Experiments (only if the layer is attempted):** flat-curve test; matched-accuracy verifier pairs; phase transition around \(\hat\rho\); verifier sweep (55–95% accuracy × no/retrieved/oracle/adversarial evidence); cluster effect on SciFact/ExpertQA; frontier recovery against CSC, Dai, TRAQ, Conformal-RAG, R²-MAD, TERA-RAG. Feasibility: 1,500–2,000 audited claims, 5–6 weeks with 2 annotators; agents prepare packets, humans adjudicate a stratified sample.

## 5. Benchmark: SciClaimBench-300

### 5.1 Size

- **24 items = calibration batch** (start here).
- **180 items = v1.2 benchmark-freeze floor** (~410 h annotation). It is **not** in the Core v1.0 matrix.
- **300 items = Full target**; **600 = stretch**; **800 + SDT model + private split = no-go**.
- **800-item design (do not build):** 4 domains × 200 (physics, chemistry/materials, biology/medicine, CS/ML); 120 dev / 480 public test / 200 private.
- Each item: question, gold answer, 3 positions (1 correct minority, 2 wrong majority), 3–6 atomic claims per position, gold evidence, gold verdicts, controls.
- **2–3 dedicated annotators; ~1,824 h for 800 items; κ ≥0.75.** Do not build 800 with agents alone.

### 5.2 Controls (14)

No pressure, neutral restatement, peer pressure, authority pressure, emotional escalation, evidence placebo, evidence-supports-minority, evidence-supports-majority, ambiguous evidence, evidence shuffle, label/position shuffle, majority-correct items, verifier-quality sweep, no-verifier ablation. The minimum essential set is 11 of 14; do not drop majority-correct, placebo, E−, or label shuffle.

### 5.3 The SDT measurement model (proposal, not validated)

\[
z = w_e e + w_s s_{\text{maj}} + w_v v + b + \epsilon
\]

- \(e\) = evidence valence; \(s_{\text{maj}}\) = social signal; \(v\) = verifier signal.
- **Sycophancy** \(= w_s/w_e\); **verifier trust** \(= w_v\); **abstention criterion** \(= \lambda\); **competence** \(= d'\).
- Report a 6-axis profile: resistance, correction, deference, attribution, abstention, robustness.
- **Headline figure: the trust plane** (resistance vs deference) — calibrated, sycophantic, contrarian, incoherent.

This turns SciClaimBench from a scoreboard into a measurement instrument. Without it, 800 items is a dataset paper; with it, it is a 9+ benchmark.

### 5.4 Release

- Original items: CC BY 4.0; code: MIT.
- GPQA/HLE/BrokenMath-derived items: IDs/hashes only, not text.
- Leaderboard: majority, MAD, RAG-MAD, DebUnc, ConsensAgent, iMAD, MoA, R²-MAD-style, TERA-RAG-style, trust-calibrated.

## 6. Causal study

### 6.1 Arms

**Core v1.0** uses the first four rows. **B8-placebo and B8-oracle are the Full target, pending WP-18**; the Full default is 32 rows with a gold-evidence oracle on SciClaimBench, and 36 rows with gold-answer trust is the alternate.

| Arm | Evidence | Aggregation | Purpose |
|---|---|---|---|
| B3 | none | majority | Vanilla MAD |
| B4-matched | retrieved | majority | Evidence-information control |
| B8-no-trust | retrieved | majority | **Primary control** |
| B8 | retrieved | trust | Treatment |
| B8-placebo | shuffled verdicts | trust | Evidence calibration vs any reweighting |
| B8-oracle | gold evidence or gold-answer trust | trust | Verifier upper bound; definition frozen by WP-18 |

### 6.2 Add-ons

- Claim-level vs document-level vs label-shuffled trust (response to Verify, Then Argue).
- Evidence-supports-majority (response to Authority Bias).
- Natural divergence (no injection); homogeneous vs heterogeneous panel; K=1 vs K=3.

### 6.3 Primary endpoints

- Final-answer accuracy (primary); CMR, correct-minority retention (co-primary).
- Trust AUROC / Brier and ARR (secondary).
- Sample size and MDE: `03_EXPERIMENT_PLAN.md` §5. Core v1.0 plans 400 GPQA-Main + 400 MMLU-Pro + 200 HLE per condition; HLE is a control, not a powered primary.

## 7. Bottom line

- **9+ is not the rational target; 8.5 is.** The 9+ layer is a call option, not the plan.
- **The one 9+ path that can work:** a derived threshold law + claim-dependence/adversarial extensions + a 180-item v1.2 benchmark (300 Full target) + the 4-arm Core / 6-arm Full causal study + a value-of-information method, all subject to an independent proof check.
- **The one thing that will kill the thesis:** trying to do all of it before securing the 8.3 core.
- **The right order:** fix the instrument → run the causal study → build the benchmark → add the theory → add the method.
- **The 9+ thesis is a portfolio; the 9+ paper is a hit.** Build the portfolio first.

**Budget:** see `08_COMPUTE_COST.md` for the measured throughput, the remaining-programme table and the caps. Do not quote retired spot rates.

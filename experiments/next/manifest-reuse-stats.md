# Manifest reuse: when may partial rows be pooled across code versions?

**Status:** design note, 20 Nov 2026. No code change, no run, no commit.
**Scope:** the confirmatory endpoints — final-answer accuracy, CMR (Correct-Minority Retention), trust AUROC/Brier — in the pre-registered Core/Full matrix (`PRE_REGISTRATION.md` v1.0 + v1.1/v1.4 errata).
**Bottom line:** the manifest hash is a reproducibility contract, not an obstacle. A hash change is a classification event. Class C (sample) and D (intervention) never pool. Class B (evidence path) pools only after a pre-specified process bridge and, where the outcome bridge is feasible, that bridge too; if the outcome bridge is not feasible, no pool. A 5-question answer-agreement check is not evidence of equivalence. Class A (timing-only) pools with an input-hash attestation. The two rows abandoned today should be rerun, not pooled: the rerun costs ~3.7 GPU-h (~$0.5–$3.0), under 1% of the $600 envelope.

## 1. What pooling must preserve

A pooled estimate is valid only if it estimates one target parameter. Here the target is the paired B8 − B8-no-trust contrast on pressure-eligible questions (§4.1–4.2, §10), with pairing key `(dataset, question_id, seed)` and the same option permutation (§6.1). Pooling across versions is valid only if:

1. **Same population** — the sampled question set and inclusion criteria are unchanged.
2. **Same intervention** — prompts, models, decoding, verifier, and trust configuration are unchanged; a parser/gold/metric fix may be replayed on stored outputs (see below).
3. **Same evidence regime** — the distribution of retrieved evidence is equivalent within a pre-specified margin, or the endpoint is invariant to it.
4. **Same pairing and assignment** — version is a stratum in the analysis, the round-0 panel that defines pressure eligibility is unchanged for CMR, and version assignment is not confounded with question order (a v1 prefix plus a v2 suffix is not poolable without a bridge).
5. **Pre-specified rule** — the pooling decision and primary estimate are fixed before unblinding; no outcome-dependent exclusion or "best stratum" selection.

Classes C and D fail conditions 1 and 2 outright. Class B puts condition 3 at risk. Class A is the only class that can satisfy all five without a new run, and only if "timing-only" is verified at the level of request bytes, not asserted.

## 2. The four change classes

| Class | What changed | Accuracy | CMR | Trust AUROC/Brier | Pool? |
|---|---|---|---|---|---|
| **A. Timing-only** | logging, type hints, order-preserving thread scheduling with identical request bytes, retry delays that do not change returned passages | exchangeable if prompt/evidence/question hashes match; analyse version-stratified | only if the round-0 panel hash matches | only if the evidence-availability rate matches | **Yes, with attestation** |
| **B. Evidence-affecting** | timeouts, concurrency, per-source locks, caching, retry policy, rate-limit handling, live index changes | only after the process bridge and an interaction CI inside the margin | same, plus evidence-availability strata | per-stratum only if the `abstained_no_evidence` rate matches; otherwise no pool | **Conditional** |
| **C. Sample-affecting** | loader/filter/dedup/cap/sampling-seed/revision changes that change which questions are drawn | no | no | no | **Never** |
| **D. Intervention-affecting** | prompt text, model revision/quant, decoding, parser/verifier logic that changes verdicts or trust | no | no | no | **Never** |

**Replayable exception (not pooling).** A pure post-processing fix — parser, gold mapping, metric definition — that does not change what the models saw can be applied to stored raw answers and evidence. Re-score both versions with the new code and treat the result as one analysis version; archive the old scores. This is an analysis-time re-score, not a resume: the run directory's condition hash still refuses the changed parser. Valid only when raw outputs and prompt/option bytes are stored (they are, schema v2). Does not apply to retrieval, prompts, models, decoding, or the question set.

**Hash caveat, three ways.** The manifest hashes the code commit, so a committed comment-only change also changes the hash; a hash change is not proof that a result-affecting input changed. Conversely, a hash match is not proof of identical execution: the serial run and both parallel runs below share hash `6a6ea0e4…` and code commit `306022e`, while the parallel/retrieval work was uncommitted on top of that commit, and `TRUSTCAL_SERIAL` is a runtime switch. The manifest also does **not** hash live retrieval responses: two runs with the same hash can still see different passages (observed below). Classify by the result-path diff, and audit the evidence; neither alone is sufficient.

**Endpoint asymmetry.** CMR is the most fragile: its denominator is the pressure-eligible set defined by the round-0 panel, so a change that alters round-0 answers changes the analysis set even when the question ids match. Trust AUROC/Brier are next: they exist only where the trust path has evidence, so a change in evidence availability changes both the scores and the denominator. Accuracy is the most robust but still not immune: it can be unchanged while CMR and the trust endpoints fail, as the worked example shows.

## 3. Quantifying the risk

The pooling-validity test is not "are the final answers the same?" It is the version × arm interaction on the paired binary endpoint. With `D_{i,v} = Y_{i,B8,v} − Y_{i,C,v}`, `θ_v = E[D_{i,v}]`, the interaction is `Δ = θ_2 − θ_1`. Running both versions on the same n questions gives `δ_i = D_{i,2} − D_{i,1}` and

`SE(Δ̂) = sqrt(2 π_d (1 − ρ) / n)`,

where `π_d` is the paired discordance rate and `ρ` is the cross-version correlation. For a TOST equivalence margin `m` (two one-sided tests at α = 0.05, i.e. a 90% CI), 80% power, and a true difference of zero:

`n ≈ 6.18 × 2 π_d (1 − ρ) / m²`.

Use the larger `π_d` if the two versions differ. `n` is the number of questions run under **both** versions; the record count is `4n` across both arms (`2n` per arm).

At `π_d = 0.20` (the project's planning value, §5):

| margin m | ρ = 0 | ρ = 0.5 | ρ = 0.8 |
|---:|---:|---:|---:|
| 7.5 pp | 440 | 220 | 88 |
| 5 pp | 989 | 494 | 198 |
| 3 pp | 2,747 | 1,373 | 549 |

At `π_d = 0.15` multiply by 0.75; at 0.25 by 1.25. The interaction MDE at n = 400 is 8.9 / 6.3 / 4.0 pp for ρ = 0 / 0.5 / 0.8 (two-sided α = 0.05), and 10.6 / 7.5 / 4.7 pp under the 4-test Holm adjustment (α = 0.0125). A 5 pp TOST margin at n = 400 therefore requires ρ ≳ 0.6; at ρ = 0.5 the bridge needs ~494 questions, at ρ = 0 ~989. The 5-question check has 5/494 ≈ 1% of the ρ = 0.5 requirement. The 5 pp figure is the project's SESOI and non-inferiority margin (§4.3, §7); smaller margins are not resolvable at the planned n.

For a **single** paired difference of 5 pp at `π_d = 0.20` (variance `π_d`, not the `2π_d` interaction variance), the formula with 7.85 gives ~630 paired questions; under the Holm-adjusted α = 0.0125, ~890. Either is larger than the 400-question cap.

**Rare-event arithmetic.** If evidence loss affects a fraction `q` of questions and changes the arm contrast by `δ_e` on those questions, the expected interaction is `q δ_e`. A 10% loss rate with a 10 pp effect gives a 1 pp interaction; detecting 1 pp at `π_d = 0.20` with a two-sided α = 0.05 test needs `n ≈ 7.85 × 0.20 / 0.01² ≈ 15,700` paired questions, 39× the GPQA cap. A 20% loss rate with a 10 pp effect (2 pp) still needs ~3,900. **Outcome tests cannot reliably catch rare load-induced evidence loss; process monitoring must.**

**Why 5 is not an equivalence test.** Four of five identical final answers is a disagreement rate of 20% with a 95% Wilson CI of [3.6%, 62.4%]. Even 5/5 agreement only bounds the disagreement rate at <45% (rule of three). To bound it at <5% with 95% confidence requires zero disagreements in 59 questions; at <1%, zero in 299. The observed same-manifest rerun agreed on only 3/5 final answers, with an evidence-set Jaccard of 0.25–0.74. The code-change disagreement (1/5) is not distinguishable from the same-manifest disagreement (2/5) at n = 5: the Wilson CIs overlap substantially. The paired B8-vs-control 5-question run had one discordant pair (B8 correct, control wrong): +20 pp, π̂_d = 0.20 (consistent with the planning value, but the CI is wide), exact McNemar p = 1.0, 95% CI ≈ [−15, +55] pp. At n = 5 the paired design cannot resolve the primary contrast, let alone a version interaction. The single serial/parallel divergence is consistent with sampling noise, but n = 5 cannot separate sampling from evidence.

## 4. Decision rule (operator)

**Step 0 — classify before running.** Diff the result path and record four booleans: prompt bytes changed? retrieval query/result path changed? question set/permutation changed? model/decoding/parser/verifier changed? Classify by the most severe true boolean: **C or D if either is true; otherwise B if retrieval changed; otherwise A.** Record the class and hashes in the run manifest.

**Class A — pool with an attestation.** Require: (i) a signed statement that the change is outside the result path; (ii) matching prompt, question, option-permutation, retrieval-query, and retrieved-passage hashes (or a pinned retrieval snapshot) for the overlapping records; (iii) a matching round-0 panel hash for CMR, or a version-stratified CMR analysis. No outcome bridge. If the round-0 panel differs, pool accuracy only; analyse CMR per version.

**Mid-row adoption.** A v1 prefix plus a v2 suffix confounds version with question order; do not pool for the confirmatory estimate without randomization or a bridge that shows no order effect, even for class A.

**Class B — process bridge, then a held-out outcome bridge.** On at least 50 randomly selected overlap questions (or all, if fewer), replay the **same stored claims/queries** through the v1 and v2 retrieval layers (a unit-level replay, not a fresh debate), and compare the returned passage sets. This isolates the retrieval change from claim drift. Require zero evidence-loss events (a v1 passage missing for the same query), no dead sources, and no query with a positive v1 count below 80% of that count. Zero events in 50 bounds the event rate at <6.0% (95%); zero in 100 at <3.0%. A nonzero event rate requires a root-cause fix and a new audit; do not pool on the first pass. If the process bridge passes, run the outcome bridge on a **held-out** sample (a separate dataset, or a pre-reserved subset excluded from the primary estimate), not the confirmatory questions, to avoid an interim look at the primary contrast (§8.2). Size it from the table; require the 90% CI of the interaction within ±5 pp. If the required n exceeds the available held-out sample, **do not pool; rerun the row.**

**Class C — never pool.** Rerun the full sample under the new manifest. Report the old row as missing with its hash and reason (§8.3: failed rows are reported, not replaced). A nested-intersection analysis is allowed only as a pre-specified secondary sensitivity analysis, never as the primary.

**Class D — never pool.** Treat as a new intervention version; a new pre-registration version is required if it touches a confirmatory endpoint. The replayable post-processing exception is the only reuse path.

**Row-level, not question-level.** A process failure excludes the whole row and is reported; it never justifies dropping individual questions after seeing outcomes. This is the pre-registration principle: no outcome-dependent exclusions (§6.4, §8.3).

## 5. Reporting a mixed-provenance row

Report every stratum, the pooled estimate, and the sensitivity analyses; the primary is fixed by the bridge result, not by which number looks better. Template (one row per manifest hash):

| stratum | hash | commit | class | n | accuracy RD (95% CI) | CMR RD | AUROC (n) | Brier (n) |
|---|---|---|---:|---:|---|---:|---:|---:|

**Primary, pre-specified.** If both the process and outcome bridges passed, the **version-stratified pooled estimate** is primary: a weighted average of stratum-specific paired differences on the common question set, with weights fixed in advance (e.g., proportional to the pre-registered question allocation), and a version-stratified bootstrap CI. If either bridge failed or was not run, the **largest homogeneous stratum** is primary (ties broken by the pre-registered version order), and the pooled estimate is a labelled sensitivity analysis.

**Sensitivity.** Largest stratum alone; leave-one-stratum-out; pooled vs stratified; worst-case bounds for missing/abandoned records; the same-manifest answer-agreement noise floor. Report all of them, not a selected subset.

**Trust endpoints.** Report AUROC and Brier per stratum with denominators and the fraction of `abstained_no_evidence` records. Do not concatenate scores across strata into one ROC: pooled AUROC is not the sample-size-weighted average of stratum AUROCs, and it can fall outside their range under a different case mix (Simpson). If a pooled number is required, define it as `Σ w_h AUROC_h` with fixed weights and a stratified bootstrap. Pooled Brier is `Σ w_h Brier_h` for the mixture; label it as a mixture, not as either version's Brier. If the evidence-availability rate differs by more than a pre-specified tolerance (e.g., 5 pp), do not pool the trust endpoints at all.

## 6. Never pool

**Class C (sample set) — never.** The question set defines the target population and the pairing. A loader/filter/dedup/cap/seed change re-draws the sample, changes inclusion probabilities, and can change the pressure-eligible denominator. A pooled accuracy or CMR across different samples estimates an average over a mixture of sampling frames, not the pre-registered estimand. Even if the first 25 ids happen to match, the inclusion probabilities and the remaining 375 do not.

**Class D (prompt/model/decoding) — never.** The intervention is different. A prompt change to both arms is a new treatment version; a model revision changes the agents; a decoding change changes the outcome distribution. Pooling gives a mixture of two interventions and can bias the contrast in either direction. §8.4 already requires a new version and a new config hash for any such change. A "small" prompt edit is not small at temperature 0.7.

**Class B is conditional, not free.** It may be pooled only after the process bridge and, where feasible, the held-out outcome bridge. If the bridge is not run, the default is no pooling. A non-significant interaction is not equivalence; the CI must fall inside the margin.

## 7. Worked example (this project)

**Timing.** Same 5 GPQA questions, B8, seed 1: serial mean 195.0 s/debate; parallel mean 127.7 s/debate (1.53× faster, 67.3 s saved). Per 400-question row: 7.5 GPU-h; 24 Core rows: ~180 GPU-h (~$24 at $0.136/h, ~$60 at $0.336/h, ~$144 at $0.80/h). The saving is real but modest; it does not justify a credibility risk.

**Equivalence.** All three runs share manifest hash `6a6ea0e4…` and code commit `306022e`; the parallel/retrieval changes were uncommitted. Serial vs parallel (pre-fix): 5/5 final answers identical, but `gpqa-0002` fetched 3 passages instead of 27 (the commit's note records 3 of 9 in that round) and two agents abstained for no evidence. Serial vs parallel (post-fix): 4/5 identical; `gpqa-0002` had **zero** passages and all three agents abstained (`abstained_no_evidence`); `gpqa-0004` changed D→C, both wrong. Serial vs serial (same manifest hash, rerun): 3/5 identical. The 4/5 and 5/5 answer agreements are therefore not distinguishable from the same-manifest rerun at n = 5, while the trust mechanism was degraded in both parallel runs. Accuracy agreement hides a mechanism failure that would bias AUROC/Brier and make the trust endpoints unestimable on the affected item.

**Abandoned rows.** Two rows (B8 and B8-no-trust), 25 valid pairs of 27 planned; 50–52 pairs, 100–104 debates. They are prefixes (questions 0–26); the remaining ~375 are not exchangeable with that prefix, so a v1-prefix + v2-suffix pool would confound version with question order. The local snapshots of these rows contain 26 parseable records each, 2 unparseable physical lines, and 2–3 records whose gold is not among the options (`gpqa_main-0008/0019/0024`). The loader change is class C where it drops and re-draws rows; its gold-mapping part is replayable only if a sample lock proves the 25 pairs' ids and content are unchanged. The retrieval-lock change is class B. With the current evidence (sample shift plus an unvalidated retrieval change), neither row is poolable. Rerun cost: 3.5–3.7 h at 128 s (≈$0.5–$3.0), ≤0.5% of the $600 envelope. **Rerun.**

**What to do.** Fix and validate the retrieval path first: a 50-question process audit with zero evidence-loss events and no `abstained_no_evidence` on serial-vs-parallel. If it passes, use parallel for non-confirmatory runs; for the confirmatory Core row, either run one version throughout or fund a held-out bridge sized from the table. Given the current evidence, run the Core row serial (or one fixed version) and keep the parallel path for the pilot. The 5-question check cannot license reuse.

## 8. Recommendations

1. Add a manifest-level refusal in the analyzer for mixed hashes (defense in depth; `runner.py` already refuses resume, but `analyze.py --allow-pool` can pool arms).
2. Store a `round0_hash`, an `evidence_hash`, a `trust_availability` count, a `retrieval_version`, and per-claim query hashes; these are the fields the process bridge needs and they are not currently first-class.
3. Adopt the sample lock in `manifest-reuse-design.md` as the structural fix for class C; this memo's rule is the statistical gate on top of it. Pre-register the bridge rule (class definitions, 50-question process audit, 5 pp margin, held-out sample) before the next code change, so the decision is not made after seeing outcomes.
4. Default to rerun for classes B/C/D. The rerun is cheap; a mixed-provenance confirmatory row is a credibility problem that no sensitivity analysis fully repairs.

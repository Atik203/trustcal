# Report Status — Full Project Report

**Updated:** 9 November 2026 · **Base:** `main` = `dev` = `bacc59c` (P0 release `7f2c11f`; tags `p0-gate`, `p0-release`).

## What changed

- **`0.0.title.tex`** — the cover now uses the exact paper title only, *The Boundaries of Evidence-Grounded Trust in Multi-Agent Scientific Debate, with a Controlled Benchmark for Sycophantic Consensus*. No registered-title or cover note is included.
- **`0.1.abstract.tex`** — rewritten as an FYDP~II abstract. States 523 current tests (514 at the P0 release), the 13/13 gate, and Gate 0 only; says explicitly that no efficacy result is reported.
- **`1.intro.tex`** — corrected the 25.5% statistic and its denominator; removed "eliminate"; replaced the per-agent-confidence sentence with the external-evidence contrast; corrected the trust bound to the simplex projection; limited "tested" to the ten-question Gate 0 slice; removed the meta opening paragraph.
- **`2.back.tex`** — corrected the iMAD characterisation; replaced the false "none of the prior studies" absolute with a scoped gap; replaced the "existing research does not contain" absolute with "we are not aware"; updated the metric list to the current endpoints.
- **`3.design.tex`** — rewritten to the university structure: 3.1 Requirement Analysis with the four required subsections, 3.2 Detailed Methodology and Design, 3.3 Project Plan, 3.4 Task Allocation, and 3.5 Summary. Detailed components use unnumbered paragraph headings so the table of contents stays clean. The FYDP~I ten-month plan was replaced with the current November 2026--December 2027 plan, the 24-run Core and 36/32-run Full targets, and the 24--180--300 benchmark ladder.
- **`4.implementation.tex`** — rewritten as **Implementation and Results** with the fixed main sections 4.1 Environment Setup, 4.2 Testing and Evaluation, 4.3 Results and Discussion, and 4.4 Summary. It records the environment, implementation architecture, P0 hardening, 523-test suite, P0 gate, Gate 0, evaluation protocol, engineering results, projected efficacy values, discussion, and threats to validity.
- **`5.sic.tex`** — corrected the Python version, FP8/PagedAttention wording, BM25/cross-encoder wording, and RAG expansion; filled the empty constraint subsections; replaced the 300-hour/340--820 budget with the 1,067--1,280 GPU-h matrix and the v1.3 4-bit/80 GB envelope (Core USD 175--210; Full target USD 210; total USD 500--600; hard stop USD 600 — that envelope is historical, superseded by the **$300 project hard stop** of 24 Nov 2026); fixed "seven attributes" to "six of seven, P6 not covered"; removed "incremental level of innovation"; removed the "energy usage very-low" claim; reconciled the six program outcomes.
- **`6.conclusion.tex`** — removed the separate "What Was and Was Not Shown" section. The summary now states the engineering-only boundary, and the limitations and future-work sections remain.
- **`CLAIMS_AUDIT.md`** — mode/rung, old-to-new table, claim-evidence map, removed/narrowed claims, figure changes, unresolved items, compile result.

## Current numbers used

- **615 passing tests** in the current suite; **514 at the P0 release** (`experiments/p0/WAVE2.md`).
- **P0 gate: 13 of 13 passed, 0 failed, 0 pending** (`p0_gate.py` strict run, 2026-11-09).
- **Matrix: 24 rows** (4 arms × 3 datasets × 2 seeds), **1,280 GPU-h** conservative gate / **1,067 GPU-h** plan. Measured throughput (24 Nov 2026) is **172.7 debates/h at $1.50/GPU-h all-in**, so the 8,000 Core debates are ~46 GPU-h and Core + Full is ~69.5 GPU-h ≈ USD 104; the 1,280 GPU-h figure is a cap, not a forecast.
- **Gate 0: 10/10 debates, 90/90 positions, 370.8 s mean**, 21.5 s stdev, approximately USD 4.29.
- **4-bit matrix stack:** 53.3GB pinned weights (Qwen3.8 AWQ, Gemma AWQ, Mistral AWQ); 80GB A100 offline check passes.
- **Final stack:** 73.68GB pinned weights (Qwen3.8 FP8, Gemma FP8, Mistral AWQ); 96 GB serving smoke passed 20 Nov 2026; FP8 precision replication not run.
- **B7:** optional appendix ceiling, three GPT-6 Luna samples per question; not in Core/Full.
- **Report:** 70 pages, 80 cited works, 0 errors/undefined refs; 12 overfull and 118 underfull boxes.

## Figure status

`fig-pipeline.png`, `fig-context.png`, and `fig-dataflow.png` were present and compiled. Their captions and surrounding text were updated to the current mechanism: seeded option shuffle, claim-domain routing, verifier labels, logit → softmax → simplex projection, one-shot injection, and `trust_for_positions`.

The PNG files were **not edited or regenerated** here. The figure agent is producing 600+ DPI replacements. The new captions were written for the current mechanism, but the PNG content was not visually checked against them. If a regenerated figure does not show those elements, update the caption or the figure.

## Compile

Explicit pdfLaTeX sequence from `FYDP_Summer/`, matching Overleaf:

```
pdflatex -interaction=nonstopmode -halt-on-error fydp.tex
bibtex fydp
pdflatex -interaction=nonstopmode -halt-on-error fydp.tex
pdflatex -interaction=nonstopmode -halt-on-error fydp.tex
```

Engine: pdfTeX 3.141592653-2.6-1.40.29 (TeX Live 2026). Each pdfLaTeX pass exited 0; BibTeX exited 0. **70 pages, 80 cited works, 0 errors, 0 undefined references, 0 undefined citations, 0 missing figures.** 12 overfull boxes and 118 underfull boxes, mostly in long table/paragraph lines and narrow table cells.

## Remaining placeholders / actions

- `LICENSE` (MIT) is present at the repository root; the reproducibility section cites it.
- The current suite records 615 passing tests (514 at the P0 release); re-run `pytest` only if the code changes.
- **Historical note (retired):** the RTX A6000 USD 0.263/hour figure is superseded, as are the 80 GB A100 at USD 0.136/GPU-h and the 96 GB FP8 rate of USD 0.336/GPU-h. The measured path is a 96 GB card at **USD 1.50/GPU-h all-in** (172.7 debates/h), so Core + Full ≈ 69.5 GPU-h ≈ **USD 104**. `docs/agent/08_COMPUTE_COST.md` still carries the dated 9 Nov spot table, and `5.sic.tex` still carries the USD 175--210 / 210 / 500--600 figures; both need a reconciliation pass.
- Run `smoke_test.py --phase final` on the 96GB stack.
- Complete the 150--200-pair verifier human audit.
- Complete the 24-item calibration batch and freeze the SciClaimBench 180-item Core floor / 300-item Full target.
- Complete the WP-18 placebo/oracle slice; the Core matrix remains four arms until it lands.
- The runner record adapter is wired; check a sample record for `manifest_hash`, `final_answer`, and the trust fields before the paid run.
- Check the regenerated 600+ DPI figures against the new captions.

## 2026-11-21 — core3 first Core row COMPLETE (399+399 debates)

`experiments/core3` (`gpqa_main` seed 1, B8 vs B8-no-trust, fourbit stack) is
complete: 399 debates/arm (q27 quarantined of 400), 798 total; both runners
exited cleanly, summaries written 2026-11-21T07:29Z (B8) / 07:42Z (control).
Final: B8 acc 0.6241 (249/399, CI 0.576–0.672) vs control 0.5865 (234/399,
CI 0.536–0.634); paired both 208 / B8-only 41 / ctl-only 26 / neither 124;
exact McNemar p = 0.086 (not significant); MPR 0.78/0.75; ARR 0.657/0.702;
CCR-e 0.102/0.150; trust AUROC 0.518, Brier 0.292; 15.3 GPU-h, mean pair
138 s. Host 61635389 (96 GB S, $1.59/h) STOPPED, not destroyed (warm fallback
~$0.71/day); credit left $2.67; row spend ~$17–19.

What the `.tex` now contains: the report `.tex` files above are unchanged
since 9 Nov (still the engineering report, no efficacy claims). The completed
row is recorded in `docs/supervisor_report/`: `core_auto.tex` holds the final
400-pair milestone table (798 debates, paired counts, McNemar p = 0.086,
milestones 100/150/200/250/300/350/400-final merged) and the B8-conditions
definitions paragraph (PR #19); `core_limits.tex` holds the reading guide and
limits text. Merged to main as PR #20 = `c55903b`.

Next (in order): post-400 speed A/Bs (`experiments/next/post-400-speed-cost.md`,
now READY), then v1.5 + `sciclaim_180` loader, then Full.

## Stage naming

The report uses the glossary names: **Core run** (legacy "C+") and **Full run** (legacy "TACL full"). "TACL" is not used as a stage name. No "C+" or "TACL full" remains in the report prose or tables.

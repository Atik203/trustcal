export interface KpiCard {
  value: string;
  label: string;
  variant?: 'default' | 'green' | 'amber' | 'rose' | 'sky';
}

export interface CoverItem {
  label: string;
  value: string;
  href?: string;
}

export interface GanttPhase {
  name: string;
  duration: string;
  deliverables: string;
  progress: number;
  barVariant?: 'default' | 'teal' | 'amber' | 'rose';
}

export interface TimelineItem {
  milestone: string;
  date: string;
  description: string;
  deliverable: string;
}

export interface ResourceCard {
  label: string;
  value: string;
  sub: string;
  href?: string;
}

export interface RiskRow {
  risk: string;
  likelihood: string;
  likelihoodVariant: 'green' | 'amber' | 'rose';
  impact: string;
  impactVariant: 'green' | 'amber' | 'rose';
  mitigation: string;
}

// Completed Core row — GPQA-Main seed 1, B8 (trust) vs B8-no-trust
// (majority). Single source of truth for the finished row; pages and
// slides render from this, so the numbers stay consistent.
export interface CoreRowResult {
  dataset: string;
  seed: number;
  debatesPerArm: number;
  totalDebates: number;
  quarantined: string;
  b8Accuracy: string;
  b8Correct: number;
  b8CiLow: number;
  b8CiHigh: number;
  controlAccuracy: string;
  controlCorrect: number;
  controlCiLow: number;
  controlCiHigh: number;
  pairedBoth: number;
  pairedB8Only: number;
  pairedControlOnly: number;
  pairedNeither: number;
  mcnemarP: number;
  mprB8: number;
  mprControl: number;
  arrB8: number;
  arrControl: number;
  ccrB8: number;
  ccrControl: number;
  gpuHours: number;
  meanPairSeconds: number;
  milestones: string;
}

export const coreRowResult: CoreRowResult = {
  dataset: 'GPQA-Main',
  seed: 1,
  debatesPerArm: 399,
  totalDebates: 798,
  quarantined: 'q27 (options are literal letters)',
  b8Accuracy: '62.4%',
  b8Correct: 249,
  b8CiLow: 57.6,
  b8CiHigh: 67.2,
  controlAccuracy: '58.7%',
  controlCorrect: 234,
  controlCiLow: 53.6,
  controlCiHigh: 63.4,
  pairedBoth: 208,
  pairedB8Only: 41,
  pairedControlOnly: 26,
  pairedNeither: 124,
  mcnemarP: 0.086,
  mprB8: 0.78,
  mprControl: 0.75,
  arrB8: 0.66,
  arrControl: 0.70,
  ccrB8: 0.10,
  ccrControl: 0.15,
  gpuHours: 15.3,
  meanPairSeconds: 138,
  milestones: '100 / 150 / 200 / 250 / 300 / 350 / 400 (final)',
};

// Short honest summary: feasibility + timing demonstrated, no efficacy claim
// (exact McNemar p = 0.086, not significant; CIs overlap).
export const coreRowSummary =
  'Row 2/24 (GPQA-Main seed 1, B8 vs B8-no-trust) complete Nov 2026: 798 debates ' +
  '(399/arm, q27 quarantined). Accuracy 62.4% (249/399, 95% CI 57.6–67.2) vs 58.7% ' +
  '(234/399, CI 53.6–63.4); paired 208/41/26/124, exact McNemar p = 0.086 (n.s.). ' +
  'MPR 0.78/0.75, ARR 0.66/0.70, CCR-e 0.10/0.15, ~15.3 GPU-h, mean pair 138 s. ' +
  'Feasibility + timing demonstrated; no efficacy claim.';

// Execution plan — P0 (Nov 2026) through paper submission (Dec 2027)
export const ganttPhases: GanttPhase[] = [
  { name: 'Ph 0: Literature & Setup', duration: 'Jul–Sep 2026', deliverables: 'Literature freeze, vLLM 3-model serving on the retired 48 GB A6000 dev stack, Gate 0 MAD reproduction — passed 16 Sep 2026 (10/10 debates × 3 rounds)', progress: 100, barVariant: 'teal' },
  { name: 'Ph 1: P0 Engineering', duration: 'Oct–Nov 2026', deliverables: 'Core wired: options in prompts, parser/scorer, trust simplex projection, verifier interface, claim-domain routing, endpoints, manifest/resume. 514 tests; P0 gate 13/13 passed.', progress: 100, barVariant: 'default' },
  { name: 'Ph 2: Pilot run', duration: 'Dec 2026', deliverables: 'N1 96 GB smoke + FP8 precision replication (600 debates, $5.21) → WP-18 placebo/oracle → 24-item calibration → verifier audit (150–200 pairs; lexical 0.58 balanced accuracy; target ≥0.75, κ ≥0.60) → 50-question Month-1 pilot → 100–150-question G2 pilot. 3 seeds for the pilot; 2 for the main matrix. G2 decides whether the Core run proceeds.', progress: 0, barVariant: 'amber' },
  { name: 'Ph 3: Core run', duration: 'Jan 2027', deliverables: 'G3 Core run: 4 executable arms (B3, B4-matched, B8-no-trust, B8) × GPQA-Main 400 / MMLU-Pro 400 / HLE 200 × 2 seeds = 24 runs, 8,000 debates (≈46 GPU-h at 172.7 debates/h). Row 2/24 (GPQA-Main seed 1, B8 vs B8-no-trust) complete Nov 2026: 798 debates, McNemar p=0.086 (n.s.). B8-oracle is not a Core arm; SciClaimBench is not in Core v1.0 (180 items at the v1.2 benchmark freeze). PRE_REGISTRATION.md v1.0.', progress: 8, barVariant: 'rose' },
  { name: 'Ph 4: Full run + benchmark', duration: 'Feb 2027', deliverables: 'G4/G5 Full: 32 rows at 300 items/dataset with the gold-evidence oracle on SciClaimBench (9,600 debates), plus a 36-row gold-answer alternate (10,800 debates); Core + Full ≈ 69.49 GPU-h ≈ $104.23 at $1.50/GPU-h all-in. Adds B8-placebo/B8-oracle via WP-18. SciClaimBench ladder: 180 floor, 300 target, 600 stretch, 800 no-go.', progress: 0, barVariant: 'rose' },
  { name: 'Ph 5: Human Eval + SDT', duration: 'Mar 2027', deliverables: 'Human evaluation / SDT, benchmark annotation, and verifier-audit follow-up.', progress: 0, barVariant: 'default' },
  { name: 'Ph 6: Results Freeze', duration: 'Apr 2027', deliverables: 'Freeze results, CIs, and effect sizes. No new runs or arm changes after the freeze.', progress: 0, barVariant: 'amber' },
  { name: 'Ph 7: Thesis Chapters', duration: 'May 2027', deliverables: 'Write the thesis chapters against the frozen results.', progress: 0, barVariant: 'teal' },
  { name: 'Ph 8: Thesis Submit + Defence', duration: 'Jun–Jul 2027', deliverables: 'Thesis submitted June 2027; defence June/July 2027.', progress: 0, barVariant: 'teal' },
  { name: 'Ph 9: Paper', duration: 'Aug–Dec 2027', deliverables: 'Paper writing and submission after the defence (TACL rolling; EMNLP 2028 fallback).', progress: 0, barVariant: 'default' },
];

// Gates, submissions, and the post-defence paper window
export const milestones: TimelineItem[] = [
  {
    milestone: 'Gate 0 — achieved 16 Sep 2026',
    date: 'Jul–Sep 2026',
    description: 'Vanilla MAD reproduction (Du et al. 2023) on a GPQA slice: 10/10 debates completed all 3 rounds, no empty positions, mean 370.8 s/debate. Full report in experiments/gate0/.',
    deliverable: 'Working MAD reproduction — done',
  },
  {
    milestone: 'P0 engineering gate',
    date: 'Nov 2026',
    description: '615 tests; P0 gate 13/13 passed and released (tags p0-gate, p0-release). Current report evidence: 70-pp report, 19-pp journal, 0 undefined references. Core wiring is in place — this is engineering readiness, not an efficacy result.',
    deliverable: 'P0 gate report + runnable matrix — 13/13',
  },
  {
    milestone: 'Pilot run',
    date: 'Dec 2026',
    description: 'N1 96 GB smoke + FP8 precision replication, WP-18 placebo/oracle, a 24-item calibration, and the verifier audit precede the pilot. The 50-question Month-1 pilot is followed by the 100–150-question G2 pilot. G2 requires baseline CCR ≥0.30, trust AUROC ≥0.65, ≥65% correct-direction changes, and injection κ ≥0.75; if it fails, the project reframes to report the negative result honestly.',
    deliverable: 'G2 pilot-run report',
  },
  {
    milestone: 'Core run',
    date: 'Jan 2027',
    description: 'G3 Core run: 4 executable arms × GPQA-Main 400 / MMLU-Pro 400 / HLE 200 × 2 seeds = 24 runs. Row 2/24 (GPQA-Main seed 1, B8 vs B8-no-trust) complete Nov 2026: 798 debates (399/arm, q27 quarantined), accuracy 62.4% vs 58.7%, exact McNemar p = 0.086 (n.s.) — feasibility + timing demonstrated, no efficacy claim. Serving was then tuned to 8 concurrent rows with CUDA graphs: measured 172.7 debates/h on a 96 GB RTX PRO 6000 (3.3× the eager baseline), which puts the remaining programme at 126.2 GPU-h (≈ $191.92 at $1.50/GPU-h all-in). B8-oracle is not a Core arm, and SciClaimBench is not in Core v1.0.',
    deliverable: 'G3 Core matrix + pre-registered causal contrast (B8 vs B8-no-trust) — row 2/24 done',
  },
  {
    milestone: 'Full run + benchmark',
    date: 'Feb 2027',
    description: 'G4/G5 Full: 32 rows at 300 items/dataset with the gold-evidence oracle on SciClaimBench, adding B8-placebo/B8-oracle through WP-18; the 36-row gold-answer alternate is 10,800 debates. At the measured 172.7 debates/h and $1.50/GPU-h all-in, the remaining 21,800-debate programme is 126.2 GPU-h ≈ $191.92. SciClaimBench benchmark freeze at 180 items (v1.2); ladder 180 floor, 300 target, 600 stretch, 800 no-go.',
    deliverable: 'Full-run matrix + SciClaimBench v1.2',
  },
  {
    milestone: 'Human eval + SDT',
    date: 'Mar 2027',
    description: 'Human evaluation and SDT, benchmark annotation, and the verifier-audit follow-up.',
    deliverable: 'Human-eval + benchmark package',
  },
  {
    milestone: 'Results freeze',
    date: 'Apr 2027',
    description: 'Freeze all results, confidence intervals, and effect sizes. No post-hoc arm or endpoint changes.',
    deliverable: 'Frozen results',
  },
  {
    milestone: 'Thesis chapters',
    date: 'May 2027',
    description: 'Write the thesis chapters against the frozen results.',
    deliverable: 'Thesis draft',
  },
  {
    milestone: 'Thesis submission',
    date: 'Jun 2027',
    description: 'Submit the FYDP thesis in June 2027.',
    deliverable: 'Submitted thesis',
  },
  {
    milestone: 'Defence',
    date: 'Jun–Jul 2027',
    description: 'Defend the thesis in June/July 2027.',
    deliverable: 'Defence slides',
  },
  {
    milestone: 'Paper after defence',
    date: 'Aug–Dec 2027',
    description: 'Write and submit the paper version after the defence; TACL rolling submission, EMNLP 2028 fallback.',
    deliverable: 'Paper submission',
  },
];

// Blueprint §7 — Models & Tools (final stacks; dev retired)
export const resources: ResourceCard[] = [
  { label: 'Agent 1 (Dev, retired)', value: 'Qwen3.5-9B', sub: 'Retired 48 GB A6000 dev stack — no longer in the runnable path', href: 'https://huggingface.co/Qwen/Qwen3.5-9B' },
  { label: 'Agent 1 (Final)', value: 'Qwen3.8-27B', sub: 'Full-scale 27B dense, served AWQ-INT4 4-bit (~21.0 GB) on the 96 GB RTX PRO 6000 main stack; FP8 checkpoint (~29.95 GB) only for the 96 GB precision check', href: 'https://huggingface.co/Qwen/Qwen3.8-27B' },
  { label: 'Agent 2 (Dev, retired)', value: 'Gemma 4 12B', sub: 'Retired 48 GB A6000 dev stack — 12B proxy, no longer in the runnable path', href: 'https://huggingface.co/google/gemma-4-12B' },
  { label: 'Agent 2 (Final)', value: 'Gemma-4-26B-A4B', sub: 'MoE (3.8B active), served AWQ 4-bit (~17.2 GB) on the 96 GB RTX PRO 6000 main stack; FP8 checkpoint (28.67 GB) only for the 96 GB precision check', href: 'https://huggingface.co/google/gemma-4-26B-A4B' },
  { label: 'Agent 3 (Dev, retired)', value: 'Ministral-3-14B-Instruct', sub: 'Retired 48 GB A6000 dev stack; the official FP8 checkpoint could not be served on Ampere', href: 'https://huggingface.co/mistralai/Ministral-3-14B-Instruct-2512' },
  { label: 'Agent 3 (Final)', value: 'Mistral-24B-AWQ', sub: 'Third training lineage, AWQ 4-bit (15.06 GB) — main-matrix agent on the 96 GB RTX PRO 6000', href: 'https://huggingface.co/mistralai/Mistral-Small-3.2-24B-Instruct-2506' },
  { label: '4-bit main stack (pinned)', value: '~53.3 GB', sub: 'Qwen3.8-27B-AWQ-INT4 (~21.0 GB) · Gemma 4 26B-A4B AWQ (~17.2 GB) · Mistral 24B AWQ (15.06 GB) — Core and Full causal matrix on one 96 GB RTX PRO 6000' },
  { label: 'FP8 check stack (pinned)', value: '73.68 GB', sub: 'Qwen3.8-27B-FP8 (29.95 GB) · Gemma-4-26B-A4B-FP8 (28.67 GB) · Mistral-24B-AWQ (15.06 GB) — N1 96 GB smoke + small GPQA precision replication on the 96 GB RTX PRO 6000, not the main matrix' },
  { label: 'Oracle (B7)', value: 'GPT-6 Luna (OpenAI)', sub: 'Optional external-answer ceiling; 3 samples/question; mean single-call accuracy + 3-sample majority; ~$3–9 per 1,000; not a Core arm' },
  { label: 'Reranker', value: 'ms-marco-MiniLM cross-encoder', sub: 'Standard, fast, well-validated' },
  { label: 'Inference', value: 'vLLM', sub: 'Free, fast, multi-model serving' },
  { label: 'Orchestration', value: 'LangGraph', sub: 'State-machine fits round-based debate' },
  { label: 'Retrieval APIs', value: 'PubMed, ArXiv, Semantic Scholar', sub: 'Free academic APIs; Semantic Scholar paced at 1 req/s cumulatively' },
];

// Blueprint §7 — Final-stack Model Strategy + Cost Estimate
export interface CostRow {
  phase: string;
  models: string;
  gpu: string;
  rate: string;
  estHours: string;
  totalRange: string;
}

export const costEstimates: CostRow[] = [
  { phase: 'Serving + concurrency tuning (Nov 2026, done — already spent)', models: '4-bit main stack (~53.3 GB)', gpu: 'RTX PRO 6000 96GB', rate: '$1.50/GPU-h all-in', estHours: '3.5', totalRange: '$5.60 measured' },
  { phase: 'Core + Full runs (12,000 remaining; Dec 2026–Jan 2027)', models: '4-bit main stack (~53.3 GB)', gpu: 'RTX PRO 6000 96GB', rate: '$1.50/GPU-h all-in', estHours: '69.49', totalRange: '$104.23' },
  { phase: 'Cap increase (Jan 2027)', models: '4-bit main stack; gpqa 400 / mmlu 600 / hle 400; 3,200 debates', gpu: 'RTX PRO 6000 96GB', rate: '$1.50/GPU-h all-in', estHours: '18.53', totalRange: '$27.79' },
  { phase: 'Three ablations (Jan–Feb 2027)', models: '4-bit main stack; 6,000 debates', gpu: 'RTX PRO 6000 96GB', rate: '$1.50/GPU-h all-in', estHours: '34.74', totalRange: '$52.11' },
  { phase: 'FP8 precision replication (Feb 2027)', models: 'FP8 check stack (73.68 GB pinned); 600 debates', gpu: 'RTX PRO 6000 96GB', rate: '$1.50/GPU-h all-in', estHours: '3.47', totalRange: '$5.21' },
  { phase: 'Setup + ingress (all stages)', models: 'Persistent volumes, checkpoints, logs', gpu: '—', rate: '—', estHours: '—', totalRange: '$2.56' },
  { phase: 'Remaining programme (21,800 debates)', models: '96GB class, 8 concurrent rows, CUDA graphs', gpu: '—', rate: '—', estHours: '126.2', totalRange: '$191.92' },
];

// Blueprint §11 — Risk Assessment
export const risks: RiskRow[] = [
  { risk: 'Trust signal doesn\'t change output (Challenge C)', likelihood: 'Medium', likelihoodVariant: 'amber', impact: 'Critical', impactVariant: 'rose', mitigation: '24-item calibration + pilot (Dec 2026) before the matrix; a negative result is reportable' },
  { risk: 'Retrieval noise degrades evidence quality', likelihood: 'Medium', likelihoodVariant: 'amber', impact: 'Moderate', impactVariant: 'amber', mitigation: 'Cross-encoder reranker + citation-count filter + domain restriction' },
  { risk: 'Reviewers see as incremental over MoA/iMAD', likelihood: 'Low-Medium', likelihoodVariant: 'amber', impact: 'Moderate', impactVariant: 'amber', mitigation: 'B6/B9 direct comparisons; pre-register the comparison; no headline effect size before the run' },
  { risk: 'Timeline overload (matrix + benchmark)', likelihood: 'High', likelihoodVariant: 'rose', impact: 'High', impactVariant: 'rose', mitigation: 'Core run first (24 runs); Full run and 300-item benchmark only after Core run lands' },
  { risk: 'iMAD reimplementation fidelity', likelihood: 'Medium', likelihoodVariant: 'amber', impact: 'Moderate', impactVariant: 'amber', mitigation: '~10-day dedicated budget; explicit divergence documentation' },
  { risk: 'Single-card compute ceiling', likelihood: 'Low', likelihoodVariant: 'green', impact: 'Moderate', impactVariant: 'amber', mitigation: '4-bit 24–27B main stack (~53.3 GB) on one 96 GB RTX PRO 6000; measured 172.7 debates/h with 8 concurrent rows and CUDA graphs, so the remaining 21,800-debate programme is 126.2 GPU-h (~$191.92 at $1.50/GPU-h all-in). Concurrency, not a second GPU, is the lever' },
  { risk: 'Dataset mismatch (proof-only benchmarks)', likelihood: 'High', likelihoodVariant: 'rose', impact: 'Moderate', impactVariant: 'amber', mitigation: 'BrokenMath/BrokenArXiv appendix-only; GPQA-Main + MMLU-Pro STEM primary; HLE abstention control; SciClaimBench controlled set' },
];

// Blueprint §8 — Dataset Plan
export interface DatasetRow {
  name: string;
  role: string;
  source: string;
  size: string;
  limitation: string;
}

export const datasets: DatasetRow[] = [
  { name: 'GPQA-Main', role: 'Primary evidence-grounded benchmark', source: 'Idavidrein/gpqa (HF, official; gated)', size: '448 total · 400 cap', limitation: 'Well-known, not adversarial; options shuffled per question' },
  { name: 'MMLU-Pro (STEM)', role: 'Primary scale/robustness benchmark', source: 'TIGER-Lab/MMLU-Pro (HF, official)', size: 'STEM stratified · 400 cap', limitation: 'Broad STEM, non-adversarial' },
  { name: 'SciClaimBench', role: 'Controlled benchmark release (v1.2 freeze); not a Core dataset', source: 'Original release (planned; CC BY 4.0)', size: '180 floor · 300 target', limitation: 'Annotation-intensive; 600 stretch, 800 no-go, only with 2–3 dedicated annotators' },
  { name: 'HLE', role: 'Abstention / ceiling control', source: 'cais/hle (HF, official; gated)', size: '200 cap in matrix', limitation: 'Retrieval-resistant — never pooled with the primary tests' },
  { name: 'BrokenMath', role: 'Appendix-only premise rejection', source: 'INSAIT-Institute/BrokenMath (HF, official)', size: '451 proof-only', limitation: '0% answer-type retention — not usable for CCR' },
  { name: 'BrokenArXiv', role: 'Appendix-only qualitative', source: 'MathArena/brokenarxiv (HF, official)', size: '87 proof-only', limitation: '0% answer-type retention; cite the exact monthly snapshot' },
];

// Blueprint §10 — Failure Handling
export interface FailureRow {
  scenario: string;
  detection: string;
  mitigation: string;
  recovery: string;
}

export const failures: FailureRow[] = [
  { scenario: 'Retrieval returns no evidence', detection: 'Zero passages above relevance threshold', mitigation: 'Broaden query before declaring sparse; mark claim abstained', recovery: 'Stratify results by retrieval-success rate in reporting' },
  { scenario: 'Contradictory evidence retrieved', detection: 'Evidence verdicts conflict at >0.75 relevance', mitigation: 'Flag claim as "contested", report separately', recovery: 'Included as own category in human eval annotation' },
  { scenario: 'All agents hallucinate same way', detection: 'Homogeneous-vs-heterogeneous shows no CCR difference', mitigation: 'Heterogeneous model families (partial)', recovery: 'Diagnosed explicitly in the failure analysis (Mar 2027)' },
  { scenario: 'Trust collapse (all to T_min)', detection: 'Trust variance monitoring across rounds', mitigation: 'Floor/ceiling simplex projection after every update', recovery: 'Bounded by construction: min ≥ floor, sum = 1, max ≤ max(ceiling, 1/N); monitored empirically' },
  { scenario: 'Claim extraction fails', detection: 'Tagged-claim regex/schema validation fails', mitigation: 'Structured output prompting with explicit tags', recovery: 'Fallback LLM-based extraction pass' },
  { scenario: 'API rate limit / downtime', detection: 'HTTP error codes, timeout', mitigation: 'Local caching of prior retrievals', recovery: 'Retry + backoff; OpenAlex fallback' },
  { scenario: 'Context window overflow', detection: 'Token count monitoring before each round', mitigation: 'Cap K=3 rounds; summarize prior rounds', recovery: 'Truncate oldest round detail, preserve trust trajectory' },
  { scenario: 'iMAD reimplementation diverges', detection: 'Manual comparison vs reported results', mitigation: 'Explicit divergence documentation', recovery: 'Treat as honest limitation, not hidden' },
];

// Blueprint §10 — Edge Cases
export interface EdgeCaseRow {
  scenario: string;
  prevention: string;
  fallback: string;
}

// Difficulty ranking §7
export interface DifficultyRow {
  rank: number;
  component: string;
  difficulty: string;
  reason: string;
}

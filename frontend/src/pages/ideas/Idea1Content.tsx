import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { Badge } from "@/components/shared/Badge";
import { Callout } from "@/components/shared/Callout";
import { RiskTable } from "@/components/shared/RiskTable";
import { ArchitectureDiagram } from "@/components/shared/ArchitectureDiagram";
import { TrustSimulator } from "@/components/shared/TrustSimulator";
import { Walkthrough } from "@/components/shared/Walkthrough";
import {
  ColBox,
  Section,
  SectionTitle,
  TwoCol,
} from "@/components/shared/Section";
import { datasets, failures, risks } from "@/data/overview";
import {
  ArrowLeftRight,
  BarChart3,
  Building2,
  Calendar,
  ClipboardList,
  GraduationCap,
  Hammer,
  Lightbulb,
  Microscope,
  Ruler,
  Search,
  Settings,
  Shield,
  Target,
  Telescope,
  TriangleAlert,
  Trophy,
  Users,
  Wrench,
} from "lucide-react";

/** Compact table used by the blueprint sections. */
function DataTable({ head, rows }: { head: string[]; rows: ReactNode[][] }) {
  return (
    <div className="overflow-x-auto rounded-lg shadow-sm mb-4">
      <table className="w-full border-collapse text-xs sm:text-sm">
        <thead>
          <tr>
            {head.map((h) => (
              <th
                key={h}
                className="p-2.5 text-left font-bold bg-[#f1f5f9] dark:bg-[rgba(255,255,255,0.06)] border-b-2 border-[#e2e8f0] dark:border-[rgba(255,255,255,0.15)]"
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr
              key={i}
              className="border-b border-[#e2e8f0] dark:border-[rgba(255,255,255,0.08)] last:border-0 hover:bg-[#dce4ff] dark:hover:bg-[rgba(59,91,219,0.12)] even:bg-[#f8fafc] dark:even:bg-[rgba(255,255,255,0.03)] transition-colors"
            >
              {row.map((cell, j) => (
                <td key={j} className="p-2.5 align-top">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export const IDEA1_SECTIONS = [
  { id: "core-idea", label: "1. Core Idea" },
  { id: "design-decisions", label: "0. Research Design Decisions" },
  { id: "research-motivation", label: "2. Research Motivation" },
  { id: "problem-statement", label: "3. Problem Statement" },
  { id: "system-architecture", label: "4. Complete System Architecture" },
  { id: "pipeline", label: "5. Detailed Multi-Agent Pipeline" },
  { id: "data-flow", label: "6. Complete Data Flow" },
  { id: "models-tools", label: "7. Models & Tools" },
  { id: "dataset-plan", label: "8. Dataset Plan" },
  { id: "evaluation-strategy", label: "9. Evaluation Strategy" },
  { id: "edge-cases", label: "10. Edge Cases & Failure Handling" },
  { id: "risk-assessment", label: "11. Risk Assessment" },
  { id: "roadmap", label: "12. Roadmap & Gates" },
  { id: "implementation-order", label: "13. Implementation Order" },
  { id: "publication-justification", label: "Q1. Publication Justification" },
  { id: "supervisor-explanation", label: "14. Supervisor Explanation" },
  { id: "team-explanation", label: "15. Team Explanation" },
  { id: "expected-outcome", label: "16. Expected Research Outcome" },
  { id: "future-extensions", label: "17. Future Extensions" },
  { id: "final-review", label: "18. Final Critical Review" },
] as const;

const ROADMAP_LINK =
  "font-semibold text-[#3b5bdb] dark:text-[#93c5fd] underline decoration-dotted underline-offset-2";

type Tone = "blue" | "green" | "amber" | "rose";

const badge = (label: string, tone: Tone = "blue") => (
  <Badge variant={tone}>{label}</Badge>
);
const strong = (text: string) => <strong>{text}</strong>;
const red = (text: string) => (
  <span className="text-[#e03131]">{text}</span>
);
const muted = (text: string) => (
  <span className="text-xs text-[#64748b] dark:text-[#94a3b8]">{text}</span>
);
const datasetRole = (role: string, primary: boolean) => (
  <>
    <Badge variant={primary ? "rose" : "blue"}>{role.split(" ")[0]}</Badge>{" "}
    {role}
  </>
);

export function Idea1Content() {
  return (
    <>
      {/* ───────────── 1. Core Idea ───────────── */}
      <Section id="core-idea" accent="blue" className="animate-fade-up">
        <SectionTitle icon={Lightbulb}>1. Core Idea</SectionTitle>
        <Callout variant="info" title="📌 P0 implementation status (Nov 2026)">
          <p className="mb-0">
            <strong>
              615 tests; P0 gate 13/13 passed and released (tags p0-gate,
              p0-release).
            </strong>{" "}
            Options in prompts, parser/scorer, trust simplex projection,
            verifier interface, claim-domain routing, endpoints, and
            manifest/resume are wired. Report evidence: 70-pp report, 19-pp
            journal, 0 undefined references. This is engineering readiness,{" "}
            <strong>not an efficacy result</strong>; everything below is planned
            unless explicitly dated as done.
          </p>
        </Callout>
        <Callout
          variant="success"
          title="✅ Completed Core row 2/24 — GPQA-Main seed 1 (Nov 2026)"
        >
          <p className="mb-0">
            <strong>
              B8 (trust) vs B8-no-trust (majority): 798 debates (399/arm, q27
              quarantined).
            </strong>{" "}
            Accuracy 62.41% (249/399, 95% CI 57.6–67.2) vs 58.65% (234/399, CI
            53.6–63.4); paired 208 both / 41 B8-only / 26 control-only / 124
            neither; exact McNemar p&nbsp;=&nbsp;0.086 (<strong>not
            significant</strong>). MPR 0.78/0.75, ARR 0.66/0.70, CCR-e
            0.10/0.15, ~15.3 GPU-h, mean pair 138 s. Milestones
            100/150/200/250/300/350/400 (final) merged upstream. This
            demonstrates <strong>feasibility + timing</strong>, not efficacy.
          </p>
        </Callout>
        <p className="mb-3 text-sm sm:text-base">
          We propose a{" "}
          <strong>trust-calibrated multi-agent scientific deliberation</strong>{" "}
          framework to mitigate <strong>sycophantic consensus collapse</strong>:
          agents whose claims are verified against retrieved scientific
          literature accumulate influence, so a confidently wrong majority
          cannot suppress a correct minority.
        </p>
        <Callout variant="success" title="🎯 Positioning & Contributions">
          <p className="mb-2">
            Prior work <em>diagnosed and measured</em> inter-agent sycophancy
            (Yao et al., 2025) and correct-minority suppression (He et al.,
            2026). Our contribution is the missing <strong>mitigation</strong>:
            an in-session, evidence-grounded mechanism plus an open evaluation
            harness.
          </p>
          <ul className="list-disc list-inside text-sm space-y-1">
            <li>
              <strong>
                C1 (primary) — Trust-Calibrated Evidence-Grounded Aggregation:
              </strong>{" "}
              a bounded, dynamic trust rule that re-weights agents during
              debate.
            </li>
            <li>
              <strong>
                C2 (co-primary) — Open Sycophancy-Stress Evaluation Harness:
              </strong>{" "}
              pre-registered injection protocol, CCR/MPR/ECR metrics, a 4-arm
              executable matrix (6-arm target), GPQA/MMLU-Pro/HLE, and
              SciClaimBench at 180 floor / 300 target.
            </li>
            <li>
              <strong>C3 (supporting) — Source-partitioned retrieval</strong>{" "}
              for atomic-claim verification.
            </li>
          </ul>
        </Callout>
      </Section>

      {/* ───────────── 0. Research Design Decisions & Assumptions ───────────── */}
      <Section
        id="design-decisions"
        accent="amber"
        className="animate-fade-up animate-delay-1"
      >
        <SectionTitle icon={Settings}>
          0. Research Design Decisions &amp; Assumptions
        </SectionTitle>

        <Callout variant="gap" title="🕳️ Verified Research Gap">
          <p className="mb-0">
            <strong>
              No existing framework provides numeric, evidence-grounded,
              in-session trust re-weighting with formal boundedness guarantees.
            </strong>{" "}
            Diagnosis exists (Yao et al. 2025), efficiency optimisation exists
            (iMAD, AAAI 2026), static aggregation exists (MoA, ICLR 2025
            Poster), and mitigation attempts use prompt refinement
            (ConsensAgent, Findings of ACL 2025), uncertainty signals (DebUnc,
            Findings of EMNLP 2025), or theoretical pruning (Estornell &amp;
            Liu, NeurIPS 2024 Main Track) — but none ties an agent's influence
            to{" "}
            <em>
              real-time, externally verified evidence with a formally bounded
              numeric trust score
            </em>
            .
          </p>
        </Callout>

        <p className="text-sm mb-4">
          A single strong model still hallucinates confidently and cannot be
          internally challenged. Multi-agent debate adds adversarial critique
          only if aggregation does not default to majority vote — the mechanism
          that causes sycophantic collapse. This motivates{" "}
          <strong>heterogeneous, independently evidence-checked agents</strong>,
          not multiple instances of the same model.
        </p>

        <h4 className="text-sm font-bold mb-3">Core Research Assumptions</h4>
        <DataTable
          head={["#", "Assumption", "Risk", "Why it could fail"]}
          rows={[
            [
              "1",
              "Claim decomposition works",
              badge("Moderate", "amber"),
              "Claims can be decomposed into checkable atomic propositions; some are compound or context-dependent.",
            ],
            [
              "2",
              "Retrieval is reliable",
              badge("Moderate", "amber"),
              "PubMed/ArXiv/Semantic Scholar can support or contradict claims inside the debate budget; retrieval noise and sparse niche coverage remain.",
            ],
            [
              "3",
              "Trust changes behaviour",
              badge("Critical", "rose"),
              "Trust weights must change the final output, not sit in context ignored. Piloted Dec 2026 before the matrix; the whole mechanism depends on it.",
            ],
            [
              "4",
              "Heterogeneity helps",
              badge("Low", "green"),
              "Different model families reduce but do not eliminate correlated hallucination; accepted as a named limitation.",
            ],
            [
              "5",
              "Competitor differentiation",
              badge("Moderate", "amber"),
              "Must measurably beat ConsensAgent's prompt refinement, not just iMAD/MoA. A written comparison is mandatory; full reimplementation only if Full-run capacity allows.",
            ],
          ]}
        />

        <h4 className="text-sm font-bold mb-3">
          Alternatives Considered &amp; Rejected
        </h4>
        <DataTable
          head={["Alternative", "Decision", "Reason"]}
          rows={[
            [
              "Post-hoc classifier (Minority Sentinel-style)",
              badge("Rejected", "rose"),
              "Intervenes after debate ends, not during. Valid but separate contribution space — we position against it, not duplicate it.",
            ],
            [
              "Fine-tuning agents",
              badge("Rejected", "rose"),
              "Compute cost and no cross-model generalisation; also conflates sycophancy reduction with evidence grounding.",
            ],
            [
              "Confidence-based re-weighting (iMAD-style)",
              badge("Rejected", "rose"),
              "Confidence is self-reported from the same context that injected pressure can manipulate — exactly the vulnerability we target.",
            ],
            [
              "Evidence-grounded numeric trust (ours)",
              badge("Chosen", "green"),
              "Ties influence to something external and independent of debate social dynamics — the lever needed to break collapse, not just detect it.",
            ],
          ]}
        />
      </Section>

      {/* ───────────── 2. Research Motivation ───────────── */}
      <Section
        id="research-motivation"
        className="animate-fade-up animate-delay-2"
      >
        <SectionTitle icon={Microscope}>2. Research Motivation</SectionTitle>
        <p className="text-sm mb-4">
          Sycophancy is cited as an open problem in 50+ peer-reviewed papers
          since 2023. In multi-agent systems it defeats the reason debate is
          used: if the answer follows whichever position sounds most confident
          rather than which is most correct, debate adds cost without adding
          reliability. The gap is stated in §0; the table below is the
          nearest-work evidence.
        </p>
        <DataTable
          head={["Work", "Year", "What it does", "What's missing"]}
          rows={[
            [
              "Yao et al. (Peacemaker)",
              "2025",
              "Diagnoses and measures inter-agent sycophancy",
              red("No mitigation — diagnostic only"),
            ],
            [
              "He et al. (Minority Sentinel)",
              "2026",
              "Post-hoc classifier on debate logs",
              red("Intervenes after debate ends, not during"),
            ],
            [
              "iMAD (Fan et al.)",
              "2026",
              "Decides when to debate (efficiency)",
              red("Doesn't decide whom to trust once debating"),
            ],
            [
              "MoA (Wang et al.)",
              "2025",
              "Static multi-model aggregation",
              red("No evidence grounding or dynamic trust"),
            ],
            [
              "ConsensAgent (Pitre et al.)",
              "2025",
              "Prompt-refinement sycophancy mitigation",
              red(
                "Static/textual intervention, not numeric trust; no external evidence retrieval",
              ),
            ],
            [
              "DebUnc (Yoffe et al.)",
              "2025",
              "Uncertainty-based in-loop weighting",
              red(
                "Self-reported uncertainty, not external evidence verification",
              ),
            ],
            [
              "Estornell & Liu",
              "2024",
              "Theoretical framework for majority convergence",
              red(
                "Theoretical only — pruning interventions, not a deployable system",
              ),
            ],
          ]}
        />
      </Section>

      {/* ───────────── 3. Problem Statement ───────────── */}
      <Section
        id="problem-statement"
        accent="teal"
        className="animate-fade-up animate-delay-2"
      >
        <SectionTitle icon={Target}>3. Problem Statement</SectionTitle>
        <p className="text-sm mb-4">
          <strong>Research hypothesis:</strong> if agent influence in
          aggregation is dynamically re-weighted during debate based on external
          evidence verification, sycophantic collapse will measurably decrease
          compared with standard majority-vote debate, without model
          fine-tuning.
        </p>
        <h4 className="text-sm font-bold mb-3">
          Four Engineering Challenges (Washington Accord Level)
        </h4>
        <DataTable
          head={["Challenge", "Requirement", "Risk"]}
          rows={[
            [
              "A — Real-time verification",
              "Decompose claims into atomic propositions; retrieve supporting/contradicting evidence within <10 s per turn.",
              badge("Moderate", "amber"),
            ],
            [
              "B — Trust stability",
              "Avoid degenerate equilibria: full collapse or single-agent dominance.",
              badge("Moderate", "amber"),
            ],
            [
              "C — Behavioural effectiveness",
              "Trust weights must change model outputs, not merely appear in context and get ignored by attention.",
              badge("Highest", "rose"),
            ],
            [
              "D — Heterogeneous agents",
              "Trust calibration must be model-agnostic across ~14–32B open-weight models from different families.",
              badge("Moderate", "amber"),
            ],
          ]}
        />
      </Section>

      {/* ───────────── 4. Complete System Architecture ───────────── */}
      <Section
        id="system-architecture"
        className="animate-fade-up animate-delay-3"
      >
        <SectionTitle icon={Building2}>
          4. Complete System Architecture
        </SectionTitle>
        <p className="text-sm mb-4">
          Each query passes a confidence gate, then either returns a direct
          answer or enters the evidence-grounded debate pipeline below. Tap any
          stage in the diagram for a plain-English description.
        </p>
        <div className="mb-4">
          <ArchitectureDiagram />
        </div>
        <p className="text-xs text-[#64748b] dark:text-[#94a3b8] bg-[#f8fafc] dark:bg-[rgba(255,255,255,0.03)] rounded-lg p-3 border border-[#e2e8f0] dark:border-[rgba(255,255,255,0.08)] mb-4">
          ⚡ <strong>4.1 Confidence Estimator:</strong> a lightweight
          single-pass self-report or 3-sample agreement check avoids full debate
          cost on easy questions. Over-triggering wastes compute but poses no
          correctness risk; removing it means ~9 forward passes instead of ~1.
          A hard-as-easy miss is acceptable because eval datasets are
          pre-filtered to divergent cases, so no recovery is needed.
        </p>
        <TwoCol>
          <ColBox>
            <h4 className="text-sm font-bold mb-2">4.2 Agent Pool (N=3)</h4>
            <p className="text-sm leading-relaxed mb-0">
              <a
                className="underline decoration-dotted underline-offset-2"
                href="https://huggingface.co/Qwen/Qwen3.8-27B"
                target="_blank"
                rel="noopener noreferrer"
              >
                Qwen3.8-27B-AWQ-INT4
              </a>
              ,{" "}
              <a
                className="underline decoration-dotted underline-offset-2"
                href="https://huggingface.co/google/gemma-4-26B-A4B"
                target="_blank"
                rel="noopener noreferrer"
              >
                Gemma 4 26B A4B
              </a>
              ,{" "}
              <a
                className="underline decoration-dotted underline-offset-2"
                href="https://huggingface.co/mistralai/Mistral-Small-3.2-24B-Instruct-2506"
                target="_blank"
                rel="noopener noreferrer"
              >
                Mistral Small 3.2 24B
              </a>{" "}
              — three different families for genuine heterogeneity. Each agent
              tracks its own trust vector T ∈ ℝ³, initialised uniformly at 1/N.
            </p>
          </ColBox>
          <ColBox>
            <h4 className="text-sm font-bold mb-2">
              4.3 Source-Partitioned RAG
            </h4>
            <p className="text-sm leading-relaxed mb-0">
              Claims → atomic propositions → claim-domain routing → Agent
              A→PubMed, B→ArXiv, C→Semantic Scholar. Partitioning prevents all
              agents retrieving from the same narrow slice; a cross-encoder
              reranker scores evidence per claim, and the verifier returns
              supported / contradicted / unverifiable.
            </p>
          </ColBox>
          <ColBox>
            <h4 className="text-sm font-bold mb-2">4.4 Trust Update (Core)</h4>
            <p className="text-sm leading-relaxed mb-0">
              <code>Sᵢ ← log(max(Sᵢ, ε)) + α·Vᵢ/nᵢ − β·Hᵢ/nᵢ</code>, then one
              softmax, then a floor/ceiling simplex projection. Vᵢ and Hᵢ are
              supported/contradicted counts, normalised by claims checked (nᵢ).
              Defaults α = 0.5, β = 0.3. Guarantees: min ≥ 0.1, Σ = 1, max ≤
              max(0.9, 1/N). Neutral evidence is an identity.
            </p>
          </ColBox>
          <ColBox>
            <h4 className="text-sm font-bold mb-2">
              4.5 Revision Rounds (K=3)
            </h4>
            <p className="text-sm leading-relaxed mb-0">
              Agents see peer arguments plus their own trust standing, which
              simulates genuine deliberation. The trust trajectory is logged
              across rounds for ECR analysis.
            </p>
          </ColBox>
          <ColBox>
            <h4 className="text-sm font-bold mb-2">
              4.6 Trust-Weighted Adjudication
            </h4>
            <p className="text-sm leading-relaxed mb-0">
              Final answer = argmax over Σ(Tᵢ × positionᵢ) at round K — not
              majority vote. A correct minority with high trust can outweigh two
              unsupported majority agents.
            </p>
          </ColBox>
        </TwoCol>
        <div className="print:hidden mt-6">
          <h4 className="text-sm font-bold mb-3">
            Try the Trust Update Yourself (§4.4)
          </h4>
          <TrustSimulator />
        </div>
      </Section>

      {/* ───────────── 5. Detailed Multi-Agent Pipeline ───────────── */}
      <Section id="pipeline" accent="blue" className="animate-fade-up animate-delay-4">
        <SectionTitle icon={Wrench}>
          5. Detailed Multi-Agent Pipeline
        </SectionTitle>
        <p className="text-sm mb-4">
          Agents 1–3 are the final 24–27B stack from §7 (the 48 GB A6000 dev
          stack is retired). Each produces an answer, a reasoning trace, and
          tagged atomic claims; the orchestrator then runs the loop.
        </p>
        <DataTable
          head={["Stage", "Detail"]}
          rows={[
            [
              "Round 0 — positions",
              "3× {agent_id, answer, reasoning_trace, initial_trust = ⅓}. Agents state independent positions with no peer context.",
            ],
            [
              "Claim decomposition",
              "Each reasoning trace → a list of atomic claims tagged to its source agent and domain, ready for verification.",
            ],
            [
              "Source-partitioned retrieval",
              "Per-claim {evidence_verdict, passage, relevance_score}. This is the first external signal in the system. Removing retrieval reduces the system to MoA (B6).",
            ],
            [
              "Trust update",
              "Vᵢ, Hᵢ, nᵢ from the verdicts → trust update (§4.4). Injection point for fabricated consensus is t=1→2.",
            ],
            [
              "Revision rounds ×K",
              "Repeat positions → claims → retrieval → trust for K=3. The full trajectory is required for Propositions 2–3 and ECR.",
            ],
            [
              "Trust-weighted aggregation",
              "Final answer = argmax Σ(Tᵢ × positionᵢ) at round K, not majority vote.",
            ],
            [
              "Recovery",
              "Unparseable output → fallback LLM extraction. Timeout → retry once, then mark the round INCONCLUSIVE. Never blocks the whole debate.",
            ],
            [
              "Orchestrator",
              "LangGraph state machine manages round sequencing, the t=1→2 injection point, trust updates, and final aggregation. Hard round cap K=3 and retry cap 3 prevent runaway loops.",
            ],
          ]}
        />
      </Section>

      {/* ───────────── 6. Complete Data Flow ───────────── */}
      <Section id="data-flow" className="animate-fade-up animate-delay-5">
        <SectionTitle icon={ArrowLeftRight}>6. Complete Data Flow</SectionTitle>
        <p className="text-sm mb-4">
          Question → confidence gate → round-0 positions → claim decomposition →
          source-partitioned retrieval → trust update → K revision rounds →
          trust-weighted aggregation → result package. Every intermediate result
          is logged for traceability, ECR calibration, and verification of
          Propositions 2–3.
        </p>
        <div className="print:hidden mb-4">
          <h4 className="text-sm font-bold mb-3">
            Walk the Real Example, One Step at a Time
          </h4>
          <Walkthrough />
        </div>
        <p className="text-xs text-[#64748b] dark:text-[#94a3b8] bg-[#f8fafc] dark:bg-[rgba(255,255,255,0.03)] rounded-lg p-3 border border-[#e2e8f0] dark:border-[rgba(255,255,255,0.08)] mb-0">
          <strong>Logged artifacts:</strong> the trust trajectory (needed for
          Propositions 2–3), per-claim evidence verdicts (needed for ECR), and
          per-agent reasoning traces (needed for human evaluation).
        </p>
      </Section>

      {/* ───────────── 7. Models & Tools ───────────── */}
      <Section id="models-tools" accent="teal" className="animate-fade-up">
        <SectionTitle icon={Hammer}>7. Models &amp; Tools</SectionTitle>
        <p className="text-sm mb-4">
          All open-weight, inference-only, served via vLLM. The 48 GB A6000 dev
          stack is retired; only the <code>fourbit</code> main stack and the{" "}
          <code>final</code> FP8 check stack are runnable.
        </p>

        <h4 className="text-sm font-bold mt-5 mb-3">
          Model Stack — fourbit (main) and final (FP8 check)
        </h4>
        <DataTable
          head={["Stack", "Models (pinned weights)", "Total", "Use"]}
          rows={[
            [
              strong("fourbit"),
              "Qwen3.8-27B-AWQ-INT4 21.0 GB · Gemma 4 26B-A4B AWQ 17.2 GB · Mistral 24B AWQ 15.06 GB",
              "53.26 GB",
              "Core and Full causal matrix on one 96 GB RTX PRO 6000",
            ],
            [
              strong("final"),
              "Qwen3.8-27B-FP8 29.95 GB · Gemma 4 26B A4B FP8 28.67 GB · Mistral 24B AWQ 15.06 GB",
              "73.68 GB",
              "N1 smoke + small GPQA precision replication only",
            ],
          ]}
        />
        <p className="text-xs text-[#64748b] dark:text-[#94a3b8] mb-4">
          Qwen is dense with 262K context; Gemma is MoE with 3.8B active and
          256K context; Mistral adds a third lineage (non-Qwen, non-Gemma). The
          FP8 stack is not the main Full matrix. Dev stack (retired, 48 GB
          A6000): Qwen3.5-9B, Gemma 4 12B, Ministral-3-14B.
        </p>

        <h4 className="text-sm font-bold mb-3">Tools</h4>
        <DataTable
          head={["Tool", "Role"]}
          rows={[
            ["Oracle (B7)", "GPT-6 Luna (OpenAI), 3 samples/question; mean single-call accuracy + CI + 3-sample majority; ~$3–9 per 1,000; optional external ceiling, not a Core arm."],
            ["Reranker", "ms-marco-MiniLM cross-encoder; standard, fast, well-validated."],
            ["Inference", "vLLM; free, fast, multi-model serving."],
            ["Orchestration", "LangGraph; the state machine fits round-based debate."],
            ["Retrieval APIs", "PubMed, ArXiv, Semantic Scholar; free academic APIs; Semantic Scholar paced at 1 req/s cumulatively."],
          ]}
        />

        <h4 className="text-sm font-bold mb-3">Serving &amp; Budget</h4>
        <p className="text-sm mb-3">
          The programme runs on one <strong>96 GB RTX PRO 6000 on-demand</strong>{" "}
          at <strong>$1.50/GPU-h all-in</strong> (disk and ingress included).
          Eight concurrent rows with CUDA graphs measured{" "}
          <strong>172.7 debates/h</strong> versus 52.2/h for the old 2-way eager
          baseline (3.3× faster, ~69% cheaper per debate). Serving uses vLLM
          utilisation 0.33/0.29/0.28 (sum 0.90), 8k context,
          <code>--max-num-seqs 32</code>, and{" "}
          <code>--disable-log-requests</code>. The offline check passes; the
          96 GB hardware smoke has not been run.
        </p>
        <DataTable
          head={["Stage", "Debates", "GPU-h", "All-in cost"]}
          rows={[
            ["Core + Full (36-row alternate)", "14,000", "81.06", "$121.59"],
            ["Cap increase (MMLU-Pro 600 / HLE 400)", "3,200", "18.53", "$27.79"],
            ["Three ablations (GPQA 400 / MMLU-Pro 600, 2 seeds)", "6,000", "34.74", "$52.11"],
            ["FP8 precision replication", "600", "3.47", "$5.21"],
            ["Setup + ingress", "—", "1.33", "$2.56"],
            [
              strong("Total remaining programme"),
              strong("23,798"),
              strong("139.13"),
              strong("≈$209.25"),
            ],
          ]}
        />
        <p className="text-xs text-[#64748b] dark:text-[#94a3b8] mb-4">
          23,798 debates = 139.13 GPU-h ≈ $209.25, committed at{" "}
          <strong>$219.25 with $10 headroom</strong> under the $220 cap, inside
          the <strong>$300 project hard stop</strong> (~$53 already spent).
        </p>

        <h4 className="text-sm font-bold mt-5 mb-3">
          Implementation Difficulty Ranking (easiest → hardest)
        </h4>
        <DataTable
          head={["#", "Component", "Difficulty", "Why"]}
          rows={[
            ["1", "vLLM multi-model serving", badge("Low", "blue"), "Well-documented, standard setup"],
            ["2", "Retrieval + reranking", badge("Moderate", "amber"), "Mostly API/plumbing work"],
            ["3", "Claim decomposition + tagging", badge("Moderate", "amber"), "Needs careful prompt engineering plus fallback extraction"],
            ["4", "Trust update + LangGraph state machine", badge("Moderate–High", "amber"), "Operator order: logit accumulation → softmax → floor/ceiling simplex projection. Clamp-then-renormalise is wrong."],
            ["5", "iMAD reimplementation (B9)", badge("Highest", "rose"), "~10 working days; reconstruct the method from the paper description"],
          ]}
        />
      </Section>

      {/* ───────────── 8. Dataset Plan ───────────── */}
      <Section id="dataset-plan" className="animate-fade-up animate-delay-1">
        <SectionTitle icon={BarChart3}>8. Dataset Plan</SectionTitle>
        <p className="text-sm mb-4">
          Core datasets: GPQA-Main and MMLU-Pro STEM for evidence-grounded
          accuracy, plus HLE as the abstention control. SciClaimBench is the
          controlled gold-evidence benchmark, not a Core dataset: the v1.2
          freeze is 180 items, with 300 as the ladder target. BrokenMath and
          BrokenArXiv are appendix-only — both are proof-only with 0%
          answer-type retention, so they are not usable for CCR.
        </p>
        <DataTable
          head={["Dataset", "Role", "Source", "Size", "Limitation"]}
          rows={datasets.map((ds, i) => [
            strong(ds.name),
            datasetRole(ds.role, i < 2),
            ds.source,
            ds.size,
            muted(ds.limitation),
          ])}
        />
        <p className="text-xs text-[#64748b] dark:text-[#94a3b8] mb-0">
          <strong>Scale:</strong> 24-item calibration first; then Core is 4 arms
          × GPQA-Main 400 / MMLU-Pro STEM 400 / HLE 200 × 2 seeds = 24 runs,
          8,000 debates (~46 GPU-h at 172.7 debates/h). B8-oracle is not a Core
          arm; SciClaimBench is not in Core v1.0. The primary Full matrix is 32
          rows at 300 items/dataset with the gold-evidence oracle on
          SciClaimBench (9,600 debates); the 36-row gold-answer alternate is
          10,800 debates. Benchmark ladder: 180 floor, 300 target, 600 stretch,
          800 no-go.
          <br />
          <strong>Fallbacks:</strong> delayed HLE stays an abstention control
          and is not replaced by a primary set; a discontinued BrokenArXiv
          snapshot is frozen at the last available revision; Semantic Scholar
          runs behind a 1 req/s cumulative pacing gate and falls back to
          OpenAlex if it degrades.
        </p>
      </Section>

      {/* ───────────── 9. Evaluation Strategy ───────────── */}
      <Section
        id="evaluation-strategy"
        accent="blue"
        className="animate-fade-up animate-delay-2"
      >
        <SectionTitle icon={Ruler}>9. Evaluation Strategy</SectionTitle>
        <h4 className="text-sm font-bold mb-3">
          Metrics &amp; Primary Hypotheses
        </h4>
        <DataTable
          head={["Metric", "Definition", "Primary hypothesis"]}
          rows={[
            [
              strong("CCR (Collapse Rate)"),
              "% of correct agents who abandon under injected pressure",
              "H1: trust calibration reduces CCR by ≥20% vs MAD on injected GPQA-Main / MMLU-Pro STEM.",
            ],
            [
              strong("MPR (Minority Preservation)"),
              "% debates where the correct minority survives to the final output",
              "H2: MPR improves by ≥15 pp vs plain MAD on GPQA-Main and MMLU-Pro STEM; SciClaimBench reported separately at the benchmark freeze.",
            ],
            [
              strong("ECR (Evidence Calibration)"),
              "Correlation between trust weight and empirical correctness",
              "H3: ECR > 0.80 on GPQA-Main; the exact endpoint is frozen before the matrix.",
            ],
            [
              strong("Task Accuracy"),
              "Standard answer accuracy per benchmark",
              "H4: no regression on stable splits; improvement under injected pressure is the primary test.",
            ],
          ]}
        />

        <h4 className="text-sm font-bold mb-3">
          Baselines (B1–B10) and Executable Arms
        </h4>
        <DataTable
          head={["ID", "Baseline", "What it measures"]}
          rows={[
            ["B1", "Single-Agent CoT", "Floor: no debate at all"],
            ["B2", "Single-Agent + RAG", "Single agent with evidence"],
            ["B3", "MAD (majority vote)", "Standard multi-agent debate"],
            ["B4", "MAD + RAG", "Debate with evidence; B4-matched uses the B8 partition and prompts"],
            ["B5", "Self-Consistency", "k samples, majority vote"],
            ["B6", "MoA (equal-weight)", "Multi-model, static aggregation"],
            ["B7", "Oracle (GPT-6 Luna, 3 samples)", "Optional external-answer ceiling; mean + CI + majority; not a Core arm"],
            ["B8", "Ours (trust-weighted)", "Primary system"],
            ["B8-no-trust", "Same evidence/prompts, majority", "Primary control — isolates the trust mechanism"],
            ["B8-placebo / B8-oracle", "Six-arm target", "Pending WP-18; verdicts shuffled / gold evidence (oracle definition conditional)"],
            ["B9", "iMAD", "Closest published efficiency competitor"],
            ["B10", "ConsensAgent (if feasible)", "Prompt-refinement mitigation — closest to ours in goal, most different in mechanism"],
          ]}
        />
        <p className="text-xs text-[#64748b] dark:text-[#94a3b8] mb-4">
          <strong>Executable now:</strong> B3, B4-matched, B8-no-trust, and B8
          (4 arms × GPQA 400 / MMLU-Pro 400 / HLE 200 × 2 seeds = 24 runs,
          8,000 debates, ≈46 GPU-h at 172.7 debates/h). Row 2/24 is complete
          (see §1). The 6-arm target adds B8-placebo and B8-oracle through
          WP-18. <strong>B10:</strong> ConsensAgent is the closest published
          mitigation — state-of-the-art on six reasoning datasets — but it
          refines prompts rather than scoring evidence against external sources.
          A written mechanism comparison is mandatory; full reimplementation is
          ~1 week and only if Full-run capacity allows.
        </p>

        <h4 className="text-sm font-bold mb-3">Ablation Studies</h4>
        <DataTable
          head={["Ablation", "What it isolates"]}
          rows={[
            ["No trust calibration", "Falls back to equal-weight aggregation → isolates the trust mechanism"],
            ["No progressive retrieval", "Single-shot retrieval only → isolates progressive refinement"],
            ["No source partitioning", "All agents retrieve from the same corpus → isolates partitioning"],
            ["No adaptive triggering", "Debate runs on every question → isolates the confidence gate"],
          ]}
        />
        <Callout variant="info" title="📊 Statistical Validation">
          2 random seeds for the main matrix (3 for the pilot) + 95% confidence
          intervals + paired bootstrap + Cohen's d across all comparisons.
          Preempts the common reviewer criticism of single-run comparisons in
          MAD literature.
        </Callout>

        <h4 className="text-sm font-bold mb-3">Threats to Validity</h4>
        <DataTable
          head={["Threat", "Status / mitigation"]}
          rows={[
            ["Retrieval noise and sparse coverage", "Cross-encoder reranking, citation-count filter, domain restriction; results stratified by retrieval-success rate."],
            ["Injection is an explicit, artificial upper bound", "Stated early and confidently; a 20–30 question paraphrase-robustness check is planned but currently a named protocol limitation (L2)."],
            ["Proof-only benchmarks (BrokenMath / BrokenArXiv)", "Appendix-only, 0% answer-type retention; never used for CCR."],
            ["Single-card compute ceiling", "4-bit 24–27B stack on one 96 GB card; concurrency (8 rows + CUDA graphs) is the lever, not a second GPU."],
            ["Hyperparameter sensitivity (α, β)", "Grid search before the matrix is frozen; no sensitivity result exists yet."],
            ["Trust signal may not change behaviour", "Dec 2026 calibration + pilot is the necessary condition; a negative result is reported honestly as a finding about when evidence-grounded trust does/doesn't influence aggregation."],
          ]}
        />
      </Section>

      {/* ───────────── 10. Edge Cases & Failure Handling ───────────── */}
      <Section id="edge-cases" className="animate-fade-up animate-delay-3">
        <SectionTitle icon={Shield}>
          10. Edge Cases &amp; Failure Handling
        </SectionTitle>
        <p className="text-sm mb-4">
          Each failure mode has documented detection, mitigation, and recovery.
        </p>
        <DataTable
          head={["Failure scenario", "Detection", "Mitigation", "Recovery"]}
          rows={failures.map((f) => [
            strong(f.scenario),
            f.detection,
            f.mitigation,
            f.recovery,
          ])}
        />
      </Section>

      {/* ───────────── 11. Risk Assessment ───────────── */}
      <Section
        id="risk-assessment"
        accent="amber"
        className="animate-fade-up animate-delay-4"
      >
        <SectionTitle icon={TriangleAlert}>11. Risk Assessment</SectionTitle>
        <p className="text-sm mb-4">
          The highest-likelihood risk is timeline overload from the matrix plus
          benchmark; the pre-planned mitigation is Core first, then Full only
          after Core lands. The critical risk remains Challenge C — trust must
          change behaviour — and a failed pilot is reported honestly. A newer
          novelty-erosion risk follows ConsensAgent (Findings of ACL 2025): the
          related-work section must carry an explicit mechanism comparison.
        </p>
        <RiskTable rows={risks} />
      </Section>

      {/* ───────────── 12. Roadmap & Gates ───────────── */}
      <Section id="roadmap" className="animate-fade-up animate-delay-5">
        <SectionTitle icon={Calendar}>12. Roadmap &amp; Gates</SectionTitle>
        <p className="text-sm mb-0">
          P0 released Nov 2026; pilot Dec 2026; Core Jan 2027; Full + benchmark
          Feb 2027; human eval/SDT Mar; results freeze Apr; thesis chapters May;
          submission Jun; defence Jun–Jul; paper Aug–Dec 2027. The
          month-by-month plan, Gantt chart, gates, and milestone timeline live
          on the <Link to="/roadmap" className={ROADMAP_LINK}>Roadmap page</Link>.
        </p>
      </Section>

      {/* ───────────── 13. Implementation Order ───────────── */}
      <Section
        id="implementation-order"
        accent="teal"
        className="animate-fade-up"
      >
        <SectionTitle icon={ClipboardList}>
          13. Implementation Order
        </SectionTitle>
        <p className="text-sm mb-0">
          The full build sequence with dependency reasoning is maintained on the{" "}
          <Link to="/roadmap" className={ROADMAP_LINK}>Roadmap page</Link>.
          Non-negotiable order: retrieval before the trust update; the core loop
          before B9 (iMAD); the Dec 2026 calibration + pilot before the matrix;
          and the N1 smoke + FP8 precision check before full-scale runs.
        </p>
      </Section>

      {/* ───────────── Q1 Justification ───────────── */}
      <Section
        id="publication-justification"
        className="animate-fade-up animate-delay-1"
      >
        <SectionTitle icon={Target}>Q1 Publication Justification</SectionTitle>
        <TwoCol>
          <ColBox>
            <h4 className="text-sm font-bold mb-2">Novel Mechanism</h4>
            <p className="text-sm mb-0">
              No prior work provides an in-session, evidence-grounded trust
              calibration mechanism for multi-agent debate. CCR/MPR/ECR metrics
              are new.
            </p>
          </ColBox>
          <ColBox>
            <h4 className="text-sm font-bold mb-2">Rigorous Evaluation</h4>
            <p className="text-sm mb-0">
              4 executable arms with a 6-arm target, 3 Core datasets, 2 seeds,
              and statistical testing with 95% CIs and effect sizes (Cohen's d).
            </p>
          </ColBox>
          <ColBox>
            <h4 className="text-sm font-bold mb-2">Open Reproducibility</h4>
            <p className="text-sm mb-0">
              The full protocol is released as a benchmark for future sycophancy
              mitigation research; the evaluation harness is independently
              reusable.
            </p>
          </ColBox>
          <ColBox>
            <h4 className="text-sm font-bold mb-2">Timely Topic</h4>
            <p className="text-sm mb-0">
              Inter-agent sycophancy is actively studied in 2025–2026. This
              fills the missing mitigation piece.
            </p>
          </ColBox>
        </TwoCol>
      </Section>

      {/* ───────────── 14. Supervisor Explanation ───────────── */}
      <Section
        id="supervisor-explanation"
        accent="blue"
        className="animate-fade-up"
      >
        <SectionTitle icon={GraduationCap}>
          14. Supervisor Explanation (5-Minute Pitch)
        </SectionTitle>
        <TwoCol>
          <ColBox>
            <h4 className="text-sm font-bold mb-2">The Problem (1 Sentence)</h4>
            <p className="text-sm leading-relaxed mb-0">
              When AI systems debate each other to reach better answers, a
              confident-but-wrong majority can talk a correct minority into
              changing its answer — even with no new evidence — defeating the
              purpose of having them debate.
            </p>
          </ColBox>
          <ColBox>
            <h4 className="text-sm font-bold mb-2">
              The Solution (1 Sentence)
            </h4>
            <p className="text-sm leading-relaxed mb-0">
              We make each AI's vote worth more or less depending on whether its
              claims actually check out against real scientific papers — not on
              how many other AIs agree with it.
            </p>
          </ColBox>
        </TwoCol>
        <ColBox className="mt-4">
          <h4 className="text-sm font-bold mb-2">
            Internal Workflow (Plain Language)
          </h4>
          <ol className="text-sm space-y-1 mb-0 pl-4 list-decimal">
            <li>Three different AI models answer the question independently.</li>
            <li>Each answer's claims are checked against real papers, like a fact-checker.</li>
            <li>Claims that hold up gain credibility; contradicted claims lose it.</li>
            <li>Agents see peer answers and revise, aware of their own credibility standing.</li>
            <li>The loop repeats for K=3 rounds, building an evidence trail.</li>
            <li>The final answer is a credibility-weighted vote, not a simple majority.</li>
          </ol>
        </ColBox>
        <Callout variant="info" title="📖 Worked Example">
          Given one 2023 clinical trial paper and asked "Does Drug X lower blood
          pressure in adults over 60?", three reviewers give different answers.
          The system checks each claim against the paper. It shows a modest
          effect in patients with a specific condition — matching Reviewer C.
          Their credibility goes up; A and B's go down.{" "}
          <strong>Output:</strong> "Yes, but only in [that subgroup]" with a
          citation.
        </Callout>
      </Section>

      {/* ───────────── 15. Team Explanation ───────────── */}
      <Section id="team-explanation" className="animate-fade-up animate-delay-1">
        <SectionTitle icon={Users}>
          15. Team Explanation (Beginner-Friendly)
        </SectionTitle>
        <p className="text-sm mb-4">
          <strong>Simple overview:</strong> think of three friends trying to
          answer a hard trivia question. Normally, if two agree and one
          disagrees, you would go with the two. Our system instead weights each
          friend's opinion by how well they can back it up with real sources —
          so the one friend with solid evidence can outvote the other two if
          they are just guessing confidently.
        </p>
        <DataTable
          head={["Term", "Meaning"]}
          rows={[
            ["LLM", "The AI model doing the reasoning (e.g., Qwen, Mistral)"],
            ["Multi-Agent Debate", "Multiple AI models discussing a question together"],
            ["Sycophancy", "An AI changing its answer to agree with others without good reason"],
            ["RAG", "Looking up real documents to check an answer instead of relying on AI memory"],
            ["Trust Score", "Our running credibility scorecard for each AI, updated each round"],
            ["Baseline", "An existing method we compare against to prove ours is better"],
            ["Ablation", "Removing one piece of the system to measure how much it matters"],
          ]}
        />
        <Callout variant="success" title="🧠 Analogy: Courtroom">
          Majority-vote debate is like a jury that goes with whichever two
          jurors talk the loudest. Our system is more like a judge who checks the
          evidence each juror cites — and rules on whose evidence holds up, not
          who is more persuasive or more numerous.
        </Callout>
      </Section>

      {/* ───────────── 16. Expected Research Outcome ───────────── */}
      <Section
        id="expected-outcome"
        accent="teal"
        className="animate-fade-up animate-delay-2"
      >
        <SectionTitle icon={Trophy}>16. Expected Research Outcome</SectionTitle>
        <TwoCol>
          <ColBox>
            <h4 className="text-sm font-bold mb-2">Pre-Registered Targets</h4>
            <ul className="text-sm space-y-1 mb-0 pl-4 list-disc">
              <li>
                <strong>20–30% CCR reduction</strong> vs standard MAD on
                injected-pressure benchmarks — a target, not a result.
              </li>
              <li>
                <strong>Comparison against ConsensAgent</strong> (closest
                published mitigation) on the same injected sets, with the
                mechanism difference stated explicitly.
              </li>
              <li>
                <strong>ECR &gt; 0.80</strong> on GPQA-Main; the endpoint is
                frozen before the matrix.
              </li>
              <li>
                <strong>No accuracy regression</strong> on GPQA-Main /
                MMLU-Pro STEM — anti-sycophancy gains must not cost baseline
                correctness.
              </li>
            </ul>
          </ColBox>
          <ColBox>
            <h4 className="text-sm font-bold mb-2">Publication Plan</h4>
            <p className="text-sm mb-0">
              The field moved faster than anticipated — ACL Findings 2025
              already has a published mitigation (ConsensAgent). That raises the
              bar but sharpens the contribution: to our knowledge, the only
              evidence-grounded, numeric, adversarially-tested approach. Primary
              target: <strong>TACL (rolling)</strong>, written after the thesis
              defence. Fallback: <strong>EMNLP 2028</strong>; a workshop is the
              safe floor. No result exists yet, so no venue claim is a promise.
            </p>
          </ColBox>
        </TwoCol>
        <h4 className="text-sm font-bold mt-5 mb-3">
          Success Criteria (Concrete &amp; Falsifiable)
        </h4>
        <div className="space-y-2">
          {[
            {
              icon: "📊",
              text: "Pre-registered CCR reduction over B8-no-trust on the injected sets, with 95% CIs; B3/B4-matched are controls, not headline competitors.",
            },
            {
              icon: "📐",
              text: "ECR > 0.80 on at least the primary evaluation dataset, or the calibration endpoint is reported as missed.",
            },
            {
              icon: "🧪",
              text: "The Dec 2026 calibration + pilot confirms trust weight behaviourally affects aggregation output; this is a necessary condition and reframes the result if it fails.",
            },
            {
              icon: "📝",
              text: "Completed FYDP thesis + submitted paper (minimum workshop, target TACL), with a fully reproducible codebase released.",
            },
          ].map((c) => (
            <div
              key={c.text}
              className="flex gap-3 items-start bg-[#f0f2f7] dark:bg-[rgba(255,255,255,0.04)] border border-[#e2e8f0] dark:border-[rgba(255,255,255,0.1)] rounded-md p-3"
            >
              <span className="text-lg flex-shrink-0">{c.icon}</span>
              <p className="text-sm mb-0">{c.text}</p>
            </div>
          ))}
        </div>
      </Section>

      {/* ───────────── 17. Future Extensions ───────────── */}
      <Section
        id="future-extensions"
        className="animate-fade-up animate-delay-3"
      >
        <SectionTitle icon={Telescope}>17. Future Extensions</SectionTitle>
        <TwoCol>
          <ColBox>
            <h4 className="text-sm font-bold mb-2">🎓 MSc/PhD Research</h4>
            <p className="text-sm leading-relaxed mb-0">
              Convergence properties for N &gt; 3 agents are future work. A
              PhD-scope extension could pursue formal convergence theorems
              rather than the bounded design-property propositions used here.
            </p>
          </ColBox>
          <ColBox>
            <h4 className="text-sm font-bold mb-2">🌐 Open-Source Framework</h4>
            <p className="text-sm leading-relaxed mb-0">
              The CCR/MPR/ECR harness is independently valuable — other
              researchers testing anti-sycophancy methods could adopt it as a
              standard benchmark.
            </p>
          </ColBox>
          <ColBox>
            <h4 className="text-sm font-bold mb-2">
              ⚖️ Cross-Domain Generalization
            </h4>
            <p className="text-sm leading-relaxed mb-0">
              Source-partitioned retrieval plus trust calibration generalises
              beyond scientific QA to legal reasoning against case law, medical
              reasoning against clinical literature, and other domains with
              retrievable, ground-truth-adjacent evidence.
            </p>
          </ColBox>
          <ColBox>
            <h4 className="text-sm font-bold mb-2">🧠 Cross-Session Trust Memory</h4>
            <p className="text-sm leading-relaxed mb-0">
              Long-term trust memory across sessions, multimodal evidence
              grounding, and domain-specific calibration — the canonical
              extensions named in the original proposal's future-directions
              FAQ.
            </p>
          </ColBox>
        </TwoCol>
      </Section>

      {/* ───────────── 18. Final Critical Review ───────────── */}
      <Section
        id="final-review"
        accent="rose"
        className="animate-fade-up animate-delay-4"
      >
        <SectionTitle icon={Search}>
          18. Final Critical Review (Reviewer #2 Mode)
        </SectionTitle>
        <Callout variant="gap" title="⚠ Challenging Every Assumption">
          <p className="mb-2">
            <strong>
              "Your trust formula has two free hyperparameters (α, β) — how do I
              know you didn't just tune them until the result looked good?"
            </strong>{" "}
            Planned mitigation: a hyperparameter sensitivity analysis (grid
            search) before the matrix is frozen. No sensitivity result exists
            yet. This must be prominent in the paper, not buried in an appendix.
          </p>
          <p className="mb-2">
            <strong>
              "Propositions 2–3 aren't real theorems — why call them
              Propositions at all?"
            </strong>{" "}
            They are already correctly reframed as "design properties, not
            global convergence theorems." Expect at least one reviewer to push
            on this framing.
          </p>
          <p className="mb-0">
            <strong>
              "Is 20–30% CCR reduction actually a big number, or is it modest
              window-dressing?"
            </strong>{" "}
            It needs contextualisation against the observed baseline collapse
            rate in the pilot; no baseline rate is assumed before the run.
          </p>
        </Callout>
        <h4 className="text-sm font-bold mt-4 mb-3">
          🧪 Missing Experiments a Sharp Reviewer Would Demand
        </h4>
        <DataTable
          head={["Experiment", "What to add"]}
          rows={[
            ["⏱️ Latency/Cost-Benefit Analysis", "The system runs ~9 forward passes vs 1 for single-agent. Add a compute-cost-vs-CCR-reduction table as a supplementary result."],
            ["🔄 Paraphrase Robustness", "Currently a named protocol limitation (L2), not tested. A small 20–30 question check would strengthen the paper."],
            ["🔢 K-Sensitivity (Debate Rounds)", "N-scaling is planned, but K is fixed at 3 throughout. A reviewer may ask whether results are an artifact of the round count."],
          ]}
        />
        <Callout variant="warning" title="🗣️ Reviewer Criticisms (Ranked by Severity)">
          <ol className="text-sm space-y-1 mb-0 pl-4 list-decimal">
            <li>
              <strong>
                "How is this different from ConsensAgent's prompt-refinement
                mitigation?"
              </strong>{" "}
              — ConsensAgent uses static/dynamic prompt refinement (a textual
              intervention); ours uses a numeric, formally bounded trust score
              grounded in <em>external</em> retrieved evidence. We test against
              adversarial injected pressure; they target naturally occurring
              sycophancy. Differentiation must be explicit in the §3
              related-work table.
            </li>
            <li>
              <strong>
                "How is this different from iMAD's confidence-weighted
                aggregation?"
              </strong>{" "}
              — External evidence vs same-context confidence signal; stated in
              the first paragraph of the results section.
            </li>
            <li>
              <strong>
                "Your injection protocol is artificially explicit — real
                sycophancy is subtler."
              </strong>{" "}
              — An honest upper-bound scenario, stated early and confidently.
            </li>
            <li>
              <strong>"Two core citations aren't peer-reviewed."</strong> —
              Addressed via proactive disclosure and the same framing in the
              related-work section.
            </li>
          </ol>
        </Callout>
        <p className="text-xs text-[#64748b] dark:text-[#94a3b8] mb-0">
          <strong>Load-bearing reading:</strong> schedule one dedicated session
          on ConsensAgent (Pitre et al., Findings of ACL 2025) and Estornell
          &amp; Liu (NeurIPS 2024 Main Track) before writing. Both are
          load-bearing, not optional background; re-verify both venues before
          the thesis cites them.
        </p>
      </Section>
    </>
  );
}

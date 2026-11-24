import { PageHeader } from "@/components/layout/PageHeader";
import { Callout } from "@/components/shared/Callout";
import { Section, SectionTitle } from "@/components/shared/Section";
import { Layers, ListChecks, Target, Workflow } from "lucide-react";

const th =
  "p-3 text-left font-bold bg-[#f1f5f9] dark:bg-[rgba(255,255,255,0.06)] border-b-2 border-[#e2e8f0] dark:border-[rgba(255,255,255,0.15)] whitespace-nowrap";
const td = "p-3 align-top";
const row =
  "border-b border-[#e2e8f0] dark:border-[rgba(255,255,255,0.08)] last:border-0 even:bg-[#f8fafc] dark:even:bg-[rgba(255,255,255,0.03)]";

const LOOP_STEPS = [
  {
    title: "Three heterogeneous agents",
    desc: "A panel of three heterogeneous agents debates each scientific question.",
  },
  {
    title: "Three rounds",
    desc: "Agents state, defend, and revise their positions across three debate rounds.",
  },
  {
    title: "Claim-level decomposition",
    desc: "Agent outputs are decomposed into individual claims before verification.",
  },
  {
    title: "Domain-routed evidence retrieval",
    desc: "Retrieval is routed by claim domain across PubMed, arXiv, Semantic Scholar, and OpenAlex.",
  },
  {
    title: "Per-claim verdicts",
    desc: "Each claim receives a verdict against the passages it cites.",
  },
  {
    title: "Trust update",
    desc: "Evidence accumulates in logit space, passes through one softmax, then a floor/ceiling simplex projection.",
  },
  {
    title: "Trust-weighted aggregation",
    desc: "The final answer is produced by trust-weighted aggregation of agent positions.",
  },
];

export function MethodologyPage() {
  return (
    <>
      <PageHeader
        docType="FYDP Methodology · Trust-Calibrated Deliberation"
        title={<>Methodology</>}
        subtitle="Three heterogeneous agents · three rounds · evidence-grounded trust · four Core conditions"
        coverItems={[
          { label: "Panel", value: "3 heterogeneous agents" },
          { label: "Rounds", value: "3" },
          { label: "Core Conditions", value: "4" },
          { label: "Core Matrix", value: "24 rows / 8,000 debates" },
        ]}
      />

      <main className="max-w-[1150px] mx-auto my-10 px-4 sm:px-5">
        {/* ── Deliberation loop ── */}
        <Section accent="blue">
          <SectionTitle icon={Workflow}>Deliberation Loop</SectionTitle>
          <p className="text-sm leading-relaxed mb-4">
            Agents debate a question while an external evidence check re-weights
            their influence. Trust is updated from per-claim verdicts before the
            final aggregation.
          </p>
          <div className="space-y-3">
            {LOOP_STEPS.map((step, i) => (
              <div
                key={step.title}
                className="flex gap-3 items-start bg-[#f0f2f7] dark:bg-[#1a1d35] border border-[#e2e8f0] dark:border-[rgba(255,255,255,0.1)] rounded-md p-3 sm:p-4"
              >
                <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-[#3b5bdb] text-white font-bold text-xs flex-shrink-0 shadow-[0_2px_8px_rgba(59,91,219,.35)]">
                  {i + 1}
                </span>
                <div className="min-w-0">
                  <div className="font-semibold text-sm">{step.title}</div>
                  <div className="text-xs text-[#64748b] dark:text-[#94a3b8] mt-0.5">
                    {step.desc}
                  </div>
                </div>
              </div>
            ))}
          </div>
          <Callout variant="info" title="Trust operator order" className="mb-0">
            <p className="text-sm">
              Logit accumulation → one softmax → floor/ceiling simplex
              projection. The projection applies a floor and a ceiling under a
              simplex constraint.
            </p>
          </Callout>
        </Section>

        {/* ── Arms ── */}
        <Section accent="teal">
          <SectionTitle icon={Layers}>Experimental Arms</SectionTitle>
          <p className="text-sm leading-relaxed mb-4">
            Four conditions run in Core. The Full matrix adds a placebo arm and
            a gold-answer oracle arm.
          </p>
          <div className="overflow-x-auto rounded-lg shadow-sm">
            <table className="w-full border-collapse text-xs sm:text-sm">
              <thead>
                <tr>
                  <th className={th}>Arm</th>
                  <th className={th}>Mechanism</th>
                  <th className={th}>Matrix</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["B3", "MAD, no retrieval", "Core"],
                  ["B4-matched", "RAG with the same source partition", "Core"],
                  ["B8-no-trust", "Primary control · majority aggregation", "Core"],
                  ["B8", "Treatment", "Core"],
                  [
                    "B8-placebo",
                    "Cross-agent round-pool verdict shuffle",
                    "Full",
                  ],
                  [
                    "B8-oracle",
                    "Gold-answer trust on all three datasets",
                    "Full",
                  ],
                ].map(([arm, mechanism, matrix]) => (
                  <tr key={arm} className={row}>
                    <td className={td + " font-medium whitespace-nowrap"}>
                      {arm}
                    </td>
                    <td className={td}>{mechanism}</td>
                    <td className={td}>{matrix}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-xs text-[#64748b] dark:text-[#94a3b8] mt-3">
            B8-no-trust is the primary control and uses majority aggregation;
            B8 is the treatment condition.
          </p>
        </Section>

        {/* ── Design matrix ── */}
        <Section accent="amber">
          <SectionTitle icon={ListChecks}>Design Matrix</SectionTitle>
          <div className="overflow-x-auto rounded-lg shadow-sm">
            <table className="w-full border-collapse text-xs sm:text-sm">
              <thead>
                <tr>
                  <th className={th}>Block</th>
                  <th className={th}>Design</th>
                  <th className={th}>Scale</th>
                </tr>
              </thead>
              <tbody>
                <tr className={row}>
                  <td className={td + " font-medium"}>Core</td>
                  <td className={td}>
                    4 conditions × 3 datasets × 2 seeds. Datasets: gpqa_main
                    400, mmlu_pro 400, hle 200.
                  </td>
                  <td className={td + " whitespace-nowrap"}>
                    24 rows / 8,000 debates
                  </td>
                </tr>
                <tr className={row}>
                  <td className={td + " font-medium"}>Full</td>
                  <td className={td}>36-row gold-answer alternate</td>
                  <td className={td + " whitespace-nowrap"}>
                    10,800 debates
                  </td>
                </tr>
                <tr className={row}>
                  <td className={td + " font-medium"}>Ablations</td>
                  <td className={td}>
                    no-partition, no-adaptive, no-progressive on gpqa 400 +
                    mmlu 600 × 2 seeds
                  </td>
                  <td className={td + " whitespace-nowrap"}>3 ablations</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h3 className="text-sm font-bold mt-6 mb-2 text-[#1e2d3d] dark:text-[#e2e8f0]">
            Core item counts
          </h3>
          <div className="overflow-x-auto rounded-lg shadow-sm">
            <table className="w-full border-collapse text-xs sm:text-sm">
              <thead>
                <tr>
                  <th className={th}>Dataset</th>
                  <th className={th}>Items per seed</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["gpqa_main", "400"],
                  ["mmlu_pro", "400"],
                  ["hle", "200"],
                ].map(([dataset, items]) => (
                  <tr key={dataset} className={row}>
                    <td className={td + " font-medium"}>{dataset}</td>
                    <td className={td}>{items}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <Callout variant="info" title="Host" className="mb-0">
            <p className="text-sm">
              The dev stack is retired. The host is a <strong>96 GB on-demand
              card</strong>.
            </p>
          </Callout>
        </Section>

        {/* ── Endpoints ── */}
        <Section>
          <SectionTitle icon={Target}>Pre-Registered Endpoints</SectionTitle>
          <div className="overflow-x-auto rounded-lg shadow-sm">
            <table className="w-full border-collapse text-xs sm:text-sm">
              <thead>
                <tr>
                  <th className={th}>Tier</th>
                  <th className={th}>Endpoint</th>
                  <th className={th}>Comparison</th>
                </tr>
              </thead>
              <tbody>
                {[
                  [
                    "Primary",
                    "Final-answer accuracy on pressure-eligible items",
                    "Paired B8 vs B8-no-trust",
                  ],
                  ["Co-primary", "CMR", "—"],
                  ["Secondary", "ARR", "—"],
                  ["Secondary", "Trust AUROC, Brier", "—"],
                  ["Secondary", "Verifier balanced accuracy", "—"],
                  ["Secondary", "Citation faithfulness", "—"],
                ].map(([tier, endpoint, comparison], i) => (
                  <tr key={`${tier}-${i}`} className={row}>
                    <td className={td + " font-medium whitespace-nowrap"}>
                      {tier}
                    </td>
                    <td className={td}>{endpoint}</td>
                    <td className={td}>{comparison}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Section>
      </main>
    </>
  );
}

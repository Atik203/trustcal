import { PageHeader } from "@/components/layout/PageHeader";
import { Callout } from "@/components/shared/Callout";
import { Section, SectionTitle } from "@/components/shared/Section";
import {
  ChartColumn,
  Gauge,
  ListChecks,
  Scale,
  Wallet,
} from "lucide-react";

const th =
  "p-3 text-left font-bold bg-[#f1f5f9] dark:bg-[rgba(255,255,255,0.06)] border-b-2 border-[#e2e8f0] dark:border-[rgba(255,255,255,0.15)] whitespace-nowrap";
const td = "p-3 align-top";
const row =
  "border-b border-[#e2e8f0] dark:border-[rgba(255,255,255,0.08)] last:border-0 even:bg-[#f8fafc] dark:even:bg-[rgba(255,255,255,0.03)]";

export function ResultsPage() {
  return (
    <>
      <PageHeader
        docType="FYDP Results · Core Row · GPQA-Main Seed 1"
        title={<>Results</>}
        subtitle="B8 trust-weighted vs B8-no-trust on gpqa_main seed 1 · engineering throughput · programme status"
        coverItems={[
          { label: "Debates", value: "798 (399 + 399)" },
          { label: "B8 Accuracy", value: "0.6241 (249/399)" },
          { label: "Control Accuracy", value: "0.5865 (234/399)" },
          { label: "McNemar", value: "p = 0.086, not significant" },
        ]}
      />

      <main className="max-w-[1150px] mx-auto my-10 px-4 sm:px-5">
        {/* ── Completed Core row ── */}
        <Section accent="blue">
          <SectionTitle icon={ChartColumn}>Completed Core Row</SectionTitle>
          <p className="text-sm leading-relaxed mb-4">
            One Core row is complete: <strong>gpqa_main, seed 1</strong>, with
            B8 (trust-weighted) against B8-no-trust (the primary control). Each
            arm covers 399 scored debates, <strong>798 in total</strong>, after
            q27 was quarantined.
          </p>

          <div className="overflow-x-auto rounded-lg shadow-sm">
            <table className="w-full border-collapse text-xs sm:text-sm">
              <thead>
                <tr>
                  <th className={th}>Metric</th>
                  <th className={th}>B8 (trust)</th>
                  <th className={th}>B8-no-trust (control)</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["Debates", "399", "399"],
                  [
                    "Accuracy (95% CI)",
                    "0.6241 (249/399) · CI 0.576–0.672",
                    "0.5865 (234/399) · CI 0.536–0.634",
                  ],
                  ["MPR", "0.78", "0.75"],
                  ["ARR", "0.657", "0.702"],
                  ["CCR-e", "0.102", "0.150"],
                ].map(([metric, treatment, control]) => (
                  <tr key={metric} className={row}>
                    <td className={td + " font-medium"}>{metric}</td>
                    <td className={td}>{treatment}</td>
                    <td className={td}>{control}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <h3 className="text-sm font-bold mt-7 mb-3 text-[#1e2d3d] dark:text-[#e2e8f0]">
            Paired outcomes (399 pairs)
          </h3>
          <div className="overflow-x-auto rounded-lg shadow-sm">
            <table className="w-full border-collapse text-xs sm:text-sm">
              <thead>
                <tr>
                  <th className={th}></th>
                  <th className={th}>Control correct</th>
                  <th className={th}>Control incorrect</th>
                </tr>
              </thead>
              <tbody>
                <tr className={row}>
                  <th scope="row" className="p-3 text-left font-medium">
                    B8 correct
                  </th>
                  <td className={td}>208</td>
                  <td className={td}>41</td>
                </tr>
                <tr className={row}>
                  <th scope="row" className="p-3 text-left font-medium">
                    B8 incorrect
                  </th>
                  <td className={td}>26</td>
                  <td className={td}>124</td>
                </tr>
              </tbody>
            </table>
          </div>

          <Callout variant="warning" title="Interpretation boundary" className="mb-0">
            <p className="text-sm">
              The discordant pairs split 41 (B8-only correct) to 26 (control-only
              correct). Exact McNemar{" "}
              <strong>p = 0.086</strong>, which is <strong>not significant</strong>.
              This row does not establish an efficacy difference.
            </p>
          </Callout>
        </Section>

        {/* ── Trust diagnostics ── */}
        <Section accent="teal">
          <SectionTitle icon={Scale}>Trust-Signal Diagnostics</SectionTitle>
          <p className="text-sm leading-relaxed mb-4">
            Two calibration diagnostics from the completed row.
          </p>
          <div className="overflow-x-auto rounded-lg shadow-sm">
            <table className="w-full border-collapse text-xs sm:text-sm">
              <thead>
                <tr>
                  <th className={th}>Diagnostic</th>
                  <th className={th}>Value</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["Trust AUROC", "0.518"],
                  ["Brier", "0.292"],
                ].map(([metric, value]) => (
                  <tr key={metric} className={row}>
                    <td className={td + " font-medium"}>{metric}</td>
                    <td className={td}>{value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Section>

        {/* ── Engineering measurements ── */}
        <Section accent="amber">
          <SectionTitle icon={Gauge}>Engineering Measurements</SectionTitle>
          <p className="text-sm leading-relaxed mb-4">
            Serving throughput and retrieval pacing measured alongside the run.
          </p>
          <div className="overflow-x-auto rounded-lg shadow-sm">
            <table className="w-full border-collapse text-xs sm:text-sm">
              <thead>
                <tr>
                  <th className={th}>Configuration</th>
                  <th className={th}>Throughput</th>
                  <th className={th}>Relative</th>
                </tr>
              </thead>
              <tbody>
                <tr className={row}>
                  <td className={td + " font-medium"}>
                    8 concurrent rows + CUDA graphs
                  </td>
                  <td className={td}>172.7 debates/h</td>
                  <td className={td}>
                    3.3× the eager baseline · ~69% cheaper per debate
                  </td>
                </tr>
                <tr className={row}>
                  <td className={td + " font-medium"}>
                    2-way eager baseline
                  </td>
                  <td className={td}>52.2 debates/h</td>
                  <td className={td}>—</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="overflow-x-auto rounded-lg shadow-sm mt-4">
            <table className="w-full border-collapse text-xs sm:text-sm">
              <thead>
                <tr>
                  <th className={th}>Measurement</th>
                  <th className={th}>Result</th>
                </tr>
              </thead>
              <tbody>
                <tr className={row}>
                  <td className={td + " font-medium"}>Disk cache</td>
                  <td className={td}>+2%</td>
                </tr>
                <tr className={row}>
                  <td className={td + " font-medium"}>
                    Semantic Scholar pacing
                  </td>
                  <td className={td}>
                    1 req/s quota held by the S2 pacing gate
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </Section>

        {/* ── Run status ── */}
        <Section>
          <SectionTitle icon={ListChecks}>Run Status</SectionTitle>
          <div className="overflow-x-auto rounded-lg shadow-sm">
            <table className="w-full border-collapse text-xs sm:text-sm">
              <thead>
                <tr>
                  <th className={th}>Workstream</th>
                  <th className={th}>Status</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["Core matrix", "2/24 rows done · re-run pending under the S2 gate"],
                  ["Full matrix", "Not run"],
                  ["FP8 precision replication", "Not run"],
                  ["SciClaimBench annotations", "In progress"],
                ].map(([workstream, status]) => (
                  <tr key={workstream} className={row}>
                    <td className={td + " font-medium"}>{workstream}</td>
                    <td className={td}>{status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Section>

        {/* ── Budget ── */}
        <Section accent="rose">
          <SectionTitle icon={Wallet}>Budget Position</SectionTitle>
          <div className="overflow-x-auto rounded-lg shadow-sm">
            <table className="w-full border-collapse text-xs sm:text-sm">
              <thead>
                <tr>
                  <th className={th}>Line</th>
                  <th className={th}>Value</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["Remaining programme", "23,798 debates"],
                  ["Remaining compute (all-in)", "139.13 GPU-h"],
                  ["Remaining cost (all-in)", "$209.25"],
                  ["Committed budget", "$219.25 · $10 headroom"],
                  ["Project hard stop", "$300 total"],
                  ["Spent to date", "~$53"],
                ].map(([line, value]) => (
                  <tr key={line} className={row}>
                    <td className={td + " font-medium"}>{line}</td>
                    <td className={td}>{value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-xs text-[#64748b] dark:text-[#94a3b8] mt-3">
            The remaining programme is priced at 139.13 GPU-h all-in ($209.25)
            against $219.25 committed, leaving $10 of headroom before the $300
            project hard stop.
          </p>
        </Section>
      </main>
    </>
  );
}

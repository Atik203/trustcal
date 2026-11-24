import { cn } from "@/lib/utils";

/**
 * Publication-stage budget.
 *
 * The main causal matrix runs the 4-bit 24–27B stack (~53.26 GB) on one
 * 96 GB RTX PRO 6000 at $1.50/GPU-h all-in (disk + ingress included), with
 * 8 concurrent rows and CUDA graphs: 172.7 debates/h (three runs, ±3%)
 * versus 52.2/h for the old 2-way eager baseline (3.3× faster, ~69% cheaper
 * per debate). The 73.68 GB FP8 stack is only the N1 hardware smoke plus a
 * small GPQA precision replication, not the Full matrix.
 * Core is 24 runs / 8,000 debates. Full is 32 rows / 9,600 debates at
 * 300 items/dataset with the gold-evidence oracle on SciClaimBench; the
 * 36-row gold-answer alternate is 10,800 debates. The remaining
 * 23,798-debate programme is 137.80 GPU-h ≈ $209.26; hard stop $300.
 */

interface Stage {
  name: string;
  scope: string;
  when: string;
  hours: string;
  cost: string;
  color: string;
  bg: string;
}

const STAGES: Stage[] = [
  {
    name: "Core + Full",
    scope: "14,000 not-yet-run debates · 4-bit main stack · 2 seeds",
    when: "Dec 2026–Jan 2027",
    hours: "81.06",
    cost: "$121.59",
    color: "#7c3aed",
    bg: "rgba(124,58,237,0.08)",
  },
  {
    name: "Cap increase",
    scope: "3,200 debates · GPQA 400 / MMLU-Pro 600 / HLE 400",
    when: "Jan 2027",
    hours: "18.53",
    cost: "$27.79",
    color: "#e8590c",
    bg: "rgba(232,89,12,0.08)",
  },
  {
    name: "Three ablations",
    scope: "6,000 debates · component and panel-size ablations",
    when: "Jan–Feb 2027",
    hours: "34.74",
    cost: "$52.11",
    color: "#0ca678",
    bg: "rgba(12,166,120,0.08)",
  },
  {
    name: "FP8 precision",
    scope: "600 debates · FP8 check stack (73.68 GB) · small GPQA replication",
    when: "Feb 2027",
    hours: "3.47",
    cost: "$5.21",
    color: "#475569",
    bg: "rgba(71,85,105,0.08)",
  },
  {
    name: "Setup + ingress",
    scope: "Persistent volumes, checkpoints, logs, dataset and retrieval caches",
    when: "All stages",
    hours: "—",
    cost: "$2.56",
    color: "#1c7ed6",
    bg: "rgba(28,126,214,0.08)",
  },
];

const MAIN_WEIGHTS = [
  { model: "Qwen3.8-27B-AWQ-INT4", gb: 21.0 },
  { model: "Gemma 4 26B-A4B AWQ", gb: 17.2 },
  { model: "Mistral Small 3.2 24B AWQ", gb: 15.06 },
] as const;

const MAIN_TOTAL = 53.26;
const MAIN_LIMIT = 96;

const FINAL_WEIGHTS = [
  { model: "Qwen3.8-27B-FP8", gb: 29.95 },
  { model: "Gemma 4 26B A4B FP8", gb: 28.67 },
  { model: "Mistral Small 3.2 24B AWQ", gb: 15.06 },
] as const;

const FINAL_TOTAL = 73.68;
const FINAL_LIMIT = 96;

export function CostTable() {
  return (
    <div className="rounded-lg border border-[#e2e8f0] dark:border-[rgba(255,255,255,0.08)] bg-white dark:bg-[rgba(255,255,255,0.03)] p-4 sm:p-5 space-y-5">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <h4 className="text-sm font-bold">Publication-Stage Budget</h4>
        <span className="text-[10px] font-semibold uppercase tracking-wide text-[#64748b] dark:text-[#94a3b8]">
          Measured 172.7 debates/h · $1.50/GPU-h all-in
        </span>
      </div>

      {/* Stage table */}
      <div className="overflow-x-auto rounded-lg border border-[#e2e8f0] dark:border-[rgba(255,255,255,0.08)]">
        <table className="w-full border-collapse text-xs sm:text-sm">
          <thead>
            <tr>
              {["Stage", "Scope", "When", "GPU hours", "All-in cost"].map((h) => (
                <th
                  key={h}
                  className="p-2.5 text-left font-bold bg-[#f1f5f9] dark:bg-[rgba(255,255,255,0.06)] border-b border-[#e2e8f0] dark:border-[rgba(255,255,255,0.15)]"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {STAGES.map((s) => (
              <tr
                key={s.name}
                className="border-b border-[#e2e8f0] dark:border-[rgba(255,255,255,0.08)] last:border-b-0"
              >
                <td className="p-2.5 font-bold whitespace-nowrap" style={{ color: s.color }}>
                  {s.name}
                </td>
                <td className="p-2.5 text-[#475569] dark:text-[#cbd5e1]">{s.scope}</td>
                <td className="p-2.5 font-semibold whitespace-nowrap">{s.when}</td>
                <td className="p-2.5 font-mono whitespace-nowrap">{s.hours}</td>
                <td
                  className={cn("p-2.5 font-mono font-bold whitespace-nowrap")}
                  style={{ color: s.color, background: s.bg }}
                >
                  {s.cost}
                </td>
              </tr>
            ))}
            <tr className="bg-[#f0f4ff] dark:bg-[rgba(59,91,219,0.12)]">
              <td className="p-2.5 font-extrabold whitespace-nowrap text-[#1e2d3d] dark:text-[#e2e8f0]">
                Total
              </td>
              <td className="p-2.5 font-semibold text-[#475569] dark:text-[#cbd5e1]">
                All stages · 23,798 debates · hard stop $300
              </td>
              <td className="p-2.5 font-semibold whitespace-nowrap">—</td>
              <td className="p-2.5 font-mono whitespace-nowrap">137.80</td>
              <td className="p-2.5 font-mono font-extrabold whitespace-nowrap text-[#1e2d3d] dark:text-[#e2e8f0]">
                $209.26
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <p className="text-[10px] text-[#64748b] dark:text-[#94a3b8] leading-relaxed">
        <strong>Core</strong> is the 4-bit main matrix: 24 runs / 8,000
        debates. <strong>Full</strong> is planned as the 36-row gold-answer alternate
        (10,800 debates), so the oracle also runs on gpqa and mmlu; the
        32-row gold-evidence default (9,600) is the preregistered fallback. Core + Full counts the 14,000 not-yet-run
        debates: completed Core rows and reusable Core→Full cells are excluded.
        The 96 GB FP8 stack is not the main Full
        matrix: it covers the N1 smoke plus the 600-debate GPQA precision
        replication. The remaining programme is 137.80 GPU-h ≈ $209.26 at
        $1.50/GPU-h all-in; hard stop $300. Post-FYDP scaling-law testing is
        outside this budget.
      </p>

      {/* 4-bit main-stack weight budget */}
      <div className="rounded-lg border border-[#e2e8f0] dark:border-[rgba(255,255,255,0.08)] p-3 space-y-2">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <span className="text-xs font-bold text-[#1e2d3d] dark:text-[#e2e8f0]">
            4-bit main stack — pinned weights
          </span>
          <span className="text-xs font-mono font-bold text-[#e8590c]">
            ~{MAIN_TOTAL.toFixed(1)} GB / {MAIN_LIMIT} GB
          </span>
        </div>
        <div className="h-2.5 rounded-full bg-[#e2e8f0] dark:bg-[rgba(255,255,255,0.08)] overflow-hidden">
          <div
            className="h-full rounded-full bg-[#e8590c]"
            style={{ width: `${(MAIN_TOTAL / MAIN_LIMIT) * 100}%` }}
          />
        </div>
        <div className="flex flex-wrap gap-x-4 gap-y-1 text-[10px] text-[#64748b] dark:text-[#94a3b8]">
          {MAIN_WEIGHTS.map((w) => (
            <span key={w.model}>
              {w.model} <strong className="font-mono">{w.gb.toFixed(2)} GB</strong>
            </span>
          ))}
          <span className="font-semibold">0.33/0.29/0.28 vLLM utilization · 8k context</span>
        </div>
        <p className="text-[10px] text-[#64748b] dark:text-[#94a3b8] leading-relaxed">
          Core and Full main causal matrix on one 96 GB RTX PRO 6000 at
          $1.50/GPU-h all-in. Full default is 32 rows (9,600 debates); the
          36-row gold-answer alternate is 10,800 debates. Serving uses CUDA
          graphs (no --enforce-eager), --max-num-seqs 32 and
          --disable-log-requests.
        </p>
      </div>

      {/* FP8 check-stack weight budget */}
      <div className="rounded-lg border border-[#e2e8f0] dark:border-[rgba(255,255,255,0.08)] p-3 space-y-2">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <span className="text-xs font-bold text-[#1e2d3d] dark:text-[#e2e8f0]">
            96 GB FP8 check stack — pinned weights
          </span>
          <span className="text-xs font-mono font-bold text-[#0ca678]">
            {FINAL_TOTAL.toFixed(2)} GB / {FINAL_LIMIT} GB
          </span>
        </div>
        <div className="h-2.5 rounded-full bg-[#e2e8f0] dark:bg-[rgba(255,255,255,0.08)] overflow-hidden">
          <div
            className="h-full rounded-full bg-[#0ca678]"
            style={{ width: `${(FINAL_TOTAL / FINAL_LIMIT) * 100}%` }}
          />
        </div>
        <div className="flex flex-wrap gap-x-4 gap-y-1 text-[10px] text-[#64748b] dark:text-[#94a3b8]">
          {FINAL_WEIGHTS.map((w) => (
            <span key={w.model}>
              {w.model} <strong className="font-mono">{w.gb.toFixed(2)} GB</strong>
            </span>
          ))}
          <span className="font-semibold">0.33/0.29/0.28 vLLM utilization · 8k context</span>
        </div>
        <p className="text-[10px] text-[#64748b] dark:text-[#94a3b8] leading-relaxed">
          N1 hardware smoke + small GPQA precision replication only. The main
          matrix is the 4-bit 24–27B stack (~53.3 GB) on one 96 GB RTX PRO
          6000, not this FP8 stack.
        </p>
      </div>

      {/* Benchmark ladder */}
      <div className="rounded-lg border border-[#e2e8f0] dark:border-[rgba(255,255,255,0.08)] bg-[#f8fafc] dark:bg-[rgba(255,255,255,0.02)] p-3">
        <div className="text-[10px] font-bold uppercase tracking-wide text-[#64748b] dark:text-[#94a3b8] mb-1.5">
          Benchmark ladder
        </div>
        <div className="flex flex-wrap items-center gap-2 text-[11px]">
          {[
            { label: "180", tag: "floor", color: "#0ca678" },
            { label: "300", tag: "target", color: "#3b5bdb" },
            { label: "600", tag: "stretch", color: "#f08c00" },
            { label: "800", tag: "no-go", color: "#e03131" },
          ].map((b) => (
            <span
              key={b.tag}
              className="rounded-full px-2 py-0.5 font-bold"
              style={{ color: b.color, background: `${b.color}14` }}
            >
              {b.label} <span className="font-medium">{b.tag}</span>
            </span>
          ))}
        </div>
      </div>

      <p className="text-[10px] text-[#94a3b8] leading-relaxed">
        All-in = GPU + disk + ingress at $1.50/GPU-h. Measured 172.7 debates/h
        (three runs, ±3%; 8 concurrent rows + CUDA graphs) versus 52.2/h for
        the old 2-way eager baseline: 3.3× faster and ~69% cheaper per debate.
        Core is 24 runs /
        8,000 debates (~46 GPU-h); Full is 32 rows / 9,600 debates; the 36-row
        alternate is 10,800. The remaining 23,798-debate programme is 137.80
        GPU-h ≈ $209.26; hard stop $300. Prices are volatile — re-run the
        market query before renting.
      </p>

      <p className="text-[10px] text-[#94a3b8] leading-relaxed">
        B7 external-answer ceiling (optional): OpenAI GPT-6 Luna — 3
        samples/question; ~$3–9 per 1,000; mean single-call accuracy + CI +
        3-sample majority. Not a Core arm; outside the GPU envelope.
      </p>
    </div>
  );
}

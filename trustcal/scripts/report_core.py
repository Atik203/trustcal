"""Rebuild the Core milestone section (table + figures) from records.

The supervisor report includes ``core_auto.tex`` inside landscape pages. At
each milestone (100, 150, ... 400 pairs) this script regenerates that file from
the local mirror, then the report is recompiled and pushed.

    python scripts/report_core.py --b8 ... --ctl ... --out core_auto.tex
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trustcal.eval.metrics import summarize  # noqa: E402

MILESTONES = [100, 150, 200, 250, 300, 350, 400]
XTICKS = "100,150,200,250,300,350,400"


def load(path: Path) -> list[dict]:
    rows: list[dict] = []
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    for index, line in enumerate(lines):
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            if index == len(lines) - 1:
                print(f"warning: skipping torn trailing line in {path}")
                continue
            raise
    return sorted(rows, key=lambda row: int(str(row["question_id"]).rsplit("-", 1)[-1]))


def cut(rows: list[dict], n: int) -> list[dict]:
    return rows[:n] if n > 0 and len(rows) >= n else []


def metrics(rows: list[dict]) -> dict:
    if not rows:
        return {}
    summary = summarize(rows).as_dict()
    endpoints = summary["endpoints"]
    times = [row["elapsed_s"] for row in rows]
    return {
        "n": len(rows),
        "acc": summary["accuracy"],
        "ci": (summary["accuracy_ci_low"], summary["accuracy_ci_high"]),
        "mpr": summary["mpr"],
        "arr": (endpoints["arr"]["value"], endpoints["arr"]["n"]),
        "ccr": (endpoints["ccr_e"]["value"], endpoints["ccr_e"]["n"]),
        "auroc": (endpoints["trust_auroc"]["value"], endpoints["trust_auroc"]["n"]),
        "brier": (endpoints["trust_brier"]["value"], endpoints["trust_brier"]["n"]),
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "verdicts": sum(len(row.get("verdicts") or []) for row in rows),
        "passages": sum(
            len(block.get("passages") or [])
            for row in rows
            for block in (row.get("evidence") or [])
        ),
    }


def pair(value, n) -> str:
    if value is None:
        return "---"
    return f"{value:.2f}" + (f" ({n})" if n is not None else "")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--b8", required=True)
    parser.add_argument("--ctl", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--fig", default=None, help="PNG path (default: core_figures.png beside --out)")
    args = parser.parse_args()

    b8 = load(Path(args.b8))
    ctl = load(Path(args.ctl))
    current = min(len(b8), len(ctl))

    targets: list[tuple[str, int]] = []
    for milestone in MILESTONES:
        if cut(b8, milestone) and cut(ctl, milestone):
            targets.append((str(milestone), milestone))
    if current and all(current != target for _label, target in targets):
        targets.append((f"current ({current})", current))

    points: list[dict] = []
    rows_a: list[str] = []
    rows_b: list[str] = []
    ctl_by_qid = {row["question_id"]: row for row in ctl}
    for label, target in targets:
        m8 = metrics(cut(b8, target))
        mc = metrics(cut(ctl, target))
        pair_times = [
            max(row["elapsed_s"], ctl_by_qid[row["question_id"]]["elapsed_s"])
            for row in b8[:target]
            if row["question_id"] in ctl_by_qid
        ]
        mean_pair = statistics.mean(pair_times) if pair_times else 0
        rows_a.append(
            f"{label} & {m8['acc']:.2f} ({m8['ci'][0]:.2f}--{m8['ci'][1]:.2f}) & "
            f"{mc['acc']:.2f} ({mc['ci'][0]:.2f}--{mc['ci'][1]:.2f}) & {m8['mpr']:.2f} & {mc['mpr']:.2f} & "
            f"{pair(*m8['arr'])} & {pair(*mc['arr'])} \\\\"
        )
        rows_b.append(
            f"{label} & {pair(*m8['ccr'])} & {pair(*mc['ccr'])} & {pair(*m8['auroc'])} & "
            f"{pair(*m8['brier'])} & {mean_pair:.0f} \\\\"
        )
        points.append(
            {
                "n": target,
                "acc": m8["acc"],
                "low": m8["ci"][0],
                "high": m8["ci"][1],
                "cacc": mc["acc"],
                "clow": mc["ci"][0],
                "chigh": mc["ci"][1],
                "mpr": m8["mpr"],
                "cmpr": mc["mpr"],
                "ccr": m8["ccr"][0],
                "cccr": mc["ccr"][0],
                "pair": mean_pair,
            }
        )

    total = metrics(b8)
    total_c = metrics(ctl)
    debates = len(b8) + len(ctl)
    verdicts = (total.get("verdicts", 0) or 0) + (total_c.get("verdicts", 0) or 0)
    passages = (total.get("passages", 0) or 0) + (total_c.get("passages", 0) or 0)
    pair_times = [
        max(row["elapsed_s"], ctl_by_qid[row["question_id"]]["elapsed_s"])
        for row in b8
        if row["question_id"] in ctl_by_qid
    ]
    mean_pair = statistics.mean(pair_times) if pair_times else 0
    gpu_h = len(pair_times) * mean_pair / 3600

    prose = (
        "\\section*{3. Core milestone results (\\texttt{gpqa\\_main}, seed 1)}\\label{sec:core}\n\n"
        f"At this checkpoint the row holds \\textbf{{{debates} debates}} "
        f"({len(b8)} B8, {len(ctl)} control), {debates * 9} agent-round responses, "
        f"{verdicts:,} claim-level verdicts, and {passages:,} retrieved passages. "
        f"The row has consumed approximately {gpu_h:.1f} GPU-hours; the mean question pair takes "
        f"{mean_pair:.0f}\\,s (median {total.get('median', 0):.0f}\\,s for B8). "
        "Both arms run concurrently, so a pair finishes in the slower arm's time rather than their sum. "
        f"Milestones completed: "
        + (", ".join(str(point["n"]) for point in points) if points else "none")
        + f"; next milestone: {next((m for m in MILESTONES if m > current), 400)}. "
        "Question 27 is quarantined (options are literal letters) and is excluded from the denominators; "
        "the row resumes at the first question id without a record.\n\n"
    )

    table = (
        "{\\Large\\setlength{\\tabcolsep}{6pt}\n"
        "\\begin{tabular}{lcccccc}\n"
        "\\toprule\n"
        "Questions & B8 acc (95\\% CI) & Control acc (95\\% CI) & B8 MPR & Control MPR & "
        "B8 ARR (n) & Control ARR (n) \\\\\n"
        "\\midrule\n"
        + ("\n".join(rows_a) if rows_a else "% no data")
        + "\n\\bottomrule\n\\end{tabular}\n}\n\n"
        "{\\Large\\setlength{\\tabcolsep}{6pt}\n"
        "\\begin{tabular}{lccccc}\n"
        "\\toprule\n"
        "Questions & B8 CCR-e (n) & Control CCR-e (n) & B8 AUROC (n) & B8 Brier (n) & "
        "Pair mean (s) \\\\\n"
        "\\midrule\n"
        + ("\n".join(rows_b) if rows_b else "% no data")
        + "\n\\bottomrule\n\\end{tabular}\n}\n\n"
    )

    abbrev = (
        "{\\normalsize\\textit{Abbreviations:} MPR = minority-position retention; "
        "ARR = adaptation rate when the majority is correct; CCR-e = collapse rate on "
        "evidence-exposed items; AUROC = area under the ROC curve; Brier = Brier score "
        "(lower is better); n = applicable debates.}\n\n"
    )

    figures = ""
    fig_path = Path(args.fig) if args.fig else Path(args.out).with_name("core_figures.png")
    if points:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        plt.rcParams.update(
            {
                "font.size": 20,
                "axes.titlesize": 24,
                "axes.labelsize": 22,
                "legend.fontsize": 18,
                "xtick.labelsize": 18,
                "ytick.labelsize": 18,
                "axes.spines.top": False,
                "axes.spines.right": False,
            }
        )
        ns = [point["n"] for point in points]
        b8_color, ctl_color = "#1f4e79", "#c55a11"
        fig, axes = plt.subplots(2, 2, figsize=(16, 9.6))

        ax = axes[0][0]
        ax.errorbar(
            ns,
            [p["acc"] for p in points],
            yerr=[
                [p["acc"] - p["low"] for p in points],
                [p["high"] - p["acc"] for p in points],
            ],
            fmt="o-",
            color=b8_color,
            capsize=6,
            linewidth=2.4,
            markersize=9,
            label="B8 (trust)",
        )
        ax.errorbar(
            ns,
            [p["cacc"] for p in points],
            yerr=[
                [p["cacc"] - p["clow"] for p in points],
                [p["chigh"] - p["cacc"] for p in points],
            ],
            fmt="s--",
            color=ctl_color,
            capsize=6,
            linewidth=2.4,
            markersize=9,
            label="Control (majority)",
        )
        ax.set_title("Accuracy (95% CI)")
        ax.set_ylabel("accuracy")
        ax.set_ylim(0, 1)
        ax.legend(loc="lower right")
        ax.grid(alpha=0.3)

        ax = axes[0][1]
        ax.plot(ns, [p["mpr"] for p in points], "o-", color=b8_color, linewidth=2.4, markersize=9)
        ax.plot(ns, [p["cmpr"] for p in points], "s--", color=ctl_color, linewidth=2.4, markersize=9)
        ax.set_title("Minority-position retention (MPR)")
        ax.set_ylabel("MPR")
        ax.set_ylim(0, 1)
        ax.grid(alpha=0.3)

        ax = axes[1][0]
        ax.plot(ns, [p["ccr"] for p in points], "o-", color=b8_color, linewidth=2.4, markersize=9)
        ax.plot(ns, [p["cccr"] for p in points], "s--", color=ctl_color, linewidth=2.4, markersize=9)
        ax.set_title("Collapse on exposed items (CCR-e)")
        ax.set_ylabel("CCR-e")
        ax.set_xlabel("questions completed (pairs)")
        ax.set_ylim(0, 1)
        ax.grid(alpha=0.3)

        ax = axes[1][1]
        ax.plot(ns, [p["pair"] for p in points], "o-", color="#2e7d32", linewidth=2.4, markersize=9)
        ax.set_title("Question pair time")
        ax.set_ylabel("seconds")
        ax.set_xlabel("questions completed (pairs)")
        ax.set_ylim(0, max(60, max(p["pair"] for p in points) * 1.15))
        ax.grid(alpha=0.3)

        for row in axes:
            for panel in row:
                panel.set_xlim(0, 420)
                panel.set_xticks(range(0, 401, 50))

        fig.tight_layout()
        fig.savefig(fig_path, dpi=600, bbox_inches="tight")
        plt.close(fig)
        figures = (
            "\\clearpage\n"
            "\\begin{center}\n"
            "\\includegraphics[width=24cm,height=15cm,keepaspectratio]"
            "{core_figures.png}\n"
            "\\end{center}\n"
        )

    Path(args.out).write_text(prose + table + abbrev + figures, encoding="utf-8")
    print(f"wrote {args.out}: {len(points)} point(s), current n={current}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

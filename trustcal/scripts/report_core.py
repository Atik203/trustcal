"""Rebuild the Core milestone section (table + pgfplots figure) from records.

The supervisor report includes ``core_auto.tex`` inside a landscape page. At
each milestone (100, 150, ... 400 pairs) this script regenerates that file from
the local mirror, then the report is recompiled and pushed.

    python scripts/report_core.py \
        --b8 results/core3/live/B8/gpqa_main/seed1/records.jsonl \
        --ctl results/core3/live/B8-no-trust/B8/gpqa_main/seed1/records.jsonl \
        --out ../docs/supervisor_report/core_auto.tex
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
    """First ``n`` records in question order (empty when not enough)."""
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


def num(value, digits: int = 2) -> str:
    return "---" if value is None else f"{value:.{digits}f}"


def pair(value, n) -> str:
    if value is None:
        return "---"
    return f"{value:.2f}" + (f" ({n})" if n is not None else "")


def row_for(name: str, m: dict) -> str:
    if not m:
        return f"{name} & --- & --- & --- & --- & --- & --- & --- & --- & --- \\\\"
    low, high = m["ci"]
    return (
        f"{name} & {m['n']} & {m['acc']:.2f} ({low:.2f}--{high:.2f}) & {m['mpr']:.2f} & "
        f"{pair(*m['arr'])} & {pair(*m['ccr'])} & {pair(*m['auroc'])} & {pair(*m['brier'])} & "
        f"{m['median']:.0f} \\\\"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--b8", required=True)
    parser.add_argument("--ctl", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    b8 = load(Path(args.b8))
    ctl = load(Path(args.ctl))
    current = min(len(b8), len(ctl))

    points = []
    rows_tex = []
    targets: list[tuple[str, int]] = []
    for milestone in MILESTONES:
        if metrics(cut(b8, milestone)) and metrics(cut(ctl, milestone)):
            targets.append((str(milestone), milestone))
    if current and all(current != target for _label, target in targets):
        targets.append((f"current ({current})", current))

    for label, target in targets:
        m8 = metrics(cut(b8, target))
        mc = metrics(cut(ctl, target))
        ctl_by_qid = {row["question_id"]: row for row in ctl}
        pair_times = [
            max(row["elapsed_s"], ctl_by_qid[row["question_id"]]["elapsed_s"])
            for row in b8[:target]
            if row["question_id"] in ctl_by_qid
        ]
        mean_pair = statistics.mean(pair_times) if pair_times else 0
        rows_tex.append(
            f"{label} & {m8['acc']:.2f} ({m8['ci'][0]:.2f}--{m8['ci'][1]:.2f}) & "
            f"{mc['acc']:.2f} ({mc['ci'][0]:.2f}--{mc['ci'][1]:.2f}) & {m8['mpr']:.2f} & {mc['mpr']:.2f} & "
            f"{pair(*m8['arr'])} & {pair(*mc['arr'])} & {pair(*m8['ccr'])} & {pair(*mc['ccr'])} & "
            f"{mean_pair:.0f} \\\\"
        )
        points.append((target, m8["acc"], m8["ci"][0], m8["ci"][1], mc["acc"], mc["ci"][0], mc["ci"][1]))

    total = metrics(b8)
    total_c = metrics(ctl)
    debates = len(b8) + len(ctl)
    verdicts = (total.get("verdicts", 0) or 0) + (total_c.get("verdicts", 0) or 0)
    passages = (total.get("passages", 0) or 0) + (total_c.get("passages", 0) or 0)
    pair_times = []
    for row in b8:
        qid = int(row["question_id"].rsplit("-", 1)[-1])
        other = next((r for r in ctl if int(r["question_id"].rsplit("-", 1)[-1]) == qid), None)
        if other is not None:
            pair_times.append(max(row["elapsed_s"], other["elapsed_s"]))
    mean_pair = statistics.mean(pair_times) if pair_times else 0
    gpu_h = len(pair_times) * mean_pair / 3600

    prose = (
        "\\section*{3. Core milestone results (\\texttt{gpqa\\_main}, seed 1)}\\label{sec:core}\n\n"
        f"At this checkpoint the row holds \\textbf{{{debates} debates}} "
        f"({len(b8)} B8, {len(ctl)} control), {debates * 9} agent-round responses, "
        f"{verdicts:,} claim-level verdicts, and {passages:,} retrieved passages. "
        f"The row has consumed approximately {gpu_h:.1f} GPU-hours; the mean question pair takes "
        f"{mean_pair:.0f}\\,s (median {total.get('median', 0):.0f}\\,s for B8). "
        "Both arms run concurrently, so a pair finishes in the slower arm's time rather than their sum.\n\n"
        f"Milestones completed so far: "
        + (", ".join(str(p[0]) for p in points) if points else "none")
        + f"; next milestone: {next((m for m in MILESTONES if m > current), 400)}. "
        "Question 27 is quarantined (options are literal letters) and is excluded from the denominators; "
        "the row resumes at the first question id without a record.\n\n"
    )

    table = (
        "{\\large\\setlength{\\tabcolsep}{4pt}\n"
        "\\begin{tabular}{lccccccccc}\n"
        "\\toprule\n"
        "Questions & B8 acc (95\\% CI) & Control acc (95\\% CI) & B8 MPR & Control MPR & "
        "B8 ARR (n) & Control ARR (n) & B8 CCR-e (n) & Control CCR-e (n) & Pair mean " + "\\\\" + "\n"
        "\\midrule\n"
        + ("\n".join(rows_tex) if rows_tex else "% no milestone reached yet")
        + "\n\\bottomrule\n\\end{tabular}\n}\n\n"
    )

    plot = ""
    if points:
        coords_b8 = " ".join(
            f"({n},{acc:.3f}) += (0,{acc - low:.3f}) -= (0,{high - acc:.3f})"
            for n, acc, low, high, _cacc, _clow, _chigh in points
        )
        coords_ctl = " ".join(
            f"({n},{cacc:.3f}) += (0,{cacc - clow:.3f}) -= (0,{chigh - cacc:.3f})"
            for n, _acc, _low, _high, cacc, clow, chigh in points
        )
        plot = (
            "\\begin{center}\n"
            "\\begin{tikzpicture}\n"
            "\\begin{axis}[width=0.88\\textwidth, height=0.38\\textheight, "
            "xlabel={questions completed (pairs)}, ylabel={accuracy}, ymin=0, ymax=1, "
            "xtick={100,150,200,250,300,350,400}, grid=major, "
            "legend style={font=\\large, at={(0.02,0.98)}, anchor=north west}, "
            "tick label style={font=\\large}, label style={font=\\large}, "
            "title style={font=\\Large}]\n"
            "\\addplot+[only marks, mark=*, line width=1.2pt, error bars/.cd, y dir=both, y explicit] "
            "coordinates {" + coords_b8 + "};\n"
            "\\addlegendentry{B8 (trust)}\n"
            "\\addplot+[only marks, mark=square*, line width=1.2pt, error bars/.cd, y dir=both, y explicit] "
            "coordinates {" + coords_ctl + "};\n"
            "\\addlegendentry{Control (majority)}\n"
            "\\end{axis}\n\\end{tikzpicture}\n\\end{center}\n"
        )

    abbrev = (
        "{\\small\\textit{Abbreviations:} MPR = minority-position retention; "
        "ARR = adaptation rate when the majority is correct; CCR-e = collapse rate on "
        "evidence-exposed items; AUROC = area under the ROC curve; Brier = Brier score "
        "(lower is better); n = applicable debates.}\n\n"
    )

    Path(args.out).write_text(prose + table + abbrev + plot, encoding="utf-8")
    print(f"wrote {args.out}: {len(points)} milestone point(s), current n={current}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

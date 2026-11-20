"""Validate a dataset sample before any GPU spend.

The runner already rejects an invalid record at write time, but by then the
debate has been paid for and the process exits (GPQA question 28 carried a
bare-letter ``answer`` next to the real ``Correct Answer`` text). This check
applies the same question-level invariants to the exact sampled slice a run
will use, so a bad row fails in seconds with no GPU cost.

    python scripts/check_questions.py --dataset gpqa_main --limit 400
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trustcal.eval.datasets import load_dataset, validate_questions  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default="gpqa_main", help="dataset name from configs/datasets.yaml")
    parser.add_argument("--limit", type=int, default=400, help="questions the run will sample")
    parser.add_argument("--split", default=None, help="override the configured split")
    args = parser.parse_args()

    questions = load_dataset(args.dataset, split=args.split, sample_cap=args.limit)[: args.limit]
    problems = validate_questions(questions)
    print(f"{args.dataset}: {len(questions)} sampled, {len(problems)} problem(s)")
    for problem in problems[:40]:
        print(" ", problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

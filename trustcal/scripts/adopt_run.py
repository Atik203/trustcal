"""Adopt a legacy run directory into the sample-locked provenance scheme.

A directory written before sample locks existed has records but no lock or
condition. Adoption freezes the *parent* sample (captured at the parent
commit), verifies every record against it, writes the lock/condition files,
and records the parent manifest hash in ``adoption.json``. Records are never
modified, and the current loader's sample is never substituted.

    python scripts/adopt_run.py --run-dir results/core3/B8/gpqa_main/seed1 \
        --parent-sample results/core3/parent_sample.json \
        --dataset gpqa_main --limit 400 --sample-seed 1 \
        --reason "resume after resilience layer" --operator "atik"
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trustcal.provenance import (  # noqa: E402
    build_condition,
    build_sample_lock,
    ensure_condition,
    load_adoption,
    load_sample_lock,
    read_records_repaired,
    verify_records_against_lock,
    write_adoption,
    write_sample_lock,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--parent-sample", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--sample-seed", type=int, default=1)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--operator", required=True)
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    questions = json.loads(Path(args.parent_sample).read_text(encoding="utf-8"))
    if len(questions) != args.limit:
        raise SystemExit(f"parent sample has {len(questions)} questions, expected {args.limit}")

    lock_path = run_dir / "sample.lock.json"
    expected = build_sample_lock(args.dataset, questions, args.limit, args.sample_seed)
    if lock_path.is_file():
        lock = load_sample_lock(lock_path)
        if lock["lock_hash"] != expected["lock_hash"]:
            raise SystemExit("existing sample.lock.json does not match --parent-sample")
    else:
        lock = expected
        write_sample_lock(lock_path, lock)
        print(f"wrote {lock_path} ({len(questions)} questions, {lock['lock_hash'][:12]})")

    records, duplicates = read_records_repaired(run_dir / "records.jsonl")
    if duplicates:
        raise SystemExit(f"duplicate question ids in records: {sorted(set(duplicates))[:5]}")
    problems = verify_records_against_lock(records, questions, args.dataset)
    if problems:
        raise SystemExit("records disagree with the parent sample:\n  " + "\n  ".join(problems[:10]))

    manifest_path = run_dir / "run_manifest.json"
    if not manifest_path.is_file():
        raise SystemExit(f"missing {manifest_path}; cannot recover the parent condition")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    condition = build_condition(manifest["run_config"], lock)
    ensure_condition(run_dir / "condition.json", condition)
    print(f"condition {condition['condition_hash'][:12]} ({len(records)} records verified)")

    adoption = load_adoption(run_dir / "adoption.json")
    known = {parent.get("manifest_hash") for parent in adoption.get("parents") or []}
    parents = sorted({record.get("manifest_hash") for record in records if record.get("manifest_hash")})
    for parent in parents:
        if parent in known:
            continue
        write_adoption(
            run_dir / "adoption.json",
            parent,
            str(manifest.get("code_commit", "unknown")),
            len(records),
            args.reason,
            args.operator,
        )
        print(f"adopted parent manifest {str(parent)[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

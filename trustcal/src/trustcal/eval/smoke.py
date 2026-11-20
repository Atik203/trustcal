"""Pure checks for the model-swap smoke test (script: scripts/smoke_test.py)."""

from __future__ import annotations

import math

from ..agents import claims_or_fallback


def check_records(records: list[dict], rounds: int, require_injection: bool = False) -> list[str]:
    """Return human-readable failures; empty list = smoke test passed."""
    failures: list[str] = []
    if not records:
        return ["no records produced"]

    for record in records:
        qid = record.get("question_id", "?")
        if record.get("rounds_completed") != rounds:
            failures.append(f"{qid}: rounds_completed={record.get('rounds_completed')} != {rounds}")
        entries = record.get("rounds") or []
        if len(entries) != rounds:
            failures.append(f"{qid}: {len(entries)} answer rounds, expected {rounds}")
        for index, entry in enumerate(entries, start=1):
            answers = entry.get("answers") or []
            if not answers or any(not str(a).strip() for a in answers):
                failures.append(f"{qid}: empty answer in round {index}")

        final_text = (record.get("transcript") or [{}])[-1].get("positions") or []
        for index, text in enumerate(final_text):
            if not claims_or_fallback(text):
                failures.append(f"{qid}: no parseable claims for agent {index + 1}")

        trajectory = record.get("trust_trajectory")
        if trajectory:
            for round_index, scores in enumerate(trajectory, start=1):
                if not scores or any(math.isnan(float(s)) for s in scores):
                    failures.append(f"{qid}: NaN/empty trust in round {round_index}")
                elif abs(sum(float(s) for s in scores) - 1.0) > 1e-6:
                    failures.append(f"{qid}: trust does not sum to 1 in round {round_index}")

        if require_injection:
            injection = record.get("injection") or {}
            targets = injection.get("targets") or []
            if injection.get("eligible"):
                if not targets:
                    failures.append(f"{qid}: injection eligible but no targets")
                else:
                    # The injection is a one-shot round-2 message. A model can
                    # change under it and then revert by round 3; that is still
                    # proof the message was delivered and acted on. Check any
                    # round at or after delivery, not only the final round.
                    first_answers = (entries[0].get("answers") if entries else []) or []
                    injection_round = int(injection.get("round") or 2)
                    post_rounds = entries[max(0, injection_round - 1):] if entries else []
                    changed = any(
                        i < len(first_answers)
                        and i < len(entry.get("answers") or [])
                        and first_answers[i] != entry["answers"][i]
                        for i in targets
                        for entry in post_rounds
                    )
                    if not changed:
                        failures.append(f"{qid}: injection did not change any targeted agent")

    return failures

"""Sample locks, condition/provenance hashes, repair and quarantine."""

from __future__ import annotations

import json

import pytest

from .provenance import (
    ConditionMismatch,
    ProvenanceMismatch,
    RecordCorruption,
    SampleLockMismatch,
    append_quarantine,
    build_condition,
    build_sample_lock,
    ensure_condition,
    ensure_provenance,
    ensure_sample_lock,
    load_sample_lock,
    read_records_repaired,
    verify_records_against_lock,
)


def _question(text: str = "Q?", answer: str = "a") -> dict:
    return {"question": text, "answer": answer, "options": ["a", "b"]}


def test_lock_round_trip_and_no_reload(tmp_path) -> None:
    path = tmp_path / "sample.lock.json"
    questions, lock = ensure_sample_lock(path, "gpqa", 1, 1, lambda: [_question()])
    assert questions == [_question()]
    assert load_sample_lock(path)["lock_hash"] == lock["lock_hash"]

    def explode():
        raise AssertionError("loader must not run when a lock exists")

    again, _ = ensure_sample_lock(path, "gpqa", 1, 1, explode)
    assert again == [_question()]


def test_lock_hash_tamper_is_refused(tmp_path) -> None:
    path = tmp_path / "sample.lock.json"
    ensure_sample_lock(path, "gpqa", 1, 1, lambda: [_question()])
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["questions"][0]["answer"] = "b"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(SampleLockMismatch, match="hash"):
        load_sample_lock(path)


def test_condition_change_is_refused(tmp_path) -> None:
    lock = build_sample_lock("gpqa", [_question()], 1, 1)
    first = build_condition({"alpha": 0.5}, lock)
    second = build_condition({"alpha": 0.9}, lock)
    path = tmp_path / "condition.json"
    ensure_condition(path, first)
    with pytest.raises(ConditionMismatch, match="run_config"):
        ensure_condition(path, second)


def test_provenance_change_needs_consent(tmp_path) -> None:
    path = tmp_path / "manifest_history.jsonl"
    first = {"provenance_hash": "a", "provenance": {"code_commit": "1"}}
    second = {"provenance_hash": "b", "provenance": {"code_commit": "2"}}
    ensure_provenance(path, first, None, "op", 0, "cond")
    with pytest.raises(ProvenanceMismatch, match="accept-provenance-change"):
        ensure_provenance(path, second, None, "op", 0, "cond")
    ensure_provenance(path, second, "fix: docs only", "op", 0, "cond")
    entries = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert len(entries) == 2
    assert entries[1]["reason"] == "fix: docs only"
    assert entries[1]["operator"] == "op"


def test_trailing_torn_line_is_truncated(tmp_path) -> None:
    path = tmp_path / "records.jsonl"
    path.write_text('{"question_id":"a"}\n{"question_id":"b"}\n{"question_id":', encoding="utf-8")
    records, duplicates = read_records_repaired(path)
    assert [record["question_id"] for record in records] == ["a", "b"]
    assert duplicates == []
    assert path.read_text(encoding="utf-8").endswith('{"question_id":"b"}\n')


def test_middle_corruption_is_fatal(tmp_path) -> None:
    path = tmp_path / "records.jsonl"
    path.write_text('{"question_id":"a"}\nnot json\n{"question_id":"b"}\n', encoding="utf-8")
    with pytest.raises(RecordCorruption):
        read_records_repaired(path)


def test_duplicate_qid_keeps_first(tmp_path) -> None:
    path = tmp_path / "records.jsonl"
    path.write_text('{"question_id":"a","v":1}\n{"question_id":"a","v":2}\n', encoding="utf-8")
    records, duplicates = read_records_repaired(path)
    assert [record["v"] for record in records] == [1]
    assert duplicates == ["a"]


def test_adoption_verification() -> None:
    question = _question()
    good = [
        {
            "question_id": "gpqa-0000",
            "question": question["question"],
            "gold": question["answer"],
            "options_raw": question["options"],
        }
    ]
    assert verify_records_against_lock(good, [question], "gpqa") == []
    bad = [dict(good[0], question="different")]
    assert verify_records_against_lock(bad, [question], "gpqa")


def test_quarantine_append(tmp_path) -> None:
    path = tmp_path / "quarantine.jsonl"
    append_quarantine(path, "q1", "bad gold", "prov")
    entry = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
    assert entry["question_id"] == "q1"
    assert entry["error"] == "bad gold"

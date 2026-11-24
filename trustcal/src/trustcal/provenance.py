"""Row resilience: sample locks, condition/provenance hashes, quarantine.

A run directory used to be bound to one manifest hash that included the git
commit, so any code change refused a resume. This module separates the two
questions that hash was answering:

* ``condition_hash`` — what experiment is this? Dataset, the exact sampled
  questions (locked), models, prompt, seed, decoding, trust/retrieval
  parameters. It must match on resume.
* ``provenance_hash`` — which code produced this record? Commit, dirty-tree
  digest, runner version. It may change with explicit operator consent, and
  every value is recorded in ``manifest_history.jsonl``.

Nothing rewrites a record's stored hashes. A torn trailing JSONL line is
repaired on read; a bad question is quarantined instead of killing the row.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

from .manifest import (
    DEFAULT_DATASETS,
    DEFAULT_MODELS,
    DEFAULT_PROMPTS,
    ManifestMismatch,
    _code_commit,
    _dataset_revisions,
    _file_sha256,
    _model_checkpoints,
)

SCHEMA_LOCK = "sample-lock-v1"
SCHEMA_CONDITION = "condition-v1"
SCHEMA_ADOPTION = "adoption-v1"
RUNNER_VERSION = "2"

LOCK_NAME = "sample.lock.json"
CONDITION_NAME = "condition.json"
HISTORY_NAME = "manifest_history.jsonl"
QUARANTINE_NAME = "quarantine.jsonl"
ADOPTION_NAME = "adoption.json"
RUN_LOCK_NAME = ".run.lock"


class ConditionMismatch(ManifestMismatch):
    """The row's experimental condition changed; reuse is not allowed."""


class ProvenanceMismatch(ManifestMismatch):
    """The code version changed without explicit operator consent."""


class SampleLockMismatch(RuntimeError):
    """The locked sample is missing, corrupt, or incompatible with the run."""


class RecordCorruption(RuntimeError):
    """A non-trailing JSONL line is invalid; refuse to guess."""


class RunLocked(RuntimeError):
    """Another process owns this run directory."""


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _atomic_write(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def _serialize_question(question: dict) -> dict:
    """Keep the full question (pilot rows carry verdicts/evidence fields)."""
    return dict(question)


def build_sample_lock(dataset: str, questions: list[dict], limit: int, sample_seed: int) -> dict:
    """Lock the exact sampled list; the loader is never consulted on resume."""
    ids = [f"{dataset}-{index:04d}" for index in range(len(questions))]
    payload = {
        "schema": SCHEMA_LOCK,
        "dataset": dataset,
        "sample_seed": int(sample_seed),
        "limit": int(limit),
        "question_ids": ids,
        "questions": [_serialize_question(question) for question in questions],
    }
    payload["lock_hash"] = digest(payload)
    return payload


def lock_hash(payload: dict) -> str:
    body = {key: value for key, value in payload.items() if key != "lock_hash"}
    return digest(body)


def write_sample_lock(path: Path, payload: dict) -> None:
    _atomic_write(path, json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=1) + "\n")


def load_sample_lock(path: Path) -> dict:
    if not path.is_file():
        raise SampleLockMismatch(f"sample lock missing: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SampleLockMismatch(f"sample lock unreadable: {path}: {exc}") from exc
    if payload.get("schema") != SCHEMA_LOCK:
        raise SampleLockMismatch(f"sample lock schema {payload.get('schema')!r} is not {SCHEMA_LOCK}")
    if payload.get("lock_hash") != lock_hash(payload):
        raise SampleLockMismatch(f"sample lock hash mismatch: {path}")
    if len(payload.get("question_ids") or []) != len(payload.get("questions") or []):
        raise SampleLockMismatch(f"sample lock id/question count mismatch: {path}")
    return payload


def ensure_sample_lock(
    path: Path,
    dataset: str,
    limit: int,
    sample_seed: int,
    loader: Callable[[], list[dict]],
) -> tuple[list[dict], dict]:
    """Return the locked questions, creating the lock on first use."""
    if path.is_file():
        payload = load_sample_lock(path)
        if payload["dataset"] != dataset:
            raise SampleLockMismatch(
                f"sample lock dataset {payload['dataset']!r} != run dataset {dataset!r}"
            )
        if payload["limit"] != limit:
            raise SampleLockMismatch(
                f"sample lock limit {payload['limit']} != run limit {limit}"
            )
        return list(payload["questions"]), payload
    questions = loader()
    if not questions:
        raise SampleLockMismatch("loader returned no questions; refusing to write an empty lock")
    questions = list(questions)[:limit]
    payload = build_sample_lock(dataset, questions, limit, sample_seed)
    write_sample_lock(path, payload)
    return list(payload["questions"]), payload


def build_condition(
    run_config: dict,
    lock: dict,
    models_path: Path | str = DEFAULT_MODELS,
    prompts_path: Path | str = DEFAULT_PROMPTS,
    datasets_path: Path | str = DEFAULT_DATASETS,
) -> dict:
    condition = {
        "sample_lock_hash": lock["lock_hash"],
        "run_config": run_config,
        "model_checkpoints": _model_checkpoints(models_path),
        "prompt_hash": _file_sha256(prompts_path),
        "dataset_revisions": _dataset_revisions(datasets_path),
    }
    return {"schema": SCHEMA_CONDITION, "condition_hash": digest(condition), "condition": condition}


def ensure_condition(path: Path, current: dict) -> dict:
    if path.is_file():
        try:
            previous = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ConditionMismatch(f"condition file unreadable: {path}: {exc}") from exc
        if previous.get("condition_hash") != current["condition_hash"]:
            prior = previous.get("condition") or {}
            now = current.get("condition") or {}
            differing = [key for key in sorted(set(prior) | set(now)) if prior.get(key) != now.get(key)]
            raise ConditionMismatch(
                f"resume refused: {path} condition differs in {', '.join(differing)}; "
                "a different experiment needs a new run directory"
            )
        return previous
    _atomic_write(path, json.dumps(current, ensure_ascii=False, sort_keys=True, indent=1) + "\n")
    return current


def _git_state() -> tuple[bool, str]:
    try:
        status = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
        diff = subprocess.run(
            ["git", "diff", "HEAD"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
        )
    except (OSError, subprocess.SubprocessError):
        return False, "unknown"
    dirty = bool(status.stdout.strip())
    payload = status.stdout + "\n" + diff.stdout
    return dirty, "clean" if not payload.strip() else hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_provenance(commit: str | None = None) -> dict:
    dirty, diff_digest = _git_state()
    payload = {
        "code_commit": commit or _code_commit(),
        "worktree_dirty": dirty,
        "code_diff_sha256": diff_digest,
        "runner_version": RUNNER_VERSION,
    }
    return {"provenance_hash": digest(payload), "provenance": payload}


def read_history(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def known_provenance(path: Path) -> set[str]:
    return {entry["provenance_hash"] for entry in read_history(path) if "provenance_hash" in entry}


def append_history(path: Path, entry: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def ensure_provenance(
    path: Path,
    provenance: dict,
    accept_change: str | None,
    operator: str | None,
    records_before: int,
    condition_hash: str,
) -> dict:
    seen = known_provenance(path)
    current = provenance["provenance_hash"]
    if not seen:
        entry = {
            "session_id": uuid.uuid4().hex,
            "started_at": utc_now(),
            "condition_hash": condition_hash,
            "provenance_hash": current,
            "code_commit": provenance["provenance"].get("code_commit", "unknown"),
            "worktree_dirty": provenance["provenance"].get("worktree_dirty", False),
            "code_diff_sha256": provenance["provenance"].get("code_diff_sha256", "unknown"),
            "runner_version": provenance["provenance"].get("runner_version", "unknown"),
            "operator": operator,
            "reason": "initial session",
            "records_before": records_before,
        }
        append_history(path, entry)
        return entry
    if current in seen:
        return {"provenance_hash": current, "reused": True}
    if not accept_change:
        raise ProvenanceMismatch(
            f"code changed under a live row ({path}): provenance {current} is not in "
            f"{sorted(seen)}; rerun with --accept-provenance-change \"<reason>\" --operator \"<name>\""
        )
    entry = {
        "session_id": uuid.uuid4().hex,
        "started_at": utc_now(),
        "condition_hash": condition_hash,
        "provenance_hash": current,
        "code_commit": provenance["provenance"].get("code_commit", "unknown"),
        "worktree_dirty": provenance["provenance"].get("worktree_dirty", False),
        "code_diff_sha256": provenance["provenance"].get("code_diff_sha256", "unknown"),
        "runner_version": provenance["provenance"].get("runner_version", "unknown"),
        "operator": operator,
        "reason": accept_change,
        "records_before": records_before,
    }
    append_history(path, entry)
    return entry


def read_records_repaired(path: Path) -> tuple[list[dict], list[str]]:
    """Parse records, repair a torn trailing line, audit duplicate qids.

    The last line may be torn by a crash mid-write; it is truncated and the
    question is re-run. A bad non-trailing line is fatal: silently dropping it
    could hide corruption. Duplicate qids keep the first valid record.
    """
    if not path.is_file():
        return [], []
    data = path.read_bytes()
    lines = data.splitlines(keepends=True)
    records: list[dict] = []
    duplicates: list[str] = []
    seen: set[str] = set()
    offset = 0
    for index, raw in enumerate(lines):
        if not raw.strip():
            offset += len(raw)
            continue
        try:
            record = json.loads(raw)
        except json.JSONDecodeError:
            if index == len(lines) - 1:
                path.write_bytes(data[:offset])
                break
            raise RecordCorruption(f"{path}: invalid JSON at line {index + 1}")
        qid = str(record.get("question_id") or "")
        if qid and qid in seen:
            duplicates.append(qid)
        elif qid:
            seen.add(qid)
            records.append(record)
        else:
            records.append(record)
        offset += len(raw)
    return records, duplicates


def append_quarantine(path: Path, question_id: str, error: str, provenance_hash: str, error_type: str = "schema") -> None:
    entry = {
        "question_id": question_id,
        "error_type": error_type,
        "error": error,
        "attempts": 1,
        "provenance_hash": provenance_hash,
        "timestamp": utc_now(),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def read_quarantine(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def acquire_run_lock(path: Path) -> None:
    if path.exists():
        try:
            pid = int(path.read_text(encoding="utf-8").strip() or "0")
        except (OSError, ValueError):
            pid = 0
        if pid > 0:
            try:
                os.kill(pid, 0)
            except OSError:
                pass
            else:
                raise RunLocked(f"run directory is already owned by pid {pid}: {path}")
        path.unlink(missing_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    except FileExistsError as exc:
        raise RunLocked(f"run directory is already locked: {path}") from exc
    os.write(fd, str(os.getpid()).encode("ascii"))
    os.close(fd)


def release_run_lock(path: Path) -> None:
    path.unlink(missing_ok=True)


def load_adoption(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def adopted_manifest_hashes(path: Path) -> set[str]:
    payload = load_adoption(path)
    parents = payload.get("parents") or []
    return {str(parent.get("manifest_hash")) for parent in parents if parent.get("manifest_hash")}


def verify_records_against_lock(records: Iterable[dict], questions: list[dict], dataset: str) -> list[str]:
    """Return mismatches between stored records and the locked questions."""
    problems: list[str] = []
    by_index = {f"{dataset}-{index:04d}": question for index, question in enumerate(questions)}
    for record in records:
        qid = str(record.get("question_id") or "")
        question = by_index.get(qid)
        if question is None:
            problems.append(f"{qid}: not in the lock")
            continue
        if str(record.get("question")) != str(question.get("question")):
            problems.append(f"{qid}: question text differs from the lock")
        if str(record.get("gold")) != str(question.get("answer")):
            problems.append(f"{qid}: gold differs from the lock")
        options_raw = record.get("options_raw")
        if options_raw is not None and list(options_raw) != list(question.get("options") or []):
            problems.append(f"{qid}: options_raw differs from the lock")
    return problems


def write_adoption(
    path: Path,
    parent_manifest_hash: str,
    parent_commit: str,
    checked_records: int,
    reason: str,
    operator: str,
) -> dict:
    payload = load_adoption(path)
    payload.setdefault("schema", SCHEMA_ADOPTION)
    payload.setdefault("parents", [])
    payload["parents"].append(
        {
            "manifest_hash": parent_manifest_hash,
            "commit": parent_commit,
            "checked_records": checked_records,
            "reason": reason,
            "operator": operator,
            "created_at": utc_now(),
        }
    )
    _atomic_write(path, json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=1) + "\n")
    return payload


def sleep_briefly(seconds: float = 0.0) -> None:
    if seconds:
        time.sleep(seconds)

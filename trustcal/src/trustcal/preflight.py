"""Preflight checks — validate everything that costs money *before* a paid run.

Each check returns a CheckResult; `run_preflight` collects them and the CLI exits
non-zero on any failure, so a broken pod session aborts before model calls pile up.
"""

from __future__ import annotations

import json
import os
import shutil
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from .agents import AGENT_INITIAL, AGENT_REVISION, AGENT_SYSTEM
from .config import (
    AgentConfig,
    ModelConfig,
    agents_for_phase,
    default_phase,
    load_models,
    max_model_len_for_phase,
)

MIN_FREE_GB = 10.0
MIN_FREE_GB_BY_PHASE = {"dev": 30.0, "fourbit": 70.0, "final": 90.0}
CHARS_PER_TOKEN = 4
PEER_TRUNCATE_CHARS = 1500  # must match orchestrator/debate.py
OWN_POSITION_EST_CHARS = 4096  # one generation at the 1024-token output cap


def resolve_hf_home(explicit: Path | str | None = None) -> Path:
    """The cache directory setup.sh and serve.sh use, in the same order.

    A new shell does not inherit setup.sh's exports, so preflight must resolve
    the same path itself or it reports a false cache miss on a perfectly good
    pod. Keep this in sync with ``setup.sh`` and ``scripts/serve.sh``.
    """
    if explicit is not None:
        return Path(explicit)
    env = os.getenv("HF_HOME", "").strip()
    if env:
        return Path(env)
    workspace = Path("/workspace")
    if workspace.is_dir() and os.access(workspace, os.W_OK):
        return workspace / ".cache" / "huggingface"
    return Path.home() / ".cache" / "huggingface"


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str

    def line(self) -> str:
        return f"{'OK  ' if self.ok else 'FAIL'} {self.name:<16} {self.detail}"


def check_servers(agents: list[AgentConfig], timeout: float = 10.0) -> list[CheckResult]:
    """Every configured port serves exactly the configured model id."""
    results = []
    for agent in agents:
        name = f"server:{agent.port}"
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{agent.port}/v1/models", timeout=timeout) as resp:
                served = [m["id"] for m in json.load(resp).get("data", [])]
            if agent.model in served:
                results.append(CheckResult(name, True, agent.model))
            else:
                results.append(CheckResult(name, False, f"expected {agent.model!r}, served {served}"))
        except Exception as exc:  # noqa: BLE001
            results.append(CheckResult(name, False, str(exc)))
    return results


def _cache_dir(hf_home: Path, model_id: str) -> Path:
    return Path(hf_home) / "hub" / f"models--{model_id.replace('/', '--')}"


def _cache_state(path: Path) -> tuple[bool, str]:
    """A snapshot is usable only with config + weights and no partial blobs.

    ``hf download`` writes ``*.incomplete`` under ``blobs/`` until a file is
    finished. Checking only "some file exists" (the old behaviour) let a killed
    download pass preflight and fail later during vLLM startup — after the GPU
    clock had started.
    """
    path = Path(path)
    snapshots = path / "snapshots"
    if not snapshots.is_dir():
        return False, f"missing {snapshots}"

    incomplete = list((path / "blobs").glob("*.incomplete"))
    if incomplete:
        return False, f"{len(incomplete)} incomplete blob(s) under {path / 'blobs'}"

    for snapshot in sorted(snapshots.iterdir()):
        if not snapshot.is_dir():
            continue
        if not (snapshot / "config.json").is_file():
            continue
        weights = list(snapshot.glob("*.safetensors")) + list(snapshot.glob("*.bin"))
        if weights:
            return True, str(snapshot)
    return False, f"no snapshot with config.json + weight files under {snapshots}"


def check_cache(agents: list[AgentConfig], hf_home: Path) -> list[CheckResult]:
    """Model weights are already on disk and complete — a miss means paid ingress."""
    results = []
    for agent in agents:
        name = f"cache:{agent.role}"
        path = _cache_dir(hf_home, agent.model)
        ok, detail = _cache_state(path)
        results.append(CheckResult(name, ok, detail if ok else f"{detail} — expect a re-download"))
    return results


def check_disk(path: Path, min_free_gb: float = MIN_FREE_GB) -> CheckResult:
    try:
        target = Path(path)
        while not target.exists() and target.parent != target:
            target = target.parent
        free_gb = shutil.disk_usage(target).free / 1e9
        ok = free_gb >= min_free_gb
        return CheckResult("disk", ok, f"{free_gb:.1f}GB free (min {min_free_gb:.0f}GB) at {target}")
    except Exception as exc:  # noqa: BLE001
        return CheckResult("disk", False, str(exc))


def check_context_budget(max_model_len: int, max_tokens: int) -> CheckResult:
    """Worst-case revision prompt fits inside (max_model_len - max_tokens)."""
    worst_prompt_chars = (
        len(AGENT_SYSTEM)
        + len(AGENT_INITIAL)
        + len(AGENT_REVISION)
        + 3 * PEER_TRUNCATE_CHARS
        + OWN_POSITION_EST_CHARS
    )
    estimated_tokens = worst_prompt_chars / CHARS_PER_TOKEN
    available = max_model_len - max_tokens
    ok = estimated_tokens <= available * 0.95
    return CheckResult(
        "context",
        ok,
        f"worst-case prompt ~{estimated_tokens:.0f} tok vs {available} available (max_model_len {max_model_len})",
    )


def check_hf_token() -> CheckResult:
    token = os.getenv("HF_TOKEN", "").strip()
    return CheckResult("hf_token", bool(token), "set" if token else "missing — gated datasets will 401")


def check_offline(hf_home: Path, enabled: bool) -> CheckResult:
    if not enabled:
        return CheckResult("offline", True, "not requested (ok when the cache is complete)")
    flag = os.getenv("HF_HUB_OFFLINE", "") == "1"
    return CheckResult("offline", flag, "HF_HUB_OFFLINE=1" if flag else "HF_HUB_OFFLINE not set")


def run_preflight(
    model_config: Path | str = "configs/models.yaml",
    hf_home: Path | None = None,
    offline: bool = False,
    max_tokens: int = 1024,
    phase: str | None = None,
) -> list[CheckResult]:
    """All checks, in fail-fast order for a human reading the output."""
    cfg: ModelConfig = load_models(model_config)
    selected = phase or default_phase()
    agents = agents_for_phase(cfg, selected)
    home = resolve_hf_home(hf_home)

    results: list[CheckResult] = []
    results += check_servers(agents)
    results += check_cache(agents, home)
    results.append(check_disk(home, MIN_FREE_GB_BY_PHASE.get(selected, MIN_FREE_GB)))
    results.append(check_context_budget(max_model_len_for_phase(cfg, selected), max_tokens))
    results.append(check_hf_token())
    results.append(check_offline(home, offline))
    return results


def format_report(results: list[CheckResult]) -> str:
    lines = [r.line() for r in results]
    failed = [r.name for r in results if not r.ok]
    lines.append("RESULT: OK" if not failed else f"RESULT: FAIL - {', '.join(failed)}")
    return "\n".join(lines)

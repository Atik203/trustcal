"""Serial vs parallel equivalence for the debate-loop fan-out.

The thread fan-out in ``DebateRunner`` (LLM calls) and ``Retriever`` (shared
caches with lock-guarded inserts) must reproduce the serial loop exactly:
same positions, verdicts, records, routes and errors. If any of these fail,
the parallel path is a method change, not an optimization.
"""

from __future__ import annotations

import pytest

from ..retrieval.pipeline import Retriever, RetrievalConfig
from ..retrieval.sources import SearchResult
from .debate import DebateRunner
from .test_debate import FakeClient


def _result(source: str, query: str, tag: str = "") -> SearchResult:
    return SearchResult(
        source=source,
        title=f"{query} paper",
        abstract=f"{query} evidence from {source} {tag}".strip(),
        url=f"https://example.com/{source}/{query}",
    )


def _clients(n: int = 3) -> list[FakeClient]:
    return [FakeClient(f"agent{i}") for i in range(1, n + 1)]


def _run(parallel: bool, **kw) -> dict:
    return DebateRunner(clients=_clients(), rounds=3, parallel_calls=parallel, **kw).run(
        "What is 6*7?"
    )


def _canon(out: dict) -> dict:
    """Drop fields that legitimately vary run to run (none expected here)."""
    return out


def test_parallel_matches_serial() -> None:
    serial = _canon(_run(False))
    for _ in range(3):
        assert _canon(_run(True)) == serial


def test_parallel_matches_serial_with_retrieval() -> None:
    def search(source: str, query: str, top_k: int = 5) -> list[SearchResult]:
        return [_result(source, query)]

    def make(parallel: bool) -> tuple[dict, Retriever]:
        retriever = Retriever(config=RetrievalConfig(top_k=2, prompt_passages=2), search_fn=search)
        out = DebateRunner(
            clients=_clients(), rounds=2, retriever=retriever, parallel_calls=parallel
        ).run("What is 6*7?")
        return out, retriever

    serial_out, serial_ret = make(False)
    for _ in range(3):
        out, ret = make(True)
        assert out == serial_out
        assert ret.routes == serial_ret.routes
        assert ret.errors == serial_ret.errors


def test_parallel_tie_claims_single_route_entry() -> None:
    """Every agent repeating the same claim must log one route, not three."""
    calls: list[tuple[str, str]] = []

    def search(source: str, query: str, top_k: int = 5) -> list[SearchResult]:
        calls.append((source, query))
        return [_result(source, query, tag="supports this")]

    retriever = Retriever(config=RetrievalConfig(top_k=2, prompt_passages=2), search_fn=search)
    out = DebateRunner(clients=_clients(), rounds=2, retriever=retriever, parallel_calls=True).run(
        "What is 6*7?"
    )
    serial = DebateRunner(
        clients=_clients(), rounds=2, retriever=Retriever(config=RetrievalConfig(top_k=2, prompt_passages=2), search_fn=search),
        parallel_calls=False,
    ).run("What is 6*7?")
    assert out == serial
    routes = [r for r in retriever.routes if r["claim"] == "because arithmetic"]
    assert len(routes) == 1


def test_parallel_failing_source_identical() -> None:
    """A dead source must produce identical outputs and error sets."""

    def search(source: str, query: str, top_k: int = 5) -> list[SearchResult]:
        if source == "pubmed":
            raise ConnectionError("boom")
        return [_result(source, query, tag="ok")]

    def make(parallel: bool) -> tuple[dict, Retriever]:
        retriever = Retriever(
            config=RetrievalConfig(top_k=2, prompt_passages=2, max_source_failures=100),
            search_fn=search,
        )
        out = DebateRunner(
            clients=_clients(), rounds=2, retriever=retriever, parallel_calls=parallel
        ).run("What is 6*7?")
        return out, retriever

    serial_out, serial_ret = make(False)
    par_out, par_ret = make(True)
    assert par_out == serial_out
    assert sorted(par_ret.errors) == sorted(serial_ret.errors)
    assert par_ret.routes == serial_ret.routes


def test_retriever_lock_present() -> None:
    import threading

    assert isinstance(Retriever()._lock, type(threading.Lock()))

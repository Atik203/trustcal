"""Claim-routed, progressive retrieval with a cache (P0-8, §5.5).

`Retriever` is the only object the debate loop talks to. It owns:
  * claim -> domain routing (PubMed / arXiv / S2 / OpenAlex) and a route log,
  * progressive depth (fewer passages in early rounds),
  * de-duplication by DOI / arXiv ID / normalized title (and passage text),
  * equal evidence volume: every agent sees the same number of passages for the
    same claim, whether source partitioning is on (an ablation) or off,
  * a per-run cache so repeated claims cost one request,
  * graceful failure: a dead API yields no passages (trust abstains) and is
    recorded in ``errors`` instead of killing a paid session.

Partitioning is no longer "agent A = PubMed, agent B = arXiv". When enabled it
rotates the *claim-routed* source order per agent (so source diversity is an
item-level property, not an agent-level confound) and falls through to the
remaining routed sources when the first returns too little. The candidate set
and the target volume are identical in both conditions.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable

from . import sources
from .verdicts import lexical_score, rerank

SearchFn = Callable[..., list[sources.SearchResult]]


@dataclass(frozen=True)
class RetrievalConfig:
    top_k: int = 5
    prompt_passages: int = 3
    max_chars: int = 1200
    partition: bool = True
    progressive: bool = True
    # Passage ranking must match the declared verifier. `auto` preserves the
    # old try-cross-encoder-then-lexical behaviour; the default is explicit so a
    # sentence-transformers install cannot put a hidden GPU model in the runner.
    rerank: str = "lexical"
    # Cost guard: a keyless API that is down must not add 60s to every claim.
    # After this many consecutive failures the source is skipped for the run.
    max_source_failures: int = 3

    def __post_init__(self) -> None:
        if self.rerank not in {"lexical", "cross-encoder", "auto"}:
            raise ValueError(
                f"unknown rerank {self.rerank!r}; expected lexical, cross-encoder, or auto"
            )


def _rotate(items: tuple[str, ...], offset: int) -> tuple[str, ...]:
    if not items:
        return items
    index = offset % len(items)
    return items[index:] + items[:index]


def _lexical_scorer(claim: str, passages: list[str]) -> list[float]:
    return [lexical_score(claim, passage) for passage in passages]


class _SourceGate:
    """Cross-process minimum interval for one upstream source.

    Semantic Scholar allows 1 request/second cumulatively across all endpoints,
    so eight concurrent runner processes cannot each call it freely. A plain
    in-process lock is not enough (there are eight of them), and a blocking
    global lock would stall debates. This gate serializes across processes with
    an atomic directory create, enforces the interval, and gives up after
    ``timeout_s`` so a claim falls through to its next source instead of waiting.

    State is one file per source in the system temp directory, so it is shared by
    every process on the host without a server or a dependency.
    """

    def __init__(self, source: str, interval_s: float, state_dir: Path | None = None) -> None:
        self.interval_s = interval_s
        base = state_dir or Path(tempfile.gettempdir())
        self._gate = base / f"trustcal_gate_{source}.lock"
        self._stamp = base / f"trustcal_gate_{source}.ts"
        self._thread_lock = threading.Lock()

    def acquire(self, timeout_s: float = 3.0) -> bool:
        if self.interval_s <= 0:
            return True
        deadline = time.monotonic() + timeout_s
        with self._thread_lock:
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return False
                try:
                    self._gate.mkdir()
                except FileExistsError:
                    if time.monotonic() >= deadline:
                        return False
                    time.sleep(0.02)
                    continue
                except OSError:
                    return True  # unwritable temp dir: never block a run
                try:
                    last = 0.0
                    try:
                        last = float(self._stamp.read_text().strip() or 0)
                    except (OSError, ValueError):
                        last = 0.0
                    wait = self.interval_s - (time.time() - last)
                    if wait > 0:
                        # Refuse rather than return early: returning after a
                        # partial sleep would let callers exceed the quota
                        # while believing they waited their turn.
                        if wait > max(deadline - time.monotonic(), 0.0):
                            return False
                        time.sleep(wait)
                    self._stamp.write_text(f"{time.time():.6f}")
                finally:
                    try:
                        self._gate.rmdir()
                    except OSError:
                        pass
                return True


def _source_gates() -> dict[str, _SourceGate]:
    """Parse TRUSTCAL_SOURCE_MIN_INTERVAL, e.g. 'semantic_scholar=1.0'."""
    raw = os.getenv("TRUSTCAL_SOURCE_MIN_INTERVAL", "").strip()
    gates: dict[str, _SourceGate] = {}
    for part in raw.split(","):
        if "=" not in part:
            continue
        name, _, value = part.partition("=")
        try:
            gates[name.strip()] = _SourceGate(name.strip(), float(value))
        except ValueError:
            continue
    return gates


def select_evidence(passages: Iterable[str], k: int) -> list[str]:
    """De-duplicate passages by normalized text, then take the first ``k``.

    Callers pass a ranked list; uniqueness is required because the same paper
    can arrive from two sources with different truncation/casing.
    """
    if k <= 0:
        return []
    seen: set[str] = set()
    selected: list[str] = []
    for passage in passages:
        key = sources.normalize_text(passage)
        if not key or key in seen:
            continue
        seen.add(key)
        selected.append(passage)
        if len(selected) >= k:
            break
    return selected


@dataclass
class Retriever:
    search_fn: SearchFn | None = None
    config: RetrievalConfig = field(default_factory=RetrievalConfig)
    errors: list[str] = field(default_factory=list)
    routes: list[dict] = field(default_factory=list)
    _cache: dict[tuple[str, str, int], list[sources.SearchResult]] = field(default_factory=dict, repr=False)
    _route_cache: dict[str, sources.ClaimRoute] = field(default_factory=dict, repr=False)
    _failures: dict[str, int] = field(default_factory=dict, repr=False)
    _dead_sources: set[str] = field(default_factory=set, repr=False)
    _source_locks: dict[str, threading.Lock] = field(default_factory=dict, repr=False)
    # Guards the shared caches/logs when the debate loop fans retrieval out
    # over threads (DebateRunner parallel_calls). Each upstream source gets its
    # own fetch lock: the APIs rate-limit per source, and a cross-source burst
    # silently loses passages (gpqa-0002 fetched 3 of 9), but different sources
    # do not compete for one quota. Serializing per source keeps the evidence
    # intact while PubMed/arXiv/S2/OpenAlex still fetch in parallel.
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False, compare=False)
    _cache_dir: Path | None = field(default=None, repr=False, compare=False)
    _excluded: frozenset[str] = field(default_factory=frozenset, repr=False, compare=False)
    _gates: dict[str, _SourceGate] = field(default_factory=dict, repr=False, compare=False)

    def __post_init__(self) -> None:
        if self.search_fn is None:
            self.search_fn = sources.search
        raw = os.getenv("TRUSTCAL_RETRIEVAL_CACHE", "").strip()
        self._cache_dir = Path(raw) if raw else None
        if self._cache_dir is not None:
            self._cache_dir.mkdir(parents=True, exist_ok=True)
        # Comma-separated source names to drop after routing. Set it to
        # semantic_scholar for any concurrent run: that API allows 1 request per
        # second cumulatively, so a 12-24 request burst can only 429.
        excluded = os.getenv("TRUSTCAL_EXCLUDE_SOURCES", "").strip()
        self._excluded = frozenset(s.strip() for s in excluded.split(",") if s.strip())
        self._gates = _source_gates()

    def _disk_path(self, key: tuple[str, str, int]) -> Path | None:
        if self._cache_dir is None:
            return None
        digest = hashlib.sha256(
            "\x00".join((key[0], key[1], str(key[2]))).encode("utf-8")
        ).hexdigest()[:32]
        # Shard by the first byte: a full programme writes ~200k entries, and
        # one flat directory that large makes lookups and listings slow.
        shard = self._cache_dir / digest[:2]
        shard.mkdir(parents=True, exist_ok=True)
        return shard / f"{digest}.json"

    def _read_disk(self, path: Path) -> list[sources.SearchResult] | None:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            return [sources.SearchResult(**row) for row in payload]
        except Exception:  # missing, truncated, or schema drift: refetch
            return None

    def _write_disk(self, path: Path, results: list[sources.SearchResult]) -> None:
        try:
            tmp = path.with_suffix(".tmp")
            tmp.write_text(
                json.dumps([r.as_dict() for r in results], ensure_ascii=False),
                encoding="utf-8",
            )
            os.replace(tmp, path)
        except Exception:  # a cache write must never fail a run
            pass

    def route(self, claim: str, domain: str | None = None) -> sources.ClaimRoute:
        """Routing decision for a claim, cached and logged once per distinct call."""
        key = f"{domain}:{claim}" if domain else claim
        hit = self._route_cache.get(key)
        if hit is None:
            with self._lock:
                hit = self._route_cache.get(key)
                if hit is None:
                    hit = sources.route_claim(claim, domain)
                    self._route_cache[key] = hit
                    self.routes.append(hit.as_dict())
        return hit

    def source_names(self, agent_index: int, claim: str | None = None) -> tuple[str, ...]:
        """Candidate sources in query order for this claim/agent.

        Without a claim the legacy all-source order is returned. Partitioning
        only rotates the routed candidates; it never adds or removes a domain's
        sources, so evidence volume cannot differ by condition.

        ``excluded`` is applied after routing so every arm drops the same
        sources. It exists for a quota that cannot serve a concurrent run:
        Semantic Scholar allows 1 request/second cumulatively, which a
        12-24-request burst always exceeds, so those calls only produce 429s.
        """
        if not claim:
            candidates = sources.SOURCES
        else:
            routed = self.route(claim).sources
            candidates = routed if not self.config.partition else _rotate(routed, agent_index)
        if self._excluded:
            candidates = tuple(s for s in candidates if s not in self._excluded)
        return candidates

    def _source_lock(self, source: str) -> threading.Lock:
        """Per-source fetch lock, created on first use under the global lock."""
        with self._lock:
            lock = self._source_locks.get(source)
            if lock is None:
                lock = threading.Lock()
                self._source_locks[source] = lock
            return lock

    def _search(self, source: str, query: str, top_k: int) -> list[sources.SearchResult]:
        if source in self._dead_sources:
            return []
        key = (source, query, top_k)
        hit = self._cache.get(key)
        if hit is not None:
            return hit
        # Disk cache: a claim's evidence is deterministic for a given
        # (source, query, top_k), so a prefetch pass makes every later run free
        # and removes the API wait from the debate loop entirely.
        disk_path = self._disk_path(key)
        if disk_path is not None and disk_path.is_file():
            stored = self._read_disk(disk_path)
            if stored is not None:
                with self._lock:
                    self._cache.setdefault(key, stored)
                    return self._cache[key]
        # One in-flight fetch per source: the APIs rate-limit per source, so a
        # burst of same-source calls loses passages. Different sources run in
        # parallel because their quotas are independent.
        with self._source_lock(source):
            hit = self._cache.get(key)
            if hit is not None:
                return hit
            if source in self._dead_sources:
                return []
            # Paced source: spend a token or fall through to the next source.
            # A skip is not a failure, so it never marks the source dead.
            gate = self._gates.get(source)
            if gate is not None and not gate.acquire():
                return []
            try:
                results = list(self.search_fn(source, query, top_k=top_k))
                failed: Exception | None = None
            except Exception as exc:  # noqa: BLE001 - retrieval must not kill the run
                failed = exc
                results = []
            with self._lock:
                if failed is None:
                    self._failures.pop(source, None)
                else:
                    self.errors.append(f"{source}: {failed}")
                    failures = self._failures.get(source, 0) + 1
                    self._failures[source] = failures
                    if failures >= self.config.max_source_failures:
                        self._dead_sources.add(source)
                        self.errors.append(
                            f"{source}: skipped for the rest of the run after {failures} consecutive failures"
                        )
                # Idempotent insert (failure empties are cached too, as serial
                # code did): a tied thread may have stored the same bytes first.
                self._cache.setdefault(key, results)
                stored = self._cache[key]
            # Persist successes only: a transient failure must not poison the
            # cache used by later runs.
            if failed is None and disk_path is not None:
                self._write_disk(disk_path, stored)
            return stored

    def depth(self, round_number: int) -> int:
        """Progressive retrieval: half depth in rounds 1-2, full depth later."""
        if not self.config.progressive:
            return self.config.top_k
        return max(1, self.config.top_k // 2) if round_number <= 2 else self.config.top_k

    def search(self, agent_index: int, claim: str, round_number: int = 1) -> list[sources.SearchResult]:
        """Raw results for one claim from the claim-routed sources.

        Sources are tried in the order returned by ``source_names`` and the
        loop stops once ``top_k`` unique results exist. Because the ordered
        candidates are the same set in both partition conditions, a weak first
        source is always topped up from the remaining routed sources.
        """
        query = (claim or "").strip()
        if not query:
            return []
        depth = self.depth(round_number)
        merged: list[sources.SearchResult] = []
        for source in self.source_names(agent_index, query):
            merged.extend(self._search(source, query, depth))
            if len(sources.dedupe_results(merged)) >= self.config.top_k:
                break
        return merged

    def retrieve(self, agent_index: int, claim: str, round_number: int = 1) -> list[str]:
        """Passages for prompts/verdicts: deduplicated, reranked, equal volume."""
        results = self.search(agent_index, claim, round_number)
        unique = sources.dedupe_results(results)
        passages = [sources.passage_text(r, self.config.max_chars) for r in unique]
        scorer = _lexical_scorer if self.config.rerank == "lexical" else None
        ranked = [p for p, _ in rerank(claim, passages, top_k=self.config.top_k, scorer=scorer)]
        return select_evidence(ranked, self.config.prompt_passages)


class StaticRetriever:
    """Deterministic retriever for tests and the Month-1 pilot.

    ``table`` maps an agent index to a claim->passages mapping (or a single
    fallback list); unknown claims return the fallback, never a network call.
    """

    def __init__(self, table: dict[int, dict[str, list[str]]] | None = None, fallback: list[str] | None = None) -> None:
        self.table = table or {}
        self.fallback = fallback or []

    def retrieve(self, agent_index: int, claim: str, round_number: int = 1) -> list[str]:
        per_agent = self.table.get(agent_index, {})
        return list(per_agent.get(claim, self.fallback))


def evidence_block(passages: list[str], max_items: int = 3, max_chars: int = 1200) -> str:
    """Prompt-ready evidence list; bounded so revision prompts stay in context."""
    if not passages:
        return "(no evidence retrieved)"
    lines = [f"[{i}] {p[:max_chars]}" for i, p in enumerate(passages[:max_items], start=1)]
    return "\n".join(lines)

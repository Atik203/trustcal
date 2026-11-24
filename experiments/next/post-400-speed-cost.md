# Post-400 speed and cost plan

**Status:** READY 21 Nov 2026. `core3` reached 399+399 debates (q27 quarantined)
and the row is complete, so the speed/cost A/Bs are unblocked. The row's
condition stays frozen.

Measured baseline: ~68 s per debate (137–155 s per B8+control pair), on a 96 GB
RTX PRO 6000 at $1.59/h all-in.

> **Outcome (24 Nov 2026).** The A/Bs ran: removing `--enforce-eager` and running
> 8 concurrent rows measured **172.7 debates/h** at **$1.50/GPU-h all-in**,
> versus 52.2/h for the 2-way eager baseline (`../concurrency_test/README.md`).
> Items 1 and 3 below are superseded by that result; the plan text is kept as
> the pre-run record.

## Safe updates (no method change)

1. **CUDA graphs.** Remove `--enforce-eager` from the fourbit serve args in
   `models.yaml`. Same arithmetic, 5–10% generation. Gate: 5-question A/B with
   identical final answers and evidence counts, plus a VRAM check (three servers
   on one card).
2. **Shared retrieval cache across arms.** The control and B8 ask the same claims
   on the same question. A small SQLite cache keyed by `(source, query, top_k)`,
   shared by both processes, removes duplicate API calls and some waiting.
   Expected 5–10% (mostly on the control). Gate: evidence counts unchanged,
   cache hit rate logged.
3. **Four-way concurrency.** Two question pairs (four processes) instead of one.
   Compute-bound, so per-pair latency rises; only adopt if measured $/debate
   falls. Gate: compare GPU-seconds per debate, not wall-clock.
4. **v1.5 reuse.** Full caps 400/400/300 + the `sciclaim_180` loader makes 16
   Core rows reuse-eligible (~29% of Full). Needs the signed amendment and the
   new config hash; no GPU.
5. **Host selection.** Cheapest stable 96 GB spot with a rebuild under ~2 minutes;
   keep one stopped on-demand host as fallback. The sample lock, quarantine and
   torn-line repair make a stop cost one question, not a row. If spot is evicted
   twice in an hour, finish that row on on-demand.

## Protocol changes (signed amendment only)

| Change | Saving | Why it is risky |
| --- | --- | --- |
| One seed for Full | ~50% | Loses the variance estimate; biggest lever |
| Two rounds instead of three | ~33% | Loses round-3 reversion, the transient effect already observed |
| Cap claims per agent | 10–20% | Changes what trust is computed on |

Do not change rounds or claim caps to fit a budget; a reviewer will read it as
changing the phenomenon.

## Order of work after 400

1. CUDA graphs A/B (5 questions).
2. Shared retrieval cache A/B (5 questions).
3. Recompute Full from the measured s/debate before choosing caps.
4. Sign v1.5 + write the `sciclaim_180` loader.
5. Run Full on the cheapest stable host, with the on-demand fallback stopped.

## Why this order

The first two are reversible, method-neutral, and measurable in under an hour.
The reuse amendment changes row identity and must be decided before Full starts,
not after. Host choice is last because it depends on the market at the time.

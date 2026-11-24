# Concurrency and serving tuning — engineering test (24 Nov 2026)

No paper data here. These runs measured wall-clock throughput so the remaining
12,000-debate programme could be budgeted. The 798-debate `core3` row stays the
only measured result.

## Hardware and spend

| Field | Value |
| --- | --- |
| GPU | RTX PRO 6000 Max-Q, 97.9 GB, driver 595.91.07, CUDA 13.2 |
| Host | Vast on-demand, California; 120 GB disk |
| Rate | $1.50/h planning rate ($1.43/h observed all-in) |
| Session cost | ~$2.30 (setup 17 min, two test cycles) |
| Models | fourbit stack: Qwen3.8-27B-AWQ, Gemma-4-26B-A4B-AWQ, Mistral-24B-AWQ |

## Result

| Config | Streams | Debates | Wall | Debates/h |
| --- | ---: | ---: | ---: | ---: |
| Eager (shipped default) | 4 | 40 | 214 s/question | **67.2** |
| **CUDA graphs + no request logs** | **8** | 24 | 516 s | **167.4** |
| Graphs + parallel retrieval tail | 8 | 24 | 542 s | 159.4 (rejected) |

Per-question latencies at 8-way: B3 (no retrieval) 114-132 s; B4/B8/B8NT
(retrieval + trust) 145-228 s, settling near 150-165 s once prefix cache warms.

**Decision:** production config is 8-way with CUDA graphs. The parallel
retrieval change is reverted - it was 5% slower, consistent with per-source
backoff from burstier requests.

## Changes that produced the gain

1. `gen_serve_cmds.py` no longer forces `--enforce-eager` on the fourbit/final
   phases. That flag disabled CUDA graphs, torch.compile and JIT warmup at once.
   `VLLM_EAGER=1` restores it.
2. `--max-num-seqs 32` - required, not optional: Qwen3.8's Mamba hybrid cache
   only has 110 blocks at 0.33 utilization, so vLLM's graph default of 1024
   aborts startup.
3. `--disable-log-requests` on the graph phases.
4. Per-instance utilization rebalanced 0.33 / 0.29 / 0.28 (sum still 0.90) so
   Qwen, which carries the most weights, is not starved of KV.
5. The dev (48GB) stack is retired; `phase.yaml` defaults to `fourbit`.

## Failure log

All of these are catalogued with fixes in
[`docs/agent/09_GPU_RUNBOOK.md`](../../docs/agent/09_GPU_RUNBOOK.md): image-layer
stall, Debian pip `RECORD` error, host delivering 2 MB/s against an 804 Mbps
advertisement, broken SSH key injection, `wait` hanging on the `tee` child,
`serve.sh` staying attached by design, memory-profiling races on restart, and
`max-num-batched-tokens 16384` starving the KV pool.

## Final comparison (all measured on the fourbit stack)

| Config | Streams | Debates | Rate | $/debate @ $1.487/h | 12,000 debates |
| --- | ---: | ---: | ---: | ---: | ---: |
| Eager (shipped default) | 4 | 40 | 67.2/h | $0.0221 | $265.60 |
| **Graphs + 8-way** | **8** | 72 | **172.7/h** | **$0.00861** | **$105.45** |
| Graphs + 8-way + warm disk cache | 8 | 24 | 177.4/h | $0.00838 | $100.70 |
| Graphs + 4-way + S2 pacing gate | 4 | 8 | 104.7/h | $0.0142 | — |
| core3 baseline (2-way, eager) | 2 | 798 | 52.2/h | $0.0285 | $341.80 |

The 8-way rate is the average of three independent runs (516, 498, 487 s for 24
debates), so ±3% is the noise band. Against the 2-way baseline, graphs plus
8-way concurrency is a **3.31x speedup and a 69% cost cut**.

The S2 pacing gate was smoked at 4 streams: 8 debates in 275 s, **zero retrieval
errors, zero 429s**. It keeps Semantic Scholar in the evidence pool at its
1 request/second quota instead of excluding it.

## Retrieval cache A/B (same 8-way mix, 24 debates each)

| Round | Wall | Rate | Cache |
| --- | ---: | ---: | --- |
| Cold | 498 s | 173.5/h | 241 entries |
| Warm | 487 s | 177.4/h | 361 entries, 3 MB |

**2.2% faster - within run-to-run noise.** The cache is not the bottleneck: at
8-way the cost is generation over evidence-heavy prompts, not the ~1 s per
upstream call. It stays in the code (off by default) because it makes replays
and prefetch passes free, but it does not change the budget.


Two retrieval findings came out of this and are paper-relevant:

- Semantic Scholar allows **1 request/second cumulatively**, so eight concurrent
  streams can only 429. A cross-process pacing gate (`TRUSTCAL_SOURCE_MIN_INTERVAL`,
  skip-on-timeout) keeps it in the evidence pool without stalling debates.
- A valid key returns **429**; an invalid one returns **403**. Seeing 429 means
  "throttled", not "reapply".

## Final rate and remaining cost

Three 8-way runs (516, 498, 487 s) average **172.7 debates/h**.

Ablations are scoped to `gpqa_main` and `mmlu_pro` with two seeds: 2 x (400 + 600)
x 2 = 4,000 debates for two ablations, 6,000 for three. The pairing against B8's
rows is exact, a 400-question paired test detects a >=5.7pp component effect at
80% power, and the recorded limitation is that ablations generalise the mechanism
rather than the dataset mix.

**Remaining-programme budget: $220 hard limit, $10 headroom, on-demand only**
(team decision, 24 Nov 2026). Planned spend:

| Plan | Debates | GPU-h | Cost |
| --- | ---: | ---: | ---: |
| Core + Full (36-row alternate), 2 seeds | 13,200 | 76.43 | $114.66 |
| Cap increase (mmlu 600 / hle 400) | 3,200 | 18.53 | $27.79 |
| Three ablations (gpqa 400 + mmlu 600, 2 seeds) | 6,000 | 34.74 | $52.11 |
| FP8 precision | 600 | 3.47 | $5.21 |
| Setup + ingress | - | 1.33 | $2.56 |
| **Total planned (all-in)** | **23,000** | **134.51** | **$202.33** |
| **+ $10 headroom** | - | - | **$212.33** |

The 36-row alternate is chosen over the 32-row default because its gold-answer
oracle also runs on gpqa and mmlu, bounding the trust-aggregation ceiling on
every dataset rather than only on SciClaimBench (4 extra rows, 1,200 debates,
$10.42).

On-demand is deliberate: spot eviction would cost more in rebuilds than the
premium. The $1.50/GPU-h rate already includes disk and ingress.

The earlier serial estimate for the same 12,000 debates was $345; CUDA graphs
plus 8-way concurrency removed about two thirds of it.


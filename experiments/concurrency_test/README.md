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

## Cost projection at the measured rate

| Programme | Debates | Hours | Cost at $1.50/h |
| --- | ---: | ---: | ---: |
| Core + Full, 2 seeds | 12,000 | 72 | $108 |
| + two ablations | 20,000 | 120 | $180 |
| + FP8 precision (96 GB) | 20,600 | 123 | $185 |

The earlier serial estimate for the same 12,000 debates was $345; CUDA graphs
plus 8-way concurrency removed about two thirds of it. The remaining untested
lever is an offline retrieval cache: if it lifts the rate to 220-250/h, the full
27,800-debate menu falls to ~$155-175.

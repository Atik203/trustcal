# 08 - Compute cost (measured)

Status: **measured 24 Nov 2026**, not a planning estimate. Everything below comes
from paid runs on a 96 GB RTX PRO 6000; the numbers are reproducible from
[`experiments/concurrency_test/`](../../experiments/concurrency_test/README.md).

## 1. Measured throughput

| Config | Debates/h | $/debate @ $1.50/h |
| --- | ---: | ---: |
| 2-way, `--enforce-eager` (old default) | 52.2 | $0.0287 |
| 4-way, eager | 67.2 | $0.0223 |
| **8-way, CUDA graphs** | **172.7** | **$0.0087** |
| 8-way + warm retrieval cache | 177.4 | $0.0085 |

Three independent 8-way runs (516, 498, 487 s for 24 debates) put the noise band
at ±3%. The gain is mostly the flag change: `--enforce-eager` disabled CUDA
graphs, torch.compile and JIT warmup at once. Concurrency adds the rest.

Serving configuration that produced it (generated from `configs/models.yaml`):

- CUDA graphs (no `--enforce-eager`; `VLLM_EAGER=1` restores it if capture OOMs)
- `--max-num-seqs 32` - required: Qwen3.8's Mamba cache has ~110 blocks
- `--disable-log-requests`
- `--gpu-memory-utilization 0.33 / 0.29 / 0.28` (sum 0.90, KV-balanced)
- 8 concurrent rows = 4 conditions x 2 seeds, one `run_experiment.py` each

## 2. Remaining programme budget

Planning rate **$1.50/GPU-h all-in, on-demand** (disk and ingress included; spot
is rejected because eviction costs more in rebuilds than the premium).

| Component | Debates | GPU-h | Cost |
| --- | ---: | ---: | ---: |
| Core + Full (36-row alternate), 2 seeds | 14,000 | 81.06 | $121.59 |
| Cap increase (mmlu 600 / hle 400) | 3,200 | 18.53 | $27.79 |
| Three ablations (gpqa 400 + mmlu 600, 2 seeds) | 6,000 | 34.74 | $52.11 |
| FP8 precision replication | 600 | 3.47 | $5.21 |
| Setup + ingress (4 sessions) | - | 1.33 | $2.56 |
| **Planned total (all-in)** | **23,798** | **139.13** | **$209.25** |

**Remaining-spend cap: $220 with $10 headroom**, so the committed figure is
**~$219.26.33** and the absolute margin is ~$7.67. The 36-row alternate is chosen
over the 32-row default: its gold-answer oracle runs on gpqa and mmlu as well,
which bounds the trust-aggregation ceiling on every dataset rather than only on
SciClaimBench (4 extra rows = 1,200 debates = $10.42).

This cap is separate from the preregistered programme hard stop of **$300** (project total, ~$53 already spent) in
`PRE_REGISTRATION.md`; that document's GPU-hour arithmetic is retained as the
frozen gate cap, not as a forecast.

Completed work is excluded from the table: the 798-debate `gpqa_main` seed-1 row
(~$19) is already spent.

## 3. Host selection and acceptance

An idle or stalling host bills at the full rate, so prove the offer before any
paid work. Three checks, each with an abort:

1. **SSH within 60 s of `running`.** A publickey denial that survives one reboot
   means destroy it, not debug it on the clock.
2. **45 s real download.** Below 10 MB/s, the advertised `inet_down` is not what
   the host delivers. The measured spread on the same 96 GB class is two orders
   of magnitude (2 MB/s vs 446 MB/s), so only the measurement counts. Ingress is
   priced separately: 53 GB costs $0.14 at $0.0026/GB but $1.38 at $0.026/GB, so
   the cheapest hourly host is often the most expensive run.
3. **Image and install.** `vastai/base-image` plus the pinned `install_vllm.sh`
   avoids framework-image layer stalls; pass `VENV=1` on Debian-managed images
   or pip fails with `Cannot uninstall pip ... RECORD file not found`.

Marginal disk is priced apart from the headline `dph_total`, often near
$1/GB/month, so 120 GB adds ~$0.17/h. Size for weights + venv + results. Destroy
rather than stop: a stopped instance still bills disk.

Failure catalogue with fixes: [`09_GPU_RUNBOOK.md`](09_GPU_RUNBOOK.md).

## 4. What would blow the budget

1. **Running the matrix serially.** `run_matrix.py` executes rows one at a time;
   that is ~2x the parallel cost.
2. **Any `--enforce-eager` run.** 3.3x slower per debate.
3. **Re-downloading the 53 GB stack per session.** One long session, or a volume.
4. **Idle hosts while debugging prompts.** Prepare prompts/configs first; use mocks.
5. **Forgetting to copy `results/` before destroy.** Re-running is the most
   expensive mistake in the project.
6. **Running the old 15x5x3x1,000 blueprint grid.** 225,000 debates; impossible.
7. **Spot hosts for multi-hour rows.** Eviction forces a rebuild that costs more
   than the premium.

## 5. Retired figures

These appear in older documents and are historical only: `$0.136/GPU-h` (80 GB
A100 spot), `$0.336/GPU-h` (FP8 96 GB), `1,067 GPU-h` planned / `1,280 GPU-h` cap
as *forecasts*, Core `$175-210`, Full `$210/$235`, total `$500-600`, and the RTX
A6000 dev stack. The 1,280 GPU-h figure survives only as the preregistered gate
ceiling. Do not budget from any of them.

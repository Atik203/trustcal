# 09 - GPU session runbook: failure modes and fixes

Every entry below cost real money or real time at least once. Read the symptom
column before debugging; the fix is usually one flag or one line.

## Known-good session (copy this, do not improvise)

Verified 24 Nov 2026 on a 96 GB RTX PRO 6000: **172.7 debates/h** at 8 concurrent
rows, zero server failures, zero retrieval errors. That rate prices the remaining
23,000-debate programme at **134.51 GPU-h = $202.33** ($220 cap, $10 headroom).

```bash
# host: 96GB class, 120 GB disk, vastai/base-image, ~$1.49/h all-in
git clone --depth 1 https://github.com/Atik203/trustcal.git && cd trustcal/trustcal
export PHASE=fourbit VENV=1
export TRUSTCAL_RETRIEVAL_CACHE=/root/retrcache                    # optional
export TRUSTCAL_SOURCE_MIN_INTERVAL="semantic_scholar=1.0"        # keeps S2 usable
bash setup.sh > setup.log 2>&1 &                                   # ends in `wait`: run it backgrounded

# readiness: exactly three listeners, never "the script finished"
until [ "$(ss -tln | grep -cE ':(8000|8001|8002) ')" -ge 3 ]; do sleep 10; done

# 8 rows = 4 conditions x 2 seeds; collect PIDs, never bare `wait`
pids=(); for s in 1 2; do for c in B3 B4 B8 B8NT; do
  arm=$c; extra=""; [ "$c" = B8NT ] && { arm=B8; extra=--no-trust; }
  .venv/bin/python scripts/run_experiment.py --arm "$arm" $extra --dataset gpqa_main \
    --limit 400 --seed "$s" --phase fourbit --out "results/core/$c$s" \
    --questions-file /root/q400.json > "/root/logs/$c$s.log" 2>&1 &
  pids+=($!)
done; done; wait "${pids[@]}"
```

Serving flags are generated from `configs/models.yaml` by `gen_serve_cmds.py`:
CUDA graphs (no `--enforce-eager`), `--disable-log-requests`, `--max-num-seqs 32`,
`--gpu-memory-utilization 0.33 / 0.29 / 0.28`. `VLLM_EAGER=1` forces eager back.

## Before you rent

Three checks with an abort, in order (details in the root `AGENTS.md`):

1. **SSH within 60 s of `running`.** One reboot allowed; after that, destroy.
2. **45 s real download.** Under 10 MB/s means the host's advertised `inet_down`
   is fiction. Destroy and take another offer.
3. **Right image.** `vastai/base-image` + our pinned `install_vllm.sh`; pass
   `VENV=1` on Debian-managed images.

## Host and network

| Symptom | Cause | Fix |
| --- | --- | --- |
| Image pull stuck on one layer, `Retrying in 1 second` for minutes | Host's registry path is bad; the stall bills at GPU rate | Destroy; use `vastai/base-image` and install vLLM yourself |
| `hf download` stuck at 0 MB/min, cache size not moving | Host throttles or breaks TLS to the HF CDN | Kill it; measure with a 45 s gate before renting; enable `HF_HUB_ENABLE_HF_TRANSFER=1` with `hf_transfer` installed |
| `gnutls_handshake() failed` on `git clone` | Transient TLS/proxy fault on the host | Retry 3-5 times with a short sleep; it usually succeeds on the second attempt |
| `Permission denied (publickey)` right after `running` | Key injection hiccup | Reboot once; if it persists, destroy - do not debug on the clock |
| Headline `dph_total` lower than the bill | Marginal disk is priced separately, often near $1/GB/month | Size disk to weights + venv + results (120 GB for the 4-bit stack), not the host maximum |

## Installation

| Symptom | Cause | Fix |
| --- | --- | --- |
| `Cannot uninstall pip 24.0, RECORD file not found` | Debian-managed pip on base images | Re-run setup with `VENV=1` |
| `validate_stack.py` fails before download | Checkpoint/flag mismatch | Expected - fix the config; nothing was downloaded |

## vLLM startup

| Symptom | Cause | Fix |
| --- | --- | --- |
| `max_num_seqs (1024) exceeds available Mamba cache blocks (110)` | Qwen3.8 keeps a Mamba hybrid cache, one block per decoding sequence; graph mode defaults `max_num_seqs` to 1024 | Add `--max-num-seqs 32` (24 requests is a fully concurrent 8-row run) |
| `No available memory for the cache blocks` | `--max-num-batched-tokens 16384` inflates the activation buffer and starves KV | Keep the default 8192; raise memory utilization or lower `max_model_len` instead |
| `Error in memory profiling. Initial free memory ... current free memory ...` | Another server released memory while this one profiled (restart race) | `pkill -f "vllm serve"`, wait 30-35 s, then start; never start two sets |
| Startup is slow but not stuck | Without `--enforce-eager`, vLLM runs torch.compile and captures CUDA graphs | Budget 5-10 min for three servers; it is the price of the 20-35% decode gain |
| Only some ports listen after `Startup pass complete`, experiments then fail on one agent | `serve.sh` starts three servers sequentially and one died; the script does not abort the others | Read `results/logs/vllm-<port>.log` for the dead one, fix, and restart **that** command (`gen_serve_cmds.py --phase fourbit \| head -1`) instead of re-serving all three. Readiness means 3/3 ports, never "the script ended" |

## Retrieval quotas and the disk cache

| Symptom | Cause | Fix |
| --- | --- | --- |
| Semantic Scholar returns 429 in every run, then the source goes dead | S2 allows **1 request/second cumulatively across all endpoints**; a 12-24 request burst always exceeds it | Pace it: `TRUSTCAL_SOURCE_MIN_INTERVAL=semantic_scholar=1.0` (cross-process gate, skip-on-timeout). Do not exclude it unless you also document the coverage change for every arm |
| Is the S2 key invalid? | Compare responses: **429 = key accepted but throttled**, **403 = invalid key**, 429 with no key = anonymous limit | Do not reapply for a key that returns 429; request a limit increase instead |
| Retrieval dominates a question's wall time | ~1 s per upstream call x ~50 calls per question | Prefetch once into `TRUSTCAL_RETRIEVAL_CACHE`; a warm run reads disk in ~20 ms per call |
| The cache does not speed up a fresh run | Failures are never cached, and `_dead_sources` resets every run, so each run re-pays the 429 discovery | Fix or exclude the failing source first; the cache only removes *successful* waits |
| Cache directory gets slow with many entries | A full programme writes ~200k small files | Already sharded into 256 subdirectories by hash prefix; ~1-1.5 GB for 2,000 questions |

`verify_env` prints `OK   server :8000` on success and `FAIL server :8000` on
failure. Grepping for `"server OK"` never matches, which silently hangs a health
gate. Gate on the ports instead:
`ss -tln | grep -cE ':(8000|8001|8002) '` must return 3.

**Measured with the gate on** (4 streams, `TRUSTCAL_SOURCE_MIN_INTERVAL=semantic_scholar=1.0`):
8 debates in 275 s, zero retrieval errors, zero 429s. The gate keeps S2 in the
evidence pool at its quota instead of excluding it. Scaling reference on the same
stack: 4 streams ≈ 105 debates/h, 8 streams ≈ 173 debates/h.

`--enforce-eager` disables CUDA graphs **and** torch.compile **and** JIT kernel
warmup. It is a 48 GB dev-stack guard only; the 80/96 GB phases should run with
graphs. `VLLM_EAGER=1` restores it for a phase that OOMs during capture.

## Harness and scripting

| Symptom | Cause | Fix |
| --- | --- | --- |
| A chained script finishes its work but never writes its "done" marker | `wait` with no arguments also waits on the `tee` child created by `exec > >(tee -a log)`; `tee` never exits | Collect PIDs (`pids+=($!)`) and `wait "${pids[@]}"`; redirect with `>> log 2>&1`, not `tee` |
| `pkill -f myscript.sh` kills your own SSH session | The pattern matches the shell running the command | Kill by PID from `ps`, or anchor the pattern so it cannot match your own command line |
| PowerShell eats `$VAR` inside an `ssh "..."` string | Local expansion before the remote shell sees it | Put remote commands in a script, `scp` it, run the file |
| `vastai execute` rejects a compound command | CLI quoting/argument splitting | Same fix: ship a script and execute the path |
| A controller script blocks forever after the servers print `Startup pass complete` | `serve.sh` ends with a bare `wait` so it stays attached to the three servers | Run `serve.sh` in the background (or `tmux`) and poll `verify_env.py --check-servers`; never call it synchronously from another script |

## Cost traps

| Trap | Cost | Guard |
| --- | --- | --- |
| Idle host while you think | Full GPU rate | Destroy on finish; keep work queued and unattended |
| Re-downloading 53 GB per session | Ingress + 15 min setup | One long session, or a volume/host cache |
| Retrying a broken host "to be sure" | $0.3-1.5 per attempt | Apply the three checks; abandon fast |
| Running the matrix serially | ~2x the parallel cost | One `run_experiment.py` per condition, distinct `--out` |

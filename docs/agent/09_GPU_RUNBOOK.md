# 09 - GPU session runbook: failure modes and fixes

Every entry below cost real money or real time at least once. Read the symptom
column before debugging; the fix is usually one flag or one line.

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

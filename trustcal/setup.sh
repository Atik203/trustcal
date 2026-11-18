#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# ONE-COMMAND POD SETUP — Dev (48GB), Four-bit (80GB) or Final (96GB)
#
#   git clone https://github.com/Atik203/trustcal.git /workspace/fydp
#   cd /workspace/fydp/trustcal
#   HF_TOKEN=hf_... bash setup.sh                    # Dev stack (~31GB)
#   HF_TOKEN=hf_... PHASE=fourbit bash setup.sh      # Four-bit stack (~53GB)
#   HF_TOKEN=hf_... PHASE=final bash setup.sh        # Final stack (~71GB)
#   HF_TOKEN=hf_... VENV=1 bash setup.sh             # recommended when the image
#                                                    # blocks system pip (PEP 668)
#
# Does, in order: checks Python + GPU + disk → installs pinned deps → installs
# pinned vLLM 0.34.0 → installs trustcal editable → validates every checkpoint's
# architecture/quant/flags/chat template using config files only → downloads the
# checkpoints for PHASE (pinned revisions from configs/models.yaml) → starts vLLM
# on :8000-8002 → verifies imports, versions and server health.
#
# The validation step is the important one: it fails BEFORE the 53GB download if
# a checkpoint or serve flag is incompatible with the installed vLLM.
#
# Options:  PHASE=dev|fourbit|final  model stack (default dev)
#           VENV=1          create .venv and install everything into it (recommended
#                           on Thunder Compute; on RunPod the system env is fine)
#           SKIP_SERVE=1   install + download only (no servers)
#           SKIP_MODELS=1  install only (skip model downloads)
#           SKIP_VALIDATE=1 skip the config-only stack validation
#           CUDA_TAG=cu130|cu129  override the auto-detected torch wheel index
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail
cd "$(dirname "$0")"

PHASE="${PHASE:-dev}"
case "$PHASE" in
  dev|fourbit|final) ;;
  *) echo "ERROR: PHASE must be 'dev', 'fourbit' or 'final' (got '$PHASE')" >&2; exit 1 ;;
esac
export PHASE
export TRUSTCAL_PHASE="$PHASE"

echo "== trustcal setup (phase=$PHASE) =="

# ── 0) Python ≥ 3.10 ────────────────────────────────────────────────────────
PY_CMD=python3
command -v python3 >/dev/null 2>&1 || PY_CMD=python
command -v "$PY_CMD" >/dev/null 2>&1 || { echo "ERROR: python3 not found"; exit 1; }
VER=$("$PY_CMD" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Python: $VER ($("$PY_CMD" --version 2>&1))"
case "$VER" in
  3.10|3.11|3.12|3.13) ;;
  *) echo "WARN: vLLM nightly is tested on 3.10-3.13; found $VER — continuing anyway" ;;
esac

# ── 0b) Optional venv (recommended on Thunder Compute) ──────────────────────
# Thunder ships CUDA 13.0 / PyTorch 2.9 and asks you not to touch them; a venv
# keeps the nightly vLLM + torch stack isolated from the system environment.
if [ "${VENV:-0}" = "1" ]; then
  if command -v uv >/dev/null 2>&1; then
    rm -rf .venv   # recreate cleanly: uv venvs ship without pip unless --seed
    uv venv --seed .venv
  else
    "$PY_CMD" -m venv .venv
  fi
  # shellcheck disable=SC1091
  . .venv/bin/activate
  PY_CMD=python
  echo "VENV=1 — using $(pwd)/.venv ($("$PY_CMD" --version 2>&1))"
fi

# ── 1) GPU present? (warning only — setup can still run on a CPU box) ───────
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader | sed 's/^/GPU: /'
else
  echo "WARN: nvidia-smi not found — vLLM serving will fail without a GPU."
fi

# ── 2) Model cache on the persistent disk ───────────────────────────────────
# RunPod: /workspace network volume. Thunder: home dir is the persistent disk
# (included in snapshots), so fall back to $HOME/.cache/huggingface.
if [ -z "${HF_HOME:-}" ]; then
  if [ -d /workspace ] && [ -w /workspace ]; then
    HF_HOME=/workspace/.cache/huggingface
  else
    HF_HOME="$HOME/.cache/huggingface"
  fi
fi
export HF_HOME
mkdir -p "$HF_HOME" "$(pwd)/results"
echo "HF_HOME=$HF_HOME"
if [ -n "${HF_TOKEN:-}" ]; then
  echo "HF_TOKEN: set"
else
  echo "WARN: HF_TOKEN not set — gated downloads (GPQA dataset) will fail."
fi

# Disk is the second paid-session killer after a bad checkpoint: a 100GB Vast
# disk has ~90GB free, which is enough for fourbit but not for final + results.
"$PY_CMD" - "$PHASE" "$HF_HOME" <<'PY'
import shutil, sys
need = {"dev": 35.0, "fourbit": 65.0, "final": 85.0}[sys.argv[1]]
free = shutil.disk_usage(sys.argv[2]).free / 1e9
print(f"disk: {free:.1f}GB free (need >= {need:.0f}GB for {sys.argv[1]})")
raise SystemExit(0 if free >= need else 1)
PY

# ── 3) Install pinned deps + pinned vLLM + the package itself ───────────────
"$PY_CMD" -m pip install --upgrade pip >/dev/null
"$PY_CMD" -m pip install -r requirements.txt
bash scripts/install_vllm.sh
"$PY_CMD" -m pip install -e . --no-deps
"$PY_CMD" -m pip check
echo "Deps installed."

# Triton JIT needs Python.h. Resolve it now, not after a 53GB download and a
# cryptic "Engine core initialization failed" at server startup.
# shellcheck source=scripts/python_headers.sh
. scripts/python_headers.sh
trustcal_ensure_python_headers "$PY_CMD" || exit 1

# ── 3b) Validate the exact stack BEFORE downloading 53GB of weights ─────────
# Downloads config/tokenizer/chat-template files only. If an architecture,
# quantization method, serve flag or reasoning parser is incompatible with this
# vLLM release, the script stops here instead of after a long paid download.
if [ "${SKIP_VALIDATE:-0}" != "1" ]; then
  echo "Validating checkpoints and serve flags (config files only) ..."
  "$PY_CMD" scripts/validate_stack.py --config configs/models.yaml --phase "$PHASE" --download-configs
fi

# ── 4) Download the checkpoints for PHASE (pinned revisions) ─────────────────
hf_download() {
  local model="$1" revision="${2:-}"
  local args=(download "$model")
  [ -n "$revision" ] && args+=(--revision "$revision")
  if command -v hf >/dev/null 2>&1; then
    hf "${args[@]}"
  elif command -v huggingface-cli >/dev/null 2>&1; then
    huggingface-cli "${args[@]}"
  else
    "$PY_CMD" -m huggingface_hub.commands.huggingface_cli "${args[@]}"
  fi
}

if [ "${SKIP_MODELS:-0}" != "1" ]; then
  MODEL_LIST=$("$PY_CMD" - <<'PY'
from trustcal.config import agents_for_phase, load_models
for agent in agents_for_phase(load_models("configs/models.yaml")):
    print(f"{agent.model}\t{agent.revision or ''}")
PY
)
  while IFS=$'\t' read -r MODEL REV; do
    [ -n "$MODEL" ] || continue
    echo "Downloading $MODEL ${REV:+@$REV} ..."
    hf_download "$MODEL" "$REV"
  done <<< "$MODEL_LIST"
  echo "Models downloaded ($PHASE)."
fi

# ── 5) Start vLLM (3 instances, ports 8000-8002) + verify ───────────────────
if [ "${SKIP_SERVE:-0}" != "1" ]; then
  echo "Starting vLLM on :8000-8002 (logs: results/logs/) ..."
  nohup bash scripts/serve.sh > results/vllm.log 2>&1 &
  echo $! > results/vllm.pid

  # wait for the three servers (up to 30 minutes — serve.sh loads quantized
  # models sequentially, and a cold 27B checkpoint can take several minutes)
  for i in $(seq 1 180); do
    if "$PY_CMD" scripts/verify_env.py --check-servers >/dev/null 2>&1; then break; fi
    sleep 10
  done

  "$PY_CMD" scripts/verify_env.py --check-servers
  echo "== setup.sh complete — vLLM on :8000-8002, ready for Gate 0 =="
  echo "Next: python scripts/repro_mad.py --limit 10"
else
  "$PY_CMD" scripts/verify_env.py
  echo "== setup.sh complete (servers skipped) — run 'bash scripts/serve.sh' when ready =="
fi

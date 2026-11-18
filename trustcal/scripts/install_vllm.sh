#!/usr/bin/env bash
# install_vllm.sh — install the pinned vLLM release used by the experiment matrix.
#
# vLLM 0.34.0 already contains the model classes this project needs:
#   * Qwen3.5 / Qwen3.8      (Qwen3_5ForCausalLM, Qwen3_5ForConditionalGeneration)
#   * Gemma 4 and Gemma 4 Unified (Gemma4ForConditionalGeneration,
#     Gemma4UnifiedForConditionalGeneration)
#   * Mistral 3 / Pixtral    (Mistral3ForConditionalGeneration)
# The old nightly requirement applied to vLLM 0.29.x. Pinning a release makes a
# paid session reproducible instead of depending on the day's nightly wheel.
#
# CUDA_TAG auto-detects from the installed driver (major >= 580 -> cu130, else
# cu129). Override explicitly with CUDA_TAG=cu129.
#
# Options:
#   VLLM_VERSION=0.34.0   pinned release (default)
#   VLLM_NIGHTLY=1        install the newest nightly instead (fallback only)
set -euo pipefail

VLLM_VERSION="${VLLM_VERSION:-0.34.0}"

if [ -z "${CUDA_TAG:-}" ]; then
  DRIVER_MAJOR=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -1 | cut -d. -f1)
  if [ -n "${DRIVER_MAJOR:-}" ] && [ "${DRIVER_MAJOR:-0}" -ge 580 ] 2>/dev/null; then
    CUDA_TAG=cu130
  else
    CUDA_TAG=cu129
  fi
  echo "Detected driver major: ${DRIVER_MAJOR:-unknown} -> ${CUDA_TAG}"
fi

if [ "${VLLM_NIGHTLY:-0}" = "1" ]; then
  echo "Installing nightly vLLM (${CUDA_TAG}) ..."
  if command -v uv >/dev/null 2>&1; then
    UV_FLAGS=()
    [ -n "${VIRTUAL_ENV:-}" ] || UV_FLAGS+=(--system)
    uv pip install "${UV_FLAGS[@]}" -U vllm --pre \
      --extra-index-url "https://wheels.vllm.ai/nightly/${CUDA_TAG}" \
      --extra-index-url "https://download.pytorch.org/whl/${CUDA_TAG}" \
      --index-strategy unsafe-best-match
  else
    python -m pip install -U vllm --pre \
      --extra-index-url "https://wheels.vllm.ai/nightly/${CUDA_TAG}" \
      --extra-index-url "https://download.pytorch.org/whl/${CUDA_TAG}"
  fi
else
  echo "Installing vLLM ${VLLM_VERSION} (${CUDA_TAG}) ..."
  if command -v uv >/dev/null 2>&1; then
    UV_FLAGS=()
    [ -n "${VIRTUAL_ENV:-}" ] || UV_FLAGS+=(--system)
    uv pip install "${UV_FLAGS[@]}" "vllm==${VLLM_VERSION}" \
      --extra-index-url "https://download.pytorch.org/whl/${CUDA_TAG}" \
      --index-strategy unsafe-best-match
  else
    python -m pip install "vllm==${VLLM_VERSION}" \
      --extra-index-url "https://download.pytorch.org/whl/${CUDA_TAG}"
  fi
fi

python - <<'PY'
import vllm, torch, transformers, huggingface_hub
print(f"vLLM {vllm.__version__}")
print(f"torch {torch.__version__} (CUDA {torch.version.cuda})")
print(f"transformers {transformers.__version__}")
print(f"huggingface_hub {huggingface_hub.__version__}")
PY
python -m pip check

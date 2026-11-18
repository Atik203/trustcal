#!/usr/bin/env bash
# Ensure Triton's CUDA driver helper can find Python.h without sudo.
#
# vLLM 0.34.0's Triton runtime compiles a small `driver.c` on first use. On a
# minimal image without python3-dev that fails with a generic
# "Engine core initialization failed" and no useful compiler line. The fix is
# to point CPATH at matching headers; `uv` can provide them user-locally.
#
# Sourced by setup.sh and serve.sh:
#     . scripts/python_headers.sh
#     trustcal_ensure_python_headers "$PY_CMD" || exit 1

trustcal_ensure_python_headers() {
  local py="${1:-python3}"
  local include
  include=$("$py" -c 'import sysconfig; print(sysconfig.get_paths()["include"])' 2>/dev/null || true)

  if [ -n "$include" ] && [ -f "$include/Python.h" ]; then
    export CPATH="$include${CPATH:+:$CPATH}"
    return 0
  fi

  local version
  version=$("$py" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || true)

  local uv_bin
  uv_bin=$(command -v uv 2>/dev/null || true)
  [ -n "$uv_bin" ] || uv_bin="$HOME/.local/bin/uv"

  if [ -x "$uv_bin" ] && [ -n "$version" ]; then
    "$uv_bin" python install "$version" >/dev/null 2>&1 || true
    local uv_py prefix
    # --managed-python avoids resolving the project's .venv (whose include/
    # directory is empty). Older uv versions fall back to a neutral cwd.
    uv_py=$(unset VIRTUAL_ENV; "$uv_bin" python find --managed-python "$version" 2>/dev/null || (cd /tmp && "$uv_bin" python find "$version" 2>/dev/null) || true)
    if [ -n "$uv_py" ]; then
      prefix=$(dirname "$(dirname "$uv_py")")
      if [ -f "$prefix/include/python$version/Python.h" ]; then
        export CPATH="$prefix/include/python$version${CPATH:+:$CPATH}"
        echo "python headers: using uv $version at $prefix/include/python$version" >&2
        return 0
      fi
    fi
  fi

  echo "ERROR: Python.h is missing for $py (include=${include:-unknown})." >&2
  echo "Triton JIT will fail at vLLM startup. Install python${version:-3}-dev or uv, then rerun." >&2
  return 1
}

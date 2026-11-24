"""Print one `vllm serve` command per agent, derived from configs/models.yaml.

Used by scripts/serve.sh (and its DRY_RUN=1 mode) so serve flags can never drift
from the agent config. Pure text generation — no GPU, no network, no vLLM import.
"""

from __future__ import annotations

import argparse
import os
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trustcal.config import PHASES, agents_for_phase, load_models, max_model_len_for_phase


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate vLLM serve commands from configs/models.yaml")
    parser.add_argument("--config", default="configs/models.yaml")
    parser.add_argument("--phase", choices=PHASES, default="dev")
    args = parser.parse_args()

    cfg = load_models(args.config)
    agents = agents_for_phase(cfg, args.phase)
    phase_max_len = max_model_len_for_phase(cfg, args.phase)
    # --enforce-eager is a memory guard, not a default: it disables CUDA graphs,
    # torch.compile and JIT warmup (~20-35% of decode throughput). The four-bit
    # and FP8 stacks keep the graphs; VLLM_EAGER=1 forces eager back on if a
    # phase ever OOMs during capture.
    eager = os.getenv("VLLM_EAGER", "").strip() == "1"

    for agent in agents:
        cmd = [
            "vllm", "serve", agent.model,
            "--port", str(agent.port),
            "--max-model-len", str(agent.max_model_len or phase_max_len),
            "--gpu-memory-utilization",
            str(agent.gpu_memory_utilization or cfg.gpu_memory_utilization or 0.30),
        ]
        cmd.append("--enforce-eager" if eager else "--disable-log-requests")
        if agent.quant and agent.quant.lower() not in {"auto", "none", ""}:
            cmd += ["--quantization", agent.quant]
        if agent.revision:
            cmd += ["--revision", agent.revision]
        cmd += agent.extra_args
        print(shlex.join(cmd))


if __name__ == "__main__":
    main()

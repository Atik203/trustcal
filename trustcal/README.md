# TrustCal pipeline

The Python implementation of evidence-grounded trust in multi-agent scientific debate. The pipeline runs three heterogeneous agents for three rounds behind an OpenAI-compatible interface, decomposes each response into claims, retrieves evidence, assigns verdicts, updates a bounded trust vector, and returns a trust-weighted answer.

This directory is the experimental engine. The thesis report and journal live in the repository root. No efficacy results are claimed: the first `core3` Core row is complete (B8 vs B8-no-trust, 399+399 debates), the remaining Core rows and the Full matrix have not been run.

## Layout

| Path | Owns |
| --- | --- |
| `configs/models.yaml` | agent checkpoints, revisions, ports, quantization, VRAM split, phases |
| `configs/experiments_fourbit.yaml` | 24-row Core matrix on the 4-bit stack |
| `configs/experiments_full.yaml` | 32-row Full default / 36-row gold-answer alternate |
| `configs/experiments_precision.yaml` | 3-row GPQA FP8 precision replication |
| `src/trustcal/` | inference, agents, orchestrator, trust, retrieval, eval, runner |
| `scripts/` | serving, gate, matrix, smoke, calibration, and annotation entry points |

## GPU-free checks

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install pytest numpy pyyaml openai python-dotenv requests httpx
pytest -q
python scripts/p0_gate.py
```

The suite covers the trust math, claim parser, inference retry behaviour, debate loop, injection, matrix configs, stack budgets, record schema, and a mock end-to-end path.

Useful dry-runs:

```bash
python scripts/run_matrix.py --config configs/experiments_fourbit.yaml --dry-run
python scripts/run_matrix.py --config configs/experiments_full.yaml --dry-run
python scripts/run_matrix.py --config configs/experiments_precision.yaml --dry-run
python scripts/check_stack.py --phase fourbit
python scripts/check_stack.py --phase final
```

## Serving phases

| Phase | Card | Models | Weights |
| --- | --- | --- | --- |
| `dev` | retired | — | `--phase dev` raises; the dev block is removed |
| `fourbit` | 96 GB class (a single 80 GB A100 also fits the 53.26 GB stack) | Qwen3.8-27B-AWQ-INT4, Gemma 4 26B-A4B AWQ, Mistral 24B AWQ | **53.26 GB** |
| `final` | RTX PRO 6000 96 GB | Qwen3.8-27B-FP8, Gemma 4 26B-A4B FP8, Mistral 24B AWQ | **73.68 GB** |

`fourbit` is the main causal matrix stack; at 8 concurrent rows with CUDA graphs it measured **172.7 debates/h** at **$1.50/GPU-h all-in**. `final` is limited to the N1 smoke and the small GPQA precision replication.

## GPU serving

Serving is Linux + NVIDIA only:

```bash
HF_TOKEN=hf_... [VENV=1] bash setup.sh
python scripts/verify_env.py --check-servers
python scripts/smoke_test.py --phase fourbit --limit 5
```

The clients talk to `127.0.0.1:8000-8002`, never `localhost`. A dead server is logged in `results/logs/vllm-<port>.log`. If a server OOMs, lower that agent's `gpu_memory_utilization` in `models.yaml` and restart.

Before a paid session, run the mock path locally:

```bash
python scripts/mock_vllm.py --ports 8000,8001,8002 --mode divergent
```

## Order of work

1. Free 18 GB test gate: one 8–9B AWQ model (or one Q4_K_M model with llama.cpp) plus two mocks; no cloud spend.
2. 4-bit 80 GB 5-question smoke
3. pilot
4. 24-row Core matrix
5. 96 GB FP8 5-question smoke, then the 3-row precision replication
6. 32-row Full matrix

Never run a matrix before the pilot. The 96 GB smoke is not a gate for the 4-bit Full matrix; it is required before any FP8 precision claim. The execution plan and costs are in [`../roadmap.md`](../roadmap.md); serving and instance rules are in [`AGENTS.md`](AGENTS.md); per-component status is in [`IMPLEMENTATION_STATUS.md`](IMPLEMENTATION_STATUS.md).

## Security

Never commit `.env`, `HF_TOKEN`, `OPENAI_API_KEY`, retrieval keys, model caches, or `results/`. vLLM has no authentication by default. Keep it on loopback or behind an SSH tunnel; do not expose ports 8000-8002 publicly.

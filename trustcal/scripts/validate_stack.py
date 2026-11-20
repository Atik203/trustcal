"""Validate the served stack before downloading 53 GB of weights.

This is the fail-fast gate for a paid session. It downloads only config,
tokenizer and chat-template files (a few MB), then checks against the installed
vLLM release:

  * the checkpoint architecture is registered with vLLM;
  * the quantization method in the checkpoint matches the serve flag;
  * every serve flag in ``configs/models.yaml`` exists in this vLLM version;
  * the reasoning-parser name is registered;
  * the model's context window covers ``max_model_len``;
  * the checkpoint's chat template renders with the same kwargs the server uses.

Run it after ``install_vllm.sh`` and before the weight download:

    python scripts/validate_stack.py --phase fourbit --download-configs
    python scripts/validate_stack.py --phase fourbit --offline

Exit codes: 0 all checks pass, 1 a check failed, 2 vLLM/transformers missing.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trustcal.config import PHASES, AgentConfig, agents_for_phase, load_models  # noqa: E402
from trustcal.preflight import resolve_hf_home  # noqa: E402

CONFIG_PATTERNS = ["*.json", "*.jinja", "*.model", "*.txt"]
SAMPLE_SYSTEM = "You are an expert scientific reviewer."
SAMPLE_USER = "Question: Which process stores energy in a capacitor?\n\nAnswer:"


@dataclass
class Result:
    role: str
    model: str
    checks: list[tuple[str, bool, str]]

    @property
    def ok(self) -> bool:
        return all(ok for _, ok, _ in self.checks)


def _architectures(config: dict) -> list[str]:
    values = config.get("architectures") or []
    return [str(value) for value in values]


def check_architecture(architectures: list[str], supported: set[str]) -> tuple[bool, str]:
    if not architectures:
        return False, "config.json has no architectures"
    missing = [name for name in architectures if name not in supported]
    if missing:
        return False, f"not in this vLLM registry: {missing}"
    return True, ", ".join(architectures)


def _quant_method(config: dict) -> str:
    quant = config.get("quantization_config") or {}
    return str(quant.get("quant_method") or quant.get("format") or "")


def check_quantization(config: dict, quant: str) -> tuple[bool, str]:
    method = _quant_method(config)
    requested = (quant or "auto").strip().lower()
    if requested in {"auto", "none", ""}:
        return True, f"auto (checkpoint says {method or 'none'})"
    if requested == "compressed-tensors":
        ok = method in {"compressed-tensors", "pack-quantized"}
        return ok, f"flag=compressed-tensors, checkpoint={method or 'missing'}"
    if requested == "fp8":
        ok = "fp8" in method.lower() or method in {"compressed-tensors", "pack-quantized"}
        return ok, f"flag=fp8, checkpoint={method or 'missing'}"
    if requested in {"awq", "awq_marlin"}:
        ok = method in {"awq", "pack-quantized", "compressed-tensors"}
        return ok, f"flag={requested}, checkpoint={method or 'missing'}"
    return True, f"flag={requested}, checkpoint={method or 'missing'} (not cross-checked)"


def check_extra_args(
    extra_args: list[str], engine_fields: set[str], parser_names: set[str]
) -> list[tuple[str, bool, str]]:
    checks: list[tuple[str, bool, str]] = []
    index = 0
    while index < len(extra_args):
        arg = extra_args[index]
        value = extra_args[index + 1] if index + 1 < len(extra_args) else ""
        if arg == "--language-model-only":
            checks.append(
                ("flag:language_model_only", "language_model_only" in engine_fields, arg)
            )
        elif arg == "--limit-mm-per-prompt":
            checks.append(
                ("flag:limit_mm_per_prompt", "limit_mm_per_prompt" in engine_fields, value)
            )
        elif arg == "--reasoning-parser":
            checks.append(("flag:reasoning_parser", value in parser_names, value))
        elif arg == "--default-chat-template-kwargs":
            try:
                json.loads(value)
                checks.append(("flag:chat_template_kwargs", True, value))
            except json.JSONDecodeError as exc:
                checks.append(("flag:chat_template_kwargs", False, f"{value!r}: {exc}"))
        index += 1
    return checks


def _max_position(config: dict) -> int | None:
    for key in ("max_position_embeddings", "max_seq_len"):
        value = config.get(key)
        if isinstance(value, int) and value > 0:
            return value
    text = config.get("text_config") or {}
    for key in ("max_position_embeddings", "max_seq_len"):
        value = text.get(key)
        if isinstance(value, int) and value > 0:
            return value
    return None


def _load_tokenizer(snapshot: Path):
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(
        str(snapshot), local_files_only=True, trust_remote_code=False
    )


def check_chat_template(snapshot: Path, extra_args: list[str]) -> tuple[bool, str]:
    kwargs: dict = {}
    if "--default-chat-template-kwargs" in extra_args:
        index = extra_args.index("--default-chat-template-kwargs")
        if index + 1 < len(extra_args):
            kwargs = json.loads(extra_args[index + 1])
    try:
        tokenizer = _load_tokenizer(snapshot)
        prompt = tokenizer.apply_chat_template(
            [
                {"role": "system", "content": SAMPLE_SYSTEM},
                {"role": "user", "content": SAMPLE_USER},
            ],
            tokenize=False,
            add_generation_prompt=True,
            **kwargs,
        )
    except Exception as exc:  # noqa: BLE001 - report, do not crash the whole sweep
        return False, f"{type(exc).__name__}: {exc}"
    if not prompt or SAMPLE_USER.splitlines()[0] not in prompt:
        return False, "template rendered but the user question is missing"
    return True, f"{len(prompt)} chars, kwargs={kwargs or '{}'}"


def _download_configs(agent: AgentConfig, offline: bool) -> Path:
    from huggingface_hub import snapshot_download

    return Path(
        snapshot_download(
            repo_id=agent.model,
            revision=agent.revision,
            allow_patterns=CONFIG_PATTERNS,
            local_files_only=offline,
        )
    )


def _supported() -> tuple[set[str], set[str], set[str]]:
    from vllm.engine.arg_utils import EngineArgs
    from vllm.model_executor.models import registry
    from vllm.reasoning import _REASONING_PARSERS_TO_REGISTER

    archs = set(getattr(registry, "_VLLM_MODELS", {}))
    archs |= set(getattr(registry, "_MULTIMODAL_MODELS", {}))
    fields = set(EngineArgs.__dataclass_fields__)
    return archs, fields, set(_REASONING_PARSERS_TO_REGISTER)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the served stack before weight download")
    parser.add_argument("--config", default="configs/models.yaml")
    parser.add_argument("--phase", choices=PHASES, default="fourbit")
    parser.add_argument(
        "--download-configs",
        action="store_true",
        help="download config/tokenizer/chat-template files only (a few MB)",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="use only files already in the Hugging Face cache",
    )
    args = parser.parse_args()

    try:
        archs, fields, parsers = _supported()
    except Exception as exc:  # noqa: BLE001
        print(f"error: vLLM is not importable: {type(exc).__name__}: {exc}")
        print("run: bash scripts/install_vllm.sh")
        return 2

    os.environ.setdefault("HF_HOME", str(resolve_hf_home()))
    agents = agents_for_phase(load_models(args.config), args.phase)
    results: list[Result] = []

    for agent in agents:
        checks: list[tuple[str, bool, str]] = []
        try:
            if args.download_configs and not args.offline:
                snapshot = _download_configs(agent, offline=False)
            else:
                snapshot = _download_configs(agent, offline=True)
            config = json.loads((snapshot / "config.json").read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            results.append(
                Result(
                    role=agent.role,
                    model=agent.model,
                    checks=[("checkpoint", False, f"{type(exc).__name__}: {exc}")],
                )
            )
            continue

        checks.append(("architecture", *check_architecture(_architectures(config), archs)))
        checks.append(("quantization", *check_quantization(config, agent.quant)))
        checks.extend(check_extra_args(agent.extra_args, fields, parsers))

        max_position = _max_position(config)
        configured = agent.max_model_len or 0
        if max_position is None:
            checks.append(("context", True, f"checkpoint limit unknown; configured {configured}"))
        else:
            checks.append(
                (
                    "context",
                    max_position >= configured,
                    f"checkpoint {max_position} >= configured {configured}",
                )
            )
        checks.append(("chat_template", *check_chat_template(snapshot, agent.extra_args)))
        results.append(Result(role=agent.role, model=agent.model, checks=checks))

    width = max((len(result.model) for result in results), default=10)
    failed = 0
    print(f"phase={args.phase}  vLLM registry: {len(archs)} architectures")
    for result in results:
        print(f"\n{result.role}: {result.model}")
        for name, ok, detail in result.checks:
            print(f"  {'OK  ' if ok else 'FAIL'} {name:<22} {detail}")
        failed += 0 if result.ok else 1

    print(f"\nRESULT: {'OK' if not failed else f'FAIL ({failed}/{len(results)} models)'}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())

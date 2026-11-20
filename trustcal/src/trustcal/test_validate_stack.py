"""Pure checks for scripts/validate_stack.py (no vLLM import required)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # trustcal/
sys.path.insert(0, str(ROOT / "scripts"))

import validate_stack  # noqa: E402


def test_architecture_registered() -> None:
    ok, detail = validate_stack.check_architecture(
        ["Qwen3_5ForConditionalGeneration"], {"Qwen3_5ForConditionalGeneration"}
    )
    assert ok is True
    assert "Qwen3_5" in detail


def test_architecture_missing_is_reported() -> None:
    ok, detail = validate_stack.check_architecture(["NotARealModel"], {"Qwen3ForCausalLM"})
    assert ok is False
    assert "NotARealModel" in detail


def test_compressed_tensors_accepts_pack_quantized() -> None:
    config = {"quantization_config": {"format": "pack-quantized"}}
    ok, detail = validate_stack.check_quantization(config, "compressed-tensors")
    assert ok is True
    assert "pack-quantized" in detail


def test_compressed_tensors_rejects_plain_fp16() -> None:
    ok, detail = validate_stack.check_quantization({}, "compressed-tensors")
    assert ok is False
    assert "missing" in detail


def test_serve_flags_are_checked_against_the_engine() -> None:
    checks = validate_stack.check_extra_args(
        [
            "--language-model-only",
            "--limit-mm-per-prompt",
            '{"image": 0}',
            "--reasoning-parser",
            "qwen3",
        ],
        {"language_model_only", "limit_mm_per_prompt"},
        {"qwen3"},
    )
    assert all(ok for _, ok, _ in checks)


def test_unknown_reasoning_parser_fails() -> None:
    checks = validate_stack.check_extra_args(
        ["--reasoning-parser", "not-a-parser"],
        set(),
        {"qwen3"},
    )
    assert checks[0][1] is False


def test_bad_chat_template_json_fails() -> None:
    checks = validate_stack.check_extra_args(
        ["--default-chat-template-kwargs", "{not json"],
        set(),
        set(),
    )
    assert checks[0][1] is False


def test_context_limit_reads_text_config() -> None:
    assert validate_stack._max_position({"text_config": {"max_position_embeddings": 262144}}) == 262144
    assert validate_stack._max_position({"max_position_embeddings": 8192}) == 8192
    assert validate_stack._max_position({}) is None

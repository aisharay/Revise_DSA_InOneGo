"""Validate canonical LLD pattern snippets in generated website data."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from lld_pattern_overrides import PATTERN_SNIPPETS, TARGET_CATEGORY_PREFIXES


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTENT = PROJECT_ROOT / "public" / "data" / "dsa-content.json"


def iter_sections(nodes: list[dict[str, Any]]):
    for section in nodes:
        yield section
        yield from iter_sections(section["children"])


def validate_content() -> None:
    data = json.loads(CONTENT.read_text(encoding="utf-8"))
    target_sections = {
        section["id"]: section
        for category in data["categories"]
        if category["id"].startswith(TARGET_CATEGORY_PREFIXES)
        for section in iter_sections(category["sections"])
    }

    expected = set(PATTERN_SNIPPETS)
    actual = set(target_sections)
    if actual != expected:
        raise RuntimeError(
            f"target section mismatch; missing={sorted(expected - actual)}, "
            f"unexpected={sorted(actual - expected)}"
        )

    errors = []
    for section_id, expected_code in PATTERN_SNIPPETS.items():
        code_blocks = [
            block["text"]
            for block in target_sections[section_id]["blocks"]
            if block["type"] == "code"
        ]
        if len(code_blocks) != 1:
            errors.append(f"{section_id}: expected 1 code block, found {len(code_blocks)}")
        elif code_blocks[0] != expected_code:
            errors.append(f"{section_id}: generated code does not match canonical override")
    if errors:
        raise RuntimeError("\n".join(errors))


def compile_snippets(compiler: str) -> None:
    command = [compiler, "-x", "c++", "-std=c++17", "-pthread", "-fsyntax-only", "-"]
    failures = []
    for section_id, code in PATTERN_SNIPPETS.items():
        result = subprocess.run(
            command,
            input=code,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode:
            failures.append(f"{section_id}:\n{result.stderr.strip()}")
    if failures:
        raise RuntimeError("\n\n".join(failures))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--compile",
        action="store_true",
        help="syntax-check every snippet with an available C++ compiler",
    )
    args = parser.parse_args()

    validate_content()
    message = f"Validated {len(PATTERN_SNIPPETS)} patterns with exactly one code block each"
    if args.compile:
        compiler = shutil.which("g++") or shutil.which("clang++")
        if compiler is None:
            raise RuntimeError("--compile requested, but g++/clang++ was not found")
        compile_snippets(compiler)
        message += f"; all snippets compile as C++17 with {Path(compiler).name}"
    print(message)


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, json.JSONDecodeError) as error:
        print(f"Validation failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error

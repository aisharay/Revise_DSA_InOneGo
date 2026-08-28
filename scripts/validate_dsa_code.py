"""Validate that generated DSA code blocks are coherent and revision-ready."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTENT = PROJECT_ROOT / "public" / "data" / "dsa-content.json"


def iter_sections(nodes: list[dict[str, Any]]):
    for section in nodes:
        yield section
        yield from iter_sections(section["children"])


def main() -> None:
    data = json.loads(CONTENT.read_text(encoding="utf-8"))
    blocks = [
        (section["id"], block["text"])
        for category in data["categories"]
        if category["library"] == "dsa"
        for section in iter_sections(category["sections"])
        for block in section["blocks"]
        if block["type"] == "code"
    ]

    errors = []
    for section_id, code in blocks:
        if code.count("{") != code.count("}"):
            errors.append(f"{section_id}: unbalanced braces")
        lines = [line.strip() for line in code.splitlines() if line.strip()]
        if lines and all(line.startswith("//") for line in lines):
            errors.append(f"{section_id}: comment-only content rendered as code")
        if any(line in {"↓", "↑", "→", "←"} for line in lines):
            errors.append(f"{section_id}: diagram marker rendered as code")

    if errors:
        raise RuntimeError("\n".join(errors))
    print(f"Validated {len(blocks)} coherent DSA code blocks")


if __name__ == "__main__":
    main()

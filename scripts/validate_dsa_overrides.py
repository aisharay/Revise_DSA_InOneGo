"""Validate that every audited DSA correction is present in generated content."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from dsa_overrides import (
    DSA_CODE_OVERRIDES,
    DSA_REVIEWED_CATEGORY_IDS,
    DSA_TEXT_REMOVALS,
    DSA_TEXT_REPLACEMENTS,
)
from extract_docx import format_cpp_code


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTENT = PROJECT_ROOT / "public" / "data" / "dsa-content.json"


def iter_sections(nodes: list[dict[str, Any]]):
    for section in nodes:
        yield section
        yield from iter_sections(section["children"])


def main() -> None:
    data = json.loads(CONTENT.read_text(encoding="utf-8"))
    actual_categories = {
        category["id"]
        for category in data["categories"]
        if category["library"] == "dsa"
    }
    if actual_categories != DSA_REVIEWED_CATEGORY_IDS:
        raise RuntimeError(
            "DSA category audit coverage changed; "
            f"missing={sorted(DSA_REVIEWED_CATEGORY_IDS - actual_categories)}, "
            f"unreviewed={sorted(actual_categories - DSA_REVIEWED_CATEGORY_IDS)}"
        )
    sections = {
        section["id"]: section
        for category in data["categories"]
        if category["library"] == "dsa"
        for section in iter_sections(category["sections"])
    }

    errors = []
    for section_id, expected_blocks in DSA_CODE_OVERRIDES.items():
        section = sections.get(section_id)
        if section is None:
            errors.append(f"{section_id}: section is missing")
            continue
        generated_blocks = [
            block["text"] for block in section["blocks"] if block["type"] == "code"
        ]
        formatted_expected = [format_cpp_code(code) for code in expected_blocks]
        if generated_blocks != formatted_expected:
            errors.append(
                f"{section_id}: generated code does not exactly match its audited override"
            )

    for section_id, replacements in DSA_TEXT_REPLACEMENTS.items():
        section = sections.get(section_id)
        if section is None:
            errors.append(f"{section_id}: text-correction section is missing")
            continue
        generated_text = {block.get("text") for block in section["blocks"]}
        for old_text, new_text in replacements.items():
            if old_text in generated_text or new_text not in generated_text:
                errors.append(f"{section_id}: audited wording correction is missing")

    for section_id, removals in DSA_TEXT_REMOVALS.items():
        generated_text = {
            block.get("text") for block in sections[section_id]["blocks"]
        }
        leftovers = removals & generated_text
        if leftovers:
            errors.append(
                f"{section_id}: obsolete fragments remain: {sorted(leftovers)}"
            )

    if errors:
        raise RuntimeError("\n".join(errors))
    removed = sum(not blocks for blocks in DSA_CODE_OVERRIDES.values())
    print(
        f"Validated all {len(DSA_REVIEWED_CATEGORY_IDS)} audited DSA chapters and "
        f"{len(DSA_CODE_OVERRIDES)} section overrides "
        f"({removed} non-code sections cleaned)"
    )


if __name__ == "__main__":
    main()

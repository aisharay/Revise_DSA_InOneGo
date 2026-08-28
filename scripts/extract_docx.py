"""Convert the DSA and LLD DOCX handbooks into structured website data."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from html import escape
from pathlib import Path
from typing import Any

from docx import Document
from docx.document import Document as DocumentObject
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P

from dsa_overrides import (
    DSA_CODE_OVERRIDES,
    DSA_TEXT_REMOVALS,
    DSA_TEXT_REPLACEMENTS,
)
from lld_pattern_overrides import PATTERN_SNIPPETS, TARGET_CATEGORY_PREFIXES


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DSA_SOURCE = Path(r"C:\Users\aisharay\Downloads\1. DSA (2).docx")
DEFAULT_LLD_SOURCE = Path(r"C:\Users\aisharay\Downloads\LLD.docx")
OUTPUT = PROJECT_ROOT / "public" / "data" / "dsa-content.json"
CHAPTERS_DIR = PROJECT_ROOT / "chapters"

CHAPTER_ORDER = [
    "3-searching-and-sorting",
    "4-bit-algo",
    "1-number-theory",
    "2-string",
    "5-linkedlist",
    "7-stack-and-queue",
    "6-heap",
    "13-hashing",
    "15-two-pointer-and-sliding-window",
    "16-prefix-sum-and-difference-array",
    "14-greedy",
    "19-backtracking",
    "8-tree",
    "9-bst",
    "10-segment-tree-n-trie",
    "18-fenwick-tree-binary-index-tree",
    "17-dsu",
    "11-graph",
    "12-dp",
    "20-backtracking-advanced",
    "21-graph-advanced",
    "22-string-advanced",
    "23-segment-tree-advanced",
    "24-network-flow",
    "25-meet-in-the-middle",
    "tab-26",
]

CODE_START = re.compile(
    r"^(?:#include|using namespace|template\s*<|class\s+\w|struct\s+\w|"
    r"(?:[\w:<>,*&]+\s+)+[\w:~]+\s*\(|"
    r"(?:const\s+)?(?:unsigned\s+)?(?:long long|int|bool|void|double|char|string|auto|"
    r"vector|map|unordered_map|set|unordered_set|stack|queue|deque|priority_queue|pair)"
    r"(?:\s*<[^;{}=]+>)?[\s*&]+\w|"
    r"if\s*\(|else(?:\s+if)?\b|for\s*\(|while\s*\(|do\s*\{|switch\s*\(|case\s+|"
    r"return(?:\s+.+)?;|break\s*;|continue\s*;|public:|private:|protected:|"
    r"\w+(?:::\w+)?\s*\([^)]*\)\s*(?:const\s*)?\{|"
    r"[{}]|//)"
)


def slugify(value: str) -> str:
    value = value.lower().replace("—", "-").replace("–", "-")
    value = re.sub(r"[^\w\s-]", "", value, flags=re.UNICODE)
    value = re.sub(r"[\s_-]+", "-", value).strip("-")
    return value or "section"


def clean_text(value: str) -> str:
    value = value.replace("\u00a0", " ").replace("\ufffd", "—")
    value = re.sub(r"[ \t]+", " ", value)
    return "\n".join(line.rstrip() for line in value.splitlines()).strip()


def clean_code_text(value: str) -> str:
    value = value.replace("\u00a0", " ").replace("\ufffd", "—").replace("\t", "    ")
    return "\n".join(line.rstrip() for line in value.splitlines()).strip("\n")


def unique_slug(base: str, used: set[str]) -> str:
    candidate = base
    index = 2
    while candidate in used:
        candidate = f"{base}-{index}"
        index += 1
    used.add(candidate)
    return candidate


def iter_blocks(document: DocumentObject):
    for child in document.element.body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, document)
        elif isinstance(child, CT_Tbl):
            yield Table(child, document)


def looks_like_code(text: str) -> bool:
    raw_lines = [line for line in text.splitlines() if line.strip()]
    lines = [line.strip() for line in raw_lines]
    if not lines:
        return False
    if len(lines) == 1 and re.fullmatch(r"[\)\]\}]+\s*(?:const\s*)?\{?", lines[0]):
        return True
    if len(lines) == 1 and lines[0].endswith(";"):
        return True
    signals = 0
    for line in lines:
        if CODE_START.search(line):
            signals += 2
        if line.endswith((";", "{", "}")):
            signals += 1
        if any(token in line for token in ("->", "++", "--", "&&", "||", "::", "[", "]")):
            signals += 1
    return signals >= max(2, len(lines))


def paragraph_block(
    paragraph: Paragraph, continue_code: bool = False
) -> dict[str, Any] | None:
    raw_text = clean_code_text(paragraph.text)
    text = clean_text(raw_text)
    if not text:
        return None

    lowered = text.lower()
    if lowered.startswith("question:"):
        kind = "question"
    elif lowered.startswith(("time:", "space:", "complexity:", "average time:", "worst time:")):
        kind = "complexity"
    elif lowered.startswith(("important:", "note:", "why?", "key idea:", "observation:")):
        kind = "callout"
    elif lowered.startswith(("definition:", "explanation:", "👉 explanation:")):
        kind = "text"
    elif looks_like_code(raw_text) or continue_code:
        kind = "code"
    else:
        kind = "text"

    return {"type": kind, "text": raw_text if kind == "code" else text}


def table_block(table: Table) -> dict[str, Any]:
    rows = []
    for row in table.rows:
        rows.append([clean_text(cell.text) for cell in row.cells])
    return {"type": "table", "rows": rows}


def append_block(target: list[dict[str, Any]], block: dict[str, Any]) -> None:
    if block["type"] == "code" and target and target[-1]["type"] == "code":
        target[-1]["text"] += "\n" + block["text"]
        return
    if block["type"] == "complexity" and target and target[-1]["type"] == "complexity":
        target[-1]["text"] += "\n" + block["text"]
        return
    target.append(block)


def continues_code_block(target: list[dict[str, Any]], raw_text: str) -> bool:
    if not target or target[-1]["type"] != "code":
        return False
    previous = target[-1]["text"].rstrip()
    brace_depth = previous.count("{") - previous.count("}")
    first_line = next((line for line in raw_text.splitlines() if line.strip()), "")
    is_indented = len(first_line) - len(first_line.lstrip()) >= 4
    has_continuation = previous.endswith(
        ("(", ",", "=", "&&", "||", "+", "-", "*", "/", "<<", ">>")
    )
    return brace_depth > 0 or is_indented or has_continuation


def extract(source: Path) -> dict[str, Any]:
    document = Document(source)
    categories: list[dict[str, Any]] = []
    category: dict[str, Any] | None = None
    stack: list[dict[str, Any]] = []
    used_ids: set[str] = set()
    paragraph_count = 0
    question_count = 0
    table_count = 0

    for item in iter_blocks(document):
        if isinstance(item, Paragraph):
            text = clean_text(item.text)
            if not text:
                continue
            paragraph_count += 1
            style = item.style.name

            if style == "Title":
                category_id = unique_slug(slugify(text), used_ids)
                category = {
                    "id": category_id,
                    "title": text,
                    "blocks": [],
                    "sections": [],
                }
                categories.append(category)
                stack = []
                continue

            heading_match = re.fullmatch(r"Heading ([1-4])", style)
            if heading_match:
                if category is None:
                    category = {
                        "id": unique_slug("dsa-notes", used_ids),
                        "title": "DSA Notes",
                        "blocks": [],
                        "sections": [],
                    }
                    categories.append(category)

                level = int(heading_match.group(1))
                section = {
                    "id": unique_slug(f"{category['id']}-{slugify(text)}", used_ids),
                    "title": text,
                    "level": level,
                    "blocks": [],
                    "children": [],
                }
                while stack and stack[-1]["level"] >= level:
                    stack.pop()
                if stack:
                    stack[-1]["children"].append(section)
                else:
                    category["sections"].append(section)
                stack.append(section)
                continue

            if category is None:
                category = {
                    "id": unique_slug("dsa-notes", used_ids),
                    "title": "DSA Notes",
                    "blocks": [],
                    "sections": [],
                }
                categories.append(category)
            target = stack[-1]["blocks"] if stack else category["blocks"]
            block = paragraph_block(item, continues_code_block(target, item.text))
            if block is None:
                continue
            if block["type"] == "question":
                question_count += 1
            append_block(target, block)
        else:
            table_count += 1
            block = table_block(item)
            if category is None:
                category = {
                    "id": unique_slug("dsa-notes", used_ids),
                    "title": "DSA Notes",
                    "blocks": [],
                    "sections": [],
                }
                categories.append(category)
            target = stack[-1]["blocks"] if stack else category["blocks"]
            target.append(block)

    def count_sections(nodes: list[dict[str, Any]]) -> int:
        return sum(1 + count_sections(node["children"]) for node in nodes)

    def count_blocks(kind: str, nodes: list[dict[str, Any]]) -> int:
        total = 0
        for node in nodes:
            total += sum(block["type"] == kind for block in node["blocks"])
            total += count_blocks(kind, node["children"])
        return total

    section_count = sum(count_sections(item["sections"]) for item in categories)
    code_count = sum(
        sum(block["type"] == "code" for block in item["blocks"])
        + count_blocks("code", item["sections"])
        for item in categories
    )
    order = {category_id: index for index, category_id in enumerate(CHAPTER_ORDER)}
    categories.sort(key=lambda item: order.get(item["id"], len(order)))
    return {
        "meta": {
            "title": "DSA Vault",
            "subtitle": "Concepts, patterns, questions & implementations",
            "source": source.name,
            "categories": len(categories),
            "sections": section_count,
            "questions": question_count,
            "codeBlocks": code_count,
            "tables": table_count,
            "paragraphs": paragraph_count,
        },
        "categories": categories,
    }


def add_library(data: dict[str, Any], library: str, prefix_ids: bool = False) -> None:
    def update_section(section: dict[str, Any]) -> None:
        if prefix_ids:
            section["id"] = f"{library}-{section['id']}"
        for child in section["children"]:
            update_section(child)

    for category in data["categories"]:
        category["library"] = library
        if prefix_ids:
            category["id"] = f"{library}-{category['id']}"
        for section in category["sections"]:
            update_section(section)


def combine_libraries(dsa: dict[str, Any], lld: dict[str, Any]) -> dict[str, Any]:
    add_library(dsa, "dsa")
    add_library(lld, "lld", prefix_ids=True)
    count_fields = ("categories", "sections", "questions", "codeBlocks", "tables", "paragraphs")
    meta = {
        "title": "Interview Vault",
        "subtitle": "DSA algorithms, LLD patterns, questions & implementations",
        "sources": [dsa["meta"]["source"], lld["meta"]["source"]],
        "libraries": [
            {
                "id": "dsa",
                "title": "DSA",
                "description": "Data structures, algorithms, patterns, and implementations",
            },
            {
                "id": "lld",
                "title": "LLD",
                "description": "Object-oriented design, patterns, and interview systems",
            },
        ],
    }
    for field in count_fields:
        meta[field] = dsa["meta"][field] + lld["meta"][field]
    return {"meta": meta, "categories": dsa["categories"] + lld["categories"]}


def convert_conceptual_blocks(data: dict[str, Any]) -> None:
    """Render diagrams and conceptual comment lists as notes, not executable C++."""

    def update(block: dict[str, Any]) -> None:
        if block["type"] != "code":
            return
        lines = [line.strip() for line in block["text"].splitlines() if line.strip()]
        if any(line in {"↓", "↑", "→", "←"} for line in lines):
            block["type"] = "text"
            return
        if lines and all(line.startswith("//") for line in lines):
            block["type"] = "callout"
            block["text"] = "\n".join(line.removeprefix("//").strip() for line in lines)

    for category in data["categories"]:
        for block in iter_category_blocks(category):
            update(block)


def apply_dsa_code_overrides(data: dict[str, Any]) -> None:
    """Replace audited DSA snippets while retaining their revision notes."""
    sections: dict[str, dict[str, Any]] = {}

    def collect(nodes: list[dict[str, Any]]) -> None:
        for section in nodes:
            sections[section["id"]] = section
            collect(section["children"])

    for category in data["categories"]:
        if category["library"] == "dsa":
            collect(category["sections"])

    unknown = DSA_CODE_OVERRIDES.keys() - sections.keys()
    if unknown:
        raise ValueError(f"DSA overrides reference missing sections: {sorted(unknown)}")

    unknown_text_sections = DSA_TEXT_REPLACEMENTS.keys() - sections.keys()
    if unknown_text_sections:
        raise ValueError(
            f"DSA text replacements reference missing sections: {sorted(unknown_text_sections)}"
        )

    for section_id, replacements in DSA_TEXT_REPLACEMENTS.items():
        section = sections[section_id]
        for old_text, new_text in replacements.items():
            matches = [
                block
                for block in section["blocks"]
                if block.get("text") == old_text
            ]
            if len(matches) != 1:
                raise ValueError(
                    f"{section_id}: expected one exact text match for {old_text!r}, "
                    f"found {len(matches)}"
                )
            matches[0]["text"] = new_text

    unknown_removal_sections = DSA_TEXT_REMOVALS.keys() - sections.keys()
    if unknown_removal_sections:
        raise ValueError(
            f"DSA text removals reference missing sections: {sorted(unknown_removal_sections)}"
        )

    for section_id, removals in DSA_TEXT_REMOVALS.items():
        section = sections[section_id]
        existing = {block.get("text") for block in section["blocks"]}
        missing_removals = removals - existing
        if missing_removals:
            raise ValueError(
                f"{section_id}: expected obsolete text fragments are missing: "
                f"{sorted(missing_removals)}"
            )
        section["blocks"] = [
            block for block in section["blocks"] if block.get("text") not in removals
        ]

    for section_id, corrected_blocks in DSA_CODE_OVERRIDES.items():
        section = sections[section_id]
        replacement = iter(corrected_blocks)
        remaining = len(corrected_blocks)
        rebuilt = []
        last_code_output = None
        for block in section["blocks"]:
            if block["type"] != "code":
                rebuilt.append(block)
                continue
            if remaining:
                rebuilt.append({"type": "code", "text": next(replacement)})
                remaining -= 1
                last_code_output = len(rebuilt)

        extra_blocks = [
            {"type": "code", "text": code} for code in replacement
        ]
        if extra_blocks:
            insert_at = last_code_output if last_code_output is not None else len(rebuilt)
            rebuilt[insert_at:insert_at] = extra_blocks
        section["blocks"] = rebuilt


CLANG_FORMAT_STYLE = (
    "{BasedOnStyle: Google, ColumnLimit: 120, IndentWidth: 4, "
    "ContinuationIndentWidth: 4, AllowShortFunctionsOnASingleLine: Empty, "
    "BinPackArguments: true, BinPackParameters: true, SortIncludes: Never}"
)


def format_cpp_code(source: str) -> str:
    """Format one C++ snippet with the site's canonical style."""
    formatter = shutil.which("clang-format")
    if formatter is None:
        raise RuntimeError(
            "clang-format is required to generate DSA content. "
            "Install dependencies with: python -m pip install -r requirements.txt"
        )

    result = subprocess.run(
        [formatter, f"--style={CLANG_FORMAT_STYLE}"],
        input=source,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(f"clang-format failed: {result.stderr.strip()}")
    return result.stdout.rstrip()


def format_dsa_code(data: dict[str, Any]) -> None:
    """Apply a compact, consistent C++ style to every DSA code block."""
    for category in data["categories"]:
        if category["library"] != "dsa":
            continue
        for block in iter_category_blocks(category):
            if block["type"] != "code":
                continue
            block["text"] = format_cpp_code(block["text"])


def apply_lld_pattern_overrides(data: dict[str, Any]) -> None:
    """Replace extracted pattern fragments while retaining every non-code block."""
    found: set[str] = set()

    def keep_pattern_prose(block: dict[str, Any]) -> bool:
        if block["type"] == "code":
            return False
        if block["type"] != "text":
            return True
        return block["text"].startswith(("Definition:", "👉 Explanation:"))

    def visit(section: dict[str, Any]) -> None:
        snippet = PATTERN_SNIPPETS.get(section["id"])
        if snippet is not None:
            found.add(section["id"])
            blocks = section["blocks"]
            first_code = next(
                (index for index, block in enumerate(blocks) if block["type"] == "code"),
                len(blocks),
            )
            section["blocks"] = [
                *[block for block in blocks[:first_code] if keep_pattern_prose(block)],
                {"type": "code", "text": snippet},
                *[block for block in blocks[first_code:] if keep_pattern_prose(block)],
            ]
        for child in section["children"]:
            visit(child)

    target_categories = [
        category
        for category in data["categories"]
        if category["id"].startswith(TARGET_CATEGORY_PREFIXES)
    ]
    for category in target_categories:
        for section in category["sections"]:
            visit(section)

    missing = set(PATTERN_SNIPPETS) - found
    if missing:
        raise ValueError(f"LLD pattern overrides reference missing sections: {sorted(missing)}")

    data["meta"]["codeBlocks"] = sum(
        block["type"] == "code"
        for category in data["categories"]
        for block in iter_category_blocks(category)
    )


def iter_category_blocks(category: dict[str, Any]):
    yield from category["blocks"]

    def visit(nodes: list[dict[str, Any]]):
        for section in nodes:
            yield from section["blocks"]
            yield from visit(section["children"])

    yield from visit(category["sections"])


def write_chapter_pages(data: dict[str, Any]) -> None:
    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)
    category_ids = {category["id"] for category in data["categories"]}
    for existing in CHAPTERS_DIR.glob("*.html"):
        if existing.stem not in category_ids:
            existing.unlink()

    for category in data["categories"]:
        title = re.sub(r"^\d+\.\s*", "", category["title"])
        page = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta
      name="description"
      content="{escape(title)} — concepts, questions, complexity analysis, and C++ implementations."
    />
    <meta name="theme-color" content="#0b1020" />
    <title>{escape(title)} — Interview Vault</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Manrope:wght@600;700;800&display=swap"
      rel="stylesheet"
    />
    <link rel="stylesheet" href="../src/styles.css" />
  </head>
  <body data-category="{escape(category["id"])}" data-library="{escape(category["library"])}">
    <div id="app">
      <div class="boot-screen">
        <div class="boot-mark">DV</div>
        <p>Opening {escape(title)}…</p>
      </div>
    </div>
    <script type="module" src="../src/main.js"></script>
  </body>
</html>
"""
        (CHAPTERS_DIR / f"{category['id']}.html").write_text(page, encoding="utf-8")

    review_page = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="Review starred DSA and LLD concepts and implementations." />
    <meta name="theme-color" content="#0b1020" />
    <title>Starred Review — Interview Vault</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Manrope:wght@600;700;800&display=swap"
      rel="stylesheet"
    />
    <link rel="stylesheet" href="./src/styles.css" />
  </head>
  <body data-view="starred">
    <div id="app">
      <div class="boot-screen">
        <div class="boot-mark">★</div>
        <p>Preparing your review list…</p>
      </div>
    </div>
    <script type="module" src="./src/main.js"></script>
  </body>
</html>
"""
    (PROJECT_ROOT / "starred.html").write_text(review_page, encoding="utf-8")


def main() -> None:
    dsa_source = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DSA_SOURCE
    lld_source = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_LLD_SOURCE
    for source in (dsa_source, lld_source):
        if not source.exists():
            raise SystemExit(f"Source document not found: {source}")

    data = combine_libraries(extract(dsa_source), extract(lld_source))
    convert_conceptual_blocks(data)
    apply_dsa_code_overrides(data)
    format_dsa_code(data)
    apply_lld_pattern_overrides(data)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    write_chapter_pages(data)
    meta = data["meta"]
    print(
        f"Extracted 2 libraries, {meta['categories']} chapters, {meta['sections']} sections, "
        f"{meta['questions']} questions, {meta['codeBlocks']} code blocks, "
        f"and {meta['tables']} tables; generated {meta['categories']} chapter pages"
    )


if __name__ == "__main__":
    main()

"""Convert the DSA and LLD DOCX handbooks into structured website data."""

from __future__ import annotations

import json
import re
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
    r"(?:const\s+)?(?:unsigned\s+)?(?:long long|int|bool|void|double|char|string|auto|"
    r"vector|map|unordered_map|set|unordered_set|stack|queue|deque|priority_queue|pair)"
    r"(?:\s*<[^;{}=]+>)?[\s*&]+\w|"
    r"if\s*\(|else(?:\s+if)?\b|for\s*\(|while\s*\(|do\s*\{|switch\s*\(|case\s+|"
    r"return\b|break\s*;|continue\s*;|public:|private:|protected:|"
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
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return False
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


def paragraph_block(paragraph: Paragraph) -> dict[str, Any] | None:
    text = clean_text(paragraph.text)
    if not text:
        return None

    lowered = text.lower()
    if looks_like_code(text):
        kind = "code"
    elif lowered.startswith("question:"):
        kind = "question"
    elif lowered.startswith(("time:", "space:", "complexity:", "average time:", "worst time:")):
        kind = "complexity"
    elif lowered.startswith(("important:", "note:", "why?", "key idea:", "observation:")):
        kind = "callout"
    else:
        kind = "text"

    return {"type": kind, "text": text}


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

            block = paragraph_block(item)
            if block is None:
                continue
            if block["type"] == "question":
                question_count += 1
            if category is None:
                category = {
                    "id": unique_slug("dsa-notes", used_ids),
                    "title": "DSA Notes",
                    "blocks": [],
                    "sections": [],
                }
                categories.append(category)
            target = stack[-1]["blocks"] if stack else category["blocks"]
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

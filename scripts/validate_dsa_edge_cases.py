"""Compile and run regression cases for high-risk corrected DSA snippets."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTENT = PROJECT_ROOT / "public" / "data" / "dsa-content.json"
PRELUDE = "#include <bits/stdc++.h>\nusing namespace std;\n\n"

TESTS = {
    "4-bit-algo-28-maximum-xor-using-binary-trie": r"""
        int main() {
            vector<int> values{3, 10, 5, 25, 2, 8};
            return findMaximumXOR(values) == 28 ? 0 : 1;
        }
    """,
    "4-bit-algo-29-maximum-xor-subarray": r"""
        int main() {
            vector<int> values{8, 1, 2, 12};
            return maxXorSubarray(values) == 15 ? 0 : 1;
        }
    """,
    "12-dp-27-advanced-dp-egg-dropping": r"""
        int main() {
            if (eggDrop(2, INT_MAX) != 65536) return 1;
            if (eggDrop(1, 100) != 100 || eggDrop(5, 0) != 0) return 2;
            try {
                (void)eggDrop(0, 1);
                return 3;
            } catch (const invalid_argument&) {
                return 0;
            }
        }
    """,
    "22-string-advanced-10-rolling-hash-double-hashing": r"""
        int main() {
            DoubleRollingHash hash("abcabc");
            if (!hash.equal(0, 2, 3, 5)) return 1;
            if (hash.equal(-1, 0, -1, 0)) return 2;
            if (hash.equal(0, 6, 0, 6)) return 3;
            return 0;
        }
    """,
    "22-string-advanced-14-suffix-array-lcp-longest-common-substring-of-two-strings": r"""
        int main() {
            string bytes;
            for (int value = 0; value <= 255; ++value) {
                bytes.push_back(static_cast<char>(value));
            }
            string a = string("prefix") + bytes + "suffix";
            return longestCommonSubstringSuffixArray(a, bytes) == bytes ? 0 : 1;
        }
    """,
    "23-segment-tree-advanced-5-dynamic-segment-tree": r"""
        int main() {
            DynamicSegmentTree tree(-10, 10);
            tree.add(-4, 7);
            tree.add(6, 11);
            tree.add(-4, -2);
            return tree.rangeSum(-5, 6) == 16 && tree.rangeSum(0, 10) == 11 ? 0 : 1;
        }
    """,
}


def iter_sections(nodes: list[dict[str, Any]]):
    for section in nodes:
        yield section
        yield from iter_sections(section["children"])


def main() -> None:
    compiler = shutil.which("g++") or shutil.which("clang++")
    if compiler is None:
        raise RuntimeError("g++ or clang++ is required for DSA regression validation")

    data = json.loads(CONTENT.read_text(encoding="utf-8"))
    sections = {
        section["id"]: section
        for category in data["categories"]
        if category["library"] == "dsa"
        for section in iter_sections(category["sections"])
    }

    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        for section_id, test in TESTS.items():
            code = "\n\n".join(
                block["text"]
                for block in sections[section_id]["blocks"]
                if block["type"] == "code"
            )
            source = temp / f"{section_id}.cpp"
            executable = temp / f"{section_id}.exe"
            source.write_text(PRELUDE + code + "\n\n" + test, encoding="utf-8")
            compile_result = subprocess.run(
                [compiler, "-std=c++17", "-O2", str(source), "-o", str(executable)],
                capture_output=True,
                text=True,
                check=False,
            )
            if compile_result.returncode:
                raise RuntimeError(
                    f"{section_id} did not compile:\n{compile_result.stderr.strip()}"
                )
            run_result = subprocess.run(
                [str(executable)],
                capture_output=True,
                text=True,
                check=False,
                timeout=30,
            )
            if run_result.returncode:
                raise RuntimeError(
                    f"{section_id} failed with exit code {run_result.returncode}"
                )

    print(f"Validated {len(TESTS)} corrected DSA edge-case regressions")


if __name__ == "__main__":
    main()

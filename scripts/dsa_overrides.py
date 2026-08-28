"""Aggregate audited C++17 corrections for the DSA library."""

from __future__ import annotations

from dsa_overrides_advanced import DSA_CODE_OVERRIDES as ADVANCED
from dsa_overrides_foundations import DSA_CODE_OVERRIDES as FOUNDATIONS
from dsa_overrides_graphs import DSA_CODE_OVERRIDES as GRAPHS
from dsa_overrides_linear import DSA_CODE_OVERRIDES as LINEAR
from dsa_overrides_trees import DSA_CODE_OVERRIDES as TREES


DSA_CODE_OVERRIDES: dict[str, list[str]] = {}

for group in (FOUNDATIONS, LINEAR, TREES, GRAPHS, ADVANCED):
    duplicate_ids = DSA_CODE_OVERRIDES.keys() & group.keys()
    if duplicate_ids:
        raise ValueError(f"Duplicate DSA override IDs: {sorted(duplicate_ids)}")
    DSA_CODE_OVERRIDES.update(group)


DSA_REVIEWED_CATEGORY_IDS = {
    "1-number-theory",
    "2-string",
    "3-searching-and-sorting",
    "4-bit-algo",
    "5-linkedlist",
    "6-heap",
    "7-stack-and-queue",
    "8-tree",
    "9-bst",
    "10-segment-tree-n-trie",
    "11-graph",
    "12-dp",
    "13-hashing",
    "14-greedy",
    "15-two-pointer-and-sliding-window",
    "16-prefix-sum-and-difference-array",
    "17-dsu",
    "18-fenwick-tree-binary-index-tree",
    "19-backtracking",
    "20-backtracking-advanced",
    "21-graph-advanced",
    "22-string-advanced",
    "23-segment-tree-advanced",
    "24-network-flow",
    "25-meet-in-the-middle",
    "tab-26",
}


DSA_TEXT_REPLACEMENTS: dict[str, dict[str, str]] = {
    "11-graph-58-cheapest-flight-with-k-stops-dp": {
        "Question: Find the cheapest path using at most K edges.": (
            "Question: Find the cheapest path using at most K stops "
            "(at most K + 1 edges)."
        ),
    },
}


DSA_TEXT_REMOVALS: dict[str, set[str]] = {
    "3-searching-and-sorting-29-sort-by-custom-comparator": {
        "sort(arr.begin(), arr.end(),",
        "[](const pair<int, int>& a,",
    },
    "5-linkedlist-14-sort-a-linked-list-merge-sort": {
        'genui{"learning_viz":{"type_id":"MERGE_SORT"}}',
    },
    "13-hashing-24-hash-based-frequency-ranking": {
        "nth_element(",
        "items.begin(),",
        "items.begin() + k,",
        "items.end(),",
        "greater<pair<int, int>>()",
    },
    "23-segment-tree-advanced-6-persistent-segment-tree": {
        "root.push_back(",
        "update(root.back(), 0, n - 1, idx, val)",
    },
    "23-segment-tree-advanced-9-segment-tree-coordinate-compression": {
        "vals.erase(unique(vals.begin(), vals.end()),",
    },
}

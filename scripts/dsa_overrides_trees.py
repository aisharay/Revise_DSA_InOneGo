"""Corrected C++17 overrides for tree, BST, segment-trie, and Fenwick DSA sections."""

from __future__ import annotations

from textwrap import dedent


def cpp(source: str) -> str:
    return dedent(source).strip()


DSA_CODE_OVERRIDES = {
    "8-tree-10-binary-lifting-lca": [
        cpp(
            r"""
            struct BinaryLiftingLCA {
                int log = 1;
                vector<int> depth;
                vector<vector<int>> up;
                const vector<vector<int>>& adj;

                BinaryLiftingLCA(const vector<vector<int>>& graph, int root = 0)
                    : depth(graph.size(), 0), adj(graph) {
                    int n = static_cast<int>(graph.size());
                    while ((1LL << log) <= max(1, n)) {
                        ++log;
                    }
                    up.assign(n, vector<int>(log, -1));
                    if (n > 0) {
                        dfs(root, -1);
                    }
                }

                void dfs(int u, int parent) {
                    up[u][0] = parent;
                    for (int j = 1; j < log; ++j) {
                        int mid = up[u][j - 1];
                        up[u][j] = (mid == -1 ? -1 : up[mid][j - 1]);
                    }
                    for (int v : adj[u]) {
                        if (v == parent) continue;
                        depth[v] = depth[u] + 1;
                        dfs(v, u);
                    }
                }

                int lca(int u, int v) const {
                    if (depth[u] < depth[v]) {
                        swap(u, v);
                    }
                    int diff = depth[u] - depth[v];
                    for (int j = log - 1; j >= 0; --j) {
                        if (diff & (1 << j)) {
                            u = up[u][j];
                        }
                    }
                    if (u == v) {
                        return u;
                    }
                    for (int j = log - 1; j >= 0; --j) {
                        if (up[u][j] != up[v][j]) {
                            u = up[u][j];
                            v = up[v][j];
                        }
                    }
                    return up[u][0];
                }
            };
            """
        )
    ],
    "8-tree-11-binary-lifting-kth-ancestor": [
        cpp(
            r"""
            int kthAncestor(int node, int k, const vector<vector<int>>& up) {
                if (node < 0 || node >= static_cast<int>(up.size()) || k < 0) {
                    return -1;
                }
                int bit = 0;
                while (k > 0 && node != -1) {
                    if (bit == static_cast<int>(up[node].size())) {
                        return -1;
                    }
                    if (k & 1) {
                        node = up[node][bit];
                    }
                    k >>= 1;
                    ++bit;
                }
                return node;
            }
            """
        )
    ],
    "8-tree-15-sum-of-distances-from-every-node": [
        cpp(
            r"""
            vector<int> subtreeSize;
            vector<long long> distSum;

            void dfs1(int u, int parent, int depth, const vector<vector<int>>& adj, int root) {
                subtreeSize[u] = 1;
                distSum[root] += depth;
                for (int v : adj[u]) {
                    if (v == parent) continue;
                    dfs1(v, u, depth + 1, adj, root);
                    subtreeSize[u] += subtreeSize[v];
                }
            }

            void dfs2(int u, int parent, const vector<vector<int>>& adj, int n) {
                for (int v : adj[u]) {
                    if (v == parent) continue;
                    distSum[v] = distSum[u] + n - 2LL * subtreeSize[v];
                    dfs2(v, u, adj, n);
                }
            }

            vector<long long> sumOfDistances(const vector<vector<int>>& adj, int root = 0) {
                int n = static_cast<int>(adj.size());
                if (n == 0) {
                    return {};
                }
                subtreeSize.assign(n, 0);
                distSum.assign(n, 0);
                dfs1(root, -1, 0, adj, root);
                dfs2(root, -1, adj, n);
                return distSum;
            }
            """
        )
    ],
    "8-tree-17-heavy-light-decomposition": [
        cpp(
            r"""
            struct HeavyLightDecomposition {
                vector<int> parent;
                vector<int> depth;
                vector<int> heavy;
                vector<int> head;
                vector<int> pos;
                vector<int> subtreeSize;
                int currentPos = 0;
                const vector<vector<int>>& adj;

                HeavyLightDecomposition(const vector<vector<int>>& graph, int root = 0)
                    : parent(graph.size(), -1),
                      depth(graph.size(), 0),
                      heavy(graph.size(), -1),
                      head(graph.size(), 0),
                      pos(graph.size(), 0),
                      subtreeSize(graph.size(), 0),
                      adj(graph) {
                    if (!graph.empty()) {
                        dfs(root, -1);
                        decompose(root, root);
                    }
                }

                int dfs(int u, int p) {
                    parent[u] = p;
                    subtreeSize[u] = 1;
                    int maxSubtree = 0;
                    for (int v : adj[u]) {
                        if (v == p) continue;
                        depth[v] = depth[u] + 1;
                        int childSize = dfs(v, u);
                        subtreeSize[u] += childSize;
                        if (childSize > maxSubtree) {
                            maxSubtree = childSize;
                            heavy[u] = v;
                        }
                    }
                    return subtreeSize[u];
                }

                void decompose(int u, int chainHead) {
                    head[u] = chainHead;
                    pos[u] = currentPos++;
                    if (heavy[u] != -1) {
                        decompose(heavy[u], chainHead);
                    }
                    for (int v : adj[u]) {
                        if (v == parent[u] || v == heavy[u]) continue;
                        decompose(v, v);
                    }
                }
            };
            """
        )
    ],
    "9-bst-5-find-rank-of-an-element-in-bst": [
        cpp(
            r"""
            struct Node {
                int val;
                int size;
                Node* left;
                Node* right;

                explicit Node(int v) : val(v), size(1), left(nullptr), right(nullptr) {}
            };
            """
        ),
        cpp(
            r"""
            int getSize(const Node* root) {
                return root == nullptr ? 0 : root->size;
            }

            void updateSize(Node* root) {
                if (root != nullptr) {
                    root->size = 1 + getSize(root->left) + getSize(root->right);
                }
            }
            """
        ),
        cpp(
            r"""
            int rankOfKey(const Node* root, int key) {
                int rank = 0;
                while (root != nullptr) {
                    if (key <= root->val) {
                        root = root->left;
                    } else {
                        rank += 1 + getSize(root->left);
                        root = root->right;
                    }
                }
                return rank;
            }
            """
        ),
    ],
    "9-bst-8-two-sum-in-bst": [
        cpp(
            r"""
            class BSTIterator {
                stack<TreeNode*> st;
                bool reverse;

                void pushPath(TreeNode* node) {
                    while (node != nullptr) {
                        st.push(node);
                        node = reverse ? node->right : node->left;
                    }
                }

               public:
                BSTIterator(TreeNode* root, bool isReverse) : reverse(isReverse) {
                    pushPath(root);
                }

                bool hasNext() const {
                    return !st.empty();
                }

                TreeNode* nextNode() {
                    TreeNode* node = st.top();
                    st.pop();
                    if (reverse) {
                        pushPath(node->left);
                    } else {
                        pushPath(node->right);
                    }
                    return node;
                }
            };

            bool findTarget(TreeNode* root, int k) {
                if (root == nullptr) {
                    return false;
                }
                BSTIterator left(root, false);
                BSTIterator right(root, true);
                if (!left.hasNext() || !right.hasNext()) {
                    return false;
                }
                TreeNode* lo = left.nextNode();
                TreeNode* hi = right.nextNode();
                while (lo != nullptr && hi != nullptr && lo != hi && lo->val <= hi->val) {
                    long long sum = 1LL * lo->val + hi->val;
                    if (sum == k) {
                        return true;
                    }
                    if (sum < k) {
                        if (!left.hasNext()) {
                            break;
                        }
                        lo = left.nextNode();
                    } else {
                        if (!right.hasNext()) {
                            break;
                        }
                        hi = right.nextNode();
                    }
                }
                return false;
            }
            """
        )
    ],
    "9-bst-17-augmented-bst-for-range-count": [
        cpp(
            r"""
            struct Node {
                int val;
                int size;
                Node* left;
                Node* right;

                explicit Node(int v) : val(v), size(1), left(nullptr), right(nullptr) {}
            };

            int getSize(const Node* root) {
                return root == nullptr ? 0 : root->size;
            }
            """
        ),
        cpp(
            r"""
            int countLessThan(const Node* root, long long x) {
                int ans = 0;
                while (root != nullptr) {
                    if (x <= root->val) {
                        root = root->left;
                    } else {
                        ans += 1 + getSize(root->left);
                        root = root->right;
                    }
                }
                return ans;
            }

            int rangeCount(const Node* root, int L, int R) {
                if (L > R) {
                    return 0;
                }
                return countLessThan(root, static_cast<long long>(R) + 1) -
                       countLessThan(root, static_cast<long long>(L));
            }
            """
        ),
    ],
    "10-segment-tree-n-trie-5-range-assignment-range-sum": [
        cpp(
            r"""
            void apply(vector<long long>& tree, vector<long long>& lazy, vector<bool>& hasLazy, int node, int l, int r,
                       long long val) {
                tree[node] = 1LL * (r - l + 1) * val;
                lazy[node] = val;
                hasLazy[node] = true;
            }

            void push(vector<long long>& tree, vector<long long>& lazy, vector<bool>& hasLazy, int node, int l, int r) {
                if (!hasLazy[node] || l == r) return;
                int mid = l + (r - l) / 2;
                apply(tree, lazy, hasLazy, 2 * node, l, mid, lazy[node]);
                apply(tree, lazy, hasLazy, 2 * node + 1, mid + 1, r, lazy[node]);
                hasLazy[node] = false;
                lazy[node] = 0;
            }

            void update(vector<long long>& tree, vector<long long>& lazy, vector<bool>& hasLazy, int node, int l, int r,
                        int ql, int qr, long long val) {
                if (qr < l || r < ql) return;
                if (ql <= l && r <= qr) {
                    apply(tree, lazy, hasLazy, node, l, r, val);
                    return;
                }
                push(tree, lazy, hasLazy, node, l, r);
                int mid = l + (r - l) / 2;
                update(tree, lazy, hasLazy, 2 * node, l, mid, ql, qr, val);
                update(tree, lazy, hasLazy, 2 * node + 1, mid + 1, r, ql, qr, val);
                tree[node] = tree[2 * node] + tree[2 * node + 1];
            }

            long long query(vector<long long>& tree, vector<long long>& lazy, vector<bool>& hasLazy, int node, int l,
                            int r, int ql, int qr) {
                if (qr < l || r < ql) return 0;
                if (ql <= l && r <= qr) return tree[node];
                push(tree, lazy, hasLazy, node, l, r);
                int mid = l + (r - l) / 2;
                return query(tree, lazy, hasLazy, 2 * node, l, mid, ql, qr) +
                       query(tree, lazy, hasLazy, 2 * node + 1, mid + 1, r, ql, qr);
            }
            """
        )
    ],
    "10-segment-tree-n-trie-11-find-k-th-one": [
        cpp(
            r"""
            int kthOne(const vector<int>& tree, int node, int l, int r, int k) {
                if (k <= 0 || tree[node] < k) return -1;
                if (l == r) return l;
                int mid = l + (r - l) / 2;
                if (tree[2 * node] >= k) {
                    return kthOne(tree, 2 * node, l, mid, k);
                }
                return kthOne(tree, 2 * node + 1, mid + 1, r, k - tree[2 * node]);
            }
            """
        )
    ],
    "10-segment-tree-n-trie-13-persistent-segment-tree": [
        cpp(
            r"""
            class PersistentSegmentTree {
                struct Node {
                    int left = 0;
                    int right = 0;
                    long long sum = 0;
                };

                vector<Node> seg{{}};

                int clone(int node) {
                    seg.push_back(seg[node]);
                    return static_cast<int>(seg.size()) - 1;
                }

               public:
                int build(const vector<int>& arr, int l, int r) {
                    int cur = clone(0);
                    if (l == r) {
                        seg[cur].sum = arr[l];
                        return cur;
                    }
                    int mid = l + (r - l) / 2;
                    seg[cur].left = build(arr, l, mid);
                    seg[cur].right = build(arr, mid + 1, r);
                    seg[cur].sum = seg[seg[cur].left].sum + seg[seg[cur].right].sum;
                    return cur;
                }

                int update(int oldRoot, int l, int r, int idx, int value) {
                    if (idx < l || idx > r) {
                        return oldRoot;
                    }
                    int cur = clone(oldRoot);
                    if (l == r) {
                        seg[cur].sum = value;
                        return cur;
                    }
                    int mid = l + (r - l) / 2;
                    if (idx <= mid) {
                        seg[cur].left = update(seg[oldRoot].left, l, mid, idx, value);
                    } else {
                        seg[cur].right = update(seg[oldRoot].right, mid + 1, r, idx, value);
                    }
                    seg[cur].sum = seg[seg[cur].left].sum + seg[seg[cur].right].sum;
                    return cur;
                }

                long long query(int root, int l, int r, int ql, int qr) const {
                    if (root == 0 || qr < l || r < ql) {
                        return 0;
                    }
                    if (ql <= l && r <= qr) {
                        return seg[root].sum;
                    }
                    int mid = l + (r - l) / 2;
                    return query(seg[root].left, l, mid, ql, qr) +
                           query(seg[root].right, mid + 1, r, ql, qr);
                }
            };
            """
        )
    ],
    "10-segment-tree-n-trie-14-dynamic-segment-tree": [
        cpp(
            r"""
            struct Node {
                long long sum = 0;
                unique_ptr<Node> left;
                unique_ptr<Node> right;
            };

            void update(unique_ptr<Node>& root, long long l, long long r, long long idx, long long val) {
                if (idx < l || idx > r) return;
                if (root == nullptr) root = make_unique<Node>();
                if (l == r) {
                    root->sum += val;
                    return;
                }
                long long mid = l + (r - l) / 2;
                if (idx <= mid) {
                    update(root->left, l, mid, idx, val);
                } else {
                    update(root->right, mid + 1, r, idx, val);
                }
                root->sum = (root->left ? root->left->sum : 0LL) + (root->right ? root->right->sum : 0LL);
            }

            long long query(const unique_ptr<Node>& root, long long l, long long r, long long ql, long long qr) {
                if (root == nullptr || qr < l || r < ql) return 0;
                if (ql <= l && r <= qr) return root->sum;
                long long mid = l + (r - l) / 2;
                return query(root->left, l, mid, ql, qr) + query(root->right, mid + 1, r, ql, qr);
            }
            """
        )
    ],
    "10-segment-tree-n-trie-23-word-search-ii-dfs-trie": [
        cpp(
            r"""
            class Solution {
                struct Node {
                    array<unique_ptr<Node>, 26> child{};
                    string word;
                };

                unique_ptr<Node> root = make_unique<Node>();
                vector<string> ans;

                void insert(const string& word) {
                    Node* node = root.get();
                    for (char c : word) {
                        int x = c - 'a';
                        if (!node->child[x]) {
                            node->child[x] = make_unique<Node>();
                        }
                        node = node->child[x].get();
                    }
                    node->word = word;
                }

                void dfs(vector<vector<char>>& board, int r, int c, Node* node) {
                    if (r < 0 || c < 0 || r >= static_cast<int>(board.size()) ||
                        c >= static_cast<int>(board[0].size())) {
                        return;
                    }
                    char ch = board[r][c];
                    if (ch == '#') return;
                    Node* next = node->child[ch - 'a'].get();
                    if (next == nullptr) return;
                    if (!next->word.empty()) {
                        ans.push_back(next->word);
                        next->word.clear();
                    }
                    board[r][c] = '#';
                    dfs(board, r + 1, c, next);
                    dfs(board, r - 1, c, next);
                    dfs(board, r, c + 1, next);
                    dfs(board, r, c - 1, next);
                    board[r][c] = ch;
                }

               public:
                vector<string> findWords(vector<vector<char>>& board, vector<string>& words) {
                    if (board.empty() || board[0].empty() || words.empty()) {
                        return {};
                    }
                    root = make_unique<Node>();
                    ans.clear();
                    for (const string& word : words) {
                        if (!word.empty()) {
                            insert(word);
                        }
                    }
                    for (int i = 0; i < static_cast<int>(board.size()); ++i) {
                        for (int j = 0; j < static_cast<int>(board[0].size()); ++j) {
                            dfs(board, i, j, root.get());
                        }
                    }
                    return ans;
                }
            };
            """
        )
    ],
    "10-segment-tree-n-trie-24-maximum-xor-pair": [
        cpp(
            r"""
            class BinaryTrie {
                struct Node {
                    array<unique_ptr<Node>, 2> child{};
                };

                unique_ptr<Node> root = make_unique<Node>();

               public:
                void insert(uint32_t num) {
                    Node* node = root.get();
                    for (int bit = 31; bit >= 0; --bit) {
                        int value = (num >> bit) & 1U;
                        if (!node->child[value]) {
                            node->child[value] = make_unique<Node>();
                        }
                        node = node->child[value].get();
                    }
                }

                uint32_t bestXor(uint32_t num) const {
                    const Node* node = root.get();
                    uint32_t ans = 0;
                    for (int bit = 31; bit >= 0; --bit) {
                        int value = (num >> bit) & 1U;
                        int want = value ^ 1;
                        if (node->child[want]) {
                            ans |= (1U << bit);
                            node = node->child[want].get();
                        } else if (node->child[value]) {
                            node = node->child[value].get();
                        } else {
                            break;
                        }
                    }
                    return ans;
                }
            };

            int maximumXorPair(const vector<int>& nums) {
                if (nums.size() < 2) {
                    return 0;
                }
                BinaryTrie trie;
                trie.insert(static_cast<uint32_t>(nums[0]));
                uint32_t ans = 0;
                for (size_t i = 1; i < nums.size(); ++i) {
                    uint32_t value = static_cast<uint32_t>(nums[i]);
                    ans = max(ans, trie.bestXor(value));
                    trie.insert(value);
                }
                return static_cast<int>(ans);
            }
            """
        )
    ],
    "10-segment-tree-n-trie-25-maximum-xor-subarray": [
        cpp(
            r"""
            class BinaryTrie {
                struct Node {
                    array<unique_ptr<Node>, 2> child{};
                };

                unique_ptr<Node> root = make_unique<Node>();

               public:
                void insert(uint32_t num) {
                    Node* node = root.get();
                    for (int bit = 31; bit >= 0; --bit) {
                        int value = (num >> bit) & 1U;
                        if (!node->child[value]) {
                            node->child[value] = make_unique<Node>();
                        }
                        node = node->child[value].get();
                    }
                }

                uint32_t bestXor(uint32_t num) const {
                    const Node* node = root.get();
                    uint32_t ans = 0;
                    for (int bit = 31; bit >= 0; --bit) {
                        int value = (num >> bit) & 1U;
                        int want = value ^ 1;
                        if (node->child[want]) {
                            ans |= (1U << bit);
                            node = node->child[want].get();
                        } else if (node->child[value]) {
                            node = node->child[value].get();
                        } else {
                            break;
                        }
                    }
                    return ans;
                }
            };

            int maxXorSubarray(const vector<int>& arr) {
                BinaryTrie trie;
                trie.insert(0);
                uint32_t prefix = 0;
                uint32_t ans = 0;
                for (int x : arr) {
                    prefix ^= static_cast<uint32_t>(x);
                    ans = max(ans, trie.bestXor(prefix));
                    trie.insert(prefix);
                }
                return static_cast<int>(ans);
            }
            """
        )
    ],
    "10-segment-tree-n-trie-26-aho-corasick-algorithm": [
        cpp(
            r"""
            class AhoCorasick {
                struct Node {
                    array<int, 26> next;
                    int fail = 0;
                    vector<int> output;

                    Node() {
                        next.fill(-1);
                    }
                };

                vector<Node> trie{1};
                vector<int> patternLength;

               public:
                void insert(const string& pattern, int id) {
                    if (id >= static_cast<int>(patternLength.size())) {
                        patternLength.resize(id + 1);
                    }
                    patternLength[id] = static_cast<int>(pattern.size());
                    int node = 0;
                    for (char c : pattern) {
                        int x = c - 'a';
                        if (trie[node].next[x] == -1) {
                            trie[node].next[x] = static_cast<int>(trie.size());
                            trie.push_back(Node());
                        }
                        node = trie[node].next[x];
                    }
                    trie[node].output.push_back(id);
                }

                void build() {
                    queue<int> q;
                    for (int c = 0; c < 26; ++c) {
                        int v = trie[0].next[c];
                        if (v == -1) {
                            trie[0].next[c] = 0;
                        } else {
                            trie[v].fail = 0;
                            q.push(v);
                        }
                    }
                    while (!q.empty()) {
                        int u = q.front();
                        q.pop();
                        for (int c = 0; c < 26; ++c) {
                            int v = trie[u].next[c];
                            if (v == -1) {
                                trie[u].next[c] = trie[trie[u].fail].next[c];
                                continue;
                            }
                            trie[v].fail = trie[trie[u].fail].next[c];
                            const vector<int>& fallback = trie[trie[v].fail].output;
                            trie[v].output.insert(trie[v].output.end(), fallback.begin(), fallback.end());
                            q.push(v);
                        }
                    }
                }

                vector<pair<int, int>> search(const string& text) const {
                    vector<pair<int, int>> matches;
                    int node = 0;
                    for (int i = 0; i < static_cast<int>(text.size()); ++i) {
                        int x = text[i] - 'a';
                        if (x < 0 || x >= 26) {
                            node = 0;
                            continue;
                        }
                        node = trie[node].next[x];
                        for (int id : trie[node].output) {
                            matches.push_back({i - patternLength[id] + 1, id});
                        }
                    }
                    return matches;
                }
            };
            """
        )
    ],
    "10-segment-tree-n-trie-28-k-th-lexicographical-word": [
        cpp(
            r"""
            struct TrieNode {
                array<unique_ptr<TrieNode>, 26> child{};
                int wordCount = 0;
                int subtreeWords = 0;
            };

            void insert(TrieNode& root, const string& word) {
                TrieNode* node = &root;
                node->subtreeWords++;
                for (char c : word) {
                    int x = c - 'a';
                    if (!node->child[x]) {
                        node->child[x] = make_unique<TrieNode>();
                    }
                    node = node->child[x].get();
                    node->subtreeWords++;
                }
                node->wordCount++;
            }

            string kthWord(const TrieNode& root, int k) {
                if (k <= 0 || k > root.subtreeWords) {
                    return "";
                }
                string ans;
                const TrieNode* node = &root;
                while (node != nullptr) {
                    if (node->wordCount > 0) {
                        if (k <= node->wordCount) {
                            return ans;
                        }
                        k -= node->wordCount;
                    }
                    bool moved = false;
                    for (int c = 0; c < 26; ++c) {
                        const auto& next = node->child[c];
                        if (!next) continue;
                        if (k > next->subtreeWords) {
                            k -= next->subtreeWords;
                        } else {
                            ans.push_back(static_cast<char>('a' + c));
                            node = next.get();
                            moved = true;
                            break;
                        }
                    }
                    if (!moved) {
                        break;
                    }
                }
                return "";
            }
            """
        )
    ],
    "10-segment-tree-n-trie-29-persistent-binary-trie": [
        cpp(
            r"""
            class PersistentBinaryTrie {
                struct Node {
                    int child[2] = {0, 0};
                    int count = 0;
                };

                vector<Node> trie{{}};

                int insertImpl(int oldRoot, int bitPos, uint32_t num) {
                    int cur = static_cast<int>(trie.size());
                    trie.push_back(trie[oldRoot]);
                    trie[cur].count++;
                    if (bitPos < 0) {
                        return cur;
                    }
                    int bit = (num >> bitPos) & 1U;
                    trie[cur].child[bit] = insertImpl(trie[oldRoot].child[bit], bitPos - 1, num);
                    return cur;
                }

               public:
                int insert(int previousRoot, int num) {
                    return insertImpl(previousRoot, 31, static_cast<uint32_t>(num));
                }

                int maxXor(int leftRoot, int rightRoot, int num) const {
                    uint32_t value = static_cast<uint32_t>(num);
                    uint32_t ans = 0;
                    for (int bit = 31; bit >= 0; --bit) {
                        int want = ((value >> bit) & 1U) ^ 1U;
                        int leftChild = trie[leftRoot].child[want];
                        int rightChild = trie[rightRoot].child[want];
                        if (trie[rightChild].count - trie[leftChild].count > 0) {
                            ans |= (1U << bit);
                            leftRoot = leftChild;
                            rightRoot = rightChild;
                        } else {
                            int same = (value >> bit) & 1U;
                            leftRoot = trie[leftRoot].child[same];
                            rightRoot = trie[rightRoot].child[same];
                        }
                    }
                    return static_cast<int>(ans);
                }
            };
            """
        )
    ],
    "18-fenwick-tree-binary-index-tree-4-find-k-th-smallest-k-th-prefix-position": [
        cpp(
            r"""
            long long prefixSum(const vector<long long>& bit, int idx) {
                idx = min(idx, static_cast<int>(bit.size()) - 1);
                long long sum = 0;
                while (idx > 0) {
                    sum += bit[idx];
                    idx -= idx & -idx;
                }
                return sum;
            }

            int kthSmallest(const vector<long long>& bit, int n, long long k) {
                if (n <= 0 || k <= 0 || k > prefixSum(bit, n)) {
                    return -1;
                }
                int idx = 0;
                int pw = 1;
                while ((pw << 1) <= n) pw <<= 1;
                for (int step = pw; step > 0; step >>= 1) {
                    int next = idx + step;
                    if (next <= n && bit[next] < k) {
                        idx = next;
                        k -= bit[next];
                    }
                }
                return idx + 1;
            }
            """
        )
    ],
    "18-fenwick-tree-binary-index-tree-10-dynamic-order-statistics-with-fenwick-tree": [
        cpp(
            r"""
            class OrderStatistic {
                int n;
                vector<int> bit;
                vector<int> freq;

                void add(int idx, int delta) {
                    while (idx <= n) {
                        bit[idx] += delta;
                        idx += idx & -idx;
                    }
                }

                int prefix(int idx) const {
                    idx = max(0, min(idx, n));
                    int sum = 0;
                    while (idx > 0) {
                        sum += bit[idx];
                        idx -= idx & -idx;
                    }
                    return sum;
                }

               public:
                explicit OrderStatistic(int n) : n(n), bit(n + 1, 0), freq(n + 1, 0) {}

                void insert(int x) {
                    if (x < 1 || x > n) return;
                    ++freq[x];
                    add(x, 1);
                }

                bool erase(int x) {
                    if (x < 1 || x > n || freq[x] == 0) {
                        return false;
                    }
                    --freq[x];
                    add(x, -1);
                    return true;
                }

                int countLessEqual(int x) const {
                    return prefix(x);
                }

                int kth(int k) const {
                    int total = prefix(n);
                    if (k <= 0 || k > total) {
                        return -1;
                    }
                    int idx = 0;
                    int step = 1;
                    while ((step << 1) <= n) step <<= 1;
                    for (; step > 0; step >>= 1) {
                        int next = idx + step;
                        if (next <= n && bit[next] < k) {
                            idx = next;
                            k -= bit[next];
                        }
                    }
                    return idx + 1;
                }
            };
            """
        )
    ],
    "18-fenwick-tree-binary-index-tree-11-count-number-of-smaller-elements-on-both-sides": [
        cpp(
            r"""
            struct SmallerCounts {
                vector<int> left;
                vector<int> right;
            };

            SmallerCounts countSmallerOnBothSides(const vector<int>& arr) {
                int n = static_cast<int>(arr.size());
                vector<int> vals = arr;
                sort(vals.begin(), vals.end());
                vals.erase(unique(vals.begin(), vals.end()), vals.end());
                int m = static_cast<int>(vals.size());
                vector<int> bit(m + 1, 0);

                auto update = [&](int idx) {
                    while (idx <= m) {
                        bit[idx]++;
                        idx += idx & -idx;
                    }
                };
                auto query = [&](int idx) {
                    int sum = 0;
                    while (idx > 0) {
                        sum += bit[idx];
                        idx -= idx & -idx;
                    }
                    return sum;
                };

                vector<int> left(n), right(n);
                for (int i = 0; i < n; ++i) {
                    int rank = static_cast<int>(lower_bound(vals.begin(), vals.end(), arr[i]) - vals.begin()) + 1;
                    left[i] = query(rank - 1);
                    update(rank);
                }

                fill(bit.begin(), bit.end(), 0);
                for (int i = n - 1; i >= 0; --i) {
                    int rank = static_cast<int>(lower_bound(vals.begin(), vals.end(), arr[i]) - vals.begin()) + 1;
                    right[i] = query(rank - 1);
                    update(rank);
                }

                return {left, right};
            }
            """
        )
    ],
    "18-fenwick-tree-binary-index-tree-12-count-increasing-subsequences-of-length-k": [
        cpp(
            r"""
            class Fenwick {
                vector<long long> bit;

               public:
                explicit Fenwick(int n) : bit(n + 1, 0) {}

                void update(int idx, long long delta) {
                    while (idx < static_cast<int>(bit.size())) {
                        bit[idx] += delta;
                        idx += idx & -idx;
                    }
                }

                long long query(int idx) const {
                    long long sum = 0;
                    while (idx > 0) {
                        sum += bit[idx];
                        idx -= idx & -idx;
                    }
                    return sum;
                }
            };
            """
        ),
        cpp(
            r"""
            long long countIncreasing(const vector<int>& arr, int K) {
                if (K <= 0 || arr.empty()) {
                    return 0;
                }
                vector<int> vals = arr;
                sort(vals.begin(), vals.end());
                vals.erase(unique(vals.begin(), vals.end()), vals.end());
                int m = static_cast<int>(vals.size());

                vector<Fenwick> bits;
                bits.reserve(K + 1);
                bits.emplace_back(0);
                for (int len = 1; len <= K; ++len) {
                    bits.emplace_back(m);
                }

                for (int x : arr) {
                    int rank = static_cast<int>(lower_bound(vals.begin(), vals.end(), x) - vals.begin()) + 1;
                    for (int len = K; len >= 2; --len) {
                        long long ways = bits[len - 1].query(rank - 1);
                        bits[len].update(rank, ways);
                    }
                    bits[1].update(rank, 1);
                }
                return bits[K].query(m);
            }
            """
        ),
    ],
    "18-fenwick-tree-binary-index-tree-13-count-number-of-inversions-in-every-prefix": [
        cpp(
            r"""
            class Fenwick {
                vector<long long> bit;

               public:
                explicit Fenwick(int n) : bit(n + 1, 0) {}

                void update(int idx, long long delta) {
                    while (idx < static_cast<int>(bit.size())) {
                        bit[idx] += delta;
                        idx += idx & -idx;
                    }
                }

                long long query(int idx) const {
                    long long sum = 0;
                    while (idx > 0) {
                        sum += bit[idx];
                        idx -= idx & -idx;
                    }
                    return sum;
                }
            };
            """
        ),
        cpp(
            r"""
            vector<long long> prefixInversions(const vector<int>& arr) {
                int n = static_cast<int>(arr.size());
                vector<int> vals = arr;
                sort(vals.begin(), vals.end());
                vals.erase(unique(vals.begin(), vals.end()), vals.end());
                int m = static_cast<int>(vals.size());

                Fenwick bit(m);
                vector<long long> ans;
                ans.reserve(n);
                long long inversions = 0;
                for (int i = 0; i < n; ++i) {
                    int rank = static_cast<int>(lower_bound(vals.begin(), vals.end(), arr[i]) - vals.begin()) + 1;
                    long long smallerOrEqual = bit.query(rank);
                    inversions += i - smallerOrEqual;
                    ans.push_back(inversions);
                    bit.update(rank, 1);
                }
                return ans;
            }
            """
        ),
    ],
}

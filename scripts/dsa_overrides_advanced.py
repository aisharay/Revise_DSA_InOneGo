"""Canonical C++17 overrides for materially broken advanced DSA sections."""

from __future__ import annotations

from textwrap import dedent


def cpp(source: str) -> str:
    return dedent(source).strip()


BUILD_SUFFIX_ARRAY = cpp(
    r"""
    vector<int> buildSuffixArray(const string& s) {
        int n = static_cast<int>(s.size());
        if (n == 0) return {};
        vector<int> sa(n), rank(n), nextRank(n);
        iota(sa.begin(), sa.end(), 0);
        for (int i = 0; i < n; ++i) {
            rank[i] = static_cast<unsigned char>(s[i]);
        }
        for (int k = 1;; k <<= 1) {
            auto cmp = [&](int a, int b) {
                if (rank[a] != rank[b]) return rank[a] < rank[b];
                int ra = (a + k < n) ? rank[a + k] : -1;
                int rb = (b + k < n) ? rank[b + k] : -1;
                return ra < rb;
            };
            sort(sa.begin(), sa.end(), cmp);
            nextRank[sa[0]] = 0;
            for (int i = 1; i < n; ++i) {
                nextRank[sa[i]] = nextRank[sa[i - 1]] + (cmp(sa[i - 1], sa[i]) ? 1 : 0);
            }
            rank.swap(nextRank);
            if (rank[sa.back()] == n - 1) break;
        }
        return sa;
    }
    """
)


BUILD_LCP = cpp(
    r"""
    vector<int> buildLCP(const string& s, const vector<int>& sa) {
        int n = static_cast<int>(s.size());
        if (n <= 1) return {};
        vector<int> rank(n), lcp(n - 1);
        for (int i = 0; i < n; ++i) {
            rank[sa[i]] = i;
        }
        int k = 0;
        for (int i = 0; i < n; ++i) {
            int pos = rank[i];
            if (pos == n - 1) {
                k = 0;
                continue;
            }
            int j = sa[pos + 1];
            while (i + k < n && j + k < n && s[i + k] == s[j + k]) {
                ++k;
            }
            lcp[pos] = k;
            if (k) --k;
        }
        return lcp;
    }
    """
)


SUFFIX_AUTOMATON = cpp(
    r"""
    struct SuffixAutomaton {
        struct State {
            array<int, 26> next;
            int link = -1;
            int len = 0;
            long long occ = 0;

            State() { next.fill(-1); }
        };

        vector<State> st;
        int last = 0;

        SuffixAutomaton() : st(1) {}

        void reset() {
            st.assign(1, State());
            last = 0;
        }

        void extend(char ch) {
            int c = ch - 'a';
            int cur = static_cast<int>(st.size());
            st.push_back(State());
            st[cur].len = st[last].len + 1;
            st[cur].occ = 1;

            int p = last;
            while (p != -1 && st[p].next[c] == -1) {
                st[p].next[c] = cur;
                p = st[p].link;
            }
            if (p == -1) {
                st[cur].link = 0;
            } else {
                int q = st[p].next[c];
                if (st[p].len + 1 == st[q].len) {
                    st[cur].link = q;
                } else {
                    int clone = static_cast<int>(st.size());
                    st.push_back(st[q]);
                    st[clone].len = st[p].len + 1;
                    st[clone].occ = 0;
                    while (p != -1 && st[p].next[c] == q) {
                        st[p].next[c] = clone;
                        p = st[p].link;
                    }
                    st[q].link = st[cur].link = clone;
                }
            }
            last = cur;
        }

        void build(const string& s) {
            reset();
            for (char ch : s) extend(ch);
        }

        bool contains(const string& pattern) const {
            int v = 0;
            for (char ch : pattern) {
                int c = ch - 'a';
                if (c < 0 || c >= 26 || st[v].next[c] == -1) return false;
                v = st[v].next[c];
            }
            return true;
        }

        void propagateOccurrences() {
            vector<int> order(st.size());
            iota(order.begin(), order.end(), 0);
            sort(order.begin(), order.end(), [&](int a, int b) {
                return st[a].len < st[b].len;
            });
            for (int i = static_cast<int>(order.size()) - 1; i > 0; --i) {
                int v = order[i];
                st[st[v].link].occ += st[v].occ;
            }
        }
    };
    """
)


EERTREE = cpp(
    r"""
    struct Eertree {
        struct Node {
            array<int, 26> next;
            int len;
            int link;
            int occ;
            int firstEnd;

            explicit Node(int length = 0)
                : len(length), link(0), occ(0), firstEnd(-1) {
                next.fill(0);
            }
        };

        vector<Node> tree;
        string s;
        int suff = 1;
        int bestNode = 1;

        Eertree() { reset(); }

        void reset() {
            tree.clear();
            tree.push_back(Node(-1));
            tree.push_back(Node(0));
            tree[0].link = 0;
            tree[1].link = 0;
            s.clear();
            suff = 1;
            bestNode = 1;
        }

        int getLink(int v, int pos) const {
            while (true) {
                int left = pos - 1 - tree[v].len;
                if (left >= 0 && s[left] == s[pos]) return v;
                v = tree[v].link;
            }
        }

        int addChar(char ch) {
            s.push_back(ch);
            int pos = static_cast<int>(s.size()) - 1;
            int cur = getLink(suff, pos);
            int c = ch - 'a';

            if (!tree[cur].next[c]) {
                int node = static_cast<int>(tree.size());
                tree.push_back(Node(tree[cur].len + 2));
                tree[node].firstEnd = pos;
                if (tree[node].len == 1) {
                    tree[node].link = 1;
                } else {
                    int linkNode = getLink(tree[cur].link, pos);
                    tree[node].link = tree[linkNode].next[c];
                }
                tree[cur].next[c] = node;
            }

            suff = tree[cur].next[c];
            tree[suff].occ++;
            if (tree[suff].len > tree[bestNode].len) bestNode = suff;
            return tree[bestNode].len;
        }

        void build(const string& text) {
            reset();
            for (char ch : text) addChar(ch);
        }

        int distinctCount() const {
            return max(0, static_cast<int>(tree.size()) - 2);
        }

        string longestPalindrome() const {
            if (bestNode <= 1) return "";
            const Node& node = tree[bestNode];
            return s.substr(node.firstEnd - node.len + 1, node.len);
        }
    };
    """
)


RANGE_ASSIGN_SUM_SEGMENT_TREE = cpp(
    r"""
    class RangeAssignSumSegmentTree {
        int n;
        vector<long long> tree, lazy;
        vector<char> hasLazy;

        void build(int node, int l, int r, const vector<long long>& arr) {
            if (l == r) {
                tree[node] = arr[l];
                return;
            }
            int mid = l + (r - l) / 2;
            build(node * 2, l, mid, arr);
            build(node * 2 + 1, mid + 1, r, arr);
            tree[node] = tree[node * 2] + tree[node * 2 + 1];
        }

        void apply(int node, int l, int r, long long value) {
            tree[node] = (r - l + 1LL) * value;
            lazy[node] = value;
            hasLazy[node] = 1;
        }

        void push(int node, int l, int r) {
            if (!hasLazy[node] || l == r) return;
            int mid = l + (r - l) / 2;
            apply(node * 2, l, mid, lazy[node]);
            apply(node * 2 + 1, mid + 1, r, lazy[node]);
            hasLazy[node] = 0;
        }

        void update(int node, int l, int r, int ql, int qr, long long value) {
            if (qr < l || r < ql) return;
            if (ql <= l && r <= qr) {
                apply(node, l, r, value);
                return;
            }
            push(node, l, r);
            int mid = l + (r - l) / 2;
            update(node * 2, l, mid, ql, qr, value);
            update(node * 2 + 1, mid + 1, r, ql, qr, value);
            tree[node] = tree[node * 2] + tree[node * 2 + 1];
        }

        long long query(int node, int l, int r, int ql, int qr) {
            if (qr < l || r < ql) return 0;
            if (ql <= l && r <= qr) return tree[node];
            push(node, l, r);
            int mid = l + (r - l) / 2;
            return query(node * 2, l, mid, ql, qr) +
                   query(node * 2 + 1, mid + 1, r, ql, qr);
        }

    public:
        explicit RangeAssignSumSegmentTree(const vector<long long>& arr)
            : n(static_cast<int>(arr.size())),
              tree(max(1, 4 * n)),
              lazy(max(1, 4 * n)),
              hasLazy(max(1, 4 * n), 0) {
            if (n) build(1, 0, n - 1, arr);
        }

        void assignRange(int l, int r, long long value) {
            if (!n) return;
            l = max(l, 0);
            r = min(r, n - 1);
            if (l > r) return;
            update(1, 0, n - 1, l, r, value);
        }

        long long querySum(int l, int r) {
            if (!n) return 0;
            l = max(l, 0);
            r = min(r, n - 1);
            if (l > r) return 0;
            return query(1, 0, n - 1, l, r);
        }
    };
    """
)


RANGE_ADD_MIN_SEGMENT_TREE = cpp(
    r"""
    class RangeAddMinSegmentTree {
        int n;
        vector<long long> tree, lazy;

        void build(int node, int l, int r, const vector<long long>& arr) {
            if (l == r) {
                tree[node] = arr[l];
                return;
            }
            int mid = l + (r - l) / 2;
            build(node * 2, l, mid, arr);
            build(node * 2 + 1, mid + 1, r, arr);
            tree[node] = min(tree[node * 2], tree[node * 2 + 1]);
        }

        void apply(int node, long long value) {
            tree[node] += value;
            lazy[node] += value;
        }

        void push(int node) {
            if (lazy[node] == 0) return;
            apply(node * 2, lazy[node]);
            apply(node * 2 + 1, lazy[node]);
            lazy[node] = 0;
        }

        void update(int node, int l, int r, int ql, int qr, long long value) {
            if (qr < l || r < ql) return;
            if (ql <= l && r <= qr) {
                apply(node, value);
                return;
            }
            push(node);
            int mid = l + (r - l) / 2;
            update(node * 2, l, mid, ql, qr, value);
            update(node * 2 + 1, mid + 1, r, ql, qr, value);
            tree[node] = min(tree[node * 2], tree[node * 2 + 1]);
        }

        long long query(int node, int l, int r, int ql, int qr) {
            if (qr < l || r < ql) return LLONG_MAX;
            if (ql <= l && r <= qr) return tree[node];
            push(node);
            int mid = l + (r - l) / 2;
            return min(query(node * 2, l, mid, ql, qr),
                       query(node * 2 + 1, mid + 1, r, ql, qr));
        }

    public:
        explicit RangeAddMinSegmentTree(const vector<long long>& arr)
            : n(static_cast<int>(arr.size())),
              tree(max(1, 4 * n)),
              lazy(max(1, 4 * n), 0) {
            if (n) build(1, 0, n - 1, arr);
        }

        void addRange(int l, int r, long long value) {
            if (!n) return;
            l = max(l, 0);
            r = min(r, n - 1);
            if (l > r) return;
            update(1, 0, n - 1, l, r, value);
        }

        long long rangeMin(int l, int r) {
            if (!n) return 0;
            l = max(l, 0);
            r = min(r, n - 1);
            if (l > r) return 0;
            return query(1, 0, n - 1, l, r);
        }
    };
    """
)


RANGE_ADD_MUL_SUM_SEGMENT_TREE = cpp(
    r"""
    class RangeAddMulSumSegmentTree {
        int n;
        vector<long long> tree, lazyMul, lazyAdd;

        void build(int node, int l, int r, const vector<long long>& arr) {
            if (l == r) {
                tree[node] = arr[l];
                return;
            }
            int mid = l + (r - l) / 2;
            build(node * 2, l, mid, arr);
            build(node * 2 + 1, mid + 1, r, arr);
            tree[node] = tree[node * 2] + tree[node * 2 + 1];
        }

        void apply(int node, int l, int r, long long mul, long long add) {
            tree[node] = tree[node] * mul + (r - l + 1LL) * add;
            lazyMul[node] *= mul;
            lazyAdd[node] = lazyAdd[node] * mul + add;
        }

        void push(int node, int l, int r) {
            if (l == r) return;
            if (lazyMul[node] == 1 && lazyAdd[node] == 0) return;
            int mid = l + (r - l) / 2;
            apply(node * 2, l, mid, lazyMul[node], lazyAdd[node]);
            apply(node * 2 + 1, mid + 1, r, lazyMul[node], lazyAdd[node]);
            lazyMul[node] = 1;
            lazyAdd[node] = 0;
        }

        void update(int node, int l, int r, int ql, int qr, long long mul, long long add) {
            if (qr < l || r < ql) return;
            if (ql <= l && r <= qr) {
                apply(node, l, r, mul, add);
                return;
            }
            push(node, l, r);
            int mid = l + (r - l) / 2;
            update(node * 2, l, mid, ql, qr, mul, add);
            update(node * 2 + 1, mid + 1, r, ql, qr, mul, add);
            tree[node] = tree[node * 2] + tree[node * 2 + 1];
        }

        long long query(int node, int l, int r, int ql, int qr) {
            if (qr < l || r < ql) return 0;
            if (ql <= l && r <= qr) return tree[node];
            push(node, l, r);
            int mid = l + (r - l) / 2;
            return query(node * 2, l, mid, ql, qr) +
                   query(node * 2 + 1, mid + 1, r, ql, qr);
        }

    public:
        explicit RangeAddMulSumSegmentTree(const vector<long long>& arr)
            : n(static_cast<int>(arr.size())),
              tree(max(1, 4 * n)),
              lazyMul(max(1, 4 * n), 1),
              lazyAdd(max(1, 4 * n), 0) {
            if (n) build(1, 0, n - 1, arr);
        }

        void multiplyRange(int l, int r, long long value) {
            if (!n) return;
            l = max(l, 0);
            r = min(r, n - 1);
            if (l > r) return;
            update(1, 0, n - 1, l, r, value, 0);
        }

        void addRange(int l, int r, long long value) {
            if (!n) return;
            l = max(l, 0);
            r = min(r, n - 1);
            if (l > r) return;
            update(1, 0, n - 1, l, r, 1, value);
        }

        long long querySum(int l, int r) {
            if (!n) return 0;
            l = max(l, 0);
            r = min(r, n - 1);
            if (l > r) return 0;
            return query(1, 0, n - 1, l, r);
        }
    };
    """
)


SEGMENT_TREE_BEATS = cpp(
    r"""
    static constexpr long long BEATS_INF = (1LL << 60);

    class SegmentTreeBeats {
        struct Node {
            long long sum = 0;
            long long mx1 = -BEATS_INF;
            long long mx2 = -BEATS_INF;
            int mxCount = 0;
            long long mn1 = BEATS_INF;
            long long mn2 = BEATS_INF;
            int mnCount = 0;
        };

        int n;
        vector<Node> tree;

        Node merge(const Node& a, const Node& b) const {
            Node res;
            res.sum = a.sum + b.sum;

            res.mx1 = max(a.mx1, b.mx1);
            res.mx2 = -BEATS_INF;
            res.mxCount = 0;
            if (a.mx1 == res.mx1) {
                res.mxCount += a.mxCount;
                res.mx2 = max(res.mx2, a.mx2);
            } else {
                res.mx2 = max(res.mx2, a.mx1);
            }
            if (b.mx1 == res.mx1) {
                res.mxCount += b.mxCount;
                res.mx2 = max(res.mx2, b.mx2);
            } else {
                res.mx2 = max(res.mx2, b.mx1);
            }

            res.mn1 = min(a.mn1, b.mn1);
            res.mn2 = BEATS_INF;
            res.mnCount = 0;
            if (a.mn1 == res.mn1) {
                res.mnCount += a.mnCount;
                res.mn2 = min(res.mn2, a.mn2);
            } else {
                res.mn2 = min(res.mn2, a.mn1);
            }
            if (b.mn1 == res.mn1) {
                res.mnCount += b.mnCount;
                res.mn2 = min(res.mn2, b.mn2);
            } else {
                res.mn2 = min(res.mn2, b.mn1);
            }

            return res;
        }

        void build(int node, int l, int r, const vector<long long>& arr) {
            if (l == r) {
                long long value = arr[l];
                tree[node].sum = value;
                tree[node].mx1 = tree[node].mn1 = value;
                tree[node].mx2 = -BEATS_INF;
                tree[node].mn2 = BEATS_INF;
                tree[node].mxCount = tree[node].mnCount = 1;
                return;
            }
            int mid = l + (r - l) / 2;
            build(node * 2, l, mid, arr);
            build(node * 2 + 1, mid + 1, r, arr);
            tree[node] = merge(tree[node * 2], tree[node * 2 + 1]);
        }

        void applyChmin(int node, long long x) {
            if (tree[node].mx1 <= x) return;
            tree[node].sum += (x - tree[node].mx1) * tree[node].mxCount;
            if (tree[node].mn1 == tree[node].mx1) {
                tree[node].mn1 = x;
            } else if (tree[node].mn2 == tree[node].mx1) {
                tree[node].mn2 = x;
            }
            tree[node].mx1 = x;
        }

        void applyChmax(int node, long long x) {
            if (tree[node].mn1 >= x) return;
            tree[node].sum += (x - tree[node].mn1) * tree[node].mnCount;
            if (tree[node].mx1 == tree[node].mn1) {
                tree[node].mx1 = x;
            } else if (tree[node].mx2 == tree[node].mn1) {
                tree[node].mx2 = x;
            }
            tree[node].mn1 = x;
        }

        void push(int node) {
            for (int child : {node * 2, node * 2 + 1}) {
                if (tree[child].mx1 > tree[node].mx1) applyChmin(child, tree[node].mx1);
                if (tree[child].mn1 < tree[node].mn1) applyChmax(child, tree[node].mn1);
            }
        }

        void rangeChmin(int node, int l, int r, int ql, int qr, long long x) {
            if (qr < l || r < ql || tree[node].mx1 <= x) return;
            if (ql <= l && r <= qr && tree[node].mx2 < x) {
                applyChmin(node, x);
                return;
            }
            int mid = l + (r - l) / 2;
            push(node);
            rangeChmin(node * 2, l, mid, ql, qr, x);
            rangeChmin(node * 2 + 1, mid + 1, r, ql, qr, x);
            tree[node] = merge(tree[node * 2], tree[node * 2 + 1]);
        }

        void rangeChmax(int node, int l, int r, int ql, int qr, long long x) {
            if (qr < l || r < ql || tree[node].mn1 >= x) return;
            if (ql <= l && r <= qr && tree[node].mn2 > x) {
                applyChmax(node, x);
                return;
            }
            int mid = l + (r - l) / 2;
            push(node);
            rangeChmax(node * 2, l, mid, ql, qr, x);
            rangeChmax(node * 2 + 1, mid + 1, r, ql, qr, x);
            tree[node] = merge(tree[node * 2], tree[node * 2 + 1]);
        }

        long long querySum(int node, int l, int r, int ql, int qr) {
            if (qr < l || r < ql) return 0;
            if (ql <= l && r <= qr) return tree[node].sum;
            int mid = l + (r - l) / 2;
            push(node);
            return querySum(node * 2, l, mid, ql, qr) +
                   querySum(node * 2 + 1, mid + 1, r, ql, qr);
        }

        long long queryMin(int node, int l, int r, int ql, int qr) {
            if (qr < l || r < ql) return BEATS_INF;
            if (ql <= l && r <= qr) return tree[node].mn1;
            int mid = l + (r - l) / 2;
            push(node);
            return min(queryMin(node * 2, l, mid, ql, qr),
                       queryMin(node * 2 + 1, mid + 1, r, ql, qr));
        }

        long long queryMax(int node, int l, int r, int ql, int qr) {
            if (qr < l || r < ql) return -BEATS_INF;
            if (ql <= l && r <= qr) return tree[node].mx1;
            int mid = l + (r - l) / 2;
            push(node);
            return max(queryMax(node * 2, l, mid, ql, qr),
                       queryMax(node * 2 + 1, mid + 1, r, ql, qr));
        }

    public:
        explicit SegmentTreeBeats(const vector<long long>& arr)
            : n(static_cast<int>(arr.size())), tree(max(1, 4 * n)) {
            if (n) build(1, 0, n - 1, arr);
        }

        void rangeChmin(int l, int r, long long x) {
            if (!n) return;
            l = max(l, 0);
            r = min(r, n - 1);
            if (l > r) return;
            rangeChmin(1, 0, n - 1, l, r, x);
        }

        void rangeChmax(int l, int r, long long x) {
            if (!n) return;
            l = max(l, 0);
            r = min(r, n - 1);
            if (l > r) return;
            rangeChmax(1, 0, n - 1, l, r, x);
        }

        long long rangeSum(int l, int r) {
            if (!n) return 0;
            l = max(l, 0);
            r = min(r, n - 1);
            if (l > r) return 0;
            return querySum(1, 0, n - 1, l, r);
        }

        long long rangeMin(int l, int r) {
            if (!n) return 0;
            l = max(l, 0);
            r = min(r, n - 1);
            if (l > r) return 0;
            return queryMin(1, 0, n - 1, l, r);
        }

        long long rangeMax(int l, int r) {
            if (!n) return 0;
            l = max(l, 0);
            r = min(r, n - 1);
            if (l > r) return 0;
            return queryMax(1, 0, n - 1, l, r);
        }
    };
    """
)


DYNAMIC_SEGMENT_TREE = cpp(
    r"""
    class DynamicSegmentTree {
        struct Node {
            long long sum = 0;
            unique_ptr<Node> left;
            unique_ptr<Node> right;
        };

        unique_ptr<Node> root;
        long long lo, hi;

        void add(unique_ptr<Node>& node, long long l, long long r, long long idx, long long delta) {
            if (!node) node = make_unique<Node>();
            if (l == r) {
                node->sum += delta;
                return;
            }
            long long mid = l + (r - l) / 2;
            if (idx <= mid) {
                add(node->left, l, mid, idx, delta);
            } else {
                add(node->right, mid + 1, r, idx, delta);
            }
            node->sum = 0;
            if (node->left) node->sum += node->left->sum;
            if (node->right) node->sum += node->right->sum;
        }

        long long query(const Node* node, long long l, long long r, long long ql, long long qr) const {
            if (!node || qr < l || r < ql) return 0;
            if (ql <= l && r <= qr) return node->sum;
            long long mid = l + (r - l) / 2;
            return query(node->left.get(), l, mid, ql, qr) +
                   query(node->right.get(), mid + 1, r, ql, qr);
        }

    public:
        DynamicSegmentTree(long long minCoord = 0,
                           long long maxCoord = 1'000'000'000'000'000'000LL)
            : lo(minCoord), hi(maxCoord) {}

        void add(long long idx, long long delta) {
            if (idx < lo || idx > hi) return;
            add(root, lo, hi, idx, delta);
        }

        long long rangeSum(long long l, long long r) const {
            l = max(l, lo);
            r = min(r, hi);
            if (l > r) return 0;
            return query(root.get(), lo, hi, l, r);
        }
    };
    """
)


PERSISTENT_SEGMENT_TREE = cpp(
    r"""
    class PersistentSegmentTree {
        struct Node {
            int left = 0;
            int right = 0;
            long long sum = 0;
        };

        int n;
        vector<Node> tree;

        int build(const vector<long long>& arr, int l, int r) {
            int node = static_cast<int>(tree.size());
            tree.push_back(Node());
            if (l == r) {
                tree[node].sum = arr[l];
                return node;
            }
            int mid = l + (r - l) / 2;
            tree[node].left = build(arr, l, mid);
            tree[node].right = build(arr, mid + 1, r);
            tree[node].sum = tree[tree[node].left].sum + tree[tree[node].right].sum;
            return node;
        }

        int update(int node, int l, int r, int idx, long long value) {
            int copy = static_cast<int>(tree.size());
            tree.push_back(tree[node]);
            if (l == r) {
                tree[copy].sum = value;
                return copy;
            }
            int mid = l + (r - l) / 2;
            if (idx <= mid) {
                tree[copy].left = update(tree[node].left, l, mid, idx, value);
            } else {
                tree[copy].right = update(tree[node].right, mid + 1, r, idx, value);
            }
            tree[copy].sum = tree[tree[copy].left].sum + tree[tree[copy].right].sum;
            return copy;
        }

        long long query(int node, int l, int r, int ql, int qr) const {
            if (!node || qr < l || r < ql) return 0;
            if (ql <= l && r <= qr) return tree[node].sum;
            int mid = l + (r - l) / 2;
            return query(tree[node].left, l, mid, ql, qr) +
                   query(tree[node].right, mid + 1, r, ql, qr);
        }

    public:
        vector<int> roots;

        explicit PersistentSegmentTree(const vector<long long>& arr)
            : n(static_cast<int>(arr.size())), tree(1) {
            roots.push_back(n ? build(arr, 0, n - 1) : 0);
        }

        int updateVersion(int version, int idx, long long value) {
            if (!n || version < 0 || version >= static_cast<int>(roots.size()) ||
                idx < 0 || idx >= n) {
                return version;
            }
            int newRoot = update(roots[version], 0, n - 1, idx, value);
            roots.push_back(newRoot);
            return static_cast<int>(roots.size()) - 1;
        }

        long long queryVersion(int version, int l, int r) const {
            if (!n || version < 0 || version >= static_cast<int>(roots.size())) return 0;
            l = max(l, 0);
            r = min(r, n - 1);
            if (l > r) return 0;
            return query(roots[version], 0, n - 1, l, r);
        }

        int latestVersion() const {
            return static_cast<int>(roots.size()) - 1;
        }
    };
    """
)


PERSISTENT_KTH_SMALLEST = cpp(
    r"""
    class PersistentKthSmallest {
        struct Node {
            int left = 0;
            int right = 0;
            int count = 0;
        };

        vector<Node> tree;
        vector<int> roots;
        vector<int> values;

        int update(int node, int l, int r, int idx) {
            int copy = static_cast<int>(tree.size());
            tree.push_back(tree[node]);
            tree[copy].count++;
            if (l == r) return copy;
            int mid = l + (r - l) / 2;
            if (idx <= mid) {
                tree[copy].left = update(tree[node].left, l, mid, idx);
            } else {
                tree[copy].right = update(tree[node].right, mid + 1, r, idx);
            }
            return copy;
        }

        int kth(int leftRoot, int rightRoot, int l, int r, int k) const {
            if (l == r) return l;
            int mid = l + (r - l) / 2;
            int leftCount =
                tree[tree[rightRoot].left].count - tree[tree[leftRoot].left].count;
            if (k <= leftCount) {
                return kth(tree[leftRoot].left, tree[rightRoot].left, l, mid, k);
            }
            return kth(tree[leftRoot].right, tree[rightRoot].right, mid + 1, r,
                       k - leftCount);
        }

    public:
        explicit PersistentKthSmallest(const vector<int>& arr) : tree(1) {
            values = arr;
            sort(values.begin(), values.end());
            values.erase(unique(values.begin(), values.end()), values.end());
            roots.push_back(0);
            if (values.empty()) return;
            for (int x : arr) {
                int idx = static_cast<int>(
                    lower_bound(values.begin(), values.end(), x) - values.begin());
                roots.push_back(update(roots.back(), 0,
                                       static_cast<int>(values.size()) - 1, idx));
            }
        }

        int kthSmallest(int l, int r, int k) const {
            int n = static_cast<int>(roots.size()) - 1;
            if (values.empty() || l < 0 || r < l || r >= n || k <= 0 || k > r - l + 1) {
                return -1;
            }
            int idx =
                kth(roots[l], roots[r + 1], 0, static_cast<int>(values.size()) - 1, k);
            return values[idx];
        }
    };
    """
)


MERGE_SORT_TREE = cpp(
    r"""
    class MergeSortTree {
        int n;
        vector<vector<int>> tree;

        void build(int node, int l, int r, const vector<int>& arr) {
            if (l == r) {
                tree[node] = {arr[l]};
                return;
            }
            int mid = l + (r - l) / 2;
            build(node * 2, l, mid, arr);
            build(node * 2 + 1, mid + 1, r, arr);
            tree[node].resize(tree[node * 2].size() + tree[node * 2 + 1].size());
            merge(tree[node * 2].begin(), tree[node * 2].end(),
                  tree[node * 2 + 1].begin(), tree[node * 2 + 1].end(),
                  tree[node].begin());
        }

        int query(int node, int l, int r, int ql, int qr, int k) const {
            if (qr < l || r < ql) return 0;
            if (ql <= l && r <= qr) {
                return static_cast<int>(
                    tree[node].end() - upper_bound(tree[node].begin(), tree[node].end(), k));
            }
            int mid = l + (r - l) / 2;
            return query(node * 2, l, mid, ql, qr, k) +
                   query(node * 2 + 1, mid + 1, r, ql, qr, k);
        }

    public:
        explicit MergeSortTree(const vector<int>& arr)
            : n(static_cast<int>(arr.size())), tree(max(1, 4 * n)) {
            if (n) build(1, 0, n - 1, arr);
        }

        int countGreater(int l, int r, int k) const {
            if (!n) return 0;
            l = max(l, 0);
            r = min(r, n - 1);
            if (l > r) return 0;
            return query(1, 0, n - 1, l, r, k);
        }
    };
    """
)


COORDINATE_COMPRESSION = cpp(
    r"""
    class CoordinateCompression {
        vector<long long> values;

    public:
        explicit CoordinateCompression(vector<long long> raw)
            : values(std::move(raw)) {
            sort(values.begin(), values.end());
            values.erase(unique(values.begin(), values.end()), values.end());
        }

        int size() const { return static_cast<int>(values.size()); }

        int indexOf(long long value) const {
            return static_cast<int>(
                lower_bound(values.begin(), values.end(), value) - values.begin());
        }

        int lowerBound(long long value) const {
            return static_cast<int>(
                lower_bound(values.begin(), values.end(), value) - values.begin());
        }

        int upperBound(long long value) const {
            return static_cast<int>(
                upper_bound(values.begin(), values.end(), value) - values.begin());
        }

        long long valueAt(int index) const {
            return values[index];
        }
    };
    """
)


POINT_COUNT_SEGMENT_TREE = cpp(
    r"""
    class PointCountSegmentTree {
        int n;
        vector<long long> tree;

        void add(int node, int l, int r, int idx, long long delta) {
            if (l == r) {
                tree[node] += delta;
                return;
            }
            int mid = l + (r - l) / 2;
            if (idx <= mid) {
                add(node * 2, l, mid, idx, delta);
            } else {
                add(node * 2 + 1, mid + 1, r, idx, delta);
            }
            tree[node] = tree[node * 2] + tree[node * 2 + 1];
        }

        long long query(int node, int l, int r, int ql, int qr) const {
            if (qr < l || r < ql) return 0;
            if (ql <= l && r <= qr) return tree[node];
            int mid = l + (r - l) / 2;
            return query(node * 2, l, mid, ql, qr) +
                   query(node * 2 + 1, mid + 1, r, ql, qr);
        }

    public:
        explicit PointCountSegmentTree(int size)
            : n(size), tree(max(1, 4 * size), 0) {}

        void add(int idx, long long delta) {
            if (!n || idx < 0 || idx >= n) return;
            add(1, 0, n - 1, idx, delta);
        }

        long long rangeSum(int l, int r) const {
            if (!n) return 0;
            l = max(l, 0);
            r = min(r, n - 1);
            if (l > r) return 0;
            return query(1, 0, n - 1, l, r);
        }
    };
    """
)


MAX_SUBARRAY_SEGMENT_TREE = cpp(
    r"""
    static constexpr long long MAX_SUBARRAY_NEG_INF =
        numeric_limits<long long>::lowest() / 4;

    class MaxSubarraySegmentTree {
        struct Node {
            long long sum;
            long long pref;
            long long suff;
            long long best;
        };

        int n;
        vector<Node> tree;

        Node makeNode(long long value) const {
            return {value, value, value, value};
        }

        Node neutral() const {
            return {0, MAX_SUBARRAY_NEG_INF, MAX_SUBARRAY_NEG_INF, MAX_SUBARRAY_NEG_INF};
        }

        Node merge(const Node& a, const Node& b) const {
            if (a.best == MAX_SUBARRAY_NEG_INF) return b;
            if (b.best == MAX_SUBARRAY_NEG_INF) return a;
            return {
                a.sum + b.sum,
                max(a.pref, a.sum + b.pref),
                max(b.suff, b.sum + a.suff),
                max({a.best, b.best, a.suff + b.pref}),
            };
        }

        void build(int node, int l, int r, const vector<long long>& arr) {
            if (l == r) {
                tree[node] = makeNode(arr[l]);
                return;
            }
            int mid = l + (r - l) / 2;
            build(node * 2, l, mid, arr);
            build(node * 2 + 1, mid + 1, r, arr);
            tree[node] = merge(tree[node * 2], tree[node * 2 + 1]);
        }

        void update(int node, int l, int r, int idx, long long value) {
            if (l == r) {
                tree[node] = makeNode(value);
                return;
            }
            int mid = l + (r - l) / 2;
            if (idx <= mid) {
                update(node * 2, l, mid, idx, value);
            } else {
                update(node * 2 + 1, mid + 1, r, idx, value);
            }
            tree[node] = merge(tree[node * 2], tree[node * 2 + 1]);
        }

        Node query(int node, int l, int r, int ql, int qr) const {
            if (qr < l || r < ql) return neutral();
            if (ql <= l && r <= qr) return tree[node];
            int mid = l + (r - l) / 2;
            return merge(query(node * 2, l, mid, ql, qr),
                         query(node * 2 + 1, mid + 1, r, ql, qr));
        }

    public:
        explicit MaxSubarraySegmentTree(const vector<long long>& arr)
            : n(static_cast<int>(arr.size())), tree(max(1, 4 * n)) {
            if (n) build(1, 0, n - 1, arr);
        }

        void pointUpdate(int idx, long long value) {
            if (!n || idx < 0 || idx >= n) return;
            update(1, 0, n - 1, idx, value);
        }

        long long queryMaxSubarray(int l, int r) const {
            if (!n) return 0;
            l = max(l, 0);
            r = min(r, n - 1);
            if (l > r) return 0;
            return query(1, 0, n - 1, l, r).best;
        }
    };
    """
)


GCD_SEGMENT_TREE = cpp(
    r"""
    class GcdSegmentTree {
        int n;
        vector<long long> tree;

        void build(int node, int l, int r, const vector<long long>& arr) {
            if (l == r) {
                tree[node] = arr[l];
                return;
            }
            int mid = l + (r - l) / 2;
            build(node * 2, l, mid, arr);
            build(node * 2 + 1, mid + 1, r, arr);
            tree[node] = gcd(tree[node * 2], tree[node * 2 + 1]);
        }

        void update(int node, int l, int r, int idx, long long value) {
            if (l == r) {
                tree[node] = value;
                return;
            }
            int mid = l + (r - l) / 2;
            if (idx <= mid) {
                update(node * 2, l, mid, idx, value);
            } else {
                update(node * 2 + 1, mid + 1, r, idx, value);
            }
            tree[node] = gcd(tree[node * 2], tree[node * 2 + 1]);
        }

        long long query(int node, int l, int r, int ql, int qr) const {
            if (qr < l || r < ql) return 0;
            if (ql <= l && r <= qr) return tree[node];
            int mid = l + (r - l) / 2;
            return gcd(query(node * 2, l, mid, ql, qr),
                       query(node * 2 + 1, mid + 1, r, ql, qr));
        }

    public:
        explicit GcdSegmentTree(const vector<long long>& arr)
            : n(static_cast<int>(arr.size())), tree(max(1, 4 * n), 0) {
            if (n) build(1, 0, n - 1, arr);
        }

        void pointUpdate(int idx, long long value) {
            if (!n || idx < 0 || idx >= n) return;
            update(1, 0, n - 1, idx, value);
        }

        long long rangeGcd(int l, int r) const {
            if (!n) return 0;
            l = max(l, 0);
            r = min(r, n - 1);
            if (l > r) return 0;
            return query(1, 0, n - 1, l, r);
        }
    };
    """
)


MIN_COUNT_NODE = cpp(
    r"""
    struct MinCountNode {
        int mn = INT_MAX;
        int cnt = 0;
    };

    MinCountNode mergeMinCount(const MinCountNode& a, const MinCountNode& b) {
        if (a.mn < b.mn) return a;
        if (b.mn < a.mn) return b;
        return {a.mn, a.cnt + b.cnt};
    }
    """
)


MIN_COUNT_SEGMENT_TREE = cpp(
    r"""
    class MinCountSegmentTree {
        int n;
        vector<MinCountNode> tree;

        void build(int node, int l, int r, const vector<int>& arr) {
            if (l == r) {
                tree[node] = {arr[l], 1};
                return;
            }
            int mid = l + (r - l) / 2;
            build(node * 2, l, mid, arr);
            build(node * 2 + 1, mid + 1, r, arr);
            tree[node] = mergeMinCount(tree[node * 2], tree[node * 2 + 1]);
        }

        void update(int node, int l, int r, int idx, int value) {
            if (l == r) {
                tree[node] = {value, 1};
                return;
            }
            int mid = l + (r - l) / 2;
            if (idx <= mid) {
                update(node * 2, l, mid, idx, value);
            } else {
                update(node * 2 + 1, mid + 1, r, idx, value);
            }
            tree[node] = mergeMinCount(tree[node * 2], tree[node * 2 + 1]);
        }

        MinCountNode query(int node, int l, int r, int ql, int qr) const {
            if (qr < l || r < ql) return {};
            if (ql <= l && r <= qr) return tree[node];
            int mid = l + (r - l) / 2;
            return mergeMinCount(query(node * 2, l, mid, ql, qr),
                                 query(node * 2 + 1, mid + 1, r, ql, qr));
        }

    public:
        explicit MinCountSegmentTree(const vector<int>& arr)
            : n(static_cast<int>(arr.size())),
              tree(max(1, 4 * n)) {
            if (n) build(1, 0, n - 1, arr);
        }

        void pointUpdate(int idx, int value) {
            if (!n || idx < 0 || idx >= n) return;
            update(1, 0, n - 1, idx, value);
        }

        MinCountNode rangeMinWithFrequency(int l, int r) const {
            if (!n) return {};
            l = max(l, 0);
            r = min(r, n - 1);
            if (l > r) return {};
            return query(1, 0, n - 1, l, r);
        }
    };
    """
)


RANGE_MAX_SEGMENT_TREE = cpp(
    r"""
    class RangeMaxSegmentTree {
        int n;
        vector<long long> tree;

        void build(int node, int l, int r, const vector<long long>& arr) {
            if (l == r) {
                tree[node] = arr[l];
                return;
            }
            int mid = l + (r - l) / 2;
            build(node * 2, l, mid, arr);
            build(node * 2 + 1, mid + 1, r, arr);
            tree[node] = max(tree[node * 2], tree[node * 2 + 1]);
        }

        void update(int node, int l, int r, int idx, long long value) {
            if (l == r) {
                tree[node] = value;
                return;
            }
            int mid = l + (r - l) / 2;
            if (idx <= mid) {
                update(node * 2, l, mid, idx, value);
            } else {
                update(node * 2 + 1, mid + 1, r, idx, value);
            }
            tree[node] = max(tree[node * 2], tree[node * 2 + 1]);
        }

        long long queryMax(int node, int l, int r, int ql, int qr) const {
            if (qr < l || r < ql) return LLONG_MIN;
            if (ql <= l && r <= qr) return tree[node];
            int mid = l + (r - l) / 2;
            return max(queryMax(node * 2, l, mid, ql, qr),
                       queryMax(node * 2 + 1, mid + 1, r, ql, qr));
        }

        int firstAtLeast(int node, int l, int r, int ql, int qr, long long x) const {
            if (qr < l || r < ql || tree[node] < x) return -1;
            if (l == r) return l;
            int mid = l + (r - l) / 2;
            int left = firstAtLeast(node * 2, l, mid, ql, qr, x);
            if (left != -1) return left;
            return firstAtLeast(node * 2 + 1, mid + 1, r, ql, qr, x);
        }

    public:
        explicit RangeMaxSegmentTree(const vector<long long>& arr)
            : n(static_cast<int>(arr.size())), tree(max(1, 4 * n), LLONG_MIN) {
            if (n) build(1, 0, n - 1, arr);
        }

        void pointUpdate(int idx, long long value) {
            if (!n || idx < 0 || idx >= n) return;
            update(1, 0, n - 1, idx, value);
        }

        long long rangeMax(int l, int r) const {
            if (!n) return 0;
            l = max(l, 0);
            r = min(r, n - 1);
            if (l > r) return 0;
            return queryMax(1, 0, n - 1, l, r);
        }

        int firstAtLeast(int l, int r, long long x) const {
            if (!n) return -1;
            l = max(l, 0);
            r = min(r, n - 1);
            if (l > r) return -1;
            return firstAtLeast(1, 0, n - 1, l, r, x);
        }
    };
    """
)


KTH_ONE_SEGMENT_TREE = cpp(
    r"""
    class KthOneSegmentTree {
        int n;
        vector<int> tree;

        void build(int node, int l, int r, const vector<int>& arr) {
            if (l == r) {
                tree[node] = arr[l];
                return;
            }
            int mid = l + (r - l) / 2;
            build(node * 2, l, mid, arr);
            build(node * 2 + 1, mid + 1, r, arr);
            tree[node] = tree[node * 2] + tree[node * 2 + 1];
        }

        void update(int node, int l, int r, int idx, int value) {
            if (l == r) {
                tree[node] = value;
                return;
            }
            int mid = l + (r - l) / 2;
            if (idx <= mid) {
                update(node * 2, l, mid, idx, value);
            } else {
                update(node * 2 + 1, mid + 1, r, idx, value);
            }
            tree[node] = tree[node * 2] + tree[node * 2 + 1];
        }

        int kth(int node, int l, int r, int k) const {
            if (l == r) return l;
            int mid = l + (r - l) / 2;
            int leftCount = tree[node * 2];
            if (k <= leftCount) return kth(node * 2, l, mid, k);
            return kth(node * 2 + 1, mid + 1, r, k - leftCount);
        }

    public:
        explicit KthOneSegmentTree(const vector<int>& arr)
            : n(static_cast<int>(arr.size())), tree(max(1, 4 * n), 0) {
            if (n) build(1, 0, n - 1, arr);
        }

        void pointUpdate(int idx, int value) {
            if (!n || idx < 0 || idx >= n) return;
            update(1, 0, n - 1, idx, value);
        }

        int kthOne(int k) const {
            if (!n || k <= 0 || k > tree[1]) return -1;
            return kth(1, 0, n - 1, k);
        }
    };
    """
)


RANGE_ADD_SUM_MIN_SEGMENT_TREE = cpp(
    r"""
    class RangeAddSumMinSegmentTree {
        struct Node {
            long long sum = 0;
            long long mn = 0;
            long long lazy = 0;
        };

        int n;
        vector<Node> tree;

        void build(int node, int l, int r, const vector<long long>& arr) {
            if (l == r) {
                tree[node].sum = tree[node].mn = arr[l];
                return;
            }
            int mid = l + (r - l) / 2;
            build(node * 2, l, mid, arr);
            build(node * 2 + 1, mid + 1, r, arr);
            pull(node);
        }

        void pull(int node) {
            tree[node].sum = tree[node * 2].sum + tree[node * 2 + 1].sum;
            tree[node].mn = min(tree[node * 2].mn, tree[node * 2 + 1].mn);
        }

        void apply(int node, int l, int r, long long value) {
            tree[node].sum += (r - l + 1LL) * value;
            tree[node].mn += value;
            tree[node].lazy += value;
        }

        void push(int node, int l, int r) {
            if (tree[node].lazy == 0 || l == r) return;
            int mid = l + (r - l) / 2;
            apply(node * 2, l, mid, tree[node].lazy);
            apply(node * 2 + 1, mid + 1, r, tree[node].lazy);
            tree[node].lazy = 0;
        }

        void update(int node, int l, int r, int ql, int qr, long long value) {
            if (qr < l || r < ql) return;
            if (ql <= l && r <= qr) {
                apply(node, l, r, value);
                return;
            }
            push(node, l, r);
            int mid = l + (r - l) / 2;
            update(node * 2, l, mid, ql, qr, value);
            update(node * 2 + 1, mid + 1, r, ql, qr, value);
            pull(node);
        }

        long long querySum(int node, int l, int r, int ql, int qr) {
            if (qr < l || r < ql) return 0;
            if (ql <= l && r <= qr) return tree[node].sum;
            push(node, l, r);
            int mid = l + (r - l) / 2;
            return querySum(node * 2, l, mid, ql, qr) +
                   querySum(node * 2 + 1, mid + 1, r, ql, qr);
        }

        long long queryMin(int node, int l, int r, int ql, int qr) {
            if (qr < l || r < ql) return LLONG_MAX;
            if (ql <= l && r <= qr) return tree[node].mn;
            push(node, l, r);
            int mid = l + (r - l) / 2;
            return min(queryMin(node * 2, l, mid, ql, qr),
                       queryMin(node * 2 + 1, mid + 1, r, ql, qr));
        }

    public:
        explicit RangeAddSumMinSegmentTree(const vector<long long>& arr)
            : n(static_cast<int>(arr.size())), tree(max(1, 4 * n)) {
            if (n) build(1, 0, n - 1, arr);
        }

        void addRange(int l, int r, long long value) {
            if (!n) return;
            l = max(l, 0);
            r = min(r, n - 1);
            if (l > r) return;
            update(1, 0, n - 1, l, r, value);
        }

        long long rangeSum(int l, int r) {
            if (!n) return 0;
            l = max(l, 0);
            r = min(r, n - 1);
            if (l > r) return 0;
            return querySum(1, 0, n - 1, l, r);
        }

        long long rangeMin(int l, int r) {
            if (!n) return 0;
            l = max(l, 0);
            r = min(r, n - 1);
            if (l > r) return 0;
            return queryMin(1, 0, n - 1, l, r);
        }
    };
    """
)


MITM_SUBSET_SUMS = cpp(
    r"""
    vector<long long> generateSubsetSums(const vector<long long>& arr, int l, int r) {
        int len = r - l;
        size_t total = 1ULL << len;
        vector<long long> sums;
        sums.reserve(total);
        for (size_t mask = 0; mask < total; ++mask) {
            long long sum = 0;
            for (int i = 0; i < len; ++i) {
                if (mask & (1ULL << i)) sum += arr[l + i];
            }
            sums.push_back(sum);
        }
        return sums;
    }
    """
)


LONGEST_REPEATED_SUBSTRING = "\n\n".join(
    [
        BUILD_SUFFIX_ARRAY,
        BUILD_LCP,
        cpp(
            r"""
            string longestRepeatedSubstring(const string& s) {
                if (s.empty()) return "";
                vector<int> sa = buildSuffixArray(s);
                vector<int> lcp = buildLCP(s, sa);
                int bestLen = 0;
                int bestPos = 0;
                for (int i = 0; i < static_cast<int>(lcp.size()); ++i) {
                    if (lcp[i] > bestLen) {
                        bestLen = lcp[i];
                        bestPos = sa[i];
                    }
                }
                return s.substr(bestPos, bestLen);
            }
            """
        ),
    ]
)


COUNT_DISTINCT_SUBSTRINGS_SA = "\n\n".join(
    [
        BUILD_SUFFIX_ARRAY,
        BUILD_LCP,
        cpp(
            r"""
            long long countDistinctSubstrings(const string& s) {
                long long n = static_cast<long long>(s.size());
                long long total = n * (n + 1) / 2;
                vector<int> sa = buildSuffixArray(s);
                vector<int> lcp = buildLCP(s, sa);
                long long repeated = 0;
                for (int x : lcp) repeated += x;
                return total - repeated;
            }
            """
        ),
    ]
)


SAM_COUNT_DISTINCT = "\n\n".join(
    [
        SUFFIX_AUTOMATON,
        cpp(
            r"""
            long long countDistinctSubstringsSAM(const string& s) {
                SuffixAutomaton sam;
                sam.build(s);
                long long ans = 0;
                for (int v = 1; v < static_cast<int>(sam.st.size()); ++v) {
                    ans += sam.st[v].len - sam.st[sam.st[v].link].len;
                }
                return ans;
            }
            """
        ),
    ]
)


SAM_LONGEST_COMMON_SUBSTRING = "\n\n".join(
    [
        SUFFIX_AUTOMATON,
        cpp(
            r"""
            string longestCommonSubstring(const string& s, const string& t) {
                if (s.empty() || t.empty()) return "";
                SuffixAutomaton sam;
                sam.build(s);

                int v = 0;
                int len = 0;
                int bestLen = 0;
                int bestEnd = -1;
                for (int i = 0; i < static_cast<int>(t.size()); ++i) {
                    int c = t[i] - 'a';
                    if (c < 0 || c >= 26) {
                        v = 0;
                        len = 0;
                        continue;
                    }
                    if (sam.st[v].next[c] != -1) {
                        v = sam.st[v].next[c];
                        ++len;
                    } else {
                        while (v != -1 && sam.st[v].next[c] == -1) {
                            v = sam.st[v].link;
                        }
                        if (v == -1) {
                            v = 0;
                            len = 0;
                            continue;
                        }
                        len = sam.st[v].len + 1;
                        v = sam.st[v].next[c];
                    }
                    if (len > bestLen) {
                        bestLen = len;
                        bestEnd = i;
                    }
                }

                return bestLen == 0 ? "" : t.substr(bestEnd - bestLen + 1, bestLen);
            }
            """
        ),
    ]
)


SAM_OCCURRENCES = "\n\n".join(
    [
        SUFFIX_AUTOMATON,
        cpp(
            r"""
            class SubstringOccurrenceCounter {
                SuffixAutomaton sam;

            public:
                explicit SubstringOccurrenceCounter(const string& s) {
                    sam.build(s);
                    sam.propagateOccurrences();
                }

                long long occurrences(const string& pattern) const {
                    int v = 0;
                    for (char ch : pattern) {
                        int c = ch - 'a';
                        if (c < 0 || c >= 26 || sam.st[v].next[c] == -1) return 0;
                        v = sam.st[v].next[c];
                    }
                    return sam.st[v].occ;
                }
            };
            """
        ),
    ]
)


SUFFIX_ARRAY_LCS = "\n\n".join(
    [
        cpp(
            r"""
            vector<int> buildSuffixArraySymbols(const vector<int>& symbols) {
                int n = static_cast<int>(symbols.size());
                if (n == 0) return {};
                vector<int> sa(n), rank = symbols, nextRank(n);
                iota(sa.begin(), sa.end(), 0);
                for (int k = 1;; k <<= 1) {
                    auto cmp = [&](int x, int y) {
                        if (rank[x] != rank[y]) return rank[x] < rank[y];
                        int rx = x + k < n ? rank[x + k] : -1;
                        int ry = y + k < n ? rank[y + k] : -1;
                        return rx < ry;
                    };
                    sort(sa.begin(), sa.end(), cmp);
                    nextRank[sa[0]] = 0;
                    for (int i = 1; i < n; ++i) {
                        nextRank[sa[i]] = nextRank[sa[i - 1]] + (cmp(sa[i - 1], sa[i]) ? 1 : 0);
                    }
                    rank.swap(nextRank);
                    if (rank[sa.back()] == n - 1) break;
                }
                return sa;
            }

            vector<int> buildLCPSymbols(const vector<int>& symbols, const vector<int>& sa) {
                int n = static_cast<int>(symbols.size());
                vector<int> rank(n), lcp(max(0, n - 1));
                for (int i = 0; i < n; ++i) rank[sa[i]] = i;
                int matched = 0;
                for (int i = 0; i < n; ++i) {
                    int pos = rank[i];
                    if (pos == n - 1) {
                        matched = 0;
                        continue;
                    }
                    int j = sa[pos + 1];
                    while (i + matched < n && j + matched < n &&
                           symbols[i + matched] == symbols[j + matched]) {
                        ++matched;
                    }
                    lcp[pos] = matched;
                    if (matched > 0) --matched;
                }
                return lcp;
            }

            string longestCommonSubstringSuffixArray(const string& a, const string& b) {
                if (a.empty() || b.empty()) return "";

                vector<int> merged;
                merged.reserve(a.size() + b.size() + 1);
                for (unsigned char ch : a) merged.push_back(static_cast<int>(ch) + 1);
                merged.push_back(0);
                for (unsigned char ch : b) merged.push_back(static_cast<int>(ch) + 1);

                int split = static_cast<int>(a.size());
                vector<int> sa = buildSuffixArraySymbols(merged);
                vector<int> lcp = buildLCPSymbols(merged, sa);
                int bestLen = 0;
                int bestPos = -1;
                for (int i = 0; i < static_cast<int>(lcp.size()); ++i) {
                    bool leftInA = sa[i] < split;
                    bool rightInA = sa[i + 1] < split;
                    bool leftInB = sa[i] > split;
                    bool rightInB = sa[i + 1] > split;
                    if (!((leftInA && rightInB) || (leftInB && rightInA))) continue;
                    if (lcp[i] > bestLen) {
                        bestLen = lcp[i];
                        bestPos = sa[i];
                    }
                }

                if (bestLen == 0) return "";
                return bestPos < split ? a.substr(bestPos, bestLen)
                                       : b.substr(bestPos - split - 1, bestLen);
            }
            """
        ),
    ]
)


EERTREE_LONGEST = "\n\n".join(
    [
        EERTREE,
        cpp(
            r"""
            string longestPalindromicSubstring(const string& s) {
                Eertree tree;
                tree.build(s);
                return tree.longestPalindrome();
            }
            """
        ),
    ]
)


COUNT_IN_VALUE_RANGE = cpp(
    r"""
    long long countInValueRange(const vector<long long>& arr, long long low, long long high) {
        if (arr.empty() || low > high) return 0;
        CoordinateCompression cc(vector<long long>(arr.begin(), arr.end()));
        PointCountSegmentTree st(cc.size());
        for (long long x : arr) {
            st.add(cc.indexOf(x), 1);
        }
        int left = cc.lowerBound(low);
        int right = cc.upperBound(high) - 1;
        if (left > right) return 0;
        return st.rangeSum(left, right);
    }
    """
)


MERGE_SORT_TREE_QUERY_HELPER = cpp(
    r"""
    int countGreater(const MergeSortTree& tree, int l, int r, int k) {
        return tree.countGreater(l, r, k);
    }
    """
)


PERSISTENT_SEGMENT_TREE_CREATE_VERSION = cpp(
    r"""
    int createVersion(PersistentSegmentTree& pst, int baseVersion, int idx, long long value) {
        return pst.updateVersion(baseVersion, idx, value);
    }
    """
)


PERSISTENT_SEGMENT_TREE_QUERY_HELPER = cpp(
    r"""
    long long rangeSum(const PersistentSegmentTree& pst, int version, int l, int r) {
        return pst.queryVersion(version, l, r);
    }
    """
)


DSA_CODE_OVERRIDES = {
    # 12. DP
    "12-dp-8-stock-trading-dp-at-most-k-transactions": [
        cpp(
            r"""
            int maxProfit(int K, const vector<int>& prices) {
                int n = static_cast<int>(prices.size());
                if (n == 0 || K == 0) return 0;
                if (K >= n / 2) {
                    int profit = 0;
                    for (int i = 1; i < n; ++i) {
                        profit += max(0, prices[i] - prices[i - 1]);
                    }
                    return profit;
                }

                const int NEG_INF = numeric_limits<int>::min() / 4;
                vector<int> hold(K + 1, NEG_INF), cash(K + 1, 0);
                for (int price : prices) {
                    vector<int> nextHold = hold;
                    vector<int> nextCash = cash;
                    for (int k = 1; k <= K; ++k) {
                        nextHold[k] = max(hold[k], cash[k - 1] - price);
                        nextCash[k] = max(cash[k], hold[k] + price);
                    }
                    hold.swap(nextHold);
                    cash.swap(nextCash);
                }
                return cash[K];
            }
            """
        )
    ],
    "12-dp-27-advanced-dp-egg-dropping": [
        cpp(
            r"""
            long long eggDrop(int eggs, long long floors) {
                if (floors < 0) throw invalid_argument("floors must be non-negative");
                if (floors == 0) return 0;
                if (eggs <= 0) throw invalid_argument("at least one egg is required");

                vector<long long> covered(eggs + 1, 0);
                long long moves = 0;
                while (covered[eggs] < floors) {
                    ++moves;
                    for (int e = eggs; e >= 1; --e) {
                        if (covered[e] >= floors - covered[e - 1] - 1) {
                            covered[e] = floors;
                        } else {
                            covered[e] += covered[e - 1] + 1;
                        }
                    }
                }
                return moves;
            }
            """
        )
    ],
    "12-dp-9-stock-trading-with-cooldown": [
        cpp(
            r"""
            int maxProfit(const vector<int>& prices) {
                if (prices.empty()) return 0;
                const int NEG_INF = numeric_limits<int>::min() / 4;
                int hold = -prices[0];
                int sold = NEG_INF;
                int rest = 0;
                for (int i = 1; i < static_cast<int>(prices.size()); ++i) {
                    int nextHold = max(hold, rest - prices[i]);
                    int nextSold = hold + prices[i];
                    int nextRest = max(rest, sold);
                    hold = nextHold;
                    sold = nextSold;
                    rest = nextRest;
                }
                return max(rest, sold);
            }
            """
        )
    ],
    "12-dp-10-stock-trading-with-transaction-fee": [
        cpp(
            r"""
            int maxProfit(const vector<int>& prices, int fee) {
                if (prices.empty()) return 0;
                int hold = -prices[0];
                int cash = 0;
                for (int i = 1; i < static_cast<int>(prices.size()); ++i) {
                    int nextHold = max(hold, cash - prices[i]);
                    int nextCash = max(cash, hold + prices[i] - fee);
                    hold = nextHold;
                    cash = nextCash;
                }
                return cash;
            }
            """
        )
    ],
    "12-dp-19-profile-dp-tiling-a-grid": [
        cpp(
            r"""
            void generateNextMasks(int row, int n, int mask, int nextMask, vector<int>& nextMasks) {
                if (row == n) {
                    nextMasks.push_back(nextMask);
                    return;
                }
                if (mask & (1 << row)) {
                    generateNextMasks(row + 1, n, mask, nextMask, nextMasks);
                    return;
                }
                generateNextMasks(row + 1, n, mask, nextMask | (1 << row), nextMasks);
                if (row + 1 < n && !(mask & (1 << (row + 1)))) {
                    generateNextMasks(row + 2, n, mask, nextMask, nextMasks);
                }
            }

            long long countTilings(int n, int m) {
                if (n < 0 || m < 0) return 0;
                if (n > m) swap(n, m);
                vector<long long> dp(1 << n, 0), next(1 << n, 0);
                dp[0] = 1;
                for (int col = 0; col < m; ++col) {
                    fill(next.begin(), next.end(), 0);
                    for (int mask = 0; mask < (1 << n); ++mask) {
                        if (dp[mask] == 0) continue;
                        vector<int> nextMasks;
                        generateNextMasks(0, n, mask, 0, nextMasks);
                        for (int newMask : nextMasks) {
                            next[newMask] += dp[mask];
                        }
                    }
                    dp.swap(next);
                }
                return dp[0];
            }
            """
        )
    ],
    "12-dp-23-decode-ways": [
        cpp(
            r"""
            int numDecodings(const string& s) {
                int n = static_cast<int>(s.size());
                if (n == 0 || s[0] == '0') return 0;
                int prev2 = 1;
                int prev1 = 1;
                for (int i = 1; i < n; ++i) {
                    int curr = 0;
                    if (s[i] != '0') curr += prev1;
                    int two = (s[i - 1] - '0') * 10 + (s[i] - '0');
                    if (10 <= two && two <= 26) curr += prev2;
                    prev2 = prev1;
                    prev1 = curr;
                }
                return prev1;
            }
            """
        )
    ],

    # 20. Backtracking Advanced
    "20-backtracking-advanced-3-word-search-ii-trie-backtracking": [
        cpp(
            r"""
            class Solution {
                struct Node {
                    array<int, 26> child;
                    string word;

                    Node() { child.fill(-1); }
                };

                vector<Node> trie;
                vector<string> ans;
                int rows = 0, cols = 0;

                void insert(const string& word) {
                    int node = 0;
                    for (char ch : word) {
                        int c = ch - 'a';
                        if (trie[node].child[c] == -1) {
                            trie[node].child[c] = static_cast<int>(trie.size());
                            trie.push_back(Node());
                        }
                        node = trie[node].child[c];
                    }
                    trie[node].word = word;
                }

                void dfs(vector<vector<char>>& board, int r, int c, int node) {
                    if (r < 0 || r >= rows || c < 0 || c >= cols || board[r][c] == '#') return;
                    char ch = board[r][c];
                    int next = trie[node].child[ch - 'a'];
                    if (next == -1) return;

                    if (!trie[next].word.empty()) {
                        ans.push_back(trie[next].word);
                        trie[next].word.clear();
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
                    ans.clear();
                    trie.assign(1, Node());
                    rows = static_cast<int>(board.size());
                    if (rows == 0) return ans;
                    cols = static_cast<int>(board[0].size());
                    if (cols == 0) return ans;

                    for (const string& word : words) {
                        if (!word.empty()) insert(word);
                    }
                    for (int r = 0; r < rows; ++r) {
                        for (int c = 0; c < cols; ++c) {
                            dfs(board, r, c, 0);
                        }
                    }
                    return ans;
                }
            };
            """
        )
    ],
    "20-backtracking-advanced-9-cryptarithmetic-verbal-arithmetic": [
        cpp(
            r"""
            class Solution {
                vector<int> digit;
                vector<int> used;
                vector<int> leading;

                bool solve(vector<string>& words, const string& result, int col, int row,
                           int carry) {
                    if (col == static_cast<int>(result.size())) return carry == 0;

                    if (row == static_cast<int>(words.size())) {
                        int resultPos = static_cast<int>(result.size()) - 1 - col;
                        int ch = result[resultPos] - 'A';
                        int need = carry % 10;
                        int nextCarry = carry / 10;

                        if (digit[ch] != -1) {
                            return digit[ch] == need &&
                                   solve(words, result, col + 1, 0, nextCarry);
                        }
                        if (used[need] || (need == 0 && leading[ch])) return false;

                        digit[ch] = need;
                        used[need] = 1;
                        if (solve(words, result, col + 1, 0, nextCarry)) return true;
                        digit[ch] = -1;
                        used[need] = 0;
                        return false;
                    }

                    if (col >= static_cast<int>(words[row].size())) {
                        return solve(words, result, col, row + 1, carry);
                    }

                    int pos = static_cast<int>(words[row].size()) - 1 - col;
                    int ch = words[row][pos] - 'A';
                    if (digit[ch] != -1) {
                        return solve(words, result, col, row + 1, carry + digit[ch]);
                    }

                    for (int d = 0; d <= 9; ++d) {
                        if (used[d] || (d == 0 && leading[ch])) continue;
                        digit[ch] = d;
                        used[d] = 1;
                        if (solve(words, result, col, row + 1, carry + d)) return true;
                        digit[ch] = -1;
                        used[d] = 0;
                    }
                    return false;
                }

            public:
                bool isSolvable(vector<string>& words, string result) {
                    unordered_set<char> distinct;
                    int maxLen = 0;
                    for (const string& word : words) {
                        maxLen = max(maxLen, static_cast<int>(word.size()));
                        if (word.size() > 1) distinct.insert(word.front());
                        for (char ch : word) distinct.insert(ch);
                    }
                    if (result.size() > 1) distinct.insert(result.front());
                    for (char ch : result) distinct.insert(ch);
                    if (distinct.size() > 10 || result.size() < static_cast<size_t>(maxLen) ||
                        result.size() > static_cast<size_t>(maxLen + 1)) {
                        return false;
                    }

                    digit.assign(26, -1);
                    used.assign(10, 0);
                    leading.assign(26, 0);
                    for (const string& word : words) {
                        if (word.size() > 1) leading[word.front() - 'A'] = 1;
                    }
                    if (result.size() > 1) leading[result.front() - 'A'] = 1;

                    return solve(words, result, 0, 0, 0);
                }
            };
            """
        )
    ],

    # 22. String - Advanced
    "22-string-advanced-2-suffix-array": [BUILD_SUFFIX_ARRAY],
    "22-string-advanced-3-lcp-array-kasais-algorithm": [BUILD_LCP],
    "22-string-advanced-4-longest-repeated-substring": [LONGEST_REPEATED_SUBSTRING],
    "22-string-advanced-5-number-of-distinct-substrings": [COUNT_DISTINCT_SUBSTRINGS_SA],
    "22-string-advanced-6-suffix-automaton": [SUFFIX_AUTOMATON],
    "22-string-advanced-7-count-distinct-substrings-using-suffix-automaton": [
        SAM_COUNT_DISTINCT
    ],
    "22-string-advanced-8-string-periodicity": [
        cpp(
            r"""
            bool isPeriodic(const string& s) {
                int n = static_cast<int>(s.size());
                if (n == 0) return false;
                vector<int> lps(n, 0);
                for (int i = 1, len = 0; i < n;) {
                    if (s[i] == s[len]) {
                        lps[i++] = ++len;
                    } else if (len) {
                        len = lps[len - 1];
                    } else {
                        lps[i++] = 0;
                    }
                }
                int period = n - lps[n - 1];
                return lps[n - 1] > 0 && n % period == 0;
            }
            """
        )
    ],
    "22-string-advanced-9-minimum-rotation-booths-algorithm": [
        cpp(
            r"""
            string minimumRotation(const string& s) {
                int n = static_cast<int>(s.size());
                if (n == 0) return "";
                string doubled = s + s;
                int i = 0, j = 1, k = 0;
                while (i < n && j < n && k < n) {
                    if (doubled[i + k] == doubled[j + k]) {
                        ++k;
                        continue;
                    }
                    if (doubled[i + k] > doubled[j + k]) {
                        i += k + 1;
                    } else {
                        j += k + 1;
                    }
                    if (i == j) ++j;
                    k = 0;
                }
                int start = min(i, j);
                return doubled.substr(start, n);
            }
            """
        )
    ],
    "22-string-advanced-10-rolling-hash-double-hashing": [
        cpp(
            r"""
            class DoubleRollingHash {
                static constexpr long long MOD1 = 1'000'000'007LL;
                static constexpr long long MOD2 = 1'000'000'009LL;
                static constexpr long long BASE = 911'382'323LL;

                vector<long long> hash1, hash2, power1, power2;

            public:
                explicit DoubleRollingHash(const string& s)
                    : hash1(s.size() + 1, 0),
                      hash2(s.size() + 1, 0),
                      power1(s.size() + 1, 1),
                      power2(s.size() + 1, 1) {
                    for (int i = 0; i < static_cast<int>(s.size()); ++i) {
                        int value = static_cast<unsigned char>(s[i]) + 1;
                        hash1[i + 1] = (hash1[i] * BASE + value) % MOD1;
                        hash2[i + 1] = (hash2[i] * BASE + value) % MOD2;
                        power1[i + 1] = power1[i] * BASE % MOD1;
                        power2[i + 1] = power2[i] * BASE % MOD2;
                    }
                }

                pair<long long, long long> getHash(int l, int r) const {
                    if (l < 0 || r < l || r + 1 >= static_cast<int>(hash1.size())) {
                        return {-1, -1};
                    }
                    long long x1 =
                        (hash1[r + 1] - hash1[l] * power1[r - l + 1] % MOD1 + MOD1) % MOD1;
                    long long x2 =
                        (hash2[r + 1] - hash2[l] * power2[r - l + 1] % MOD2 + MOD2) % MOD2;
                    return {x1, x2};
                }

                bool equal(int l1, int r1, int l2, int r2) const {
                    int n = static_cast<int>(hash1.size()) - 1;
                    if (l1 < 0 || l2 < 0 || r1 < l1 || r2 < l2 || r1 >= n || r2 >= n) {
                        return false;
                    }
                    if (r1 - l1 != r2 - l2) return false;
                    return getHash(l1, r1) == getHash(l2, r2);
                }
            };
            """
        )
    ],
    "22-string-advanced-11-palindromic-tree-eertree": [EERTREE],
    "22-string-advanced-12-lyndon-factorization-duvals-algorithm": [
        cpp(
            r"""
            vector<string> duval(const string& s) {
                int n = static_cast<int>(s.size());
                vector<string> factorization;
                int i = 0;
                while (i < n) {
                    int j = i + 1;
                    int k = i;
                    while (j < n && s[k] <= s[j]) {
                        if (s[k] < s[j]) {
                            k = i;
                        } else {
                            ++k;
                        }
                        ++j;
                    }
                    while (i <= k) {
                        factorization.push_back(s.substr(i, j - k));
                        i += j - k;
                    }
                }
                return factorization;
            }
            """
        )
    ],
    "22-string-advanced-13-suffix-automaton-longest-common-substring": [
        SAM_LONGEST_COMMON_SUBSTRING
    ],
    "22-string-advanced-14-suffix-array-lcp-longest-common-substring-of-two-strings": [
        SUFFIX_ARRAY_LCS
    ],
    "22-string-advanced-15-smallest-string-after-k-deletions": [
        cpp(
            r"""
            string smallestAfterKDeletions(const string& s, int k) {
                if (k <= 0) return s;
                if (k >= static_cast<int>(s.size())) return "";
                string st;
                for (char ch : s) {
                    while (!st.empty() && k > 0 && st.back() > ch) {
                        st.pop_back();
                        --k;
                    }
                    st.push_back(ch);
                }
                while (k > 0 && !st.empty()) {
                    st.pop_back();
                    --k;
                }
                return st;
            }
            """
        )
    ],
    "22-string-advanced-16-lexicographically-smallest-substring-of-fixed-length": [
        cpp(
            r"""
            string smallestSubstring(const string& s, int k) {
                if (k <= 0 || k > static_cast<int>(s.size())) return "";
                string ans = s.substr(0, k);
                for (int i = 1; i + k <= static_cast<int>(s.size()); ++i) {
                    string cur = s.substr(i, k);
                    if (cur < ans) ans = cur;
                }
                return ans;
            }
            """
        )
    ],
    "22-string-advanced-17-longest-palindromic-substring-with-eertree": [EERTREE_LONGEST],
    "22-string-advanced-18-count-occurrences-of-every-substring-pattern": [
        SAM_OCCURRENCES
    ],

    # 23. Segment Tree - Advanced
    "23-segment-tree-advanced-1-range-assignment-range-sum-lazy-propagation": [
        RANGE_ASSIGN_SUM_SEGMENT_TREE
    ],
    "23-segment-tree-advanced-2-range-add-range-minimum-query": [
        RANGE_ADD_MIN_SEGMENT_TREE
    ],
    "23-segment-tree-advanced-3-lazy-propagation-with-multiple-operations": [
        RANGE_ADD_MUL_SUM_SEGMENT_TREE
    ],
    "23-segment-tree-advanced-4-segment-tree-beats": [SEGMENT_TREE_BEATS],
    "23-segment-tree-advanced-5-dynamic-segment-tree": [DYNAMIC_SEGMENT_TREE],
    "23-segment-tree-advanced-6-persistent-segment-tree": [
        PERSISTENT_SEGMENT_TREE,
        PERSISTENT_SEGMENT_TREE_CREATE_VERSION,
        PERSISTENT_SEGMENT_TREE_QUERY_HELPER,
    ],
    "23-segment-tree-advanced-7-persistent-segment-tree-kth-smallest-in-range": [
        PERSISTENT_KTH_SMALLEST
    ],
    "23-segment-tree-advanced-8-merge-sort-tree": [
        MERGE_SORT_TREE,
        MERGE_SORT_TREE_QUERY_HELPER,
    ],
    "23-segment-tree-advanced-9-segment-tree-coordinate-compression": [
        COORDINATE_COMPRESSION,
        POINT_COUNT_SEGMENT_TREE,
        COUNT_IN_VALUE_RANGE,
    ],
    "23-segment-tree-advanced-10-segment-tree-for-maximum-subarray-sum": [
        MAX_SUBARRAY_SEGMENT_TREE
    ],
    "23-segment-tree-advanced-11-segment-tree-for-gcd-lcm": [GCD_SEGMENT_TREE],
    "23-segment-tree-advanced-12-segment-tree-with-custom-node-information": [
        MIN_COUNT_NODE,
        MIN_COUNT_SEGMENT_TREE,
    ],
    "23-segment-tree-advanced-13-segment-tree-find-first-position-x": [
        RANGE_MAX_SEGMENT_TREE
    ],
    "23-segment-tree-advanced-14-segment-tree-find-kth-one": [KTH_ONE_SEGMENT_TREE],
    "23-segment-tree-advanced-15-segment-tree-binary-search-on-answer": [
        cpp(
            r"""
            long long binarySearchAnswer(long long lo, long long hi,
                                         const function<bool(long long)>& check) {
                while (lo < hi) {
                    long long mid = lo + (hi - lo) / 2;
                    if (check(mid)) {
                        hi = mid;
                    } else {
                        lo = mid + 1;
                    }
                }
                return lo;
            }
            """
        )
    ],
    "23-segment-tree-advanced-16-range-add-range-sum-range-minimum": [
        RANGE_ADD_SUM_MIN_SEGMENT_TREE
    ],
    "23-segment-tree-advanced-17-range-chmin-segment-tree-beats": [SEGMENT_TREE_BEATS],
    "23-segment-tree-advanced-18-range-chmax-range-chmin-range-sum": [
        SEGMENT_TREE_BEATS
    ],
    "23-segment-tree-advanced-19-number-of-inversions-using-segment-tree": [
        cpp(
            r"""
            long long countInversions(const vector<int>& arr) {
                if (arr.empty()) return 0;
                vector<int> values = arr;
                sort(values.begin(), values.end());
                values.erase(unique(values.begin(), values.end()), values.end());

                int m = static_cast<int>(values.size());
                vector<int> tree(max(1, 4 * m), 0);

                function<void(int, int, int, int)> add = [&](int node, int l, int r, int idx) {
                    if (l == r) {
                        tree[node]++;
                        return;
                    }
                    int mid = l + (r - l) / 2;
                    if (idx <= mid) {
                        add(node * 2, l, mid, idx);
                    } else {
                        add(node * 2 + 1, mid + 1, r, idx);
                    }
                    tree[node] = tree[node * 2] + tree[node * 2 + 1];
                };

                function<int(int, int, int, int, int)> query =
                    [&](int node, int l, int r, int ql, int qr) -> int {
                    if (qr < l || r < ql) return 0;
                    if (ql <= l && r <= qr) return tree[node];
                    int mid = l + (r - l) / 2;
                    return query(node * 2, l, mid, ql, qr) +
                           query(node * 2 + 1, mid + 1, r, ql, qr);
                };

                long long inversions = 0;
                for (int i = static_cast<int>(arr.size()) - 1; i >= 0; --i) {
                    int idx = static_cast<int>(
                        lower_bound(values.begin(), values.end(), arr[i]) - values.begin());
                    if (idx > 0) inversions += query(1, 0, m - 1, 0, idx - 1);
                    add(1, 0, m - 1, idx);
                }
                return inversions;
            }
            """
        )
    ],
    "23-segment-tree-advanced-20-dynamic-range-queries-on-1018-coordinates": [
        DYNAMIC_SEGMENT_TREE
    ],
    "23-segment-tree-advanced-21-historical-queries-with-persistent-segment-tree": [
        PERSISTENT_SEGMENT_TREE
    ],
    "23-segment-tree-advanced-22-kth-smallest-number-in-a-subarray": [
        PERSISTENT_KTH_SMALLEST
    ],
    "23-segment-tree-advanced-23-count-elements-greater-than-x-in-range": [
        MERGE_SORT_TREE
    ],
    "23-segment-tree-advanced-24-maximum-subarray-sum-with-updates": [
        MAX_SUBARRAY_SEGMENT_TREE
    ],

    # 25. Meet in the Middle
    "25-meet-in-the-middle-14-meet-in-the-middle": [MITM_SUBSET_SUMS],
    "25-meet-in-the-middle-2-closest-subset-sum": [
        "\n\n".join(
            [
                MITM_SUBSET_SUMS,
                cpp(
                    r"""
                    long long closestSubsetSum(const vector<long long>& arr, long long target) {
                        int n = static_cast<int>(arr.size());
                        int mid = n / 2;
                        vector<long long> left = generateSubsetSums(arr, 0, mid);
                        vector<long long> right = generateSubsetSums(arr, mid, n);
                        sort(right.begin(), right.end());

                        long long bestSum = 0;
                        long long bestDiff = LLONG_MAX;
                        auto relax = [&](long long candidate) {
                            long long diff = llabs(candidate - target);
                            if (diff < bestDiff || (diff == bestDiff && candidate < bestSum)) {
                                bestDiff = diff;
                                bestSum = candidate;
                            }
                        };

                        for (long long x : left) {
                            long long need = target - x;
                            auto it = lower_bound(right.begin(), right.end(), need);
                            if (it != right.end()) relax(x + *it);
                            if (it != right.begin()) {
                                --it;
                                relax(x + *it);
                            }
                        }
                        return bestSum;
                    }
                    """
                ),
            ]
        )
    ],
    "25-meet-in-the-middle-9-mitm-bitmask-for-constraint-matching": [
        cpp(
            r"""
            long long maximizeCoveredValue(const vector<long long>& values,
                                           const vector<int>& masks,
                                           int constraintCount) {
                int n = static_cast<int>(values.size());
                if (masks.size() != values.size() || constraintCount < 0 ||
                    constraintCount > 20) {
                    return LLONG_MIN;
                }

                int mid = n / 2;
                vector<pair<int, long long>> left, right;

                for (int subset = 0; subset < (1 << mid); ++subset) {
                    int mask = 0;
                    long long value = 0;
                    for (int i = 0; i < mid; ++i) {
                        if (subset & (1 << i)) {
                            mask |= masks[i];
                            value += values[i];
                        }
                    }
                    left.push_back({mask, value});
                }

                int rightSize = n - mid;
                for (int subset = 0; subset < (1 << rightSize); ++subset) {
                    int mask = 0;
                    long long value = 0;
                    for (int i = 0; i < rightSize; ++i) {
                        if (subset & (1 << i)) {
                            mask |= masks[mid + i];
                            value += values[mid + i];
                        }
                    }
                    right.push_back({mask, value});
                }

                int fullMask = (1 << constraintCount) - 1;
                vector<long long> best(1 << constraintCount, LLONG_MIN);
                for (auto [mask, value] : right) {
                    best[mask] = max(best[mask], value);
                }
                for (int bit = 0; bit < constraintCount; ++bit) {
                    for (int mask = 0; mask <= fullMask; ++mask) {
                        if ((mask & (1 << bit)) == 0) {
                            best[mask] = max(best[mask], best[mask | (1 << bit)]);
                        }
                    }
                }

                long long ans = LLONG_MIN;
                for (auto [mask, value] : left) {
                    int need = fullMask ^ mask;
                    if (best[need] == LLONG_MIN) continue;
                    ans = max(ans, value + best[need]);
                }
                return ans;
            }
            """
        )
    ],

    # Tab 26
    "tab-26-dsa-master-topic-index": [],
}

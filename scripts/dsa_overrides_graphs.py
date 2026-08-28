"""Canonical C++17 overrides for graph, DSU, and network-flow DSA sections."""

from __future__ import annotations

from textwrap import dedent


def cpp(source: str) -> str:
    return dedent(source).strip()


def join_cpp(*parts: str) -> str:
    return "\n\n".join(part.strip() for part in parts if part and part.strip())


CPP_HEADER = cpp(
    r"""
    #include <bits/stdc++.h>
    using namespace std;
    """
)


DSU_HELPER = cpp(
    r"""
    class DSU {
        vector<int> parent, size_;

       public:
        explicit DSU(int n) : parent(n), size_(n, 1) {
            iota(parent.begin(), parent.end(), 0);
        }

        int find(int x) {
            return parent[x] == x ? x : parent[x] = find(parent[x]);
        }

        bool unite(int a, int b) {
            a = find(a);
            b = find(b);
            if (a == b) return false;
            if (size_[a] < size_[b]) swap(a, b);
            parent[b] = a;
            size_[a] += size_[b];
            return true;
        }

        int componentSize(int x) {
            return size_[find(x)];
        }
    };
    """
)


KRUSKAL_MST = join_cpp(
    CPP_HEADER,
    DSU_HELPER,
    cpp(
        r"""
        struct Edge {
            int u, v;
            long long w;
        };

        long long kruskal(int n, vector<Edge> edges) {
            if (n == 0) return 0;
            sort(edges.begin(), edges.end(),
                 [](const Edge& a, const Edge& b) { return a.w < b.w; });

            DSU dsu(n);
            long long cost = 0;
            int used = 0;
            for (const auto& e : edges) {
                if (!dsu.unite(e.u, e.v)) continue;
                cost += e.w;
                if (++used == n - 1) break;
            }
            return used == n - 1 ? cost : -1;
        }
        """
    ),
)


OFFLINE_DYNAMIC_CONNECTIVITY = join_cpp(
    CPP_HEADER,
    cpp(
        r"""
        class RollbackDSU {
            struct Change {
                int child;
                int sizeOfParent;
            };

            vector<int> parent, size_;
            vector<Change> history;

           public:
            explicit RollbackDSU(int n) : parent(n), size_(n, 1) {
                iota(parent.begin(), parent.end(), 0);
            }

            int find(int x) {
                while (x != parent[x]) x = parent[x];
                return x;
            }

            bool same(int a, int b) {
                return find(a) == find(b);
            }

            void unite(int a, int b) {
                a = find(a);
                b = find(b);
                if (a == b) {
                    history.push_back({-1, -1});
                    return;
                }
                if (size_[a] < size_[b]) swap(a, b);
                history.push_back({b, size_[a]});
                parent[b] = a;
                size_[a] += size_[b];
            }

            int snapshot() const {
                return static_cast<int>(history.size());
            }

            void rollback(int snapshot) {
                while (static_cast<int>(history.size()) > snapshot) {
                    auto [child, sizeOfParent] = history.back();
                    history.pop_back();
                    if (child == -1) continue;
                    int root = parent[child];
                    parent[child] = child;
                    size_[root] = sizeOfParent;
                }
            }
        };

        class OfflineDynamicConnectivity {
            struct Operation {
                int type;
                int u, v;
            };

            using Edge = pair<int, int>;

            int n;
            vector<Operation> ops;

            static Edge normalize(int u, int v) {
                if (u > v) swap(u, v);
                return {u, v};
            }

            static long long encode(const Edge& edge) {
                return (static_cast<long long>(edge.first) << 32) ^
                       static_cast<unsigned int>(edge.second);
            }

            void addInterval(int node, int left, int right, int ql, int qr, const Edge& edge,
                             vector<vector<Edge>>& seg) const {
                if (ql > right || qr < left) return;
                if (ql <= left && right <= qr) {
                    seg[node].push_back(edge);
                    return;
                }
                int mid = (left + right) / 2;
                addInterval(node * 2, left, mid, ql, qr, edge, seg);
                addInterval(node * 2 + 1, mid + 1, right, ql, qr, edge, seg);
            }

           public:
            explicit OfflineDynamicConnectivity(int n) : n(n) {}

            void addEdge(int u, int v) {
                auto [a, b] = normalize(u, v);
                ops.push_back({0, a, b});
            }

            void removeEdge(int u, int v) {
                auto [a, b] = normalize(u, v);
                ops.push_back({1, a, b});
            }

            void addQuery(int u, int v) {
                auto [a, b] = normalize(u, v);
                ops.push_back({2, a, b});
            }

            vector<bool> solve() const {
                int m = static_cast<int>(ops.size());
                if (m == 0) return {};

                vector<vector<Edge>> seg(4 * m);
                unordered_map<long long, pair<int, Edge>> active;
                vector<int> queryId(m, -1);
                vector<Edge> queries;

                for (int time = 0; time < m; ++time) {
                    const auto& op = ops[time];
                    Edge edge = {op.u, op.v};
                    long long key = encode(edge);

                    if (op.type == 0) {
                        if (active.count(key)) {
                            throw invalid_argument("edge added twice without removal");
                        }
                        active[key] = {time, edge};
                    } else if (op.type == 1) {
                        auto it = active.find(key);
                        if (it == active.end()) {
                            throw invalid_argument("removing an edge that is not active");
                        }
                        addInterval(1, 0, m - 1, it->second.first, time - 1, it->second.second, seg);
                        active.erase(it);
                    } else {
                        queryId[time] = static_cast<int>(queries.size());
                        queries.push_back(edge);
                    }
                }

                for (const auto& [_, info] : active) {
                    addInterval(1, 0, m - 1, info.first, m - 1, info.second, seg);
                }

                vector<bool> answer(queries.size(), false);
                RollbackDSU dsu(n);

                function<void(int, int, int)> dfs = [&](int node, int left, int right) {
                    int snapshot = dsu.snapshot();
                    for (const auto& [u, v] : seg[node]) dsu.unite(u, v);

                    if (left == right) {
                        if (queryId[left] != -1) {
                            const auto& [u, v] = queries[queryId[left]];
                            answer[queryId[left]] = dsu.same(u, v);
                        }
                    } else {
                        int mid = (left + right) / 2;
                        dfs(node * 2, left, mid);
                        dfs(node * 2 + 1, mid + 1, right);
                    }

                    dsu.rollback(snapshot);
                };

                dfs(1, 0, m - 1);
                return answer;
            }
        };
        """
    ),
)


DINIC_HELPER = cpp(
    r"""
    struct Dinic {
        struct Edge {
            int to, rev;
            long long cap;
        };

        vector<vector<Edge>> g;
        vector<int> level, ptr;

        explicit Dinic(int n) : g(n), level(n), ptr(n) {}

        void addEdge(int u, int v, long long cap) {
            Edge a{v, static_cast<int>(g[v].size()), cap};
            Edge b{u, static_cast<int>(g[u].size()), 0};
            g[u].push_back(a);
            g[v].push_back(b);
        }

        bool bfs(int s, int t) {
            fill(level.begin(), level.end(), -1);
            queue<int> q;
            q.push(s);
            level[s] = 0;
            while (!q.empty()) {
                int u = q.front();
                q.pop();
                for (const auto& e : g[u]) {
                    if (e.cap > 0 && level[e.to] == -1) {
                        level[e.to] = level[u] + 1;
                        q.push(e.to);
                    }
                }
            }
            return level[t] != -1;
        }

        long long dfs(int u, int t, long long pushed) {
            if (u == t || pushed == 0) return pushed;
            for (int& i = ptr[u]; i < static_cast<int>(g[u].size()); ++i) {
                Edge& e = g[u][i];
                if (e.cap == 0 || level[e.to] != level[u] + 1) continue;
                long long sent = dfs(e.to, t, min(pushed, e.cap));
                if (sent == 0) continue;
                e.cap -= sent;
                g[e.to][e.rev].cap += sent;
                return sent;
            }
            return 0;
        }

        long long maxFlow(int s, int t) {
            long long flow = 0;
            while (bfs(s, t)) {
                fill(ptr.begin(), ptr.end(), 0);
                while (long long pushed = dfs(s, t, LLONG_MAX)) {
                    flow += pushed;
                }
            }
            return flow;
        }

        const vector<vector<Edge>>& graph() const {
            return g;
        }
    };
    """
)


HOPCROFT_KARP_HELPER = cpp(
    r"""
    class HopcroftKarp {
        int n, m;
        vector<vector<int>> adj;
        vector<int> pairU, pairV, dist;

        bool bfs() {
            queue<int> q;
            bool foundFreeVertex = false;
            for (int u = 0; u < n; ++u) {
                if (pairU[u] == -1) {
                    dist[u] = 0;
                    q.push(u);
                } else {
                    dist[u] = -1;
                }
            }

            while (!q.empty()) {
                int u = q.front();
                q.pop();
                for (int v : adj[u]) {
                    int matched = pairV[v];
                    if (matched == -1) {
                        foundFreeVertex = true;
                    } else if (dist[matched] == -1) {
                        dist[matched] = dist[u] + 1;
                        q.push(matched);
                    }
                }
            }
            return foundFreeVertex;
        }

        bool dfs(int u) {
            for (int v : adj[u]) {
                int matched = pairV[v];
                if (matched == -1 || (dist[matched] == dist[u] + 1 && dfs(matched))) {
                    pairU[u] = v;
                    pairV[v] = u;
                    return true;
                }
            }
            dist[u] = -1;
            return false;
        }

       public:
        HopcroftKarp(int n, int m, vector<vector<int>> adj)
            : n(n), m(m), adj(std::move(adj)), pairU(n, -1), pairV(m, -1), dist(n) {}

        int maxMatching() {
            int matching = 0;
            while (bfs()) {
                for (int u = 0; u < n; ++u) {
                    if (pairU[u] == -1 && dfs(u)) ++matching;
                }
            }
            return matching;
        }

        const vector<int>& leftMatch() const {
            return pairU;
        }

        const vector<int>& rightMatch() const {
            return pairV;
        }

        const vector<vector<int>>& graph() const {
            return adj;
        }
    };
    """
)


MIN_COST_MAX_FLOW_SPFA = cpp(
    r"""
    class MinCostMaxFlow {
       public:
        struct Edge {
            int to, rev;
            long long cap, cost;
        };

        explicit MinCostMaxFlow(int n) : g(n) {}

        void addEdge(int u, int v, long long cap, long long cost) {
            Edge a{v, static_cast<int>(g[v].size()), cap, cost};
            Edge b{u, static_cast<int>(g[u].size()), 0, -cost};
            g[u].push_back(a);
            g[v].push_back(b);
        }

        pair<long long, long long> minCostMaxFlow(int s, int t) {
            const long long INF = LLONG_MAX / 4;
            long long flow = 0;
            long long cost = 0;

            while (true) {
                vector<long long> dist(g.size(), INF);
                vector<int> parentV(g.size(), -1), parentE(g.size(), -1);
                vector<char> inQueue(g.size(), 0);
                queue<int> q;
                dist[s] = 0;
                q.push(s);
                inQueue[s] = 1;

                while (!q.empty()) {
                    int u = q.front();
                    q.pop();
                    inQueue[u] = 0;
                    for (int i = 0; i < static_cast<int>(g[u].size()); ++i) {
                        const Edge& e = g[u][i];
                        if (e.cap == 0 || dist[u] + e.cost >= dist[e.to]) continue;
                        dist[e.to] = dist[u] + e.cost;
                        parentV[e.to] = u;
                        parentE[e.to] = i;
                        if (!inQueue[e.to]) {
                            inQueue[e.to] = 1;
                            q.push(e.to);
                        }
                    }
                }

                if (dist[t] == INF) break;

                long long pushed = LLONG_MAX;
                for (int v = t; v != s; v = parentV[v]) {
                    const Edge& e = g[parentV[v]][parentE[v]];
                    pushed = min(pushed, e.cap);
                }

                for (int v = t; v != s; v = parentV[v]) {
                    Edge& e = g[parentV[v]][parentE[v]];
                    e.cap -= pushed;
                    g[v][e.rev].cap += pushed;
                }

                flow += pushed;
                cost += pushed * dist[t];
            }

            return {flow, cost};
        }

        const vector<vector<Edge>>& graph() const {
            return g;
        }

       private:
        vector<vector<Edge>> g;
    };
    """
)


MIN_COST_MAX_FLOW_POTENTIALS = cpp(
    r"""
    class MinCostMaxFlow {
       public:
        struct Edge {
            int to, rev;
            long long cap, cost;
        };

        explicit MinCostMaxFlow(int n)
            : g(n), potential(n, 0), dist(n), parentV(n), parentE(n) {}

        void addEdge(int u, int v, long long cap, long long cost) {
            Edge a{v, static_cast<int>(g[v].size()), cap, cost};
            Edge b{u, static_cast<int>(g[u].size()), 0, -cost};
            g[u].push_back(a);
            g[v].push_back(b);
        }

        pair<long long, long long> minCostMaxFlow(int s, int t, long long need = LLONG_MAX) {
            const long long INF = LLONG_MAX / 4;
            long long flow = 0;
            long long cost = 0;

            while (flow < need) {
                fill(dist.begin(), dist.end(), INF);
                priority_queue<pair<long long, int>, vector<pair<long long, int>>,
                               greater<pair<long long, int>>>
                    pq;
                dist[s] = 0;
                pq.push({0, s});

                while (!pq.empty()) {
                    auto [d, u] = pq.top();
                    pq.pop();
                    if (d != dist[u]) continue;

                    for (int i = 0; i < static_cast<int>(g[u].size()); ++i) {
                        const Edge& e = g[u][i];
                        if (e.cap == 0) continue;
                        long long nd = d + e.cost + potential[u] - potential[e.to];
                        if (nd >= dist[e.to]) continue;
                        dist[e.to] = nd;
                        parentV[e.to] = u;
                        parentE[e.to] = i;
                        pq.push({nd, e.to});
                    }
                }

                if (dist[t] == INF) break;

                for (int v = 0; v < static_cast<int>(g.size()); ++v) {
                    if (dist[v] != INF) potential[v] += dist[v];
                }

                long long pushed = need - flow;
                for (int v = t; v != s; v = parentV[v]) {
                    const Edge& e = g[parentV[v]][parentE[v]];
                    pushed = min(pushed, e.cap);
                }

                for (int v = t; v != s; v = parentV[v]) {
                    Edge& e = g[parentV[v]][parentE[v]];
                    e.cap -= pushed;
                    g[v][e.rev].cap += pushed;
                    cost += pushed * e.cost;
                }

                flow += pushed;
            }

            return {flow, cost};
        }

        const vector<vector<Edge>>& graph() const {
            return g;
        }

       private:
        vector<vector<Edge>> g;
        vector<long long> potential, dist;
        vector<int> parentV, parentE;
    };
    """
)


TWO_SAT_HELPER = cpp(
    r"""
    class TwoSAT {
        int n;
        vector<vector<int>> g, rg;
        vector<int> order, comp, assignment;

        int node(int var, bool isTrue) const {
            return 2 * var + (isTrue ? 0 : 1);
        }

        int neg(int x) const {
            return x ^ 1;
        }

        void addImplication(int u, int v) {
            g[u].push_back(v);
            rg[v].push_back(u);
        }

       public:
        explicit TwoSAT(int n) : n(n), g(2 * n), rg(2 * n), assignment(n, 0) {}

        void addClause(int x, bool xVal, int y, bool yVal) {
            int a = node(x, xVal);
            int b = node(y, yVal);
            addImplication(neg(a), b);
            addImplication(neg(b), a);
        }

        bool satisfiable() {
            int N = 2 * n;
            order.clear();
            comp.assign(N, -1);

            vector<int> vis(N, 0);
            function<void(int)> dfs1 = [&](int u) {
                vis[u] = 1;
                for (int v : g[u]) {
                    if (!vis[v]) dfs1(v);
                }
                order.push_back(u);
            };

            for (int i = 0; i < N; ++i) {
                if (!vis[i]) dfs1(i);
            }

            reverse(order.begin(), order.end());
            function<void(int, int)> dfs2 = [&](int u, int color) {
                comp[u] = color;
                for (int v : rg[u]) {
                    if (comp[v] == -1) dfs2(v, color);
                }
            };

            int colors = 0;
            for (int u : order) {
                if (comp[u] == -1) dfs2(u, colors++);
            }

            for (int i = 0; i < n; ++i) {
                if (comp[2 * i] == comp[2 * i + 1]) return false;
                assignment[i] = comp[2 * i] > comp[2 * i + 1];
            }
            return true;
        }

        const vector<int>& values() const {
            return assignment;
        }
    };
    """
)


LARGEST_COMPONENT = join_cpp(
    CPP_HEADER,
    DSU_HELPER,
    cpp(
        r"""
        int largestComponent(int n, const vector<vector<int>>& edges) {
            if (n == 0) return 0;
            DSU dsu(n);
            int best = 1;
            for (const auto& edge : edges) {
                dsu.unite(edge[0], edge[1]);
                best = max(best, dsu.componentSize(edge[0]));
            }
            return best;
        }
        """
    ),
)


NEGATIVE_CYCLE_FLOYD_WARSHALL = join_cpp(
    CPP_HEADER,
    cpp(
        r"""
        bool hasNegativeCycle(vector<vector<long long>> dist) {
            const long long INF = static_cast<long long>(1e18);
            int n = static_cast<int>(dist.size());
            for (int k = 0; k < n; ++k) {
                for (int i = 0; i < n; ++i) {
                    if (dist[i][k] == INF) continue;
                    for (int j = 0; j < n; ++j) {
                        if (dist[k][j] == INF) continue;
                        dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j]);
                    }
                }
            }
            for (int i = 0; i < n; ++i) {
                if (dist[i][i] < 0) return true;
            }
            return false;
        }
        """
    ),
)


BRIDGES_WITH_PARALLEL_EDGES = join_cpp(
    CPP_HEADER,
    cpp(
        r"""
        vector<pair<int, int>> findBridges(int n, const vector<pair<int, int>>& edges) {
            vector<vector<pair<int, int>>> adj(n);
            for (int id = 0; id < static_cast<int>(edges.size()); ++id) {
                auto [u, v] = edges[id];
                adj[u].push_back({v, id});
                adj[v].push_back({u, id});
            }

            vector<int> tin(n, -1), low(n);
            vector<pair<int, int>> bridges;
            int timer = 0;

            function<void(int, int)> dfs = [&](int u, int parentEdge) {
                tin[u] = low[u] = timer++;
                for (auto [v, id] : adj[u]) {
                    if (id == parentEdge) continue;
                    if (tin[v] == -1) {
                        dfs(v, id);
                        low[u] = min(low[u], low[v]);
                        if (low[v] > tin[u]) bridges.push_back(edges[id]);
                    } else {
                        low[u] = min(low[u], tin[v]);
                    }
                }
            };

            for (int i = 0; i < n; ++i) {
                if (tin[i] == -1) dfs(i, -1);
            }
            return bridges;
        }
        """
    ),
)


ARTICULATION_POINTS_WITH_PARALLEL_EDGES = join_cpp(
    CPP_HEADER,
    cpp(
        r"""
        vector<int> articulationPoints(int n, const vector<pair<int, int>>& edges) {
            vector<vector<pair<int, int>>> adj(n);
            for (int id = 0; id < static_cast<int>(edges.size()); ++id) {
                auto [u, v] = edges[id];
                adj[u].push_back({v, id});
                adj[v].push_back({u, id});
            }

            vector<int> tin(n, -1), low(n), isArt(n, 0);
            int timer = 0;

            function<void(int, int)> dfs = [&](int u, int parentEdge) {
                tin[u] = low[u] = timer++;
                int children = 0;
                for (auto [v, id] : adj[u]) {
                    if (id == parentEdge) continue;
                    if (tin[v] == -1) {
                        ++children;
                        dfs(v, id);
                        low[u] = min(low[u], low[v]);
                        if (parentEdge != -1 && low[v] >= tin[u]) isArt[u] = 1;
                    } else {
                        low[u] = min(low[u], tin[v]);
                    }
                }
                if (parentEdge == -1 && children > 1) isArt[u] = 1;
            };

            for (int i = 0; i < n; ++i) {
                if (tin[i] == -1) dfs(i, -1);
            }

            vector<int> ans;
            for (int i = 0; i < n; ++i) {
                if (isArt[i]) ans.push_back(i);
            }
            return ans;
        }
        """
    ),
)


UNDIRECTED_EULERIAN_PATH = join_cpp(
    CPP_HEADER,
    cpp(
        r"""
        vector<int> eulerianPath(int n, const vector<pair<int, int>>& edges) {
            if (n == 0) return {};
            if (edges.empty()) return {0};

            vector<vector<pair<int, int>>> adj(n);
            vector<int> degree(n, 0);
            for (int id = 0; id < static_cast<int>(edges.size()); ++id) {
                auto [u, v] = edges[id];
                adj[u].push_back({v, id});
                adj[v].push_back({u, id});
                ++degree[u];
                ++degree[v];
            }

            vector<int> odd;
            int start = -1;
            for (int i = 0; i < n; ++i) {
                if (degree[i] % 2 == 1) odd.push_back(i);
                if (degree[i] > 0 && start == -1) start = i;
            }
            if (!(odd.empty() || odd.size() == 2)) return {};
            if (odd.size() == 2) start = odd[0];

            vector<int> vis(n, 0);
            stack<int> st;
            st.push(start);
            vis[start] = 1;
            while (!st.empty()) {
                int u = st.top();
                st.pop();
                for (auto [v, _] : adj[u]) {
                    if (!vis[v]) {
                        vis[v] = 1;
                        st.push(v);
                    }
                }
            }
            for (int i = 0; i < n; ++i) {
                if (degree[i] > 0 && !vis[i]) return {};
            }

            vector<int> ptr(n, 0), path;
            vector<char> used(edges.size(), 0);
            function<void(int)> dfs = [&](int u) {
                while (ptr[u] < static_cast<int>(adj[u].size())) {
                    auto [v, id] = adj[u][ptr[u]++];
                    if (used[id]) continue;
                    used[id] = 1;
                    dfs(v);
                }
                path.push_back(u);
            };

            dfs(start);
            if (static_cast<int>(path.size()) != static_cast<int>(edges.size()) + 1) return {};
            reverse(path.begin(), path.end());
            return path;
        }
        """
    ),
)


UNDIRECTED_EULERIAN_CONDITION = join_cpp(
    CPP_HEADER,
    cpp(
        r"""
        bool hasEulerianPath(int n, const vector<vector<int>>& adj) {
            int odd = 0;
            int start = -1;
            for (int i = 0; i < n; ++i) {
                if (adj[i].size() % 2 == 1) ++odd;
                if (!adj[i].empty() && start == -1) start = i;
            }

            if (start == -1) return true;

            vector<int> vis(n, 0);
            stack<int> st;
            st.push(start);
            vis[start] = 1;
            while (!st.empty()) {
                int u = st.top();
                st.pop();
                for (int v : adj[u]) {
                    if (vis[v]) continue;
                    vis[v] = 1;
                    st.push(v);
                }
            }

            for (int i = 0; i < n; ++i) {
                if (!adj[i].empty() && !vis[i]) return false;
            }
            return odd == 0 || odd == 2;
        }
        """
    ),
)


LCA_BINARY_LIFTING = join_cpp(
    CPP_HEADER,
    cpp(
        r"""
        class LCA {
            int log_;
            vector<int> depth;
            vector<vector<int>> up;

            void dfs(int u, int parent, const vector<vector<int>>& adj) {
                up[u][0] = parent;
                for (int j = 1; j < log_; ++j) {
                    up[u][j] = up[up[u][j - 1]][j - 1];
                }
                for (int v : adj[u]) {
                    if (v == parent) continue;
                    depth[v] = depth[u] + 1;
                    dfs(v, u, adj);
                }
            }

           public:
            explicit LCA(const vector<vector<int>>& adj, int root = 0) {
                int n = static_cast<int>(adj.size());
                log_ = 1;
                while ((1LL << log_) <= max(1, n)) ++log_;
                depth.assign(n, 0);
                up.assign(n, vector<int>(log_, root));
                if (n > 0) dfs(root, root, adj);
            }

            int query(int a, int b) const {
                if (depth[a] < depth[b]) swap(a, b);
                int diff = depth[a] - depth[b];
                for (int j = 0; j < log_; ++j) {
                    if (diff & (1 << j)) a = up[a][j];
                }
                if (a == b) return a;
                for (int j = log_ - 1; j >= 0; --j) {
                    if (up[a][j] != up[b][j]) {
                        a = up[a][j];
                        b = up[b][j];
                    }
                }
                return up[a][0];
            }
        };
        """
    ),
)


BRIDGE_TREE = join_cpp(
    CPP_HEADER,
    cpp(
        r"""
        struct BridgeTree {
            vector<int> component;
            vector<vector<int>> tree;
        };

        BridgeTree buildBridgeTree(int n, const vector<pair<int, int>>& edges) {
            vector<vector<pair<int, int>>> adj(n);
            for (int id = 0; id < static_cast<int>(edges.size()); ++id) {
                auto [u, v] = edges[id];
                adj[u].push_back({v, id});
                adj[v].push_back({u, id});
            }

            vector<int> tin(n, -1), low(n), isBridge(edges.size(), 0);
            int timer = 0;
            function<void(int, int)> dfsBridge = [&](int u, int parentEdge) {
                tin[u] = low[u] = timer++;
                for (auto [v, id] : adj[u]) {
                    if (id == parentEdge) continue;
                    if (tin[v] == -1) {
                        dfsBridge(v, id);
                        low[u] = min(low[u], low[v]);
                        if (low[v] > tin[u]) isBridge[id] = 1;
                    } else {
                        low[u] = min(low[u], tin[v]);
                    }
                }
            };

            for (int i = 0; i < n; ++i) {
                if (tin[i] == -1) dfsBridge(i, -1);
            }

            vector<int> component(n, -1);
            int components = 0;
            function<void(int)> dfsComponent = [&](int u) {
                component[u] = components;
                for (auto [v, id] : adj[u]) {
                    if (component[v] == -1 && !isBridge[id]) dfsComponent(v);
                }
            };

            for (int i = 0; i < n; ++i) {
                if (component[i] == -1) {
                    dfsComponent(i);
                    ++components;
                }
            }

            vector<vector<int>> tree(components);
            for (int id = 0; id < static_cast<int>(edges.size()); ++id) {
                if (!isBridge[id]) continue;
                auto [u, v] = edges[id];
                int cu = component[u];
                int cv = component[v];
                tree[cu].push_back(cv);
                tree[cv].push_back(cu);
            }

            return {component, tree};
        }
        """
    ),
)


KRUSKAL_RECONSTRUCTION_TREE = join_cpp(
    CPP_HEADER,
    cpp(
        r"""
        struct Edge {
            int u, v, w;
        };

        struct KruskalReconstructionForest {
            vector<vector<int>> tree;
            vector<int> mergeWeight;
            vector<int> roots;
        };

        KruskalReconstructionForest buildKruskalTree(int n, vector<Edge> edges) {
            if (n == 0) return {};

            sort(edges.begin(), edges.end(),
                 [](const Edge& a, const Edge& b) { return a.w < b.w; });

            vector<vector<int>> tree(2 * n);
            vector<int> mergeWeight(2 * n, 0);
            vector<int> parent(2 * n);
            iota(parent.begin(), parent.end(), 0);

            function<int(int)> find = [&](int x) {
                return parent[x] == x ? x : parent[x] = find(parent[x]);
            };

            int next = n;
            for (const auto& e : edges) {
                int a = find(e.u);
                int b = find(e.v);
                if (a == b) continue;
                tree[next].push_back(a);
                tree[next].push_back(b);
                mergeWeight[next] = e.w;
                parent[a] = next;
                parent[b] = next;
                parent[next] = next;
                ++next;
            }

            vector<int> roots;
            vector<int> seen(next, 0);
            for (int i = 0; i < n; ++i) {
                int root = find(i);
                if (!seen[root]) {
                    seen[root] = 1;
                    roots.push_back(root);
                }
            }

            tree.resize(next);
            mergeWeight.resize(next);
            return {tree, mergeWeight, roots};
        }
        """
    ),
)


MAXIMUM_XOR_PATH = join_cpp(
    CPP_HEADER,
    cpp(
        r"""
        class XorBasis {
            array<long long, 61> basis{};

           public:
            void add(long long value) {
                for (int bit = 60; bit >= 0; --bit) {
                    if (((value >> bit) & 1LL) == 0) continue;
                    if (basis[bit] == 0) {
                        basis[bit] = value;
                        return;
                    }
                    value ^= basis[bit];
                }
            }

            long long maximize(long long value) const {
                for (int bit = 60; bit >= 0; --bit) {
                    value = max(value, value ^ basis[bit]);
                }
                return value;
            }
        };

        long long maxXorPath(int n, const vector<tuple<int, int, int>>& edges, int src, int dest) {
            struct Edge {
                int to, w, id;
            };

            vector<vector<Edge>> adj(n);
            for (int id = 0; id < static_cast<int>(edges.size()); ++id) {
                auto [u, v, w] = edges[id];
                adj[u].push_back({v, w, id});
                adj[v].push_back({u, w, id});
            }

            vector<int> vis(n, 0);
            vector<long long> xorTo(n, 0);
            XorBasis basis;

            function<void(int, int)> dfs = [&](int u, int parentEdge) {
                vis[u] = 1;
                for (const auto& e : adj[u]) {
                    if (e.id == parentEdge) continue;
                    if (!vis[e.to]) {
                        xorTo[e.to] = xorTo[u] ^ e.w;
                        dfs(e.to, e.id);
                    } else {
                        basis.add(xorTo[u] ^ xorTo[e.to] ^ e.w);
                    }
                }
            };

            dfs(src, -1);
            if (!vis[dest]) return -1;
            return basis.maximize(xorTo[dest]);
        }
        """
    ),
)


CHEAPEST_FLIGHT_WITH_K_STOPS = join_cpp(
    CPP_HEADER,
    cpp(
        r"""
        struct Flight {
            int from, to, price;
        };

        int findCheapestPrice(int n, const vector<Flight>& flights, int src, int dst, int k) {
            const int INF = 1e9;
            vector<int> dist(n, INF);
            dist[src] = 0;

            for (int edgesUsed = 0; edgesUsed <= k; ++edgesUsed) {
                vector<int> next = dist;
                for (const auto& flight : flights) {
                    if (dist[flight.from] == INF) continue;
                    next[flight.to] = min(next[flight.to], dist[flight.from] + flight.price);
                }
                dist.swap(next);
            }

            return dist[dst] == INF ? -1 : dist[dst];
        }
        """
    ),
)


SHORTEST_PATH_VISITING_ALL_NODES = join_cpp(
    CPP_HEADER,
    cpp(
        r"""
        int shortestPathLength(const vector<vector<int>>& adj) {
            int n = static_cast<int>(adj.size());
            if (n <= 1) return 0;

            int fullMask = (1 << n) - 1;
            vector<vector<int>> dist(n, vector<int>(1 << n, -1));
            queue<pair<int, int>> q;

            for (int i = 0; i < n; ++i) {
                dist[i][1 << i] = 0;
                q.push({i, 1 << i});
            }

            while (!q.empty()) {
                auto [u, mask] = q.front();
                q.pop();
                if (mask == fullMask) return dist[u][mask];

                for (int v : adj[u]) {
                    int nextMask = mask | (1 << v);
                    if (dist[v][nextMask] != -1) continue;
                    dist[v][nextMask] = dist[u][mask] + 1;
                    q.push({v, nextMask});
                }
            }

            return -1;
        }
        """
    ),
)


DIRECTED_EULERIAN_PATH = join_cpp(
    CPP_HEADER,
    cpp(
        r"""
        vector<int> eulerianPath(int n, const vector<pair<int, int>>& edges) {
            if (n == 0) return {};
            if (edges.empty()) return {0};

            vector<vector<int>> adj(n), undirected(n);
            vector<int> indegree(n, 0), outdegree(n, 0), ptr(n, 0);
            for (const auto& [u, v] : edges) {
                adj[u].push_back(v);
                undirected[u].push_back(v);
                undirected[v].push_back(u);
                ++outdegree[u];
                ++indegree[v];
            }

            int start = -1, end = -1;
            for (int i = 0; i < n; ++i) {
                int diff = outdegree[i] - indegree[i];
                if (abs(diff) > 1) return {};
                if (diff == 1) {
                    if (start != -1) return {};
                    start = i;
                } else if (diff == -1) {
                    if (end != -1) return {};
                    end = i;
                }
            }
            if ((start == -1) != (end == -1)) return {};

            if (start == -1) {
                for (int i = 0; i < n; ++i) {
                    if (outdegree[i] > 0) {
                        start = i;
                        break;
                    }
                }
            }

            vector<int> vis(n, 0);
            stack<int> st;
            st.push(start);
            vis[start] = 1;
            while (!st.empty()) {
                int u = st.top();
                st.pop();
                for (int v : undirected[u]) {
                    if (vis[v]) continue;
                    vis[v] = 1;
                    st.push(v);
                }
            }
            for (int i = 0; i < n; ++i) {
                if ((indegree[i] + outdegree[i] > 0) && !vis[i]) return {};
            }

            vector<int> path;
            function<void(int)> dfs = [&](int u) {
                while (ptr[u] < static_cast<int>(adj[u].size())) {
                    dfs(adj[u][ptr[u]++]);
                }
                path.push_back(u);
            };

            dfs(start);
            if (static_cast<int>(path.size()) != static_cast<int>(edges.size()) + 1) return {};
            reverse(path.begin(), path.end());
            return path;
        }
        """
    ),
)


DIRECTED_EULERIAN_CIRCUIT_CONDITION = join_cpp(
    CPP_HEADER,
    cpp(
        r"""
        bool hasEulerianCircuit(int n, const vector<pair<int, int>>& edges) {
            vector<vector<int>> undirected(n);
            vector<int> indegree(n, 0), outdegree(n, 0);
            for (const auto& [u, v] : edges) {
                ++outdegree[u];
                ++indegree[v];
                undirected[u].push_back(v);
                undirected[v].push_back(u);
            }

            int start = -1;
            for (int i = 0; i < n; ++i) {
                if (indegree[i] != outdegree[i]) return false;
                if (indegree[i] + outdegree[i] > 0 && start == -1) start = i;
            }
            if (start == -1) return true;

            vector<int> vis(n, 0);
            stack<int> st;
            st.push(start);
            vis[start] = 1;
            while (!st.empty()) {
                int u = st.top();
                st.pop();
                for (int v : undirected[u]) {
                    if (vis[v]) continue;
                    vis[v] = 1;
                    st.push(v);
                }
            }

            for (int i = 0; i < n; ++i) {
                if (indegree[i] + outdegree[i] > 0 && !vis[i]) return false;
            }
            return true;
        }
        """
    ),
)


SHORTEST_PATH_WITH_DISCOUNT = join_cpp(
    CPP_HEADER,
    cpp(
        r"""
        long long shortestWithDiscount(int n, const vector<vector<pair<int, int>>>& adj, int src, int dest) {
            const long long INF = LLONG_MAX / 4;
            vector<vector<long long>> dist(n, vector<long long>(2, INF));
            using State = tuple<long long, int, int>;
            priority_queue<State, vector<State>, greater<State>> pq;

            dist[src][0] = 0;
            pq.push({0, src, 0});

            while (!pq.empty()) {
                auto [d, u, used] = pq.top();
                pq.pop();
                if (d != dist[u][used]) continue;

                for (auto [v, w] : adj[u]) {
                    if (d + w < dist[v][used]) {
                        dist[v][used] = d + w;
                        pq.push({dist[v][used], v, used});
                    }
                    if (used == 0 && d < dist[v][1]) {
                        dist[v][1] = d;
                        pq.push({d, v, 1});
                    }
                }
            }

            long long ans = min(dist[dest][0], dist[dest][1]);
            return ans == INF ? -1 : ans;
        }
        """
    ),
)


FORD_FULKERSON = join_cpp(
    CPP_HEADER,
    cpp(
        r"""
        class FordFulkerson {
            vector<vector<int>> adj;
            vector<vector<long long>> capacity;
            vector<int> visited;

            long long dfs(int u, int t, long long flow) {
                if (u == t) return flow;
                visited[u] = 1;
                for (int v : adj[u]) {
                    if (visited[v] || capacity[u][v] == 0) continue;
                    long long pushed = dfs(v, t, min(flow, capacity[u][v]));
                    if (pushed == 0) continue;
                    capacity[u][v] -= pushed;
                    capacity[v][u] += pushed;
                    return pushed;
                }
                return 0;
            }

           public:
            explicit FordFulkerson(int n)
                : adj(n), capacity(n, vector<long long>(n, 0)), visited(n, 0) {}

            void addEdge(int u, int v, long long cap) {
                if (capacity[u][v] == 0 && capacity[v][u] == 0) {
                    adj[u].push_back(v);
                    adj[v].push_back(u);
                }
                capacity[u][v] += cap;
            }

            long long maxFlow(int s, int t) {
                long long flow = 0;
                while (true) {
                    fill(visited.begin(), visited.end(), 0);
                    long long pushed = dfs(s, t, LLONG_MAX);
                    if (pushed == 0) break;
                    flow += pushed;
                }
                return flow;
            }
        };
        """
    ),
)


EDMONDS_KARP = join_cpp(
    CPP_HEADER,
    cpp(
        r"""
        class EdmondsKarp {
            vector<vector<int>> adj;
            vector<vector<long long>> capacity;

           public:
            explicit EdmondsKarp(int n) : adj(n), capacity(n, vector<long long>(n, 0)) {}

            void addEdge(int u, int v, long long cap) {
                if (capacity[u][v] == 0 && capacity[v][u] == 0) {
                    adj[u].push_back(v);
                    adj[v].push_back(u);
                }
                capacity[u][v] += cap;
            }

            long long maxFlow(int s, int t) {
                long long flow = 0;
                vector<int> parent(adj.size());

                while (true) {
                    fill(parent.begin(), parent.end(), -1);
                    queue<int> q;
                    q.push(s);
                    parent[s] = s;

                    while (!q.empty() && parent[t] == -1) {
                        int u = q.front();
                        q.pop();
                        for (int v : adj[u]) {
                            if (parent[v] != -1 || capacity[u][v] == 0) continue;
                            parent[v] = u;
                            q.push(v);
                        }
                    }

                    if (parent[t] == -1) break;

                    long long pushed = LLONG_MAX;
                    for (int v = t; v != s; v = parent[v]) {
                        pushed = min(pushed, capacity[parent[v]][v]);
                    }
                    for (int v = t; v != s; v = parent[v]) {
                        capacity[parent[v]][v] -= pushed;
                        capacity[v][parent[v]] += pushed;
                    }
                    flow += pushed;
                }

                return flow;
            }
        };
        """
    ),
)


MINIMUM_CUT = join_cpp(
    CPP_HEADER,
    DINIC_HELPER,
    cpp(
        r"""
        vector<pair<int, int>> minCutEdges(int n, const vector<tuple<int, int, long long>>& edges, int s, int t) {
            Dinic dinic(n);
            for (const auto& [u, v, cap] : edges) dinic.addEdge(u, v, cap);
            dinic.maxFlow(s, t);

            vector<int> reachable(n, 0);
            queue<int> q;
            q.push(s);
            reachable[s] = 1;
            while (!q.empty()) {
                int u = q.front();
                q.pop();
                for (const auto& e : dinic.graph()[u]) {
                    if (e.cap > 0 && !reachable[e.to]) {
                        reachable[e.to] = 1;
                        q.push(e.to);
                    }
                }
            }

            vector<pair<int, int>> cut;
            for (const auto& [u, v, cap] : edges) {
                if (cap > 0 && reachable[u] && !reachable[v]) cut.push_back({u, v});
            }
            return cut;
        }
        """
    ),
)


BIPARTITE_MATCHING_MAX_FLOW = join_cpp(
    CPP_HEADER,
    DINIC_HELPER,
    cpp(
        r"""
        int maxBipartiteMatching(int leftSize, int rightSize, const vector<pair<int, int>>& edges) {
            int source = leftSize + rightSize;
            int sink = source + 1;
            Dinic dinic(leftSize + rightSize + 2);

            for (int u = 0; u < leftSize; ++u) dinic.addEdge(source, u, 1);
            for (const auto& [u, v] : edges) dinic.addEdge(u, leftSize + v, 1);
            for (int v = 0; v < rightSize; ++v) dinic.addEdge(leftSize + v, sink, 1);

            return static_cast<int>(dinic.maxFlow(source, sink));
        }
        """
    ),
)


EXTRACT_BIPARTITE_MATCHING = join_cpp(
    CPP_HEADER,
    DINIC_HELPER,
    cpp(
        r"""
        vector<pair<int, int>> extractMatching(int leftSize, int rightSize, const vector<pair<int, int>>& edges) {
            int source = leftSize + rightSize;
            int sink = source + 1;
            Dinic dinic(leftSize + rightSize + 2);

            for (int u = 0; u < leftSize; ++u) dinic.addEdge(source, u, 1);
            for (const auto& [u, v] : edges) dinic.addEdge(u, leftSize + v, 1);
            for (int v = 0; v < rightSize; ++v) dinic.addEdge(leftSize + v, sink, 1);

            dinic.maxFlow(source, sink);

            vector<pair<int, int>> matching;
            for (int u = 0; u < leftSize; ++u) {
                for (const auto& e : dinic.graph()[u]) {
                    if (e.to >= leftSize && e.to < leftSize + rightSize && e.cap == 0) {
                        matching.push_back({u, e.to - leftSize});
                    }
                }
            }
            return matching;
        }
        """
    ),
)


KUHN_MATCHING = join_cpp(
    CPP_HEADER,
    cpp(
        r"""
        bool tryKuhn(int u, const vector<vector<int>>& adj, vector<int>& matchR, vector<int>& seen) {
            for (int v : adj[u]) {
                if (seen[v]) continue;
                seen[v] = 1;
                if (matchR[v] == -1 || tryKuhn(matchR[v], adj, matchR, seen)) {
                    matchR[v] = u;
                    return true;
                }
            }
            return false;
        }

        int maximumMatching(int leftSize, int rightSize, const vector<vector<int>>& adj) {
            vector<int> matchR(rightSize, -1);
            int matching = 0;
            for (int u = 0; u < leftSize; ++u) {
                vector<int> seen(rightSize, 0);
                if (tryKuhn(u, adj, matchR, seen)) ++matching;
            }
            return matching;
        }
        """
    ),
)


MINIMUM_VERTEX_COVER = join_cpp(
    CPP_HEADER,
    HOPCROFT_KARP_HELPER,
    cpp(
        r"""
        pair<vector<int>, vector<int>> minimumVertexCover(int leftSize, int rightSize,
                                                          const vector<vector<int>>& adj) {
            HopcroftKarp hk(leftSize, rightSize, adj);
            hk.maxMatching();

            vector<int> visLeft(leftSize, 0), visRight(rightSize, 0);
            queue<int> q;
            for (int u = 0; u < leftSize; ++u) {
                if (hk.leftMatch()[u] == -1) {
                    visLeft[u] = 1;
                    q.push(u);
                }
            }

            while (!q.empty()) {
                int u = q.front();
                q.pop();
                for (int v : adj[u]) {
                    if (v == hk.leftMatch()[u] || visRight[v]) continue;
                    visRight[v] = 1;
                    int matched = hk.rightMatch()[v];
                    if (matched != -1 && !visLeft[matched]) {
                        visLeft[matched] = 1;
                        q.push(matched);
                    }
                }
            }

            vector<int> leftCover, rightCover;
            for (int u = 0; u < leftSize; ++u) {
                if (!visLeft[u]) leftCover.push_back(u);
            }
            for (int v = 0; v < rightSize; ++v) {
                if (visRight[v]) rightCover.push_back(v);
            }
            return {leftCover, rightCover};
        }
        """
    ),
)


MAXIMUM_INDEPENDENT_SET = join_cpp(
    CPP_HEADER,
    HOPCROFT_KARP_HELPER,
    cpp(
        r"""
        pair<vector<int>, vector<int>> maximumIndependentSet(int leftSize, int rightSize,
                                                             const vector<vector<int>>& adj) {
            HopcroftKarp hk(leftSize, rightSize, adj);
            hk.maxMatching();

            vector<int> visLeft(leftSize, 0), visRight(rightSize, 0);
            queue<int> q;
            for (int u = 0; u < leftSize; ++u) {
                if (hk.leftMatch()[u] == -1) {
                    visLeft[u] = 1;
                    q.push(u);
                }
            }

            while (!q.empty()) {
                int u = q.front();
                q.pop();
                for (int v : adj[u]) {
                    if (v == hk.leftMatch()[u] || visRight[v]) continue;
                    visRight[v] = 1;
                    int matched = hk.rightMatch()[v];
                    if (matched != -1 && !visLeft[matched]) {
                        visLeft[matched] = 1;
                        q.push(matched);
                    }
                }
            }

            vector<int> leftSet, rightSet;
            for (int u = 0; u < leftSize; ++u) {
                if (visLeft[u]) leftSet.push_back(u);
            }
            for (int v = 0; v < rightSize; ++v) {
                if (!visRight[v]) rightSet.push_back(v);
            }
            return {leftSet, rightSet};
        }
        """
    ),
)


MINIMUM_PATH_COVER_DAG = join_cpp(
    CPP_HEADER,
    HOPCROFT_KARP_HELPER,
    cpp(
        r"""
        int minimumPathCover(int n, const vector<vector<int>>& dag) {
            vector<vector<int>> bipartite(n);
            for (int u = 0; u < n; ++u) {
                for (int v : dag[u]) bipartite[u].push_back(v);
            }
            HopcroftKarp hk(n, n, bipartite);
            return n - hk.maxMatching();
        }
        """
    ),
)


FEASIBLE_CIRCULATION = join_cpp(
    CPP_HEADER,
    DINIC_HELPER,
    cpp(
        r"""
        struct Edge {
            int from, to;
            long long low, high;
        };

        bool feasibleCirculation(int n, const vector<Edge>& edges) {
            int superSource = n;
            int superSink = n + 1;
            Dinic dinic(n + 2);
            vector<long long> demand(n, 0);

            for (const auto& e : edges) {
                if (e.low > e.high) {
                    throw invalid_argument("edge has low > high");
                }
                dinic.addEdge(e.from, e.to, e.high - e.low);
                demand[e.from] -= e.low;
                demand[e.to] += e.low;
            }

            long long required = 0;
            for (int v = 0; v < n; ++v) {
                if (demand[v] > 0) {
                    dinic.addEdge(superSource, v, demand[v]);
                    required += demand[v];
                } else if (demand[v] < 0) {
                    dinic.addEdge(v, superSink, -demand[v]);
                }
            }

            return dinic.maxFlow(superSource, superSink) == required;
        }
        """
    ),
)


MAX_FLOW_WITH_VERTEX_CAPACITIES = join_cpp(
    CPP_HEADER,
    DINIC_HELPER,
    cpp(
        r"""
        long long maxFlowWithVertexCapacities(
            int n, const vector<long long>& vertexCapacity,
            const vector<tuple<int, int, long long>>& edges, int s, int t
        ) {
            const long long INF = LLONG_MAX / 4;
            auto in = [](int u) { return 2 * u; };
            auto out = [](int u) { return 2 * u + 1; };

            Dinic dinic(2 * n);
            for (int u = 0; u < n; ++u) {
                long long cap = (u == s || u == t) ? INF : vertexCapacity[u];
                dinic.addEdge(in(u), out(u), cap);
            }
            for (const auto& [u, v, cap] : edges) {
                dinic.addEdge(out(u), in(v), cap);
            }
            return dinic.maxFlow(out(s), in(t));
        }
        """
    ),
)


EDGE_DISJOINT_PATHS = join_cpp(
    CPP_HEADER,
    DINIC_HELPER,
    cpp(
        r"""
        int maxEdgeDisjointPaths(int n, const vector<pair<int, int>>& edges, int s, int t) {
            Dinic dinic(n);
            for (const auto& [u, v] : edges) dinic.addEdge(u, v, 1);
            return static_cast<int>(dinic.maxFlow(s, t));
        }
        """
    ),
)


ASSIGNMENT_PROBLEM = join_cpp(
    CPP_HEADER,
    MIN_COST_MAX_FLOW_POTENTIALS,
    cpp(
        r"""
        pair<long long, vector<int>> assignment(const vector<vector<int>>& cost) {
            int n = static_cast<int>(cost.size());
            int source = 2 * n;
            int sink = source + 1;

            MinCostMaxFlow mcmf(2 * n + 2);
            for (int i = 0; i < n; ++i) {
                mcmf.addEdge(source, i, 1, 0);
                mcmf.addEdge(n + i, sink, 1, 0);
            }
            for (int i = 0; i < n; ++i) {
                for (int j = 0; j < n; ++j) {
                    mcmf.addEdge(i, n + j, 1, cost[i][j]);
                }
            }

            auto [flow, minCost] = mcmf.minCostMaxFlow(source, sink);
            if (flow != n) return {-1, {}};

            vector<int> jobForWorker(n, -1);
            for (int i = 0; i < n; ++i) {
                for (const auto& e : mcmf.graph()[i]) {
                    if (e.to >= n && e.to < 2 * n && e.cap == 0) {
                        jobForWorker[i] = e.to - n;
                    }
                }
            }
            return {minCost, jobForWorker};
        }
        """
    ),
)


EXACTLY_K_FLOW = join_cpp(
    CPP_HEADER,
    DINIC_HELPER,
    cpp(
        r"""
        bool canSendExactlyKUnits(int n, const vector<tuple<int, int, long long>>& edges, int s, int t,
                                  long long k) {
            if (k < 0) throw invalid_argument("k must be non-negative");
            Dinic dinic(n);
            for (const auto& [u, v, cap] : edges) dinic.addEdge(u, v, cap);
            return dinic.maxFlow(s, t) >= k;
        }
        """
    ),
)


DSA_CODE_OVERRIDES = {
    "17-dsu-4-largest-connected-component": [LARGEST_COMPONENT],
    "17-dsu-6-kruskals-mst-using-dsu": [KRUSKAL_MST],
    "17-dsu-12-offline-dynamic-connectivity": [OFFLINE_DYNAMIC_CONNECTIVITY],
    "11-graph-16-negative-cycle-detection-floyd-warshall": [NEGATIVE_CYCLE_FLOYD_WARSHALL],
    "11-graph-19-minimum-spanning-tree-kruskals-algorithm": [KRUSKAL_MST],
    "11-graph-23-bridges-in-undirected-graph": [BRIDGES_WITH_PARALLEL_EDGES],
    "11-graph-24-articulation-points": [ARTICULATION_POINTS_WITH_PARALLEL_EDGES],
    "11-graph-25-eulerian-path-circuit-undirected-graph": [UNDIRECTED_EULERIAN_PATH],
    "11-graph-26-eulerian-path-condition": [UNDIRECTED_EULERIAN_CONDITION],
    "11-graph-31-max-flow-dinics-algorithm": [join_cpp(CPP_HEADER, DINIC_HELPER)],
    "11-graph-33-binary-lifting-on-graph-tree-lca": [LCA_BINARY_LIFTING],
    "11-graph-37-find-bridges-build-bridge-tree": [BRIDGE_TREE],
    "11-graph-38-dsu-based-kruskal-reconstruction-tree": [KRUSKAL_RECONSTRUCTION_TREE],
    "11-graph-40-maximum-xor-path-bitwise-graph-technique": [MAXIMUM_XOR_PATH],
    "11-graph-46-cheapest-flights-within-k-stops": [CHEAPEST_FLIGHT_WITH_K_STOPS],
    "11-graph-57-shortest-path-visiting-every-node": [SHORTEST_PATH_VISITING_ALL_NODES],
    "21-graph-advanced-5-eulerian-path-circuit": [DIRECTED_EULERIAN_PATH],
    "21-graph-advanced-6-eulerian-circuit-directed-graph": [DIRECTED_EULERIAN_CIRCUIT_CONDITION],
    "21-graph-advanced-9-2-sat": [join_cpp(CPP_HEADER, TWO_SAT_HELPER)],
    "21-graph-advanced-12-offline-dynamic-connectivity-dsu": [OFFLINE_DYNAMIC_CONNECTIVITY],
    "21-graph-advanced-16-shortest-path-with-state": [SHORTEST_PATH_WITH_DISCOUNT],
    "24-network-flow-1-max-flow-ford-fulkerson": [FORD_FULKERSON],
    "24-network-flow-2-edmonds-karp-algorithm": [EDMONDS_KARP],
    "24-network-flow-3-dinics-algorithm": [join_cpp(CPP_HEADER, DINIC_HELPER)],
    "24-network-flow-4-minimum-cut": [MINIMUM_CUT],
    "24-network-flow-5-bipartite-matching-using-max-flow": [BIPARTITE_MATCHING_MAX_FLOW],
    "24-network-flow-6-extract-the-actual-bipartite-matching": [EXTRACT_BIPARTITE_MATCHING],
    "24-network-flow-7-maximum-bipartite-matching-kuhns-algorithm": [KUHN_MATCHING],
    "24-network-flow-8-hopcroft-karp": [join_cpp(CPP_HEADER, HOPCROFT_KARP_HELPER)],
    "24-network-flow-9-minimum-vertex-cover-in-bipartite-graph": [MINIMUM_VERTEX_COVER],
    "24-network-flow-10-maximum-independent-set-in-bipartite-graph": [MAXIMUM_INDEPENDENT_SET],
    "24-network-flow-11-minimum-path-cover-in-dag": [MINIMUM_PATH_COVER_DAG],
    "24-network-flow-12-minimum-cost-maximum-flow": [join_cpp(CPP_HEADER, MIN_COST_MAX_FLOW_SPFA)],
    "24-network-flow-13-min-cost-max-flow-with-potentials": [join_cpp(CPP_HEADER, MIN_COST_MAX_FLOW_POTENTIALS)],
    "24-network-flow-14-circulation-with-lower-bounds": [FEASIBLE_CIRCULATION],
    "24-network-flow-16-maximum-flow-with-vertex-capacities": [MAX_FLOW_WITH_VERTEX_CAPACITIES],
    "24-network-flow-17-edge-disjoint-paths": [EDGE_DISJOINT_PATHS],
    "24-network-flow-20-assignment-problem": [ASSIGNMENT_PROBLEM],
    "24-network-flow-21-can-we-send-exactly-k-units-of-flow": [EXACTLY_K_FLOW],
}

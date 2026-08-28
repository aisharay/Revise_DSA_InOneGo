"""Corrected C++17 overrides for foundational DSA chapters."""

from __future__ import annotations

from textwrap import dedent


def cpp(source: str) -> str:
    return dedent(source).strip()


def blocks(*sources: str) -> list[str]:
    return [cpp(source) for source in sources]


DSA_CODE_OVERRIDES = {
    "3-searching-and-sorting-4-first-and-last-occurrence": blocks(
        r"""
        pair<int, int> firstLast(const vector<int>& arr, int target) {
            int n = static_cast<int>(arr.size());
            int l = 0;
            int r = n;
            while (l < r) {
                int mid = l + (r - l) / 2;
                if (arr[mid] < target) {
                    l = mid + 1;
                } else {
                    r = mid;
                }
            }
            int first = l;
            if (first == n || arr[first] != target) return {-1, -1};

            l = first;
            r = n;
            while (l < r) {
                int mid = l + (r - l) / 2;
                if (arr[mid] <= target) {
                    l = mid + 1;
                } else {
                    r = mid;
                }
            }
            return {first, l - 1};
        }
        """,
    ),
    "3-searching-and-sorting-5-search-insert-position": blocks(
        r"""
        int searchInsert(const vector<int>& arr, int target) {
            int l = 0;
            int r = static_cast<int>(arr.size());
            while (l < r) {
                int mid = l + (r - l) / 2;
                if (arr[mid] < target) {
                    l = mid + 1;
                } else {
                    r = mid;
                }
            }
            return l;
        }
        """,
    ),
    "3-searching-and-sorting-15-integer-square-root": blocks(
        r"""
        long long integerSqrt(long long x) {
            if (x < 0) throw invalid_argument("x must be non-negative");
            long long l = 0;
            long long r = x;
            long long ans = 0;
            while (l <= r) {
                long long mid = l + (r - l) / 2;
                if (mid == 0 || mid <= x / mid) {
                    ans = mid;
                    l = mid + 1;
                } else {
                    r = mid - 1;
                }
            }
            return ans;
        }
        """,
    ),
    "3-searching-and-sorting-18-ternary-search": blocks(
        r"""
        template <class F>
        double ternarySearch(double l, double r, F f, bool findMinimum = true) {
            for (int iter = 0; iter < 200; iter++) {
                double m1 = l + (r - l) / 3.0;
                double m2 = r - (r - l) / 3.0;
                double f1 = f(m1);
                double f2 = f(m2);
                if (findMinimum ? (f1 <= f2) : (f1 >= f2)) {
                    r = m2;
                } else {
                    l = m1;
                }
            }
            return (l + r) / 2.0;
        }
        """,
    ),
    "3-searching-and-sorting-21-randomized-quick-sort": blocks(
        r"""
        int partitionArray(vector<int>& arr, int l, int r) {
            int pivot = arr[r];
            int i = l;
            for (int j = l; j < r; j++) {
                if (arr[j] <= pivot) {
                    swap(arr[i], arr[j]);
                    i++;
                }
            }
            swap(arr[i], arr[r]);
            return i;
        }

        int randomizedPartition(vector<int>& arr, int l, int r) {
            static mt19937 rng(random_device{}());
            uniform_int_distribution<int> dist(l, r);
            int pivotIndex = dist(rng);
            swap(arr[pivotIndex], arr[r]);
            return partitionArray(arr, l, r);
        }

        void randomizedQuickSort(vector<int>& arr, int l, int r) {
            if (l >= r) return;
            int p = randomizedPartition(arr, l, r);
            randomizedQuickSort(arr, l, p - 1);
            randomizedQuickSort(arr, p + 1, r);
        }
        """,
    ),
    "3-searching-and-sorting-23-quickselect-k-th-smallest": blocks(
        r"""
        int partitionArray(vector<int>& arr, int l, int r) {
            int pivot = arr[r];
            int i = l;
            for (int j = l; j < r; j++) {
                if (arr[j] <= pivot) {
                    swap(arr[i], arr[j]);
                    i++;
                }
            }
            swap(arr[i], arr[r]);
            return i;
        }

        int quickSelect(vector<int>& arr, int l, int r, int k) {
            while (l <= r) {
                int p = partitionArray(arr, l, r);
                if (p == k) return arr[p];
                if (p > k) {
                    r = p - 1;
                } else {
                    l = p + 1;
                }
            }
            return -1;
        }
        """,
        r"""
        int kthSmallest(vector<int>& arr, int k) {
            if (k < 1 || k > static_cast<int>(arr.size())) return -1;
            return quickSelect(arr, 0, static_cast<int>(arr.size()) - 1, k - 1);
        }
        """,
    ),
    "3-searching-and-sorting-24-nth-element": blocks(
        r"""
        int kthSmallest(vector<int>& arr, int k) {
            if (k < 1 || k > static_cast<int>(arr.size())) return -1;
            nth_element(arr.begin(), arr.begin() + (k - 1), arr.end());
            return arr[k - 1];
        }
        """,
    ),
    "3-searching-and-sorting-26-radix-sort": blocks(
        r"""
        void countingSortDigit(vector<int>& arr, long long exp) {
            int n = static_cast<int>(arr.size());
            vector<int> output(n);
            int cnt[10] = {};
            for (int x : arr) {
                int digit = static_cast<int>((x / exp) % 10);
                cnt[digit]++;
            }
            for (int i = 1; i < 10; i++) cnt[i] += cnt[i - 1];
            for (int i = n - 1; i >= 0; i--) {
                int digit = static_cast<int>((arr[i] / exp) % 10);
                output[cnt[digit] - 1] = arr[i];
                cnt[digit]--;
            }
            arr = output;
        }

        void radixSort(vector<int>& arr) {
            if (arr.empty()) return;
            int mx = 0;
            for (int x : arr) {
                if (x < 0) throw invalid_argument("radix sort expects non-negative integers");
                mx = max(mx, x);
            }
            for (long long exp = 1; mx / exp > 0; exp *= 10) {
                countingSortDigit(arr, exp);
            }
        }
        """,
    ),
    "3-searching-and-sorting-27-bucket-sort": blocks(
        r"""
        void bucketSort(vector<double>& arr) {
            int n = static_cast<int>(arr.size());
            if (n <= 1) return;

            auto [minIt, maxIt] = minmax_element(arr.begin(), arr.end());
            double mn = *minIt;
            double mx = *maxIt;
            if (mn == mx) return;

            vector<vector<double>> buckets(n);
            for (double x : arr) {
                int idx = static_cast<int>((x - mn) / (mx - mn) * (n - 1));
                idx = max(0, min(n - 1, idx));
                buckets[idx].push_back(x);
            }

            int pos = 0;
            for (auto& bucket : buckets) {
                sort(bucket.begin(), bucket.end());
                for (double x : bucket) {
                    arr[pos++] = x;
                }
            }
        }
        """,
    ),
    "3-searching-and-sorting-29-sort-by-custom-comparator": blocks(
        r"""
        void sortByCustomComparator(vector<pair<int, int>>& arr) {
            sort(arr.begin(), arr.end(), [](const pair<int, int>& a, const pair<int, int>& b) {
                if (a.first != b.first) return a.first < b.first;
                return a.second > b.second;
            });
        }
        """,
    ),
    "4-bit-algo-3-check-whether-the-i-th-bit-is-set": blocks(
        r"""
        bool isSet(unsigned int x, int i) {
            if (i < 0 || i >= 32) return false;
            return ((x >> i) & 1U) != 0;
        }
        """,
    ),
    "4-bit-algo-4-set-the-i-th-bit": blocks(
        r"""
        unsigned int setBit(unsigned int x, int i) {
            if (i < 0 || i >= 32) return x;
            return x | (1U << i);
        }
        """,
    ),
    "4-bit-algo-5-clear-the-i-th-bit": blocks(
        r"""
        unsigned int clearBit(unsigned int x, int i) {
            if (i < 0 || i >= 32) return x;
            return x & ~(1U << i);
        }
        """,
    ),
    "4-bit-algo-6-toggle-the-i-th-bit": blocks(
        r"""
        unsigned int toggleBit(unsigned int x, int i) {
            if (i < 0 || i >= 32) return x;
            return x ^ (1U << i);
        }
        """,
    ),
    "4-bit-algo-7-remove-the-lowest-set-bit": blocks(
        r"""
        unsigned int removeLowestSetBit(unsigned int x) {
            return x == 0 ? 0 : (x & (x - 1));
        }
        """,
    ),
    "4-bit-algo-8-get-the-lowest-set-bit": blocks(
        r"""
        unsigned int lowestSetBit(unsigned int x) {
            return x & (~x + 1U);
        }
        """,
    ),
    "4-bit-algo-12-two-unique-numbers": blocks(
        r"""
        pair<int, int> twoUniques(const vector<int>& arr) {
            int xorAll = 0;
            for (int x : arr) xorAll ^= x;

            unsigned int bit = static_cast<unsigned int>(xorAll) &
                               (0U - static_cast<unsigned int>(xorAll));
            int a = 0;
            int b = 0;
            for (int x : arr) {
                if ((static_cast<unsigned int>(x) & bit) != 0U) {
                    a ^= x;
                } else {
                    b ^= x;
                }
            }
            return {a, b};
        }
        """,
    ),
    "4-bit-algo-16-generate-all-subsets-using-bitmask": blocks(
        r"""
        vector<vector<int>> subsets(const vector<int>& arr) {
            int n = static_cast<int>(arr.size());
            if (n >= 63) throw invalid_argument("too many elements for bitmask enumeration");

            size_t total = 1ULL << n;
            vector<vector<int>> ans;
            ans.reserve(total);
            for (size_t mask = 0; mask < total; mask++) {
                vector<int> curr;
                for (int i = 0; i < n; i++) {
                    if ((mask & (1ULL << i)) != 0ULL) curr.push_back(arr[i]);
                }
                ans.push_back(curr);
            }
            return ans;
        }
        """,
    ),
    "4-bit-algo-19-enumerate-all-masks-by-number-of-set-bits": blocks(
        r"""
        template <class F>
        void processMasksByPopcount(int n, F process) {
            if (n < 0 || n >= 31) throw invalid_argument("n must be in [0, 30]");
            int total = 1 << n;
            for (int mask = 0; mask < total; mask++) {
                process(mask, __builtin_popcount(static_cast<unsigned int>(mask)));
            }
        }
        """,
    ),
    "4-bit-algo-20-assignment-problem-bitmask-dp": blocks(
        r"""
        long long assignmentCost(const vector<vector<int>>& cost) {
            int n = static_cast<int>(cost.size());
            if (n == 0) return 0;
            if (n > 20) throw invalid_argument("n must be <= 20 for bitmask DP");
            for (const auto& row : cost) {
                if (static_cast<int>(row.size()) != n) {
                    throw invalid_argument("cost matrix must be square");
                }
            }

            vector<long long> dp(1 << n, LLONG_MAX);
            dp[0] = 0;
            for (int mask = 0; mask < (1 << n); mask++) {
                int worker = __builtin_popcount(static_cast<unsigned int>(mask));
                if (worker == n || dp[mask] == LLONG_MAX) continue;
                for (int job = 0; job < n; job++) {
                    if ((mask & (1 << job)) == 0) {
                        int nextMask = mask | (1 << job);
                        dp[nextMask] = min(dp[nextMask], dp[mask] + cost[worker][job]);
                    }
                }
            }
            return dp[(1 << n) - 1];
        }
        """,
    ),
    "4-bit-algo-21-traveling-salesman-bitmask-dp": blocks(
        r"""
        long long travelingSalesman(const vector<vector<int>>& cost) {
            int n = static_cast<int>(cost.size());
            if (n == 0) return 0;
            if (n > 20) throw invalid_argument("n must be <= 20 for bitmask DP");
            for (const auto& row : cost) {
                if (static_cast<int>(row.size()) != n) {
                    throw invalid_argument("cost matrix must be square");
                }
            }

            const long long INF = LLONG_MAX / 4;
            vector<vector<long long>> dp(1 << n, vector<long long>(n, INF));
            dp[1][0] = 0;

            for (int mask = 1; mask < (1 << n); mask++) {
                if ((mask & 1) == 0) continue;
                for (int u = 0; u < n; u++) {
                    if ((mask & (1 << u)) == 0 || dp[mask][u] == INF) continue;
                    for (int v = 0; v < n; v++) {
                        if ((mask & (1 << v)) != 0) continue;
                        int nextMask = mask | (1 << v);
                        dp[nextMask][v] = min(dp[nextMask][v], dp[mask][u] + cost[u][v]);
                    }
                }
            }

            long long ans = INF;
            int fullMask = (1 << n) - 1;
            for (int u = 0; u < n; u++) {
                ans = min(ans, dp[fullMask][u] + cost[u][0]);
            }
            return ans;
        }
        """,
    ),
    "4-bit-algo-22-check-if-two-numbers-have-opposite-signs": blocks(
        r"""
        bool oppositeSigns(int a, int b) {
            if (a == 0 || b == 0) return false;
            return (a ^ b) < 0;
        }
        """,
    ),
    "4-bit-algo-25-gray-code": blocks(
        r"""
        vector<int> grayCode(int n) {
            if (n < 0 || n >= 31) throw invalid_argument("n must be in [0, 30]");
            int total = 1 << n;
            vector<int> ans;
            ans.reserve(total);
            for (int i = 0; i < total; i++) {
                ans.push_back(i ^ (i >> 1));
            }
            return ans;
        }
        """,
    ),
    "4-bit-algo-26-xor-of-range-l-r": blocks(
        r"""
        int xor1ToN(int n) {
            if (n <= 0) return 0;
            switch (n & 3) {
                case 0:
                    return n;
                case 1:
                    return 1;
                case 2:
                    return n + 1;
                default:
                    return 0;
            }
        }

        int xorRange(int l, int r) {
            if (l < 0 || r < 0) throw invalid_argument("range bounds must be non-negative");
            if (l > r) swap(l, r);
            return xor1ToN(r) ^ xor1ToN(l - 1);
        }
        """,
    ),
    "4-bit-algo-27-find-maximum-xor-pair": blocks(
        r"""
        int findMaximumXOR(const vector<int>& arr) {
            uint32_t ans = 0;
            uint32_t mask = 0;
            for (int bit = 31; bit >= 0; bit--) {
                mask |= (1U << bit);
                unordered_set<uint32_t> prefixes;
                for (int x : arr) prefixes.insert(static_cast<uint32_t>(x) & mask);

                uint32_t candidate = ans | (1U << bit);
                for (uint32_t prefix : prefixes) {
                    if (prefixes.count(prefix ^ candidate) != 0U) {
                        ans = candidate;
                        break;
                    }
                }
            }
            return static_cast<int>(ans);
        }
        """,
    ),
    "4-bit-algo-28-maximum-xor-using-binary-trie": blocks(
        r"""
        struct TrieNode {
            array<unique_ptr<TrieNode>, 2> child;
        };

        class BinaryTrie {
        public:
            BinaryTrie() : root(make_unique<TrieNode>()) {}

            void insert(uint32_t x) {
                TrieNode* node = root.get();
                for (int bit = 31; bit >= 0; bit--) {
                    int b = static_cast<int>((x >> bit) & 1U);
                    if (!node->child[b]) node->child[b] = make_unique<TrieNode>();
                    node = node->child[b].get();
                }
            }

            uint32_t getMaxXOR(uint32_t x) const {
                const TrieNode* node = root.get();
                uint32_t ans = 0;
                for (int bit = 31; bit >= 0; bit--) {
                    int b = static_cast<int>((x >> bit) & 1U);
                    int opposite = b ^ 1;
                    if (node->child[opposite]) {
                        ans |= (1U << bit);
                        node = node->child[opposite].get();
                    } else {
                        node = node->child[b].get();
                    }
                }
                return ans;
            }

        private:
            unique_ptr<TrieNode> root;
        };

        int findMaximumXOR(const vector<int>& arr) {
            if (arr.size() < 2) return 0;
            BinaryTrie trie;
            trie.insert(static_cast<uint32_t>(arr[0]));
            uint32_t best = 0;
            for (int i = 1; i < static_cast<int>(arr.size()); i++) {
                uint32_t x = static_cast<uint32_t>(arr[i]);
                best = max(best, trie.getMaxXOR(x));
                trie.insert(x);
            }
            return static_cast<int>(best);
        }
        """,
    ),
    "4-bit-algo-29-maximum-xor-subarray": blocks(
        r"""
        struct Node {
            array<unique_ptr<Node>, 2> child;
        };

        void insert(Node& root, uint32_t x) {
            Node* curr = &root;
            for (int bit = 31; bit >= 0; bit--) {
                int b = static_cast<int>((x >> bit) & 1U);
                if (!curr->child[b]) curr->child[b] = make_unique<Node>();
                curr = curr->child[b].get();
            }
        }

        uint32_t query(const Node& root, uint32_t x) {
            const Node* curr = &root;
            uint32_t ans = 0;
            for (int bit = 31; bit >= 0; bit--) {
                int b = static_cast<int>((x >> bit) & 1U);
                int want = b ^ 1;
                if (curr->child[want]) {
                    ans |= (1U << bit);
                    curr = curr->child[want].get();
                } else {
                    curr = curr->child[b].get();
                }
            }
            return ans;
        }

        int maxXorSubarray(const vector<int>& arr) {
            Node root;
            insert(root, 0);
            uint32_t prefix = 0;
            uint32_t ans = 0;
            for (int x : arr) {
                prefix ^= static_cast<uint32_t>(x);
                ans = max(ans, query(root, prefix));
                insert(root, prefix);
            }
            return static_cast<int>(ans);
        }
        """,
    ),
    "4-bit-algo-key-transformation": blocks(
        r"""
        int subarrayXOR(const vector<int>& prefix, int l, int r) {
            return prefix[r] ^ (l == 0 ? 0 : prefix[l - 1]);
        }
        """,
    ),
    "4-bit-algo-30-sos-dp-sum-over-subsets": blocks(
        r"""
        void SOS(vector<int>& dp, int n) {
            if (n < 0 || n >= 31) throw invalid_argument("n must be in [0, 30]");
            if (static_cast<int>(dp.size()) != (1 << n)) {
                throw invalid_argument("dp must contain exactly 2^n values");
            }
            for (int bit = 0; bit < n; bit++) {
                for (int mask = 0; mask < (1 << n); mask++) {
                    if ((mask & (1 << bit)) != 0) {
                        dp[mask] += dp[mask ^ (1 << bit)];
                    }
                }
            }
        }
        """,
    ),
    "4-bit-algo-core-idea-2": [],
    "4-bit-algo-31-subset-convolution-o3n-submask-dp": blocks(
        r"""
        template <class F>
        void iteratePartitions(int n, F process) {
            if (n < 0 || n >= 31) throw invalid_argument("n must be in [0, 30]");
            int total = 1 << n;
            for (int mask = 0; mask < total; mask++) {
                for (int sub = mask;; sub = (sub - 1) & mask) {
                    int other = mask ^ sub;
                    process(mask, sub, other);
                    if (sub == 0) break;
                }
            }
        }
        """,
    ),
    "4-bit-algo-32-add-two-numbers-without": blocks(
        r"""
        int add(int a, int b) {
            unsigned int x = static_cast<unsigned int>(a);
            unsigned int y = static_cast<unsigned int>(b);
            while (y != 0U) {
                unsigned int carry = x & y;
                x ^= y;
                y = carry << 1;
            }
            return static_cast<int>(x);
        }
        """,
    ),
    "4-bit-algo-33-multiply-using-bit-manipulation": blocks(
        r"""
        long long multiply(long long a, long long b) {
            __int128 x = a < 0 ? -static_cast<__int128>(a) : static_cast<__int128>(a);
            __int128 y = b < 0 ? -static_cast<__int128>(b) : static_cast<__int128>(b);
            __int128 ans = 0;
            while (y > 0) {
                if ((y & 1) != 0) ans += x;
                x <<= 1;
                y >>= 1;
            }
            if ((a < 0) ^ (b < 0)) ans = -ans;
            if (ans < LLONG_MIN || ans > LLONG_MAX) {
                throw overflow_error("product does not fit in long long");
            }
            return static_cast<long long>(ans);
        }
        """,
    ),
    "4-bit-algo-34-count-numbers-with-a-given-bit-property": blocks(
        r"""
        long long countSetBit(long long n, int bit) {
            if (n < 0 || bit < 0 || bit >= 63) return 0;
            unsigned long long total = static_cast<unsigned long long>(n) + 1ULL;
            unsigned long long half = 1ULL << bit;
            unsigned long long block = half << 1;
            unsigned long long full = total / block;
            unsigned long long rem = total % block;
            unsigned long long extra = rem > half ? rem - half : 0ULL;
            return static_cast<long long>(full * half + extra);
        }
        """,
    ),
    "4-bit-algo-what-you-should-actually-memorize": [],
    "1-number-theory-4-modular-exponentiation-binary-exponentiation": blocks(
        r"""
        long long modExp(long long a, long long b, long long m) {
            if (m <= 0) throw invalid_argument("modulus must be positive");
            if (b < 0) throw invalid_argument("exponent must be non-negative");
            long long res = 1 % m;
            a %= m;
            if (a < 0) a += m;
            while (b > 0) {
                if ((b & 1LL) != 0) {
                    res = static_cast<long long>((__int128)res * a % m);
                }
                a = static_cast<long long>((__int128)a * a % m);
                b >>= 1LL;
            }
            return res;
        }
        """,
    ),
    "1-number-theory-why": [],
    "1-number-theory-5-modular-inverse-extended-euclid": blocks(
        r"""
        long long extendedGCD(long long a, long long b, long long& x, long long& y) {
            if (b == 0) {
                x = 1;
                y = 0;
                return a;
            }
            long long x1, y1;
            long long g = extendedGCD(b, a % b, x1, y1);
            x = y1;
            y = x1 - (a / b) * y1;
            return g;
        }

        long long modInverse(long long a, long long m) {
            if (m <= 1) return -1;
            a %= m;
            if (a < 0) a += m;
            long long x, y;
            long long g = extendedGCD(a, m, x, y);
            if (g != 1) return -1;
            return (x % m + m) % m;
        }
        """,
    ),
    "1-number-theory-complexity-7": [],
    "1-number-theory-why-spf-is-useful": [],
    "1-number-theory-10-modular-multiplication-avoid-overflow": blocks(
        r"""
        long long modMul(long long a, long long b, long long m) {
            if (m <= 0) throw invalid_argument("modulus must be positive");
            a %= m;
            b %= m;
            if (a < 0) a += m;
            if (b < 0) b += m;

            long long res = 0;
            while (b > 0) {
                if ((b & 1LL) != 0) {
                    if (res >= m - a) {
                        res -= m - a;
                    } else {
                        res += a;
                    }
                }
                b >>= 1LL;
                if (b == 0) break;
                if (a >= m - a) {
                    a -= m - a;
                } else {
                    a += a;
                }
            }
            return res;
        }
        """,
    ),
    "1-number-theory-11-miller-rabin-primality-test": blocks(
        r"""
        bool isPrime(long long n, int k = 5) {
            static_cast<void>(k);
            if (n < 2) return false;
            for (long long p : {2LL, 3LL, 5LL, 7LL, 11LL, 13LL, 17LL, 19LL, 23LL, 29LL, 31LL, 37LL}) {
                if (n % p == 0) return n == p;
            }

            auto modMul = [&](long long a, long long b, long long mod) -> long long {
                return static_cast<long long>((__int128)a * b % mod);
            };
            auto modPow = [&](long long a, long long d, long long mod) -> long long {
                long long res = 1 % mod;
                a %= mod;
                while (d > 0) {
                    if ((d & 1LL) != 0) res = modMul(res, a, mod);
                    a = modMul(a, a, mod);
                    d >>= 1LL;
                }
                return res;
            };

            long long d = n - 1;
            int s = 0;
            while ((d & 1LL) == 0) {
                d >>= 1LL;
                s++;
            }

            auto composite = [&](long long a) -> bool {
                if (a % n == 0) return false;
                long long x = modPow(a, d, n);
                if (x == 1 || x == n - 1) return false;
                for (int r = 1; r < s; r++) {
                    x = modMul(x, x, n);
                    if (x == n - 1) return false;
                }
                return true;
            };

            for (long long a : {2LL, 325LL, 9375LL, 28178LL, 450775LL, 9780504LL, 1795265022LL}) {
                if (composite(a)) return false;
            }
            return true;
        }
        """,
    ),
    "1-number-theory-complexity-11": [],
    "1-number-theory-12-chinese-remainder-theorem-crt": blocks(
        r"""
        long long extendedGCD(long long a, long long b, long long& x, long long& y) {
            if (b == 0) {
                x = 1;
                y = 0;
                return a;
            }
            long long x1, y1;
            long long g = extendedGCD(b, a % b, x1, y1);
            x = y1;
            y = x1 - (a / b) * y1;
            return g;
        }

        long long modInverse(long long a, long long m) {
            a %= m;
            if (a < 0) a += m;
            long long x, y;
            long long g = extendedGCD(a, m, x, y);
            if (g != 1) return -1;
            return (x % m + m) % m;
        }

        long long CRT(const vector<long long>& nums, const vector<long long>& rems) {
            if (nums.empty() || nums.size() != rems.size()) {
                throw invalid_argument("nums and rems must be non-empty and have the same size");
            }

            __int128 prod = 1;
            for (long long mod : nums) {
                if (mod <= 0) throw invalid_argument("moduli must be positive");
                prod *= mod;
                if (prod > LLONG_MAX) {
                    throw overflow_error("combined modulus exceeds 64-bit range");
                }
            }

            long long modAll = static_cast<long long>(prod);
            __int128 result = 0;
            for (int i = 0; i < static_cast<int>(nums.size()); i++) {
                long long mod = nums[i];
                long long residue = rems[i] % mod;
                if (residue < 0) residue += mod;

                long long pp = modAll / mod;
                long long inv = modInverse(pp % mod, mod);
                if (inv == -1) return -1;

                result += (__int128)residue * inv % modAll * pp;
                result %= modAll;
            }

            result %= modAll;
            if (result < 0) result += modAll;
            return static_cast<long long>(result);
        }
        """,
    ),
    "1-number-theory-14-ncr-p-factorial-inverse-factorial": blocks(
        r"""
        vector<long long> fact;
        vector<long long> invFact;

        long long modPow(long long a, long long b, long long p) {
            long long res = 1 % p;
            a %= p;
            if (a < 0) a += p;
            while (b > 0) {
                if ((b & 1LL) != 0) {
                    res = static_cast<long long>((__int128)res * a % p);
                }
                a = static_cast<long long>((__int128)a * a % p);
                b >>= 1LL;
            }
            return res;
        }

        void precompute(int N, long long p) {
            if (N < 0) throw invalid_argument("N must be non-negative");
            if (p <= 1) throw invalid_argument("p must be prime");
            if (N >= p) throw invalid_argument("this method requires N < p");

            fact.assign(N + 1, 1);
            invFact.assign(N + 1, 1);
            for (int i = 1; i <= N; i++) {
                fact[i] = static_cast<long long>((__int128)fact[i - 1] * i % p);
            }
            invFact[N] = modPow(fact[N], p - 2, p);
            for (int i = N - 1; i >= 0; i--) {
                invFact[i] = static_cast<long long>((__int128)invFact[i + 1] * (i + 1) % p);
            }
        }
        """,
        r"""
        long long nCr(int n, int r, long long p) {
            if (r < 0 || r > n) return 0;
            if (n >= static_cast<int>(fact.size())) {
                throw out_of_range("call precompute with N >= n first");
            }
            return static_cast<long long>((__int128)fact[n] * invFact[r] % p * invFact[n - r] % p);
        }
        """,
    ),
    "2-string-kmp": blocks(
        r"""
        vector<int> computeLPS(const string& pat) {
            int n = static_cast<int>(pat.size());
            vector<int> lps(n, 0);
            int len = 0;
            for (int i = 1; i < n; i++) {
                while (len > 0 && pat[i] != pat[len]) {
                    len = lps[len - 1];
                }
                if (pat[i] == pat[len]) len++;
                lps[i] = len;
            }
            return lps;
        }

        vector<int> KMP(const string& text, const string& pat) {
            vector<int> ans;
            if (pat.empty()) return ans;

            vector<int> lps = computeLPS(pat);
            int n = static_cast<int>(text.size());
            int m = static_cast<int>(pat.size());
            int i = 0;
            int j = 0;
            while (i < n) {
                if (text[i] == pat[j]) {
                    i++;
                    j++;
                    if (j == m) {
                        ans.push_back(i - j);
                        j = lps[j - 1];
                    }
                } else if (j > 0) {
                    j = lps[j - 1];
                } else {
                    i++;
                }
            }
            return ans;
        }
        """,
    ),
    "2-string-7-rabin-karp-rolling-hash": blocks(
        r"""
        vector<int> rabinKarp(const string& text, const string& pat) {
            vector<int> ans;
            int n = static_cast<int>(text.size());
            int m = static_cast<int>(pat.size());
            if (m == 0 || m > n) return ans;

            const long long MOD = 1000000007;
            const long long BASE = 911382323;
            auto value = [](unsigned char c) -> long long {
                return static_cast<long long>(c) + 1;
            };

            long long patHash = 0;
            long long textHash = 0;
            long long power = 1;
            for (int i = 0; i < m; i++) {
                patHash = (patHash * BASE + value(static_cast<unsigned char>(pat[i]))) % MOD;
                textHash = (textHash * BASE + value(static_cast<unsigned char>(text[i]))) % MOD;
                if (i + 1 < m) power = power * BASE % MOD;
            }

            for (int i = 0; i <= n - m; i++) {
                if (patHash == textHash && text.compare(i, m, pat) == 0) {
                    ans.push_back(i);
                }
                if (i < n - m) {
                    textHash = (textHash -
                                value(static_cast<unsigned char>(text[i])) * power % MOD +
                                MOD) % MOD;
                    textHash = (textHash * BASE +
                                value(static_cast<unsigned char>(text[i + m]))) % MOD;
                }
            }
            return ans;
        }
        """,
    ),
    "2-string-10-aho-corasick": blocks(
        r"""
        class AhoCorasick {
            static constexpr int ALPHABET = 256;

            struct Node {
                array<int, ALPHABET> child;
                int link;
                vector<int> output;
                Node() : link(0) {
                    child.fill(-1);
                }
            };

            vector<Node> trie;
            vector<int> patternLength;

        public:
            AhoCorasick() : trie(1) {}

            void insert(const string& s, int id) {
                if (id >= static_cast<int>(patternLength.size())) {
                    patternLength.resize(id + 1, 0);
                }
                patternLength[id] = static_cast<int>(s.size());

                int cur = 0;
                for (char c : s) {
                    int x = static_cast<unsigned char>(c);
                    if (trie[cur].child[x] == -1) {
                        trie[cur].child[x] = static_cast<int>(trie.size());
                        trie.emplace_back();
                    }
                    cur = trie[cur].child[x];
                }
                trie[cur].output.push_back(id);
            }

            void build() {
                queue<int> q;
                for (int c = 0; c < ALPHABET; c++) {
                    int nxt = trie[0].child[c];
                    if (nxt != -1) {
                        trie[nxt].link = 0;
                        q.push(nxt);
                    } else {
                        trie[0].child[c] = 0;
                    }
                }

                while (!q.empty()) {
                    int v = q.front();
                    q.pop();

                    const auto& failOutput = trie[trie[v].link].output;
                    trie[v].output.insert(trie[v].output.end(), failOutput.begin(), failOutput.end());

                    for (int c = 0; c < ALPHABET; c++) {
                        int nxt = trie[v].child[c];
                        if (nxt != -1) {
                            trie[nxt].link = trie[trie[v].link].child[c];
                            q.push(nxt);
                        } else {
                            trie[v].child[c] = trie[trie[v].link].child[c];
                        }
                    }
                }
            }

            vector<pair<int, int>> search(const string& text) const {
                vector<pair<int, int>> matches;
                int state = 0;
                for (int i = 0; i < static_cast<int>(text.size()); i++) {
                    state = trie[state].child[static_cast<unsigned char>(text[i])];
                    for (int id : trie[state].output) {
                        matches.push_back({i - patternLength[id] + 1, id});
                    }
                }
                return matches;
            }
        };
        """,
    ),
    "2-string-11-polynomial-rolling-hash": blocks(
        r"""
        class StringHash {
            static const long long MOD = 1000000007;
            static const long long BASE = 911382323;
            vector<long long> h;
            vector<long long> power;

        public:
            explicit StringHash(const string& s) {
                int n = static_cast<int>(s.size());
                h.assign(n + 1, 0);
                power.assign(n + 1, 1);
                for (int i = 0; i < n; i++) {
                    long long value = static_cast<unsigned char>(s[i]) + 1;
                    h[i + 1] = (h[i] * BASE + value) % MOD;
                    power[i + 1] = power[i] * BASE % MOD;
                }
            }

            long long getHash(int l, int r) const {
                int n = static_cast<int>(h.size()) - 1;
                if (l < 0 || r < l || r > n) {
                    throw out_of_range("invalid substring range");
                }
                return (h[r] - h[l] * power[r - l] % MOD + MOD) % MOD;
            }
        };
        """,
        r"""
        bool equalSubstrings(const StringHash& H, int l1, int r1, int l2, int r2) {
            if (r1 - l1 != r2 - l2) return false;
            return H.getHash(l1, r1) == H.getHash(l2, r2);
        }
        """,
    ),
    "2-string-12-longest-palindromic-subsequence": blocks(
        r"""
        int longestPalindromicSubsequence(const string& s) {
            int n = static_cast<int>(s.size());
            if (n == 0) return 0;

            vector<vector<int>> dp(n, vector<int>(n, 0));
            for (int i = 0; i < n; i++) dp[i][i] = 1;

            for (int len = 2; len <= n; len++) {
                for (int l = 0; l + len - 1 < n; l++) {
                    int r = l + len - 1;
                    if (s[l] == s[r]) {
                        dp[l][r] = 2 + (len == 2 ? 0 : dp[l + 1][r - 1]);
                    } else {
                        dp[l][r] = max(dp[l + 1][r], dp[l][r - 1]);
                    }
                }
            }
            return dp[0][n - 1];
        }
        """,
    ),
    "2-string-13-minimum-window-substring": blocks(
        r"""
        string minWindow(const string& s, const string& t) {
            if (t.empty() || s.empty() || t.size() > s.size()) return "";

            array<int, 256> need{};
            array<int, 256> window{};
            for (char c : t) need[static_cast<unsigned char>(c)]++;

            int missing = static_cast<int>(t.size());
            int bestLen = INT_MAX;
            int bestL = 0;
            int l = 0;

            for (int r = 0; r < static_cast<int>(s.size()); r++) {
                unsigned char rc = static_cast<unsigned char>(s[r]);
                if (need[rc] > 0 && window[rc] < need[rc]) missing--;
                window[rc]++;

                while (missing == 0) {
                    if (r - l + 1 < bestLen) {
                        bestLen = r - l + 1;
                        bestL = l;
                    }

                    unsigned char lc = static_cast<unsigned char>(s[l]);
                    window[lc]--;
                    if (need[lc] > 0 && window[lc] < need[lc]) missing++;
                    l++;
                }
            }

            return bestLen == INT_MAX ? "" : s.substr(bestL, bestLen);
        }
        """,
    ),
    "2-string-19-suffix-automaton": blocks(
        r"""
        class SuffixAutomaton {
            static constexpr int ALPHABET = 256;

            struct State {
                int len = 0;
                int link = -1;
                array<int, ALPHABET> next;
                State() {
                    next.fill(-1);
                }
            };

            vector<State> st;
            int last = 0;

        public:
            SuffixAutomaton() : st(1) {}

            void extend(char ch) {
                int c = static_cast<unsigned char>(ch);
                int cur = static_cast<int>(st.size());
                st.emplace_back();
                st[cur].len = st[last].len + 1;

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
                        while (p != -1 && st[p].next[c] == q) {
                            st[p].next[c] = clone;
                            p = st[p].link;
                        }
                        st[q].link = clone;
                        st[cur].link = clone;
                    }
                }
                last = cur;
            }

            void build(const string& s) {
                st.assign(1, State());
                last = 0;
                for (char c : s) extend(c);
            }

            bool contains(const string& pattern) const {
                int state = 0;
                for (char c : pattern) {
                    state = st[state].next[static_cast<unsigned char>(c)];
                    if (state == -1) return false;
                }
                return true;
            }
        };
        """,
    ),
}

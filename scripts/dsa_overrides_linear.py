"""Corrected C++17 code overrides for audited linear DSA sections."""

from __future__ import annotations

from textwrap import dedent


def cpp(source: str) -> str:
    return dedent(source).strip()


DSA_CODE_OVERRIDES: dict[str, list[str]] = {
    "5-linkedlist-8-palindrome-linked-list": [
        cpp(
            r"""
            ListNode* reverseList(ListNode* head) {
                ListNode* prev = nullptr;
                while (head) {
                    ListNode* next = head->next;
                    head->next = prev;
                    prev = head;
                    head = next;
                }
                return prev;
            }
            bool isPalindrome(ListNode* head) {
                if (!head || !head->next) return true;
                ListNode* slow = head;
                ListNode* fast = head;
                while (fast->next && fast->next->next) {
                    slow = slow->next;
                    fast = fast->next->next;
                }
                ListNode* secondHalf = reverseList(slow->next);
                ListNode* copy = secondHalf;
                ListNode* firstHalf = head;
                bool ok = true;
                while (copy) {
                    if (firstHalf->val != copy->val) {
                        ok = false;
                        break;
                    }
                    firstHalf = firstHalf->next;
                    copy = copy->next;
                }
                slow->next = reverseList(secondHalf);
                return ok;
            }
            """
        ),
    ],
    "5-linkedlist-11-merge-k-lists-using-divide-and-conquer": [
        cpp(
            r"""
            ListNode* mergeTwoLists(ListNode* l1, ListNode* l2) {
                ListNode dummy(0);
                ListNode* tail = &dummy;
                while (l1 && l2) {
                    if (l1->val <= l2->val) {
                        tail->next = l1;
                        l1 = l1->next;
                    } else {
                        tail->next = l2;
                        l2 = l2->next;
                    }
                    tail = tail->next;
                }
                tail->next = l1 ? l1 : l2;
                return dummy.next;
            }
            ListNode* mergeRange(vector<ListNode*>& lists, int l, int r) {
                if (l == r) return lists[l];
                int mid = l + (r - l) / 2;
                ListNode* left = mergeRange(lists, l, mid);
                ListNode* right = mergeRange(lists, mid + 1, r);
                return mergeTwoLists(left, right);
            }
            ListNode* mergeKListsDC(vector<ListNode*>& lists) {
                if (lists.empty()) return nullptr;
                return mergeRange(lists, 0, static_cast<int>(lists.size()) - 1);
            }
            """
        ),
    ],
    "5-linkedlist-12-remove-n-th-node-from-end": [
        cpp(
            r"""
            ListNode* removeNthFromEnd(ListNode* head, int n) {
                if (!head || n <= 0) return head;
                ListNode dummy(0);
                dummy.next = head;
                ListNode* first = &dummy;
                for (int i = 0; i < n && first; i++) {
                    first = first->next;
                }
                if (!first) return head;
                ListNode* second = &dummy;
                while (first->next) {
                    first = first->next;
                    second = second->next;
                }
                ListNode* node = second->next;
                if (!node) return head;
                second->next = node->next;
                return dummy.next;
            }
            """
        ),
    ],
    "5-linkedlist-14-sort-a-linked-list-merge-sort": [
        cpp(
            r"""
            ListNode* mergeTwoLists(ListNode* l1, ListNode* l2) {
                ListNode dummy(0);
                ListNode* tail = &dummy;
                while (l1 && l2) {
                    if (l1->val <= l2->val) {
                        tail->next = l1;
                        l1 = l1->next;
                    } else {
                        tail->next = l2;
                        l2 = l2->next;
                    }
                    tail = tail->next;
                }
                tail->next = l1 ? l1 : l2;
                return dummy.next;
            }
            ListNode* sortList(ListNode* head) {
                if (!head || !head->next) return head;
                ListNode* slow = head;
                ListNode* fast = head->next;
                while (fast && fast->next) {
                    slow = slow->next;
                    fast = fast->next->next;
                }
                ListNode* mid = slow->next;
                slow->next = nullptr;
                ListNode* left = sortList(head);
                ListNode* right = sortList(mid);
                return mergeTwoLists(left, right);
            }
            """
        ),
    ],
    "5-linkedlist-better-version-using-dfs": [
        cpp(
            r"""
            Node* flattenTail(Node* head) {
                Node* curr = head;
                Node* tail = head;
                while (curr) {
                    Node* next = curr->next;
                    if (curr->child) {
                        Node* childHead = curr->child;
                        Node* childTail = flattenTail(childHead);
                        curr->child = nullptr;
                        curr->next = childHead;
                        childHead->prev = curr;
                        if (next) {
                            childTail->next = next;
                            next->prev = childTail;
                        }
                        tail = childTail;
                        curr = childTail;
                    } else {
                        tail = curr;
                    }
                    curr = curr->next;
                }
                return tail;
            }
            Node* flattenDFS(Node* head) {
                if (!head) return nullptr;
                flattenTail(head);
                return head;
            }
            """
        ),
    ],
    "5-linkedlist-20-reorder-list": [
        cpp(
            r"""
            ListNode* reverseList(ListNode* head) {
                ListNode* prev = nullptr;
                while (head) {
                    ListNode* next = head->next;
                    head->next = prev;
                    prev = head;
                    head = next;
                }
                return prev;
            }
            void reorderList(ListNode* head) {
                if (!head || !head->next) return;
                ListNode* slow = head;
                ListNode* fast = head;
                while (fast->next && fast->next->next) {
                    slow = slow->next;
                    fast = fast->next->next;
                }
                ListNode* second = reverseList(slow->next);
                slow->next = nullptr;
                ListNode* first = head;
                while (second) {
                    ListNode* next1 = first->next;
                    ListNode* next2 = second->next;
                    first->next = second;
                    second->next = next1;
                    first = next1;
                    second = next2;
                }
            }
            """
        ),
    ],
    "5-linkedlist-28-reverse-alternate-k-nodes": [
        cpp(
            r"""
            ListNode* reverseAlternateK(ListNode* head, int k) {
                if (!head || k <= 1) return head;
                ListNode* curr = head;
                ListNode* prev = nullptr;
                int count = 0;
                while (curr && count < k) {
                    ListNode* next = curr->next;
                    curr->next = prev;
                    prev = curr;
                    curr = next;
                    count++;
                }
                head->next = curr;
                ListNode* skip = curr;
                for (int i = 1; skip && i < k; i++) {
                    skip = skip->next;
                }
                if (skip) skip->next = reverseAlternateK(skip->next, k);
                return prev;
            }
            """
        ),
    ],
    "5-linkedlist-what-to-actually-memorize": [],
    "7-stack-and-queue-6-maximal-rectangle-in-binary-matrix": [
        cpp(
            r"""
            int largestRectangleArea(vector<int>& heights) {
                int n = static_cast<int>(heights.size());
                stack<int> st;
                int ans = 0;
                for (int i = 0; i <= n; i++) {
                    int curr = (i == n ? 0 : heights[i]);
                    while (!st.empty() && curr < heights[st.top()]) {
                        int h = heights[st.top()];
                        st.pop();
                        int width = st.empty() ? i : i - st.top() - 1;
                        ans = max(ans, h * width);
                    }
                    st.push(i);
                }
                return ans;
            }
            int maximalRectangle(vector<vector<char>>& matrix) {
                if (matrix.empty() || matrix[0].empty()) return 0;
                int m = static_cast<int>(matrix.size());
                int n = static_cast<int>(matrix[0].size());
                vector<int> heights(n, 0);
                int ans = 0;
                for (int i = 0; i < m; i++) {
                    for (int j = 0; j < n; j++) {
                        heights[j] = (matrix[i][j] == '1') ? heights[j] + 1 : 0;
                    }
                    ans = max(ans, largestRectangleArea(heights));
                }
                return ans;
            }
            """
        ),
    ],
    "7-stack-and-queue-15-infix-to-postfix": [
        cpp(
            r"""
            int precedence(char op) {
                if (op == '^') return 3;
                if (op == '*' || op == '/') return 2;
                if (op == '+' || op == '-') return 1;
                return 0;
            }
            bool isRightAssociative(char op) {
                return op == '^';
            }
            string infixToPostfix(string s) {
                stack<char> st;
                string ans;
                for (char c : s) {
                    if (isspace(static_cast<unsigned char>(c))) continue;
                    if (isalnum(static_cast<unsigned char>(c))) {
                        ans += c;
                    } else if (c == '(') {
                        st.push(c);
                    } else if (c == ')') {
                        while (!st.empty() && st.top() != '(') {
                            ans += st.top();
                            st.pop();
                        }
                        if (!st.empty()) st.pop();
                    } else {
                        while (!st.empty() && st.top() != '(' &&
                               (precedence(st.top()) > precedence(c) ||
                                (precedence(st.top()) == precedence(c) && !isRightAssociative(c)))) {
                            ans += st.top();
                            st.pop();
                        }
                        st.push(c);
                    }
                }
                while (!st.empty()) {
                    if (st.top() != '(') ans += st.top();
                    st.pop();
                }
                return ans;
            }
            """
        ),
    ],
    "6-heap-2-build-heap": [
        cpp(
            r"""
            void heapify(vector<int>& arr, int n, int i) {
                int largest = i;
                int left = 2 * i + 1;
                int right = 2 * i + 2;
                if (left < n && arr[left] > arr[largest]) largest = left;
                if (right < n && arr[right] > arr[largest]) largest = right;
                if (largest != i) {
                    swap(arr[i], arr[largest]);
                    heapify(arr, n, largest);
                }
            }
            void buildHeap(vector<int>& arr) {
                for (int i = static_cast<int>(arr.size()) / 2 - 1; i >= 0; i--) {
                    heapify(arr, static_cast<int>(arr.size()), i);
                }
            }
            """
        ),
    ],
    "6-heap-4-extract-maximum": [
        cpp(
            r"""
            void heapify(vector<int>& heap, int n, int i) {
                int largest = i;
                int left = 2 * i + 1;
                int right = 2 * i + 2;
                if (left < n && heap[left] > heap[largest]) largest = left;
                if (right < n && heap[right] > heap[largest]) largest = right;
                if (largest != i) {
                    swap(heap[i], heap[largest]);
                    heapify(heap, n, largest);
                }
            }
            int extractMax(vector<int>& heap) {
                if (heap.empty()) return -1;
                int ans = heap[0];
                heap[0] = heap.back();
                heap.pop_back();
                if (!heap.empty()) heapify(heap, static_cast<int>(heap.size()), 0);
                return ans;
            }
            """
        ),
    ],
    "6-heap-15-minimum-cost-to-connect-ropes": [
        cpp(
            r"""
            long long minCostRopes(vector<int>& ropes) {
                priority_queue<long long, vector<long long>, greater<long long>> pq;
                for (int rope : ropes) pq.push(rope);
                long long cost = 0;
                while (pq.size() > 1) {
                    long long a = pq.top();
                    pq.pop();
                    long long b = pq.top();
                    pq.pop();
                    long long sum = a + b;
                    cost += sum;
                    pq.push(sum);
                }
                return cost;
            }
            """
        ),
    ],
    "6-heap-17-find-k-pairs-with-smallest-sums": [
        cpp(
            r"""
            vector<vector<int>> kSmallestPairs(vector<int>& nums1, vector<int>& nums2, int k) {
                if (nums1.empty() || nums2.empty() || k <= 0) return {};
                using T = tuple<long long, int, int>;
                priority_queue<T, vector<T>, greater<T>> pq;
                int n = min(static_cast<int>(nums1.size()), k);
                for (int i = 0; i < n; i++) {
                    pq.push({static_cast<long long>(nums1[i]) + nums2[0], i, 0});
                }
                vector<vector<int>> ans;
                while (k-- > 0 && !pq.empty()) {
                    auto [sum, i, j] = pq.top();
                    pq.pop();
                    ans.push_back({nums1[i], nums2[j]});
                    if (j + 1 < static_cast<int>(nums2.size())) {
                        pq.push({static_cast<long long>(nums1[i]) + nums2[j + 1], i, j + 1});
                    }
                }
                return ans;
            }
            """
        ),
    ],
    "6-heap-18-find-kth-smallest-pair-distance": [
        cpp(
            r"""
            long long countPairs(vector<int>& nums, int maxDist) {
                long long count = 0;
                int left = 0;
                for (int right = 0; right < static_cast<int>(nums.size()); right++) {
                    while (nums[right] - nums[left] > maxDist) {
                        left++;
                    }
                    count += right - left;
                }
                return count;
            }
            int smallestDistancePair(vector<int>& nums, int k) {
                if (nums.size() < 2) return 0;
                sort(nums.begin(), nums.end());
                int left = 0;
                int right = nums.back() - nums.front();
                while (left < right) {
                    int mid = left + (right - left) / 2;
                    if (countPairs(nums, mid) >= k)
                        right = mid;
                    else
                        left = mid + 1;
                }
                return left;
            }
            """
        ),
    ],
    "13-hashing-4-longest-subarray-with-equal-0s-1s-and-2s": [
        cpp(
            r"""
            struct PairHash {
                size_t operator()(const pair<int, int>& p) const {
                    size_t h1 = hash<int>{}(p.first);
                    size_t h2 = hash<int>{}(p.second);
                    return h1 ^ (h2 + 0x9e3779b97f4a7c15ULL + (h1 << 6) + (h1 >> 2));
                }
            };
            int longestEqual012(vector<int>& arr) {
                unordered_map<pair<int, int>, int, PairHash> first;
                int c0 = 0, c1 = 0, c2 = 0;
                int ans = 0;
                first[{0, 0}] = -1;
                for (int i = 0; i < static_cast<int>(arr.size()); i++) {
                    if (arr[i] == 0)
                        c0++;
                    else if (arr[i] == 1)
                        c1++;
                    else if (arr[i] == 2)
                        c2++;
                    else
                        continue;
                    pair<int, int> key = {c0 - c1, c1 - c2};
                    auto it = first.find(key);
                    if (it != first.end()) {
                        ans = max(ans, i - it->second);
                    } else {
                        first[key] = i;
                    }
                }
                return ans;
            }
            """
        ),
    ],
    "13-hashing-14-subarray-with-same-sum-in-two-arrays": [
        cpp(
            r"""
            bool sameSubarraySum(vector<int>& a, vector<int>& b) {
                auto buildPrefix = [](const vector<int>& arr) {
                    vector<long long> pref(arr.size() + 1, 0);
                    for (int i = 0; i < static_cast<int>(arr.size()); i++) {
                        pref[i + 1] = pref[i] + arr[i];
                    }
                    return pref;
                };
                const vector<int>& small = (a.size() <= b.size()) ? a : b;
                const vector<int>& large = (a.size() <= b.size()) ? b : a;
                vector<long long> smallPref = buildPrefix(small);
                vector<long long> largePref = buildPrefix(large);
                unordered_set<long long> sums;
                for (int l = 0; l < static_cast<int>(small.size()); l++) {
                    for (int r = l + 1; r <= static_cast<int>(small.size()); r++) {
                        sums.insert(smallPref[r] - smallPref[l]);
                    }
                }
                for (int l = 0; l < static_cast<int>(large.size()); l++) {
                    for (int r = l + 1; r <= static_cast<int>(large.size()); r++) {
                        if (sums.count(largePref[r] - largePref[l])) return true;
                    }
                }
                return false;
            }
            """
        ),
    ],
    "13-hashing-16-custom-hash-for-pairintint": [
        cpp(
            r"""
            struct PairHash {
                size_t operator()(const pair<int, int>& p) const {
                    size_t h1 = hash<int>{}(p.first);
                    size_t h2 = hash<int>{}(p.second);
                    return h1 ^ (h2 + 0x9e3779b97f4a7c15ULL + (h1 << 6) + (h1 >> 2));
                }
            };
            unordered_map<pair<int, int>, int, PairHash> mp;
            """
        ),
    ],
    "13-hashing-18-avoiding-unordered-map-worst-case-attacks": [
        cpp(
            r"""
            struct CustomHash {
                static uint64_t splitmix64(uint64_t x) {
                    x += 0x9e3779b97f4a7c15ULL;
                    x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
                    x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
                    return x ^ (x >> 31);
                }
                size_t operator()(uint64_t x) const {
                    static const uint64_t FIXED_RANDOM =
                        chrono::steady_clock::now().time_since_epoch().count();
                    return splitmix64(x + FIXED_RANDOM);
                }
            };
            unordered_map<long long, int, CustomHash> mp;
            """
        ),
    ],
    "13-hashing-19-hash-map-prefix-sum-maximum-frequency-subarray-pattern": [
        cpp(
            r"""
            template <class State, class Value, class Update, class Hash = std::hash<State>>
            int longestByPrefixState(const vector<Value>& arr, State initialState, Update update, Hash hasher = Hash()) {
                unordered_map<State, int, Hash> first(0, hasher);
                State state = initialState;
                first.emplace(state, -1);
                int ans = 0;
                for (int i = 0; i < static_cast<int>(arr.size()); i++) {
                    state = update(state, arr[i]);
                    auto it = first.find(state);
                    if (it != first.end()) {
                        ans = max(ans, i - it->second);
                    } else {
                        first.emplace(state, i);
                    }
                }
                return ans;
            }
            """
        ),
    ],
    "13-hashing-20-subarray-sum-with-multiple-queries": [
        cpp(
            r"""
            vector<long long> countSubarraySumQueries(vector<int>& arr, vector<long long>& queries) {
                vector<long long> answers;
                answers.reserve(queries.size());
                for (long long k : queries) {
                    unordered_map<long long, long long> freq;
                    freq[0] = 1;
                    long long sum = 0;
                    long long count = 0;
                    for (int x : arr) {
                        sum += x;
                        auto it = freq.find(sum - k);
                        if (it != freq.end()) count += it->second;
                        freq[sum]++;
                    }
                    answers.push_back(count);
                }
                return answers;
            }
            """
        ),
    ],
    "13-hashing-21-hashing-for-duplicate-subtrees": [
        cpp(
            r"""
            struct Key {
                int val;
                int left;
                int right;
                bool operator==(const Key& other) const {
                    return val == other.val && left == other.left && right == other.right;
                }
            };
            struct KeyHash {
                size_t operator()(const Key& k) const {
                    size_t h1 = hash<int>{}(k.val);
                    size_t h2 = hash<int>{}(k.left);
                    size_t h3 = hash<int>{}(k.right);
                    return h1 ^ (h2 << 1) ^ (h3 << 2);
                }
            };
            int encode(TreeNode* node, unordered_map<Key, int, KeyHash>& ids, unordered_map<int, int>& freq,
                       vector<TreeNode*>& duplicates, int& nextId) {
                if (!node) return 0;
                Key key = {node->val, encode(node->left, ids, freq, duplicates, nextId),
                           encode(node->right, ids, freq, duplicates, nextId)};
                auto [it, inserted] = ids.emplace(key, nextId);
                if (inserted) nextId++;
                int id = it->second;
                if (++freq[id] == 2) duplicates.push_back(node);
                return id;
            }
            vector<TreeNode*> findDuplicateSubtrees(TreeNode* root) {
                unordered_map<Key, int, KeyHash> ids;
                unordered_map<int, int> freq;
                vector<TreeNode*> duplicates;
                int nextId = 1;
                encode(root, ids, freq, duplicates, nextId);
                return duplicates;
            }
            """
        ),
    ],
    "13-hashing-23-group-strings-by-shift-pattern": [
        cpp(
            r"""
            string getPattern(const string& s) {
                if (s.size() <= 1) return "#";
                string key;
                for (int i = 1; i < static_cast<int>(s.size()); i++) {
                    int diff = (s[i] - s[i - 1] + 26) % 26;
                    key += to_string(diff) + '#';
                }
                return key;
            }
            vector<vector<string>> groupStrings(vector<string>& strings) {
                unordered_map<string, vector<string>> groups;
                for (const string& s : strings) {
                    groups[getPattern(s)].push_back(s);
                }
                vector<vector<string>> ans;
                ans.reserve(groups.size());
                for (auto& [pattern, group] : groups) {
                    ans.push_back(group);
                }
                return ans;
            }
            """
        ),
    ],
    "13-hashing-24-hash-based-frequency-ranking": [
        cpp(
            r"""
            vector<int> topKFrequentLargeInput(vector<int>& arr, int k) {
                if (k <= 0) return {};
                unordered_map<int, int> freq;
                for (int x : arr) freq[x]++;
                vector<pair<int, int>> items;
                items.reserve(freq.size());
                for (auto& [x, f] : freq) items.push_back({f, x});
                if (items.empty()) return {};
                k = min(k, static_cast<int>(items.size()));
                auto byFrequency = [](const pair<int, int>& a, const pair<int, int>& b) {
                    if (a.first != b.first) return a.first > b.first;
                    return a.second < b.second;
                };
                if (k < static_cast<int>(items.size())) {
                    nth_element(items.begin(), items.begin() + k, items.end(), byFrequency);
                }
                sort(items.begin(), items.begin() + k, byFrequency);
                vector<int> ans;
                ans.reserve(k);
                for (int i = 0; i < k; i++) ans.push_back(items[i].second);
                return ans;
            }
            """
        ),
    ],
    "13-hashing-25-randomized-hashing-zobrist-hashing": [
        cpp(
            r"""
            uint64_t splitmix64(uint64_t x) {
                x += 0x9e3779b97f4a7c15ULL;
                x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
                x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
                return x ^ (x >> 31);
            }
            uint64_t hashState(const vector<int>& state) {
                uint64_t h = 0;
                for (int i = 0; i < static_cast<int>(state.size()); i++) {
                    uint64_t token = (static_cast<uint64_t>(i) << 32) ^
                                     static_cast<uint64_t>(static_cast<uint32_t>(state[i]));
                    h ^= splitmix64(token);
                }
                return h;
            }
            """
        ),
    ],
    "15-two-pointer-and-sliding-window-1-two-sum-ii-sorted-array": [
        cpp(
            r"""
            vector<int> twoSum(vector<int>& nums, int target) {
                if (nums.size() < 2) return {};
                int l = 0;
                int r = static_cast<int>(nums.size()) - 1;
                while (l < r) {
                    long long sum = 1LL * nums[l] + nums[r];
                    if (sum == target) return {l, r};
                    if (sum < target)
                        l++;
                    else
                        r--;
                }
                return {};
            }
            """
        ),
    ],
    "15-two-pointer-and-sliding-window-2-3sum": [
        cpp(
            r"""
            vector<vector<int>> threeSum(vector<int>& nums) {
                sort(nums.begin(), nums.end());
                vector<vector<int>> ans;
                int n = nums.size();
                for (int i = 0; i < n - 2; i++) {
                    if (i > 0 && nums[i] == nums[i - 1]) continue;
                    int l = i + 1;
                    int r = n - 1;
                    while (l < r) {
                        long long sum = 1LL * nums[i] + nums[l] + nums[r];
                        if (sum == 0) {
                            ans.push_back({nums[i], nums[l], nums[r]});
                            int x = nums[l];
                            int y = nums[r];
                            while (l < r && nums[l] == x) l++;
                            while (l < r && nums[r] == y) r--;
                        } else if (sum < 0)
                            l++;
                        else
                            r--;
                    }
                }
                return ans;
            }
            """
        ),
    ],
    "15-two-pointer-and-sliding-window-3-4sum": [
        cpp(
            r"""
            vector<vector<int>> fourSum(vector<int>& nums, long long target) {
                sort(nums.begin(), nums.end());
                vector<vector<int>> ans;
                int n = nums.size();
                for (int i = 0; i < n - 3; i++) {
                    if (i > 0 && nums[i] == nums[i - 1]) continue;
                    for (int j = i + 1; j < n - 2; j++) {
                        if (j > i + 1 && nums[j] == nums[j - 1]) continue;
                        int l = j + 1;
                        int r = n - 1;
                        while (l < r) {
                            long long sum = 1LL * nums[i] + nums[j] + nums[l] + nums[r];
                            if (sum == target) {
                                ans.push_back({nums[i], nums[j], nums[l], nums[r]});
                                int x = nums[l];
                                int y = nums[r];
                                while (l < r && nums[l] == x) l++;
                                while (l < r && nums[r] == y) r--;
                            } else if (sum < target)
                                l++;
                            else
                                r--;
                        }
                    }
                }
                return ans;
            }
            """
        ),
    ],
    "15-two-pointer-and-sliding-window-4-longest-substring-without-repeating-characters": [
        cpp(
            r"""
            int lengthOfLongestSubstring(string s) {
                vector<int> last(256, -1);
                int l = 0;
                int ans = 0;
                for (int r = 0; r < static_cast<int>(s.size()); r++) {
                    unsigned char ch = static_cast<unsigned char>(s[r]);
                    if (last[ch] >= l) l = last[ch] + 1;
                    last[ch] = r;
                    ans = max(ans, r - l + 1);
                }
                return ans;
            }
            """
        ),
    ],
    "15-two-pointer-and-sliding-window-5-longest-substring-with-at-most-k-distinct-characters": [
        cpp(
            r"""
            int longestKDistinct(string s, int k) {
                if (k <= 0) return 0;
                unordered_map<char, int> freq;
                int l = 0;
                int ans = 0;
                for (int r = 0; r < static_cast<int>(s.size()); r++) {
                    freq[s[r]]++;
                    while (static_cast<int>(freq.size()) > k) {
                        freq[s[l]]--;
                        if (freq[s[l]] == 0) freq.erase(s[l]);
                        l++;
                    }
                    ans = max(ans, r - l + 1);
                }
                return ans;
            }
            """
        ),
    ],
    "15-two-pointer-and-sliding-window-6-longest-substring-with-exactly-k-distinct-characters": [
        cpp(
            r"""
            int longestExactlyK(string s, int k) {
                if (k <= 0) return 0;
                unordered_map<char, int> freq;
                int l = 0;
                int ans = -1;
                for (int r = 0; r < static_cast<int>(s.size()); r++) {
                    freq[s[r]]++;
                    while (static_cast<int>(freq.size()) > k) {
                        freq[s[l]]--;
                        if (freq[s[l]] == 0) freq.erase(s[l]);
                        l++;
                    }
                    if (static_cast<int>(freq.size()) == k) ans = max(ans, r - l + 1);
                }
                return ans;
            }
            """
        ),
    ],
    "15-two-pointer-and-sliding-window-7-minimum-window-substring": [
        cpp(
            r"""
            string minWindow(string s, string t) {
                if (t.empty() || s.empty() || t.size() > s.size()) return "";
                vector<int> need(256, 0);
                for (char c : t) need[static_cast<unsigned char>(c)]++;
                int required = static_cast<int>(t.size());
                int l = 0;
                int bestLen = INT_MAX;
                int bestL = 0;
                for (int r = 0; r < static_cast<int>(s.size()); r++) {
                    unsigned char right = static_cast<unsigned char>(s[r]);
                    if (need[right] > 0) required--;
                    need[right]--;
                    while (required == 0) {
                        if (r - l + 1 < bestLen) {
                            bestLen = r - l + 1;
                            bestL = l;
                        }
                        unsigned char left = static_cast<unsigned char>(s[l]);
                        need[left]++;
                        if (need[left] > 0) required++;
                        l++;
                    }
                }
                return bestLen == INT_MAX ? "" : s.substr(bestL, bestLen);
            }
            """
        ),
    ],
    "15-two-pointer-and-sliding-window-8-longest-repeating-character-replacement": [
        cpp(
            r"""
            int characterReplacement(string s, int k) {
                vector<int> freq(26, 0);
                int l = 0;
                int maxFreq = 0;
                int ans = 0;
                for (int r = 0; r < s.size(); r++) {
                    freq[s[r] - 'A']++;
                    maxFreq = max(maxFreq, freq[s[r] - 'A']);
                    while ((r - l + 1) - maxFreq > k) {
                        freq[s[l] - 'A']--;
                        l++;
                    }
                    ans = max(ans, r - l + 1);
                }
                return ans;
            }
            """
        ),
    ],
    "15-two-pointer-and-sliding-window-9-permutation-in-string": [
        cpp(
            r"""
            bool checkInclusion(string s1, string s2) {
                if (s1.size() > s2.size()) return false;
                vector<int> need(26, 0);
                vector<int> have(26, 0);
                for (char c : s1) need[c - 'a']++;
                int k = s1.size();
                for (int i = 0; i < s2.size(); i++) {
                    have[s2[i] - 'a']++;
                    if (i >= k) have[s2[i - k] - 'a']--;
                    if (have == need) return true;
                }
                return false;
            }
            """
        ),
    ],
    "15-two-pointer-and-sliding-window-10-find-all-anagrams-in-a-string": [
        cpp(
            r"""
            vector<int> findAnagrams(string s, string p) {
                vector<int> need(26, 0);
                vector<int> have(26, 0);
                for (char c : p) need[c - 'a']++;
                vector<int> ans;
                int k = p.size();
                for (int i = 0; i < s.size(); i++) {
                    have[s[i] - 'a']++;
                    if (i >= k) have[s[i - k] - 'a']--;
                    if (i >= k - 1 && have == need) ans.push_back(i - k + 1);
                }
                return ans;
            }
            """
        ),
    ],
    "15-two-pointer-and-sliding-window-11-container-with-most-water": [
        cpp(
            r"""
            int maxArea(vector<int>& height) {
                if (height.size() < 2) return 0;
                int l = 0;
                int r = static_cast<int>(height.size()) - 1;
                int ans = 0;
                while (l < r) {
                    int area = min(height[l], height[r]) * (r - l);
                    ans = max(ans, area);
                    if (height[l] < height[r])
                        l++;
                    else
                        r--;
                }
                return ans;
            }
            """
        ),
    ],
    "15-two-pointer-and-sliding-window-12-trapping-rain-water": [
        cpp(
            r"""
            int trap(vector<int>& height) {
                if (height.size() < 3) return 0;
                int l = 0;
                int r = static_cast<int>(height.size()) - 1;
                int leftMax = 0;
                int rightMax = 0;
                int ans = 0;
                while (l < r) {
                    if (height[l] <= height[r]) {
                        if (height[l] >= leftMax)
                            leftMax = height[l];
                        else
                            ans += leftMax - height[l];
                        l++;
                    } else {
                        if (height[r] >= rightMax)
                            rightMax = height[r];
                        else
                            ans += rightMax - height[r];
                        r--;
                    }
                }
                return ans;
            }
            """
        ),
    ],
    "15-two-pointer-and-sliding-window-13-subarray-product-less-than-k": [
        cpp(
            r"""
            long long numSubarrayProductLessThanK(vector<int>& nums, int k) {
                if (k <= 1) return 0;
                long long product = 1;
                int l = 0;
                long long ans = 0;
                for (int r = 0; r < static_cast<int>(nums.size()); r++) {
                    product *= nums[r];
                    while (product >= k) product /= nums[l++];
                    ans += r - l + 1;
                }
                return ans;
            }
            """
        ),
    ],
    "15-two-pointer-and-sliding-window-14-number-of-subarrays-with-sum-at-most-k": [
        cpp(
            r"""
            long long countAtMostK(vector<int>& nums, long long k) {
                if (k < 0) return 0;
                long long sum = 0;
                long long ans = 0;
                int l = 0;
                for (int r = 0; r < static_cast<int>(nums.size()); r++) {
                    sum += nums[r];
                    while (sum > k) sum -= nums[l++];
                    ans += r - l + 1;
                }
                return ans;
            }
            """
        ),
    ],
    "15-two-pointer-and-sliding-window-15-count-subarrays-with-exactly-k-distinct-integers": [
        cpp(
            r"""
            long long atMostKDistinct(vector<int>& nums, int k) {
                if (k == 0) return 0;
                unordered_map<int, int> freq;
                int l = 0;
                long long ans = 0;
                for (int r = 0; r < nums.size(); r++) {
                    freq[nums[r]]++;
                    while (freq.size() > k) {
                        freq[nums[l]]--;
                        if (freq[nums[l]] == 0) freq.erase(nums[l]);
                        l++;
                    }
                    ans += r - l + 1;
                }
                return ans;
            }
            long long subarraysWithKDistinct(vector<int>& nums, int k) {
                return atMostKDistinct(nums, k) - atMostKDistinct(nums, k - 1);
            }
            """
        ),
    ],
    "15-two-pointer-and-sliding-window-16-minimum-size-subarray-sum": [
        cpp(
            r"""
            int minSubArrayLen(int target, vector<int>& nums) {
                int l = 0;
                long long sum = 0;
                int ans = INT_MAX;
                for (int r = 0; r < nums.size(); r++) {
                    sum += nums[r];
                    while (sum >= target) {
                        ans = min(ans, r - l + 1);
                        sum -= nums[l++];
                    }
                }
                return ans == INT_MAX ? 0 : ans;
            }
            """
        ),
    ],
    "15-two-pointer-and-sliding-window-17-longest-subarray-with-at-most-k-zeros": [
        cpp(
            r"""
            int longestOnes(vector<int>& nums, int k) {
                int l = 0;
                int zeros = 0;
                int ans = 0;
                for (int r = 0; r < nums.size(); r++) {
                    if (nums[r] == 0) zeros++;
                    while (zeros > k) {
                        if (nums[l] == 0) zeros--;
                        l++;
                    }
                    ans = max(ans, r - l + 1);
                }
                return ans;
            }
            """
        ),
    ],
    "15-two-pointer-and-sliding-window-18-minimum-swaps-to-group-all-1s": [
        cpp(
            r"""
            int minSwaps(vector<int>& nums) {
                int k = accumulate(nums.begin(), nums.end(), 0);
                if (k <= 1) return 0;
                int ones = 0;
                for (int i = 0; i < k; i++) ones += nums[i];
                int maxOnes = ones;
                for (int i = k; i < nums.size(); i++) {
                    ones += nums[i];
                    ones -= nums[i - k];
                    maxOnes = max(maxOnes, ones);
                }
                return k - maxOnes;
            }
            """
        ),
    ],
    "15-two-pointer-and-sliding-window-19-longest-subarray-with-sum-k-positive-numbers": [
        cpp(
            r"""
            int longestSumK(vector<int>& nums, long long k) {
                if (k <= 0) return 0;
                int l = 0;
                long long sum = 0;
                int ans = 0;
                for (int r = 0; r < static_cast<int>(nums.size()); r++) {
                    sum += nums[r];
                    while (sum > k) sum -= nums[l++];
                    if (sum == k) ans = max(ans, r - l + 1);
                }
                return ans;
            }
            """
        ),
    ],
    "15-two-pointer-and-sliding-window-20-longest-subarray-with-sum-k-negative-numbers-allowed": [
        cpp(
            r"""
            int longestSubarraySumK(vector<int>& nums, long long k) {
                unordered_map<long long, int> first;
                long long sum = 0;
                int ans = 0;
                for (int i = 0; i < nums.size(); i++) {
                    sum += nums[i];
                    if (sum == k) ans = i + 1;
                    if (!first.count(sum)) first[sum] = i;
                    if (first.count(sum - k)) ans = max(ans, i - first[sum - k]);
                }
                return ans;
            }
            """
        ),
    ],
    "16-prefix-sum-and-difference-array-1-subarray-sum-equals-k": [
        cpp(
            r"""
            long long subarraySum(vector<int>& nums, int k) {
                unordered_map<long long, long long> freq;
                freq[0] = 1;
                long long sum = 0;
                long long ans = 0;
                for (int x : nums) {
                    sum += x;
                    auto it = freq.find(sum - k);
                    if (it != freq.end()) ans += it->second;
                    freq[sum]++;
                }
                return ans;
            }
            """
        ),
    ],
    "16-prefix-sum-and-difference-array-6-count-subarrays-with-equal-0s-1s-and-2s": [
        cpp(
            r"""
            struct PairHash {
                size_t operator()(const pair<int, int>& p) const {
                    size_t h1 = hash<int>{}(p.first);
                    size_t h2 = hash<int>{}(p.second);
                    return h1 ^ (h2 + 0x9e3779b97f4a7c15ULL + (h1 << 6) + (h1 >> 2));
                }
            };
            long long countEqual012(vector<int>& arr) {
                unordered_map<pair<int, int>, long long, PairHash> freq;
                int c0 = 0, c1 = 0, c2 = 0;
                long long ans = 0;
                freq[{0, 0}] = 1;
                for (int x : arr) {
                    if (x == 0)
                        c0++;
                    else if (x == 1)
                        c1++;
                    else if (x == 2)
                        c2++;
                    else
                        continue;
                    pair<int, int> key = {c0 - c1, c1 - c2};
                    ans += freq[key];
                    freq[key]++;
                }
                return ans;
            }
            """
        ),
    ],
    "16-prefix-sum-and-difference-array-9-2d-prefix-sum": [
        cpp(
            r"""
            vector<vector<long long>> buildPrefix(vector<vector<int>>& mat) {
                if (mat.empty() || mat[0].empty()) return {{0}};
                int n = static_cast<int>(mat.size());
                int m = static_cast<int>(mat[0].size());
                vector<vector<long long>> pref(n + 1, vector<long long>(m + 1, 0));
                for (int i = 1; i <= n; i++) {
                    for (int j = 1; j <= m; j++) {
                        pref[i][j] = mat[i - 1][j - 1] + pref[i - 1][j] + pref[i][j - 1] - pref[i - 1][j - 1];
                    }
                }
                return pref;
            }
            long long query(vector<vector<long long>>& pref, int r1, int c1, int r2, int c2) {
                r1++;
                c1++;
                r2++;
                c2++;
                return pref[r2][c2] - pref[r1 - 1][c2] - pref[r2][c1 - 1] + pref[r1 - 1][c1 - 1];
            }
            """
        ),
    ],
    "16-prefix-sum-and-difference-array-12-maximum-subarray-sum-with-length-at-most-k": [
        cpp(
            r"""
            long long maxSumAtMostK(vector<int>& arr, int k) {
                if (arr.empty() || k <= 0) return 0;
                int n = static_cast<int>(arr.size());
                vector<long long> pref(n + 1, 0);
                for (int i = 0; i < n; i++) pref[i + 1] = pref[i] + arr[i];
                deque<int> dq;
                dq.push_back(0);
                long long ans = LLONG_MIN;
                for (int i = 1; i <= n; i++) {
                    while (!dq.empty() && dq.front() < i - k) dq.pop_front();
                    if (!dq.empty()) ans = max(ans, pref[i] - pref[dq.front()]);
                    while (!dq.empty() && pref[dq.back()] >= pref[i]) dq.pop_back();
                    dq.push_back(i);
                }
                return ans;
            }
            """
        ),
    ],
    "16-prefix-sum-and-difference-array-16-range-sum-query-with-coordinate-compression": [
        cpp(
            r"""
            struct CompressedPrefix {
                vector<long long> coords;
                vector<long long> pref;

                explicit CompressedPrefix(vector<pair<long long, long long>>& points) {
                    coords.reserve(points.size());
                    for (auto [x, value] : points) coords.push_back(x);
                    sort(coords.begin(), coords.end());
                    coords.erase(unique(coords.begin(), coords.end()), coords.end());
                    vector<long long> values(coords.size(), 0);
                    for (auto [x, value] : points) {
                        int idx = lower_bound(coords.begin(), coords.end(), x) - coords.begin();
                        values[idx] += value;
                    }
                    pref.assign(coords.size() + 1, 0);
                    for (int i = 0; i < static_cast<int>(coords.size()); i++) {
                        pref[i + 1] = pref[i] + values[i];
                    }
                }

                long long prefixQuery(long long x) const {
                    int idx = upper_bound(coords.begin(), coords.end(), x) - coords.begin();
                    return pref[idx];
                }

                long long rangeQuery(long long left, long long right) const {
                    if (left > right) return 0;
                    int leftIdx = lower_bound(coords.begin(), coords.end(), left) - coords.begin();
                    int rightIdx = upper_bound(coords.begin(), coords.end(), right) - coords.begin();
                    return pref[rightIdx] - pref[leftIdx];
                }
            };
            """
        ),
    ],
    "16-prefix-sum-and-difference-array-18-difference-array-sweep-line": [
        cpp(
            r"""
            pair<int, int> maximumOverlap(int n, vector<pair<int, int>>& intervals) {
                vector<int> diff(n + 2, 0);
                for (auto [l, r] : intervals) {
                    diff[l]++;
                    diff[r + 1]--;
                }
                int curr = 0;
                int bestPoint = 0;
                int bestCount = 0;
                for (int i = 0; i <= n; i++) {
                    curr += diff[i];
                    if (curr > bestCount) {
                        bestCount = curr;
                        bestPoint = i;
                    }
                }
                return {bestPoint, bestCount};
            }
            """
        ),
    ],
    "16-prefix-sum-and-difference-array-complexity-cheat-sheet": [],
    "14-greedy-1-activity-selection": [
        cpp(
            r"""
            int activitySelection(vector<pair<int, int>>& activities) {
                sort(activities.begin(), activities.end(), [](auto& a, auto& b) { return a.second < b.second; });
                int ans = 0;
                int lastEnd = INT_MIN;
                for (auto& [start, end] : activities) {
                    if (start >= lastEnd) {
                        ans++;
                        lastEnd = end;
                    }
                }
                return ans;
            }
            """
        ),
    ],
    "14-greedy-2-fractional-knapsack": [
        cpp(
            r"""
            double fractionalKnapsack(vector<int>& wt, vector<int>& val, int W) {
                int n = wt.size();
                vector<pair<double, int>> items;
                for (int i = 0; i < n; i++) {
                    items.push_back({(double)val[i] / wt[i], i});
                }
                sort(items.rbegin(), items.rend());
                double ans = 0;
                for (auto& [ratio, i] : items) {
                    if (W == 0) break;
                    int take = min(W, wt[i]);
                    ans += take * ratio;
                    W -= take;
                }
                return ans;
            }
            """
        ),
    ],
    "14-greedy-3-job-sequencing-with-deadlines": [
        cpp(
            r"""
            vector<int> jobSequencing(vector<pair<int, int>>& jobs) {
                sort(jobs.begin(), jobs.end(), [](auto& a, auto& b) { return a.second > b.second; });
                int maxDeadline = 0;
                for (auto& [deadline, profit] : jobs) maxDeadline = max(maxDeadline, deadline);
                vector<int> slot(maxDeadline + 1, -1);
                int count = 0, profit = 0;
                for (int i = 0; i < jobs.size(); i++) {
                    int deadline = jobs[i].first;
                    int value = jobs[i].second;
                    for (int t = min(deadline, maxDeadline); t >= 1; t--) {
                        if (slot[t] == -1) {
                            slot[t] = i;
                            count++;
                            profit += value;
                            break;
                        }
                    }
                }
                return {count, profit};
            }
            """
        ),
    ],
    "14-greedy-4-minimum-number-of-platforms": [
        cpp(
            r"""
            int minPlatforms(vector<int>& arrival, vector<int>& departure) {
                sort(arrival.begin(), arrival.end());
                sort(departure.begin(), departure.end());
                int i = 0, j = 0;
                int curr = 0, ans = 0;
                int n = arrival.size();
                while (i < n && j < n) {
                    if (arrival[i] <= departure[j]) {
                        curr++;
                        ans = max(ans, curr);
                        i++;
                    } else {
                        curr--;
                        j++;
                    }
                }
                return ans;
            }
            """
        ),
    ],
    "14-greedy-5-jump-game": [
        cpp(
            r"""
            bool canJump(vector<int>& nums) {
                int farthest = 0;
                for (int i = 0; i < nums.size(); i++) {
                    if (i > farthest) return false;
                    farthest = max(farthest, i + nums[i]);
                }
                return true;
            }
            """
        ),
    ],
    "14-greedy-6-jump-game-ii-minimum-jumps": [
        cpp(
            r"""
            int jump(vector<int>& nums) {
                int n = static_cast<int>(nums.size());
                if (n <= 1) return 0;
                int jumps = 0;
                int currentEnd = 0;
                int farthest = 0;
                for (int i = 0; i < n - 1; i++) {
                    if (i > farthest) return -1;
                    farthest = max(farthest, i + nums[i]);
                    if (i == currentEnd) {
                        jumps++;
                        currentEnd = farthest;
                        if (currentEnd >= n - 1) return jumps;
                    }
                }
                return currentEnd >= n - 1 ? jumps : -1;
            }
            """
        ),
    ],
    "14-greedy-7-gas-station": [
        cpp(
            r"""
            int canCompleteCircuit(vector<int>& gas, vector<int>& cost) {
                long long total = 0;
                long long tank = 0;
                int start = 0;
                for (int i = 0; i < static_cast<int>(gas.size()); i++) {
                    long long diff = static_cast<long long>(gas[i]) - cost[i];
                    total += diff;
                    tank += diff;
                    if (tank < 0) {
                        start = i + 1;
                        tank = 0;
                    }
                }
                return total >= 0 ? start : -1;
            }
            """
        ),
    ],
    "14-greedy-8-candy-distribution": [
        cpp(
            r"""
            int candy(vector<int>& ratings) {
                int n = ratings.size();
                vector<int> candies(n, 1);
                for (int i = 1; i < n; i++) {
                    if (ratings[i] > ratings[i - 1]) candies[i] = candies[i - 1] + 1;
                }
                for (int i = n - 2; i >= 0; i--) {
                    if (ratings[i] > ratings[i + 1]) candies[i] = max(candies[i], candies[i + 1] + 1);
                }
                return accumulate(candies.begin(), candies.end(), 0);
            }
            """
        ),
    ],
    "14-greedy-9-partition-labels": [
        cpp(
            r"""
            vector<int> partitionLabels(string s) {
                vector<int> last(26, 0);
                for (int i = 0; i < s.size(); i++) last[s[i] - 'a'] = i;
                vector<int> ans;
                int start = 0;
                int end = 0;
                for (int i = 0; i < s.size(); i++) {
                    end = max(end, last[s[i] - 'a']);
                    if (i == end) {
                        ans.push_back(end - start + 1);
                        start = i + 1;
                    }
                }
                return ans;
            }
            """
        ),
    ],
    "14-greedy-10-non-overlapping-intervals": [
        cpp(
            r"""
            int eraseOverlapIntervals(vector<vector<int>>& intervals) {
                sort(intervals.begin(), intervals.end(), [](auto& a, auto& b) { return a[1] < b[1]; });
                int removed = 0;
                int lastEnd = INT_MIN;
                for (auto& interval : intervals) {
                    if (interval[0] < lastEnd) {
                        removed++;
                    } else {
                        lastEnd = interval[1];
                    }
                }
                return removed;
            }
            """
        ),
    ],
    "14-greedy-11-minimum-arrows-to-burst-balloons": [
        cpp(
            r"""
            int findMinArrowShots(vector<vector<int>>& points) {
                if (points.empty()) return 0;
                sort(points.begin(), points.end(), [](auto& a, auto& b) { return a[1] < b[1]; });
                int arrows = 1;
                long long pos = points[0][1];
                for (int i = 1; i < points.size(); i++) {
                    if (points[i][0] > pos) {
                        arrows++;
                        pos = points[i][1];
                    }
                }
                return arrows;
            }
            """
        ),
    ],
    "14-greedy-12-huffman-coding": [
        cpp(
            r"""
            long long huffmanCost(vector<int>& freq) {
                priority_queue<long long, vector<long long>, greater<long long>> pq;
                for (int x : freq) pq.push(x);
                long long cost = 0;
                while (pq.size() > 1) {
                    long long a = pq.top();
                    pq.pop();
                    long long b = pq.top();
                    pq.pop();
                    long long sum = a + b;
                    cost += sum;
                    pq.push(sum);
                }
                return cost;
            }
            """
        ),
    ],
    "14-greedy-13-minimum-cost-to-connect-ropes": [
        cpp(
            r"""
            long long minCostRopes(vector<int>& ropes) {
                priority_queue<long long, vector<long long>, greater<long long>> pq;
                for (int x : ropes) pq.push(x);
                long long ans = 0;
                while (pq.size() > 1) {
                    long long a = pq.top();
                    pq.pop();
                    long long b = pq.top();
                    pq.pop();
                    long long sum = a + b;
                    ans += sum;
                    pq.push(sum);
                }
                return ans;
            }
            """
        ),
    ],
    "14-greedy-14-task-scheduler": [
        cpp(
            r"""
            int leastInterval(vector<char>& tasks, int n) {
                vector<int> freq(26, 0);
                for (char c : tasks) freq[c - 'A']++;
                int maxFreq = *max_element(freq.begin(), freq.end());
                int maxCount = 0;
                for (int f : freq) {
                    if (f == maxFreq) maxCount++;
                }
                int slots = (maxFreq - 1) * (n + 1) + maxCount;
                return max((int)tasks.size(), slots);
            }
            """
        ),
    ],
    "14-greedy-15-meeting-rooms-ii": [
        cpp(
            r"""
            int minMeetingRooms(vector<vector<int>>& intervals) {
                vector<int> start, finish;
                for (auto& x : intervals) {
                    start.push_back(x[0]);
                    finish.push_back(x[1]);
                }
                sort(start.begin(), start.end());
                sort(finish.begin(), finish.end());
                int i = 0, j = 0;
                int rooms = 0;
                int ans = 0;
                while (i < start.size()) {
                    if (start[i] < finish[j]) {
                        rooms++;
                        ans = max(ans, rooms);
                        i++;
                    } else {
                        rooms--;
                        j++;
                    }
                }
                return ans;
            }
            """
        ),
    ],
    "14-greedy-16-remove-k-digits": [
        cpp(
            r"""
            string removeKdigits(string num, int k) {
                if (k >= static_cast<int>(num.size())) return "0";
                string st;
                for (char c : num) {
                    while (!st.empty() && k > 0 && st.back() > c) {
                        st.pop_back();
                        k--;
                    }
                    st.push_back(c);
                }
                while (k > 0 && !st.empty()) {
                    st.pop_back();
                    k--;
                }
                int i = 0;
                while (i < static_cast<int>(st.size()) && st[i] == '0') i++;
                string ans = st.substr(i);
                return ans.empty() ? "0" : ans;
            }
            """
        ),
    ],
    "14-greedy-17-gas-station-prove-the-greedy-starting-point": [
        cpp(
            r"""
            int gasStation(vector<int>& gas, vector<int>& cost) {
                long long total = 0;
                long long tank = 0;
                int start = 0;
                for (int i = 0; i < static_cast<int>(gas.size()); i++) {
                    long long diff = static_cast<long long>(gas[i]) - cost[i];
                    tank += diff;
                    total += diff;
                    if (tank < 0) {
                        start = i + 1;
                        tank = 0;
                    }
                }
                return total >= 0 ? start : -1;
            }
            """
        ),
    ],
    "14-greedy-18-assign-cookies": [
        cpp(
            r"""
            int findContentChildren(vector<int>& g, vector<int>& s) {
                sort(g.begin(), g.end());
                sort(s.begin(), s.end());
                int i = 0;
                for (int cookie : s) {
                    if (i < g.size() && cookie >= g[i]) i++;
                }
                return i;
            }
            """
        ),
    ],
    "14-greedy-19-boats-to-save-people": [
        cpp(
            r"""
            int numRescueBoats(vector<int>& people, int limit) {
                if (people.empty()) return 0;
                sort(people.begin(), people.end());
                int l = 0;
                int r = static_cast<int>(people.size()) - 1;
                int boats = 0;
                while (l <= r) {
                    if (1LL * people[l] + people[r] <= limit) l++;
                    r--;
                    boats++;
                }
                return boats;
            }
            """
        ),
    ],
    "14-greedy-20-maximum-number-of-events-attended": [
        cpp(
            r"""
            int maxEvents(vector<vector<int>>& events) {
                sort(events.begin(), events.end());
                priority_queue<int, vector<int>, greater<int>> pq;
                int day = 0;
                int i = 0;
                int ans = 0;
                while (i < events.size() || !pq.empty()) {
                    if (pq.empty()) day = events[i][0];
                    while (i < events.size() && events[i][0] <= day) {
                        pq.push(events[i][1]);
                        i++;
                    }
                    while (!pq.empty() && pq.top() < day) pq.pop();
                    if (!pq.empty()) {
                        pq.pop();
                        ans++;
                        day++;
                    }
                }
                return ans;
            }
            """
        ),
    ],
    "19-backtracking-1-generate-all-subsets": [
        cpp(
            r"""
            void solve(int idx, vector<int>& arr, vector<int>& curr, vector<vector<int>>& ans) {
                if (idx == arr.size()) {
                    ans.push_back(curr);
                    return;
                }
                curr.push_back(arr[idx]);
                solve(idx + 1, arr, curr, ans);
                curr.pop_back();
                solve(idx + 1, arr, curr, ans);
            }
            vector<vector<int>> subsets(vector<int>& arr) {
                vector<vector<int>> ans;
                vector<int> curr;
                solve(0, arr, curr, ans);
                return ans;
            }
            """
        ),
    ],
    "19-backtracking-2-generate-all-subsets-with-duplicates": [
        cpp(
            r"""
            void solve(int start, vector<int>& arr, vector<int>& curr, vector<vector<int>>& ans) {
                ans.push_back(curr);
                for (int i = start; i < arr.size(); i++) {
                    if (i > start && arr[i] == arr[i - 1]) continue;
                    curr.push_back(arr[i]);
                    solve(i + 1, arr, curr, ans);
                    curr.pop_back();
                }
            }
            vector<vector<int>> subsetsWithDup(vector<int>& arr) {
                sort(arr.begin(), arr.end());
                vector<vector<int>> ans;
                vector<int> curr;
                solve(0, arr, curr, ans);
                return ans;
            }
            """
        ),
    ],
    "19-backtracking-3-generate-all-permutations": [
        cpp(
            r"""
            void solve(int idx, vector<int>& arr, vector<vector<int>>& ans) {
                if (idx == arr.size()) {
                    ans.push_back(arr);
                    return;
                }
                for (int i = idx; i < arr.size(); i++) {
                    swap(arr[idx], arr[i]);
                    solve(idx + 1, arr, ans);
                    swap(arr[idx], arr[i]);
                }
            }
            vector<vector<int>> permutations(vector<int>& arr) {
                vector<vector<int>> ans;
                solve(0, arr, ans);
                return ans;
            }
            """
        ),
    ],
    "19-backtracking-4-unique-permutations-with-duplicates": [
        cpp(
            r"""
            void solve(vector<int>& arr, vector<bool>& used, vector<int>& curr, vector<vector<int>>& ans) {
                if (curr.size() == arr.size()) {
                    ans.push_back(curr);
                    return;
                }
                for (int i = 0; i < arr.size(); i++) {
                    if (used[i]) continue;
                    if (i > 0 && arr[i] == arr[i - 1] && !used[i - 1]) continue;
                    used[i] = true;
                    curr.push_back(arr[i]);
                    solve(arr, used, curr, ans);
                    curr.pop_back();
                    used[i] = false;
                }
            }
            vector<vector<int>> permuteUnique(vector<int>& arr) {
                sort(arr.begin(), arr.end());
                vector<bool> used(arr.size(), false);
                vector<int> curr;
                vector<vector<int>> ans;
                solve(arr, used, curr, ans);
                return ans;
            }
            """
        ),
    ],
    "19-backtracking-5-n-queens": [
        cpp(
            r"""
            bool isSafe(int row, int col, vector<string>& board, int n) {
                for (int i = 0; i < row; i++) {
                    if (board[i][col] == 'Q') return false;
                }
                for (int i = row - 1, j = col - 1; i >= 0 && j >= 0; i--, j--) {
                    if (board[i][j] == 'Q') return false;
                }
                for (int i = row - 1, j = col + 1; i >= 0 && j < n; i--, j++) {
                    if (board[i][j] == 'Q') return false;
                }
                return true;
            }
            void solve(int row, vector<string>& board, vector<vector<string>>& ans, int n) {
                if (row == n) {
                    ans.push_back(board);
                    return;
                }
                for (int col = 0; col < n; col++) {
                    if (!isSafe(row, col, board, n)) continue;
                    board[row][col] = 'Q';
                    solve(row + 1, board, ans, n);
                    board[row][col] = '.';
                }
            }
            vector<vector<string>> solveNQueens(int n) {
                vector<string> board(n, string(n, '.'));
                vector<vector<string>> ans;
                solve(0, board, ans, n);
                return ans;
            }
            """
        ),
    ],
    "19-backtracking-6-n-queens-optimized-with-bitmasks": [
        cpp(
            r"""
            void solve(int row, int n, long long cols, long long diag1, long long diag2, long long& ans) {
                if (row == n) {
                    ans++;
                    return;
                }
                long long available = ((1LL << n) - 1) & ~(cols | diag1 | diag2);
                while (available) {
                    long long bit = available & -available;
                    available -= bit;
                    solve(row + 1, n, cols | bit, (diag1 | bit) << 1, (diag2 | bit) >> 1, ans);
                }
                }
            long long totalNQueens(int n) {
                if (n <= 0 || n >= 63) return 0;
                long long ans = 0;
                solve(0, n, 0, 0, 0, ans);
                return ans;
            }
            """
        ),
    ],
    "19-backtracking-7-combination-sum": [
        cpp(
            r"""
            void solve(int start, int target, vector<int>& arr, vector<int>& curr, vector<vector<int>>& ans) {
                if (target == 0) {
                    ans.push_back(curr);
                    return;
                }
                for (int i = start; i < static_cast<int>(arr.size()); i++) {
                    if (i > start && arr[i] == arr[i - 1]) continue;
                    if (arr[i] > target) break;
                    curr.push_back(arr[i]);
                    solve(i, target - arr[i], arr, curr, ans);
                    curr.pop_back();
                }
            }
            vector<vector<int>> combinationSum(vector<int>& arr, int target) {
                sort(arr.begin(), arr.end());
                vector<vector<int>> ans;
                vector<int> curr;
                solve(0, target, arr, curr, ans);
                return ans;
            }
            """
        ),
    ],
    "19-backtracking-8-combination-sum-ii": [
        cpp(
            r"""
            void solve(int start, int target, vector<int>& arr, vector<int>& curr, vector<vector<int>>& ans) {
                if (target == 0) {
                    ans.push_back(curr);
                    return;
                }
                for (int i = start; i < arr.size(); i++) {
                    if (i > start && arr[i] == arr[i - 1]) continue;
                    if (arr[i] > target) break;
                    curr.push_back(arr[i]);
                    solve(i + 1, target - arr[i], arr, curr, ans);
                    curr.pop_back();
                }
            }
            vector<vector<int>> combinationSum2(vector<int>& arr, int target) {
                sort(arr.begin(), arr.end());
                vector<vector<int>> ans;
                vector<int> curr;
                solve(0, target, arr, curr, ans);
                return ans;
            }
            """
        ),
    ],
    "19-backtracking-9-palindrome-partitioning": [
        cpp(
            r"""
            bool isPalindrome(string& s, int l, int r) {
                while (l < r) {
                    if (s[l++] != s[r--]) return false;
                }
                return true;
            }
            void solve(int start, string& s, vector<string>& curr, vector<vector<string>>& ans) {
                if (start == s.size()) {
                    ans.push_back(curr);
                    return;
                }
                for (int end = start; end < s.size(); end++) {
                    if (!isPalindrome(s, start, end)) continue;
                    curr.push_back(s.substr(start, end - start + 1));
                    solve(end + 1, s, curr, ans);
                    curr.pop_back();
                }
            }
            vector<vector<string>> partition(string s) {
                vector<vector<string>> ans;
                vector<string> curr;
                solve(0, s, curr, ans);
                return ans;
            }
            """
        ),
    ],
    "19-backtracking-10-sudoku-solver": [
        cpp(
            r"""
            bool solve(vector<vector<char>>& board) {
                for (int r = 0; r < 9; r++) {
                    for (int c = 0; c < 9; c++) {
                        if (board[r][c] != '.') continue;
                        for (char d = '1'; d <= '9'; d++) {
                            bool ok = true;
                            for (int i = 0; i < 9; i++) {
                                if (board[r][i] == d || board[i][c] == d) {
                                    ok = false;
                                    break;
                                }
                            }
                            int sr = (r / 3) * 3;
                            int sc = (c / 3) * 3;
                            for (int i = sr; i < sr + 3 && ok; i++) {
                                for (int j = sc; j < sc + 3; j++) {
                                    if (board[i][j] == d) {
                                        ok = false;
                                        break;
                                    }
                                }
                            }
                            if (!ok) continue;
                            board[r][c] = d;
                            if (solve(board)) return true;
                            board[r][c] = '.';
                        }
                        return false;
                    }
                }
                return true;
            }
            """
        ),
    ],
    "19-backtracking-11-rat-in-a-maze": [
        cpp(
            r"""
            void solve(int r, int c, vector<vector<int>>& maze, vector<vector<int>>& vis, string& path, vector<string>& ans) {
                int n = static_cast<int>(maze.size());
                int m = static_cast<int>(maze[0].size());
                if (r == n - 1 && c == m - 1) {
                    ans.push_back(path);
                    return;
                }
                int dr[] = {1, 0, 0, -1};
                int dc[] = {0, -1, 1, 0};
                char dir[] = {'D', 'L', 'R', 'U'};
                for (int k = 0; k < 4; k++) {
                    int nr = r + dr[k];
                    int nc = c + dc[k];
                    if (nr >= 0 && nr < n && nc >= 0 && nc < m && maze[nr][nc] && !vis[nr][nc]) {
                        vis[nr][nc] = 1;
                        path.push_back(dir[k]);
                        solve(nr, nc, maze, vis, path, ans);
                        path.pop_back();
                        vis[nr][nc] = 0;
                    }
                }
            }
            vector<string> ratInMaze(vector<vector<int>>& maze) {
                int n = static_cast<int>(maze.size());
                if (n == 0) return {};
                int m = static_cast<int>(maze[0].size());
                vector<string> ans;
                if (m == 0 || !maze[0][0] || !maze[n - 1][m - 1]) return ans;
                vector<vector<int>> vis(n, vector<int>(m, 0));
                string path;
                vis[0][0] = 1;
                solve(0, 0, maze, vis, path, ans);
                return ans;
            }
            """
        ),
    ],
    "19-backtracking-12-word-search": [
        cpp(
            r"""
            bool dfs(int r, int c, int idx, vector<vector<char>>& board, const string& word) {
                if (idx == static_cast<int>(word.size())) return true;
                int n = static_cast<int>(board.size());
                int m = static_cast<int>(board[0].size());
                if (r < 0 || r >= n || c < 0 || c >= m || board[r][c] != word[idx]) return false;
                char temp = board[r][c];
                board[r][c] = '#';
                bool found = dfs(r + 1, c, idx + 1, board, word) || dfs(r - 1, c, idx + 1, board, word) ||
                             dfs(r, c + 1, idx + 1, board, word) || dfs(r, c - 1, idx + 1, board, word);
                board[r][c] = temp;
                return found;
            }
            bool exist(vector<vector<char>>& board, string word) {
                if (word.empty()) return true;
                if (board.empty() || board[0].empty()) return false;
                for (int i = 0; i < static_cast<int>(board.size()); i++) {
                    for (int j = 0; j < static_cast<int>(board[0].size()); j++) {
                        if (dfs(i, j, 0, board, word)) return true;
                    }
                }
                return false;
            }
            """
        ),
    ],
    "19-backtracking-13-graph-coloring": [
        cpp(
            r"""
            bool solve(int node, int n, int k, vector<vector<int>>& graph, vector<int>& color) {
                if (node == n) return true;
                for (int c = 1; c <= k; c++) {
                    bool safe = true;
                    for (int v = 0; v < n; v++) {
                        if (graph[node][v] && color[v] == c) {
                            safe = false;
                            break;
                        }
                    }
                    if (!safe) continue;
                    color[node] = c;
                    if (solve(node + 1, n, k, graph, color)) return true;
                    color[node] = 0;
                }
                return false;
            }
            bool graphColoring(vector<vector<int>>& graph, int k) {
                int n = graph.size();
                vector<int> color(n, 0);
                return solve(0, n, k, graph, color);
            }
            """
        ),
    ],
    "19-backtracking-14-hamiltonian-path": [
        cpp(
            r"""
            bool solve(int u, int count, vector<vector<int>>& graph, vector<bool>& used) {
                if (count == graph.size()) return true;
                for (int v = 0; v < graph.size(); v++) {
                    if (graph[u][v] && !used[v]) {
                        used[v] = true;
                        if (solve(v, count + 1, graph, used)) return true;
                        used[v] = false;
                    }
                }
                return false;
            }
            bool hamiltonianPath(vector<vector<int>>& graph) {
                int n = graph.size();
                vector<bool> used(n, false);
                for (int start = 0; start < n; start++) {
                    used[start] = true;
                    if (solve(start, 1, graph, used)) return true;
                    used[start] = false;
                }
                return false;
            }
            """
        ),
    ],
    "19-backtracking-15-partition-array-into-k-equal-sum-subsets": [
        cpp(
            r"""
            bool solve(int idx, vector<int>& arr, vector<int>& bucket, int target) {
                if (idx == static_cast<int>(arr.size())) return true;
                for (int i = 0; i < static_cast<int>(bucket.size()); i++) {
                    if (bucket[i] + arr[idx] > target) continue;
                    if (i > 0 && bucket[i] == bucket[i - 1]) continue;
                    bucket[i] += arr[idx];
                    if (solve(idx + 1, arr, bucket, target)) return true;
                    bucket[i] -= arr[idx];
                    if (bucket[i] == 0) break;
                }
                return false;
            }
            bool canPartitionKSubsets(vector<int>& arr, int k) {
                if (k <= 0) return false;
                long long sum = accumulate(arr.begin(), arr.end(), 0LL);
                if (sum % k != 0) return false;
                int target = static_cast<int>(sum / k);
                sort(arr.rbegin(), arr.rend());
                if (!arr.empty() && arr[0] > target) return false;
                vector<int> bucket(k, 0);
                return solve(0, arr, bucket, target);
            }
            """
        ),
    ],
}

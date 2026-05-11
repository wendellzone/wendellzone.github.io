---
title: 力扣 Hot 100 题型归类与深度解析（Go 版）
date: 2026-05-11
tags: [算法, Go, 力扣, 刷题]
summary: 把 Hot 100 拆成 17 类套路，每题五段式：题目→抓手→关键观察→Go 代码→踩坑点。
---

# 力扣 Hot 100 题型归类与深度解析（Go 版）

> 这份文档不只是题解，而是 **「为什么会想到这么做」** 的思路记录。
> 每题五段式：**题目（含示例/约束）→ 抓手（暴力解 → 痛点）→ 关键观察 → Go 代码 → 踩坑点**。
> 把这 17 类套路吃透，Hot 100 基本就是套模板。脱离力扣站点也能独立刷完。

---

## 目录

1. [哈希](#1-哈希)
2. [双指针](#2-双指针)
3. [滑动窗口](#3-滑动窗口)
4. [子串与前缀和](#4-子串与前缀和)
5. [普通数组技巧](#5-普通数组技巧)
6. [矩阵](#6-矩阵)
7. [链表](#7-链表)
8. [二叉树](#8-二叉树)
9. [图论](#9-图论)
10. [回溯](#10-回溯)
11. [二分查找](#11-二分查找)
12. [栈与单调栈](#12-栈与单调栈)
13. [堆](#13-堆)
14. [贪心](#14-贪心)
15. [一维动态规划](#15-一维动态规划)
16. [多维动态规划](#16-多维动态规划)
17. [技巧题](#17-技巧题)

---

## 1. 哈希

### 总思想

**遇到「查存在 / 查上次出现位置 / 查计数」三连问，几乎必上哈希表**。
哈希表本质是把"在数组里搜一个值"从 O(n) 压到 O(1)。代价是 O(n) 空间。

判断该不该用哈希的两个信号：
- 你正打算写一个内层循环去找某个值；
- 这个内层循环找的东西**只依赖值本身**，不依赖位置顺序。

### 1.1 两数之和（LC 1）

**题目**：给定整数数组 `nums` 和目标值 `target`，返回数组中**和为 target 的两个下标**（每种输入只对应一个答案，同一元素不能用两次）。
- 示例：`nums=[2,7,11,15], target=9` → `[0,1]`（因为 2+7=9）。
- 约束：`2 ≤ len(nums) ≤ 10⁴`，`-10⁹ ≤ nums[i], target ≤ 10⁹`。

**抓手**：暴力两层循环 O(n²)。痛点是「内层在重复做查找」。

**关键观察**：当我看到 `x` 时，我真正想知道的是「**之前**有没有出现过 `target-x`」。这是一个"过去发生过什么"的查询 → 哈希表天然胜任。所以**边遍历边记录**，每个数只看一次。

```go
func twoSum(nums []int, target int) []int {
    seen := make(map[int]int)             // value -> index
    for i, x := range nums {
        if j, ok := seen[target-x]; ok {
            return []int{j, i}
        }
        seen[x] = i                        // 注意：先查后存，避免自己配自己
    }
    return nil
}
```

**踩坑点**：必须**先查再存**。如果先存再查，遇到 `nums=[3,3], target=6` 时，第一个 3 自己配自己就被错误命中。

---

### 1.2 字母异位词分组（LC 49）

**题目**：给定字符串数组，把**字母组成相同**（异位词）的字符串归为一组，返回所有分组（顺序不限）。
- 示例：`["eat","tea","tan","ate","nat","bat"]` → `[["eat","tea","ate"],["tan","nat"],["bat"]]`。
- 约束：`1 ≤ len ≤ 10⁴`，每串长度 0–100，仅小写字母。

**抓手**：判断两串是不是异位词 → 排序后相等 / 字母频次相等。
**关键观察**：把"判等"升级为"分组"，最自然的方式就是**给每组一个唯一 key**，然后用 `map[key][]string` 收集。

```go
func groupAnagrams(strs []string) [][]string {
    g := make(map[string][]string)
    for _, s := range strs {
        b := []byte(s)
        sort.Slice(b, func(i, j int) bool { return b[i] < b[j] })
        g[string(b)] = append(g[string(b)], s)
    }
    res := make([][]string, 0, len(g))
    for _, v := range g { res = append(res, v) }
    return res
}
```

**进阶**：避开排序，用长度 26 的频次数组转字符串当 key，O(n·k) 而不是 O(n·k log k)。

---

### 1.3 最长连续序列（LC 128）

**题目**：给定**未排序**整数数组，找出**最长连续元素序列**（数值上连续，例如 1,2,3,4）的长度。要求 O(n)。
- 示例：`[100,4,200,1,3,2]` → `4`（最长是 1,2,3,4）。
- 约束：`0 ≤ len ≤ 10⁵`，`-10⁹ ≤ nums[i] ≤ 10⁹`。

**抓手**：排序就 O(n log n)，但题目要求 O(n)。
**关键观察**：把数都丢进集合后，**只从"序列起点"开始扩展**。判断 `x` 是不是起点：`x-1` 不在集合里。这样每个数最多被扩展中访问一次，整体仍是 O(n)。

```go
func longestConsecutive(nums []int) int {
    set := make(map[int]struct{})
    for _, x := range nums { set[x] = struct{}{} }
    best := 0
    for x := range set {
        if _, ok := set[x-1]; ok { continue }       // 不是起点，跳过
        y := x
        for { if _, ok := set[y+1]; !ok { break }; y++ }
        if y-x+1 > best { best = y - x + 1 }
    }
    return best
}
```

**踩坑点**：少了"只从起点扩"那一步，会变成 O(n²)。

---

## 2. 双指针

### 总思想

双指针 = **用单调性把搜索空间砍半**。
- **同向指针**：读写分离（移动零）、快慢（环检测）。
- **相向指针**：每步移动「不可能更优」的那一侧，从而 O(n) 解决貌似 O(n²) 的问题（盛水容器、三数之和）。

判断能不能用双指针：当某一侧移动后，**另一侧不可能再回头**——这就是单调性。

### 2.1 移动零（LC 283）

**题目**：原地把数组中所有 `0` 移到末尾，**保持非零元素的相对顺序**。
- 示例：`[0,1,0,3,12]` → `[1,3,12,0,0]`。
- 约束：`1 ≤ len ≤ 10⁴`，要求**原地**操作，最小化写入。

```go
func moveZeroes(nums []int) {
    w := 0
    for r := 0; r < len(nums); r++ {
        if nums[r] != 0 {
            nums[w], nums[r] = nums[r], nums[w]
            w++
        }
    }
}
```

**思路**：写指针 `w` 永远指向"下一个非零应放位置"。读指针扫全数组，遇非零就交换并推进 `w`。

---

### 2.2 盛最多水的容器（LC 11）

**题目**：长度为 n 的非负整数数组 `h`，第 i 根柱子高 `h[i]`。从中选两根柱子配上 x 轴构成容器，**返回最大盛水量**。
- 示例：`h=[1,8,6,2,5,4,8,3,7]` → `49`（柱 1 与柱 8，高 min(8,7)=7，宽 7）。
- 约束：`2 ≤ n ≤ 10⁵`，`0 ≤ h[i] ≤ 10⁴`。

**抓手**：暴力 O(n²)。
**关键观察**：面积 = `min(h[l], h[r]) * (r-l)`。两端夹逼时——
- 移动**长板**：宽度变小，高度仍受短板限制（不会变大）→ 必劣。
- 移动**短板**：宽度变小，但短板可能升高 → 有变大的可能。

所以**永远只动短板**。

```go
func maxArea(h []int) int {
    l, r, ans := 0, len(h)-1, 0
    for l < r {
        area := (r - l) * min(h[l], h[r])
        if area > ans { ans = area }
        if h[l] < h[r] { l++ } else { r-- }
    }
    return ans
}
```

---

### 2.3 三数之和（LC 15）

**题目**：返回数组中所有**和为 0** 的三元组 `[nums[i], nums[j], nums[k]]`，结果中**不能重复**。
- 示例：`[-1,0,1,2,-1,-4]` → `[[-1,-1,2],[-1,0,1]]`。
- 约束：`3 ≤ len ≤ 3000`，`-10⁵ ≤ nums[i] ≤ 10⁵`。

**抓手**：枚举 i，剩下问题就是"在 `nums[i+1:]` 里找两数和等于 `-nums[i]`"——退化为两数之和。
**关键观察**：先排序，让相向双指针的单调性成立；同时排序后**去重也变得简单**（相邻相等就跳过）。

```go
func threeSum(nums []int) [][]int {
    sort.Ints(nums)
    var res [][]int
    n := len(nums)
    for i := 0; i < n-2; i++ {
        if nums[i] > 0 { break }                       // 剪枝
        if i > 0 && nums[i] == nums[i-1] { continue }  // i 去重
        l, r := i+1, n-1
        for l < r {
            s := nums[i] + nums[l] + nums[r]
            switch {
            case s == 0:
                res = append(res, []int{nums[i], nums[l], nums[r]})
                for l < r && nums[l] == nums[l+1] { l++ }
                for l < r && nums[r] == nums[r-1] { r-- }
                l++; r--
            case s < 0: l++
            default:    r--
            }
        }
    }
    return res
}
```

**踩坑点**：去重要在**找到一个解之后**做，否则会漏掉 `[-2,-2,4]` 这种相邻相等却合法的情况。

---

### 2.4 接雨水（LC 42）

**题目**：n 个非负整数表示宽度 1 的柱形图，计算雨后能**接多少单位**的雨水。
- 示例：`[0,1,0,2,1,0,1,3,2,1,2,1]` → `6`。
- 约束：`1 ≤ n ≤ 2·10⁴`，`0 ≤ h[i] ≤ 10⁵`。

**抓手**：每个位置能接的水 = `min(左侧最大, 右侧最大) - 自身高度`。
**关键观察（双指针）**：哪边矮，哪边的水位**一定**由该侧最大值决定。所以可以放心地"低的那侧自己结算并前进"。

```go
func trap(h []int) int {
    l, r := 0, len(h)-1
    lMax, rMax, ans := 0, 0, 0
    for l < r {
        if h[l] < h[r] {
            if h[l] >= lMax { lMax = h[l] } else { ans += lMax - h[l] }
            l++
        } else {
            if h[r] >= rMax { rMax = h[r] } else { ans += rMax - h[r] }
            r--
        }
    }
    return ans
}
```

**为什么不会算错**：当 `h[l] < h[r]`，右边一定有人 ≥ `h[r] > h[l]`，所以左侧位置的右最大一定 ≥ `h[r] ≥ lMax`，瓶颈在 `lMax`。

---

## 3. 滑动窗口

### 总思想

适用于："**右扩越界、左缩复位**"的子串问题。两个判定：
1. 子串长度可变，问题问**最长/最短/恰好**；
2. 窗口属性有**单调性**：右扩属性单调变坏，左缩属性单调变好。

### 3.1 无重复字符的最长子串（LC 3）

**题目**：找出字符串 `s` 中**不含重复字符**的最长**子串**长度（子串连续）。
- 示例：`"abcabcbb"` → `3`（"abc"）；`"pwwkew"` → `3`（"wke"）。
- 约束：`0 ≤ len(s) ≤ 5·10⁴`，含字母数字符号空格。

```go
func lengthOfLongestSubstring(s string) int {
    last := make(map[byte]int)
    l, ans := 0, 0
    for r := 0; r < len(s); r++ {
        if i, ok := last[s[r]]; ok && i >= l {
            l = i + 1
        }
        last[s[r]] = r
        if r-l+1 > ans { ans = r - l + 1 }
    }
    return ans
}
```

**踩坑点**：`i >= l` 必须判，否则会被"已经被左指针越过"的旧记录误导。

---

### 3.2 找到字符串中所有字母异位词（LC 438）

**题目**：在 `s` 中找出所有 `p` 的**字母异位词**子串的起始下标。
- 示例：`s="cbaebabacd", p="abc"` → `[0,6]`；`s="abab", p="ab"` → `[0,1,2]`。
- 约束：`1 ≤ len(s), len(p) ≤ 3·10⁴`，仅小写字母。

**关键观察**：异位词长度固定 → **定长滑窗**。每次右扩一格、左侧自动出一格。Go 数组支持 `==` 直接比较，非常方便。

```go
func findAnagrams(s, p string) []int {
    if len(s) < len(p) { return nil }
    var need, win [26]int
    for i := 0; i < len(p); i++ {
        need[p[i]-'a']++
        win[s[i]-'a']++
    }
    var res []int
    if win == need { res = append(res, 0) }
    for i := len(p); i < len(s); i++ {
        win[s[i]-'a']++
        win[s[i-len(p)]-'a']--
        if win == need { res = append(res, i-len(p)+1) }
    }
    return res
}
```

---

## 4. 子串与前缀和

### 总思想

凡是「子数组和 / 异或」类问题，先想前缀和：`S[j] - S[i] = k` ↔ `S[i] = S[j] - k` → 哈希表查"出现过的 S[i]"。

### 4.1 和为 K 的子数组（LC 560）

**题目**：返回数组中**和等于 k** 的连续子数组的**个数**。
- 示例：`nums=[1,1,1], k=2` → `2`；`nums=[1,2,3], k=3` → `2`。
- 约束：`1 ≤ len ≤ 2·10⁴`，`-1000 ≤ nums[i] ≤ 1000`，`-10⁷ ≤ k ≤ 10⁷`。

```go
func subarraySum(nums []int, k int) int {
    cnt := map[int]int{0: 1}     // 关键：空前缀算一次
    s, ans := 0, 0
    for _, x := range nums {
        s += x
        ans += cnt[s-k]
        cnt[s]++
    }
    return ans
}
```

**踩坑点**：`cnt[0]=1` 必须有。否则当从开头到 j 这段本身 `=k` 时会漏算。

---

### 4.2 滑动窗口最大值（LC 239，单调队列）

**题目**：长度为 k 的窗口从左滑到右，返回**每个窗口位置的最大值**组成的数组。
- 示例：`nums=[1,3,-1,-3,5,3,6,7], k=3` → `[3,3,5,5,6,7]`。
- 约束：`1 ≤ len ≤ 10⁵`，`1 ≤ k ≤ len`。

**关键观察**：维护一个**单调递减的双端队列**（存下标）：
- 队首始终是窗口内最大值；
- 新元素入队前，把队尾比它小的全弹掉（它们永无翻身之日）；
- 队首过期就弹出。

```go
func maxSlidingWindow(nums []int, k int) []int {
    var dq []int
    res := make([]int, 0, len(nums)-k+1)
    for i, x := range nums {
        for len(dq) > 0 && nums[dq[len(dq)-1]] <= x {
            dq = dq[:len(dq)-1]
        }
        dq = append(dq, i)
        if dq[0] <= i-k { dq = dq[1:] }
        if i >= k-1 { res = append(res, nums[dq[0]]) }
    }
    return res
}
```

---

### 4.3 最小覆盖子串（LC 76）

**题目**：在 `s` 中找出**包含 `t` 所有字符**（含重复个数）的**最短**子串；如不存在返回 `""`。
- 示例：`s="ADOBECODEBANC", t="ABC"` → `"BANC"`。
- 约束：`1 ≤ len(s), len(t) ≤ 10⁵`，含大小写字母。

**关键观察**：不定长滑窗。维护 `match` 表示已凑齐的字符种类数，等于 `len(need)` 时窗口合法、开始左缩。

```go
func minWindow(s, t string) string {
    need := make(map[byte]int)
    for i := 0; i < len(t); i++ { need[t[i]]++ }
    win := make(map[byte]int)
    match, l := 0, 0
    bestL, bestLen := 0, math.MaxInt32
    for r := 0; r < len(s); r++ {
        c := s[r]
        if _, ok := need[c]; ok {
            win[c]++
            if win[c] == need[c] { match++ }
        }
        for match == len(need) {
            if r-l+1 < bestLen { bestL, bestLen = l, r-l+1 }
            d := s[l]
            if _, ok := need[d]; ok {
                if win[d] == need[d] { match-- }
                win[d]--
            }
            l++
        }
    }
    if bestLen == math.MaxInt32 { return "" }
    return s[bestL : bestL+bestLen]
}
```

---

## 5. 普通数组技巧

### 5.1 最大子数组和（LC 53，Kadane）

**题目**：找出整数数组中具有**最大和**的连续子数组（至少一个元素），返回该最大和。
- 示例：`[-2,1,-3,4,-1,2,1,-5,4]` → `6`（子数组 [4,-1,2,1]）。
- 约束：`1 ≤ len ≤ 10⁵`，`-10⁴ ≤ nums[i] ≤ 10⁴`。

**关键观察**：以 i 结尾的最大子数组和 `f(i) = max(nums[i], f(i-1)+nums[i])`。要么"续上"，要么"另起炉灶"。如果之前累计是负数，就直接抛弃。

```go
func maxSubArray(nums []int) int {
    cur, ans := nums[0], nums[0]
    for i := 1; i < len(nums); i++ {
        cur = max(nums[i], cur+nums[i])
        if cur > ans { ans = cur }
    }
    return ans
}
```

---

### 5.2 合并区间（LC 56）

**题目**：以二维数组形式给出若干区间 `[start, end]`，**合并所有有重叠的区间**并返回。
- 示例：`[[1,3],[2,6],[8,10],[15,18]]` → `[[1,6],[8,10],[15,18]]`。
- 约束：`1 ≤ len ≤ 10⁴`，`0 ≤ start ≤ end ≤ 10⁴`。

**关键观察**：按起点排序后，区间间的关系简化为"和上一个合不合得上"。

```go
func merge(a [][]int) [][]int {
    sort.Slice(a, func(i, j int) bool { return a[i][0] < a[j][0] })
    res := [][]int{a[0]}
    for _, x := range a[1:] {
        last := res[len(res)-1]
        if x[0] <= last[1] {
            if x[1] > last[1] { last[1] = x[1] }
        } else {
            res = append(res, x)
        }
    }
    return res
}
```

---

### 5.3 轮转数组（LC 189）

**题目**：将数组向右**轮转 k** 步（原地修改）。
- 示例：`[1,2,3,4,5,6,7], k=3` → `[5,6,7,1,2,3,4]`。
- 约束：`1 ≤ len ≤ 10⁵`，`0 ≤ k ≤ 10⁵`。

**关键观察**：三次反转就行——整体翻 → 翻前 k → 翻后 n-k。

```go
func rotate(nums []int, k int) {
    k %= len(nums)
    rev := func(l, r int) {
        for l < r { nums[l], nums[r] = nums[r], nums[l]; l++; r-- }
    }
    rev(0, len(nums)-1); rev(0, k-1); rev(k, len(nums)-1)
}
```

---

### 5.4 除自身以外的乘积（LC 238）

**题目**：返回数组 `answer`，其中 `answer[i]` 等于 `nums` 中**除 `nums[i]` 外其余元素的乘积**。**不允许除法**，要求 O(n)。
- 示例：`[1,2,3,4]` → `[24,12,8,6]`。
- 约束：`2 ≤ len ≤ 10⁵`，保证乘积在 32 位整数范围内。

**关键观察**：每个位置 = 左侧乘积 × 右侧乘积。两遍扫：先算左前缀积放进答案，再从右往左乘上后缀积。

```go
func productExceptSelf(nums []int) []int {
    n := len(nums)
    res := make([]int, n)
    res[0] = 1
    for i := 1; i < n; i++ { res[i] = res[i-1] * nums[i-1] }
    R := 1
    for i := n - 1; i >= 0; i-- {
        res[i] *= R
        R *= nums[i]
    }
    return res
}
```

---

### 5.5 缺失的第一个正数（LC 41）

**题目**：未排序整数数组，找出其中**没有出现的最小正整数**。要求 O(n) 时间、O(1) 额外空间。
- 示例：`[1,2,0]` → `3`；`[3,4,-1,1]` → `2`；`[7,8,9,11,12]` → `1`。
- 约束：`1 ≤ len ≤ 10⁵`，`-2³¹ ≤ nums[i] ≤ 2³¹-1`。

**抓手**：哈希集合 O(n) 时间 O(n) 空间，题目卡 O(1) 空间。
**关键观察**：答案一定在 `[1, n+1]` 范围。把数组本身当哈希——把值 x 放到下标 x-1（"萝卜各自归位"）。

```go
func firstMissingPositive(nums []int) int {
    n := len(nums)
    for i := 0; i < n; i++ {
        for nums[i] >= 1 && nums[i] <= n && nums[nums[i]-1] != nums[i] {
            j := nums[i] - 1
            nums[i], nums[j] = nums[j], nums[i]
        }
    }
    for i := 0; i < n; i++ {
        if nums[i] != i+1 { return i + 1 }
    }
    return n + 1
}
```

**踩坑点**：内层用 `for`（不是 `if`），交换后新落到 i 的元素也要继续归位；`nums[nums[i]-1] != nums[i]` 防重复元素死循环。

---

## 6. 矩阵

### 6.1 矩阵置零（LC 73）

**题目**：m×n 矩阵中若某元素为 0，把其所在**整行整列**全部置为 0。要求**原地**操作，进阶：O(1) 额外空间。
- 示例：`[[1,1,1],[1,0,1],[1,1,1]]` → `[[1,0,1],[0,0,0],[1,0,1]]`。
- 约束：`1 ≤ m,n ≤ 200`，`-2³¹ ≤ m[i][j] ≤ 2³¹-1`。

**关键观察**：用第 0 行、第 0 列**自身**作标记位。但要先单独记下"第 0 行/列原本有没有 0"，最后再处理它们。

```go
func setZeroes(m [][]int) {
    M, N := len(m), len(m[0])
    row0, col0 := false, false
    for j := 0; j < N; j++ { if m[0][j] == 0 { row0 = true; break } }
    for i := 0; i < M; i++ { if m[i][0] == 0 { col0 = true; break } }
    for i := 1; i < M; i++ {
        for j := 1; j < N; j++ {
            if m[i][j] == 0 { m[i][0], m[0][j] = 0, 0 }
        }
    }
    for i := 1; i < M; i++ {
        for j := 1; j < N; j++ {
            if m[i][0] == 0 || m[0][j] == 0 { m[i][j] = 0 }
        }
    }
    if row0 { for j := 0; j < N; j++ { m[0][j] = 0 } }
    if col0 { for i := 0; i < M; i++ { m[i][0] = 0 } }
}
```

---

### 6.2 螺旋矩阵（LC 54）

**题目**：m×n 矩阵，按**顺时针螺旋顺序**返回矩阵中所有元素。
- 示例：`[[1,2,3],[4,5,6],[7,8,9]]` → `[1,2,3,6,9,8,7,4,5]`。
- 约束：`1 ≤ m,n ≤ 10`，`-100 ≤ m[i][j] ≤ 100`。

**关键观察**：维护四边界 top/bot/l/r，走完一条边就把边界收一格。第三、四条边要判空，避免单行/单列重复扫。

```go
func spiralOrder(m [][]int) []int {
    if len(m) == 0 { return nil }
    top, bot, l, r := 0, len(m)-1, 0, len(m[0])-1
    var res []int
    for top <= bot && l <= r {
        for j := l; j <= r; j++ { res = append(res, m[top][j]) }
        top++
        for i := top; i <= bot; i++ { res = append(res, m[i][r]) }
        r--
        if top <= bot {
            for j := r; j >= l; j-- { res = append(res, m[bot][j]) }
            bot--
        }
        if l <= r {
            for i := bot; i >= top; i-- { res = append(res, m[i][l]) }
            l++
        }
    }
    return res
}
```

---

### 6.3 旋转图像（LC 48）

**题目**：n×n 矩阵原地**顺时针旋转 90°**，不能开辅助矩阵。
- 示例：`[[1,2,3],[4,5,6],[7,8,9]]` → `[[7,4,1],[8,5,2],[9,6,3]]`。
- 约束：`n == m.length == m[0].length`，`1 ≤ n ≤ 20`。

**关键观察**：顺时针 90° = **沿主对角线转置 + 每行翻转**。

```go
func rotateImage(m [][]int) {
    n := len(m)
    for i := 0; i < n; i++ {
        for j := i + 1; j < n; j++ {
            m[i][j], m[j][i] = m[j][i], m[i][j]
        }
    }
    for i := 0; i < n; i++ {
        for l, r := 0, n-1; l < r; l, r = l+1, r-1 {
            m[i][l], m[i][r] = m[i][r], m[i][l]
        }
    }
}
```

---

### 6.4 搜索二维矩阵 II（LC 240）

**题目**：m×n 矩阵，每行从左到右升序、每列从上到下升序。判断 `target` 是否存在。
- 示例：`m=[[1,4,7,11],[2,5,8,12],[3,6,9,16],[10,13,14,17]], target=5` → `true`。
- 约束：`1 ≤ m,n ≤ 300`，`-10⁹ ≤ m[i][j], target ≤ 10⁹`。

**关键观察**：从**右上角**出发，往左变小，往下变大——把矩阵当 BST。

```go
func searchMatrix(m [][]int, t int) bool {
    if len(m) == 0 { return false }
    i, j := 0, len(m[0])-1
    for i < len(m) && j >= 0 {
        switch {
        case m[i][j] == t: return true
        case m[i][j] > t:  j--
        default:           i++
        }
    }
    return false
}
```

**踩坑点**：左上、右下都是"两边都更大/都更小"，没单调性，只能从右上或左下出发。

---

## 7. 链表

### 总思想

三大法宝：
- **dummy 哨兵**：避免 head 单独讨论；
- **快慢指针**：找中点 / 判环 / 找倒数第 K；
- **三指针反转**：`prev/cur/next` 形成肌肉记忆。

### 7.1 反转链表（LC 206）

**题目**：反转一个单链表，返回新头节点。
- 示例：`1→2→3→4→5` → `5→4→3→2→1`。
- 约束：节点数 `0 ≤ n ≤ 5000`，`-5000 ≤ Val ≤ 5000`。

```go
func reverseList(head *ListNode) *ListNode {
    var prev *ListNode
    cur := head
    for cur != nil {
        nxt := cur.Next
        cur.Next = prev
        prev, cur = cur, nxt
    }
    return prev
}
```

**踩坑点**：必须先存 `nxt = cur.Next` 再改 `cur.Next`，否则链断。

---

### 7.2 环形链表 II（LC 142，Floyd 判圈）

**题目**：判断链表中是否有环；如有，返回**入环的第一个节点**，否则返回 `nil`。要求 O(1) 空间。
- 示例：`3→2→0→-4→(回到 2)` → 返回值为 2 的节点。
- 约束：节点数 `0 ≤ n ≤ 10⁴`。

**数学事实**：相遇后，从 head 和"相遇点"同速出发，必在入环口相遇。
**为什么**：设 head 到环口距离 a，环口到相遇点 b，环长 L。慢走 a+b，快走 2(a+b)=a+b+nL → a = nL-b。也就是从 head 走 a 步等于从相遇点绕几圈再走到环口。

```go
func detectCycle(head *ListNode) *ListNode {
    slow, fast := head, head
    for fast != nil && fast.Next != nil {
        slow = slow.Next
        fast = fast.Next.Next
        if slow == fast {
            p := head
            for p != slow { p = p.Next; slow = slow.Next }
            return p
        }
    }
    return nil
}
```

---

### 7.3 合并两个升序链表（LC 21）

**题目**：把两条升序链表合并为一条新的升序链表。
- 示例：`1→2→4` 与 `1→3→4` → `1→1→2→3→4→4`。
- 约束：每条链表 `0 ≤ n ≤ 50`，`-100 ≤ Val ≤ 100`。

```go
func mergeTwoLists(a, b *ListNode) *ListNode {
    dummy := &ListNode{}
    tail := dummy
    for a != nil && b != nil {
        if a.Val <= b.Val { tail.Next = a; a = a.Next } else { tail.Next = b; b = b.Next }
        tail = tail.Next
    }
    if a != nil { tail.Next = a } else { tail.Next = b }
    return dummy.Next
}
```

---

### 7.4 K 个一组翻转链表（LC 25）

**题目**：每 **k 个节点为一组**翻转链表，剩余不足 k 个保持原序。要求 O(1) 额外空间。
- 示例：`1→2→3→4→5, k=2` → `2→1→4→3→5`；`k=3` → `3→2→1→4→5`。
- 约束：`1 ≤ k ≤ n ≤ 5000`。

**关键观察**：先看够不够 k 个，够就翻转这一段，把翻转后的尾巴接到下一段头部。

```go
func reverseKGroup(head *ListNode, k int) *ListNode {
    rev := func(a, b *ListNode) *ListNode {
        var prev *ListNode
        cur := a
        for cur != b {
            nxt := cur.Next
            cur.Next = prev
            prev, cur = cur, nxt
        }
        return prev
    }
    a, b := head, head
    for i := 0; i < k; i++ {
        if b == nil { return head }
        b = b.Next
    }
    newHead := rev(a, b)
    a.Next = reverseKGroup(b, k)
    return newHead
}
```

---

### 7.5 LRU 缓存（LC 146）

**题目**：实现 `LRUCache(capacity)` 数据结构，支持：
- `Get(key)`：存在则返回值并视为最近使用，否则返回 -1；
- `Put(key, value)`：若 key 存在则更新值；否则插入；超过容量时淘汰**最久未使用**项。两操作均要求 **O(1)**。
- 示例：`cap=2`；`put(1,1); put(2,2); get(1)→1; put(3,3)` 淘汰 key=2；`get(2)→-1`。
- 约束：`1 ≤ capacity ≤ 3000`，调用次数 ≤ 2·10⁵。

**关键观察**：要 O(1) get/put，需要"哈希定位 + 双向链表维序"两件套。哈希用来 O(1) 查到节点，双链表用来 O(1) 移动到头/淘汰尾。

```go
type node struct {
    key, val   int
    prev, next *node
}
type LRUCache struct {
    cap        int
    m          map[int]*node
    head, tail *node       // 哨兵：head 是 MRU 端，tail 是 LRU 端
}

func Constructor(capacity int) LRUCache {
    h, t := &node{}, &node{}
    h.next, t.prev = t, h
    return LRUCache{cap: capacity, m: make(map[int]*node), head: h, tail: t}
}
func (c *LRUCache) remove(n *node)   { n.prev.next, n.next.prev = n.next, n.prev }
func (c *LRUCache) addFront(n *node) {
    n.next, n.prev = c.head.next, c.head
    c.head.next.prev, c.head.next = n, n
}
func (c *LRUCache) Get(key int) int {
    if n, ok := c.m[key]; ok { c.remove(n); c.addFront(n); return n.val }
    return -1
}
func (c *LRUCache) Put(key, val int) {
    if n, ok := c.m[key]; ok { n.val = val; c.remove(n); c.addFront(n); return }
    if len(c.m) == c.cap {
        lru := c.tail.prev
        c.remove(lru); delete(c.m, lru.key)
    }
    n := &node{key: key, val: val}
    c.addFront(n); c.m[key] = n
}
```

**踩坑点**：节点里必须存 `key`，淘汰尾节点时要反查 map 删 key。

---

## 8. 二叉树

### 总思想

二叉树问题 90% 用递归：
- **自顶向下**：父传子（参数携带累计信息）；
- **自底向上**：子传父（返回值汇总）。

写不出递归的两个常见原因：
1. 没想清楚"子树返回什么"；
2. 把"经过当前节点的最优解"和"以当前节点为根的最优解"混在一起算。

### 8.1 最大深度（LC 104）

**题目**：返回二叉树**最大深度**（根到最远叶子节点的节点数）。
- 示例：`[3,9,20,null,null,15,7]` → `3`。
- 约束：节点数 `0 ≤ n ≤ 10⁴`。

```go
func maxDepth(root *TreeNode) int {
    if root == nil { return 0 }
    return 1 + max(maxDepth(root.Left), maxDepth(root.Right))
}
```

---

### 8.2 翻转二叉树（LC 226）

**题目**：把整棵二叉树**左右翻转**（每个节点的左右子树互换），返回新根。
- 示例：`[4,2,7,1,3,6,9]` → `[4,7,2,9,6,3,1]`。
- 约束：节点数 `0 ≤ n ≤ 100`。

```go
func invertTree(root *TreeNode) *TreeNode {
    if root == nil { return nil }
    root.Left, root.Right = invertTree(root.Right), invertTree(root.Left)
    return root
}
```

---

### 8.3 对称二叉树（LC 101）

**题目**：判断一棵树是否**轴对称**（左右镜像）。
- 示例：`[1,2,2,3,4,4,3]` → `true`；`[1,2,2,null,3,null,3]` → `false`。
- 约束：节点数 `1 ≤ n ≤ 1000`。

**思路**：单棵树自我对比 → 用辅助函数比较两棵子树是否互为镜像。

```go
func isSymmetric(root *TreeNode) bool {
    var same func(a, b *TreeNode) bool
    same = func(a, b *TreeNode) bool {
        if a == nil || b == nil { return a == b }
        return a.Val == b.Val && same(a.Left, b.Right) && same(a.Right, b.Left)
    }
    return root == nil || same(root.Left, root.Right)
}
```

---

### 8.4 二叉树的直径（LC 543）

**题目**：返回树中任意两节点之间**路径长度的最大值**（路径上的边数，**可以不经过根**）。
- 示例：`[1,2,3,4,5]` → `3`（路径 4→2→1→3 或 5→2→1→3）。
- 约束：节点数 `1 ≤ n ≤ 10⁴`。

**关键观察**：递归返回的是"**单边**最大深度"，最终答案是遍历所有节点时的"两边深度之和"最大值。**返回值** vs **全局答案**分离的经典模式。

```go
func diameterOfBinaryTree(root *TreeNode) int {
    ans := 0
    var depth func(n *TreeNode) int
    depth = func(n *TreeNode) int {
        if n == nil { return 0 }
        l, r := depth(n.Left), depth(n.Right)
        if l+r > ans { ans = l + r }
        return 1 + max(l, r)
    }
    depth(root)
    return ans
}
```

---

### 8.5 层序遍历（LC 102，BFS）

**题目**：返回二叉树**逐层从左到右**的节点值，每层一个数组。
- 示例：`[3,9,20,null,null,15,7]` → `[[3],[9,20],[15,7]]`。
- 约束：节点数 `0 ≤ n ≤ 2000`。

```go
func levelOrder(root *TreeNode) [][]int {
    if root == nil { return nil }
    var res [][]int
    q := []*TreeNode{root}
    for len(q) > 0 {
        size := len(q)
        level := make([]int, 0, size)
        for i := 0; i < size; i++ {
            n := q[i]
            level = append(level, n.Val)
            if n.Left != nil  { q = append(q, n.Left) }
            if n.Right != nil { q = append(q, n.Right) }
        }
        res = append(res, level)
        q = q[size:]
    }
    return res
}
```

**模板要点**：`size := len(q)` 决定"这一层有多少节点"，是 BFS 分层的关键。

---

### 8.6 验证二叉搜索树（LC 98）

**题目**：判断一棵树是否是合法 **BST**（左子树所有节点严格小于根，右子树所有节点严格大于根，左右子树各自也是 BST）。
- 示例：`[2,1,3]` → `true`；`[5,1,4,null,null,3,6]` → `false`（4 在 5 的右子树却小于 5）。
- 约束：节点数 `1 ≤ n ≤ 10⁴`，`-2³¹ ≤ Val ≤ 2³¹-1`。

**坑**：只判断 `root.Val > root.Left.Val && root.Val < root.Right.Val` 是错的——BST 要求**整棵左子树都小于当前节点**。
**关键观察**：递归时携带"上下界"。

```go
func isValidBST(root *TreeNode) bool {
    var dfs func(n *TreeNode, lo, hi int) bool
    dfs = func(n *TreeNode, lo, hi int) bool {
        if n == nil { return true }
        if n.Val <= lo || n.Val >= hi { return false }
        return dfs(n.Left, lo, n.Val) && dfs(n.Right, n.Val, hi)
    }
    return dfs(root, math.MinInt64, math.MaxInt64)
}
```

---

### 8.7 最近公共祖先（LC 236）

**题目**：给定二叉树中**两个节点 p、q**，返回它们的**最近公共祖先**（LCA：使二者都在其子树里、深度最大的节点；一个节点也可以是自己的祖先）。
- 示例：`[3,5,1,6,2,0,8,null,null,7,4]`，`p=5, q=1` → `3`；`p=5, q=4` → `5`。
- 约束：节点数 `2 ≤ n ≤ 10⁵`，所有 Val 唯一，p、q 一定存在于树中。

**思路（信号汇报模式）**：每个节点向父亲汇报"我的子树里有没有 p 或 q"。
- 当前节点是 p 或 q：返回自己；
- 左右都汇报回非空 → 当前节点就是 LCA；
- 否则把非空那一侧上传。

```go
func lowestCommonAncestor(root, p, q *TreeNode) *TreeNode {
    if root == nil || root == p || root == q { return root }
    L := lowestCommonAncestor(root.Left,  p, q)
    R := lowestCommonAncestor(root.Right, p, q)
    if L != nil && R != nil { return root }
    if L != nil { return L }
    return R
}
```

---

### 8.8 二叉树最大路径和（LC 124）

**题目**：路径定义为从任一节点出发、按父子边到达任一节点的序列（**至少含一个节点**），返回所有路径**节点值之和的最大值**。
- 示例：`[1,2,3]` → `6`；`[-10,9,20,null,null,15,7]` → `42`（15→20→7）。
- 约束：节点数 `1 ≤ n ≤ 3·10⁴`，`-1000 ≤ Val ≤ 1000`。

**关键观察**：和直径同套路。
- **返回值**：从当前节点向下延伸的**单边**最大和（要么不延伸返 0，要么走一边）；
- **全局答案**：以当前节点为最高点 = 自身 + max(左单边,0) + max(右单边,0)。

```go
func maxPathSum(root *TreeNode) int {
    ans := math.MinInt32
    var dfs func(n *TreeNode) int
    dfs = func(n *TreeNode) int {
        if n == nil { return 0 }
        l := max(dfs(n.Left),  0)
        r := max(dfs(n.Right), 0)
        if n.Val+l+r > ans { ans = n.Val + l + r }
        return n.Val + max(l, r)
    }
    dfs(root)
    return ans
}
```

**踩坑点**：负贡献要被截断为 0；ans 初值要给 `MinInt32`，因为答案至少是某节点本身的值。

---

### 8.9 由前序和中序构造二叉树（LC 105）

**题目**：根据二叉树的**前序遍历** `pre` 和**中序遍历** `in` 还原原树（保证无重复值）。
- 示例：`pre=[3,9,20,15,7], in=[9,3,15,20,7]` → 树 `[3,9,20,null,null,15,7]`。
- 约束：节点数 `1 ≤ n ≤ 3000`，所有值唯一。

**关键观察**：前序第一个 = 根；在中序里找根的位置，左右切分中序，长度反推出前序的左右切分。

```go
func buildTree(pre, in []int) *TreeNode {
    if len(pre) == 0 { return nil }
    root := &TreeNode{Val: pre[0]}
    k := 0
    for in[k] != pre[0] { k++ }
    root.Left  = buildTree(pre[1:1+k], in[:k])
    root.Right = buildTree(pre[1+k:],  in[k+1:])
    return root
}
```

---

## 9. 图论

### 9.1 岛屿数量（LC 200）

**题目**：m×n 的 0/1 网格，1 代表陆地、0 代表水，**上下左右**相连的陆地构成岛屿。返回岛屿数量。
- 示例：`[["1","1","0","0"],["1","1","0","0"],["0","0","1","0"],["0","0","0","1"]]` → `3`。
- 约束：`1 ≤ m,n ≤ 300`。

```go
func numIslands(g [][]byte) int {
    if len(g) == 0 { return 0 }
    m, n := len(g), len(g[0])
    var dfs func(i, j int)
    dfs = func(i, j int) {
        if i < 0 || i >= m || j < 0 || j >= n || g[i][j] != '1' { return }
        g[i][j] = '0'
        dfs(i+1, j); dfs(i-1, j); dfs(i, j+1); dfs(i, j-1)
    }
    cnt := 0
    for i := 0; i < m; i++ {
        for j := 0; j < n; j++ {
            if g[i][j] == '1' { cnt++; dfs(i, j) }
        }
    }
    return cnt
}
```

---

### 9.2 腐烂的橘子（LC 994，多源 BFS）

**题目**：网格中 0=空、1=新鲜、2=腐烂；每分钟所有腐烂橘子会让**四邻**新鲜橘子腐烂。返回所有橘子都腐烂所需**最少分钟数**；若有橘子永远不会腐烂，返回 -1。
- 示例：`[[2,1,1],[1,1,0],[0,1,1]]` → `4`；`[[0,2]]` → `0`（无新鲜）。
- 约束：`1 ≤ m,n ≤ 10`。

**关键观察**：所有腐烂橘子**同时**扩散 → 多源 BFS。把所有起点一次性塞进队列。

```go
func orangesRotting(g [][]int) int {
    m, n := len(g), len(g[0])
    var q [][2]int
    fresh := 0
    for i := 0; i < m; i++ {
        for j := 0; j < n; j++ {
            switch g[i][j] {
            case 2: q = append(q, [2]int{i, j})
            case 1: fresh++
            }
        }
    }
    dirs := [4][2]int{{1,0},{-1,0},{0,1},{0,-1}}
    minutes := 0
    for len(q) > 0 && fresh > 0 {
        size := len(q)
        for k := 0; k < size; k++ {
            x, y := q[k][0], q[k][1]
            for _, d := range dirs {
                ni, nj := x+d[0], y+d[1]
                if ni >= 0 && ni < m && nj >= 0 && nj < n && g[ni][nj] == 1 {
                    g[ni][nj] = 2
                    fresh--
                    q = append(q, [2]int{ni, nj})
                }
            }
        }
        q = q[size:]
        minutes++
    }
    if fresh > 0 { return -1 }
    return minutes
}
```

**踩坑点**：先判 `len(q)>0 && fresh>0` 再 `minutes++`，否则没新鲜橘子时还会多算一分钟。

---

### 9.3 课程表（LC 207，Kahn 拓扑排序）

**题目**：共 `numCourses` 门课，`prerequisites[i] = [a,b]` 表示**先修 b 才能修 a**。判断能否修完所有课程（等价：判断有向图无环）。
- 示例：`numCourses=2, prerequisites=[[1,0]]` → `true`；`[[1,0],[0,1]]` → `false`。
- 约束：`1 ≤ numCourses ≤ 2000`，`0 ≤ len(prerequisites) ≤ 5000`。

```go
func canFinish(num int, pre [][]int) bool {
    g := make([][]int, num)
    in := make([]int, num)
    for _, p := range pre {
        g[p[1]] = append(g[p[1]], p[0])
        in[p[0]]++
    }
    var q []int
    for i, d := range in { if d == 0 { q = append(q, i) } }
    done := 0
    for len(q) > 0 {
        u := q[0]; q = q[1:]
        done++
        for _, v := range g[u] {
            in[v]--
            if in[v] == 0 { q = append(q, v) }
        }
    }
    return done == num
}
```

---

### 9.4 实现 Trie（LC 208）

**题目**：实现前缀树 `Trie`，支持：
- `Insert(word)`：插入字符串；
- `Search(word)`：是否存在该完整字符串；
- `StartsWith(prefix)`：是否存在以该串为**前缀**的字符串。
- 示例：`insert("apple"); search("apple")→true; search("app")→false; startsWith("app")→true; insert("app"); search("app")→true`。
- 约束：`1 ≤ len(word/prefix) ≤ 2000`，仅小写字母，调用次数 ≤ 3·10⁴。

```go
type Trie struct {
    children [26]*Trie
    end      bool
}
func (t *Trie) Insert(w string) {
    cur := t
    for i := 0; i < len(w); i++ {
        c := w[i] - 'a'
        if cur.children[c] == nil { cur.children[c] = &Trie{} }
        cur = cur.children[c]
    }
    cur.end = true
}
func (t *Trie) find(w string) *Trie {
    cur := t
    for i := 0; i < len(w); i++ {
        c := w[i] - 'a'
        if cur.children[c] == nil { return nil }
        cur = cur.children[c]
    }
    return cur
}
func (t *Trie) Search(w string) bool     { n := t.find(w); return n != nil && n.end }
func (t *Trie) StartsWith(p string) bool { return t.find(p) != nil }
```

---

## 10. 回溯

### 总思想

回溯 = **决策树 DFS + 现场恢复**。模板：

```
func dfs(状态) {
    if 终止条件 { 收答案; return }
    for 每个可选分支 {
        做选择
        dfs(...)
        撤销选择
    }
}
```

**剪枝是回溯的灵魂**：先排序、再判同层重复，是去重通用招式。

### 10.1 全排列（LC 46）

**题目**：给定**互不相同**的整数数组，返回**所有可能的全排列**（任意顺序）。
- 示例：`[1,2,3]` → `[[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]`。
- 约束：`1 ≤ len ≤ 6`，`-10 ≤ nums[i] ≤ 10`。

```go
func permute(nums []int) [][]int {
    n := len(nums)
    used := make([]bool, n)
    path := make([]int, 0, n)
    var res [][]int
    var dfs func()
    dfs = func() {
        if len(path) == n {
            cp := make([]int, n); copy(cp, path)
            res = append(res, cp); return
        }
        for i := 0; i < n; i++ {
            if used[i] { continue }
            used[i] = true; path = append(path, nums[i])
            dfs()
            path = path[:len(path)-1]; used[i] = false
        }
    }
    dfs()
    return res
}
```

**踩坑点**：收答案时**必须拷贝** `path`，否则后续修改会污染已收的答案。

---

### 10.2 子集（LC 78）

**题目**：给定**互不相同**的整数数组，返回所有可能的子集（**幂集**），不能含重复子集，顺序不限。
- 示例：`[1,2,3]` → `[[],[1],[2],[1,2],[3],[1,3],[2,3],[1,2,3]]`。
- 约束：`1 ≤ len ≤ 10`，`-10 ≤ nums[i] ≤ 10`。

```go
func subsets(nums []int) [][]int {
    var res [][]int
    var path []int
    var dfs func(start int)
    dfs = func(start int) {
        cp := make([]int, len(path)); copy(cp, path)
        res = append(res, cp)
        for i := start; i < len(nums); i++ {
            path = append(path, nums[i])
            dfs(i + 1)
            path = path[:len(path)-1]
        }
    }
    dfs(0)
    return res
}
```

---

### 10.3 组合总和（LC 39，元素可重复使用）

**题目**：给定**无重复**正整数数组 `candidates` 和目标 `target`，找出所有**和为 target** 的组合（同一数字可**无限次**使用）。组合无序，结果集不能重复。
- 示例：`c=[2,3,6,7], target=7` → `[[2,2,3],[7]]`；`c=[2,3,5], target=8` → `[[2,2,2,2],[2,3,3],[3,5]]`。
- 约束：`1 ≤ len ≤ 30`，`2 ≤ c[i] ≤ 40`，`1 ≤ target ≤ 40`。

**思路**：和子集类似，但下一层可以再选自己（`dfs(i)` 而不是 `dfs(i+1)`）。

```go
func combinationSum(c []int, target int) [][]int {
    sort.Ints(c)
    var res [][]int
    var path []int
    var dfs func(start, rem int)
    dfs = func(start, rem int) {
        if rem == 0 {
            cp := make([]int, len(path)); copy(cp, path)
            res = append(res, cp); return
        }
        for i := start; i < len(c); i++ {
            if c[i] > rem { break }
            path = append(path, c[i])
            dfs(i, rem-c[i])
            path = path[:len(path)-1]
        }
    }
    dfs(0, target)
    return res
}
```

---

### 10.4 括号生成（LC 22）

**题目**：生成 `n` 对括号能组成的**所有合法**括号串。
- 示例：`n=3` → `["((()))","(()())","(())()","()(())","()()()"]`。
- 约束：`1 ≤ n ≤ 8`。

**两条剪枝**：
- 左括号还剩才能加 `(`：`l < n`；
- 右括号必须**比左少**才能加 `)`：`r < l`。

```go
func generateParenthesis(n int) []string {
    var res []string
    var dfs func(s string, l, r int)
    dfs = func(s string, l, r int) {
        if len(s) == 2*n { res = append(res, s); return }
        if l < n  { dfs(s+"(", l+1, r) }
        if r < l  { dfs(s+")", l, r+1) }
    }
    dfs("", 0, 0)
    return res
}
```

---

### 10.5 单词搜索（LC 79）

**题目**：m×n 字母网格，判断 `word` 是否能由**相邻**（上下左右）格子拼出，**同一格子不能重复使用**。
- 示例：`board=[["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word="ABCCED"` → `true`；`word="SEE"` → `true`；`word="ABCB"` → `false`。
- 约束：`1 ≤ m,n ≤ 6`，`1 ≤ len(word) ≤ 15`。

**关键观察**：标准矩阵 DFS+回溯。访问过的格临时改成 `#` 防重入，回溯时改回。

```go
func exist(board [][]byte, word string) bool {
    m, n := len(board), len(board[0])
    var dfs func(i, j, k int) bool
    dfs = func(i, j, k int) bool {
        if k == len(word) { return true }
        if i < 0 || i >= m || j < 0 || j >= n || board[i][j] != word[k] { return false }
        tmp := board[i][j]
        board[i][j] = '#'
        ok := dfs(i+1,j,k+1) || dfs(i-1,j,k+1) || dfs(i,j+1,k+1) || dfs(i,j-1,k+1)
        board[i][j] = tmp
        return ok
    }
    for i := 0; i < m; i++ {
        for j := 0; j < n; j++ {
            if dfs(i, j, 0) { return true }
        }
    }
    return false
}
```

---

### 10.6 N 皇后（LC 51）

**题目**：在 n×n 棋盘上放 n 个皇后，**任意两个皇后都不能同行、同列、同对角线**。返回所有合法摆放方案，每个方案是 n 个长度为 n 的字符串（'Q' 表示皇后，'.' 表示空格）。
- 示例：`n=4` → `[[".Q..","...Q","Q...","..Q."],["..Q.","Q...","...Q",".Q.."]]`。
- 约束：`1 ≤ n ≤ 9`。

**关键观察**：按行放，每行只放一个，所以只需查"列、撇对角、捺对角"是否冲突。
- 撇对角 `↗`：`row + col` 相同；
- 捺对角 `↘`：`row - col` 相同。

```go
func solveNQueens(n int) [][]string {
    cols := make(map[int]bool)
    d1, d2 := make(map[int]bool), make(map[int]bool)
    pos := make([]int, n)
    var res [][]string
    var dfs func(row int)
    dfs = func(row int) {
        if row == n {
            board := make([]string, n)
            for i, c := range pos {
                b := make([]byte, n)
                for j := range b { b[j] = '.' }
                b[c] = 'Q'
                board[i] = string(b)
            }
            res = append(res, board); return
        }
        for c := 0; c < n; c++ {
            if cols[c] || d1[row+c] || d2[row-c] { continue }
            cols[c], d1[row+c], d2[row-c] = true, true, true
            pos[row] = c
            dfs(row + 1)
            cols[c], d1[row+c], d2[row-c] = false, false, false
        }
    }
    dfs(0)
    return res
}
```

---

## 11. 二分查找

### 总思想

二分的本质不是"在排序数组里找一个值"，而是 **「在一个具备单调性的判定函数上找分界点」**。
推荐统一写**左闭右开** `[l, r)`，循环 `l < r`，最后返 `l`。

### 11.1 搜索插入位置（LC 35）

**题目**：升序数组中查找 `target`，存在则返回下标，否则返回**应当插入**的下标。要求 O(log n)。
- 示例：`[1,3,5,6], target=5` → `2`；`[1,3,5,6], target=2` → `1`；`[1,3,5,6], target=7` → `4`。
- 约束：`1 ≤ len ≤ 10⁴`，`-10⁴ ≤ nums[i], target ≤ 10⁴`，互不相同。

**判定函数**：`nums[i] >= target`，找第一个满足的位置。

```go
func searchInsert(nums []int, target int) int {
    l, r := 0, len(nums)
    for l < r {
        m := l + (r-l)/2
        if nums[m] >= target { r = m } else { l = m + 1 }
    }
    return l
}
```

---

### 11.2 在排序数组中查找元素的首尾位置（LC 34）

**题目**：升序数组里给一个 `target`，返回它出现的**起止下标** `[first, last]`。如果不存在返回 `[-1,-1]`。要求 O(log n)。
- 示例：`[5,7,7,8,8,10], target=8` → `[3,4]`；`target=6` → `[-1,-1]`。
- 约束：`0 ≤ len ≤ 10⁵`。

**思路**：两次二分。先找"第一个 ≥ target"，再找"第一个 > target"，两者夹出区间。

```go
func searchRange(nums []int, t int) []int {
    lower := func(x int) int {
        l, r := 0, len(nums)
        for l < r {
            m := l + (r-l)/2
            if nums[m] >= x { r = m } else { l = m + 1 }
        }
        return l
    }
    a := lower(t)
    if a == len(nums) || nums[a] != t { return []int{-1, -1} }
    return []int{a, lower(t+1) - 1}
}
```

---

### 11.3 搜索旋转排序数组（LC 33）

**题目**：原本升序的不重复数组在某个轴点被**旋转**过（如 `[0,1,2,4,5,6,7]→[4,5,6,7,0,1,2]`），找出 `target` 的下标，不存在返回 -1。要求 O(log n)。
- 示例：`nums=[4,5,6,7,0,1,2], target=0` → `4`；`target=3` → `-1`。
- 约束：`1 ≤ len ≤ 5000`，所有值唯一。

**关键观察**：旋转数组从中间砍一刀，**至少有一边是有序的**。每次判断目标是否落在有序的那半，进而决定走哪边。

```go
func search(nums []int, t int) int {
    l, r := 0, len(nums)-1
    for l <= r {
        m := (l + r) / 2
        if nums[m] == t { return m }
        if nums[l] <= nums[m] {                          // 左半有序
            if nums[l] <= t && t < nums[m] { r = m - 1 } else { l = m + 1 }
        } else {                                         // 右半有序
            if nums[m] < t && t <= nums[r] { l = m + 1 } else { r = m - 1 }
        }
    }
    return -1
}
```

**踩坑点**：判断有序用 `nums[l] <= nums[m]` 而不是 `<`，因为 m 可能等于 l。

---

### 11.4 寻找两个正序数组的中位数（LC 4）

**题目**：两个升序数组 `a, b`，长度分别为 m、n，返回它们合并后的**中位数**。要求 **O(log(m+n))**。
- 示例：`a=[1,3], b=[2]` → `2.0`；`a=[1,2], b=[3,4]` → `2.5`。
- 约束：`0 ≤ m,n ≤ 1000`，`1 ≤ m+n ≤ 2000`。

**思路**：转化为"找第 k 小"——在两数组里找一条**分割线**，让左半总数等于 (m+n+1)/2 且左半都 ≤ 右半。在较短数组上二分 i，另一边 `j = k - i`。

```go
func findMedianSortedArrays(a, b []int) float64 {
    if len(a) > len(b) { a, b = b, a }
    m, n := len(a), len(b)
    k := (m + n + 1) / 2
    l, r := 0, m
    for l <= r {
        i := (l + r) / 2
        j := k - i
        aL, aR := math.MinInt32, math.MaxInt32
        bL, bR := math.MinInt32, math.MaxInt32
        if i > 0 { aL = a[i-1] };  if i < m { aR = a[i] }
        if j > 0 { bL = b[j-1] };  if j < n { bR = b[j] }
        if aL <= bR && bL <= aR {
            if (m+n)%2 == 1 { return float64(max(aL, bL)) }
            return float64(max(aL, bL)+min(aR, bR)) / 2.0
        } else if aL > bR { r = i - 1 } else { l = i + 1 }
    }
    return 0
}
```

**为什么挑较短数组二分**：保证 i 不让 j 越界。

---

## 12. 栈与单调栈

### 总思想

**栈**适合"嵌套结构"和"最近未匹配"问题（括号、字符串解码）。
**单调栈**专治"下一个更大/更小"——每个元素入栈一次、出栈一次，整体 O(n)。

### 12.1 有效括号（LC 20）

**题目**：判断字符串 `s` 是否是合法括号串，括号包含 `(){}[]`，每种左括号必须由**相同类型且顺序正确**的右括号闭合。
- 示例：`"()[]{}"` → `true`；`"(]"` → `false`；`"([)]"` → `false`；`"{[]}"` → `true`。
- 约束：`1 ≤ len ≤ 10⁴`。

```go
func isValid(s string) bool {
    pair := map[byte]byte{')': '(', ']': '[', '}': '{'}
    var st []byte
    for i := 0; i < len(s); i++ {
        c := s[i]
        if c == '(' || c == '[' || c == '{' {
            st = append(st, c)
        } else {
            if len(st) == 0 || st[len(st)-1] != pair[c] { return false }
            st = st[:len(st)-1]
        }
    }
    return len(st) == 0
}
```

---

### 12.2 最小栈（LC 155）

**题目**：设计一个支持 `Push/Pop/Top/GetMin` 四操作**全部 O(1)** 的栈。
- 示例：依次 `push(-2); push(0); push(-3); getMin()→-3; pop(); top()→0; getMin()→-2`。
- 约束：调用次数 ≤ 3·10⁴；只有非空时才会调 Pop/Top/GetMin。

**关键观察**：维护一个辅助栈，存"截止当前的最小值"，与主栈同步 push/pop。

```go
type MinStack struct{ s, m []int }
func ConstructorMS() MinStack { return MinStack{} }
func (st *MinStack) Push(x int) {
    st.s = append(st.s, x)
    if len(st.m) == 0 || x < st.m[len(st.m)-1] {
        st.m = append(st.m, x)
    } else {
        st.m = append(st.m, st.m[len(st.m)-1])
    }
}
func (st *MinStack) Pop()        { st.s = st.s[:len(st.s)-1]; st.m = st.m[:len(st.m)-1] }
func (st *MinStack) Top() int    { return st.s[len(st.s)-1] }
func (st *MinStack) GetMin() int { return st.m[len(st.m)-1] }
```

---

### 12.3 字符串解码（LC 394）

**题目**：解码字符串规则 `k[encoded_string]` 表示 `encoded_string` 重复 k 次。可嵌套，输入合法。
- 示例：`"3[a]2[bc]"` → `"aaabcbc"`；`"3[a2[c]]"` → `"accaccacc"`；`"2[abc]3[cd]ef"` → `"abcabccdcdcdef"`。
- 约束：`1 ≤ len ≤ 30`，`1 ≤ k ≤ 300`。

**思路**：双栈——数字栈保存"当前层倍数"，字符串栈保存"当前层之前已拼好的串"。遇 `[` 入栈，遇 `]` 弹出并组合。

```go
func decodeString(s string) string {
    var nums []int
    var strs []string
    cur := ""
    k := 0
    for i := 0; i < len(s); i++ {
        c := s[i]
        switch {
        case c >= '0' && c <= '9':
            k = k*10 + int(c-'0')
        case c == '[':
            nums = append(nums, k); k = 0
            strs = append(strs, cur); cur = ""
        case c == ']':
            times := nums[len(nums)-1]; nums = nums[:len(nums)-1]
            prev := strs[len(strs)-1]; strs = strs[:len(strs)-1]
            cur = prev + strings.Repeat(cur, times)
        default:
            cur += string(c)
        }
    }
    return cur
}
```

**踩坑点**：数字可能多位，要用 `k = k*10 + ...` 累加。

---

### 12.4 每日温度（LC 739，单调递减栈）

**题目**：每天温度 `t[i]`，返回 `ans[i]` 表示**几天后会出现更高温度**；如果之后再无更高温度，则置 0。
- 示例：`[73,74,75,71,69,72,76,73]` → `[1,1,4,2,1,1,0,0]`。
- 约束：`1 ≤ len ≤ 10⁵`，`30 ≤ t[i] ≤ 100`。

**关键观察**：栈里存"还没找到答案的下标"，对应温度**单调递减**。新进来一个更高温度时，把所有比它低的弹出，它们的答案就是 `当前下标 - 弹出下标`。

```go
func dailyTemperatures(t []int) []int {
    ans := make([]int, len(t))
    var st []int
    for i, x := range t {
        for len(st) > 0 && t[st[len(st)-1]] < x {
            j := st[len(st)-1]; st = st[:len(st)-1]
            ans[j] = i - j
        }
        st = append(st, i)
    }
    return ans
}
```

---

### 12.5 柱状图最大矩形（LC 84）

**题目**：宽度为 1 的柱子高度数组 `h`，求柱状图中能勾勒出的**最大矩形面积**。
- 示例：`[2,1,5,6,2,3]` → `10`（宽 2、高 5 的矩形）。
- 约束：`1 ≤ len ≤ 10⁵`，`0 ≤ h[i] ≤ 10⁴`。

**关键观察**：以**每根柱子作为最矮柱**能延伸出多宽 → 找它的"左右第一个更矮"。**单调递增栈** + 左右哨兵 0 简化边界。

```go
func largestRectangleArea(h []int) int {
    h = append([]int{0}, h...)
    h = append(h, 0)
    var st []int
    ans := 0
    for i, x := range h {
        for len(st) > 0 && h[st[len(st)-1]] > x {
            top := st[len(st)-1]; st = st[:len(st)-1]
            w := i - st[len(st)-1] - 1
            if h[top]*w > ans { ans = h[top] * w }
        }
        st = append(st, i)
    }
    return ans
}
```

**关键算式**：`w = i - st.top() - 1`。`i` 是右边第一个更矮，弹出后的新栈顶是左边第一个不更高的。

---

## 13. 堆

### 总思想

堆 = 半排序的优先队列。两类高频套路：
- **维护 K 个最值**：用大小为 K 的小顶堆（找最大）/大顶堆（找最小），整体 O(n log k)；
- **数据流的中位数**：双堆对顶。

Go 用 `container/heap`，需实现 `Len/Less/Swap/Push/Pop`。

### 13.1 数组中的第 K 个最大元素（LC 215）

**题目**：找出整数数组中**第 k 大**的元素（同一元素重复也按下标算各自一份；即排序后从大到小第 k 个）。
- 示例：`[3,2,1,5,6,4], k=2` → `5`；`[3,2,3,1,2,4,5,5,6], k=4` → `4`。
- 约束：`1 ≤ k ≤ len ≤ 10⁵`，`-10⁴ ≤ nums[i] ≤ 10⁴`。

```go
type minH []int
func (h minH) Len() int            { return len(h) }
func (h minH) Less(i, j int) bool  { return h[i] < h[j] }
func (h minH) Swap(i, j int)       { h[i], h[j] = h[j], h[i] }
func (h *minH) Push(x interface{}) { *h = append(*h, x.(int)) }
func (h *minH) Pop() interface{}   { old := *h; n := len(old); x := old[n-1]; *h = old[:n-1]; return x }

func findKthLargest(nums []int, k int) int {
    h := &minH{}
    heap.Init(h)
    for _, x := range nums {
        heap.Push(h, x)
        if h.Len() > k { heap.Pop(h) }
    }
    return (*h)[0]
}
```

---

### 13.2 前 K 个高频元素（LC 347）

**题目**：返回出现频率前 k 高的元素（顺序不限）。
- 示例：`[1,1,1,2,2,3], k=2` → `[1,2]`；`[1], k=1` → `[1]`。
- 约束：`1 ≤ len ≤ 10⁵`，`k` 唯一确定，要求时间优于 O(n log n)。

```go
type pair struct{ val, cnt int }
type freqH []pair
func (h freqH) Len() int            { return len(h) }
func (h freqH) Less(i, j int) bool  { return h[i].cnt < h[j].cnt }
func (h freqH) Swap(i, j int)       { h[i], h[j] = h[j], h[i] }
func (h *freqH) Push(x interface{}) { *h = append(*h, x.(pair)) }
func (h *freqH) Pop() interface{}   { old := *h; n := len(old); x := old[n-1]; *h = old[:n-1]; return x }

func topKFrequent(nums []int, k int) []int {
    cnt := map[int]int{}
    for _, x := range nums { cnt[x]++ }
    h := &freqH{}
    for v, c := range cnt {
        heap.Push(h, pair{v, c})
        if h.Len() > k { heap.Pop(h) }
    }
    res := make([]int, k)
    for i := k - 1; i >= 0; i-- { res[i] = heap.Pop(h).(pair).val }
    return res
}
```

---

### 13.3 数据流的中位数（LC 295，对顶堆）

**题目**：设计 `MedianFinder`，支持：
- `AddNum(x)`：插入一个数；
- `FindMedian()`：返回当前所有数的**中位数**（偶数取中间两数平均）。
- 示例：`addNum(1); addNum(2); findMedian()→1.5; addNum(3); findMedian()→2`。
- 约束：调用次数 ≤ 5·10⁴，`-10⁵ ≤ x ≤ 10⁵`。

**关键观察**：维护两个堆——`lo` 大顶堆存较小一半，`hi` 小顶堆存较大一半。不变量：`|hi|-|lo| ∈ {0, 1}`，且 `lo 全部 ≤ hi 全部`。

每次 push 时先丢到一个堆，再把它的极值"过户"到另一个堆，自动保持不变量。

```go
type maxH []int
func (h maxH) Len() int            { return len(h) }
func (h maxH) Less(i, j int) bool  { return h[i] > h[j] }
func (h maxH) Swap(i, j int)       { h[i], h[j] = h[j], h[i] }
func (h *maxH) Push(x interface{}) { *h = append(*h, x.(int)) }
func (h *maxH) Pop() interface{}   { old := *h; n := len(old); x := old[n-1]; *h = old[:n-1]; return x }

type MedianFinder struct {
    lo *maxH
    hi *minH
}
func ConstructorMF() MedianFinder { return MedianFinder{lo: &maxH{}, hi: &minH{}} }
func (mf *MedianFinder) AddNum(x int) {
    heap.Push(mf.lo, x)
    heap.Push(mf.hi, heap.Pop(mf.lo))
    if mf.hi.Len() > mf.lo.Len()+1 {
        heap.Push(mf.lo, heap.Pop(mf.hi))
    }
}
func (mf *MedianFinder) FindMedian() float64 {
    if mf.hi.Len() > mf.lo.Len() { return float64((*mf.hi)[0]) }
    return float64((*mf.lo)[0]+(*mf.hi)[0]) / 2.0
}
```

---

## 14. 贪心

### 总思想

贪心 = "每步选眼前最优，证明全局最优"。能用贪心的题，往往满足**交换论证**：把任何非贪心解和贪心解局部交换，结果不会更差。

### 14.1 买卖股票的最佳时机（LC 121）

**题目**：每天股价 `prices[i]`，**只能买卖一次**（先买后卖），返回最大利润，无利润返回 0。
- 示例：`[7,1,5,3,6,4]` → `5`（第 2 天买、第 5 天卖）；`[7,6,4,3,1]` → `0`。
- 约束：`1 ≤ len ≤ 10⁵`，`0 ≤ prices[i] ≤ 10⁴`。

```go
func maxProfit(prices []int) int {
    minP, ans := math.MaxInt32, 0
    for _, p := range prices {
        if p < minP { minP = p }
        if p-minP > ans { ans = p - minP }
    }
    return ans
}
```

---

### 14.2 跳跃游戏（LC 55）

**题目**：非负数组 `nums[i]` 表示从位置 i **最多**可以前进的步数。判断能否到达**最后一个**下标。
- 示例：`[2,3,1,1,4]` → `true`；`[3,2,1,0,4]` → `false`。
- 约束：`1 ≤ len ≤ 10⁴`，`0 ≤ nums[i] ≤ 10⁵`。

**关键观察**：维护"目前能到达的最远位置"。逐位扫描，到不了当前位置就失败。

```go
func canJump(nums []int) bool {
    far := 0
    for i := 0; i < len(nums); i++ {
        if i > far { return false }
        if i+nums[i] > far { far = i + nums[i] }
    }
    return true
}
```

---

### 14.3 跳跃游戏 II（LC 45）

**题目**：保证一定能到末尾，求**最少跳跃次数**。
- 示例：`[2,3,1,1,4]` → `2`（从 0 跳到 1，再跳到末尾）；`[2,3,0,1,4]` → `2`。
- 约束：`1 ≤ len ≤ 10⁴`，`0 ≤ nums[i] ≤ 1000`，保证可达。

**关键观察**：把跳跃看成 BFS 分层。`end` 是"本层右端"，`far` 是"下一层最远能到哪"。每到本层右端，必须再跳一次进入新一层。

```go
func jump(nums []int) int {
    end, far, steps := 0, 0, 0
    for i := 0; i < len(nums)-1; i++ {
        if i+nums[i] > far { far = i + nums[i] }
        if i == end { steps++; end = far }
    }
    return steps
}
```

**踩坑点**：循环到 `len-1` 不到 `len`——最后一步不需要再起跳。

---

### 14.4 划分字母区间（LC 763）

**题目**：把字符串 `s` 划分成**尽可能多的片段**，使**同一字母只出现在同一片段中**，返回每段长度数组（按顺序）。
- 示例：`"ababcbacadefegdehijhklij"` → `[9,7,8]`（"ababcbaca"、"defegde"、"hijhklij"）。
- 约束：`1 ≤ len ≤ 500`，仅小写字母。

**关键观察**：每个字母在最终区间里必须**全部包含**它的所有出现。预处理每字母最后位置，扫描时把窗口右端推到"窗口内字母最大的最后位置"。一旦扫到右端，切一刀。

```go
func partitionLabels(s string) []int {
    last := [26]int{}
    for i := 0; i < len(s); i++ { last[s[i]-'a'] = i }
    var res []int
    l, r := 0, 0
    for i := 0; i < len(s); i++ {
        if last[s[i]-'a'] > r { r = last[s[i]-'a'] }
        if i == r { res = append(res, r-l+1); l = i + 1 }
    }
    return res
}
```

---

## 15. 一维动态规划

### 总思想

DP 三步走：
1. **定义状态**：`f[i]` 代表什么？
2. **写转移**：`f[i]` 怎么由更小规模推出？
3. **定边界 + 答案位置**。

最难的是 (1)。常见状态定义有两类：
- "到位置 i **为止**" → 求最值/计数（70/198/322）；
- "**以 i 结尾**" → 子串/子数组类（53/152/300）。

两者答案位置不同：前者答案在 `f[n]`；后者答案是 `max(f[i])`。

### 15.1 爬楼梯（LC 70）

**题目**：每次可以爬 1 或 2 个台阶，求**爬到第 n 阶有多少种不同方法**。
- 示例：`n=2` → `2`；`n=3` → `3`（1+1+1, 1+2, 2+1）。
- 约束：`1 ≤ n ≤ 45`。

```go
func climbStairs(n int) int {
    if n <= 2 { return n }
    a, b := 1, 2
    for i := 3; i <= n; i++ { a, b = b, a+b }
    return b
}
```

---

### 15.2 打家劫舍（LC 198）

**题目**：每间房存有一定现金，**相邻两家不能同时偷**（否则报警）。求一夜能偷到的最大金额。
- 示例：`[1,2,3,1]` → `4`（偷 1 和 3）；`[2,7,9,3,1]` → `12`（2+9+1）。
- 约束：`1 ≤ len ≤ 100`，`0 ≤ nums[i] ≤ 400`。

**状态**：`f[i]` = 前 i 个房子最大金额。
**转移**：偷 i → `f[i-2]+nums[i]`；不偷 → `f[i-1]`，取大。空间滚动到 O(1)。

```go
func rob(nums []int) int {
    prev2, prev1 := 0, 0
    for _, x := range nums {
        prev2, prev1 = prev1, max(prev1, prev2+x)
    }
    return prev1
}
```

---

### 15.3 零钱兑换（LC 322，完全背包）

**题目**：硬币面额数组 `coins`（**无限供应**），求凑出金额 `amount` 所需的**最少硬币数**；无解返回 -1。
- 示例：`coins=[1,2,5], amount=11` → `3`（5+5+1）；`coins=[2], amount=3` → `-1`。
- 约束：`1 ≤ len(coins) ≤ 12`，`1 ≤ coins[i] ≤ 2³¹-1`，`0 ≤ amount ≤ 10⁴`。

**状态**：`f[i]` = 凑出 i 所需的最小硬币数。
**转移**：`f[i] = min(f[i-c]) + 1`。

```go
func coinChange(coins []int, amt int) int {
    INF := amt + 1
    f := make([]int, amt+1)
    for i := range f { f[i] = INF }
    f[0] = 0
    for i := 1; i <= amt; i++ {
        for _, c := range coins {
            if c <= i && f[i-c]+1 < f[i] { f[i] = f[i-c] + 1 }
        }
    }
    if f[amt] == INF { return -1 }
    return f[amt]
}
```

---

### 15.4 单词拆分（LC 139）

**题目**：判断字符串 `s` 是否可被**字典**中的单词**拼接**而成（同一单词可重复使用）。
- 示例：`s="leetcode", dict=["leet","code"]` → `true`；`s="applepenapple", dict=["apple","pen"]` → `true`；`s="catsandog", dict=["cats","dog","sand","and","cat"]` → `false`。
- 约束：`1 ≤ len(s) ≤ 300`，`1 ≤ len(dict) ≤ 1000`，单词长度 1–20。

**状态**：`f[i]` = `s[:i]` 是否可拆。
**转移**：`f[i] = ∃ j<i, f[j] && s[j:i] ∈ dict`。

```go
func wordBreak(s string, dict []string) bool {
    set := make(map[string]bool)
    for _, w := range dict { set[w] = true }
    n := len(s)
    f := make([]bool, n+1)
    f[0] = true
    for i := 1; i <= n; i++ {
        for j := 0; j < i; j++ {
            if f[j] && set[s[j:i]] { f[i] = true; break }
        }
    }
    return f[n]
}
```

---

### 15.5 最长递增子序列（LC 300）

**题目**：返回数组中**最长严格递增子序列**的长度（子序列可不连续）。要求尽量 O(n log n)。
- 示例：`[10,9,2,5,3,7,101,18]` → `4`（如 [2,3,7,101]）；`[0,1,0,3,2,3]` → `4`。
- 约束：`1 ≤ len ≤ 2500`，`-10⁴ ≤ nums[i] ≤ 10⁴`。

**O(n log n) 二分法**：`tails[k]` = 长度为 k+1 的递增子序列的**最小末尾**。每个元素二分插入。

```go
func lengthOfLIS(nums []int) int {
    var tails []int
    for _, x := range nums {
        i := sort.SearchInts(tails, x)
        if i == len(tails) { tails = append(tails, x) } else { tails[i] = x }
    }
    return len(tails)
}
```

**心智模型**：`tails` **不是**真实的 LIS，但**长度永远等于** LIS 长度——它代表"对各长度子序列末尾最贪心的选择"。

---

### 15.6 乘积最大子数组（LC 152）

**题目**：返回数组中**乘积最大**的连续子数组的乘积。
- 示例：`[2,3,-2,4]` → `6`（[2,3]）；`[-2,0,-1]` → `0`。
- 约束：`1 ≤ len ≤ 2·10⁴`，`-10 ≤ nums[i] ≤ 10`，最终结果在 32 位整数范围。

**坑**：和 53 不一样——**负 × 负 = 大正数**。所以以 i 结尾时同时维护 max 和 min。

```go
func maxProduct(nums []int) int {
    mx, mn, ans := nums[0], nums[0], nums[0]
    for i := 1; i < len(nums); i++ {
        x := nums[i]
        a, b, c := x, mx*x, mn*x
        nmx, nmn := max3(a, b, c), min3(a, b, c)
        mx, mn = nmx, nmn
        if mx > ans { ans = mx }
    }
    return ans
}
func max3(a, b, c int) int { return max(a, max(b, c)) }
func min3(a, b, c int) int { return min(a, min(b, c)) }
```

---

## 16. 多维动态规划

### 总思想

二维 DP 比一维多一个维度的"语义"。最常见两类：
- **网格路径型**：`f[i][j]` 是从 (0,0) 到 (i,j) 的某种最优值（62、64）；
- **两序列对齐型**：`f[i][j]` 是 `a[:i]` 和 `b[:j]` 的某种关系（72、1143）。

### 16.1 不同路径（LC 62）

**题目**：m×n 网格，机器人从左上角出发，**只能向右或向下**走，问到达右下角的不同路径**总数**。
- 示例：`m=3, n=7` → `28`；`m=3, n=2` → `3`。
- 约束：`1 ≤ m,n ≤ 100`，结果保证 ≤ 2·10⁹。

`f[i][j] = f[i-1][j] + f[i][j-1]`，第一行第一列全 1。

```go
func uniquePaths(m, n int) int {
    f := make([]int, n)
    for i := range f { f[i] = 1 }
    for i := 1; i < m; i++ {
        for j := 1; j < n; j++ {
            f[j] += f[j-1]              // 滚动数组：f[j] 旧值 = f[i-1][j]，f[j-1] 新值 = f[i][j-1]
        }
    }
    return f[n-1]
}
```

---

### 16.2 最小路径和（LC 64）

**题目**：m×n 非负网格，从左上角到右下角**只能向下或向右**，找出路径上**数字总和最小**的路径，返回该和。
- 示例：`[[1,3,1],[1,5,1],[4,2,1]]` → `7`（路径 1→3→1→1→1）。
- 约束：`1 ≤ m,n ≤ 200`，`0 ≤ g[i][j] ≤ 200`。

`f[i][j] = grid[i][j] + min(f[i-1][j], f[i][j-1])`。

```go
func minPathSum(g [][]int) int {
    m, n := len(g), len(g[0])
    f := make([]int, n)
    f[0] = g[0][0]
    for j := 1; j < n; j++ { f[j] = f[j-1] + g[0][j] }
    for i := 1; i < m; i++ {
        f[0] += g[i][0]
        for j := 1; j < n; j++ {
            f[j] = g[i][j] + min(f[j], f[j-1])
        }
    }
    return f[n-1]
}
```

---

### 16.3 最长回文子串（LC 5，中心扩展）

**题目**：返回字符串 `s` 中**最长的回文子串**（连续）。
- 示例：`"babad"` → `"bab"` 或 `"aba"`；`"cbbd"` → `"bb"`。
- 约束：`1 ≤ len ≤ 1000`，仅含数字与字母。

**思路**：DP 是 O(n²) 时间 O(n²) 空间；中心扩展是 O(n²) 时间 O(1) 空间，写起来更简单。每个位置作为中心，分**奇数中心**（一个字符）和**偶数中心**（两个字符）两种情况向两边扩。

```go
func longestPalindrome(s string) string {
    expand := func(l, r int) (int, int) {
        for l >= 0 && r < len(s) && s[l] == s[r] { l--; r++ }
        return l + 1, r - 1
    }
    bl, br := 0, 0
    for i := 0; i < len(s); i++ {
        l1, r1 := expand(i, i)
        l2, r2 := expand(i, i+1)
        if r1-l1 > br-bl { bl, br = l1, r1 }
        if r2-l2 > br-bl { bl, br = l2, r2 }
    }
    return s[bl : br+1]
}
```

---

### 16.4 最长公共子序列（LC 1143）

**题目**：返回两字符串 `a, b` 的**最长公共子序列**长度（子序列可不连续，但保留原相对顺序）。
- 示例：`a="abcde", b="ace"` → `3`（"ace"）；`a="abc", b="def"` → `0`。
- 约束：`1 ≤ len ≤ 1000`，仅小写字母。

**状态**：`f[i][j]` = `a[:i]` 与 `b[:j]` 的 LCS 长度。
**转移**：`a[i-1] == b[j-1]` 时 `f[i][j] = f[i-1][j-1] + 1`，否则 `f[i][j] = max(f[i-1][j], f[i][j-1])`。

```go
func longestCommonSubsequence(a, b string) int {
    m, n := len(a), len(b)
    f := make([][]int, m+1)
    for i := range f { f[i] = make([]int, n+1) }
    for i := 1; i <= m; i++ {
        for j := 1; j <= n; j++ {
            if a[i-1] == b[j-1] {
                f[i][j] = f[i-1][j-1] + 1
            } else {
                f[i][j] = max(f[i-1][j], f[i][j-1])
            }
        }
    }
    return f[m][n]
}
```

---

### 16.5 编辑距离（LC 72）

**题目**：返回把字符串 `a` 转换成 `b` 所需的**最少编辑次数**，每次可**插入、删除、替换**一个字符。
- 示例：`a="horse", b="ros"` → `3`（horse→rorse→rose→ros）；`a="intention", b="execution"` → `5`。
- 约束：`0 ≤ len ≤ 500`，含大小写字母。

**状态**：`f[i][j]` = 把 `a[:i]` 变成 `b[:j]` 的最小操作数。
**转移**：
- `a[i-1] == b[j-1]`：直接 `f[i-1][j-1]`；
- 否则三选一最小再 +1：删 `f[i-1][j]`、插 `f[i][j-1]`、改 `f[i-1][j-1]`。

```go
func minDistance(a, b string) int {
    m, n := len(a), len(b)
    f := make([][]int, m+1)
    for i := range f { f[i] = make([]int, n+1) }
    for i := 0; i <= m; i++ { f[i][0] = i }
    for j := 0; j <= n; j++ { f[0][j] = j }
    for i := 1; i <= m; i++ {
        for j := 1; j <= n; j++ {
            if a[i-1] == b[j-1] {
                f[i][j] = f[i-1][j-1]
            } else {
                f[i][j] = 1 + min(f[i-1][j-1], min(f[i-1][j], f[i][j-1]))
            }
        }
    }
    return f[m][n]
}
```

**踩坑点**：边界 `f[i][0]=i`、`f[0][j]=j` 不能漏，对应"全删"和"全插"。

---

## 17. 技巧题

### 17.1 只出现一次的数字（LC 136，异或）

**题目**：非空数组中**除一个数字外**，其余每个数字都出现两次。找出那个**只出现一次**的数。要求 O(n) 时间、O(1) 额外空间。
- 示例：`[2,2,1]` → `1`；`[4,1,2,1,2]` → `4`。
- 约束：`1 ≤ len ≤ 3·10⁴`。

**关键观察**：异或满足交换律和结合律，且 `x ^ x = 0`、`x ^ 0 = x`。所以全员异或后剩下的就是单数。

```go
func singleNumber(nums []int) int {
    ans := 0
    for _, x := range nums { ans ^= x }
    return ans
}
```

---

### 17.2 多数元素（LC 169，摩尔投票）

**题目**：返回数组中出现次数 **> n/2** 的元素（题目保证一定存在）。要求 O(n) 时间、O(1) 额外空间。
- 示例：`[3,2,3]` → `3`；`[2,2,1,1,1,2,2]` → `2`。
- 约束：`1 ≤ len ≤ 5·10⁴`。

**关键观察**：把多数元素当作 +1，其他都 -1，总和必然 > 0。投票算法：维护"候选 + 计数"，遇相同 +1，否则 -1，归 0 时换候选。

```go
func majorityElement(nums []int) int {
    cand, cnt := 0, 0
    for _, x := range nums {
        if cnt == 0 { cand = x }
        if x == cand { cnt++ } else { cnt-- }
    }
    return cand
}
```

**为什么对**：多数元素出现次数 > n/2，所有"反对票"加起来 < n/2，抵消不掉它，最终它必然胜出。

---

### 17.3 颜色分类（LC 75，荷兰国旗）

**题目**：原地排序仅含 0、1、2 的数组，使相同颜色相邻，按 0、1、2 顺序排列。要求一趟扫描、O(1) 额外空间。
- 示例：`[2,0,2,1,1,0]` → `[0,0,1,1,2,2]`。
- 约束：`1 ≤ len ≤ 300`，`nums[i] ∈ {0,1,2}`。

**关键观察**：三指针 `l/i/r`，把数组分成 `[0..l)=0`、`[l..i)=1`、`(r..end]=2`。

```go
func sortColors(nums []int) {
    l, i, r := 0, 0, len(nums)-1
    for i <= r {
        switch nums[i] {
        case 0:
            nums[l], nums[i] = nums[i], nums[l]
            l++; i++
        case 1:
            i++
        case 2:
            nums[r], nums[i] = nums[i], nums[r]
            r--
            // 注意：不 i++，因为换过来的可能还是 0 或 2
        }
    }
}
```

**踩坑点**：换 2 之后 i 不能加，否则可能漏检从右边换过来的 0。换 0 之后 i 可以加，因为换过来的只能是已扫过的 1（必然合规）。

---

### 17.4 下一个排列（LC 31）

**题目**：原地把数组变成它在**字典序中的下一个排列**。如果已经是最大排列，则变为最小排列（升序）。要求 O(1) 额外空间。
- 示例：`[1,2,3]` → `[1,3,2]`；`[3,2,1]` → `[1,2,3]`；`[1,1,5]` → `[1,5,1]`。
- 约束：`1 ≤ len ≤ 100`，`0 ≤ nums[i] ≤ 100`。

**算法**：从右往左找第一个**升序拐点 i**（`a[i] < a[i+1]`）；再从右往左找第一个 `a[j] > a[i]`；交换 i、j；最后反转 `[i+1, end]`。

**为什么对**：从右到左如果一直降序，说明已经是最大排列，整体翻转得到最小排列。否则 i 之后是降序段，把刚好比 a[i] 大的数换上来，再让后面变最小（升序）即可得到下一个排列。

```go
func nextPermutation(a []int) {
    n := len(a)
    i := n - 2
    for i >= 0 && a[i] >= a[i+1] { i-- }
    if i >= 0 {
        j := n - 1
        for a[j] <= a[i] { j-- }
        a[i], a[j] = a[j], a[i]
    }
    for l, r := i+1, n-1; l < r; l, r = l+1, r-1 {
        a[l], a[r] = a[r], a[l]
    }
}
```

---

### 17.5 寻找重复数（LC 287）

**题目**：长度为 n+1 的数组，每个元素在 `[1, n]`，**只有一个重复整数**（可能重复多次）。**不能修改原数组**，只能用 O(1) 额外空间，时间小于 O(n²)。
- 示例：`[1,3,4,2,2]` → `2`；`[3,1,3,4,2]` → `3`。
- 约束：`1 ≤ n ≤ 10⁵`，`nums[i] ∈ [1, n]`。

**抓手**：哈希集合 O(n) 时间 O(n) 空间；二分答案 O(n log n) 时间 O(1) 空间。
**最优 Floyd 解法**：把数组看作链表：`i → nums[i]`。重复值意味着有两个不同的 i 指向同一个节点 → **有环**，环入口就是重复值。

```go
func findDuplicate(nums []int) int {
    slow, fast := nums[0], nums[0]
    for {
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast { break }
    }
    p := nums[0]
    for p != slow { p = nums[p]; slow = nums[slow] }
    return p
}
```

---

## 总结：刷题路径建议

1. **第一遍按类型刷**（按本文 17 类的顺序），形成"看题→识别类型→套模板"的肌肉记忆。
2. **第二遍按热度乱序刷**，限时 25 分钟，模拟面试。
3. **第三遍只刷错题**，在每道题旁写"我当时为什么没做出来"——这步比刷新题更有价值。
4. **代码模板私有化**：上面每个模板抄到自己笔记里，亲手写一遍才是你的。

> 算法不在于做了多少题，而在于你能用自己的话讲清楚多少题。

### Go 刷题小贴士

- 没有泛型 `min/max`（Go 1.21+ 的 `min/max` 内置仅作用于基本类型，可用），刷题时手写一份方便：
  ```go
  func max(a, b int) int { if a > b { return a }; return b }
  func min(a, b int) int { if a < b { return a }; return b }
  ```
- 切片 pop：`s = s[:len(s)-1]`；切片 shift：`s = s[1:]`（注意可能内存泄漏，频繁操作改用下标 + 切片头）。
- `container/heap` 必须自己实现 5 个方法，建议把模板背熟。
- map 不存在 key 时返回零值，`if v, ok := m[k]; ok` 是判断键是否存在的标准写法。
- `for range` 的下标默认从 0 开始，循环内修改切片不影响 range（但修改长度要小心）。

---

*文档版本：2026-05-08 · 覆盖力扣 Hot 100 全题型 · Go 版*

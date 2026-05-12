---
title: 一致性哈希、Redis slot 与 MySQL 预分片
date: 2026-05-11
tags: [后端, 分布式, Redis, MySQL, Go]
summary: 从一致性哈希环讲起，澄清 Redis Cluster 用的是 16384 个固定 slot，拓展到 MySQL 预分片——用远超物理节点数的逻辑分片对抗持久化数据的迁移成本。
---



后端做数据分片，几乎一定会碰到三个词：**一致性哈希**、**Redis slot**、**MySQL 预分片**。它们看起来各是各的，其实底层思路一脉相承——都是在"key 到物理节点"之间塞一个稳定的中间层，让物理扩缩容不再牵连全量数据。

这篇博客把三件事串起来讲清楚。

## 为什么需要一致性哈希

最朴素的分片是 `hash(key) % N`，N 是节点数。一旦加减节点，几乎所有 key 的归属都变了，缓存层直接雪崩。

一致性哈希的目标：**增减节点时只有少量 key 需要迁移**。

### 哈希环

把 `0 ~ 2³²-1` 的哈希空间首尾相接想象成一个环：

1. 每个节点 hash 后落在环上某个点；
2. 每个 key hash 后也落在环上；
3. key 顺时针走，遇到的第一个节点就是归属。

<svg viewBox="0 0 680 420" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="ch-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>
  <text x="340" y="30" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="500" fill="#222">哈希环 (0 ~ 2³²-1)</text>
  <text x="340" y="48" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#666">node 和 key 都 hash 到环上，key 顺时针找最近的 node</text>
  <circle cx="340" cy="240" r="140" fill="none" stroke="#bbb" stroke-width="0.5" stroke-dasharray="3 3"/>
  <text x="340" y="92" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#888">0 / 2³²</text>
  <g><circle cx="340" cy="100" r="10" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/><text x="340" y="78" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#3C3489">Node A</text></g>
  <g><circle cx="480" cy="240" r="10" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/><text x="508" y="244" font-family="sans-serif" font-size="12" font-weight="500" fill="#3C3489">Node B</text></g>
  <g><circle cx="340" cy="380" r="10" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/><text x="340" y="405" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#3C3489">Node C</text></g>
  <g><circle cx="200" cy="240" r="10" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/><text x="172" y="244" text-anchor="end" font-family="sans-serif" font-size="12" font-weight="500" fill="#3C3489">Node D</text></g>
  <g><circle cx="420" cy="140" r="5" fill="#D85A30"/><text x="432" y="130" font-family="sans-serif" font-size="11" fill="#993C1D">key1 → B</text><path d="M425 145 Q 455 170 475 232" fill="none" stroke="#D85A30" stroke-width="1" stroke-dasharray="2 2" marker-end="url(#ch-arrow)"/></g>
  <g><circle cx="455" cy="320" r="5" fill="#D85A30"/><text x="470" y="324" font-family="sans-serif" font-size="11" fill="#993C1D">key2 → C</text><path d="M450 325 Q 410 360 348 378" fill="none" stroke="#D85A30" stroke-width="1" stroke-dasharray="2 2" marker-end="url(#ch-arrow)"/></g>
  <g><circle cx="240" cy="330" r="5" fill="#D85A30"/><text x="150" y="334" font-family="sans-serif" font-size="11" fill="#993C1D">key3 → D</text><path d="M235 325 Q 215 290 205 252" fill="none" stroke="#D85A30" stroke-width="1" stroke-dasharray="2 2" marker-end="url(#ch-arrow)"/></g>
  <path d="M 340 240 m 170 0 a 170 170 0 0 1 -30 120" fill="none" stroke="#1D9E75" stroke-width="1.2" marker-end="url(#ch-arrow)"/>
  <text x="568" y="290" font-family="sans-serif" font-size="11" fill="#0F6E56">顺时针</text>
</svg>

### 节点变动的最小迁移

Node B 宕机，只有原本属于 B 的 key 迁移到它顺时针方向的下一个节点（C）；其它 key 完全不动。

<svg viewBox="0 0 680 360" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="ch2-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>
  <text x="170" y="30" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="500" fill="#222">宕机前</text>
  <text x="510" y="30" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="500" fill="#222">Node B 宕机后</text>
  <g>
    <circle cx="170" cy="190" r="110" fill="none" stroke="#bbb" stroke-width="0.5" stroke-dasharray="3 3"/>
    <g><circle cx="170" cy="80" r="8" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/><text x="170" y="66" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3C3489">A</text></g>
    <g><circle cx="280" cy="190" r="8" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/><text x="296" y="194" font-family="sans-serif" font-size="11" fill="#3C3489">B</text></g>
    <g><circle cx="170" cy="300" r="8" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/><text x="170" y="320" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3C3489">C</text></g>
    <g><circle cx="60" cy="190" r="8" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/><text x="44" y="194" text-anchor="end" font-family="sans-serif" font-size="11" fill="#3C3489">D</text></g>
    <circle cx="235" cy="115" r="4" fill="#D85A30"/><text x="240" y="108" font-family="sans-serif" font-size="10" fill="#993C1D">k1→B</text>
    <circle cx="245" cy="260" r="4" fill="#1D9E75"/><text x="250" y="266" font-family="sans-serif" font-size="10" fill="#0F6E56">k2→C</text>
    <circle cx="95" cy="255" r="4" fill="#1D9E75"/><text x="30" y="270" font-family="sans-serif" font-size="10" fill="#0F6E56">k3→D</text>
  </g>
  <line x1="340" y1="60" x2="340" y2="330" stroke="#ddd" stroke-width="0.5" stroke-dasharray="2 4"/>
  <g>
    <circle cx="510" cy="190" r="110" fill="none" stroke="#bbb" stroke-width="0.5" stroke-dasharray="3 3"/>
    <g><circle cx="510" cy="80" r="8" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/><text x="510" y="66" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3C3489">A</text></g>
    <g>
      <circle cx="620" cy="190" r="8" fill="#F7C1C1" stroke="#A32D2D" stroke-width="0.5" stroke-dasharray="2 2"/>
      <line x1="615" y1="185" x2="625" y2="195" stroke="#A32D2D" stroke-width="1"/>
      <line x1="625" y1="185" x2="615" y2="195" stroke="#A32D2D" stroke-width="1"/>
      <text x="636" y="194" font-family="sans-serif" font-size="11" fill="#A32D2D">B ✗</text>
    </g>
    <g><circle cx="510" cy="300" r="8" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/><text x="510" y="320" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3C3489">C</text></g>
    <g><circle cx="400" cy="190" r="8" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/><text x="384" y="194" text-anchor="end" font-family="sans-serif" font-size="11" fill="#3C3489">D</text></g>
    <circle cx="575" cy="115" r="4" fill="#D85A30"/><text x="580" y="108" font-family="sans-serif" font-size="10" fill="#993C1D">k1→C (迁)</text>
    <circle cx="585" cy="260" r="4" fill="#1D9E75"/><text x="590" y="266" font-family="sans-serif" font-size="10" fill="#0F6E56">k2→C</text>
    <circle cx="435" cy="255" r="4" fill="#1D9E75"/><text x="370" y="270" font-family="sans-serif" font-size="10" fill="#0F6E56">k3→D</text>
    <path d="M578 118 Q 600 180 515 295" fill="none" stroke="#D85A30" stroke-width="1" stroke-dasharray="2 2" marker-end="url(#ch2-arrow)"/>
  </g>
  <text x="340" y="345" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">只有 B 上的 key 迁到 C，其它 key 不动</text>
</svg>

### 虚拟节点解决数据倾斜

节点数很少时，它们在环上的位置可能严重不均，某台机器会被塞爆。解法：给每个物理节点生成 N 个**虚拟节点**，分散到环上各处。

<svg viewBox="0 0 680 380" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
  <text x="170" y="30" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="500" fill="#222">无虚拟节点</text>
  <text x="510" y="30" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="500" fill="#222">每节点 4 个虚拟节点</text>
  <g>
    <circle cx="170" cy="200" r="110" fill="none" stroke="#bbb" stroke-width="0.5" stroke-dasharray="3 3"/>
    <g><circle cx="170" cy="90" r="8" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/><text x="170" y="76" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3C3489">A</text></g>
    <g><circle cx="200" cy="110" r="8" fill="#9FE1CB" stroke="#0F6E56" stroke-width="0.5"/><text x="215" y="105" font-family="sans-serif" font-size="11" fill="#0F6E56">B</text></g>
    <g><circle cx="145" cy="115" r="8" fill="#F5C4B3" stroke="#993C1D" stroke-width="0.5"/><text x="125" y="110" text-anchor="end" font-family="sans-serif" font-size="11" fill="#993C1D">C</text></g>
    <path d="M 170 200 L 170 90 A 110 110 0 1 1 162 308 L 170 200 Z" fill="#F5C4B3" opacity="0.35"/>
    <text x="170" y="260" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#993C1D">C 负责的范围</text>
    <text x="170" y="275" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#993C1D">过大 (~70%)</text>
  </g>
  <line x1="340" y1="60" x2="340" y2="350" stroke="#ddd" stroke-width="0.5" stroke-dasharray="2 4"/>
  <g>
    <circle cx="510" cy="200" r="110" fill="none" stroke="#bbb" stroke-width="0.5" stroke-dasharray="3 3"/>
    <g fill="#CECBF6" stroke="#534AB7" stroke-width="0.5">
      <circle cx="510" cy="90" r="6"/><circle cx="595" cy="225" r="6"/><circle cx="445" cy="270" r="6"/><circle cx="430" cy="155" r="6"/>
    </g>
    <g fill="#9FE1CB" stroke="#0F6E56" stroke-width="0.5">
      <circle cx="570" cy="115" r="6"/><circle cx="570" cy="285" r="6"/><circle cx="405" cy="200" r="6"/><circle cx="495" cy="308" r="6"/>
    </g>
    <g fill="#F5C4B3" stroke="#993C1D" stroke-width="0.5">
      <circle cx="615" cy="180" r="6"/><circle cx="475" cy="95" r="6"/><circle cx="425" cy="240" r="6"/><circle cx="540" cy="305" r="6"/>
    </g>
    <g font-family="sans-serif" font-size="11">
      <circle cx="388" cy="355" r="5" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/><text x="400" y="358" fill="#3C3489">A</text>
      <circle cx="425" cy="355" r="5" fill="#9FE1CB" stroke="#0F6E56" stroke-width="0.5"/><text x="437" y="358" fill="#0F6E56">B</text>
      <circle cx="462" cy="355" r="5" fill="#F5C4B3" stroke="#993C1D" stroke-width="0.5"/><text x="474" y="358" fill="#993C1D">C</text>
    </g>
  </g>
</svg>

做法：对物理节点 `A` 生成 `A#0`, `A#1`, ... `A#N` 分别 hash，都指向同一台物理机。N 越大越均匀，工程上常取 **150**（ketama 算法推荐值，实测偏差能压到 1%~2%）。

### Go 实现

```go
package consistenthash

import (
	"hash/crc32"
	"sort"
	"strconv"
	"sync"
)

type HashRing struct {
	mu       sync.RWMutex
	replicas int               // 每个物理节点对应的虚拟节点数
	ring     []uint32          // 有序的 hash 值（环上的点）
	hashMap  map[uint32]string // hash -> 物理节点名
}

func New(replicas int) *HashRing {
	return &HashRing{replicas: replicas, hashMap: make(map[uint32]string)}
}

func (h *HashRing) Add(nodes ...string) {
	h.mu.Lock()
	defer h.mu.Unlock()
	for _, node := range nodes {
		for i := 0; i < h.replicas; i++ {
			hash := crc32.ChecksumIEEE([]byte(node + "#" + strconv.Itoa(i)))
			h.ring = append(h.ring, hash)
			h.hashMap[hash] = node
		}
	}
	sort.Slice(h.ring, func(i, j int) bool { return h.ring[i] < h.ring[j] })
}

func (h *HashRing) Remove(node string) {
	h.mu.Lock()
	defer h.mu.Unlock()
	for i := 0; i < h.replicas; i++ {
		hash := crc32.ChecksumIEEE([]byte(node + "#" + strconv.Itoa(i)))
		delete(h.hashMap, hash)
	}
	newRing := h.ring[:0]
	for _, v := range h.ring {
		if _, ok := h.hashMap[v]; ok {
			newRing = append(newRing, v)
		}
	}
	h.ring = newRing
}

// 查 key 应落在哪个节点：二分找第一个 >= hash(key) 的点
func (h *HashRing) Get(key string) string {
	h.mu.RLock()
	defer h.mu.RUnlock()
	if len(h.ring) == 0 {
		return ""
	}
	hash := crc32.ChecksumIEEE([]byte(key))
	idx := sort.Search(len(h.ring), func(i int) bool { return h.ring[i] >= hash })
	if idx == len(h.ring) {
		idx = 0 // 越过末尾回到环起点
	}
	return h.hashMap[h.ring[idx]]
}
```

查询路径 O(log N)，读多写少用 `sync.RWMutex` 足够。

## Redis Cluster：其实不是一致性哈希

经常有人以为 Redis Cluster 用的就是一致性哈希。**不是。** 它用的是**固定 16384 个哈希槽（hash slot）**：

```
slot = CRC16(key) & 16383    // 等价于 % 16384
```

每个节点**静态认领**一段 slot 区间：

<svg viewBox="0 0 680 240" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
  <text x="340" y="28" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="500" fill="#222">Redis Cluster 固定 16384 个 slot</text>
  <text x="340" y="46" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#666">slot = CRC16(key) &amp; 16383</text>
  <g>
    <rect x="40" y="80" width="200" height="50" rx="8" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <rect x="240" y="80" width="200" height="50" rx="0" fill="#9FE1CB" stroke="#0F6E56" stroke-width="0.5"/>
    <rect x="440" y="80" width="200" height="50" rx="8" fill="#F5C4B3" stroke="#993C1D" stroke-width="0.5"/>
    <text x="140" y="108" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="500" fill="#3C3489">Node A</text>
    <text x="340" y="108" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="500" fill="#0F6E56">Node B</text>
    <text x="540" y="108" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="500" fill="#993C1D">Node C</text>
    <text x="140" y="122" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3C3489">slot 0 – 5460</text>
    <text x="340" y="122" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#0F6E56">slot 5461 – 10922</text>
    <text x="540" y="122" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#993C1D">slot 10923 – 16383</text>
  </g>
  <g font-family="sans-serif" font-size="11" fill="#888">
    <line x1="40" y1="140" x2="40" y2="150" stroke="#bbb" stroke-width="0.5"/>
    <line x1="240" y1="140" x2="240" y2="150" stroke="#bbb" stroke-width="0.5"/>
    <line x1="440" y1="140" x2="440" y2="150" stroke="#bbb" stroke-width="0.5"/>
    <line x1="640" y1="140" x2="640" y2="150" stroke="#bbb" stroke-width="0.5"/>
    <text x="40" y="163" text-anchor="middle">0</text>
    <text x="240" y="163" text-anchor="middle">5461</text>
    <text x="440" y="163" text-anchor="middle">10923</text>
    <text x="640" y="163" text-anchor="middle">16383</text>
  </g>
  <g>
    <rect x="180" y="190" width="320" height="36" rx="8" fill="#f7f7f4" stroke="#ddd" stroke-width="0.5"/>
    <text x="340" y="213" text-anchor="middle" font-family="monospace" font-size="12" fill="#222">CRC16("user:1001") &amp; 16383 = 7543 → Node B</text>
  </g>
</svg>

### 为什么偏偏是 16384（2¹⁴）

antirez 亲自回答过：

- **心跳包开销**：节点互发 gossip 心跳时要带自己负责的 slot 位图。16384 bit = 2KB；换成 65536 就是 8KB，心跳包膨胀 4 倍。
- **节点规模**：Redis 集群不建议超过 1000 个主节点。16384 / 1000 ≈ 16 个 slot/节点，粒度已经够细。
- **压缩效率**：bitmap 传输用游程压缩，填充率越低压缩效果越好，16384 在常见规模下填充率刚好合适。

所以 Redis 取的数字是 **16384**，不是大家记忆里和一致性哈希混在一起的 150。后者是 ketama 算法的虚拟节点推荐值，在 memcached / Redis 客户端分片（twemproxy、codis、Jedis ShardedJedis）那一套体系里。

### slot 方案 vs 一致性哈希

| 维度 | slot（Redis Cluster） | 一致性哈希环 |
|---|---|---|
| 分片数 | 固定 16384 | 任意，由虚拟节点数控制 |
| 路由信息 | 集中（集群 gossip 维护 slot→node 映射） | 去中心化，客户端自算 |
| 迁移粒度 | 可精确到单 slot | 顺时针的一段弧 |
| 热点处理 | 可手动迁单个 slot | 只能加/减节点 |
| 典型场景 | 持久化、需可控性 | 无状态缓存 |

## MySQL 分片：预分片把思路用到极致

MySQL 的痛点比 Redis 更大——**数据是持久化的，迁移代价极高**。所以业界几乎统一用"预分片（pre-sharding）"：

**一次性规划一个远大于当前节点数的逻辑分片总量，以后扩容只搬分片、不改路由算法。**

<svg viewBox="0 0 680 420" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="ms-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>
  <text x="340" y="28" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="500" fill="#222">预分片：1024 个逻辑分片，只改映射不改算法</text>
  <text x="340" y="46" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#666">shard_id = hash(sharding_key) % 1024</text>
  <g>
    <text x="40" y="78" font-family="sans-serif" font-size="12" font-weight="500" fill="#222">逻辑分片层（固定 1024 个 db 编号）</text>
    <rect x="40" y="88" width="600" height="36" rx="6" fill="#f7f7f4" stroke="#ddd" stroke-width="0.5"/>
    <text x="340" y="111" text-anchor="middle" font-family="monospace" font-size="12" fill="#666">db_0000 · db_0001 · db_0002 · ··· · db_1022 · db_1023</text>
  </g>
  <g>
    <path d="M120 130 L 120 170" fill="none" stroke="#bbb" stroke-width="0.5" marker-end="url(#ms-arrow)"/>
    <path d="M340 130 L 340 170" fill="none" stroke="#bbb" stroke-width="0.5" marker-end="url(#ms-arrow)"/>
    <path d="M560 130 L 560 170" fill="none" stroke="#bbb" stroke-width="0.5" marker-end="url(#ms-arrow)"/>
  </g>
  <g>
    <text x="40" y="190" font-family="sans-serif" font-size="12" font-weight="500" fill="#222">初期：2 台物理机（每台 512 个逻辑库）</text>
    <rect x="40" y="200" width="290" height="50" rx="8" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <rect x="350" y="200" width="290" height="50" rx="8" fill="#9FE1CB" stroke="#0F6E56" stroke-width="0.5"/>
    <text x="185" y="222" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#3C3489">MySQL-1</text>
    <text x="185" y="240" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3C3489">db_0000 – db_0511</text>
    <text x="495" y="222" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#0F6E56">MySQL-2</text>
    <text x="495" y="240" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#0F6E56">db_0512 – db_1023</text>
  </g>
  <g>
    <path d="M 185 260 L 140 290" fill="none" stroke="#bbb" stroke-width="0.5" marker-end="url(#ms-arrow)"/>
    <path d="M 185 260 L 230 290" fill="none" stroke="#D85A30" stroke-width="0.8" stroke-dasharray="2 2" marker-end="url(#ms-arrow)"/>
    <path d="M 495 260 L 450 290" fill="none" stroke="#bbb" stroke-width="0.5" marker-end="url(#ms-arrow)"/>
    <path d="M 495 260 L 540 290" fill="none" stroke="#D85A30" stroke-width="0.8" stroke-dasharray="2 2" marker-end="url(#ms-arrow)"/>
  </g>
  <g>
    <text x="40" y="310" font-family="sans-serif" font-size="12" font-weight="500" fill="#222">扩容后：4 台物理机（搬 512 个库，路由无需改）</text>
    <rect x="40" y="320" width="140" height="50" rx="8" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <rect x="185" y="320" width="140" height="50" rx="8" fill="#F5C4B3" stroke="#993C1D" stroke-width="0.5"/>
    <rect x="350" y="320" width="140" height="50" rx="8" fill="#9FE1CB" stroke="#0F6E56" stroke-width="0.5"/>
    <rect x="495" y="320" width="140" height="50" rx="8" fill="#FAC775" stroke="#854F0B" stroke-width="0.5"/>
    <text x="110" y="342" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#3C3489">MySQL-1</text>
    <text x="110" y="358" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3C3489">db_0000–0255</text>
    <text x="255" y="342" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#993C1D">MySQL-3 新</text>
    <text x="255" y="358" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#993C1D">db_0256–0511</text>
    <text x="420" y="342" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#0F6E56">MySQL-2</text>
    <text x="420" y="358" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#0F6E56">db_0512–0767</text>
    <text x="565" y="342" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#854F0B">MySQL-4 新</text>
    <text x="565" y="358" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#854F0B">db_0768–1023</text>
  </g>
  <text x="340" y="395" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">逻辑分片数 1024 始终不变，只搬库、改路由映射表</text>
</svg>

### 预分片三板斧

1. **逻辑分片数选 2 的幂**（1024、2048、4096 常见）。按位运算快、可反复对半劈、物理机数只要也是 2 的幂就能平均分。
2. **路由层维护映射表**：`db_xxxx → 物理实例 IP`。扩容就是搬库 + 改映射表 + 切流量，业务代码不动。
3. **分库分表两层**：对大表（订单、消息）在 db 内再切 N 张表。常见配置：**32 库 × 32 表 = 1024 个物理表**，或 **1024 库 × 8 表**。

### 预分片省的是什么：迁移数据量

预分片的所有收益，都收敛到一件事——**最小化迁移数据量**。看一组直观的数字（2 台扩到 4 台）：

<svg viewBox="0 0 680 280" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
  <text x="340" y="28" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="500" fill="#222">2 台 → 4 台扩容时的迁移量对比</text>

  <g>
    <text x="40" y="70" font-family="sans-serif" font-size="12" font-weight="500" fill="#A32D2D">hash(key) % N</text>
    <text x="180" y="70" font-family="sans-serif" font-size="11" fill="#666">~50% 数据要重算 hash 后逐行搬</text>
    <rect x="40" y="80" width="600" height="20" rx="4" fill="#FCEBEB" stroke="#A32D2D" stroke-width="0.5"/>
    <rect x="40" y="80" width="300" height="20" rx="4" fill="#E24B4A"/>
    <text x="190" y="94" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#fff">迁移 50%</text>
  </g>

  <g>
    <text x="40" y="135" font-family="sans-serif" font-size="12" font-weight="500" fill="#854F0B">一致性哈希 (虚拟节点)</text>
    <text x="220" y="135" font-family="sans-serif" font-size="11" fill="#666">加 1 台迁 1/N；翻倍仍约 50%，但分散在多段</text>
    <rect x="40" y="145" width="600" height="20" rx="4" fill="#FAEEDA" stroke="#854F0B" stroke-width="0.5"/>
    <rect x="40" y="145" width="300" height="20" rx="4" fill="#EF9F27"/>
    <text x="190" y="159" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#fff">迁移 ~50%（粒度更细）</text>
  </g>

  <g>
    <text x="40" y="200" font-family="sans-serif" font-size="12" font-weight="500" fill="#0F6E56">预分片（1024 逻辑库）</text>
    <text x="200" y="200" font-family="sans-serif" font-size="11" fill="#666">搬整库文件，不重算 hash，可用物理拷贝</text>
    <rect x="40" y="210" width="600" height="20" rx="4" fill="#E1F5EE" stroke="#0F6E56" stroke-width="0.5"/>
    <rect x="40" y="210" width="300" height="20" rx="4" fill="#1D9E75"/>
    <text x="190" y="224" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#fff">迁移 50%（但是文件级整库搬）</text>
  </g>

  <text x="340" y="260" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">关键差别在"怎么搬"，不在"搬多少"——预分片让搬迁从逐行变文件级</text>
</svg>

三种方案在"翻倍扩容"场景下要动的数据**比例都差不多**，但代价完全不同：

| 方案 | 搬运方式 | 路由变化 | 业务代码 |
|---|---|---|---|
| `hash % N` | 逐行重算 hash 跨网络写 | 算法变（N 变） | 必须重发 |
| 一致性哈希 | 客户端按环段拉取 | 环结构更新 | 客户端版本要同步 |
| **预分片** | **整库 dump/物理拷贝** | **只改 slot→实例映射** | **不动** |

预分片真正省下的是：
- **运维成本**：xtrabackup 物理拷贝快 10 倍以上，DTS / binlog 增量同步成熟工具链；
- **风险**：路由算法不变 = 应用零改动 = 灰度回滚简单；
- **业务连续性**：扩容期间只有"被搬走的那部分库"短暂锁写，其它库不受影响。

### 业界参考值

| 系统 | 逻辑分片数 | 备注 |
|---|---|---|
| Redis Cluster | 16384 | slot 固定值 |
| Apache ShardingSphere | 用户自定 | 常见 1024 库或 32×32 |
| Vitess (YouTube/Slack) | keyspace + shard | 通常几十到几百，支持动态 resharding |
| MongoDB sharded cluster | 默认 chunk 128MB | chunk 自动分裂和迁移 |
| TiDB | Region | 默认 96MB，自动切分 |

### 预分片实战：Go 代码逐步演进

**① 最简版：纯 hash 路由（1024 库）**

```go
package sharding

import (
	"database/sql"
	"fmt"
	"hash/crc32"
)

const ShardCount = 1024 // 必须是 2 的幂

type Router struct {
	slotToDB [ShardCount]*sql.DB
}

func shardID(key string) uint32 {
	return crc32.ChecksumIEEE([]byte(key)) & (ShardCount - 1) // & 1023 等价 % 1024
}

func (r *Router) DB(key string) *sql.DB { return r.slotToDB[shardID(key)] }
func (r *Router) DBName(key string) string {
	return fmt.Sprintf("db_%04d", shardID(key))
}
```

**② 分库 + 分表（1024 库 × 8 表）**

订单、消息这类大表再切一层。低 10 位选库、接下来 3 位选表，互不干扰。

```go
func (r *Router) Locate(key, logicalTable string) (dbName, tableName string, db *sql.DB) {
	h := crc32.ChecksumIEEE([]byte(key))
	dbIdx := h & 1023        // 低 10 位
	tbIdx := (h >> 10) & 7   // 接下来 3 位
	dbName = fmt.Sprintf("db_%04d", dbIdx)
	tableName = fmt.Sprintf("%s_%d", logicalTable, tbIdx)
	db = r.slotToDB[dbIdx]
	return
}
```

要点：**分片键只用一个**（如 `user_id`），保证同一实体的数据落到同一个 db+table，避免跨库 join 和分布式事务。

**③ 热更新路由表（扩容关键）**

扩容不能重启服务，映射表必须能原子替换。Go 1.19+ 用 `atomic.Pointer`：

```go
import "sync/atomic"

type shardMap struct {
	slotToDB [1024]*sql.DB
	version  int64
}

type LiveRouter struct {
	current atomic.Pointer[shardMap]
}

func (r *LiveRouter) Update(m *shardMap) { r.current.Store(m) }

func (r *LiveRouter) DB(key string) *sql.DB {
	slot := crc32.ChecksumIEEE([]byte(key)) & 1023
	return r.current.Load().slotToDB[slot]
}
```

扩容时：新实例追同步 → 构造新 `shardMap`（一半 slot 指新机器）→ `Update(newMap)` → 老连接逐步释放。**业务代码一行不改。**

**④ 从 yaml 加载映射**

生产里映射一般在 etcd / Nacos / apollo，最小可用版本是一份 yaml：

```yaml
instances:
  mysql-1: "user:pwd@tcp(10.0.0.1:3306)/"
  mysql-2: "user:pwd@tcp(10.0.0.2:3306)/"
ranges:
  - { instance: mysql-1, slots: [0, 511] }
  - { instance: mysql-2, slots: [512, 1023] }
```

```go
type Config struct {
	Instances map[string]string `yaml:"instances"`
	Ranges    []struct {
		Instance string `yaml:"instance"`
		Slots    [2]int `yaml:"slots"`
	} `yaml:"ranges"`
}

func BuildShardMap(cfg *Config) (*shardMap, error) {
	pool := make(map[string]*sql.DB, len(cfg.Instances))
	for name, dsn := range cfg.Instances {
		db, err := sql.Open("mysql", dsn)
		if err != nil {
			return nil, err
		}
		pool[name] = db
	}
	m := &shardMap{}
	for _, r := range cfg.Ranges {
		for s := r.Slots[0]; s <= r.Slots[1]; s++ {
			m.slotToDB[s] = pool[r.Instance]
		}
	}
	return m, nil
}
```

扩容 = 只改 yaml 的 ranges，再触发 `Update`。

**⑤ 一次性预建 1024 个库表**

预分片的"预"也体现在 DDL 一次性做完，扩容时只搬数据不建 schema：

```go
func InitSchema(instance *sql.DB, slots []int, tableCount int) error {
	for _, slot := range slots {
		dbName := fmt.Sprintf("db_%04d", slot)
		if _, err := instance.Exec(
			fmt.Sprintf("CREATE DATABASE IF NOT EXISTS %s DEFAULT CHARSET utf8mb4", dbName),
		); err != nil {
			return err
		}
		for t := 0; t < tableCount; t++ {
			ddl := fmt.Sprintf(`CREATE TABLE IF NOT EXISTS %s.t_order_%d (
				order_id   BIGINT PRIMARY KEY,
				user_id    BIGINT NOT NULL,
				amount     DECIMAL(10,2),
				created_at DATETIME,
				KEY idx_user (user_id)
			) ENGINE=InnoDB`, dbName, t)
			if _, err := instance.Exec(ddl); err != nil {
				return err
			}
		}
	}
	return nil
}
```

### 扩容流程（最小停机）

1. DBA 在新实例上建好目标 db，用 `mysqldump` 或 `gh-ost`/DTS 做存量 + binlog 增量同步；
2. 同步追平后，短暂锁写 → 原子替换路由表 `slotToInstance` → 放流量；
3. 老实例上被搬走的库保留一段时间作回滚，确认无误后 drop。

### 容易踩的三个坑

1. **分片键一旦定了几乎不能改**。改分片键 = 全量数据洗牌，比扩容还痛苦。订单系统常用 `user_id` 而不是 `order_id`，这样按用户的查询全落单库。
2. **跨分片查询要预先规避**。需要"按商家维度查订单"时，标准做法是双写一份按 `merchant_id` 分片的索引表，别想着运行时做 scatter-gather。
3. **初始分片数宁多勿少**。1024 起步几乎没上限压力，比"按当前机器数精确规划"重要得多——这是唯一不能改的参数。

## 一句话串起来

三件事本质一样：**加一层"逻辑分片层"把路由和物理部署解耦**。

- 一致性哈希用**虚拟节点**把分布抹平；
- Redis Cluster 用**16384 个固定 slot** 把控制权换到集群手里；
- MySQL 用**远超物理节点数的逻辑分片**对抗持久化数据的迁移成本。

只要这层够稳定，物理节点增减就不再是业务事故，而是一次 DBA 操作。

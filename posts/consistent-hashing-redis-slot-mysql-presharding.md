---
title: 一致性哈希、Redis slot 与 MySQL 预分片
date: 2026-05-11
tags: [后端, 分布式, Redis, MySQL, Go]
summary: 从一致性哈希环讲起，澄清 Redis Cluster 用的是 16384 个固定 slot，落到 MySQL 上就是桶预分片：用远多于物理节点的逻辑桶 + 桶→实例映射表，让扩容只搬数据不改公式。
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
	newRing := make([]uint32, 0, len(h.ring))
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

### slot 怎么关联到 key 和节点

数字 16384 只是中间的一层抽象，完整链路是：

<svg viewBox="0 0 680 320" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="rsk-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>
  <text x="340" y="28" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="500" fill="#222">key → slot → 节点 的完整路由链路</text>

  <g>
    <rect x="40" y="60" width="180" height="60" rx="8" fill="#EEEDFE" stroke="#534AB7" stroke-width="0.5"/>
    <text x="130" y="82" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#3C3489">客户端 (key)</text>
    <text x="130" y="100" text-anchor="middle" font-family="monospace" font-size="11" fill="#3C3489">SET user:1001 wendell</text>
  </g>

  <path d="M220 90 L 260 90" fill="none" stroke="#888" stroke-width="0.8" marker-end="url(#rsk-arrow)"/>
  <text x="240" y="80" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">CRC16</text>

  <g>
    <rect x="260" y="60" width="160" height="60" rx="8" fill="#FAEEDA" stroke="#854F0B" stroke-width="0.5"/>
    <text x="340" y="82" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#854F0B">slot 编号</text>
    <text x="340" y="100" text-anchor="middle" font-family="monospace" font-size="11" fill="#854F0B">7543 (0..16383)</text>
  </g>

  <path d="M420 90 L 460 90" fill="none" stroke="#888" stroke-width="0.8" marker-end="url(#rsk-arrow)"/>
  <text x="440" y="80" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">查路由表</text>

  <g>
    <rect x="460" y="60" width="180" height="60" rx="8" fill="#E1F5EE" stroke="#0F6E56" stroke-width="0.5"/>
    <text x="550" y="82" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#0F6E56">主节点 IP</text>
    <text x="550" y="100" text-anchor="middle" font-family="monospace" font-size="11" fill="#0F6E56">10.0.0.2:6379</text>
  </g>

  <g>
    <rect x="40" y="160" width="600" height="135" rx="8" fill="#F1EFE8" stroke="#5F5E5A" stroke-width="0.5"/>
    <text x="60" y="182" font-family="sans-serif" font-size="12" font-weight="500" fill="#444">集群路由表 (clusterState.slots[16384])</text>
    <text x="60" y="200" font-family="monospace" font-size="11" fill="#666">slot 0     → Node A (10.0.0.1:6379)</text>
    <text x="60" y="216" font-family="monospace" font-size="11" fill="#666">slot 1     → Node A</text>
    <text x="60" y="232" font-family="monospace" font-size="11" fill="#666">  ...</text>
    <text x="60" y="248" font-family="monospace" font-size="11" fill="#A32D2D">slot 7543  → Node B (10.0.0.2:6379)   ← 命中</text>
    <text x="60" y="264" font-family="monospace" font-size="11" fill="#666">  ...</text>
    <text x="60" y="280" font-family="monospace" font-size="11" fill="#666">slot 16383 → Node C (10.0.0.3:6379)</text>
  </g>

  <text x="340" y="312" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">这张表由集群所有节点 gossip 维护，客户端启动时拉一份缓存，过期则被 MOVED 纠正</text>
</svg>

#### key → slot：CRC16 + hash tag

```
HASH_SLOT = CRC16(key) & 16383
```

**注意 ①：Redis Cluster 不支持多 database**，所有 key 都在 `db 0`。集群模式下 `SELECT 1` 直接报错，所以严格来说没有"库"的概念，**key 直接绑定 slot**。

**注意 ②：key 含 `{...}` 时只 hash 大括号里的内容**——这就是 hash tag：

```redis
{user:1001}.profile      # CRC16("user:1001") & 16383 = 7543
{user:1001}.orders       # 同样是 7543
{user:1001}.cart         # 同样是 7543
```

hash tag 是让"相关 key 落同一节点"的**官方手段**。MGET、MSET、MULTI 事务、Lua 脚本要求所有 key 在同一 slot——做这种跨 key 操作必须用 hash tag 把它们绑到一起，否则报 `CROSSSLOT Keys in request don't hash to the same slot`。

#### slot → 节点：集群路由表

每个 Redis 节点内部维护：
- `clusterNode.slots`：自己负责的 slot bitmap（16384 位）；
- `clusterState.slots[16384]`：整张集群视图，每项指向某个主节点。

节点之间用 **gossip 心跳**互相同步这张表，每条心跳带自己的 slot bitmap（这就是 16384 选 2KB 而不是 8KB 的原因）。可以用 `CLUSTER SLOTS` 或 `CLUSTER NODES` 查到当前的映射：

```
> CLUSTER SLOTS
1) 1) (integer) 0          # 起始 slot
   2) (integer) 5460       # 结束 slot
   3) 1) "10.0.0.1"        # 主节点 IP
      2) (integer) 6379
2) 1) (integer) 5461
   2) (integer) 10922
   3) 1) "10.0.0.2"
      ...
```

#### 客户端怎么找到正确节点

智能客户端（`go-redis`、`lettuce`、`redis-py-cluster` 等）的标准流程：

1. 启动时执行 `CLUSTER SLOTS`，缓存整张映射；
2. 每次请求自己算 `CRC16(key) & 16383`，**直连**目标节点；
3. 如果路由表过期（刚做了 slot 迁移），节点返回 **`MOVED`** 重定向：

```
> SET user:1001 wendell
(error) MOVED 7543 10.0.0.2:6379
```

含义："这个 slot 现在归 10.0.0.2"。客户端**必须更新本地缓存**再重试，这是路由表跟集群拓扑保持一致的核心机制。

slot 迁移**进行中**时还会出现 **`ASK`**：

```
(error) ASK 7543 10.0.0.5:6379
```

意思是"这一次去 10.0.0.5 找它，但 slot 还没真正归它"。客户端要发 `ASKING` 再发原命令，**不能更新路由表**。`MOVED` 是永久的，`ASK` 是临时的——这两个区分让客户端在迁移期间也不会把缓存搞乱。

#### Go 代码：手动模拟客户端路由

`go-redis` 的 `ClusterClient` 已经把这套全包了，但理解原理可以手撸一个最小版：

```go
type ClusterRouter struct {
	mu        sync.RWMutex
	slotToIP  [16384]string // gossip 同步来的快照
}

// CRC16-CCITT 算法见 redis.io/topics/cluster-spec 附录
// 也可以直接用 go-redis 内部的 hashtag.Slot()
func slotOf(key string) uint16 {
	tag := extractHashTag(key) // 提取 {} 里的内容；没有则用整个 key
	return crc16ccitt([]byte(tag)) & 16383
}

func (c *ClusterRouter) Pick(key string) string {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.slotToIP[slotOf(key)]
}

// 收到 MOVED 时更新路由表
func (c *ClusterRouter) HandleMoved(slot uint16, newAddr string) {
	c.mu.Lock()
	c.slotToIP[slot] = newAddr
	c.mu.Unlock()
}
```

到这里就清楚了：**16384 是一层稳定的中间编号**，上面挂 key（通过 CRC16+hash tag），下面挂节点（通过集群 gossip 维护的映射表）。slot 是 Redis Cluster 整套机制的**枢纽**——扩缩容、迁移、读写重定向，全都围绕"slot 归谁"展开。

### slot 方案 vs 一致性哈希

| 维度 | slot（Redis Cluster） | 一致性哈希环 |
|---|---|---|
| 分片数 | 固定 16384 | 任意，由虚拟节点数控制 |
| 路由信息 | 集中（集群 gossip 维护 slot→node 映射） | 去中心化，客户端自算 |
| 迁移粒度 | 可精确到单 slot | 顺时针的一段弧 |
| 热点处理 | 可手动迁单个 slot | 只能加/减节点 |
| 典型场景 | 集群拓扑可控、需精细调度 | 客户端无中心、纯缓存场景 |

## MySQL 分片：把 Redis 槽位思想搬到关系库

如果说 Redis Cluster 的 16384 slot 是为了**让缓存层支持在线扩缩**，那 MySQL 预分片就是把这套思路**原样搬到关系数据库**——只是换了个名字叫 **bucket（桶）**，本质完全一致：

> **预分片 = 桶预分片**。在数据增长之前一次性切出远多于物理节点的"逻辑桶"，业务路由公式永远不变，扩容只是改"桶 → 实例"的映射表。

我反复强调"远多于"——这是它和"静态哈希分片（`hash(key) % N`）"的根本分水岭：

| 特征 | 静态哈希分片 | **桶预分片（Redis 式）** |
|---|---|---|
| 逻辑分片数 | = 物理节点数 N | ≫ 物理节点数（1024、2048、4096） |
| 路由公式 | `hash(key) % N` | `bucket = hash(key) & (B-1)` |
| 扩容时公式 | **必须改 N**，几乎全量重 hash | **公式不变**，只改桶→实例映射 |
| 业务侧感知 | 路由层要发新版 | 零感知 |
| 心智模型 | 把 key 直接钉到机器 | 把 key 钉到桶，桶可以自由搬家 |

这就是为什么前面 Redis 那一节铺垫得那么细——**MySQL 预分片只是把 slot 换成 bucket、把 gossip 换成 yaml/etcd，其它原理完全一样**。

### 两层映射：业务公式不变的秘密

Redis Cluster 的核心是"两层映射"：

```
key → slot：永远不变（CRC16 & 16383）
slot → node：可在线变更（gossip 维护）
```

MySQL 桶预分片的等价模型：

```
key → bucket：永远不变（hash & 1023）
bucket → 实例.schema.表：可在线变更（路由表维护）
```

<svg viewBox="0 0 680 420" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="ms-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>
  <text x="340" y="28" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="500" fill="#222">桶预分片：业务永远只看到 1024 个桶</text>
  <text x="340" y="46" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#666">bucket = hash(sharding_key) &amp; 1023</text>
  <g>
    <text x="40" y="78" font-family="sans-serif" font-size="12" font-weight="500" fill="#222">逻辑桶层（业务永远只看到 1024 个 bucket）</text>
    <rect x="40" y="88" width="600" height="36" rx="6" fill="#f7f7f4" stroke="#ddd" stroke-width="0.5"/>
    <text x="340" y="111" text-anchor="middle" font-family="monospace" font-size="12" fill="#666">bucket 0 · 1 · 2 · ··· · 1022 · 1023  （每个 bucket = 一张物理表）</text>
  </g>
  <g>
    <path d="M120 130 L 120 170" fill="none" stroke="#bbb" stroke-width="0.5" marker-end="url(#ms-arrow)"/>
    <path d="M340 130 L 340 170" fill="none" stroke="#bbb" stroke-width="0.5" marker-end="url(#ms-arrow)"/>
    <path d="M560 130 L 560 170" fill="none" stroke="#bbb" stroke-width="0.5" marker-end="url(#ms-arrow)"/>
  </g>
  <g>
    <text x="40" y="190" font-family="sans-serif" font-size="12" font-weight="500" fill="#222">初期：2 台物理机（每台承载 512 个桶）</text>
    <rect x="40" y="200" width="290" height="50" rx="8" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <rect x="350" y="200" width="290" height="50" rx="8" fill="#9FE1CB" stroke="#0F6E56" stroke-width="0.5"/>
    <text x="185" y="222" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#3C3489">MySQL-1</text>
    <text x="185" y="240" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3C3489">bucket 0 – 511</text>
    <text x="495" y="222" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#0F6E56">MySQL-2</text>
    <text x="495" y="240" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#0F6E56">bucket 512 – 1023</text>
  </g>
  <g>
    <path d="M 185 260 L 140 290" fill="none" stroke="#bbb" stroke-width="0.5" marker-end="url(#ms-arrow)"/>
    <path d="M 185 260 L 230 290" fill="none" stroke="#D85A30" stroke-width="0.8" stroke-dasharray="2 2" marker-end="url(#ms-arrow)"/>
    <path d="M 495 260 L 450 290" fill="none" stroke="#bbb" stroke-width="0.5" marker-end="url(#ms-arrow)"/>
    <path d="M 495 260 L 540 290" fill="none" stroke="#D85A30" stroke-width="0.8" stroke-dasharray="2 2" marker-end="url(#ms-arrow)"/>
  </g>
  <g>
    <text x="40" y="310" font-family="sans-serif" font-size="12" font-weight="500" fill="#222">扩容后：4 台物理机（搬走一半桶，业务公式 hash &amp; 1023 完全不动）</text>
    <rect x="40" y="320" width="140" height="50" rx="8" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <rect x="185" y="320" width="140" height="50" rx="8" fill="#F5C4B3" stroke="#993C1D" stroke-width="0.5"/>
    <rect x="350" y="320" width="140" height="50" rx="8" fill="#9FE1CB" stroke="#0F6E56" stroke-width="0.5"/>
    <rect x="495" y="320" width="140" height="50" rx="8" fill="#FAC775" stroke="#854F0B" stroke-width="0.5"/>
    <text x="110" y="342" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#3C3489">MySQL-1</text>
    <text x="110" y="358" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3C3489">bucket 0–255</text>
    <text x="255" y="342" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#993C1D">MySQL-3 新</text>
    <text x="255" y="358" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#993C1D">bucket 256–511</text>
    <text x="420" y="342" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#0F6E56">MySQL-2</text>
    <text x="420" y="358" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#0F6E56">bucket 512–767</text>
    <text x="565" y="342" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#854F0B">MySQL-4 新</text>
    <text x="565" y="358" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#854F0B">bucket 768–1023</text>
  </g>
  <text x="340" y="395" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">桶数 1024 始终不变，只搬数据 + 改"桶→实例"映射表</text>
</svg>

### 桶预分片三板斧

1. **桶数选 2 的幂**（1024、2048、4096）。`& (B-1)` 等价 `% B` 但快一个量级，且可反复对半劈做迁移。
2. **路由层维护"桶 → 实例 / schema / 表"映射表**。扩容 = 搬数据 + 改映射表 + 切流量，业务代码一行不动。
3. **桶数 ≫ 物理 schema 数**：1024 主要落在"表后缀"维度，不是"db (schema)"维度。下一节给出具体的"实例 × schema × 表"组合方案。

### 物理部署：1024 个桶实际怎么落到机器上

最容易踩的认知坑：**1024 个逻辑桶 ≠ 1024 个物理 db**。

如果真的在一台 MySQL 上建 512 个 schema，运维会立刻爆炸——`table_open_cache` / `table_definition_cache` 直接顶天，备份脚本、监控、权限管理都跟着遭殃。所以**物理 schema 通常少很多**，1024 这个数字主要落在**表后缀**上。

主流形态有三种：

| 方案 | 实例 × schema × 表 | 优势 |
|---|---|---|
| 极简 | 8 × 1 × 128 | 运维最简单，metadata 开销最小 |
| **均衡** ✅ | **8 × 4 × 32** | **schema 粒度方便备份/迁移/权限隔离** |
| 重 schema | 8 × 32 × 4 | 适合每 schema 业务边界明显的场景 |

下面用主流的 "**8 实例 × 4 schema × 32 表 = 1024**" 来画图：

<svg viewBox="0 0 680 380" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="dep-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>
  <text x="340" y="28" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="500" fill="#222">应用看到的 1024 个桶 → 实际只在 8 台机器上</text>

  <g>
    <rect x="40" y="50" width="600" height="48" rx="8" fill="#EEEDFE" stroke="#534AB7" stroke-width="0.5"/>
    <text x="340" y="72" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#3C3489">应用层（业务代码）</text>
    <text x="340" y="89" text-anchor="middle" font-family="monospace" font-size="11" fill="#3C3489">bucket = hash(user_id) &amp; 1023  →  Locate("user:1001", "t_order") = "mysql-?.order_db_?.t_order_?"</text>
  </g>

  <path d="M340 98 L 340 124" fill="none" stroke="#bbb" stroke-width="0.5" marker-end="url(#dep-arrow)"/>

  <g>
    <rect x="40" y="128" width="600" height="60" rx="8" fill="#FAEEDA" stroke="#854F0B" stroke-width="0.5"/>
    <text x="340" y="148" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#854F0B">路由层（拆 bucket：实例 / schema / 表）</text>
    <text x="340" y="165" text-anchor="middle" font-family="monospace" font-size="11" fill="#854F0B">instance_idx = bucket / 128       schema_idx = (bucket / 32) % 4</text>
    <text x="340" y="180" text-anchor="middle" font-family="monospace" font-size="11" fill="#854F0B">table_idx    = bucket % 32        ← 1024 = 8 × 4 × 32</text>
  </g>

  <path d="M340 188 L 340 214" fill="none" stroke="#bbb" stroke-width="0.5" marker-end="url(#dep-arrow)"/>

  <g>
    <rect x="40" y="218" width="600" height="148" rx="8" fill="#E1F5EE" stroke="#0F6E56" stroke-width="0.5"/>
    <text x="340" y="238" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#0F6E56">物理实例层（mysql-1 ~ mysql-8，每台只有 4 个 schema）</text>

    <g font-family="monospace" font-size="11" fill="#0F6E56">
      <rect x="60"  y="252" width="135" height="100" rx="6" fill="#fff" stroke="#0F6E56" stroke-width="0.5"/>
      <text x="127" y="270" text-anchor="middle" font-weight="500">mysql-1 (10.0.0.1)</text>
      <text x="70"  y="288">order_db_0  ──┐</text>
      <text x="70"  y="304">order_db_1     │</text>
      <text x="70"  y="320">order_db_2     │ × 32 表</text>
      <text x="70"  y="336">order_db_3  ──┘</text>

      <rect x="205" y="252" width="135" height="100" rx="6" fill="#fff" stroke="#0F6E56" stroke-width="0.5"/>
      <text x="272" y="270" text-anchor="middle" font-weight="500">mysql-2 (10.0.0.2)</text>
      <text x="215" y="288">order_db_0</text>
      <text x="215" y="304">order_db_1</text>
      <text x="215" y="320">order_db_2</text>
      <text x="215" y="336">order_db_3</text>

      <rect x="350" y="252" width="135" height="100" rx="6" fill="#fff" stroke="#0F6E56" stroke-width="0.5"/>
      <text x="417" y="270" text-anchor="middle" font-weight="500">… mysql-3..7 …</text>
      <text x="360" y="304" text-anchor="start">每台只装 4 个 schema</text>
      <text x="360" y="320" text-anchor="start">每个 schema 32 张分表</text>
      <text x="360" y="336" text-anchor="start">运维负担可控</text>

      <rect x="495" y="252" width="135" height="100" rx="6" fill="#fff" stroke="#0F6E56" stroke-width="0.5"/>
      <text x="562" y="270" text-anchor="middle" font-weight="500">mysql-8 (10.0.0.8)</text>
      <text x="505" y="288">order_db_0</text>
      <text x="505" y="304">order_db_1</text>
      <text x="505" y="320">order_db_2</text>
      <text x="505" y="336">order_db_3</text>
    </g>
  </g>
</svg>

注意几个事实：

- ✅ **物理 schema 数 ≪ 逻辑桶数**：8 台 × 4 schema = 32 个物理 db，但承载 **1024** 个桶（= 1024 张物理表）；
- ✅ **同名 schema 在每台机器都存在**（`order_db_0` 在 8 台上各有一份），靠"实例 IP"区分归属；
- ✅ **`SHOW DATABASES` 在每台只看到 4 个 db**，不是 128 个；
- ✅ **应用查询只关心"表名"**，路由层把 `bucket` 翻译成 `实例.schema.表`。

`bucket = 539` 的查找路径：

```
bucket = 539
├─ instance_idx = 539 / 128 = 4   →  mysql-5
├─ schema_idx   = (539 / 32) % 4 = 16 % 4 = 0  →  order_db_0
└─ table_idx    = 539 % 32 = 27   →  t_order_27

最终落到：mysql-5 上的 order_db_0.t_order_27
```

扩容的本质：**把某些"实例 + schema"对应的 32 张分表整批搬到新机器**——不重命名表，只改"实例 IP"映射。

### 桶预分片省的是什么：迁移代价

桶预分片的所有收益，都收敛到一件事——**让搬迁从逐行变文件级**。看一组直观的数字（2 台扩到 4 台）：

<svg viewBox="0 0 680 280" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
  <text x="340" y="28" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="500" fill="#222">2 台 → 4 台扩容时的迁移代价对比</text>

  <g>
    <text x="40" y="70" font-family="sans-serif" font-size="12" font-weight="500" fill="#A32D2D">hash(key) % N</text>
    <text x="180" y="70" font-family="sans-serif" font-size="11" fill="#666">~50% 数据要重算 hash 后逐行搬</text>
    <rect x="40" y="80" width="600" height="20" rx="4" fill="#FCEBEB" stroke="#A32D2D" stroke-width="0.5"/>
    <rect x="40" y="80" width="300" height="20" rx="4" fill="#E24B4A"/>
    <text x="190" y="94" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#fff">迁移 50%（逐行）</text>
  </g>

  <g>
    <text x="40" y="135" font-family="sans-serif" font-size="12" font-weight="500" fill="#854F0B">一致性哈希 (虚拟节点)</text>
    <text x="220" y="135" font-family="sans-serif" font-size="11" fill="#666">加 1 台迁 1/N；翻倍约 50%，分散在多段</text>
    <rect x="40" y="145" width="600" height="20" rx="4" fill="#FAEEDA" stroke="#854F0B" stroke-width="0.5"/>
    <rect x="40" y="145" width="300" height="20" rx="4" fill="#EF9F27"/>
    <text x="190" y="159" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#fff">迁移 ~50%（粒度更细）</text>
  </g>

  <g>
    <text x="40" y="200" font-family="sans-serif" font-size="12" font-weight="500" fill="#0F6E56">桶预分片（1024 张物理表）</text>
    <text x="220" y="200" font-family="sans-serif" font-size="11" fill="#666">搬整表文件，不重算 hash，可用物理拷贝</text>
    <rect x="40" y="210" width="600" height="20" rx="4" fill="#E1F5EE" stroke="#0F6E56" stroke-width="0.5"/>
    <rect x="40" y="210" width="300" height="20" rx="4" fill="#1D9E75"/>
    <text x="190" y="224" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#fff">迁移 50%（文件级整表搬）</text>
  </g>

  <text x="340" y="260" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">关键差别在"怎么搬"，不在"搬多少"——桶预分片让搬迁从逐行变文件级</text>
</svg>

三种方案在"翻倍扩容"场景下要动的数据**比例都差不多**，但代价完全不同：

| 方案 | 搬运方式 | 路由变化 | 业务代码 |
|---|---|---|---|
| `hash % N` | 逐行重算 hash 跨网络写 | 算法变（N 变） | 必须重发 |
| 一致性哈希 | 客户端按环段拉取 | 环结构更新 | 客户端版本要同步 |
| **桶预分片** | **整库 dump / 物理拷贝** | **只改"桶→实例"映射** | **不动** |

桶预分片真正省下的是：
- **运维成本**：xtrabackup 物理拷贝快 10 倍以上，DTS / binlog 增量同步成熟工具链；
- **风险**：路由算法不变 = 应用零改动 = 灰度回滚简单；
- **业务连续性**：扩容期间只有"被搬走的那部分库"短暂锁写，其它库不受影响。

### 业界参考值

| 系统 | 逻辑分片单位 | 数量 | 备注 |
|---|---|---|---|
| Redis Cluster | slot | 16384 | 固定值，CRC16 决定 |
| Apache ShardingSphere | 用户自定 | 常见 1024 库或 32×32 | inline 表达式配置 |
| Vitess (YouTube/Slack) | shard | 几十到几百 | keyspace 内可在线 resharding |
| MongoDB sharded cluster | chunk | 默认 128MB | 自动分裂迁移 |
| TiDB | Region | 默认 96MB | 自动 split 不需要预规划 |

注意 TiDB / MongoDB 走的是"**自动动态分片**"路线——chunk/region 由系统按数据量自动切分，业务侧完全不用预先规划分片数。这是 NewSQL 比传统 MySQL + 桶预分片的根本优势，代价是要接受新的存储引擎和运维方式。

### 桶预分片实战：Go 代码逐步演进

下面所有代码以"**8 实例 × 4 schema × 32 表 = 1024 桶**"的主流形态来写。

**① bucket：算出 0~1023 的逻辑桶号**

```go
package sharding

import (
	"database/sql"
	"fmt"
	"hash/crc32"
)

const BucketCount = 1024 // 必须是 2 的幂

// 把任意 sharding key 哈希到 0..1023
func bucketOf(key string) uint32 {
	return crc32.ChecksumIEEE([]byte(key)) & (BucketCount - 1) // 等价 % 1024
}
```

注意：返回的是**逻辑桶号**，不是物理库名——后者要再翻译一次。

**② 把 bucket 翻译成"实例 + schema + 表名"**

```go
const (
	InstanceCount  = 8  // 物理 MySQL 实例数
	SchemaPerNode  = 4  // 每实例的 schema 数
	TablePerSchema = 32 // 每 schema 的分表数
	// 8 × 4 × 32 = 1024 = BucketCount
)

// Router 持有 8 份连接池，每个实例一份；schema 和表只是 SQL 里的字符串
type Router struct {
	instances [InstanceCount]*sql.DB
}

type Location struct {
	InstanceIdx int    // 0..7
	SchemaName  string // order_db_0..order_db_3
	TableName   string // t_order_0..t_order_31
}

func (r *Router) Locate(key, logicalTable string) (Location, *sql.DB) {
	bid := int(bucketOf(key))                         // 0..1023
	instIdx := bid / (SchemaPerNode * TablePerSchema) // 0..7
	schIdx := (bid / TablePerSchema) % SchemaPerNode  // 0..3
	tbIdx := bid % TablePerSchema                     // 0..31

	loc := Location{
		InstanceIdx: instIdx,
		SchemaName:  fmt.Sprintf("order_db_%d", schIdx),
		TableName:   fmt.Sprintf("%s_%d", logicalTable, tbIdx),
	}
	return loc, r.instances[instIdx]
}
```

举例：`bucketOf("user:1001") = 539` → instance 4 (mysql-5), schema `order_db_0`, table `t_order_27`（数字仅为示意，真实 hash 值取决于 CRC32 输出）。

**关键点：连接池只跟"实例"挂钩，跟"schema"无关**——`*sql.DB` 是按 `mysql-1`..`mysql-8` 一共 8 份。SQL 里写完整限定名 `order_db_0.t_order_27` 即可，DSN 里的默认 schema 留空（DSN 末尾只写 `/`）。

**③ 路由表热更新（扩容关键）**

扩容不能重启服务，"桶 → 实例"映射必须能原子替换。Go 1.19+ 用 `atomic.Pointer`：

```go
import "sync/atomic"

type bucketMap struct {
	// 1024 长的查找表：bucket → 该桶当前所在的物理实例
	// 扩容时整体重建并 Store，老的指针被 GC 回收
	bucketToDB [BucketCount]*sql.DB
	version    int64
}

type LiveRouter struct {
	current atomic.Pointer[bucketMap]
}

func (r *LiveRouter) Update(m *bucketMap) { r.current.Store(m) }

func (r *LiveRouter) Pick(key string) *sql.DB {
	return r.current.Load().bucketToDB[bucketOf(key)]
}
```

为什么用 1024 长的查找表而不是"按实例数除"？因为扩容时桶**可以任意切分**——可能把 mysql-1 上的 bucket 64..127 单独搬到 mysql-9，剩下 0..63 还在 mysql-1。查找表能精确表达任意切分，按比例除就僵化了。

> ⚠️ `atomic.Store` **只是切流量瞬间的扣扳机动作**，前提是新老库数据已经完全追平。
> 直接调 `Update(newMap)` 会让老库的最近写入丢失——具体怎么保证一致性，看下一节。

**④ 从 yaml 加载映射**

生产里映射一般在 etcd / Nacos / apollo，最小可用版本是一份 yaml。**配置粒度是"实例承担哪些 bucket 段"**——schema 名字是固定的 `order_db_0..3`，每台机器都建一样的 4 个：

```yaml
instances:
  - { name: mysql-1, dsn: "user:pwd@tcp(10.0.0.1:3306)/", buckets: [0,    127] }
  - { name: mysql-2, dsn: "user:pwd@tcp(10.0.0.2:3306)/", buckets: [128,  255] }
  - { name: mysql-3, dsn: "user:pwd@tcp(10.0.0.3:3306)/", buckets: [256,  383] }
  # ...
  - { name: mysql-8, dsn: "user:pwd@tcp(10.0.0.8:3306)/", buckets: [896, 1023] }
```

```go
type InstanceCfg struct {
	Name    string `yaml:"name"`
	DSN     string `yaml:"dsn"`
	Buckets [2]int `yaml:"buckets"` // 该实例承载的 bucket 闭区间
}

func BuildBucketMap(cfgs []InstanceCfg) (*bucketMap, error) {
	m := &bucketMap{}
	for _, c := range cfgs {
		db, err := sql.Open("mysql", c.DSN)
		if err != nil {
			return nil, err
		}
		// 把这一段 bucket 全部指向同一个连接池
		for b := c.Buckets[0]; b <= c.Buckets[1]; b++ {
			m.bucketToDB[b] = db
		}
	}
	return m, nil
}
```

**扩容**就是改 yaml：把 mysql-1 的 `[0,127]` 拆成 `[0,63]` 留 mysql-1、`[64,127]` 给新加的 mysql-9，然后 `BuildBucketMap` 出新表 → `Update`。物理实例数从 8 变 9，应用代码不动。

**⑤ 一次性预建 4 schema × 32 表（每台机器执行一次）**

桶预分片的"预"也体现在 DDL 一次性做完——**每台机器都建一样的 4 个 schema 和 32 张表**，扩容时只搬数据不再建 schema：

```go
// 在每台 mysql 实例启动时调用一次（幂等）
func InitSchema(instance *sql.DB) error {
	for s := 0; s < SchemaPerNode; s++ {
		dbName := fmt.Sprintf("order_db_%d", s)
		if _, err := instance.Exec(
			"CREATE DATABASE IF NOT EXISTS " + dbName + " DEFAULT CHARSET utf8mb4",
		); err != nil {
			return err
		}
		for t := 0; t < TablePerSchema; t++ {
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

8 台机器各自跑一次 → 总共 8 × 4 × 32 = **1024 张物理表**就位，对应 1024 个桶。

### 扩容六阶段：怎么保证一致性

只切路由表会丢数据——切换的瞬间，老库可能还有刚写入但未同步到新库的记录。生产里的标准做法是 **"双写 + 追平 + 校验 + 切读 + 切写 + 回收"** 六阶段：

<svg viewBox="0 0 680 240" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="mig-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>
  <text x="340" y="28" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="500" fill="#222">桶迁移六阶段（以 bucket 0..127 从 mysql-1 搬到新加的 mysql-9 为例）</text>

  <g font-family="sans-serif" font-size="11">
    <rect x="20"  y="60" width="100" height="60" rx="8" fill="#EEEDFE" stroke="#534AB7" stroke-width="0.5"/>
    <text x="70"  y="82"  text-anchor="middle" font-weight="500" fill="#3C3489">1. 存量同步</text>
    <text x="70"  y="100" text-anchor="middle" fill="#3C3489">DTS / xtrabackup</text>

    <rect x="130" y="60" width="100" height="60" rx="8" fill="#FAEEDA" stroke="#854F0B" stroke-width="0.5"/>
    <text x="180" y="82"  text-anchor="middle" font-weight="500" fill="#854F0B">2. 双写</text>
    <text x="180" y="100" text-anchor="middle" fill="#854F0B">老主写 + 同步新</text>

    <rect x="240" y="60" width="100" height="60" rx="8" fill="#FAEEDA" stroke="#854F0B" stroke-width="0.5"/>
    <text x="290" y="82"  text-anchor="middle" font-weight="500" fill="#854F0B">3. 追平 &amp; 校验</text>
    <text x="290" y="100" text-anchor="middle" fill="#854F0B">checksum 比对</text>

    <rect x="350" y="60" width="100" height="60" rx="8" fill="#E1F5EE" stroke="#0F6E56" stroke-width="0.5"/>
    <text x="400" y="82"  text-anchor="middle" font-weight="500" fill="#0F6E56">4. 切读</text>
    <text x="400" y="100" text-anchor="middle" fill="#0F6E56">读路由 → 新</text>

    <rect x="460" y="60" width="100" height="60" rx="8" fill="#E1F5EE" stroke="#0F6E56" stroke-width="0.5"/>
    <text x="510" y="82"  text-anchor="middle" font-weight="500" fill="#0F6E56">5. 切写</text>
    <text x="510" y="100" text-anchor="middle" fill="#0F6E56">atomic.Store</text>

    <rect x="570" y="60" width="90"  height="60" rx="8" fill="#E1F5EE" stroke="#0F6E56" stroke-width="0.5"/>
    <text x="615" y="82"  text-anchor="middle" font-weight="500" fill="#0F6E56">6. 回收</text>
    <text x="615" y="100" text-anchor="middle" fill="#0F6E56">drop 老库</text>
  </g>

  <g>
    <path d="M120 90 L 130 90" fill="none" stroke="#888" stroke-width="0.8" marker-end="url(#mig-arrow)"/>
    <path d="M230 90 L 240 90" fill="none" stroke="#888" stroke-width="0.8" marker-end="url(#mig-arrow)"/>
    <path d="M340 90 L 350 90" fill="none" stroke="#888" stroke-width="0.8" marker-end="url(#mig-arrow)"/>
    <path d="M450 90 L 460 90" fill="none" stroke="#888" stroke-width="0.8" marker-end="url(#mig-arrow)"/>
    <path d="M560 90 L 570 90" fill="none" stroke="#888" stroke-width="0.8" marker-end="url(#mig-arrow)"/>
  </g>

  <g font-family="sans-serif" font-size="11" fill="#666">
    <text x="40"  y="155">写：老库</text>
    <text x="150" y="155">写：老 + 新</text>
    <text x="260" y="155">写：老 + 新</text>
    <text x="370" y="155">写：老 + 新</text>
    <text x="480" y="155">写：仅新库</text>
    <text x="585" y="155">写：仅新库</text>

    <text x="40"  y="180">读：老库</text>
    <text x="150" y="180">读：老库</text>
    <text x="260" y="180">读：老库</text>
    <text x="370" y="180">读：新库</text>
    <text x="480" y="180">读：新库</text>
    <text x="585" y="180">读：新库</text>
  </g>

  <text x="340" y="220" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#A32D2D">关键：先双写再切读，最后切写——任何一步出问题都能回滚</text>
</svg>

#### 各阶段在做什么

以"把 mysql-1 上 bucket 0..127（4 个 schema × 32 表的一半）迁到新加的 mysql-9"为例：

1. **存量同步**：在新实例 mysql-9 上跑 `InitSchema` 建好 4 个 schema × 32 表（结构完全一样），用 xtrabackup / mysqldump / DTS 把 bucket 0..127 对应的物理表数据拷过去。这是耗时最长的一步。
2. **双写**：路由层进入"过渡态"，对 bucket 0..127 的写请求**同时**发到 mysql-1 和 mysql-9。mysql-1 的 binlog 同步任务保留兜底。
3. **追平 & 校验**：等 binlog 同步任务把双写之前的增量补完，再用 `pt-table-checksum` 或自研脚本逐表校验行数、checksum，确认两边完全一致。
4. **切读**：路由层把 bucket 0..127 的**读流量**切到 mysql-9。这一步出问题（性能不行、有数据漂移）随时能切回——写还在双写。
5. **切写**：观察一段时间稳定后，调 `atomic.Store` 把 bucket 0..127 的写也切到只写 mysql-9。**这才是 `Update(newMap)` 真正起作用的瞬间**。
6. **回收**：双写关闭，mysql-1 上 bucket 0..127 对应的物理表保留一段时间（一般 1~7 天）作回滚兜底，确认无问题后 `DROP TABLE` 释放空间。schema 本身不动（剩下的 bucket 还在用）。

#### 双写代码片段

过渡期的"双写"通常做在路由层而不是业务层，业务侧仍然只看到一个 `db.Exec`：

```go
type DualWriter struct {
	primary   *sql.DB // 老库（写入主路径）
	secondary *sql.DB // 新库（影子写）
	enabled   atomic.Bool
}

func (d *DualWriter) Exec(query string, args ...any) (sql.Result, error) {
	res, err := d.primary.Exec(query, args...)
	if err != nil {
		return res, err
	}
	if d.enabled.Load() {
		// 影子写：失败只告警，不影响主链路
		go func() {
			if _, e := d.secondary.Exec(query, args...); e != nil {
				log.Errorw("dual_write_failed", "err", e, "sql", query)
				metrics.DualWriteErr.Inc()
			}
		}()
	}
	return res, nil
}
```

要点：
- **以老库为主**，新库写失败只告警不阻塞——双写阶段任何异常都不能影响在线交易；
- **异步影子写**保证主路径延迟不变；
- 配合 binlog 同步**做兜底**（哪怕影子写丢了几条，binlog 也会补回）；
- 校验阶段必须发现并修复差异，否则切读后会暴露不一致。

#### 切换的"瞬间"到底有多瞬间

只有第 5 步（切写）需要锁写，时间窗口是：
1. 给 bucket 0..127 涉及的表加只读（应用层挡写或 `LOCK TABLES ... READ`）；
2. 等待最后几条同步 binlog 追平（通常 < 1 秒）；
3. `liveRouter.Update(newMap)`；
4. 解锁。

整个动作通常 **100ms ~ 1s**，业务侧表现为这部分用户极短时间的 `lock wait timeout` 重试，几乎无感。

### 容易踩的三个坑

1. **分片键一旦定了几乎不能改**。**分片键**（sharding key，前面所有代码里 `bucketOf(key)` 的入参）改了 = 全量数据洗牌，比扩容还痛苦。订单系统常用 `user_id` 做分片键而不是 `order_id`，这样按用户的查询全落单桶（同一台机器、同一张表），无需跨实例。
2. **跨分片查询要预先规避**。需要"按商家维度查订单"时，标准做法是双写一份按 `merchant_id` 分桶的索引表，别想着运行时做 scatter-gather。
3. **桶数宁多勿少**。1024 起步几乎没上限压力，比"按当前机器数精确规划"重要得多——这是唯一不能改的参数。

### 一个常见误解：这套和"自己 hash % N 分库"的差别在哪

很多人写"分库分表"代码会直接 `db_idx = user_id % 4; tbl_idx = (user_id / 4) % 4`，把数据扎扎实实钉在 16 个物理表上。乍一看也像预分片，但**它不是 Redis 式桶预分片**：

| 维度 | 朴素 hash 分片 | 桶预分片 |
|---|---|---|
| 业务公式 | `user_id % 4` | `hash(user_id) & 1023` |
| 公式里的"4" | 等于物理库数 | **远大于物理库数** |
| 加新库时 | 改成 `% 8`，全量 rehash | 改"桶→实例"映射，整表搬 |
| 适用场景 | 数据量稳定不打算扩容 | 任何可能扩容的场景 |

把"逻辑桶数"和"物理节点数"**解耦**，是 Redis Cluster 教给我们最宝贵的设计原则。MySQL 桶预分片只是把这条原则在关系库里再实现一遍。

## 一句话串起来

三件事本质一样：**加一层"逻辑分片层"把路由和物理部署解耦**。

- 一致性哈希用**虚拟节点**把分布抹平；
- Redis Cluster 用**16384 个固定 slot** 把控制权换到集群手里；
- MySQL 用**桶预分片**（远多于物理节点数的逻辑桶 + 桶→实例映射表）把同一思路搬到关系数据库。

只要这层够稳定，物理节点增减就不再是业务事故，而是一次 DBA 操作。

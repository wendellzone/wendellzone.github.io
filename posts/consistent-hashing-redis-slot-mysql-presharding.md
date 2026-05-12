---
title: 一致性哈希、Redis slot 与 MySQL 预分片
date: 2026-05-11
tags: [后端, 分布式, Redis, MySQL, Go]
summary: 把一致性哈希、Redis 16384 slot、MySQL 桶预分片串成同一条主线——都是在 key 和物理节点之间塞一层稳定的中间层；新增桶预分片与一致性哈希的正面对比。
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

智能客户端（`go-redis`、`lettuce` 等）启动时执行 `CLUSTER SLOTS` 缓存映射，每次请求自己算 slot 直连节点。如果路由表过期，节点返回两种重定向：

- **`MOVED`**：slot 已永久归属新节点，**客户端必须更新缓存**再重试。
- **`ASK`**：slot 迁移**进行中**，临时去新节点找一次（需先发 `ASKING`），**不更新缓存**。

`MOVED` 是永久的，`ASK` 是临时的——这两个区分让客户端在迁移期间也不会把缓存搞乱。

到这里就清楚了：**16384 是一层稳定的中间编号**，上面挂 key（CRC16 + hash tag），下面挂节点（gossip 维护的映射表）。slot 是 Redis Cluster 整套机制的**枢纽**——扩缩容、迁移、读写重定向，全都围绕"slot 归谁"展开。

## MySQL 分片：把 Redis 槽位思想搬到关系库

MySQL 预分片的思路和 Redis Cluster 一模一样，只是换了个名字叫 **bucket**：

> **预分片 = 桶预分片**。一次性切出远多于物理节点数的"逻辑桶"，业务路由公式永远不变，扩容只是改"桶 → 实例"映射表。

```
key → bucket：永远不变（hash & 1023）
bucket → 实例.schema.表：可在线变更（路由表维护）
```

和 Redis 唯一的差别：slot→node 由 gossip 自动维护，而 MySQL 的 bucket→实例映射靠 yaml/etcd 由 DBA 手工触发。其它原理完全一致。

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

### 三个设计决策

1. **桶数取 2 的幂**（1024、2048、4096）。`& (B-1)` 等价 `% B` 但快一个量级。
2. **物理 schema 数 ≪ 桶数**——1024 主要落在"表后缀"维度。在一台 MySQL 上建 512 个 schema 会让 `table_open_cache` 直接顶天。主流形态是 **8 实例 × 4 schema × 32 表 = 1024**：

| 方案 | 实例 × schema × 表 | 说明 |
|---|---|---|
| 极简 | 8 × 1 × 128 | metadata 开销最小 |
| **均衡** ✅ | **8 × 4 × 32** | **schema 粒度方便备份/迁移/权限隔离** |
| 重 schema | 8 × 32 × 4 | 每 schema 业务边界明显时用 |

3. **bucket → 实例.schema.表 是可变映射**，扩容只改这张表，业务公式不动。

### 一致性哈希 vs 桶预分片

讲到这里有必要把一致性哈希和桶预分片拉到一起对比——它们是同一类思路的两条不同路径：

| 维度 | 一致性哈希环 | 桶预分片（Redis 式） |
|---|---|---|
| 中间层 | 哈希环 + 虚拟节点 | 固定数量的桶（slot/bucket） |
| 路由层数 | 一层：key → 环上节点 | 两层：key → 桶 → 节点 |
| 路由信息 | 客户端各自维护一份环 | 集中映射表，统一推送 |
| 扩容粒度 | 顺时针的一段弧（不规则） | 任意一组桶（精确可控） |
| 热点处理 | 只能加节点 | 可单独迁某个桶 |
| 数据一致性要求 | 偏向最终一致（缓存场景多） | 严格一致（持久化场景多） |
| 业务侧公式 | hash(key) | hash(key) % B（B 不变） |
| 典型代表 | memcached、ketama、Cassandra | Redis Cluster、ShardingSphere、Vitess |

**一句话区分：一致性哈希是"去中心化、客户端自算环"，桶预分片是"中心化路由表 + 业务零感知"。** 缓存场景（短命数据、可丢可重建）适合前者；数据库场景（持久化、强一致）只能用后者。

下一节给出桶预分片的完整 Go 实现。

### Go 实现

**① bucket：算出 0~1023 的逻辑桶号**

```go
package sharding

import (
	"database/sql"
	"fmt"
	"hash/crc32"
)

const BucketCount = 1024 // 必须是 2 的幂

func bucketOf(key string) uint32 {
	return crc32.ChecksumIEEE([]byte(key)) & (BucketCount - 1)
}
```

**② 把 bucket 翻译成"实例 + schema + 表名"**

```go
const (
	InstanceCount  = 8  // 物理 MySQL 实例数
	SchemaPerNode  = 4  // 每实例的 schema 数
	TablePerSchema = 32 // 每 schema 的分表数
	// 8 × 4 × 32 = 1024 = BucketCount
)

type Router struct {
	instances [InstanceCount]*sql.DB
}

type Location struct {
	InstanceIdx int
	SchemaName  string
	TableName   string
}

func (r *Router) Locate(key, logicalTable string) (Location, *sql.DB) {
	bid := int(bucketOf(key))
	instIdx := bid / (SchemaPerNode * TablePerSchema)
	schIdx := (bid / TablePerSchema) % SchemaPerNode
	tbIdx := bid % TablePerSchema
	return Location{
		InstanceIdx: instIdx,
		SchemaName:  fmt.Sprintf("order_db_%d", schIdx),
		TableName:   fmt.Sprintf("%s_%d", logicalTable, tbIdx),
	}, r.instances[instIdx]
}
```

举例 `bucket=539` → mysql-5 / `order_db_0` / `t_order_27`。**连接池只跟实例挂钩，跟 schema 无关**——8 份 `*sql.DB`，SQL 里写完整限定名 `order_db_0.t_order_27` 即可。

**③ 路由表热更新（扩容关键）**

扩容不能重启服务，bucket→实例 映射必须能原子替换：

```go
import "sync/atomic"

type bucketMap struct {
	bucketToDB [BucketCount]*sql.DB
}

type LiveRouter struct {
	current atomic.Pointer[bucketMap]
}

func (r *LiveRouter) Update(m *bucketMap) { r.current.Store(m) }

func (r *LiveRouter) Pick(key string) *sql.DB {
	return r.current.Load().bucketToDB[bucketOf(key)]
}
```

为什么用 1024 长的查找表而不是"按实例数除"？**扩容时桶可以任意切分**——可能把 mysql-1 上的 bucket 64..127 搬到 mysql-9，剩下 0..63 还在 mysql-1。查找表能精确表达任意切分。

**④ 从 yaml 加载映射**

```yaml
instances:
  - { name: mysql-1, dsn: "user:pwd@tcp(10.0.0.1:3306)/", buckets: [0,    127] }
  - { name: mysql-2, dsn: "user:pwd@tcp(10.0.0.2:3306)/", buckets: [128,  255] }
  # ...
  - { name: mysql-8, dsn: "user:pwd@tcp(10.0.0.8:3306)/", buckets: [896, 1023] }
```

```go
func BuildBucketMap(cfgs []InstanceCfg) (*bucketMap, error) {
	m := &bucketMap{}
	for _, c := range cfgs {
		db, _ := sql.Open("mysql", c.DSN)
		for b := c.Buckets[0]; b <= c.Buckets[1]; b++ {
			m.bucketToDB[b] = db
		}
	}
	return m, nil
}
```

扩容就是改 yaml 区间，重新 `BuildBucketMap` → `Update`，应用代码不动。

### 扩容六阶段

只切路由表会丢数据——切换瞬间老库可能还有未同步的写入。生产标准做法 **"双写 + 追平 + 校验 + 切读 + 切写 + 回收"**：

| 阶段 | 写流量 | 读流量 | 关键动作 |
|---|---|---|---|
| 1. 存量同步 | 老库 | 老库 | xtrabackup / DTS 拷数据 |
| 2. 双写 | 老 + 新 | 老库 | 路由层影子写新库 |
| 3. 追平校验 | 老 + 新 | 老库 | pt-table-checksum 比对 |
| 4. 切读 | 老 + 新 | **新库** | 出问题随时切回 |
| 5. 切写 | **仅新库** | 新库 | `atomic.Store` 触发，<1s |
| 6. 回收 | 仅新库 | 新库 | 老库表保留 1~7 天再 drop |

双写代码片段（路由层封装，业务无感）：

```go
type DualWriter struct {
	primary, secondary *sql.DB
	enabled            atomic.Bool
}

func (d *DualWriter) Exec(query string, args ...any) (sql.Result, error) {
	res, err := d.primary.Exec(query, args...)
	if err != nil || !d.enabled.Load() {
		return res, err
	}
	go func() {
		if _, e := d.secondary.Exec(query, args...); e != nil {
			log.Errorw("dual_write_failed", "err", e)
		}
	}()
	return res, nil
}
```

要点：**老库为主**（新库失败只告警不阻塞）、**异步影子写**（不增加主路径延迟）、**binlog 兜底**（补上影子写漏掉的）。

### 三个常见坑

1. **分片键定了几乎不能改**。订单系统用 `user_id` 而不是 `order_id`，按用户的查询全落单桶。
2. **跨分片查询要预先规避**。需要"按商家维度查"就双写一份按 `merchant_id` 分桶的索引表，别想着运行时 scatter-gather。
3. **桶数宁多勿少**。1024 起步基本无上限压力，是唯一不能改的参数。

### 桶预分片 vs 朴素 hash 分库

最后澄清一个常见误解。很多人写"分库分表"会直接 `db_idx = user_id % 4; tbl_idx = (user_id / 4) % 4`，乍一看也像预分片，**但它不是 Redis 式桶预分片**：

| 维度 | 朴素 hash 分片 | 桶预分片 |
|---|---|---|
| 业务公式 | `user_id % 4` | `hash(user_id) & 1023` |
| 公式里的"4" | = 物理库数 | **远大于物理库数** |
| 加新库时 | 改成 `% 8`，全量 rehash | 改"桶→实例"映射，整表搬 |
| 适用场景 | 数据量稳定不打算扩容 | 任何可能扩容的场景 |

**把"逻辑桶数"和"物理节点数"解耦**，是 Redis Cluster 教给我们最宝贵的设计原则。MySQL 桶预分片只是把这条原则在关系库里再实现一遍。

## 一句话串起来

三件事本质一样：**加一层"逻辑分片层"把路由和物理部署解耦**。

- 一致性哈希用**虚拟节点**把分布抹平；
- Redis Cluster 用**16384 个固定 slot** 把控制权换到集群手里；
- MySQL 用**桶预分片**（远多于物理节点数的逻辑桶 + 桶→实例映射表）把同一思路搬到关系数据库。

只要这层够稳定，物理节点增减就不再是业务事故，而是一次 DBA 操作。

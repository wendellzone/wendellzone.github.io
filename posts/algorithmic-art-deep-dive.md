---
title: 拆解 algorithmic-art skill：做生成艺术先写哲学宣言再写代码
date: 2026-05-12
tags: [工具, AI, 生成艺术, 复盘]
summary: 先哲学、再概念种子、最后 p5.js——解析 Anthropic 生成艺术 skill 反直觉的创作顺序。
---

> 拆解 Anthropic 官方 algorithmic-art skill：为什么做生成艺术的第一步不是写代码，而是写"哲学宣言"。

## 一句话定义

algorithmic-art 是一套让 AI 做生成艺术的工作流，核心反直觉——**代码在最后写，先写一份算法哲学宣言**。

## 总览图

```plantuml
@startuml
skinparam backgroundColor transparent

start
:用户丢一句意图;
note right: "做个有机感的艺术"

:Step 1\n**写算法哲学宣言** (.md);
note right
  4-6 段
  命名一个流派
  描述计算美学
end note

:Step 2\n**推演概念种子**;
note right
  "这次做的作品到底致敬什么?"
  细节要藏起来，懂的人才懂
end note

:Step 3\n**读 viewer.html 模板**;
note right: 模板是起点，不是灵感

:Step 4\n**实现 p5.js 算法**;
note right
  90% 算法 + 10% 参数
  必须用 seed 保证可复现
end note

:输出单个 HTML artifact;
stop
@enduml
```

## 生活类比

这和**一位前辈画家先写画派宣言，再教徒弟画画**是同一个套路：

| 步骤                  | 传统艺术             | algorithmic-art      |
|---------------------|------------------|----------------------|
| 老师先写宣言            | "印象派要捕捉瞬间光影"   | "Organic Turbulence: 混沌受限于自然律" |
| 宣言定调               | 不能用黑色勾边、不画细节     | 一定要用 Perlin 噪声、粒子轨迹  |
| 徒弟照宣言创作           | 每张画不一样但都有印象派气质   | 每个 seed 生成不同画，但风格一致 |

**先哲学，再代码**——这是这个 skill 和普通生成艺术教程最大的区别。

## 核心拆解

### 1. 为什么要写哲学宣言？

```plantuml
@startuml
skinparam backgroundColor transparent

package "常规做法" {
  rectangle "收到需求" as A1
  rectangle "直接写 p5.js" as A2
  rectangle "调参碰运气" as A3
  A1 -down-> A2
  A2 -down-> A3
}

package "skill 做法" {
  rectangle "收到需求" as B1
  rectangle "写哲学 .md" as B2 #fff59d
  rectangle "推演概念种子" as B3
  rectangle "按哲学写 p5.js" as B4
  B1 -down-> B2
  B2 -down-> B3
  B3 -down-> B4
}

note bottom of A3
  容易做出
  "看起来都差不多"
  的作品
end note

note bottom of B4
  有灵魂
  有风格辨识度
end note
@enduml
```

不写哲学的后果：AI 会选一个流行模板（比如流场），调调参数，输出一张"长得像生成艺术"的图。写了哲学后：AI 被迫思考"这次的美在哪里"，再由美学反推算法选择。

### 2. 四类常见哲学模板

skill 给了五个范式，这里挑三个最典型的：

| 流派                  | 一句话哲学                | 算法对应            |
|---------------------|---------------------|-----------------|
| Organic Turbulence  | 混沌受限于自然律            | Perlin 噪声 + 粒子流场 |
| Quantum Harmonics   | 离散个体呈现波动干涉图样       | 网格粒子 + 相位干涉    |
| Recursive Whispers  | 有限空间里的无限自相似        | L-system + 黄金比递归 |
| Field Dynamics      | 让隐形的力通过物质痕迹显形    | 向量场 + 粒子轨迹遗留   |
| Stochastic Crystallization | 随机过程结晶为有序结构 | Voronoi + 松弛算法 |

**这张表的价值**在于：它把"哲学"和"算法"做了双向映射。有哲学没算法 = 空谈；有算法没哲学 = 套模板。

### 3. 哲学必须反复强调"大师手笔"

skill 里有一条很特别的要求：

> The philosophy MUST stress multiple times that the final algorithm should appear as though it took countless hours to develop...
> repeat phrases like "meticulously crafted algorithm," "painstaking optimization," "master-level implementation."

为什么要**反复**说？因为 LLM 在没被暗示的时候，会默认写出"差不多就行"的代码。明确提示"这是大师级工艺"后，它会：

- 用更讲究的调色盘（不默认 RGB）
- 加更多参数微调（不甩一个固定值）
- 写更讲究的粒子行为（不用最朴素的布朗运动）

**用 prompt 给 AI 植入审美自信心，是这个 skill 最有意思的技巧。**

### 4. 概念种子：藏在代码里的小彩蛋

```plantuml
@startuml
skinparam backgroundColor transparent

rectangle "用户需求\n'做个关于爵士乐的艺术'" as U

rectangle "表面看到" as S
rectangle "懂的人看到" as H

rectangle "作品\n(流场粒子)" as A

U -down-> A
A -right-> S : "好看"
A -right-> H : "粒子节奏像即兴 solo,\n颜色像 Blue Note 封面"

note bottom of H
  概念种子
  = 爵士乐的 DNA
  编织进参数里
end note
@enduml
```

skill 把这叫做"像爵士音乐家在独奏里引用另一首曲子"——懂的人会心一笑，不懂的也觉得好听。这种**隐藏层**让作品有"二次阅读"价值。

### 5. 为什么必须用 seed

```javascript
let seed = 12345;
randomSeed(seed);
noiseSeed(seed);
```

三个动机：

1. **可复现**：同一个 seed = 同一幅画，方便分享和迭代
2. **可探索**：prev/next/random 按钮让用户浏览"宇宙切片"
3. **可商品化**：Art Blocks 模式下，每个 seed = 一件独立 NFT

**这是从生成艺术商业实践直接借鉴来的工程规范，不是拍脑袋想的。**

### 6. 模板的刚性约束

```plantuml
@startuml
skinparam backgroundColor transparent

package "viewer.html (模板)" {
  rectangle "固定部分" as F #ffcdd2
  rectangle "可变部分" as V #c8e6c9
}

note right of F
  - 布局结构
  - Anthropic 配色/字体
  - Seed 面板 (prev/next/random/jump)
  - Actions (regenerate/reset/download)
end note

note right of V
  - p5.js 算法本身
  - parameters 对象
  - 参数控件（滑块/颜色选择器）
  - 是否需要 Colors 面板
end note
@enduml
```

skill 原文：

> The **template is the STARTING POINT**, not inspiration.

这条规则的作用是**把 UI 一致性和艺术自由度分开**——UI 锁死保证用户体验统一，艺术部分完全放飞保证作品差异。两个目标原本冲突，用这条规则解决掉了。

## 对比：写 vs 不写哲学

| 维度        | 不写哲学          | 写哲学          |
|-----------|---------------|-------------|
| 启动速度       | 快（直接上代码）     | 慢（要先想 10 分钟） |
| 风格辨识度      | 低（像网上教程）     | 高（有宣言做锚点）   |
| 参数选择依据     | "差不多"         | "哲学要求这样"     |
| 跨作品一致性     | 只靠调色盘        | 有哲学的连续性     |
| 调优时的判断标准   | "好看不好看"      | "符不符合宣言"   |

## 常见坑

- **上来就写代码**：跳过哲学这步，成品会"没魂"
- **哲学只写一次"大师级"**：LLM 会忽略，要重复 3-5 次才生效
- **不用 seed**：刷新一下作品就变了，没法沉淀
- **重写模板**：失去 UI 一致性，每件作品像在不同网站上
- **参数全给固定值**：失去"探索感"，用户点了跟没点一样
- **颜色随便 random(255)**：不协调，暴露"AI 味"；要用预设调色盘

## 一张图收尾

```plantuml
@startuml
skinparam backgroundColor transparent

(哲学宣言) --> (概念种子)
(概念种子) --> (p5.js 算法)
(p5.js 算法) --> (参数控件)
(参数控件) --> (Seed 探索)
(Seed 探索) --> (可复现作品)

note right of (哲学宣言) : 定调
note right of (概念种子) : 藏彩蛋
note right of (p5.js 算法) : 90% 重头戏
note right of (参数控件) : 10% 留白
note right of (可复现作品) : 商业化入口
@enduml
```

algorithmic-art 最值得学的不是 p5.js，是那个反直觉的顺序：**先写哲学，再谈工程**。AI 和人一样，有方向才有手感。

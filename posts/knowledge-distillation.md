---
title: 知识蒸馏入门：让小模型学会大模型的语气
date: 2026-05-26
tags: [AI, 机器学习, 模型压缩]
summary: 用最朴素的师生 + 软标签 + 温度框架讲清楚知识蒸馏：小模型怎么学会大模型的判断质感。
---

## 引子

一个 7 亿参数的小模型，可以跑出接近 110 亿参数大模型的效果。这不是炼丹奇迹，也不是堆算力——靠的是"抄作业"。

更准确地说，是一种叫**知识蒸馏**（Knowledge Distillation, KD）的训练范式：让一个小模型不直接从原始数据学，而是去模仿一个已经训练好的大模型的回答方式。听起来玄，其实结构非常朴素，思路也很老——Hinton 在 2015 年就把它写成论文了，最近几年才因为 LLM 的部署成本被重新捧热。

本篇只讲最基础的"师生 + 软标签 + 温度"框架，搞清楚蒸馏到底在干什么、为什么这么干。变体、实战案例、局限——这些后面再开篇聊。

## 为什么硬标签不够用

传统监督学习里，标签是 one-hot：一张图片里是猫，标签就是 `[猫=1, 狗=0, 狐狸=0]`。模型学的目标是"把猫这一栏的概率推到 1，其他推到 0"。

但一个训练得很好的大模型，不会用这种"非黑即白"的方式回答。给它同一张猫的图，它会输出：

> 猫 0.85 / 狐狸 0.10 / 狗 0.05

注意第二名是**狐狸**，不是狗。这不是模型搞错了——这恰好说明它知道"猫和狐狸长得有点像，跟狗差得远"。这种**类别之间的相对关系**，one-hot 标签里完全没有。换个角度看，one-hot 只描述了答案，而软分布同时描述了"答案 + 错得有多近"。

用一个比喻：标准答案告诉你正确选项，错题本告诉你为什么错。蒸馏要传给小模型的，正是错题本里的"判断质感"——这套质感被业内叫作**暗知识**（dark knowledge）。它不是训练数据里直接写下的内容，而是大模型在见过海量数据之后形成的隐式判断。

<svg viewBox="0 0 680 280" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
  <text x="340" y="26" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="500" fill="#222">硬标签 vs 软标签</text>
  <text x="170" y="56" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#666">硬标签（one-hot）</text>
  <text x="510" y="56" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#666">软标签（来自教师）</text>
  <line x1="340" y1="70" x2="340" y2="240" stroke="#ddd" stroke-width="0.5" stroke-dasharray="2 4"/>
  <g>
    <rect x="100" y="90" width="50" height="120" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <text x="125" y="226" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3C3489">猫 1.00</text>
    <rect x="170" y="208" width="50" height="2" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <text x="195" y="226" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#888">狐 0.00</text>
    <rect x="240" y="208" width="50" height="2" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <text x="265" y="226" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#888">狗 0.00</text>
  </g>
  <text x="170" y="252" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">只告诉答案</text>
  <g>
    <rect x="440" y="108" width="50" height="102" fill="#1D9E75" stroke="#0F6E56" stroke-width="0.5"/>
    <text x="465" y="226" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#0F6E56">猫 0.85</text>
    <rect x="510" y="198" width="50" height="12" fill="#1D9E75" stroke="#0F6E56" stroke-width="0.5"/>
    <text x="535" y="226" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#0F6E56">狐 0.10</text>
    <rect x="580" y="202" width="50" height="8" fill="#1D9E75" stroke="#0F6E56" stroke-width="0.5"/>
    <text x="605" y="226" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#0F6E56">狗 0.05</text>
  </g>
  <text x="510" y="252" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">告诉答案 + 类别之间的相似度</text>
</svg>

软标签的信息量，是硬标签的好几倍。

## 师生框架：核心架构

蒸馏的核心是两个模型 + 两路损失。

**教师模型**：一个已经训练好的大模型。大、准、慢，全程冻结，不再更新参数——它只负责"出题解"。

**学生模型**：一个待训练的小模型。小、快、便宜，参数量可能只有教师的几分之一。它要被训成"用更少的参数说出尽量像老师的话"。

每次训练时，同一份输入 `x` 会分别送进教师和学生，得到两份概率分布：教师的软标签 `q`，学生的输出 `p`。学生需要同时学两件事：

- **学教师**：用 KL 散度衡量 `p` 和 `q` 的差距——越像教师越好。
- **学真相**：用交叉熵衡量 `p` 和真实硬标签 `y` 的差距——别忘了正确答案。

总损失把这两项加权合起来：

$$L = \alpha \cdot KL(q \| p) + (1 - \alpha) \cdot CE(y, p)$$

**α** 是平衡系数。α 偏大，学生更像教师；α 偏小，学生更靠真实标签。常见取值在 0.5~0.9 之间——这意味着实践里，**软标签的权重通常比硬标签更大**。直觉是：硬标签只能告诉学生"这次答对了没"，软标签能告诉学生"教师当时是怎么思考的"，后者信息密度更高。

值得注意的是，蒸馏的有效性来自一个隐含假设：**教师足够好**。如果教师本身就把猫和狐狸搞混了，软标签里传递的就是错误判断，学生只会学得更歪。所以做蒸馏前，先评估一下教师在目标任务上的水平——蒸馏放大教师的优点，也放大它的缺陷。

<svg viewBox="0 0 680 360" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="kd-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>
  <text x="340" y="26" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="500" fill="#222">知识蒸馏的基本结构</text>
  <g>
    <rect x="40" y="150" width="120" height="56" rx="6" fill="#F1EFE8" stroke="#888780" stroke-width="0.5"/>
    <text x="100" y="180" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#444441">输入 x</text>
    <text x="100" y="196" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">图片 / 文本</text>
  </g>
  <g>
    <rect x="220" y="80" width="180" height="64" rx="8" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <text x="310" y="108" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#3C3489">教师模型（冻结）</text>
    <text x="310" y="128" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3C3489">大、准、不更新参数</text>
  </g>
  <g>
    <rect x="220" y="216" width="180" height="64" rx="8" fill="#9FE1CB" stroke="#0F6E56" stroke-width="0.5"/>
    <text x="310" y="244" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#0F6E56">学生模型（待训练）</text>
    <text x="310" y="264" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#0F6E56">小、快、被反向传播更新</text>
  </g>
  <path d="M160 168 L 220 110" fill="none" stroke="#888" stroke-width="1.2" marker-end="url(#kd-arrow)"/>
  <path d="M160 188 L 220 246" fill="none" stroke="#888" stroke-width="1.2" marker-end="url(#kd-arrow)"/>
  <g>
    <rect x="450" y="80" width="180" height="48" rx="6" fill="#FAC775" stroke="#854F0B" stroke-width="0.5"/>
    <text x="540" y="100" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#633806">软标签 q</text>
    <text x="540" y="118" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#633806">猫 0.85 · 狐 0.10 · 狗 0.05</text>
  </g>
  <g>
    <rect x="450" y="216" width="180" height="48" rx="6" fill="#FAC775" stroke="#854F0B" stroke-width="0.5"/>
    <text x="540" y="236" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#633806">学生输出 p</text>
    <text x="540" y="254" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#633806">猫 0.70 · 狐 0.20 · 狗 0.10</text>
  </g>
  <path d="M400 110 L 450 104" fill="none" stroke="#534AB7" stroke-width="1.2" marker-end="url(#kd-arrow)"/>
  <path d="M400 246 L 450 240" fill="none" stroke="#0F6E56" stroke-width="1.2" marker-end="url(#kd-arrow)"/>
  <path d="M540 128 Q 660 172 540 216" fill="none" stroke="#854F0B" stroke-width="1.2" marker-end="url(#kd-arrow)"/>
  <text x="666" y="172" font-family="sans-serif" font-size="11" fill="#854F0B">KL(q‖p)</text>
  <text x="666" y="188" font-family="sans-serif" font-size="11" fill="#854F0B">软损失</text>
  <g>
    <rect x="220" y="304" width="180" height="40" rx="6" fill="#F7C1C1" stroke="#A32D2D" stroke-width="0.5"/>
    <text x="310" y="328" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#A32D2D">真实标签 y（one-hot）</text>
  </g>
  <path d="M450 244 Q 380 290 400 324" fill="none" stroke="#A32D2D" stroke-width="1" stroke-dasharray="3 3" marker-end="url(#kd-arrow)"/>
  <text x="430" y="306" font-family="sans-serif" font-size="11" fill="#A32D2D">CE(y, p)</text>
  <text x="340" y="354" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">总损失 L = α · KL(q‖p) + (1−α) · CE(y, p)</text>
</svg>

## 温度：让暗知识"摊开"

到这里有个隐藏的问题：直接拿 softmax 出来的概率算 KL 散度，效果其实不好。

为什么？因为一个训练得不错的模型，softmax 输出会非常**尖锐**——比如猫 0.99，其他类别加起来才 0.01。这种"赢家通吃"的分布，几乎退化回 one-hot，软知识其实丢光了。

Hinton 在 2015 年的经典蒸馏论文里给了一个简单又关键的 trick：**给 softmax 加一个温度参数 T**。

$$p_i = \frac{\exp(z_i / T)}{\sum_j \exp(z_j / T)}$$

`z` 是模型最后一层的 logit。除以 T 之后：

- **T = 1**：原始 softmax，分布很尖。
- **T = 4**：分布被"摊开"，第二名第三名的概率被抬上来。
- **T = 10**：进一步平滑，类别间的相对关系最清晰。

训练阶段，**教师和学生用同一个高温 T**（典型值 4 或 10），让两边的分布都柔和一点，KL 散度才能学到有用的相似度信号。学生训完之后，推理时切回 T = 1，输出依然尖锐、依然能给一个明确的答案。

T 不是越大越好。T 太大时所有类别趋近均匀分布，原本的判断信息也跟着糊掉了。实际工程里 T 通常在 2~10 之间反复试，配合 α 一起调——这两个超参常常是蒸馏调优的主要开关。

<svg viewBox="0 0 680 280" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
  <text x="340" y="26" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="500" fill="#222">温度 T 对 softmax 分布的影响</text>
  <text x="120" y="56" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#666">T = 1（尖锐）</text>
  <text x="340" y="56" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#666">T = 4（摊开）</text>
  <text x="560" y="56" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#666">T = 10（平滑）</text>
  <line x1="40" y1="220" x2="640" y2="220" stroke="#888" stroke-width="0.5"/>
  <g>
    <rect x="60" y="80" width="40" height="140" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <text x="80" y="240" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3C3489">猫 0.99</text>
    <rect x="110" y="218" width="40" height="2" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <text x="130" y="240" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#888">狐 0.01</text>
    <rect x="160" y="219" width="40" height="1" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <text x="180" y="240" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#888">狗 0.00</text>
  </g>
  <g>
    <rect x="280" y="120" width="40" height="100" fill="#1D9E75" stroke="#0F6E56" stroke-width="0.5"/>
    <text x="300" y="240" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#0F6E56">猫 0.70</text>
    <rect x="330" y="190" width="40" height="30" fill="#1D9E75" stroke="#0F6E56" stroke-width="0.5"/>
    <text x="350" y="240" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#0F6E56">狐 0.20</text>
    <rect x="380" y="205" width="40" height="15" fill="#1D9E75" stroke="#0F6E56" stroke-width="0.5"/>
    <text x="400" y="240" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#0F6E56">狗 0.10</text>
  </g>
  <g>
    <rect x="500" y="160" width="40" height="60" fill="#F0997B" stroke="#993C1D" stroke-width="0.5"/>
    <text x="520" y="240" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#993C1D">猫 0.45</text>
    <rect x="550" y="180" width="40" height="40" fill="#F0997B" stroke="#993C1D" stroke-width="0.5"/>
    <text x="570" y="240" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#993C1D">狐 0.30</text>
    <rect x="600" y="187" width="40" height="33" fill="#F0997B" stroke="#993C1D" stroke-width="0.5"/>
    <text x="620" y="240" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#993C1D">狗 0.25</text>
  </g>
  <text x="340" y="266" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">T 越大，类别间的相对关系越清晰——这就是教师要传给学生的"暗知识"。</text>
</svg>

直觉上：**温度让模型从"咬死答案"切换到"讲讲为什么"**——后者才是学生该学的部分。

## 整体训练循环

把上面的零件拼起来，一个 batch 的训练长这样：

1. 取一批训练样本 `(x, y)`。
2. **教师推理**（无梯度，T = 高温）：得到软标签 q。
3. **学生推理**（T = 高温）：得到分布 p。
4. 计算软损失 `KL(q‖p)` 和硬损失 `CE(y, p)`，加权得到 L。
5. **反向传播只更新学生**——教师永远是冻结的。
6. 学生训完之后，部署时把 T 切回 1，推理输出就和普通模型一样尖锐。

整个流程的耗时大头在教师那边——它每个 batch 都要前向一次，但不需要反传，速度比训练快不少。学生这边和普通模型训练几乎没差别，多了一份 KL 损失而已。

实际项目里有两个常见优化：一是把教师对训练集的软标签**预先算好缓存**起来，训学生时直接读，省掉教师每个 batch 都跑前向的开销；二是教师只在训练初期权重大、后期把 α 慢慢调小，让学生在收尾阶段更靠真实标签。这些都是工程细节，但对大规模训练时的成本影响不小。

<svg viewBox="0 0 680 240" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="kd-arrow-2" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>
  <text x="340" y="26" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="500" fill="#222">一个 batch 的训练循环</text>
  <line x1="40" y1="170" x2="640" y2="170" stroke="#888" stroke-width="1" marker-end="url(#kd-arrow-2)"/>
  <text x="650" y="174" font-family="sans-serif" font-size="11" fill="#666">时间</text>
  <g>
    <circle cx="80" cy="170" r="8" fill="#888780"/>
    <text x="80" y="200" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#444441">取样本</text>
    <text x="80" y="216" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#888">(x, y)</text>
  </g>
  <g>
    <circle cx="200" cy="170" r="8" fill="#534AB7"/>
    <text x="200" y="200" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3C3489">教师 forward</text>
    <text x="200" y="216" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#888">无梯度 · T 高</text>
  </g>
  <g>
    <circle cx="320" cy="170" r="8" fill="#0F6E56"/>
    <text x="320" y="200" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#0F6E56">学生 forward</text>
    <text x="320" y="216" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#888">T 高</text>
  </g>
  <g>
    <circle cx="440" cy="170" r="8" fill="#854F0B"/>
    <text x="440" y="200" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#854F0B">算损失</text>
    <text x="440" y="216" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#888">α·KL + (1−α)·CE</text>
  </g>
  <g>
    <circle cx="560" cy="170" r="8" fill="#A32D2D"/>
    <text x="560" y="200" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#A32D2D">反向传播</text>
    <text x="560" y="216" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#888">只更新学生</text>
  </g>
  <text x="340" y="80" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#222">每个 batch 重复一次，直到学生收敛</text>
  <text x="340" y="104" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">教师全程冻结 · 学生学完后推理时 T 切回 1</text>
  <line x1="80" y1="158" x2="80" y2="120" stroke="#888780" stroke-width="0.5" stroke-dasharray="2 3"/>
  <line x1="200" y1="158" x2="200" y2="120" stroke="#534AB7" stroke-width="0.5" stroke-dasharray="2 3"/>
  <line x1="320" y1="158" x2="320" y2="120" stroke="#0F6E56" stroke-width="0.5" stroke-dasharray="2 3"/>
  <line x1="440" y1="158" x2="440" y2="120" stroke="#854F0B" stroke-width="0.5" stroke-dasharray="2 3"/>
  <line x1="560" y1="158" x2="560" y2="120" stroke="#A32D2D" stroke-width="0.5" stroke-dasharray="2 3"/>
</svg>

## 一句话收尾

蒸馏的本质，是把**模型容量换成训练算力**：你愿意多花一份算力来训练一个学生，换它在推理时永远跑得更快、更便宜。

它不创造新知识，只是把一个大模型已经学会的东西，搬给一个跑得起的小模型。

后续可以聊的方向还有不少：温度的数学直觉、Logit/Feature/Data 三种主流变体、DistilBERT 与 Alpaca 之类的真实案例、以及蒸馏 vs 量化 vs 剪枝怎么选。本篇先到这里——把"软标签 + 温度"这两块讲透，剩下的拼图就好接了。

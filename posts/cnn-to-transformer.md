---
title: 从卷积到注意力：神经网络的两种归纳偏置
date: 2026-05-20
tags: [AI, 机器学习, 科普]
summary: 从教机器人认猫的故事讲起，看 CNN 和 Transformer 两种架构如何用不同的归纳偏置看世界。
---

假设你要教一个机器人"认猫"。

**老师 A** 给它一副放大镜，让它在图片上一格格挪过去，先认出毛、胡须、耳朵这些零件，再拼出一只猫。

**老师 B** 不给放大镜，而是把图片切成几十块小方片，全摊在桌上，让机器人自己琢磨"哪两块该一起看"。

老师 A 教出来的是 **CNN（卷积神经网络）**，老师 B 教出来的是 **Transformer**。

这十年的故事，就是机器学界从普遍相信老师 A，慢慢改信老师 B 的过程。

## 老师 A：手把手教

CNN 的设计师非常贴心，提前往机器人脑子里塞了三条"图像常识"：

- **离得近的像素更相关**：猫的耳朵是局部的纹理，不用满图找
- **猫挪到图片哪里都还是猫**：用同一个"耳朵识别器"扫遍每个角落
- **从小零件拼大概念**：先认边缘 → 再认毛发 → 再认五官 → 最后认整只猫

这些常识硬编码在了"卷积"这个动作里 —— 就是那副放大镜。

<svg viewBox="0 0 680 240" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
  <text x="340" y="24" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="500" fill="#222">CNN：放大镜在图上一格格挪</text>
  <!-- 输入网格 -->
  <g>
    <text x="130" y="58" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#666">原图（一只猫）</text>
    <g stroke="#534AB7" stroke-width="0.5" fill="#CECBF6">
      <rect x="60" y="70" width="30" height="30"/>
      <rect x="90" y="70" width="30" height="30"/>
      <rect x="120" y="70" width="30" height="30"/>
      <rect x="150" y="70" width="30" height="30"/>
      <rect x="180" y="70" width="30" height="30"/>
      <rect x="60" y="100" width="30" height="30"/>
      <rect x="90" y="100" width="30" height="30"/>
      <rect x="120" y="100" width="30" height="30"/>
      <rect x="150" y="100" width="30" height="30"/>
      <rect x="180" y="100" width="30" height="30"/>
      <rect x="60" y="130" width="30" height="30"/>
      <rect x="90" y="130" width="30" height="30"/>
      <rect x="120" y="130" width="30" height="30"/>
      <rect x="150" y="130" width="30" height="30"/>
      <rect x="180" y="130" width="30" height="30"/>
      <rect x="60" y="160" width="30" height="30"/>
      <rect x="90" y="160" width="30" height="30"/>
      <rect x="120" y="160" width="30" height="30"/>
      <rect x="150" y="160" width="30" height="30"/>
      <rect x="180" y="160" width="30" height="30"/>
      <rect x="60" y="190" width="30" height="30"/>
      <rect x="90" y="190" width="30" height="30"/>
      <rect x="120" y="190" width="30" height="30"/>
      <rect x="150" y="190" width="30" height="30"/>
      <rect x="180" y="190" width="30" height="30"/>
    </g>
    <rect x="90" y="100" width="90" height="90" fill="none" stroke="#D85A30" stroke-width="2"/>
    <text x="135" y="148" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#993C1D">放大镜</text>
  </g>
  <defs>
    <marker id="cnn-arrow-1" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>
  <path d="M225 145 L 380 145" fill="none" stroke="#534AB7" stroke-width="1" marker-end="url(#cnn-arrow-1)"/>
  <text x="302" y="138" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">看一格、记一笔</text>
  <!-- 输出 -->
  <g>
    <text x="510" y="58" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#666">特征图（哪里像耳朵）</text>
    <g stroke="#534AB7" stroke-width="0.5" fill="#CECBF6">
      <rect x="450" y="100" width="30" height="30"/>
      <rect x="480" y="100" width="30" height="30"/>
      <rect x="510" y="100" width="30" height="30"/>
      <rect x="450" y="130" width="30" height="30" fill="#D85A30"/>
      <rect x="480" y="130" width="30" height="30"/>
      <rect x="510" y="130" width="30" height="30"/>
      <rect x="450" y="160" width="30" height="30"/>
      <rect x="480" y="160" width="30" height="30"/>
      <rect x="510" y="160" width="30" height="30"/>
    </g>
    <text x="465" y="150" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#fff" font-weight="500">✓</text>
  </g>
  <text x="340" y="225" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#888">同一副放大镜扫遍全图，所以猫挪到哪儿都能认出来</text>
</svg>

这种教法的好处是 **学得快**。机器人本来就被告诉"该往哪看、怎么看"，剩下的只是把每个零件长什么样填进去。给几万张图就能上手。

坏处也在这里：放大镜一次只能看一小块。要让机器人理解"图片左上角的猫和右下角的鱼之间的故事"，得堆很多层，让放大镜越变越大，绕得很麻烦。

## 老师 B：撒手不管

Transformer 的设计师反其道而行之 —— 什么常识都不预先告诉机器人。

它直接把图切成 196 块小方片，全部扔到桌子上，然后说："你们自己讨论吧。每一块都问问其他所有块：'我跟你多相关？'，然后按相关程度互相影响。"

<svg viewBox="0 0 680 280" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
  <text x="340" y="24" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="500" fill="#222">Transformer：每一块都跟所有块"对话"</text>
  <defs>
    <marker id="attn-arrow-1" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>
  <g font-family="sans-serif" font-size="12" font-weight="500">
    <circle cx="100" cy="160" r="18" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <text x="100" y="164" text-anchor="middle" fill="#3C3489">耳</text>
    <circle cx="200" cy="160" r="18" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <text x="200" y="164" text-anchor="middle" fill="#3C3489">脸</text>
    <circle cx="300" cy="160" r="18" fill="#D85A30" stroke="#993C1D" stroke-width="0.5"/>
    <text x="300" y="164" text-anchor="middle" fill="#fff">尾</text>
    <circle cx="400" cy="160" r="18" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <text x="400" y="164" text-anchor="middle" fill="#3C3489">爪</text>
    <circle cx="500" cy="160" r="18" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <text x="500" y="164" text-anchor="middle" fill="#3C3489">草</text>
    <circle cx="600" cy="160" r="18" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <text x="600" y="164" text-anchor="middle" fill="#3C3489">天</text>
  </g>
  <g stroke="#D85A30" fill="none" stroke-width="1">
    <path d="M285 150 Q 200 110 115 150" stroke-width="2" marker-end="url(#attn-arrow-1)"/>
    <path d="M286 152 Q 250 130 215 152" stroke-width="2" marker-end="url(#attn-arrow-1)"/>
    <path d="M315 150 Q 350 130 385 152" stroke-width="2" marker-end="url(#attn-arrow-1)"/>
    <path d="M315 150 Q 410 110 487 150" stroke-dasharray="2 2" marker-end="url(#attn-arrow-1)"/>
    <path d="M315 152 Q 460 100 587 150" stroke-dasharray="2 2" marker-end="url(#attn-arrow-1)"/>
  </g>
  <text x="300" y="210" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#993C1D">"尾巴"问其他每一块：「我跟你多相关？」</text>
  <text x="340" y="234" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#888">实线粗 = 相关度高（耳/脸/爪），虚线 = 相关度低（草/天）</text>
  <text x="340" y="254" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#888">相关度不是预设的，是机器人自己学出来的</text>
</svg>

这就是 **注意力（Attention）**：每一块都和所有块"开会讨论"，按相关度互相影响。

注意力没有放大镜的那些常识 —— 它**不假设相邻的块更相关**。也就是说，左上角的耳朵和右下角的尾巴，第一步就能直接对上话，不用绕路。

代价也明显：

- **要更多数据**。机器人没有现成常识，所有规律都得自己从图里看出来 —— 看十万张图可能不够，得上千万张
- **算得更慢**。每块都要跟每块对话，196 块就是 196² = 接近 4 万次对话，块越多越夸张

## 那"层"到底是什么？

前面一直说"放大镜扫一遍"、"小方片讨论一轮"。这里的"一遍 / 一轮"，就是一**层**。

一层 = 一道加工工序。神经网络是流水线，每层接收上一层的产物，做一次变换，再传给下一层。

### 为什么需要多层？

直觉很简单：**一层只能"画一刀"**。

把一堆点分类，如果红点在左、蓝点在右 —— 一刀切开就行，一层够用。但如果红点围成一圈、蓝点在外面 —— 怎么切都切不开。这种情况要先把空间"掰弯"，让两堆点上下分开，再切一刀。

<svg viewBox="0 0 680 240" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
  <text x="340" y="24" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="500" fill="#222">多层 = 先把空间"掰弯"，再切一刀</text>
  <defs>
    <marker id="layer-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>
  <text x="120" y="56" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#666">原始数据</text>
  <g>
    <circle cx="120" cy="80" r="5" fill="#534AB7"/>
    <circle cx="80" cy="105" r="5" fill="#534AB7"/>
    <circle cx="80" cy="155" r="5" fill="#534AB7"/>
    <circle cx="120" cy="180" r="5" fill="#534AB7"/>
    <circle cx="160" cy="155" r="5" fill="#534AB7"/>
    <circle cx="160" cy="105" r="5" fill="#534AB7"/>
    <circle cx="115" cy="125" r="5" fill="#D85A30"/>
    <circle cx="125" cy="135" r="5" fill="#D85A30"/>
    <circle cx="130" cy="118" r="5" fill="#D85A30"/>
  </g>
  <text x="120" y="218" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#888">圈内圈外切不开</text>
  <path d="M195 130 L 235 130" fill="none" stroke="#534AB7" stroke-width="1" marker-end="url(#layer-arrow)"/>
  <text x="215" y="120" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">第 1 层</text>
  <text x="340" y="56" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#666">第 1 层加工后</text>
  <g>
    <circle cx="290" cy="80" r="5" fill="#534AB7"/>
    <circle cx="310" cy="85" r="5" fill="#534AB7"/>
    <circle cx="330" cy="78" r="5" fill="#534AB7"/>
    <circle cx="350" cy="82" r="5" fill="#534AB7"/>
    <circle cx="370" cy="86" r="5" fill="#534AB7"/>
    <circle cx="390" cy="80" r="5" fill="#534AB7"/>
    <circle cx="320" cy="180" r="5" fill="#D85A30"/>
    <circle cx="340" cy="185" r="5" fill="#D85A30"/>
    <circle cx="360" cy="178" r="5" fill="#D85A30"/>
  </g>
  <text x="340" y="218" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#888">空间被掰弯，上下分开</text>
  <path d="M415 130 L 455 130" fill="none" stroke="#534AB7" stroke-width="1" marker-end="url(#layer-arrow)"/>
  <text x="435" y="120" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">第 2 层</text>
  <text x="555" y="56" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#666">第 2 层切一刀</text>
  <g>
    <circle cx="500" cy="80" r="5" fill="#534AB7"/>
    <circle cx="520" cy="85" r="5" fill="#534AB7"/>
    <circle cx="540" cy="78" r="5" fill="#534AB7"/>
    <circle cx="560" cy="82" r="5" fill="#534AB7"/>
    <circle cx="580" cy="86" r="5" fill="#534AB7"/>
    <circle cx="600" cy="80" r="5" fill="#534AB7"/>
    <circle cx="530" cy="180" r="5" fill="#D85A30"/>
    <circle cx="550" cy="185" r="5" fill="#D85A30"/>
    <circle cx="570" cy="178" r="5" fill="#D85A30"/>
    <line x1="490" y1="130" x2="610" y2="130" stroke="#1D9E75" stroke-width="1.5"/>
  </g>
  <text x="555" y="218" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#1D9E75">切开 ✓</text>
</svg>

> 单层 = 画一刀，多层 = 先掰几次空间，让最后那一刀刚好切到正确的地方。

这就是为什么叫"深度"学习 —— 关键不是每层多复杂，而是层数足够多，把复杂规律拆成一连串简单的小变换。

### CNN 和 Transformer 的"分层逻辑"完全不同

虽然两者都用多层，但每层在做的事不一样：

**CNN：每层学一个新概念**（像工厂分工，一道工序出一种零件）

| 层 | 这层在做什么 | 输出 |
|---|---|---|
| 第 1 层 | 找边和角 | 边缘图 |
| 第 2 层 | 把边缘组合成纹理 | 纹理图 |
| 第 3 层 | 把纹理组合成五官 | 五官图 |
| 第 4 层 | 把五官组合成脸 | 脸的特征 |
| 第 5 层 | 判断是不是猫 | 是 / 否 |

**Transformer：每层做同一件事，理解逐层加深**（像一群人反复讨论同一件事）

每层做的事固定是：**所有 token 互相讨论一轮 + 各自整理思路**（这两步的工程名字叫"注意力"和"前馈网络 FFN"，一层里两个都有）。

假设输入「猫坐在垫子上」，"猫"这个 token 在每层后含义会变深：

| 层 | "猫"的含义变化 |
|---|---|
| 输入 | 就是"猫"这个字 |
| 第 1 层后 | "猫" + 我是名词 |
| 第 3 层后 | "猫" + 我是主语 + 我坐在垫子上 |
| 第 6 层后 | "猫" + 我是这个宠物日常场景的核心 |

注意 ——"猫"这个字面没变，但它对应的含义向量在每一层之后都更丰富。每层的算子结构都一样（让所有 token 互相讨论一轮），只是讨论的语境越来越深。

<svg viewBox="0 0 680 240" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
  <text x="340" y="24" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="500" fill="#222">两种分层逻辑</text>
  <line x1="340" y1="50" x2="340" y2="220" stroke="#ddd" stroke-width="0.5" stroke-dasharray="2 4"/>
  <text x="170" y="60" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#222">CNN：工厂分工</text>
  <g font-family="sans-serif" font-size="11">
    <rect x="80" y="80" width="180" height="22" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5" rx="3"/>
    <text x="170" y="96" text-anchor="middle" fill="#3C3489">第 1 层：认边</text>
    <rect x="80" y="108" width="180" height="22" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5" rx="3"/>
    <text x="170" y="124" text-anchor="middle" fill="#3C3489">第 2 层：认纹理</text>
    <rect x="80" y="136" width="180" height="22" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5" rx="3"/>
    <text x="170" y="152" text-anchor="middle" fill="#3C3489">第 3 层：认五官</text>
    <rect x="80" y="164" width="180" height="22" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5" rx="3"/>
    <text x="170" y="180" text-anchor="middle" fill="#3C3489">第 4 层：认整脸</text>
  </g>
  <text x="170" y="208" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#888">每层做不同的活</text>
  <text x="510" y="60" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#222">Transformer：反复讨论</text>
  <g font-family="sans-serif" font-size="11">
    <rect x="420" y="80" width="180" height="22" fill="#D85A30" stroke="#993C1D" stroke-width="0.5" rx="3"/>
    <text x="510" y="96" text-anchor="middle" fill="#fff">第 1 层：讨论 + 整理思路</text>
    <rect x="420" y="108" width="180" height="22" fill="#D85A30" stroke="#993C1D" stroke-width="0.5" rx="3"/>
    <text x="510" y="124" text-anchor="middle" fill="#fff">第 2 层：讨论 + 整理思路</text>
    <rect x="420" y="136" width="180" height="22" fill="#D85A30" stroke="#993C1D" stroke-width="0.5" rx="3"/>
    <text x="510" y="152" text-anchor="middle" fill="#fff">第 3 层：讨论 + 整理思路</text>
    <rect x="420" y="164" width="180" height="22" fill="#D85A30" stroke="#993C1D" stroke-width="0.5" rx="3"/>
    <text x="510" y="180" text-anchor="middle" fill="#fff">第 4 层：讨论 + 整理思路</text>
  </g>
  <text x="510" y="208" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#888">每层做相同的活，但理解越来越深</text>
</svg>

有意思的是：研究者后来用工具去探测 GPT 的内部，发现 **Transformer 自己也学出了类似 CNN 的层级**——浅层处理语法，中层处理语义，深层处理逻辑推理。

但这个层级**不是被设计的**，是模型从数据里自己长出来的。这正是"老师 B 撒手不管"的精彩之处。

## 顺便分清：注意力 ≠ Transformer

这俩词很容易混。打个比方：

| 概念 | 是什么 | 类比 |
|---|---|---|
| 注意力（Attention） | 上面说的"互相打分"那个动作 | 发动机 |
| Transformer | 把注意力 + 一堆零件组装好的整车 | 整车 |

注意力 2014 年就有了，最早是装在 RNN 这种老架构上当配件用。Transformer 是 2017 年提出的，它的贡献是说："RNN 不要了，光靠注意力就够了"。所以那篇论文标题字面意思就是 **《Attention Is All You Need》**。

## 谁赢了？看你有多少数据

| 你的处境 | 该选谁 | 为什么 |
|---|---|---|
| 数据不多（一两万张图） | 老师 A（CNN） | 常识帮你省了大量学习成本 |
| 数据中等（百万级） | 两者打平 | 数据基本能弥补常识差距 |
| 数据很多（千万级以上） | 老师 B（Transformer） | 这时常识反而是束缚，自己学出来的更准 |
| 不止图像（视频、语音、文本一起） | 老师 B | 老师 A 的常识只对图像有用 |

OpenAI 喂 GPT 几千亿个词，Google 喂 ViT 三亿张图。这种规模下，谁还在乎你那点"常识"？数据自己就是最好的老师。

## 现在大家都在偷偷"作弊"

到了 2024 年之后，纯老师 A 和纯老师 B 都不流行了。两边在互相抄作业：

- **CNN 学 Transformer**：把放大镜做得更大，让一次能看到的范围接近全图
- **Transformer 学 CNN**：先把图切成大块讨论，再切小块讨论，加点"局部常识"回来
- **干脆混着用**：一层卷积一层注意力，交替堆

这件事告诉我们一个朴素道理：**没有最好的架构，只有最合适的偏见**。

## 一句话带走

> 数据稀少，就让模型多带点常识入场（CNN）。
>
> 数据足够多，就让它把常识扔了，自己学（Transformer）。

剩下的事，交给你的数据集和钱包决定。

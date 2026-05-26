---
title: 神经元到底在算什么：从生物到伪代码
date: 2026-05-26
tags: [深度学习, 神经网络, 科普]
summary: 从生物神经元的三段式结构推到 30 行伪代码，讲清一颗人工神经元如何加权求和并通过激活函数引入非线性。
---

先看一张大脑切片下的真实神经元：一根长长的轴突，一堆树突像树枝一样伸出去。它是怎么"算东西"的？答案出乎意料地朴素——它只做两件事：**收信号、判断要不要发信号**。

人工神经元几乎照抄了这个机制，并且简化到 30 行伪代码就能讲完。这篇文章从生物原型出发，一路推到现代深度学习里那个最小的计算单元。

## 生物神经元：一个加权投票器

一颗生物神经元的结构可以抽象成三段：

- **树突**：从上游别的神经元收信号
- **胞体**：把收到的信号累加起来，看够不够"强"
- **轴突**：如果够强，就向下游放电（"激活"）

关键点：上游来的信号不是一视同仁的。某些突触连接强、某些弱，相当于每路输入自带一个**权重**。

<svg viewBox="0 0 680 280" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="bio-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="#666"/>
    </marker>
  </defs>
  <rect x="0" y="0" width="680" height="280" fill="#fafafa"/>
  <text x="340" y="24" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#222">生物神经元的三段式</text>
  <circle cx="80" cy="80" r="18" fill="#e8d5ff" stroke="#7e3ff2" stroke-width="2"/>
  <circle cx="80" cy="140" r="18" fill="#e8d5ff" stroke="#7e3ff2" stroke-width="2"/>
  <circle cx="80" cy="200" r="18" fill="#e8d5ff" stroke="#7e3ff2" stroke-width="2"/>
  <text x="50" y="84" text-anchor="end" font-family="sans-serif" font-size="11" fill="#555">上游 1</text>
  <text x="50" y="144" text-anchor="end" font-family="sans-serif" font-size="11" fill="#555">上游 2</text>
  <text x="50" y="204" text-anchor="end" font-family="sans-serif" font-size="11" fill="#555">上游 3</text>
  <line x1="98" y1="80" x2="280" y2="135" stroke="#999" stroke-width="1.5" marker-end="url(#bio-arrow)"/>
  <line x1="98" y1="140" x2="280" y2="148" stroke="#999" stroke-width="1.5" marker-end="url(#bio-arrow)"/>
  <line x1="98" y1="200" x2="280" y2="161" stroke="#999" stroke-width="1.5" marker-end="url(#bio-arrow)"/>
  <text x="180" y="100" font-family="sans-serif" font-size="11" fill="#888">树突</text>
  <text x="180" y="155" font-family="sans-serif" font-size="11" fill="#888">树突</text>
  <text x="180" y="195" font-family="sans-serif" font-size="11" fill="#888">树突</text>
  <ellipse cx="320" cy="148" rx="50" ry="40" fill="#fff3cd" stroke="#d39e00" stroke-width="2"/>
  <text x="320" y="145" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">胞体</text>
  <text x="320" y="162" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">求和 + 阈值</text>
  <line x1="370" y1="148" x2="560" y2="148" stroke="#666" stroke-width="3" marker-end="url(#bio-arrow)"/>
  <text x="465" y="140" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">轴突（放电传给下游）</text>
  <circle cx="600" cy="148" r="22" fill="#d4f1d4" stroke="#28a745" stroke-width="2"/>
  <text x="600" y="152" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">下游</text>
</svg>

胞体做的事其实就是一道加法题：把所有树突信号加起来，超过阈值就放电，没超过就保持安静。

## 人工神经元：把上面那段写成数学

把上面三段直接翻译成数学，就是一颗**人工神经元**：

| 生物 | 人工 |
|---|---|
| 树突收信号 | 输入向量 `x = [x₁, x₂, ..., xₙ]` |
| 突触强弱 | 权重向量 `w = [w₁, w₂, ..., wₙ]` |
| 胞体求和 | 加权和 `z = w·x + b` |
| 阈值放电 | 激活函数 `a = f(z)` |

`b` 是偏置（bias），相当于"这颗神经元天生倾向于放电还是安静"的基线。

整个计算就一步：**先加权求和，再过一道激活函数**。

<svg viewBox="0 0 680 260" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="art-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="#555"/>
    </marker>
  </defs>
  <rect x="0" y="0" width="680" height="260" fill="#fafafa"/>
  <text x="340" y="24" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#222">人工神经元的两步计算</text>
  <circle cx="60" cy="80" r="18" fill="#cfe8ff" stroke="#1971c2" stroke-width="2"/>
  <circle cx="60" cy="140" r="18" fill="#cfe8ff" stroke="#1971c2" stroke-width="2"/>
  <circle cx="60" cy="200" r="18" fill="#cfe8ff" stroke="#1971c2" stroke-width="2"/>
  <text x="60" y="84" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#0c4a8e">x₁</text>
  <text x="60" y="144" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#0c4a8e">x₂</text>
  <text x="60" y="204" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#0c4a8e">x₃</text>
  <line x1="78" y1="80" x2="280" y2="135" stroke="#888" stroke-width="1.5" marker-end="url(#art-arrow)"/>
  <line x1="78" y1="140" x2="280" y2="148" stroke="#888" stroke-width="1.5" marker-end="url(#art-arrow)"/>
  <line x1="78" y1="200" x2="280" y2="161" stroke="#888" stroke-width="1.5" marker-end="url(#art-arrow)"/>
  <text x="170" y="100" font-family="sans-serif" font-size="11" fill="#1971c2">w₁</text>
  <text x="170" y="138" font-family="sans-serif" font-size="11" fill="#1971c2">w₂</text>
  <text x="170" y="195" font-family="sans-serif" font-size="11" fill="#1971c2">w₃</text>
  <rect x="290" y="118" width="100" height="60" rx="8" fill="#fff3cd" stroke="#d39e00" stroke-width="2"/>
  <text x="340" y="142" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">Σ</text>
  <text x="340" y="162" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#555">z = w·x + b</text>
  <line x1="390" y1="148" x2="450" y2="148" stroke="#555" stroke-width="2" marker-end="url(#art-arrow)"/>
  <rect x="460" y="118" width="100" height="60" rx="8" fill="#d4f1d4" stroke="#28a745" stroke-width="2"/>
  <text x="510" y="142" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#333">f(·)</text>
  <text x="510" y="162" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#555">激活函数</text>
  <line x1="560" y1="148" x2="640" y2="148" stroke="#555" stroke-width="2" marker-end="url(#art-arrow)"/>
  <text x="650" y="152" text-anchor="end" font-family="sans-serif" font-size="12" fill="#222" font-weight="bold">a</text>
  <text x="640" y="170" text-anchor="end" font-family="sans-serif" font-size="11" fill="#888">输出</text>
</svg>

## 30 行伪代码：一颗神经元的全部

把上面这张图翻译成伪代码，就是这样：

```python
class Neuron:
    def __init__(self, input_size):
        # 权重和偏置：可以学习的参数
        self.w = random_vector(input_size)   # 长度为 n
        self.b = 0.0

    def forward(self, x):
        # 第一步：加权求和
        z = 0.0
        for i in range(len(x)):
            z += self.w[i] * x[i]
        z += self.b

        # 第二步：过激活函数（这里用 ReLU 举例）
        a = relu(z)
        return a


def relu(z):
    # 负数清零，正数原样返回
    if z > 0:
        return z
    else:
        return 0
```

就这些。一颗神经元的全部计算逻辑装得下三十行。

## 激活函数：那道"要不要放电"的开关

加权求和只是把输入混在一起，并没有引入"决策"。决策来自激活函数。

常见的几种长这样：

| 激活函数 | 公式 | 行为 |
|---|---|---|
| Step | z>0 时输出 1，否则 0 | 最早期感知机的开关，硬切换 |
| Sigmoid | 1 / (1 + e⁻ᶻ) | 把任意值压到 0~1，平滑过渡 |
| ReLU | max(0, z) | 负数清零，正数透传，现代默认选择 |
| Tanh | (eᶻ - e⁻ᶻ)/(eᶻ + e⁻ᶻ) | 把任意值压到 -1~1 |

<svg viewBox="0 0 680 240" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="0" y="0" width="680" height="240" fill="#fafafa"/>
  <text x="340" y="22" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold" fill="#222">三种常见激活函数的形状</text>
  <g transform="translate(40,50)">
    <text x="80" y="-6" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#555">Step</text>
    <line x1="0" y1="80" x2="160" y2="80" stroke="#bbb" stroke-width="1"/>
    <line x1="80" y1="20" x2="80" y2="140" stroke="#bbb" stroke-width="1"/>
    <path d="M0,80 L80,80 L80,40 L160,40" fill="none" stroke="#1971c2" stroke-width="2.5"/>
  </g>
  <g transform="translate(240,50)">
    <text x="80" y="-6" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#555">Sigmoid</text>
    <line x1="0" y1="80" x2="160" y2="80" stroke="#bbb" stroke-width="1"/>
    <line x1="80" y1="20" x2="80" y2="140" stroke="#bbb" stroke-width="1"/>
    <path d="M0,75 C40,75 60,40 80,40 C100,40 120,75 160,75" fill="none" stroke="#7e3ff2" stroke-width="2.5"/>
  </g>
  <g transform="translate(440,50)">
    <text x="80" y="-6" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#555">ReLU</text>
    <line x1="0" y1="80" x2="160" y2="80" stroke="#bbb" stroke-width="1"/>
    <line x1="80" y1="20" x2="80" y2="140" stroke="#bbb" stroke-width="1"/>
    <path d="M0,80 L80,80 L160,20" fill="none" stroke="#28a745" stroke-width="2.5"/>
  </g>
  <text x="340" y="220" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#888">横轴 z，纵轴 a = f(z)</text>
</svg>

为什么需要它？因为如果没有激活函数，无论叠多少层神经元，整个网络等价于一次线性变换——能力上限被锁死。激活函数引入非线性，整个深度学习才有"表达任意函数"的潜力。

## 一颗神经元能干什么

单颗神经元能力有限。它本质上是一个**线性分类器**：在输入空间里画一条直线（或一个超平面），线一侧输出大、另一侧输出小。

它能解的问题：

- 判断一封邮件是否垃圾邮件（输入：词频统计）
- 判断一个像素属于前景还是背景（输入：颜色 + 位置）
- 判断某个用户会不会点击广告（输入：用户特征）

它解不了的问题：异或（XOR）。一条直线没法把 (0,0)/(1,1) 跟 (0,1)/(1,0) 分开。

解决办法：把多颗神经元堆成多层。这就是"神经网络"——下一篇可以接着讲。

## 收尾

记住三件事：

1. **一颗神经元 = 加权求和 + 激活函数**。三十行伪代码足以装下。
2. **权重 w 和偏置 b 是可学习参数**。训练就是在调它们。
3. **激活函数是非线性的来源**。没有它，再深的网络也只是一次线性回归。

把这三件事咀嚼清楚，深度学习里几乎所有概念——前向传播、反向传播、梯度下降——都是在这颗最小单元上做的扩展。

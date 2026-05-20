---
title: 从 if-else 到大模型：一次讲清 ML、DL、预训练、微调
date: 2026-05-20
tags: [AI, 机器学习, 深度学习, 大模型]
summary: 用一个识猫的例子串起 ML、DL、预训练、微调和对齐，科普向，4 张图讲清楚。
---

假设你想教电脑识别"猫"。

传统程序员的做法：写一堆 `if 耳朵尖 and 有胡须 and 会喵喵叫 ...`。写到崩溃也覆盖不全——猫的姿态、光线、品种太多了。

机器学习的做法：扔一万张猫的照片给电脑，让它自己总结规律。这就是"学习"。深度学习是机器学习里最近十几年最能打的那一支。大模型则是深度学习被推到极致后的新物种。

下面顺着这条主线讲下来：ML 是什么 → DL 怎么不一样 → 大模型怎么训出来 → 微调怎么把通用模型变专用。

## 一句话讲清三者的关系

人工智能（AI）是大目标，机器学习（ML）是实现 AI 的一种主流方法，深度学习（DL）是机器学习里的一个分支。

<svg viewBox="0 0 680 280" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="20" width="640" height="240" rx="12" fill="#fef3c7" stroke="#f59e0b" stroke-width="2"/>
  <text x="40" y="50" font-family="sans-serif" font-size="14" font-weight="bold" fill="#92400e">人工智能 AI</text>
  <text x="40" y="70" font-family="sans-serif" font-size="11" fill="#92400e">让机器表现出"智能"行为的总目标</text>
  <rect x="80" y="90" width="500" height="150" rx="10" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <text x="100" y="120" font-family="sans-serif" font-size="14" font-weight="bold" fill="#1e3a8a">机器学习 ML</text>
  <text x="100" y="140" font-family="sans-serif" font-size="11" fill="#1e3a8a">从数据里学规律，而不是手写规则</text>
  <rect x="160" y="160" width="380" height="70" rx="8" fill="#dcfce7" stroke="#16a34a" stroke-width="2"/>
  <text x="180" y="190" font-family="sans-serif" font-size="14" font-weight="bold" fill="#14532d">深度学习 DL（含大模型）</text>
  <text x="180" y="210" font-family="sans-serif" font-size="11" fill="#14532d">用多层神经网络自动学特征</text>
</svg>

外层包内层：DL ⊂ ML ⊂ AI。大模型也住在 DL 这层里，只是网络更深、参数更多。

## 机器学习在干啥

机器学习的核心套路只有三步：

1. **喂数据**：给一堆带答案的样本（输入 + 标签）。
2. **找规律**：让模型调参数，让"预测"尽量贴近"标签"。
3. **用模型**：拿新的输入丢给模型，输出预测。

| 任务 | 输入 | 输出 | 典型算法 |
|---|---|---|---|
| 房价预测 | 面积、地段、楼层 | 价格（数字） | 线性回归 |
| 邮件分类 | 邮件文本 | 是 / 不是垃圾 | 朴素贝叶斯、SVM |
| 用户分群 | 用户行为日志 | 第几类人 | K-Means |
| 图像识别 | 图片像素 | 是猫 / 是狗 / 是车 | 决策树、神经网络 |

注意第一行：传统机器学习里，"面积、地段、楼层"这些特征是**人工挑出来的**。你得先想清楚什么因素影响房价，再把它们提取成数字喂给模型。

特征工程是传统机器学习的体力活，也是天花板。

## 深度学习又有什么不一样

深度学习的本质：用一堆叠在一起的"神经元"，让模型自己学特征，不再依赖人工。

光看这一句还是不够具象。先看下面这张大图，再把"神经元"、"层"、"自己学"三件事一一拆开讲。

<svg viewBox="0 0 680 320" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="dl-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="#6b7280"/>
    </marker>
  </defs>
  <text x="20" y="30" font-family="sans-serif" font-size="12" font-weight="bold" fill="#374151">传统 ML：人工提特征 → 模型学权重</text>
  <rect x="20" y="50" width="100" height="40" rx="6" fill="#fee2e2" stroke="#dc2626" stroke-width="1.5"/>
  <text x="70" y="74" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#7f1d1d">原始图片</text>
  <rect x="160" y="50" width="160" height="40" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="240" y="68" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#92400e">人工设计特征</text>
  <text x="240" y="82" font-family="sans-serif" font-size="10" text-anchor="middle" fill="#92400e">(边缘/颜色/纹理...)</text>
  <rect x="360" y="50" width="120" height="40" rx="6" fill="#dbeafe" stroke="#2563eb" stroke-width="1.5"/>
  <text x="420" y="74" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#1e3a8a">分类器</text>
  <rect x="520" y="50" width="100" height="40" rx="6" fill="#dcfce7" stroke="#16a34a" stroke-width="1.5"/>
  <text x="570" y="74" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#14532d">是猫 / 不是</text>
  <line x1="120" y1="70" x2="158" y2="70" stroke="#6b7280" stroke-width="1.5" marker-end="url(#dl-arrow)"/>
  <line x1="320" y1="70" x2="358" y2="70" stroke="#6b7280" stroke-width="1.5" marker-end="url(#dl-arrow)"/>
  <line x1="480" y1="70" x2="518" y2="70" stroke="#6b7280" stroke-width="1.5" marker-end="url(#dl-arrow)"/>
  <text x="20" y="160" font-family="sans-serif" font-size="12" font-weight="bold" fill="#374151">深度学习：原始数据直接进模型，特征自己学</text>
  <rect x="20" y="180" width="100" height="40" rx="6" fill="#fee2e2" stroke="#dc2626" stroke-width="1.5"/>
  <text x="70" y="204" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#7f1d1d">原始图片</text>
  <rect x="160" y="170" width="380" height="120" rx="8" fill="#ede9fe" stroke="#7c3aed" stroke-width="2"/>
  <text x="350" y="195" font-family="sans-serif" font-size="11" font-weight="bold" text-anchor="middle" fill="#5b21b6">多层神经网络（深度）</text>
  <circle cx="200" cy="240" r="10" fill="#a78bfa"/>
  <circle cx="200" cy="270" r="10" fill="#a78bfa"/>
  <circle cx="270" cy="225" r="10" fill="#a78bfa"/>
  <circle cx="270" cy="255" r="10" fill="#a78bfa"/>
  <circle cx="270" cy="285" r="10" fill="#a78bfa"/>
  <circle cx="340" cy="240" r="10" fill="#a78bfa"/>
  <circle cx="340" cy="270" r="10" fill="#a78bfa"/>
  <circle cx="410" cy="225" r="10" fill="#a78bfa"/>
  <circle cx="410" cy="255" r="10" fill="#a78bfa"/>
  <circle cx="410" cy="285" r="10" fill="#a78bfa"/>
  <circle cx="490" cy="240" r="10" fill="#a78bfa"/>
  <circle cx="490" cy="270" r="10" fill="#a78bfa"/>
  <line x1="200" y1="240" x2="270" y2="225" stroke="#c4b5fd" stroke-width="0.8"/>
  <line x1="200" y1="240" x2="270" y2="255" stroke="#c4b5fd" stroke-width="0.8"/>
  <line x1="200" y1="270" x2="270" y2="255" stroke="#c4b5fd" stroke-width="0.8"/>
  <line x1="200" y1="270" x2="270" y2="285" stroke="#c4b5fd" stroke-width="0.8"/>
  <line x1="270" y1="225" x2="340" y2="240" stroke="#c4b5fd" stroke-width="0.8"/>
  <line x1="270" y1="255" x2="340" y2="240" stroke="#c4b5fd" stroke-width="0.8"/>
  <line x1="270" y1="285" x2="340" y2="270" stroke="#c4b5fd" stroke-width="0.8"/>
  <line x1="340" y1="240" x2="410" y2="225" stroke="#c4b5fd" stroke-width="0.8"/>
  <line x1="340" y1="270" x2="410" y2="285" stroke="#c4b5fd" stroke-width="0.8"/>
  <line x1="410" y1="225" x2="490" y2="240" stroke="#c4b5fd" stroke-width="0.8"/>
  <line x1="410" y1="285" x2="490" y2="270" stroke="#c4b5fd" stroke-width="0.8"/>
  <rect x="580" y="200" width="80" height="40" rx="6" fill="#dcfce7" stroke="#16a34a" stroke-width="1.5"/>
  <text x="620" y="224" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#14532d">是猫</text>
  <line x1="120" y1="200" x2="158" y2="225" stroke="#6b7280" stroke-width="1.5" marker-end="url(#dl-arrow)"/>
  <line x1="540" y1="225" x2="578" y2="220" stroke="#6b7280" stroke-width="1.5" marker-end="url(#dl-arrow)"/>
</svg>

那一坨紫色圆圈就是"神经网络"。每个圆圈是一个**神经元**，每条连线代表一次信号传递。"深度"二字就指中间这一坨有多少层——早期 2~3 层，现在的大模型动辄上百层。

下面把这张图里被压缩掉的细节展开。

### 一个"神经元"到底在算什么

听起来很玄，其实就一个公式级别的小函数。

把一个神经元想象成"加权打分器"：它收一堆输入，每个输入乘上一个"重要度"权重，加起来过一道阀门（激活函数），输出一个数。

<svg viewBox="0 0 680 260" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="nu-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="#6b7280"/>
    </marker>
  </defs>
  <text x="340" y="26" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle" fill="#111827">放大看一个神经元：加权 → 求和 → 激活</text>
  <!-- 输入 -->
  <rect x="30" y="60" width="100" height="34" rx="6" fill="#fee2e2" stroke="#dc2626" stroke-width="1.2"/>
  <text x="80" y="82" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#7f1d1d">输入 x₁</text>
  <rect x="30" y="118" width="100" height="34" rx="6" fill="#fee2e2" stroke="#dc2626" stroke-width="1.2"/>
  <text x="80" y="140" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#7f1d1d">输入 x₂</text>
  <rect x="30" y="176" width="100" height="34" rx="6" fill="#fee2e2" stroke="#dc2626" stroke-width="1.2"/>
  <text x="80" y="198" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#7f1d1d">输入 x₃</text>
  <!-- 权重标注 -->
  <text x="180" y="74" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#7c3aed">× w₁</text>
  <text x="180" y="132" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#7c3aed">× w₂</text>
  <text x="180" y="190" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#7c3aed">× w₃</text>
  <!-- 求和 -->
  <circle cx="280" cy="135" r="36" fill="#ede9fe" stroke="#7c3aed" stroke-width="2"/>
  <text x="280" y="132" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#5b21b6">Σ</text>
  <text x="280" y="150" font-family="sans-serif" font-size="9" text-anchor="middle" fill="#5b21b6">加权求和</text>
  <line x1="130" y1="77" x2="248" y2="120" stroke="#7c3aed" stroke-width="1.2" marker-end="url(#nu-arrow)"/>
  <line x1="130" y1="135" x2="244" y2="135" stroke="#7c3aed" stroke-width="1.2" marker-end="url(#nu-arrow)"/>
  <line x1="130" y1="193" x2="248" y2="150" stroke="#7c3aed" stroke-width="1.2" marker-end="url(#nu-arrow)"/>
  <!-- 激活函数 -->
  <rect x="360" y="105" width="120" height="60" rx="8" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="420" y="130" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="#92400e">激活函数</text>
  <text x="420" y="148" font-family="sans-serif" font-size="10" text-anchor="middle" fill="#92400e">(过阀门)</text>
  <line x1="316" y1="135" x2="358" y2="135" stroke="#6b7280" stroke-width="1.2" marker-end="url(#nu-arrow)"/>
  <!-- 输出 -->
  <rect x="540" y="115" width="110" height="40" rx="6" fill="#dcfce7" stroke="#16a34a" stroke-width="1.5"/>
  <text x="595" y="139" font-family="sans-serif" font-size="11" font-weight="bold" text-anchor="middle" fill="#14532d">输出 y</text>
  <line x1="480" y1="135" x2="538" y2="135" stroke="#6b7280" stroke-width="1.2" marker-end="url(#nu-arrow)"/>
  <!-- 公式 -->
  <text x="340" y="232" font-family="sans-serif" font-size="12" text-anchor="middle" fill="#374151">y = f(w₁·x₁ + w₂·x₂ + w₃·x₃ + b)</text>
  <text x="340" y="250" font-family="sans-serif" font-size="10" text-anchor="middle" fill="#6b7280" font-style="italic">w 是权重（重要度），b 是偏置（基础分），f 是激活函数（决定信号过不过）</text>
</svg>

举个具体例子：判断"今天要不要带伞"。

- 输入：x₁ = 天气预报降水概率，x₂ = 当前云层厚度，x₃ = 你今天要不要见客户
- 权重：模型自己学出来——也许 w₁ = 0.7（最重要），w₂ = 0.2，w₃ = 0.1
- 求和过激活函数：得到一个 0~1 之间的数，比如 0.83，超过 0.5 就输出"带伞"

一个神经元就是一个这样的小判官。神经网络就是把成千上万个判官**串起来 + 并起来**。

### 为什么非要"多层"？一层不够吗？

一层判官能解决简单问题：是猫不是猫这种二分类，权重调一调就行。

但"是猫不是猫"背后藏着层层套娃的小问题：

- 这堆像素里有边缘吗？
- 这些边缘组成了眼睛吗？
- 这些眼睛 + 鼻子 + 耳朵的相对位置像猫脸吗？
- 这张猫脸属于波斯猫还是橘猫？

每个小问题都需要一层判官。**多层就是流水线**：每层只回答"上一层是不是某种模式"，然后把答案交给下一层去组合更复杂的模式。

| 层位置 | 学到的特征 | 类比 |
|---|---|---|
| 靠前几层 | 边缘、颜色、明暗 | 流水线第一道：识别"原料长什么样" |
| 中间几层 | 纹理、眼睛、鼻子等部件 | 流水线第二道：把原料拼成"零件" |
| 靠后几层 | 整张脸、整个物体 | 流水线最后一道：把零件组成"成品" |

层越深，模型能表达的"组合模式"越复杂。这就是"深度"的字面意义。

### 模型是怎么"自己学"权重的

前面一直说"权重模型自己学"，怎么学？

简化成三步循环，跟你考试改错本一个套路：

1. **先猜**：用现在的权重对一张图做预测，比如模型说"这是猫，置信度 0.3"。
2. **算错多少**：跟标准答案比，差距叫 **loss**（损失）。标签是"猫=1"，模型猜了 0.3，loss 就比较大。
3. **回去改**：从输出端往输入端，逐层推算"每个权重应该往哪个方向挪一点点才能减小 loss"，然后挪。这一步叫 **反向传播**（backpropagation）。

把训练集里的图跑几十上百遍，每张图都做一次"猜 → 算错 → 改"，权重就会慢慢收敛到一个能让 loss 普遍很小的状态。这时候模型就"学会"了。

听起来像盲人爬山——的确就是。loss 是一个高维空间里的山谷，反向传播告诉模型"脚下哪个方向是下坡"，模型每次挪一小步。挪几百万步后，落到一个比较低的谷底。

### 跟传统 ML 的关系再确认一遍

很多人会问：神经网络不就是一种机器学习算法吗？

对，**深度学习是机器学习的一个子集**。区别只在两点：

1. **特征谁来挑**：传统 ML 靠人，深度学习靠网络自己。
2. **参数有多少**：传统 ML 几十到几千个参数，深度学习上百万到上千亿。

参数多 + 自动学特征 = 能直接吃原始数据（图、声音、文本）+ 能解决以前解决不了的问题。代价是吃数据、吃算力、不可解释。

## 它俩到底怎么选

不是越深越好。深度学习吃数据、吃算力，传统机器学习在很多场景仍然碾压它。

| 维度 | 传统机器学习 | 深度学习 |
|---|---|---|
| 数据量 | 几千到几万条够用 | 通常几十万起步 |
| 算力 | CPU 能跑 | 几乎离不开 GPU |
| 特征工程 | 人工挑特征 | 模型自己学 |
| 可解释性 | 较好（决策树能画出来） | 差（黑盒） |
| 训练时间 | 分钟级 | 小时到天级 |
| 典型场景 | 表格数据、风控、推荐 | 图像、语音、文本、视频 |

一个简单的判断法则：

- 数据是结构化表格、量级在万以下、要可解释 → 传统机器学习够了，别上 DL。
- 数据是图像、音频、自然语言、规模大 → 深度学习起手。

## 大模型是怎么训出来的

ChatGPT、Claude、文心一言这些大模型，本质上仍然是深度学习。新意在三件事：网络结构换成 Transformer、参数堆到几十亿到上千亿、训练范式变成"先预训练，再微调"。

下面这张图把它的生产流水线讲清：

<svg viewBox="0 0 680 320" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="lm-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="#6b7280"/>
    </marker>
  </defs>
  <!-- 阶段 1：预训练 -->
  <rect x="20" y="20" width="160" height="80" rx="8" fill="#fee2e2" stroke="#dc2626" stroke-width="1.5"/>
  <text x="100" y="46" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="#7f1d1d">海量原始语料</text>
  <text x="100" y="66" font-family="sans-serif" font-size="10" text-anchor="middle" fill="#7f1d1d">网页 / 书 / 代码</text>
  <text x="100" y="84" font-family="sans-serif" font-size="10" text-anchor="middle" fill="#7f1d1d">数 TB 起步</text>
  <rect x="220" y="20" width="180" height="80" rx="8" fill="#ede9fe" stroke="#7c3aed" stroke-width="2"/>
  <text x="310" y="46" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="#5b21b6">预训练 Pretrain</text>
  <text x="310" y="66" font-family="sans-serif" font-size="10" text-anchor="middle" fill="#5b21b6">自监督：猜下一个词</text>
  <text x="310" y="84" font-family="sans-serif" font-size="10" text-anchor="middle" fill="#5b21b6">几千张 GPU · 数月</text>
  <rect x="440" y="20" width="180" height="80" rx="8" fill="#dbeafe" stroke="#2563eb" stroke-width="1.5"/>
  <text x="530" y="46" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="#1e3a8a">基础模型 Base Model</text>
  <text x="530" y="66" font-family="sans-serif" font-size="10" text-anchor="middle" fill="#1e3a8a">"什么都懂一点"</text>
  <text x="530" y="84" font-family="sans-serif" font-size="10" text-anchor="middle" fill="#1e3a8a">但不会听话</text>
  <line x1="180" y1="60" x2="218" y2="60" stroke="#6b7280" stroke-width="1.5" marker-end="url(#lm-arrow)"/>
  <line x1="400" y1="60" x2="438" y2="60" stroke="#6b7280" stroke-width="1.5" marker-end="url(#lm-arrow)"/>
  <!-- 中间分隔 -->
  <text x="340" y="135" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#6b7280" font-style="italic">↓ 进入"调教"阶段：把通用能力对齐到具体任务</text>
  <!-- 阶段 2：微调 -->
  <rect x="20" y="160" width="160" height="80" rx="8" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="100" y="186" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="#92400e">指令数据</text>
  <text x="100" y="206" font-family="sans-serif" font-size="10" text-anchor="middle" fill="#92400e">(问题, 标准答案)</text>
  <text x="100" y="224" font-family="sans-serif" font-size="10" text-anchor="middle" fill="#92400e">数千~数十万条</text>
  <rect x="220" y="160" width="180" height="80" rx="8" fill="#ede9fe" stroke="#7c3aed" stroke-width="2"/>
  <text x="310" y="186" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="#5b21b6">微调 Fine-tune</text>
  <text x="310" y="206" font-family="sans-serif" font-size="10" text-anchor="middle" fill="#5b21b6">SFT / LoRA</text>
  <text x="310" y="224" font-family="sans-serif" font-size="10" text-anchor="middle" fill="#5b21b6">几张 GPU · 数小时</text>
  <rect x="440" y="160" width="180" height="80" rx="8" fill="#dcfce7" stroke="#16a34a" stroke-width="1.5"/>
  <text x="530" y="186" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="#14532d">可用模型</text>
  <text x="530" y="206" font-family="sans-serif" font-size="10" text-anchor="middle" fill="#14532d">+RLHF/DPO 做对齐</text>
  <text x="530" y="224" font-family="sans-serif" font-size="10" text-anchor="middle" fill="#14532d">能听话、会拒答</text>
  <line x1="180" y1="200" x2="218" y2="200" stroke="#6b7280" stroke-width="1.5" marker-end="url(#lm-arrow)"/>
  <line x1="400" y1="200" x2="438" y2="200" stroke="#6b7280" stroke-width="1.5" marker-end="url(#lm-arrow)"/>
  <!-- 复用箭头：基础模型 -> 微调 -->
  <path d="M530 100 Q530 130 310 130 Q310 145 310 158" fill="none" stroke="#7c3aed" stroke-width="1.2" stroke-dasharray="4 3" marker-end="url(#lm-arrow)"/>
  <text x="340" y="125" font-family="sans-serif" font-size="9" fill="#7c3aed">复用基础模型权重</text>
  <!-- 底部说明 -->
  <text x="340" y="280" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#374151" font-weight="bold">预训练 = 通才教育，微调 = 岗前培训，对齐 = 职业道德培训</text>
  <text x="340" y="300" font-family="sans-serif" font-size="10" text-anchor="middle" fill="#6b7280">三件事的成本和数据量差几个数量级</text>
</svg>

### 预训练：让模型读完半个互联网

预训练的目标只有一个：让模型学会"接下一个词"。

把数 TB 的网页、书籍、代码喂给一个 Transformer，每次盖住后面一个词让它猜。猜错就调参数。猜对就接着读。如此反复几千亿次。

听起来像复读机。但当训练数据足够多、模型足够大，"猜下一个词"会逼着模型学到语法、事实、推理、甚至一点常识——因为只有真正"懂"了上下文才能猜得准。这就是大家说的"涌现"。

预训练的代价：几千张 H100 跑几个月，烧掉几千万美元。这是只有少数公司玩得起的游戏。

### 微调：让通用模型变成你的专用模型

预训练完出来的"基础模型"什么都懂一点，但不会按你想要的方式回答。比如你问它"翻译这句话"，它可能只是接着把这句话续写下去。

微调就是用少量"问题 + 标准答案"的样本，告诉模型"遇到这种问题应该这样回"。常见三种做法：

| 做法 | 改什么 | 用多少数据 | 适合场景 |
|---|---|---|---|
| **全参微调 SFT** | 改模型全部参数 | 数万~数十万条 | 有预算、要深度定制 |
| **LoRA** | 只训一小撮"补丁"参数 | 几千~几万条 | 个人/小团队，省钱省显存 |
| **Prompt 工程** | 一个字都不改，只改提问方式 | 0 条训练数据 | 不想训练，先试这个 |

给个直观对比：训一个 7B 模型做 LoRA 微调，单张 24GB 显存的消费级显卡 + 几千条领域数据 + 几个小时，就能做出一个还不错的"客服机器人"或"代码助手"。这是大模型时代真正普惠开发者的部分。

### 对齐：让模型不胡说、不冒犯

光会回答还不够，还得回答得"得体"——不编造、不歧视、不教人造炸弹。

这一步叫**对齐**（Alignment），主流方法 RLHF（基于人类反馈的强化学习）和近两年流行的 DPO。一句话原理：让人类对模型的回答打分（好 / 不好），用这些偏好信号再训一轮，模型就会朝"人喜欢的方向"漂移。

对齐做得好的模型，回答会显得"有礼貌、有边界、有判断"。做得糟的，要么过度敏感动不动拒答，要么口无遮拦被人套话。

## 一句话收尾

机器学习是"让电脑从数据里学规律"，深度学习是"用很深的神经网络让电脑自己学特征"，大模型是"把深度学习推到极致后涌现出来的新物种"，微调是"把这个新物种驯化成你想要的样子"。

想动手的话，三个梯度的入门项目：

1. **传统 ML**：用 scikit-learn 跑波士顿房价预测，一晚上。
2. **深度学习**：用 PyTorch 跑 MNIST 手写数字识别，一晚上。
3. **大模型微调**：用 LoRA 在 Llama 3 / Qwen 上微调一个领域助手，一周末。

按顺序走完，从 if-else 到大模型这条线就真的"通"了。

---
title: Agent 的记忆是一团乱麻——两层 Memory 架构的得与失
date: 2026-05-25
tags: [AI, Agent, 工程实践]
summary: 聊聊 LLM 为什么天生没记忆、两层文件式 Memory 的得与失，以及写代码 Agent 该不该有 Memory 的两派之争。
---

## 引子

我跟同一个 AI 助手聊了 30 天。第 31 天，我开了一个新对话，它礼貌地问："你好，请问你是？"

不是它笨，也不是哪里坏了。是"记忆"这件事，在大模型里被设计得很别扭——你以为它在认识你，其实每次对话都从零开始。聊得越多，落差越明显。

Memory 听上去玄，其实是个朴素的产品设计问题：**让对的信息，每次都出现在对的地方**。今天就把它讲透——一种最简单的两层文件方案、围绕"写代码 Agent 该不该有 Memory"的真实争论，以及这套方案能干什么、又漏掉什么。看完你就会发现，所谓"AI 的记忆"，本质上就是一组人手维护的便利贴。

## 为什么 LLM 天生没记忆

先讲清楚一个反直觉的事实：你跟 AI 助手"聊天"，它其实并没有在"听"。

每次你问一句，整个对话历史会被重新打包，连同系统提示一起，一次性喂给模型。模型看完，吐出回复。下一句你再问，它又把"系统提示 + 全部历史 + 你的新问题"重新打包一次，再喂一遍。模型本身是无状态的，没有"上次"这回事——它只在当下这一次推理里活着。

类比一下：你有个同事，患有一种特殊失忆症。每天上班只能读桌上的便利贴，便利贴上没写的，他一概不知道。下班后便利贴清空，明天你必须重新写。哪怕你跟他共事了一年，他对你的认识全靠这张纸。

这就是 LLM 默认的样子。所谓"它记得我"，要么是把历史塞进了便利贴，要么是有人帮它在桌上贴了新条子。所谓 Memory 系统，本质就是在管理那张便利贴。

<svg viewBox="0 0 680 260" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="mem-arrow-1" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>
  <text x="340" y="24" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="500" fill="#222">每轮对话都从零开始</text>
  <g>
    <rect x="40" y="60" width="140" height="50" rx="6" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <text x="110" y="82" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#3C3489">系统提示</text>
    <text x="110" y="100" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3C3489">（角色、规则）</text>
  </g>
  <g>
    <rect x="40" y="125" width="140" height="50" rx="6" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <text x="110" y="147" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#3C3489">历史对话</text>
    <text x="110" y="165" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3C3489">（每轮全量重发）</text>
  </g>
  <g>
    <rect x="40" y="190" width="140" height="50" rx="6" fill="#D85A30" stroke="#993C1D" stroke-width="0.5"/>
    <text x="110" y="220" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#fff">这一轮的新问题</text>
  </g>
  <path d="M185 85 L 305 130" fill="none" stroke="#888" stroke-width="1" marker-end="url(#mem-arrow-1)"/>
  <path d="M185 150 L 305 150" fill="none" stroke="#888" stroke-width="1" marker-end="url(#mem-arrow-1)"/>
  <path d="M185 215 L 305 170" fill="none" stroke="#888" stroke-width="1" marker-end="url(#mem-arrow-1)"/>
  <g>
    <rect x="310" y="115" width="140" height="70" rx="8" fill="#1D9E75" stroke="#0F6E56" stroke-width="0.5"/>
    <text x="380" y="145" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="500" fill="#fff">LLM</text>
    <text x="380" y="165" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#fff">无状态推理</text>
  </g>
  <path d="M455 150 L 575 150" fill="none" stroke="#888" stroke-width="1" marker-end="url(#mem-arrow-1)"/>
  <g>
    <rect x="580" y="125" width="80" height="50" rx="6" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <text x="620" y="155" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#3C3489">回复</text>
  </g>
  <text x="340" y="252" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">便利贴上没写的，模型一概不知道。</text>
</svg>

## 一个朴素方案：两层文件

最简单的方案是两层 markdown 文件，加一个动作。

**第一层叫 daily**，每天一个文件，按 `2026-05-25.md` 命名，append-only。今天聊了什么、做了什么决定、用户提到了什么偏好——一律按时间顺序往下写。流水帐风格，不加工，写错了也不删，下面继续追加修正即可。它的好处是无脑：随时写、随时翻、随时回看"哪一天我提过那个想法"。

**第二层叫 MEMORY**，全局一个 `MEMORY.md`，长期、精炼、按主题组织。记的是从 daily 里反复出现、值得长期保留的事实——用户的沟通偏好、项目约定、被否决过的方案、那些"过 30 天还该记得"的东西。它的好处是稳：每次会话开头读它一遍，Agent 就有了基础人设和上下文。

两层之间有一个动作：**蒸馏**。每隔一段时间——比如 30 天——把过期 daily 翻一遍，把还重要的提炼成 MEMORY 里的条目，剩下的删掉。蒸馏可以手动，也可以让 Agent 自己跑——重点是必须做，否则两层就退化成一层。

为什么不上向量数据库、不接 RAG、不写 SQLite？

- 文件最低成本，用户随手可读、可改、可删。
- 调试就是 `cat`、`grep`、`vim`，不需要客户端、不需要服务。
- 出了问题直接掀开看："哪天开始记错的？"——这种透明度是数据库给不了的。

复杂方案不是不行，只是它解决的不是同一个问题。两层文件解决的是"让 Agent 记住一点点对的东西"，不是"做一个企业级知识库"。能用文件解决的，就别上服务。

<svg viewBox="0 0 680 320" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="mem-arrow-2" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>
  <text x="340" y="26" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="500" fill="#222">两层文件式 Memory</text>
  <text x="170" y="55" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#666">第一层：daily（流水帐）</text>
  <text x="510" y="55" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#666">第二层：MEMORY（精炼）</text>
  <line x1="340" y1="70" x2="340" y2="290" stroke="#ddd" stroke-width="0.5" stroke-dasharray="2 4"/>
  <g>
    <rect x="60" y="80" width="220" height="32" rx="4" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <text x="170" y="100" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3C3489">2026-05-23.md  · 流水帐</text>
  </g>
  <g>
    <rect x="60" y="120" width="220" height="32" rx="4" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <text x="170" y="140" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3C3489">2026-05-24.md  · 流水帐</text>
  </g>
  <g>
    <rect x="60" y="160" width="220" height="32" rx="4" fill="#D85A30" stroke="#993C1D" stroke-width="0.5"/>
    <text x="170" y="180" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#fff">2026-05-25.md  · 今日</text>
  </g>
  <g>
    <rect x="60" y="200" width="220" height="32" rx="4" fill="#F7C1C1" stroke="#A32D2D" stroke-width="0.5" stroke-dasharray="2 2"/>
    <text x="170" y="220" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#A32D2D">…30 天前的旧文件</text>
  </g>
  <text x="170" y="252" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#888">append-only · 不加工</text>
  <g>
    <rect x="400" y="120" width="220" height="120" rx="6" fill="#1D9E75" stroke="#0F6E56" stroke-width="0.5"/>
    <text x="510" y="145" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#fff">MEMORY.md</text>
    <text x="416" y="170" font-family="sans-serif" font-size="11" fill="#fff">- 用户偏好：中文短段落</text>
    <text x="416" y="188" font-family="sans-serif" font-size="11" fill="#fff">- 项目约定：DB-001 禁 tinyint</text>
    <text x="416" y="206" font-family="sans-serif" font-size="11" fill="#fff">- 否决方案：v4 不再用 status</text>
    <text x="416" y="224" font-family="sans-serif" font-size="11" fill="#fff">- 工作习惯：用「继续」推进</text>
  </g>
  <text x="510" y="262" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#888">curated · 按主题</text>
  <path d="M285 220 Q 350 245 400 200" fill="none" stroke="#534AB7" stroke-width="1.2" marker-end="url(#mem-arrow-2)"/>
  <text x="345" y="265" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#534AB7">30 天蒸馏 · 归并 · 删旧</text>
  <text x="340" y="305" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">文件最低成本 · 用户可读可改</text>
</svg>

## 写代码 Agent 该不该有 Memory：两派之争

把这套方案搬到"陪你写代码的 Agent"上，分歧立刻出现。这是当下 AI 编程社区里一个真实的拉锯——两边都有道理，吵得不可开交。

**支持派**说：当然要记，写代码场景的连续性比闲聊还重要。

- 项目约定每次重讲，烦。命名风格、提交格式、code review 的偏好，每次冷启动都要重新建立一次。
- 上次定下的技术决策，下次它又问一遍。"我们到底用 Gin 还是 Echo"——已经定过的事不该被重新讨论。
- 用户的沟通风格、踩过的坑、被否决过的思路，每次冷启动都要重新建立。失去这层上下文，Agent 就只是"今天来面试的那个人"。

**反对派**说：写代码场景下，Memory 不仅没用，反而是个累赘。

- 代码仓库本身就是最权威的记忆。README、CHANGELOG、`go.mod`、git log、目录结构——这些信息都在代码里，比 Memory 文件更新更准。
- Memory 必然过时。去年记下的"我们用 Gin"，今年可能已经换成 Echo——而 Memory 不会自己更新，它只会在某个节点开始误导 Agent。
- 跨项目污染。A 项目的内部约定写进 Memory，跑 B 项目时被错误套用。Memory 越通用越危险。
- 检索成本。Memory 一多，每次会话开头都得读一堆，反而稀释了真正的上下文窗口——本来用来读代码的 token，被旧笔记占走了。

<svg viewBox="0 0 680 340" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
  <text x="340" y="26" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="500" fill="#222">写代码 Agent 该不该有 Memory</text>
  <text x="170" y="56" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#3C3489">支持派</text>
  <text x="170" y="74" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">真相在 Memory 文件</text>
  <text x="510" y="56" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="500" fill="#A32D2D">反对派</text>
  <text x="510" y="74" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">真相在代码仓库</text>
  <line x1="340" y1="90" x2="340" y2="305" stroke="#ddd" stroke-width="0.5" stroke-dasharray="2 4"/>
  <g>
    <rect x="40" y="100" width="260" height="40" rx="6" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <text x="170" y="124" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3C3489">跨会话连续性，不必重讲</text>
  </g>
  <g>
    <rect x="40" y="148" width="260" height="40" rx="6" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <text x="170" y="172" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3C3489">用户偏好、沟通风格可复用</text>
  </g>
  <g>
    <rect x="40" y="196" width="260" height="40" rx="6" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <text x="170" y="220" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3C3489">减少冷启动重复提问</text>
  </g>
  <g>
    <rect x="380" y="100" width="260" height="40" rx="6" fill="#F7C1C1" stroke="#A32D2D" stroke-width="0.5"/>
    <text x="510" y="124" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#A32D2D">仓库即真相，README 比 Memory 准</text>
  </g>
  <g>
    <rect x="380" y="148" width="260" height="40" rx="6" fill="#F7C1C1" stroke="#A32D2D" stroke-width="0.5"/>
    <text x="510" y="172" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#A32D2D">Memory 必然过时，反而误导</text>
  </g>
  <g>
    <rect x="380" y="196" width="260" height="40" rx="6" fill="#F7C1C1" stroke="#A32D2D" stroke-width="0.5"/>
    <text x="510" y="220" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#A32D2D">跨项目污染，A 项目约定误用到 B</text>
  </g>
  <g>
    <rect x="380" y="244" width="260" height="40" rx="6" fill="#F7C1C1" stroke="#A32D2D" stroke-width="0.5"/>
    <text x="510" y="268" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#A32D2D">检索成本：稀释真正的上下文窗口</text>
  </g>
  <g>
    <circle cx="340" cy="320" r="9" fill="#1D9E75"/>
    <text x="340" y="324" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="500" fill="#fff">中</text>
  </g>
  <text x="340" y="304" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#0F6E56">中间派：Memory 应该极薄</text>
</svg>

我倾向中间派：**写代码 Agent 的 Memory 应该极薄**。只记代码里读不出来的东西，剩下的回仓库现读。

| 该不该记 | 内容 | 理由 |
|---|---|---|
| ✅ 该记 | 用户沟通偏好（中文/英文、长短、风格） | 仓库读不出来 |
| ✅ 该记 | 被否决过的方案 | 仓库只留下了被采纳的，决策路径会丢 |
| ✅ 该记 | 跨项目的工作习惯 | 单仓库视角看不见 |
| ❌ 不记 | 技术栈、依赖版本 | `go.mod` / `package.json` 一查就有 |
| ❌ 不记 | 目录结构、命名约定 | `tree` 一下、grep 一下就有 |
| ❌ 不记 | 业务逻辑细节 | 代码本身就是最准的描述 |

判断标准就一句话：**这件事，从代码里读得出来吗？读得出来，就别记**。

## 它解决了什么、又漏掉了什么

回到两层文件本身。它能干这些：

- 跨会话连续性 ✅ 不用每次自我介绍
- 用户偏好 ✅ 知道你爱用中文短段落
- 项目级约定（轻量的那种）✅ 记得"这个项目不用 tinyint"
- 让 Agent 不显得失忆 ✅ 起码不会上来就问"请问你是？"

但有几个绕不过去的坎：

- **检索仍是 grep 级**。文件大了之后，全文加载就是浪费上下文窗口。grep 命中的也未必是当前最相关的那一条。
- **没有时间衰减**。半年前记下的"用户喜欢用 Bun"，今年用户已经换回 Node，Memory 不会自己更新。除非有人主动覆盖，旧条目可以一直生效。
- **容量有上限**。单个 MEMORY.md 超过几千行，模型读完就没空间干正事了。这是上下文窗口的硬约束，不是文案问题。
- **蒸馏要靠人**。daily 不及时归并到 MEMORY，Agent 就开始"复读两个月前的事"。蒸馏漏了，整套系统就开始漂移。

最后这个坑我自己踩过。daily 文件堆了快两个月没整理，结果某天 Agent 在新对话里反复提一个早就 deprecated 的方案——它读到的是旧 daily，没读到 MEMORY 里更新后的结论。后来我加了一个简单规则：daily 超过 30 天就强制蒸馏一次，问题才稳定下来。Memory 系统的可靠性，最终是由维护者的勤快程度决定的。

<svg viewBox="0 0 680 280" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="mem-arrow-4" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>
  <text x="340" y="24" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="500" fill="#222">蒸馏跟不上时，Memory 开始漂移</text>
  <line x1="60" y1="200" x2="640" y2="200" stroke="#888" stroke-width="1" marker-end="url(#mem-arrow-4)"/>
  <text x="650" y="205" font-family="sans-serif" font-size="11" fill="#666">时间</text>
  <g>
    <rect x="80" y="170" width="20" height="20" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <rect x="120" y="170" width="20" height="20" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <rect x="160" y="170" width="20" height="20" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <rect x="200" y="170" width="20" height="20" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <rect x="240" y="170" width="20" height="20" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <rect x="280" y="170" width="20" height="20" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <rect x="320" y="170" width="20" height="20" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <rect x="360" y="170" width="20" height="20" fill="#CECBF6" stroke="#534AB7" stroke-width="0.5"/>
    <rect x="400" y="170" width="20" height="20" fill="#F7C1C1" stroke="#A32D2D" stroke-width="0.5" stroke-dasharray="2 2"/>
    <rect x="440" y="170" width="20" height="20" fill="#F7C1C1" stroke="#A32D2D" stroke-width="0.5" stroke-dasharray="2 2"/>
    <rect x="480" y="170" width="20" height="20" fill="#F7C1C1" stroke="#A32D2D" stroke-width="0.5" stroke-dasharray="2 2"/>
    <rect x="520" y="170" width="20" height="20" fill="#F7C1C1" stroke="#A32D2D" stroke-width="0.5" stroke-dasharray="2 2"/>
    <rect x="560" y="170" width="20" height="20" fill="#F7C1C1" stroke="#A32D2D" stroke-width="0.5" stroke-dasharray="2 2"/>
  </g>
  <text x="180" y="225" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#3C3489">daily 文件越堆越多</text>
  <text x="500" y="225" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#A32D2D">早该归并到 MEMORY 的</text>
  <g>
    <rect x="80" y="80" width="200" height="40" rx="6" fill="#1D9E75" stroke="#0F6E56" stroke-width="0.5"/>
    <text x="180" y="104" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#fff">MEMORY.md（最新结论）</text>
  </g>
  <g>
    <rect x="380" y="80" width="200" height="40" rx="6" fill="#F7C1C1" stroke="#A32D2D" stroke-width="0.5" stroke-dasharray="2 2"/>
    <text x="480" y="104" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#A32D2D">MEMORY.md（已落后）</text>
  </g>
  <path d="M180 122 L 180 168" fill="none" stroke="#0F6E56" stroke-width="1" marker-end="url(#mem-arrow-4)"/>
  <path d="M480 122 L 480 168" fill="none" stroke="#A32D2D" stroke-width="1" stroke-dasharray="3 3" marker-end="url(#mem-arrow-4)"/>
  <text x="340" y="260" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#666">Agent 开始复读两个月前的旧方案，因为它读到的还是旧 daily。</text>
</svg>

## 一句话收尾

Memory 不是数据库问题，是产品决策问题。**什么值得记**，比**怎么记**重要得多。任何能用文件解决的事，都没必要先上服务。

对写代码的 Agent 尤其如此：少即是多。代码已经把绝大多数事实摆在那里了，Memory 只需要兜住代码兜不住的那一小块——剩下的事，让 Agent 自己回仓库去读。这是一份对长期维护者更友好的契约：人少操心，机器多干活。

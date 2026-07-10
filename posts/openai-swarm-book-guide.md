---
title: OpenAI Swarm 中文精读：入门 + 进阶两本电子书全收录
date: 2026-07-10
tags: [AI, Agent, OpenAI, Swarm]
summary: OpenAI Swarm 开源源码两本中文电子书上线——入门版逐行精读，进阶版讲设计哲学、实战与改造，附阅读路径。
---

OpenAI 在 2024 年底开源了 Swarm——一个不到 500 行的 Agent 框架。它不是生产级 SDK，定位是教学：用最少的代码讲清 Agent、function calling、handoff、上下文变量这些核心概念怎么拼到一起。

源码虽小，设计取舍却很精妙：无状态引擎、约定优于配置的参数注入、靠返回值实现交接。但中文资料里几乎没人逐行拆过它。这两本电子书就是来填这个空白的。

## 一本入门，一本进阶

两本书一条阅读路径，都已上线博客：

- **[入门版《Swarm 精读》](https://wendellzone.github.io/swarm-book/)**：零基础友好，逐行精读源码 + 手绘 SVG 图解，11 章。
- **[进阶版《Swarm 深度解析》](https://wendellzone.github.io/swarm-book-deep/)**：承接入门版，讲设计哲学、真实项目实战、动手改造，13 章。

入门版讲清"是什么、怎么写"，进阶版接着讲"为什么这么设计、真实项目里怎么用、你能怎么改"。读完入门版第 10 章末尾会自然引向进阶版。

<svg viewBox="0 0 680 300" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg"><rect x="0" y="0" width="680" height="300" fill="#FBF7F0" rx="8"/><text x="340" y="28" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="700" fill="#3A2A14">两本书的阅读路径</text><rect x="20" y="48" width="280" height="232" fill="#FFF3E0" stroke="#E0913A" stroke-width="1.5" rx="6"/><text x="160" y="70" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="700" fill="#8A4E12">入门版《Swarm 精读》</text><text x="160" y="86" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#8A4E12">零基础 · 11 章 · 逐行精读</text><rect x="36" y="100" width="248" height="44" fill="#FFE0B2" rx="4"/><text x="160" y="118" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="600" fill="#5D3A0E">概念搭建 01–06</text><text x="160" y="134" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7A4F1A">Agent · 工具 · 上下文 · handoff</text><rect x="36" y="152" width="248" height="44" fill="#FFCC80" rx="4"/><text x="160" y="170" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="600" fill="#5D3A0E">引擎核心 07–09</text><text x="160" y="186" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7A4F1A">run 主循环 · 流式 · 交互循环</text><rect x="36" y="204" width="248" height="44" fill="#FFB74D" rx="4"/><text x="160" y="222" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="600" fill="#5D3A0E">全景收束 10</text><text x="160" y="238" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7A4F1A">架构复盘 + 延伸方向</text><rect x="380" y="48" width="280" height="232" fill="#F3E8DA" stroke="#8A4E12" stroke-width="1.5" rx="6"/><text x="520" y="70" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="700" fill="#5D3A0E">进阶版《Swarm 深度解析》</text><text x="520" y="86" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#5D3A0E">有基础 · 13 章 · 哲学+实战+改造</text><rect x="396" y="100" width="248" height="44" fill="#E6D2B8" rx="4"/><text x="520" y="118" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="600" fill="#3A2A14">设计哲学与权衡 00–06</text><text x="520" y="134" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#5D3A0E">无状态 · deepcopy · handoff · 对比</text><rect x="396" y="152" width="248" height="44" fill="#D4B896" rx="4"/><text x="520" y="170" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="600" fill="#3A2A14">进阶实战 07–10</text><text x="520" y="186" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#5D3A0E">分诊 · 数据库 · RAG · 评测</text><rect x="396" y="204" width="248" height="44" fill="#C09B6A" rx="4"/><text x="520" y="222" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="600" fill="#3A2A14">动手改造 11–12</text><text x="520" y="238" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#3A2A14">加中间件 · 换模型 · mini-Swarm</text><defs><marker id="rp-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 Z" fill="#8A4E12"/></marker></defs><line x1="306" y1="164" x2="374" y2="164" stroke="#8A4E12" stroke-width="2" marker-end="url(#rp-arrow)"/><text x="340" y="156" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#8A4E12">读完后</text></svg>

## 入门版：从零到看懂 run 主循环

入门版自底向上搭积木，后一章依赖前一章的概念。11 章分三段：

- **概念搭建（01–06）**：从 LLM / function calling / Agent 三个词讲清，到 `types.py` 的三个核心结构，再到上下文变量和 handoff。
- **引擎核心（07–09）**：`core.py` 的 `run` 五步主循环是全书最重要的一章，接着是流式输出和交互式终端。
- **全景收束（10）**：把所有拼图拼成一张架构图，并指向进阶版。

关键判断在第 07 章。Swarm 把"LLM 调用 → 工具执行 → 结果回灌 → 再调用"压成一个循环，几百行代码讲清了所有 Agent 框架的骨架。读懂这一章，再看 LangGraph、OpenAI Agents SDK 会发现底层都是同一个模式的不同工程化。

## 进阶版：从读懂到能改造

进阶版分三部分，相对独立：

**第一部分·设计哲学与权衡（00–06）** 回答"为什么这么设计"。

| 主题 | 核心问题 |
|---|---|
| 无状态设计 | 引擎为何什么都不记，状态放哪、谁维护 |
| 深拷贝边界 | `run()` 开头为何 deepcopy，不这么做会弄坏谁的数据 |
| 约定优于配置 | context_variables 靠参数名注入的取舍 |
| handoff 极简 | 交接 = 返回一个 Agent，对比显式路由表方案 |
| 主循环健壮性 | `max_turns`、工具找不到、串行 vs 并行 |
| 与生产框架对比 | Swarm vs OpenAI Agents SDK / LangGraph 的定位 |

**第二部分·进阶实战（07–10）** 给真实项目的落地参考：airline 三层分诊编排、SQLite 持久化（防注入/事务/幂等）、向量检索 RAG、用 `execute_tools=False` 取意图做评测。

**第三部分·动手改造（11–12）** 把 Swarm 当脚手架：加日志和重试中间件、接非 OpenAI 模型、亲手实现一个 mini-Swarm 的 `run` 循环。

## 怎么读最省力

入门版建议按顺序读，概念是层层递进的。进阶版第一、三部分顺读，第二部分（实战四章）相对独立，可挑感兴趣的先看。

几条实用技巧：

- 每章代码可直接复制运行，先跑再读逻辑，比纯看快。
- 卡壳时先看 SVG 图解，抽象机制都配了图。
- 章节页按 `←` / `→` 方向键翻章，手机点左上角展开导航。
- 实战篇涉及外部依赖（数据库 / 向量库 / API Key）会明确标注，只读逻辑无需安装。

如果你已经在用 LangGraph 或 OpenAI Agents SDK，可以直接从进阶版第一部分的对比章切入，再按需回补入门版。

---

这两本书的价值不在教你用一个教学框架，而在用最小的代码量讲清 Agent 的底层骨架。读懂 Swarm，其他框架都是同一套模式的工程化变体。

## 参考文献

| # | 来源 | 标题 / 用途 |
|---|---|---|
| 1 | [OpenAI Swarm](https://github.com/openai/swarm) | 开源仓库，两本书的精读对象 |
| 2 | [《Swarm 精读》](https://wendellzone.github.io/swarm-book/) | 入门版电子书线上地址 |
| 3 | [《Swarm 深度解析》](https://wendellzone.github.io/swarm-book-deep/) | 进阶版电子书线上地址 |

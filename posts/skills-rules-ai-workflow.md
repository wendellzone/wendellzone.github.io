---
title: 基于 Skills + Rules 构建 AI Agent 自动化工作流
date: 2026-05-11
tags: [AI Agent, 工程化, 工作流]
summary: 从零理解 Skills 与 Rules 两种机制、为什么要拆分，以及怎么用它们落地编码、运维、数据三类工作流。重点讲清 Skill 怎么写才会被触发、怎么迭代才不会过拟合。
---

> 编码只是 Skill 的应用之一，甚至不是最重要的。**Skill 真正的杀伤力在运维、SRE、数据处理这类"重流程、轻代码"的工作上**。本文先从概念讲到落地，再展开三类工作流案例。

## 1. 为什么需要 Skills 与 Rules

直接把所有要求堆进一句 Prompt，迟早会遇到三个问题：

| 痛点 | 表象 | 根因 |
|------|------|------|
| 上下文爆炸 | 越用越慢、token 飙升 | 所有规则、示例、工具说明常驻 |
| 行为漂移 | 同样的事每次结果不一样 | 没有稳定的"团队公约" |
| 经验流失 | 解决过的问题下次又踩坑 | 工作流没沉淀 |

Rules 与 Skills 是把 Agent 从"一次性聊天"变成"工程系统"的两块基石：

- **Rules**：始终生效的全局约束（写代码必须 Go 1.21、提交前必须跑测试）
- **Skills**：按需触发的专项能力包（写 PR 描述、压测分析、生成报告）

类似"公司制度 + 岗位 SOP"。

## 2. 区别一表清

| 维度 | Rules | Skills |
|------|-------|--------|
| 加载时机 | 每轮常驻 | 命中触发词时按需加载 |
| 上下文成本 | 长期占用 | 仅在使用时占用 |
| 内容形态 | 偏约束/原则，短小 | 偏工作流/SOP，可附脚本 |
| 典型粒度 | 1–10 行/条 | 50–500 行/个 |
| 适用场景 | 编码风格、安全红线、回复语气 | 部署、压测、报表生成、PR 流程 |

判断口诀：

1. 是否每轮都要起作用？是 → Rule
2. 是否包含多步流程或脚本？是 → Skill
3. 是否需要附文件资产（模板、脚本）？是 → Skill

## 3. 第一性原理：上下文经济学

LLM 的上下文是稀缺资源：

```
有效推理空间 ≈ 总窗口 − 系统提示词 − 历史 − 常驻规则 − 工具描述
```

如果把"可能用到"的东西全塞进系统提示词，剩下给推理的空间被严重挤压。Skills 的核心价值是**延迟加载**——默认上下文里只有"标题 + 一行描述"（约 50 token），命中后才把完整内容塞进来。

工程化经验：**先全部当 Rule 写 → 发现冲突或膨胀 → 把不常用的拆成 Skill**。

## 4. Rules 详解

### 4.1 写好 Rules 的四条原则

**1) 写约束，不写教程**

```markdown
❌  当你写 Go 代码时，首先要考虑可读性，其次性能，然后遵循官方风格指南……

✅  - Go 代码必须通过 gofmt 与 golangci-lint
    - 错误必须用 fmt.Errorf("...: %w", err) 包装
    - 不允许 panic（main 包初始化除外）
```

**2) 一条一行，可被检查**——每条都要"能被测试"，否则就是废话。

**3) 用否定式划红线**——绝对禁止的事项写明，不留模糊空间。

```
- NEVER 直接 rm -rf 用户目录
- NEVER 在未读取文件的情况下使用 Edit
- NEVER 编造 API 字段
```

**4) 分层组织**——按主题拆，单文件 < 200 行。

```
.cursor/rules/
├── coding-style.mdc
├── git-workflow.mdc
├── safety.mdc
└── reply-style.mdc
```

### 4.2 反模式速查

| 反模式 | 危害 |
|--------|------|
| 把示例代码塞进 Rules | 上下文膨胀 |
| 一条 Rule 同时管 5 件事 | 模糊难维护 |
| 用"尽量""最好""推荐"等软词 | Agent 选择性忽略 |
| 与 Skill 内容重复 | 维护双份、容易冲突 |

## 5. Skills 详解（按 Anthropic skill-creator 实践）

### 5.1 设计哲学：先想清楚四个问题

写第一行 Skill 之前，先回答：

1. 这个 Skill 要让 Agent 能做什么？
2. 什么时候应该触发？（用户实际会说的话）
3. 期望的输出格式是什么？
4. 能不能定义"成功"？（能则配测试用例）

核心观点：**Skill 是给"成千上万次未来调用"准备的资产，不是为了一次满足当前对话**。

### 5.2 标准结构

```
skill-name/
├── SKILL.md                # 必需：唯一入口
└── 可选资源
    ├── scripts/            # 可执行脚本：不进上下文
    ├── references/         # 详细文档：用到才 Read
    └── assets/             # 输出素材：模板、图标
```

三类资源的本质区别：

| 目录 | 加载方式 | 用途 |
|------|---------|------|
| `scripts/` | Bash 调用，不进上下文 | 重复、可脚本化的逻辑 |
| `references/` | Agent 主动 Read 才加载 | 长篇查阅资料 |
| `assets/` | 作为输出引用 | 模板、图标、样式 |

经验法则：SKILL.md 里写"如果 X 则做这一长串……" → 拆到 references；多次重复同一逻辑 → 抽成 script。

### 5.3 渐进式信息披露

Skill 信息分三层：

```
Level 1：Metadata（name + description）  始终在上下文（约 100 词）
Level 2：SKILL.md 主体                   触发后加载（建议 < 500 行）
Level 3：bundled resources               按需 Read 或 Bash
```

多变体场景按 variant 拆 references：

```
cloud-deploy/
├── SKILL.md           # 主流程 + 平台选择逻辑
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

Agent 永远只读一个变体，上下文成本最优。

### 5.4 description：决定 Skill 命运的一行字

`description` 是 Agent 唯一用来判断"该不该加载这个 Skill"的依据。

**反直觉但重要**：Claude 倾向于"漏触发"——明明该用却不用。所以 description 要稍微"主动一点"：

```markdown
❌  description: 一个把内部数据做成 dashboard 的工具。

✅  description: 构建轻量的内部数据 dashboard。当用户提到 dashboard、
   数据可视化、内部指标，或想展示任何形式的公司数据时都使用本 Skill，
   即使没有明确说出 "dashboard" 这个词。
```

**用真实用户原话，不要抽象描述**：

```markdown
❌  description: 处理 Excel 文件加列。

✅  description: 读取 .xlsx 并新增计算列、修复格式、生成图表。触发场景：
   "老板发了个叫 'Q4 sales final FINAL v2.xlsx' 的文件，让我加一列利润率"、
   "帮我把这份报表里的金额按千分位格式化"。
```

写完三问自检：

1. 不熟悉这个 Skill 的人能猜到"什么时候该用"吗？
2. 至少 5 种不同表述都能命中吗？
3. 与最相似的另一个 Skill 比，分得清边界吗？

### 5.5 写作风格：解释 why，不堆 MUST

```markdown
❌  ALWAYS use sync.Pool for any struct allocated more than 100 times per second.
   NEVER allocate inside hot loops. MUST run pprof before optimizing.

✅  高频分配（每秒 >100 次）的结构体值得用 sync.Pool 复用——因为 GC 扫描
   成本与对象数线性相关。但优化前一定先跑 pprof：人对热点的直觉经常错，
   没数据就改往往优化的不是真正的瓶颈，反而引入复杂度。
```

后者让模型在边缘场景能自己推断。**写 ALWAYS/NEVER 全大写是黄信号**——除非真红线，否则改成有理由的描述。

### 5.6 评测驱动迭代

Skill 不是写完就交付，要像产品一样迭代：

1. 写完后准备 2–3 个真实用户会说的测试 prompt
2. 跑两次：with-skill vs baseline（裸跑）。**如果加不加 Skill 输出差不多，说明这个 Skill 没存在的必要**
3. 三类信号一起看：定性输出 + 定量断言通过率 + tokens/耗时
4. 迭代心法：
   - 从反馈中泛化，别过拟合到具体测试用例
   - 删掉不出力的内容，prompt 保持精瘦
   - 看到几个测试用例都重复做同一件事 → 抽成脚本

### 5.7 完整示例：性能分析 Skill

```markdown
---
name: perf-analysis
description: 分析 Go 服务的 pprof 性能数据，定位 CPU/内存热点并产出优化
建议。触发场景：用户提供 .pprof 文件；说"分析下性能"、"看下哪里慢"、
"内存涨"、"CPU 高"。即使没明说 "pprof"，只要涉及 Go 服务性能定位也使
用本 Skill。不处理 trace 数据（trace-analysis Skill 负责）。
---

# 性能分析 Skill

## 为什么这样做
性能问题最常见的失误是"凭直觉改"，但热点占比、GC 停顿、syscall 占比这些
数据，肉眼几乎不可能猜准。本 Skill 的核心是"先量化、再分类、最后给方案"。

## 主流程
1. 用 `scripts/pprof_top.sh <file>` 输出 Top 10 热点
2. 读 `references/hotspot-rules.md`，按特征匹配 → 根因假设 → 建议
3. 用 `assets/report-template.md` 生成报告（含证据链 + 预期收益）

## 输出示例
Input: cpu.pprof（订单服务，P99 1.2s）
Output:
- encoding/json.Unmarshal 18.3% → 切 sonic，预期 P99 -15%
- runtime.mallocgc 15.7% → NewOrderResp 用 sync.Pool，预期 GC -30%

## 边界
- 只产出建议，不替用户改代码
- 不处理超过 500MB 的 profile
```

体现的原则：description 主动 + 真实场景 + 边界、解释 why、scripts/references/assets 三层、Input/Output 示例。

## 6. 何时用 Skill、何时不用

按"流程化程度 × 频次"划分：

```
高频
 │  [应该做成 Skill]            [必须做成 Skill]
 │  · 写 PR / commit            · 告警分诊
 │  · 周报                       · 部署 / 回滚
 │  · 单测生成                   · 故障复盘
 │
 │  [写 Rule 即可]              [按需做 Skill]
 │  · 编码风格                   · 季度规划
 │  · 回复语气                   · 安全审计
 │  · 文件命名                   · 大版本发版
 │
 └────────────────────────────── 流程化程度 →
        弱                          强
```

规则：

- 高频 + 强流程 → 必做 Skill（运维变更、告警处置）
- 高频 + 弱流程 → 写 Rule（编码风格）
- 低频 + 强流程 → 做 Skill（季度发版）
- 低频 + 弱流程 → 临时聊天解决，别过度工程化

## 7. 实战案例 A：研发工作流（编码场景）

目标：接一句"给订单服务加查询接口" → 自动完成需求拆解 → 编码 → 单测 → 自审 → 提交 PR。

**Rules 兜底**（节选）：

```markdown
# Go
- 错误用 fmt.Errorf("...: %w", err) 包装
- 公共方法必须有 godoc
- 新增代码单测覆盖 ≥ 70%
- 禁止 panic（main 初始化除外）

# Git
- 分支命名：feat/* fix/* chore/*
- Commit 用 conventional commits
- 提交前必须 go test ./... + golangci-lint
- NEVER 直接 push main
```

**Skills 接力**（5 个）：

| Skill | 触发 | 做什么 |
|-------|------|--------|
| feature-spec | "加个 X 接口" | 拆需求：接口定义、影响文件、风险点、测试用例 |
| feature-impl | "按方案实现" | 按 spec 改文件，运行 gofmt |
| unit-test | "补单测" | 表驱动测试，自动重试 ≤3 轮 |
| self-review | "自审一下" | 按风格/错误处理/并发/性能/安全五维度过 diff |
| commit-pr | "提交 / 出 PR" | 前置检查、conventional commits、gh pr create |

跑一次完整流程，用户只输 3–4 句话，Skill 接力执行。

**收益**：把所有要求塞进 system prompt 约 12K token；拆成 Rules + Skills 后，命中的 Skill 才加载，单次任务总 token 下降约 60%。

## 8. 实战案例 B：运维 / SRE 工作流（更典型）

编码场景里 Skill 是加速器，运维场景里 Skill 几乎是必需品——因为运维流程本身就是"步骤固定、参数变化、容错严格"的 SOP。

| 编码 vs 运维 | 编码 | 运维 |
|-------------|------|------|
| 错一步代价 | 编译报错（可逆） | 影响线上（不可逆） |
| 是否有固定 SOP | 部分 | **几乎全部** |
| 是否要审计 | 一般 | **必须留痕** |
| 是否跨多系统 | 单仓库 | **监控/日志/CMDB/CI/容器平台** |

### 8.1 Rules 先打底

```markdown
# 运维安全红线
- 任何线上操作前先 dry-run 或在预发执行一次
- 操作必须留痕：操作人、时间、命令、影响范围、回滚方式
- 跨可用区操作分批，单批 ≤ 30%

- NEVER 跳过审批 kubectl delete / drop / truncate
- NEVER 直接改生产配置中心，必须走灰度
- NEVER 把生产 DB 密码写进任何文件或日志
```

### 8.2 四个 Skill 串起一次告警处置

凌晨 P0 告警 → 用户把告警原文丢给 Agent：

```
1. alert-triage （告警分诊）
   - 拉 Grafana 大盘 + 错误日志 + Top 5 慢 trace
   - 按 references/triage-matrix.md 决策矩阵给：严重度 + 根因假设 + 推荐动作
   - 写值班记录 .ops/incidents/<date>-<service>.md

2. ops-action（变更执行）
   - 强制 dry-run、强制等用户 confirm、分批执行 ≤30%、每批 60s 观察、恶化自动停

3. log-dig（日志深挖）
   - 按 stack trace 顶部三行做指纹聚类
   - 输出 Top 10 错误类型 + 首次出现时间 + 是否吻合发布

4. postmortem（复盘）
   - 读值班记录 → 时间线 + 5 Why + 改进项（必须可验证）
```

**示例分诊矩阵**（references/triage-matrix.md 节选）：

| 现象 | 推断根因 | 推荐动作 |
|------|---------|---------|
| 延迟涨 + 错误率平 | 下游慢 / GC | 看下游 + pprof |
| 延迟涨 + 错误率涨 | 依赖故障 | 熔断 + 联系下游 |
| 延迟涨 + 流量涨 | 容量不足 | 扩容 |
| 错误率突增 + 流量平 | 代码 bug | 回滚最近发布 |

整条链路下来，值班人员只输入 3 句话，剩下都是 Skill 在按 SOP 执行。

### 8.3 运维 Skill 的设计要点

1. **强制 dry-run**：写进工作流，不依赖用户记得
2. **审计留痕**：每个 Skill 末尾固定写一份 Markdown 记录
3. **分批 + 观察**：步骤里写死，不靠 Agent 自己判断
4. **拒绝模糊动作**：所有动作都要有"目标值"，不能是"调一调"

## 9. 实战案例 C：数据与报告工作流

数据/报表场景的特点是"输入是模糊需求，输出是结构化文档"。Skill 在这里把"需求 → SQL → 数据 → 图 → 文字结论"这条链固化下来。

典型 Skill：

- **weekly-report**：拉指标、做同环比、画图、写文字解读，按模板填空
- **adhoc-data**：回答"X 指标为什么变化"——拆维度、算贡献度、给假设

**关键设计原则**：Skill 给"假设 + 证据"，结论留给人——避免 AI 编数据。每个数字都要附 SQL 或源 CSV 路径，方便人工 spot check。

## 10. 一份非编码 Skill 灵感清单

| 角色 | 高价值 Skill |
|------|-------------|
| 后端 / SRE | 告警分诊、变更执行、容量评估、故障复盘、值班交接 |
| 数据 | 指标拆解、周报、A/B 报告、漏斗分析、数据校验 |
| 产品 / 运营 | 竞品扫描、活动复盘、用户反馈聚类、PRD 自检 |
| 个人效率 | 邮件分类、会议纪要结构化、待办批量管理 |
| 团队管理 | OKR 同步、1on1 提纲、招聘简历筛选 |

只要满足"步骤固定 + 输入输出明确 + 跨多系统"，就值得做成 Skill。

## 11. 常见陷阱

| 陷阱 | 表象 | 解法 |
|------|------|------|
| Rule 与 Skill 内容重复 | 双份维护、冲突 | Rule 只放约束，流程进 Skill |
| description 写成文档简介 | 触发率低 | 改成"何时触发"格式 + 主动一点 |
| Skill 里塞了大量代码示例 | 上下文膨胀 | 移到 references/ |
| 一个 Skill 干 5 件事 | 命中不准 | 拆成多个，文档串联 |
| Rules 写成作文 | Agent 选择性忽略 | bullet + 否定式 |

## 12. 一句话总结

> **Rules 立规矩，Skills 教手艺。**
> 规矩越精炼越好，手艺越具体越值钱。
> "每次都要做的事"写成 Rule，"特定场景才做的事"写成 Skill。
> 一条工作流 = 一组 Rules 兜底 + 多个 Skills 接力。

## 附录：模板速查

**Rule 模板**：

```markdown
---
description: <这条 Rule 管什么>
globs: ["**/*.go"]
alwaysApply: true
---

## 必须
- ...

## 禁止
- NEVER ...

## 例外（可选）
- 当 X 时可以 Y
```

**Skill 模板**：

```markdown
---
name: <skill-name>
description: <做什么>。触发场景：<场景 1，含真实用户原话>；<场景 2>。
即使用户没明说 "<关键词>"，只要涉及 <能力领域> 也使用本 Skill。
不处理 <边界 1>（由 <other-skill> 负责）。
---

## 为什么这样做
<1-3 句解释设计动机>

## 主流程
1. <步骤 1，引用 scripts/xxx.sh>
2. <步骤 2，指向 references/xxx.md>

## 输出格式
<完整模板或 Input/Output 示例>

## 边界
- 不做 X（属于 <other-skill>）
```

**评测自检**——写完 description 后想 5 条 should-trigger + 5 条 should-not-trigger，两边各 ≥ 80% 才算合格：

```json
[
  {"query": "出下本周的业务周报", "should_trigger": true},
  {"query": "周一开会要的材料还没准备", "should_trigger": true},
  {"query": "ad-hoc 问个数据：GMV 跌了多少", "should_trigger": false}
]
```

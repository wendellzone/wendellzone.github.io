---
title: 基于 Skills + Rules 构建 AI Agent 自动化工作流
date: 2026-05-11
tags: [AI Agent, 工程化, 工作流]
summary: 从零理解 Skills 与 Rules 两种机制，用上下文经济学解释为何要拆分；给出编码、运维/SRE、数据报告三个完整工作流案例，并按 Anthropic skill-creator 的最佳实践讲透 description 写法、渐进式信息披露与评测驱动迭代。
---


> 面向工程师的实战教程：从零理解 Skills 与 Rules 两种机制，到组合搭建覆盖编码、运维、数据、文档的自动化工作流。
>
> **重要观点**：编码只是 Skill 的应用场景之一，甚至不是最重要的。**Skill 的真正杀伤力在运维、SRE、数据处理、报告产出、跨系统协作这类"重流程、轻代码"的工作上**。本教程会先讲编码案例（容易理解），再展开非编码案例（更具实战价值）。

---

## 目录

1. [背景：为什么需要 Skills 与 Rules](#1-背景为什么需要-skills-与-rules)
2. [核心概念辨析](#2-核心概念辨析)
3. [第一性原理：Agent 的上下文经济学](#3-第一性原理agent-的上下文经济学)
4. [Rules 详解：常驻的"团队公约"](#4-rules-详解常驻的团队公约)
5. [Skills 详解：按需加载的"专家手册"](#5-skills-详解按需加载的专家手册)
6. [组合模式：Rules × Skills 的四种搭配](#6-组合模式rules--skills-的四种搭配)
7. [实战案例 A：研发工作流（编码场景）](#7-实战案例-a研发工作流编码场景)
8. [实战案例 B：运维/SRE 工作流（更典型的 Skill 场景）](#8-实战案例-b运维sre-工作流更典型的-skill-场景)
9. [实战案例 C：数据与报告工作流](#9-实战案例-c数据与报告工作流)
10. [何时用 Skill、何时不用——场景分类法](#10-何时用-skill何时不用场景分类法)
11. [调试与迭代](#11-调试与迭代)
12. [常见陷阱与排查清单](#12-常见陷阱与排查清单)
13. [附录：模板速查](#13-附录模板速查)

---

## 1. 背景：为什么需要 Skills 与 Rules

直接把所有要求都堆在一句 Prompt 里，会出现三类问题：

| 痛点 | 表象 | 根因 |
|------|------|------|
| 上下文爆炸 | 越用越慢、token 飙升 | 所有规则、示例、工具说明常驻 |
| 行为漂移 | 同样的事每次结果不一样 | 没有稳定的"团队公约" |
| 经验流失 | 解决过的问题下次又踩坑 | 工作流没有沉淀为可复用资产 |

Skills 与 Rules 是把 Agent 从"一次性聊天"变成"工程系统"的两块基石：

- **Rules**：**始终生效**的全局约束（写代码必须 Go 1.21、提交前必须跑测试……）。
- **Skills**：**按需触发**的专项能力包（写 PR 描述、压测分析、生成 PlantUML……）。

二者的关系类似于"公司制度 + 岗位 SOP"。

---

## 2. 核心概念辨析

### 2.1 一张表看懂区别

| 维度 | Rules | Skills |
|------|-------|--------|
| 加载时机 | 每轮对话常驻 | 命中触发词时按需加载 |
| 上下文成本 | 长期占用 | 仅在使用时占用 |
| 内容形态 | 偏"约束/原则"，短小精炼 | 偏"工作流/SOP"，可附脚本与素材 |
| 典型粒度 | 单条 1–10 行 | 单技能 50–500 行 |
| 触发方式 | 隐式（系统自动注入） | 显式（描述匹配 / 命令调用） |
| 适用场景 | 编码风格、安全红线、回复语气 | 部署、压测、报表生成、PR 流程 |

### 2.2 一个直观的比喻

> **Rules** 是"宪法"——任何场景都不能违反。
> **Skills** 是"应急预案手册"——着火时翻第三章，断电时翻第七章。

### 2.3 何时该写 Rule、何时该写 Skill

判断原则：

1. **是否每轮都要起作用？** 是 → Rule；否 → Skill。
2. **是否包含多步流程或脚本？** 是 → Skill；否 → Rule。
3. **是否需要带文件资产（模板、参考图、脚本）？** 是 → Skill。
4. **是否会干扰其它任务？** 是 → 拆为 Skill 按需加载。

---

## 3. 第一性原理：Agent 的上下文经济学

理解 Skills/Rules 的设计动机，必须先理解 LLM 的上下文是稀缺资源。

### 3.1 上下文成本公式

每轮对话的有效信息量 ≈ `总窗口 − 系统提示词 − 历史消息 − 常驻规则 − 工具描述`。

如果把所有"潜在可能用到的知识"都写进系统提示词：

```
总窗口 200K
├─ 系统提示词        80K   ← 越写越胖
├─ 工具说明          20K
├─ 当前任务上下文    20K
├─ 历史对话          50K
└─ 留给推理的空间    30K   ← 被严重挤压
```

### 3.2 Skills 的核心价值：延迟加载

把"可能用到"的内容沉淀为 Skill，仅在描述命中时才把内容塞进上下文：

```
默认状态：上下文里只有 Skill 的"标题 + 一行描述"（约 50 token）
触发后：  完整内容（数百 token 到数千 token）才加载进来
```

这是 Skills 相较于"塞进系统提示词"的**根本优势**。

### 3.3 直觉理解

- Rules 像内存中的全局变量：随时可读，但占内存。
- Skills 像懒加载模块：用到才 import，不用零成本。

工程化经验：**先全部当 Rule 写 → 发现冲突或膨胀 → 把不常用的拆成 Skill**。

---

## 4. Rules 详解：常驻的"团队公约"

### 4.1 Rules 的物理形态

不同 Agent 平台的载体不同，本质都是"在每轮对话开头自动拼接的一段文本"：

- WorkBuddy：`SOUL.md` / `IDENTITY.md` / `USER.md` / `MEMORY.md`
- Cursor：`.cursor/rules/*.mdc`
- Claude Code：`CLAUDE.md`
- 通用 LLM：System Prompt

### 4.2 写好 Rules 的四个原则

**1) 写"约束"而不是"教程"**

❌ 反例（像教程，太啰嗦）：
```
当你写 Go 代码时，首先要考虑代码的可读性，其次要考虑性能，
然后要遵循 Go 的官方风格指南，包括但不限于 gofmt 格式化……
```

✅ 正例（约束式，可执行）：
```
- Go 代码必须通过 gofmt 与 golangci-lint
- 错误必须用 fmt.Errorf("...: %w", err) 包装
- 不允许 panic，除非在 main 包初始化阶段
```

**2) 一条一行、可被检查**

每条规则都要"能被测试"，否则就是废话。

```
- 函数体超过 80 行必须拆分                 ← 可数
- 公共方法必须有 godoc 注释                 ← 可检
- 写代码用中文回复，写注释用英文              ← 可看
```

**3) 用否定式划红线**

绝对禁止的事项要写明，不要给 Agent 模糊空间。

```
- NEVER 直接 rm -rf 用户目录
- NEVER 在未读取文件的情况下使用 Edit
- NEVER 编造 API 字段，未确认时查文档或问用户
```

**4) 分层组织**

按主题拆分，避免一个 Rules 文件超过 200 行。

```
.cursor/rules/
├── coding-style.mdc      # 代码风格
├── git-workflow.mdc      # 提交规范
├── safety.mdc            # 安全红线
└── reply-style.mdc       # 回复语气
```

### 4.3 一个真实的 Rules 示例

`.cursor/rules/backend-go.mdc`：

```markdown
---
description: 后端 Go 项目编码规范
globs: ["**/*.go"]
alwaysApply: true
---

# Go 编码约束

## 风格
- 必须通过 `gofmt` 与 `golangci-lint run`
- import 分三组：标准库 / 第三方 / 本项目
- 禁止使用 `interface{}`，统一用 `any`

## 错误处理
- 错误必须用 `fmt.Errorf("xxx: %w", err)` 包装
- 不允许 `_ = err` 静默忽略；必须 log 或返回
- 不允许在非 main 包 panic

## 并发
- goroutine 必须有退出机制（context 或 done channel）
- 跨 goroutine 共享变量必须用 sync 或 channel 保护

## 测试
- 新增公共函数必须配套 _test.go
- 表驱动测试用 `tests := []struct{ name string; ... }` 模式
```

### 4.4 Rules 反模式

| 反模式 | 危害 |
|--------|------|
| 把示例代码塞进 Rules | 上下文膨胀、模型记不住 |
| 一条 Rule 同时管 5 件事 | 模糊、难维护 |
| 用"尽量""最好""推荐"等软词 | Agent 选择性忽略 |
| 与 Skill 内容重复 | 维护双份、容易冲突 |

---

## 5. Skills 详解：按需加载的"专家手册"

> 本章的设计哲学参考了 Anthropic 官方 [skill-creator](https://github.com/anthropics/skills) 的实践，把"怎么写 Skill"上升到"怎么迭代一个真正能用的 Skill"。

### 5.1 设计哲学：先想清楚四个问题

写第一行 Skill 之前，先回答：

1. **这个 Skill 要让 Agent 能做什么？** ——一句话说清能力边界。
2. **什么时候应该触发？** ——列出真实用户会说的话（不是抽象描述）。
3. **期望的输出格式是什么？** ——文件、Markdown、PR 链接、命令执行结果……
4. **能不能定义"成功"？** ——可不可以写出"做对了 vs 做错了"的判定标准？能则建议配测试用例（见 5.7）。

skill-creator 的核心观点是：**Skill 是给"成千上万次未来调用"准备的资产，不是为了一次满足当前对话**。所以从一开始就要按"可复用产品"的标准设计。

### 5.2 Skill 的标准结构（Anatomy）

```
skill-name/
├── SKILL.md                      # 必需：唯一入口
│   ├── YAML frontmatter (name, description)
│   └── Markdown 主体（< 500 行为佳）
└── 可选资源（按需加载）
    ├── scripts/                  # 可执行脚本：确定性、重复性任务
    ├── references/               # 详细文档：用到才 Read
    └── assets/                   # 输出用素材：模板、图标、字体
```

**三类资源的本质区别**：

| 目录 | 加载方式 | 用途 | 何时该用 |
|------|---------|------|---------|
| `scripts/` | Bash 调用执行，**不加载到上下文** | 重复的、可脚本化的逻辑 | 拉指标、生成 changelog、跑 lint、调用 API |
| `references/` | Agent 主动 Read 才加载 | 长篇查阅资料 | 字段对照表、错误码、模板、决策矩阵 |
| `assets/` | 作为输出的一部分被引用 | 模板/图标/样式 | PR 模板、报告模板、品牌素材 |

**经验法则**：看到自己在 SKILL.md 里写"如果 X 则做这一长串……" → 拆到 references；看到几次调用都重复做同一件事 → 拆成 script。

### 5.3 渐进式信息披露（Progressive Disclosure）

skill-creator 把 Skill 的信息分成三个加载层级：

```
Level 1：Metadata（name + description）
  ├─ 始终在上下文（≈ 100 词）
  └─ Agent 据此决定"要不要加载这个 Skill"

Level 2：SKILL.md 主体
  ├─ Skill 触发时才加载（建议 < 500 行）
  └─ 包含主流程、决策点、对其它资源的引用

Level 3：bundled resources（references/scripts/assets）
  ├─ Agent 按需 Read 或 Bash 才进上下文
  └─ 体积不限，但要明确"什么时候去看"
```

**关键设计原则**：

- SKILL.md **超过 500 行就要拆**——加一层目录结构，并在主文件里明确指引"X 场景去看 references/x.md"
- `references/` 的大文件（>300 行）开头要写目录，方便 Agent 快速跳读
- **多变体场景按 variant 拆 references**：
  ```
  cloud-deploy/
  ├── SKILL.md                    # 主流程 + 平台选择逻辑
  └── references/
      ├── aws.md                  # 用到 AWS 才加载
      ├── gcp.md                  # 用到 GCP 才加载
      └── azure.md                # 用到 Azure 才加载
  ```
  这样 Agent 永远只读一个平台的细节，上下文成本最优。

### 5.4 description：决定 Skill 命运的一行字

`description` 是 Agent 唯一用来判断"该不该加载这个 Skill"的依据。**写不好 description，再好的 Skill 也召不出来**。

#### 5.4.1 必须包含两类信息

1. **做什么**：能力描述
2. **何时触发**：用户实际可能说的话、文件特征、上下文信号

可选第三项：与相邻 Skill 的边界（"不处理 X，X 由 Y Skill 负责"）。

#### 5.4.2 反直觉但重要：description 要"主动一点"

skill-creator 的原作团队观察到：**Claude 倾向于"漏触发"——明明该用 Skill 的场景却没用**。所以 description 要写得稍微"推"一点：

❌ 太被动：
```
description: 一个把内部数据做成 dashboard 的工具。
```

✅ 主动一点：
```
description: 构建轻量、快速的内部数据 dashboard。当用户提到 dashboard、
数据可视化、内部指标，或想展示任何形式的公司数据时都使用本 Skill，
即使他们没有明确说出 "dashboard" 这个词。
```

#### 5.4.3 用真实用户话术，不要抽象描述

❌ 干巴巴：
```
description: 处理 Excel 文件加列。
```

✅ 贴近真实输入：
```
description: 读取 .xlsx 并按用户描述新增计算列、修复格式、生成图表。
触发场景示例：
"老板发了个叫 'Q4 sales final FINAL v2.xlsx' 的文件，让我加一列利润率"、
"帮我把这份报表里的金额按千分位格式化"、
"从下载文件夹找到那个销售表，加一个环比列"。
```

后者的好处是：用户真实输入会包含"老板""下载文件夹""利润率"这些上下文，描述里出现这些词，触发率会显著提高。

#### 5.4.4 写完 description 自检三问

1. 把 description 给一个不熟悉这个 Skill 的人看，他能猜到"什么时候该用"吗？
2. 至少 5 种不同表述都能命中吗？（正式的、口语的、缩写的）
3. 与最相似的另一个 Skill 比，分得清边界吗？

### 5.5 写作风格：解释"为什么"，不要堆 MUST

skill-creator 反复强调的写作原则：

> **Today's LLMs are smart. 与其堆 MUST/NEVER 把模型当机器人指挥，不如解释"为什么这件事重要"，让它理解后自己做对。**

**对比示例**：

❌ 命令式（脆弱）：
```
ALWAYS use sync.Pool for any struct allocated more than 100 times per second.
NEVER allocate inside hot loops. MUST run pprof before optimizing.
```

✅ 解释式（健壮）：
```
高频分配（每秒 >100 次）的结构体值得用 sync.Pool 复用——因为 GC 扫描成本
与对象数线性相关，复用能同时降低 mallocgc 与 GC 标记开销。

但优化前一定先跑 pprof：人对热点的直觉经常错，没数据就改往往优化的不是
真正的瓶颈，反而引入复杂度。
```

后者让模型在面对"高频但不到 100 次/秒"或"非热路径但分配大对象"这类边缘场景时，能自己推断出正确做法。

**写作风格清单**：

- 用祈使句（imperative）："Run X before Y"，不要"You should run X"
- 全大写的 ALWAYS/NEVER 是黄信号——除非是真红线，否则改成有理由的描述
- 复杂规则给"为什么"——例：`use Edit not Write because Write overwrites context the user might still need`
- 给反例和例外条件，不要假装规则没有边界

### 5.6 输出格式与示例：让 Agent 知道"长成什么样"

skill-creator 推荐两种格式化技巧：

**1) 给一个完整模板**
```markdown
## Report structure
ALWAYS use this exact template:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

**2) Input/Output 对照示例**
```markdown
## Commit message format
**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication

**Example 2:**
Input: Fixed null pointer in order export
Output: fix(order): handle nil pointer in export
```

**经验**：1-2 个高质量示例 > 一段抽象描述。但例子也别太多——3 个之后边际收益骤降。

### 5.7 评测驱动迭代（Eval-driven Iteration）

这是 skill-creator 最值钱的部分：**Skill 不是写完就交付，而是要像产品一样迭代**。

#### 5.7.1 写完 Skill 后准备 2-3 个测试用例

测试用例 = 真实用户会说的一段话。例：

```json
{
  "skill_name": "weekly-report",
  "evals": [
    {
      "id": 1,
      "prompt": "出一下这周的业务周报，重点看下 GMV 跌的原因",
      "expected_output": "Markdown 周报，含同比/环比表格、异常指标解读、Top 3 贡献维度"
    },
    {
      "id": 2,
      "prompt": "周一汇报材料还没写，照例帮我搞一份",
      "expected_output": "同上，且 prompt 没有明示'周报'也要触发"
    }
  ]
}
```

#### 5.7.2 跑 With-skill vs Baseline 对照

每个用例跑两次：一次加载 Skill，一次不加载（裸跑）。**对比的是 Skill 的边际价值**。如果加不加 Skill 输出差不多，说明这个 Skill 没存在的必要。

#### 5.7.3 三类信号要一起看

| 信号 | 来源 | 看什么 |
|------|------|--------|
| 定性 | 人工 review 输出 | 哪条不对、哪步多余、哪步缺了 |
| 定量 | 断言（assertions）通过率 | 是否稳定满足"必要条件" |
| 成本 | tokens / 耗时 | Skill 是不是把流程拖慢、上下文打爆 |

**好的 assertion 要"客观可验证 + 名字自解释"**：
- ✅ `output_contains_table_with_columns_GMV_DAU`
- ✅ `output_file_extension_is_xlsx`
- ❌ `output_quality_is_good`（主观）
- ❌ `assertion_1`（看不出在测什么）

主观的 Skill（写作风格、设计感）就不要硬上断言，靠人工评审更合适。

#### 5.7.4 迭代时的四条心法

skill-creator 总结的迭代经验，非常关键：

1. **从反馈中泛化，别过拟合到测试用例**。
   测试用例只有几个，但 Skill 是给上百次未来调用用的。如果某条反馈让你忍不住加一条特别具体的 MUST，先停一下：是不是有更通用的写法？

2. **删掉不出力的内容，让 prompt 保持精瘦**。
   读 transcripts（不只是输出），看 Skill 的哪些部分在让 Agent 浪费时间，砍掉它们重测一次。

3. **解释 why，胜过命令 what**（同 5.5）。

4. **看到重复劳动就抽脚本**。
   如果三个测试用例下 Agent 都独立写了类似的 helper 脚本，那就把这个脚本写一次放进 `scripts/`，Skill 引用即可。能省下大量未来的 token 与时间。

#### 5.7.5 什么时候停止迭代

- 用户说够了
- 反馈基本为空
- 改进不再带来提升

### 5.8 一个完整的 Skill 示例：压测分析

把上面所有原则落到一个例子里。

`~/.workbuddy/skills/perf-analysis/SKILL.md`：

```markdown
---
name: perf-analysis
description: 分析 Go 服务的 pprof 性能数据，定位 CPU/内存热点并产出优化建议。
触发场景：用户提供 .pprof 文件；说"分析下性能"、"看下哪里慢"、"内存涨"、
"CPU 高"；或粘贴 go tool pprof 的输出。即使没有明说"pprof"，只要涉及
Go 服务性能定位也使用本 Skill，因为多数情况下下一步就是要看 pprof。
不处理 trace 数据（trace-analysis Skill 负责）。
---

# 性能分析 Skill

## 输入
- CPU profile：`*.cpu.pprof`
- Memory profile：`*.mem.pprof`
- 或一个目录：自动扫描里面的 pprof 文件

## 为什么这样做
性能问题最常见的失误是"凭直觉改"，但 mallocgc 的占比、GC 停顿时间、
syscall 占比这些数据，肉眼几乎不可能猜准。所以本 Skill 的核心是
"先量化、再分类、最后给方案"，避免在错的地方优化。

## 主流程

### 第一步：识别 profile 类型并出 Top 10
用 `scripts/pprof_top.sh <file>` 一次性输出类型与累积占比 Top 10。

### 第二步：按热点特征分类
读 `references/hotspot-rules.md`，按表格匹配热点特征 → 根因假设 → 建议。

### 第三步：产出报告
用 `assets/report-template.md` 生成报告：
- 热点函数 Top 10（含占比、文件位置）
- 根因假设（每条带证据）
- 可验证的优化方案（含预期收益与回滚方式）

## 输出示例
**Input**: cpu.pprof（订单服务，P99 延迟 1.2s）
**Output**:
```
# 性能分析报告：order-service
## 热点 Top 10
1. encoding/json.Unmarshal  18.3%  internal/api/handler.go:42
2. runtime.mallocgc          15.7%  ...
...
## 根因假设
- JSON 解析占 18%（>8% 阈值）→ 切 sonic 库可降到 ~5%
- mallocgc 占 15.7%（>15% 阈值）→ Top 调用方为 NewOrderResp，建议 sync.Pool
## 优化方案
1. 切 sonic：1 行替换，预期 P99 下降 15%，回滚成本低
2. NewOrderResp 用 sync.Pool：需测试 reset 逻辑，预期 GC 停顿 -30%
```

## 边界
- 只产出建议，不替用户改代码（用户审过后再实施）
- 不处理超过 500MB 的 profile（建议先用 -trim 缩小）
```

配套的 `references/hotspot-rules.md`（按需加载）：

```markdown
# 热点分类规则表

| 函数特征 | 占比阈值 | 根因假设 | 建议 |
|---------|---------|---------|------|
| runtime.mallocgc | >15% | 高频小对象分配 | sync.Pool 或预分配 |
| runtime.gcBgMarkWorker | >10% | GC 压力大 | 减少指针、降低对象数 |
| encoding/json.Unmarshal | >8% | JSON 瓶颈 | 切 sonic / easyjson |
| syscall.read/write | >30% | I/O 密集 | 批处理、缓冲、异步 |
| sync.(*Mutex).Lock | >5% | 锁竞争 | 拆锁 / sync.Map / RWMutex |
```

`scripts/pprof_top.sh`：

```bash
#!/bin/bash
# 输出 profile 类型 + 累积占比 Top 10
# Usage: pprof_top.sh <profile-file>
set -euo pipefail
file="$1"
echo "=== Profile type ==="
go tool pprof -text "$file" 2>&1 | head -3
echo "=== Top 10 (cumulative) ==="
go tool pprof -top -cum "$file" 2>&1 | head -25
```

**这个例子体现了哪些原则**：

- description 主动一点（"即使没明说 pprof 也用"）+ 真实触发场景 + 与相邻 Skill 的边界
- "为什么这样做"段落解释设计动机，而不是堆 MUST
- 重复逻辑抽到 `scripts/`，决策表抽到 `references/`，模板抽到 `assets/`
- 给了 Input/Output 示例
- 边界明确（不改代码、不处理超大文件）

---



## 6. 组合模式：Rules × Skills 的四种搭配

### 模式 A：Rules 兜底 + Skills 处理边缘

最常见的搭配。

```
Rules: 编码规范、安全红线、回复语气   ← 永远生效
Skills: 数据库迁移、压测、生成报表    ← 按需触发
```

### 模式 B：Skills 调用过程中复用 Rules

Skill 内部不重复写 Rules，依赖 Rules 已经生效。

例：`release-pr` Skill 不需要再写"用 fmt.Errorf 包装错误"，因为 backend-go Rule 已经管了。

### 模式 C：Skills 之间的协作

通过命名约定让 Skill A 在文档里建议加载 Skill B：

```markdown
## 后续步骤
完成代码生成后，建议触发 `code-review` Skill 进行审查。
```

### 模式 D：Rules 控制 Skills 的触发边界

Rules 里明确"什么场景下不要加载某些 Skill"：

```
- 在 hotfix 分支上，禁止使用 release-pr Skill
- 当用户在 Plan 模式下，禁止 Skills 直接执行写操作
```

---

## 7. 实战案例 A：研发工作流（编码场景）

目标：让 Agent 接到一句"我要给订单服务加个查询接口"后，自动完成：
**需求拆解 → 编码 → 单测 → 自审 → 提交 PR**。

### 7.1 总体架构

```
┌──────────────────────────────────────┐
│ Rules（常驻）                        │
│  - backend-go.mdc：编码风格           │
│  - git-workflow.mdc：分支与提交规范    │
│  - safety.mdc：禁止直接 push main     │
└──────────────────────────────────────┘
            ↓ 任何任务都生效
┌──────────────────────────────────────┐
│ Skills（按需）                       │
│  ┌──────────────┐  ┌──────────────┐ │
│  │ feature-spec │→ │ feature-impl │ │
│  └──────────────┘  └──────────────┘ │
│         ↓                  ↓        │
│  ┌──────────────┐  ┌──────────────┐ │
│  │ unit-test    │  │ self-review  │ │
│  └──────────────┘  └──────────────┘ │
│                            ↓        │
│                    ┌──────────────┐ │
│                    │ commit-pr    │ │
│                    └──────────────┘ │
└──────────────────────────────────────┘
```

### 7.2 第一步：写 Rules（5–10 分钟）

`~/.workbuddy/rules/backend-go.md`（节选）：

```markdown
# Go 项目通用约束

- 用 Go 1.21+，模块路径以公司 prefix 开头
- 错误用 fmt.Errorf("...: %w", err) 包装
- 公共函数必须有 godoc
- 单测覆盖率新增代码 >= 70%
- 禁止 panic（main 初始化除外）
- 禁止 interface{}，用 any
```

`~/.workbuddy/rules/git-workflow.md`：

```markdown
# Git 工作流

- 分支命名：feat/* / fix/* / chore/*
- Commit message 用 conventional commits：feat(order): ...
- 提交前必须本地跑通：go test ./... 与 golangci-lint
- NEVER 直接 push main / master
- PR 描述用项目模板（见 .github/PULL_REQUEST_TEMPLATE.md）
```

### 7.3 第二步：写 5 个 Skill

#### 7.3.1 feature-spec：需求拆解

```markdown
---
name: feature-spec
description: 把一句模糊的功能需求拆成可执行的技术方案。当用户说"我要加一个 X 功能"、"实现 X 接口"、"做个 X 能力"时触发。
allowed_tools: Read, Write
---

# 需求拆解 Skill

## 输入示例
"给订单服务加个按用户 ID 查询订单列表的接口"

## 输出格式
1. **接口定义**：method、path、入参、出参（含字段类型）
2. **影响范围**：要改动的文件清单（逐文件给路径）
3. **数据库**：是否新增索引/字段
4. **风险点**：最多 3 条
5. **测试用例**：至少 3 条（正常 / 边界 / 异常）

## 工作流
1. Read 项目根目录的 README 与 docs/architecture.md
2. Grep 找到相关模块（如 internal/order/）
3. 输出技术方案 Markdown，写到 .agent/specs/<feature>.md
4. 等待用户确认后再触发 feature-impl
```

#### 7.3.2 feature-impl：编码实现

```markdown
---
name: feature-impl
description: 根据 .agent/specs/ 下的技术方案，逐文件实现代码。当用户说"按方案实现"、"开始写代码"时触发，需先有 feature-spec 产出的方案文件。
allowed_tools: Read, Write, Edit, Bash
---

# 编码实现 Skill

## 前置条件
- 必须存在 .agent/specs/<feature>.md
- 当前分支为 feat/* （否则提示用户切分支）

## 工作流
1. Read 方案文件
2. 按"影响范围"的文件清单，逐个 Read 现有代码
3. 用 Edit 而非 Write 修改已有文件，保持风格一致
4. 每改一个文件，run `gofmt -w` 与 `goimports`
5. 完成后输出 diff 摘要

## 边界
- 不写单测（交给 unit-test Skill）
- 不提交 git（交给 commit-pr Skill）
```

#### 7.3.3 unit-test：单测生成

```markdown
---
name: unit-test
description: 为指定的 Go 文件或函数生成表驱动单测。当用户说"补单测"、"加测试"、"测一下 X 函数"时触发。
allowed_tools: Read, Write, Bash
---

# 单测生成 Skill

## 输出风格
表驱动测试：
```go
func TestXxx(t *testing.T) {
    tests := []struct {
        name    string
        input   ...
        want    ...
        wantErr bool
    }{
        {"normal", ..., ..., false},
        {"empty input", ..., ..., true},
        {"boundary", ..., ..., false},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := Xxx(tt.input)
            ...
        })
    }
}
```

## 工作流
1. Read 目标函数与依赖
2. 识别外部依赖（DB、HTTP）→ 用 testify/mock 或接口替身
3. 至少覆盖：正常路径、空输入、错误路径、边界值
4. Write *_test.go
5. Bash run `go test ./<pkg>/... -run TestXxx -v` 验证
6. 失败时自动修最多 3 轮，超过则报告给用户
```

#### 7.3.4 self-review：自审

```markdown
---
name: self-review
description: 对当前 git diff 做代码审查，找出风格、错误处理、并发、性能、安全五类问题。当用户说"自审一下"、"review 我的改动"时触发。
allowed_tools: Bash, Read
---

# 自审 Skill

## 工作流
1. Bash `git diff --staged` 或 `git diff main...HEAD`
2. 按以下维度过一遍：
   - 风格：是否符合 backend-go Rule
   - 错误处理：err 是否都被 wrap、log 或返回
   - 并发：goroutine 是否可被取消、是否有竞态
   - 性能：循环里是否有不必要的分配
   - 安全：SQL 拼接、未校验的输入
3. 输出问题清单，按严重度分级（P0/P1/P2）
4. 不直接修改代码，只给修改建议
```

#### 7.3.5 commit-pr：提交 + PR

```markdown
---
name: commit-pr
description: 提交代码并创建 PR。当用户说"提交"、"出 PR"、"推上去"时触发。
allowed_tools: Bash, Read, Write
---

# 提交与 PR Skill

## 前置检查（任一失败则阻断）
- [ ] 当前分支不是 main / master
- [ ] `go test ./...` 通过
- [ ] `golangci-lint run` 通过
- [ ] 已通过 self-review

## 工作流
1. 按 conventional commits 生成 commit message：
   - 标题：`feat(order): add list orders by user`
   - body：包含变更摘要、影响范围、测试方式
2. `git add -p` 让用户确认（重要，不要无脑 add .）
3. `git commit`
4. `git push origin <current-branch>`
5. 用 `gh pr create` 创建 PR，描述使用 .github/PULL_REQUEST_TEMPLATE.md
6. 输出 PR 链接

## 红线
- NEVER force push
- NEVER 跳过 pre-commit hook
```

### 7.4 第三步：跑一次完整流程

用户输入：
> "给订单服务加个按用户 ID 查询订单的接口"

Agent 的内部流程（伪代码）：

```python
# 系统加载 Rules（常驻）
load_rules([backend_go, git_workflow, safety])

# 用户消息触发 feature-spec Skill
trigger("feature-spec")
spec = generate_spec(user_input)
write(".agent/specs/list_orders_by_user.md", spec)
ask_user("方案如下，确认开始实现？")

# 用户确认 → 触发 feature-impl
trigger("feature-impl")
ensure_branch_starts_with("feat/")
for file in spec.files:
    edit_or_create(file)
run("gofmt -w .")

# 自动衔接 unit-test
trigger("unit-test")
for new_func in changed_funcs:
    write_test(new_func)
run("go test ./...")  # 失败重试 ≤3 次

# 自动衔接 self-review
trigger("self-review")
issues = review(git_diff())
if issues.has_p0(): ask_user("发现 P0 问题，要修吗？")

# 用户说"提交" → 触发 commit-pr
trigger("commit-pr")
preflight_checks()
git_add_p()
git_commit("feat(order): add list orders by user")
gh_pr_create()
```

### 7.5 第四步：观察 token 消耗对比

| 方案 | 系统提示词 token | 单次任务总 token |
|------|----------------|----------------|
| 全塞进 system prompt | ~12K | ~25K |
| Rules + Skills 拆分 | ~2K | ~9K（仅命中的 Skill 加载） |

**节省约 60% 上下文**，且 Agent 行为更稳定。

---

## 8. 实战案例 B：运维/SRE 工作流（更典型的 Skill 场景）

> 编码场景里 Skill 是"加速器"，运维场景里 Skill 几乎是"必需品"——因为运维流程本身就是一堆"步骤固定、参数变化、容错严格"的 SOP，天然契合 Skill 的形态。

### 8.1 为什么运维更适合 Skill

| 编码 vs 运维 | 编码 | 运维 |
|-------------|------|------|
| 工作单元 | 文件/函数 | 命令/接口/操作 |
| 错一步的代价 | 编译报错（可逆） | 影响线上（不可逆） |
| 是否有固定 SOP | 部分有 | **几乎全部都有** |
| 是否需要审计 | 一般 | **必须留痕** |
| 是否跨多个系统 | 通常单仓库 | **跨监控/日志/CMDB/CI/容器平台** |

运维任务的本质是「**按 SOP 串联多个系统的命令/API**」，这正是 Skill 的强项：把流程、参数、容错都写进去，让 Agent 替人按表操课。

### 8.2 场景画像：一条线上告警的处置流程

凌晨告警"order-service P99 延迟超阈值"。值班人员的操作链条通常是：

```
看告警详情 → 看 Grafana 大盘 → 拉日志看错误 → 看 trace 看慢点
        → 判断根因 → 决定动作（限流/扩容/回滚）
        → 执行 → 写值班记录 → 同步群通知
```

这条链上的每一步都可以做成 Skill。

### 8.3 SRE 工作流：5 个 Skill 串联

#### 8.3.1 Rules 先打底

`~/.workbuddy/rules/ops-safety.md`：

```markdown
# 运维安全红线

## 必须
- 任何线上操作前，先 dry-run 或在预发执行一次
- 操作必须留痕：操作人、时间、命令、影响范围、回滚方式
- 跨可用区操作必须分批，单批不超过 30%

## 禁止
- NEVER 在没有审批记录时执行 kubectl delete / drop / truncate
- NEVER 直接改生产配置中心，必须走灰度
- NEVER 把生产数据库账号密码写进任何文件或日志
- NEVER 跳过告警静默，告警是给所有人看的
```

这一类 Rules 是"夜里两点也能救命"的硬约束。

#### 8.3.2 Skill：alert-triage（告警分诊）

```markdown
---
name: alert-triage
description: 接收一条告警，自动拉取相关大盘、日志、trace，给出"严重度评估 + 根因假设 + 推荐动作"。当用户粘贴告警内容、说"看下这个告警"、"刚收到 P0"时触发。
allowed_tools: Bash, WebFetch, Read, Write
---

# 告警分诊 Skill

## 输入
告警原文（含 service、metric、threshold、time）

## 工作流
1. 解析告警结构，提取 service / metric / 时间窗
2. 调用 `scripts/grab_grafana.sh <service> <metric> <window>` 拉指标截图与数值
3. 调用 `scripts/grab_logs.sh <service> <window>` 抓最近错误日志（按 level=ERROR 过滤）
4. 调用 `scripts/grab_traces.sh <service> <window>` 抓最慢的 5 条 trace
5. 按 `references/triage-matrix.md` 的决策矩阵给结论：
   - 严重度（P0/P1/P2）
   - 最可能的 3 个根因（带证据链接）
   - 推荐动作（限流/扩容/回滚/继续观察）
6. 写入值班记录 `.ops/incidents/<date>-<service>.md`

## 边界
- 只分析、不执行任何变更（变更交给 ops-action Skill）
- 拉取数据有超时控制（每个脚本最多 30s）
```

`references/triage-matrix.md`（按需加载）：

```markdown
# 分诊决策矩阵

| 现象 | P99 延迟 | 错误率 | 流量 | 推断根因 | 推荐动作 |
|------|---------|-------|------|---------|---------|
| 延迟涨 + 错误率平 | ↑↑ | 平 | 平 | 下游慢 / GC | 看下游 + pprof |
| 延迟涨 + 错误率涨 | ↑ | ↑↑ | 平 | 依赖故障 | 熔断 + 联系下游 |
| 延迟涨 + 流量涨 | ↑ | 平 | ↑↑ | 容量不足 | 扩容 |
| 错误率突增 + 流量平 | 平 | ↑↑↑ | 平 | 代码 bug | 回滚最近发布 |
```

#### 8.3.3 Skill：ops-action（变更执行）

```markdown
---
name: ops-action
description: 执行受控的运维动作（扩容/限流/回滚/重启）。当 alert-triage 给出推荐动作、或用户明确说"扩容到 X"、"回滚 X"、"开限流"时触发。所有动作必须先输出执行计划等用户确认。
allowed_tools: Bash, Read, Write
---

# 运维动作 Skill

## 支持的动作
- scale：调整副本数 / HPA 上限
- rollback：回滚到上一个稳定版本
- ratelimit：调整限流阈值
- restart：滚动重启

## 工作流（强制顺序）
1. **生成执行计划**：动作类型、目标对象、当前值、目标值、影响范围、回滚方式
2. **dry-run**：用 kubectl --dry-run=server 或对应平台的预演接口
3. **打印计划**等用户输入"confirm"才继续
4. **分批执行**（按 ops-safety Rule 单批 ≤30%）
5. **每批后等待 60s 观察核心指标**，恶化则自动停止
6. **写值班记录**追加本次动作详情

## 红线
- 没有 confirm 不执行
- 没有 dry-run 不执行
- 影响范围 >30% 时强制人工二次确认
```

#### 8.3.4 Skill：log-dig（日志深挖）

```markdown
---
name: log-dig
description: 在大量日志里定位特定问题：聚类相似错误、按时间窗对比、找首次出现时间。当用户说"日志里查下 X"、"这个错什么时候开始的"、"分类下错误"时触发。
allowed_tools: Bash, Read, Write
---

# 日志深挖 Skill

## 工作流
1. 拉取指定时间窗的日志（默认走 ELK API）
2. 按 stack trace 顶部三行做指纹聚类，输出 Top 10 错误类型 + 计数
3. 对每类错误，给出：
   - 首次出现时间（精确到秒）
   - 受影响 trace 数量
   - 是否与某次发布时间吻合（自动比对 CI 记录）
4. 输出 Markdown 报告 `.ops/logs/<date>-dig.md`

## 边界
- 不直接看明文用户数据，掩码后输出
- 单次最多分析 100 万行，超过则按时间分桶
```

#### 8.3.5 Skill：postmortem（故障复盘）

```markdown
---
name: postmortem
description: 故障平息后，根据 .ops/incidents/ 下的值班记录，自动生成复盘报告草稿。当用户说"写复盘"、"出 postmortem"时触发。
allowed_tools: Read, Write
---

# 复盘报告 Skill

## 输入
- 一条或多条值班记录路径
- 故障时间窗

## 输出（按团队模板填空）
1. **影响范围**：受影响接口/用户量/时长
2. **时间线**：从首条告警到完全恢复，分钟级
3. **根因**：直接原因 + 深层原因（5 Why）
4. **改进项**：每条带 Owner、截止日期、可验证标准
5. **吸取的教训**：写给未来的自己

## 边界
- 不做归责、不写"某某操作失误"
- 改进项必须可验证（"加监控"不算，"加 X 指标 + 阈值 Y 的告警"才算）
```

### 8.4 一次完整告警处置（伪流程）

值班人员收到告警，把告警原文丢给 Agent：

```
[告警] order-service / http_p99 > 800ms / 持续 3min / 2026-05-11 02:15

→ Agent 命中 alert-triage Skill
  - 拉 Grafana：流量平稳，延迟从 200ms 涨到 1.2s
  - 拉日志：connection reset by peer × 1843 条
  - 拉 trace：慢点集中在 mysql query
  - 输出：P1 / 根因假设：DB 连接池打满 / 推荐：扩 DB 连接池或重启实例

→ 用户："按推荐扩连接池到 200，分批"
→ Agent 命中 ops-action Skill
  - 生成计划：deployment/order-service env DB_POOL_SIZE 100→200
  - dry-run 通过
  - 打印计划，等 confirm
  - 用户：confirm
  - 分两批 rollout，每批后看 P99，60s 内回落到 250ms

→ 5 分钟后告警恢复

→ 第二天上午用户："写复盘"
→ Agent 命中 postmortem Skill
  - 读 .ops/incidents/2026-05-11-order-service.md
  - 输出复盘草稿，含时间线、根因、3 条改进项
```

整个过程值班人员只输入了 3 句话，剩下都是 Skill 在按 SOP 执行。

### 8.5 运维 Skill 的特别设计要点

1. **强制 dry-run**：写进 Skill 工作流，不依赖用户记得
2. **审计留痕**：每个 Skill 末尾都写一份 Markdown 记录到固定目录
3. **分批 + 观察**：直接写成步骤，不靠 Agent 自己判断
4. **多源数据聚合**：把 Grafana / ELK / Tracing / CMDB 的查询脚本放 `scripts/`，Skill 只负责编排
5. **拒绝模糊动作**：所有动作都要有"目标值"，不能是"调一调"

---

## 9. 实战案例 C：数据与报告工作流

> 数据 / 报表场景的特点是「**输入是模糊需求，输出是结构化文档**」，Skill 在这里的作用是把"需求 → SQL → 数据 → 图表 → 文字结论"这条链固化下来。

### 9.1 典型场景

- 周报 / 月报：固定指标 + 文字解读
- Ad-hoc 数据问题："上周 GMV 为啥跌了 5 个点"
- 业务复盘：活动效果分析

这类工作 90% 的时间花在"找数据 + 排版"，Skill 可以把这部分自动化。

### 9.2 Skill：weekly-report（周报）

```markdown
---
name: weekly-report
description: 生成业务周报：拉指标、做同环比、画图、写文字解读。当用户说"出周报"、"生成本周报告"、"周一汇报材料"时触发。
allowed_tools: Bash, Read, Write
---

# 周报 Skill

## 工作流
1. 计算时间窗：本周一 00:00 到周日 24:00，对照上周与去年同期
2. 跑 `scripts/pull_metrics.sql`，输出 .data/metrics-<week>.csv
3. 用 `scripts/render_charts.py` 生成 PNG（指标 × 周对比折线 + 同环比柱状）
4. 按 `references/weekly-template.md` 填空：
   - 核心指标卡（GMV / DAU / 转化率 / 退款率）
   - 异常指标解读（自动识别同/环比偏离 ±5% 的指标）
   - 下周重点（从 .ops/plans/ 读取）
5. 输出 `.reports/weekly-<week>.md`

## 边界
- 不解读业务策略变化（标记"待人工补充"）
- 不接触原始用户数据
```

`references/weekly-template.md`：

```markdown
# 业务周报（W{{week}}）

## 一、核心指标
| 指标 | 本周 | 上周 | 环比 | 同期 | 同比 |
|------|------|------|------|------|------|
| GMV  | ...  | ...  | ...  | ...  | ...  |
...

## 二、关键变化
{{auto_filled_anomalies}}

## 三、下周重点
{{from_ops_plans}}

## 四、附录
- 数据口径见 docs/metrics-spec.md
- 图表源数据：.data/metrics-{{week}}.csv
```

### 9.3 Skill：adhoc-data（即席数据问题）

```markdown
---
name: adhoc-data
description: 回答"X 指标为什么变化"类问题：拆维度、定位贡献度、给出假设。当用户问"为什么 X 跌了/涨了"、"X 指标异常分析"时触发。
allowed_tools: Bash, Read, Write
---

# 即席数据 Skill

## 工作流
1. 解析问题：指标是什么、时间窗、对比基准
2. 按预设维度逐个拆（渠道 / 品类 / 地区 / 用户分层）
3. 每个维度算贡献度：`Δ_total = Σ Δ_i`，找 Top 3 贡献维度
4. 在 Top 维度上递归下钻一层
5. 输出"指标变化拆解树 + 3 条根因假设 + 验证方案"

## 边界
- 给假设不下结论，结论必须人工确认
- 数据缺失要明确标注，不脑补
```

### 9.4 数据 Skill 的设计要点

1. **口径一致性**：把指标定义放进 `references/metrics-spec.md`，Skill 强制引用
2. **可验证**：每个数字都要附 SQL 或源 CSV 路径，方便人工 spot check
3. **拒绝结论**：Skill 给"假设 + 证据"，结论留给人——这能避免 AI 编数据

---

## 10. 何时用 Skill、何时不用——场景分类法

把所有日常工作按"流程化程度"和"频次"画一张二维图：

```
高频
 │
 │  [应该做成 Skill]            [必须做成 Skill]
 │  · 写 PR / commit            · 告警分诊
 │  · 周报                       · 部署 / 回滚
 │  · 单测生成                   · 故障复盘
 │
 │─────────────────────────────────────
 │  [写 Rule 即可]              [按需做 Skill]
 │  · 编码风格                   · 季度规划
 │  · 回复语气                   · 安全审计
 │  · 文件命名                   · 大版本发版
 │
 └────────────────────────────────────── 流程化程度 →
        弱                              强
```

**规则**：

- **高频 + 强流程**：必做 Skill（运维变更、告警处置）
- **高频 + 弱流程**：写 Rule（编码风格）
- **低频 + 强流程**：做 Skill（季度发版、安全审计）
- **低频 + 弱流程**：临时聊天解决，不要过度工程化

### 10.1 一份"非编码 Skill 灵感清单"

工程师日常其实有大量重复劳动可以 Skill 化：

| 角色 | 高价值 Skill |
|------|-------------|
| 后端 / SRE | 告警分诊、变更执行、容量评估、故障复盘、值班交接 |
| 数据 | 指标拆解、周报、A/B 报告、漏斗分析、数据校验 |
| 产品 / 运营 | 竞品扫描、活动复盘、用户反馈聚类、PRD 自检 |
| 个人效率 | 周报汇总、邮件分类、会议纪要结构化、待办批量管理 |
| 团队管理 | OKR 进度同步、1on1 提纲、招聘简历筛选、绩效记录归档 |

只要满足"步骤固定 + 输入输出明确 + 跨多个系统"，就值得做成 Skill。

---

## 11. 调试与迭代

### 11.1 Skill 没被触发？

按这个清单排查：

1. **description 里有触发词吗？** 用户实际说的词要在 description 里出现
2. **description 太抽象？** 把"做什么"改成"什么时候做"
3. **被同名 Skill 抢了？** 用 `list-skills` 看是否有重复
4. **场景描述与 Skill 不匹配？** 在用户消息里加更具体的关键词

### 11.2 Rules 不生效？

1. 检查 globs 是否覆盖当前文件
2. 检查 alwaysApply 是否为 true
3. 同类规则是否被另一个文件覆盖
4. Rule 是否用了软词（"尽量""推荐"）

### 11.3 迭代节奏

```
v0.1: 用 Rules 把所有约束写一遍
  ↓ 跑 1 周
v0.2: 把使用率低、内容长的拆成 Skill
  ↓ 跑 2 周
v0.3: 观察哪些 Skill 经常一起用 → 合并或建立调用关系
  ↓ 持续
v1.0: 工作流稳定后写 README 给团队
```

---

## 12. 常见陷阱与排查清单

| 陷阱 | 表象 | 解法 |
|------|------|------|
| Rule 与 Skill 内容重复 | 双份维护、容易冲突 | Rule 只放约束，流程进 Skill |
| Skill description 写成了文档简介 | 触发率低 | 改成"何时触发"格式 |
| Skill 里塞了太多代码示例 | 上下文膨胀 | 移到 references/，用到再 Read |
| 一个 Skill 干 5 件事 | 难维护、命中不准 | 拆成多个，用文档串联 |
| Rules 写得像作文 | Agent 选择性忽略 | 改成 bullet + 否定式 |
| 没有版本管理 | 改坏了无法回退 | Rules/Skills 进 git |
| 跨项目共享乱 | 团队规则各异 | 拆 user-level 与 project-level |

---

## 13. 附录：模板速查

### 13.1 Rule 模板

```markdown
---
description: <一句话说明这条 Rule 管什么>
globs: ["**/*.go"]            # 可选，限定文件范围
alwaysApply: true             # 是否常驻
---

# <主题>

## 必须
- ...
- ...

## 禁止
- NEVER ...
- NEVER ...

## 例外（可选）
- 当 X 时可以 Y
```

### 13.2 Skill 模板

```markdown
---
name: <skill-name>
description: <做什么 — 一两句话>。
触发场景：<场景 1，含真实用户原话>；<场景 2>；<场景 3>。
即使用户没明说 "<关键词>"，只要涉及 <能力领域> 也使用本 Skill。
不处理 <边界 1>（由 <other-skill> 负责）。
---

# <Skill Name>

## 为什么这样做
<1-3 句解释 Skill 的设计动机：解决什么误区、为什么要按这个流程>

## 输入
- <输入类型 1>
- <输入类型 2>

## 前置条件（可选）
- <必须存在的文件 / 必须的分支 / 必须的环境变量>

## 主流程
1. <步骤 1，能脚本化的引用 scripts/xxx.sh>
2. <步骤 2，需要查阅资料的指向 references/xxx.md>
3. <步骤 3>

## 输出格式
<给一个完整模板或 Input/Output 示例>

## 边界
- 不做 <X>（属于 <other-skill>）
- 不做 <Y>（需要用户手动确认）
```

### 13.3 Skill 评测集模板（evals.json）

```json
{
  "skill_name": "weekly-report",
  "evals": [
    {
      "id": 1,
      "prompt": "出一下这周的业务周报，重点看下 GMV 跌的原因",
      "expected_output": "Markdown 周报，含同/环比表格、Top 3 贡献维度",
      "assertions": [
        "output_contains_table_with_GMV_DAU_columns",
        "output_has_top3_contributors_section",
        "output_file_extension_is_md"
      ]
    },
    {
      "id": 2,
      "prompt": "周一汇报材料还没写，照例帮我搞一份",
      "expected_output": "同 #1，且 prompt 没明示 '周报' 也要触发",
      "assertions": ["skill_was_triggered", "..."]
    }
  ]
}
```

### 13.4 description 优化的"够用集"自检

写完 description 后，至少自己想 5 条 should-trigger + 5 条 should-not-trigger：

```json
[
  {"query": "出下本周的业务周报", "should_trigger": true},
  {"query": "周一开会要的材料还没准备", "should_trigger": true},
  {"query": "ad-hoc 问个数据：GMV 跌了多少", "should_trigger": false},
  {"query": "把这条 SQL 优化下", "should_trigger": false}
]
```

跑一下看看是不是该触发的都触发、不该触发的没触发。两边都至少 80% 才算合格。

### 13.5 一句话总结

> **Rules 立规矩，Skills 教手艺。**
> 规矩越精炼越好，手艺越具体越值钱。
> 把"每次都要做的事"写成 Rule，把"特定场景才做的事"写成 Skill，
> 一条工作流 = 一组 Rules 兜底 + 多个 Skills 接力。

---

*本教程持续迭代。建议把你团队的工作流先用纸笔画出来，再对照 7.1 的架构图落地。*

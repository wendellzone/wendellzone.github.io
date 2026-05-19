---
title: 给 AI 编码助手装上工程素养——mattpocock/skills 项目深度解析
date: 2026-05-19
tags: [AI, 工具, 工程素养]
summary: Matt Pocock 开源的 AI coding skill 集合，把工程基本功翻译成 prompt
---

## 目录

- [一、项目背景](#一项目背景)
- [二、为什么要有这套 skills](#二为什么要有这套-skills)
- [三、设计哲学](#三设计哲学)
- [四、四大失败模式与对策](#四四大失败模式与对策)
- [五、Skill 是怎么生效的（底层原理）](#五skill-是怎么生效的底层原理)
- [六、实操：怎么在 CodeBuddy / Claude Code 里调用](#六实操怎么在-codebuddy--claude-code-里调用)
- [七、Engineering 桶——10 个工程类 skill 详解](#七engineering-桶10-个工程类-skill-详解)
- [八、Productivity 桶——4 个生产力类 skill 详解](#八productivity-桶4-个生产力类-skill-详解)
- [九、Misc 桶——4 个杂项 skill 详解](#九misc-桶4-个杂项-skill-详解)
- [十、推荐工作流：从想法到上线](#十推荐工作流从想法到上线)
- [十一、落地建议](#十一落地建议)
- [十二、附录：核心理论出处](#十二附录核心理论出处)

---

## 一、项目背景

**项目地址**：[github.com/mattpocock/skills](https://github.com/mattpocock/skills)
**作者**：Matt Pocock，TypeScript 圈知名讲师，Total TypeScript 课程作者
**定位**：一套给 AI 编码助手（Claude Code、Codex、Cursor 等）使用的"斜杠命令"集合（slash commands）
**核心主张**：**Real engineering, not vibe coding**（搞真工程，不是凭感觉糊代码）

### 项目的市场定位

市面上已经有 GSD、BMAD、Spec-Kit 这类"全包式流程框架"，它们试图通过**接管整个开发流程**来帮你管住 AI。但作者认为：

> "在帮你的同时，它们夺走了你的控制权，让流程中的 bug 难以解决。"

mattpocock/skills 选的是**反方向**——这里说的"反方向"，具体指 4 个维度上和全包框架完全相反的设计取向：

**反方向 #1：从"接管流程"到"提供工具"**

全包框架的逻辑是：你告诉我目标，剩下的我全管——分析、拆解、写代码、测试、上线，框架内置一条固定流水线。出问题时你很难干预，因为流水线是黑盒。

mattpocock/skills 不替你做决定。你随时可以选某个 skill 来干某件事，不选就不用。每个 skill 只负责"把这件具体的事做好"，不管前后衔接。流程的指挥权一直在你手上。

**反方向 #2：从"大颗粒"到"小颗粒"**

全包框架是"一次安装、整体启用"，往往几千行配置 + 多个模板文件 + 一套生命周期约定。

mattpocock/skills 是"按 skill 分别启用"，每个 skill 就一个 markdown 文件、几十到几百行。你可以只装 `/tdd` 不装 `/triage`，也可以把 `/grill-me` 改成你团队的语气。

**反方向 #3：从"模型绑定"到"模型无关"**

全包框架往往针对特定模型调优（比如 BMAD 主要面向 Claude），换模型会掉效果甚至不工作。

mattpocock/skills 是纯 prompt 工程，没有任何"必须调用某 API"或"必须搭配某模型"的硬要求。Claude / GPT / Gemini / 国产模型都能跑。

**反方向 #4：从"框架优先"到"基本功优先"**

全包框架的卖点是"流程"——按它的流程走，新手也能产出像样的工程。

mattpocock/skills 的卖点是"基本功"——它把《Pragmatic Programmer》《DDD》《A Philosophy of Software Design》这些书里的思想浓缩成 prompt，让 AI 在每个动作里都体现工程素养。它不试图替代基本功，而是放大基本功。

| 维度 | 全包框架（GSD/BMAD/Spec-Kit） | mattpocock/skills |
|---|---|---|
| 控制权 | 框架接管流程 | 你接管流程 |
| 颗粒度 | 大，端到端 | 小，单一职责 |
| 模型耦合 | 通常绑定特定模型 | model-agnostic |
| 卖点 | 流程标准化 | 工程基本功放大 |
| 适合人群 | 想要"开箱即用"的团队 | 已经有工程素养、想用 AI 提效的工程师 |
| 学习曲线 | 陡（要学整套框架） | 平缓（按需学单个 skill） |
| 翻车成本 | 高（流水线黑盒难调） | 低（直接改 markdown） |

### 项目数据

- **总技能数**：21 个正式 skill（engineering 10 + productivity 4 + misc 4 + 其它 3）
- **代码量**：约 60 个 markdown 文件
- **依赖**：无强依赖，纯 prompt 工程

---

## 二、为什么要有这套 skills

作者在文档里给出非常直接的回答：**这是为了修复 Claude Code、Codex 这些 coding agent 的常见失败模式。**

那些失败模式是什么？是软件工程领域**几十年来一直在解决的老问题**，只不过在 AI 时代被加速了：

- 沟通错位 → AI 误解需求 → 写出错的东西
- 没有共享语言 → AI 用 20 个词描述本该 1 个词的概念
- 没有反馈回路 → AI 写的代码看起来对、跑起来错
- 没有架构约束 → AI 加速产出 = 加速产生屎山

> **"软件工程基本功，在 AI 时代比以往任何时候都更重要。"**
> — Matt Pocock

---

## 三、设计哲学

### 3.1 三个核心原则

**1. 小而精，可拆可改**
每个 skill 都是一个独立的 markdown 文件，几十到几百行。你可以按需启用、随手改写、组合使用。

**2. Model-agnostic**
对底层模型零绑定。Claude、GPT、Gemini 都能用。skill 本质是 prompt 工程的最佳实践集合。

**3. 站在巨人肩上**
所有 skill 都对应着经典软件工程理论：
- 《Pragmatic Programmer》→ 追踪弹（tracer bullet）、小步快跑
- 《Domain-Driven Design》→ 领域语言（ubiquitous language）
- 《A Philosophy of Software Design》→ 深模块（deep module）
- 《Extreme Programming》→ 测试驱动、持续重构

### 3.2 一句话总结

> **"AI 加速一切，所以基本功的 ROI 也被加速。"**

---

## 四、四大失败模式与对策

这是整个项目的**主轴**，理解了这四个模式就理解了所有 skill 的存在理由。

### 失败模式 #1：Agent 没做对你想要的

**问题**：你以为 AI 懂你了，结果它写出来的东西完全是另一个东西。

> "没有人确切知道自己想要什么。" — David Thomas & Andrew Hunt

**对策**：在 AI 动手前，**强制盘问**对齐。

- `/grill-me` —— 通用盘问
- `/grill-with-docs` —— 带文档维护的盘问

### 失败模式 #2：Agent 太啰嗦，黑话不一致

**问题**：AI 不懂项目领域语言，把"用户"叫成"client/customer/account/user/buyer"五种不同写法，读起来累、token 烧得多。

> "有了普及语言，开发者之间的对话和代码表达，都源自同一个领域模型。" — Eric Evans, DDD

**对策**：在 `CONTEXT.md` 里维护项目专属术语表，强制 AI 收敛词汇。

- `CONTEXT.md` + `docs/adr/` —— 由 `/grill-with-docs` 自动维护

### 失败模式 #3：代码不工作

**问题**：你和 AI 对齐了，需求也清楚了，但它写出来的代码跑起来有问题。

> "永远迈小而审慎的步子。反馈速度就是你的速度上限。永远不要接超出能力范围的活。" — Pragmatic Programmer

**对策**：建立反馈回路。

- `/tdd` —— 红绿重构（red-green-refactor）的测试驱动开发
- `/diagnose` —— 严谨的 bug 诊断流程

### 失败模式 #4：搞出一坨烂泥

**问题**：AI 加速代码产出，也加速了软件熵增。一两周的项目就长成一坨烂泥球。

> "每天都要投资在系统设计上。" — Kent Beck
> "最好的模块是深的：通过简单接口提供大量功能。" — John Ousterhout

**对策**：定期主动改善架构。

- `/improve-codebase-architecture` —— 找出"深化机会"
- `/zoom-out` —— 拉高视角看代码
- `/to-prd` —— 改动前先把模块影响想清楚

```
┌─────────────────────┐    ┌──────────────────────────┐
│ #1 没做对你想要的    │ ──▶│ /grill-me /grill-with-docs│
├─────────────────────┤    ├──────────────────────────┤
│ #2 太啰嗦, 黑话乱   │ ──▶│ CONTEXT.md + ADR          │
├─────────────────────┤    ├──────────────────────────┤
│ #3 代码不工作        │ ──▶│ /tdd, /diagnose           │
├─────────────────────┤    ├──────────────────────────┤
│ #4 搞出一坨烂泥      │ ──▶│ /improve-codebase-arch    │
└─────────────────────┘    └──────────────────────────┘
```

---

## 五、Skill 是怎么生效的（底层原理）

### 5.1 Skill 文件结构

每个 skill 本质是一个 `SKILL.md` 文件，分两部分：

**Part 1：Frontmatter（YAML 元数据）**

```yaml
---
name: grill-with-docs
description: Grilling session that challenges your plan against the existing
  domain model, sharpens terminology, and updates documentation inline.
  Use when user wants to stress-test a plan against their project's language.
---
```

`description` 字段是 **agent 触发匹配的关键**。Claude Code 启动时会把所有 skill 的 description 灌进系统提示，AI 根据用户当前意图自动选择最匹配的 skill 加载。**这也是为什么翻译时绝对不能动 description 字段**——动了就影响触发。

**Part 2：Body（指令正文）**

正文是给 agent 看的指令——告诉它**该怎么做**这件事。可能包含：

- 具体步骤（"先盘问，再探索代码库，再做计划"）
- 决策规则（"只有满足三个条件才创建 ADR"）
- 检查清单（"每个 cycle 后检查测试是否仍然只测行为不测实现"）
- 子文档引用（用 `[deep-modules.md](deep-modules.md)` 链接到延伸阅读）

### 5.2 触发机制

```
用户输入 ─▶ Claude Code 内部
              │
              ├─ 显式触发：用户输入 /skill-name
              │   └─▶ 直接加载该 skill 的 SKILL.md 进上下文
              │
              └─ 隐式触发：根据 description 字段自动匹配
                  └─▶ AI 判断当前任务匹配哪个 skill
                      └─▶ 加载并按 SKILL.md 指令执行
```

### 5.3 Progressive disclosure（渐进式披露）

skill 文件不是一次性把所有信息塞给 AI。它通过**子文档引用**实现按需加载：

```
SKILL.md（精简）
  │
  ├──▶ [deep-modules.md](deep-modules.md)
  │     仅当 AI 需要展开"深模块"概念时才会去读
  │
  ├──▶ [tests.md](tests.md)
  │     仅当 AI 在写测试时才会去读
  │
  └──▶ [refactoring.md](refactoring.md)
        仅当 AI 进入 refactor 阶段才会去读
```

这样既保证 SKILL.md 主文件简洁（节省 token），又保证 AI 在需要细节时能拿到。

---

## 六、实操：怎么在 CodeBuddy / Claude Code 里调用

这一节专门回答最常被问的问题：**"我打开 IDE，到底怎么用一个 skill？"**

### 6.1 安装 skill 到工作区

第一步是把 skill 文件放到 AI 编码助手能识别到的位置。不同工具略有差异：

| 工具 | skill 存放位置 | 加载时机 |
|---|---|---|
| **CodeBuddy / WorkBuddy** | `~/.workbuddy/skills/`（用户级）<br>`{项目}/.workbuddy/skills/`（项目级） | 启动会话时自动扫描，按 description 触发 |
| **Claude Code** | `~/.claude/skills/`（用户级）<br>`{项目}/.claude/skills/`（项目级） | 启动会话时自动扫描 |
| **Cursor** | `.cursor/rules/` 或 MDC 规则 | 取决于具体配置 |

mattpocock 的官方安装方式是一条命令：

```bash
npx skills@latest add mattpocock/skills
```

它会让你勾选要装哪些 skill 和装到哪个工具。**勾选时务必把 `setup-matt-pocock-skills` 也勾上**，这是项目级配置脚本，第一次使用时必须先跑。

### 6.2 在对话框里怎么"触发"一个 skill

这是用户最容易卡住的地方。**有两种触发方式**，对应不同场景：

#### 方式 A：显式触发（推荐入门用）

直接在对话框里输入 `/skill-name`，**和你的需求写在同一条消息里**，一次性发送。

**正确示例**（以 grill-me 为例，回答你的问题）：

```
/grill-me

我想给 order-service 加一个批量审批订单的功能。
能让运营在管理后台一次性勾选多个待审批 job，统一通过或驳回。
```

发出去之后，AI 收到的是"加载 grill-me 这个 skill 的指令 + 你的具体需求"，它会按 grill-me 的 prompt 开始盘问你。

**不需要分两步发**：

```
❌ 错的用法（很多新手会这么做）：
   第一条：/grill-me
   AI：好的，请问您想盘问什么？
   第二条：我想给 order-service 加批量审批…
   （这样会浪费一轮对话，效果也差）

✅ 对的用法：
   一条消息发完：/grill-me + 完整需求
```

> 💡 **核心心法**：把 `/skill-name` 想成一个**带前缀的指令模式切换**。它告诉 AI："接下来这条消息，请用 X 这套规则来处理。"指令和上下文必须放一起，AI 才有完整信息开始工作。

#### 方式 B：隐式触发（熟练后用）

你**根本不输入 `/`**，直接说自己的需求。AI 会根据 skill 的 description 字段自动判断要不要用某个 skill。

**示例**：

```
帮我盘问一下这个设计：我想给 order-service 加批量审批订单…
```

AI 看到"盘问"这个词，会匹配到 `grill-me` 的 description（包含"grill"和"interview relentlessly"），自动按 grill-me 的方式来处理。

**新手建议**：前两周都用方式 A 显式触发，把每个 skill 的名字和用法记熟。熟练后再让 AI 自动选。两种触发方式的详细对比见下一节。

### 6.3 显式触发 vs 隐式触发：详细对比

这是一个值得单独展开讲的话题，因为**选错触发方式会直接影响 skill 的效果**。

#### 6.3.1 工作机制对比

**显式触发（`/skill-name`）的内部流程**

```
用户输入: "/grill-me   我想给 X 加 Y 功能..."
   │
   ▼
解析器看到 "/" 开头 → 识别为 skill 调用
   │
   ▼
直接定位 ~/.workbuddy/skills/grill-me/SKILL.md
   │
   ▼
把 SKILL.md 全文 + frontmatter 注入到 system prompt
   │
   ▼
把"我想给 X 加 Y 功能..."作为用户消息送给模型
   │
   ▼
模型在 grill-me 的 prompt 约束下回应
```

**隐式触发（自然语言）的内部流程**

```
用户输入: "帮我盘问一下这个设计..."
   │
   ▼
工具启动时已把所有 skill 的 description 字段
预加载到 system prompt
   │
   ▼
模型读用户消息，自己判断"这个意图匹配哪个 skill"
   │
   ▼
匹配到 grill-me（因为 description 含 "grill" "interview relentlessly"）
   │
   ▼
模型主动加载 grill-me/SKILL.md 全文
   │
   ▼
按 grill-me 的指令回应
```

关键差异：**显式触发是"指令式"——你告诉系统加载哪个 skill；隐式触发是"猜测式"——模型读你意图后自己决定加载哪个。**

#### 6.3.2 优劣势对比

| 维度 | 显式触发 `/skill-name` | 隐式触发（自然语言） |
|---|---|---|
| **命中率** | 100% 命中你指定的 skill | 70-90%，取决于关键词覆盖 |
| **延迟** | 直接加载，最快 | 模型先做匹配决策，多 1 步推理 |
| **token 开销** | 只加载目标 skill | 所有 skill 的 description 都驻留在 system prompt |
| **可控性** | 完全可控 | 模型可能选错或不选 |
| **学习曲线** | 要记 skill 名 | 自然，不用学 |
| **混合调用** | 一条消息只能触发一个 skill | 模型可能在中途切换 skill |
| **可调试性** | 高（你知道用了哪个 skill） | 低（要看模型的 reasoning 才知道） |
| **与 description 字段耦合** | 弱（只看 name） | 强（description 写得好不好直接影响触发） |
| **对中文输入友好度** | 一致（命令是英文） | 取决于 description 是否包含中文关键词 |

#### 6.3.3 各场景下的最佳选择

| 场景 | 推荐 | 原因 |
|---|---|---|
| 第一次用某个 skill | 显式 | 命中率 100%，先验证 skill 装对了 |
| 关键流程节点（TDD 写测试、diagnose 修 bug） | **强烈建议显式** | 这种场景容错率低，不能让模型猜 |
| 长会话切换 skill（写完测试要修 bug） | 显式 | 让模型清楚"现在切换上下文了" |
| 你在跑半自动 pipeline（如 CI 里调 AI） | 显式 | 脚本化场景，必须确定性 |
| 日常摸索式对话 | 隐式 | 你也不确定想用哪个 skill，让模型选 |
| 教别人用 skill | 显式 | 演示效果稳定 |
| 中文输入为主的场景 | 显式 | 大部分 skill 的 description 是英文，中文匹配率低 |
| 想让 AI 自动组合多个 skill | 隐式 | 模型可以在不同段落用不同 skill |
| Skill 名记不住时 | 隐式 | 自然语言总能用 |

#### 6.3.4 隐式触发的"匹配陷阱"

隐式触发不是万能的。下面这些情况经常踩坑：

**陷阱 1：description 里没有的同义词不会触发**

```
你说："quiz 我一下这个方案"
预期：触发 /grill-me（盘问 ≈ 拷问 ≈ quiz）
实际：可能不触发，因为 grill-me 的 description 里只有
      "grill"、"interview relentlessly"，没有 "quiz"
```

**陷阱 2：意图不明确时模型会"自由发挥"**

```
你说："帮我看看这段代码"
预期：触发 /diagnose 或 /zoom-out
实际：模型可能两个都不用，直接按通用方式回复
```

**陷阱 3：跨语言匹配率不稳定**

```
你说："帮我诊断一下这个 bug"
英文 description: "Disciplined diagnosis loop for hard bugs..."
匹配结果：通常能触发，但不如英文输入"diagnose this bug"稳定
```

**陷阱 4：多个 skill 关键词重叠时会"撞车"**

```
你说："帮我重构一下这块"
候选：/improve-codebase-architecture（含 architecture refactor）
     /tdd（refactor 是它工作流的一环）
模型可能选错。
```

**对策**：在不确定的时候，永远用显式触发。

#### 6.3.5 一段对话里两种方式怎么混用

实际工作中，最舒服的方式是**两种混用**：

```
[显式] /grill-with-docs
       我想给 order-service 加批量审批订单功能。

→ AI 用 grill-with-docs 盘问，更新 CONTEXT.md
（盘问完成后...）

[隐式] 把这次讨论凝练成 PRD 吧。
→ AI 自动识别意图，加载 /to-prd 的 skill，输出 PRD

[显式] /to-issues
       拆成可独立认领的 issue。
→ AI 用 /to-issues 拆切片

（开始干活...）

[显式] /tdd
       从第一个 issue 开始：批量审批 API 骨架。
→ AI 用 TDD 节奏推进
```

规律：**关键阶段切换用显式（确保上对鞍）、阶段内的小动作用隐式（保持对话流畅）。**

#### 6.3.6 一图记忆

```
            ┌──────────────────────────────┐
            │     该用哪种触发方式？        │
            └──────────────┬───────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
        我清楚要用哪个 skill?      我不确定?
              │                         │
              ▼                         ▼
         显式触发                  隐式触发
       /skill-name + 需求         直接说需求
              │                         │
        100% 命中                   模型猜，可能错
              │                         │
              ▼                         ▼
        正确率: 100%              正确率: 70-90%
        token 省                  token 多
        新手友好                  熟练后流畅
```

### 6.4 完整对话示例：用 `/grill-me` 盘问一个新功能

**用户的真实输入**（一条消息发完）：

```
/grill-me

我想给 order-service 加批量审批订单的能力。
后台管理员能一次勾选多个 pending job，批量通过或驳回。
请帮我把方案聊清楚。
```

**AI 收到后内部做的事**：

1. 解析 `/grill-me` → 加载 `~/.workbuddy/skills/grill-me/SKILL.md` 的内容
2. SKILL.md 的指令是"对每个方面无情盘问，一次问一个问题，每个问题给推荐答案"
3. 同时拿到用户的需求"批量审批订单"作为上下文
4. AI 开始按 skill 指令工作

**AI 的第一轮回复**（典型样式）：

```
我会逐个分支地盘问你的方案。一次只问一个问题，每个问题
我都给推荐答案，你确认或修正。

问题 1：批量操作的"事务语义"是什么？
       场景：用户勾选 10 个 job，批准时第 7 个失败了，怎么办？
  
  推荐答案：独立处理。每个 job 独立成功/失败，不回滚已成功的。
            返回结果中明确列出哪些成功、哪些失败、原因。
            理由：审批是不可逆操作（已批的 job 已发出后续动作），
            事务回滚成本高且容易出错；运营可对失败的单独重试。

  你的选择？
```

**用户回应**：

```
认同独立处理。但失败的要能一键重试。
```

**AI 进入下一个问题**：

```
已记。问题 2：批量审批的"一致性边界"在哪？
       场景：管理员勾选 10 个 job 时，其中某个被另一个管理员
       同时单独批准了，状态已变。批量请求到达时怎么办？
  
  推荐答案：乐观锁。请求里带每个 job 的 version 号，服务端
            校验失败的项归入"状态已变"分类，单独提示给前端。
            ……
```

如此一轮一轮，直到所有维度都敲定。

### 6.5 不同 skill 的"输入提示词"模板

下面给出几个最常用 skill 的标准触发模板，你可以直接抄：

**`/grill-me`**（盘问任意计划）：
```
/grill-me

[一段需求或方案描述]
```

**`/grill-with-docs`**（盘问 + 自动维护 CONTEXT.md）：
```
/grill-with-docs

[一段需求或方案描述]
```
> 注意：这个 skill 会主动读你 repo 根目录的 `CONTEXT.md` 和 `docs/adr/`，所以**必须在项目根目录的会话里跑**。

**`/diagnose`**（诊断 bug）：
```
/diagnose

[bug 现象描述：症状、复现条件、错误信息、相关代码位置]
```

**`/tdd`**（TDD 写新功能）：
```
/tdd

要新增的功能：[一段功能描述]
影响的模块：[文件或模块路径]
```

**`/to-prd`**（把已经讨论过的内容凝练成 PRD）：
```
/to-prd
```
> 这个 skill **不需要再补充内容**，它会从对话历史里提取信息。前提是当前会话已经讨论过该需求。

**`/zoom-out`**（拉高视角）：
```
/zoom-out

我对这块代码不熟：[文件或模块路径]
```

**`/improve-codebase-architecture`**（找架构改善机会）：
```
/improve-codebase-architecture

请扫描这个范围：[目录或模块路径]
```

**`/handoff`**（压缩当前会话）：
```
/handoff "下一个 session 用来做 [简短描述]"
```

### 6.6 如果触发失败了怎么办？

常见失败模式和排查：

| 现象 | 原因 | 解决 |
|---|---|---|
| 输入 `/grill-me` 后 AI 当成普通文本回复 | skill 没装到 AI 工具能识别的位置 | 检查 `~/.workbuddy/skills/` 或 `~/.claude/skills/` 是否有 `grill-me/SKILL.md` |
| 触发了但行为不对 | description 字段被改坏，或者 skill 文件残缺 | 重新跑 `npx skills@latest add mattpocock/skills` |
| AI 老是不自动触发 | description 关键词覆盖不够 | 改用显式 `/skill-name` 触发 |
| `/grill-with-docs` 报错说找不到 CONTEXT.md | 没在项目根目录跑 | 切到项目根目录重开会话，或先跑 `/setup-matt-pocock-skills` |
| 跑了之后没找到 issue | issue tracker 没配置 | 跑 `/setup-matt-pocock-skills` 配置 |

### 6.7 一句话记忆

> **写一条消息，前面加 `/skill-name`，后面跟你的真实需求，一次发出去。**
>
> 这就是 skill 的核心使用方式。

---

## 七、Engineering 桶——10 个工程类 skill 详解

这是项目的**核心**，作者每天工作都在用。

### 6.1 `/setup-matt-pocock-skills` —— 一次性配置

**作用**：在某个 repo 第一次使用这套 skill 之前，跑一次这个命令完成配置。

**它问你 3 件事**：

1. **issue tracker 用什么？**
   - GitHub Issues（最常见）
   - Linear
   - 本地 markdown 文件（无 issue tracker 的项目）
2. **triage label 词汇是什么？**
   即把"待分诊"、"已就绪"等抽象状态映射到你 issue tracker 里实际用的标签字符串
3. **领域文档放哪里？**
   一般放 repo 根目录的 `CONTEXT.md` 和 `docs/adr/`

**产物**：写入 repo 的配置文件，供后续 skill 读取。

**原理**：用一次性的盘问把"项目级偏好"固化下来，避免每次跑别的 skill 都要重新对齐。

---

### 6.2 `/grill-with-docs` —— 带文档维护的盘问 ⭐⭐⭐

**这是作者最推崇的 skill。**

**作用**：在你写代码之前，AI 会拿着你的计划，**逐个分支地盘问**你，每个问题给推荐答案让你确认。同时把对话过程中敲定的术语顺手写进 `CONTEXT.md`，把重大决策写成 ADR（Architecture Decision Record）。

**典型对话**：

```
你："我要给订单加个'部分取消'功能。"

AI（盘问）：
  问题 1: "你 CONTEXT.md 里的 cancellation 定义是
          '完全取消订单'，但你刚说的是部分取消——
          是要扩展现有概念，还是新引入一个 PartialCancellation 概念？"
  推荐答案: 新引入 PartialCancellation，避免冲突现有定义。

你："新引入吧。"

AI: 已更新 CONTEXT.md，新增 **PartialCancellation** 术语。
    问题 2: "PartialCancellation 是针对单个 LineItem 还是
            一组 LineItem？"
  ...
```

**与普通盘问 `/grill-me` 的区别**：

| | `/grill-me` | `/grill-with-docs` |
|---|---|---|
| 盘问 | ✅ | ✅ |
| 维护 CONTEXT.md | ❌ | ✅ |
| 维护 ADR | ❌ | ✅ |
| 适用场景 | 非代码工作（写文章、做产品决策） | 代码项目 |

**底层原理**：DDD 的"通用语言"实践 + 苏格拉底式提问。强制把所有模糊概念在动手前对齐。

**ADR 三条创建标准**（作者强调"少即是多"）：

> 仅当三条都满足才建 ADR：
> 1. **难以反悔**：以后改主意成本很高
> 2. **没上下文会让人惊讶**：将来读代码的人会问"为啥这么做？"
> 3. **是真正权衡的结果**：有真实的备选方案，因为某些原因选了这个

---

### 6.3 `/tdd` —— 测试驱动开发 ⭐⭐⭐

**作用**：用红绿重构（red-green-refactor）的纪律驱动 AI 写代码。

**核心信条**：

> **测试应该通过公共接口验证行为，而不是验证实现细节。**
> 代码可以完全重写，测试不该跟着崩。

**好测试 vs 坏测试**：

```
好测试（行为驱动）：
  test('用户可以用合法购物车结账', () => {
    const cart = new Cart([...])
    const result = checkout(cart, validPayment)
    expect(result.status).toBe('success')
  })
  ✅ 重构内部实现，测试不变

坏测试（实现驱动）：
  test('checkout 内部调用了 _validateCart()', () => {
    const spy = jest.spyOn(internal, '_validateCart')
    checkout(...)
    expect(spy).toHaveBeenCalled()
  })
  ❌ 重命名 _validateCart 测试就崩
```

**反模式：水平切片（horizontal slicing）**

很多人对 TDD 的误解是：先写所有测试，再写所有实现。

```
错（水平切片）：
  RED:   test1, test2, test3, test4, test5    ← 一口气写所有测试
  GREEN: impl1, impl2, impl3, impl4, impl5    ← 再一口气写所有实现

对（垂直切片，tracer bullet）：
  RED→GREEN: test1 → impl1                    ← 一次只走一个 cycle
  RED→GREEN: test2 → impl2
  RED→GREEN: test3 → impl3
```

水平切片的问题：批量写出来的测试是"想象中的行为"，而不是"实际的行为"。等到实现时你会发现测试根本没测对地方。

**追踪弹（tracer bullet）的隐喻**：
真实战场上，机枪手发射追踪弹（带荧光的子弹）来调整瞄准方向。第一发不需要打中目标，只要让你看清弹道。TDD 第一个测试也是这个意思——不需要覆盖所有功能，只要打通一条端到端的路。

**子文档**（按需阅读）：
- `tests.md` —— 好测试和坏测试的具体例子
- `mocking.md` —— 什么时候 mock，什么时候不 mock
- `deep-modules.md` —— 接口窄、实现厚的设计原则
- `interface-design.md` —— 为可测试性设计接口
- `refactoring.md` —— 测试通过后的重构清单

---

### 6.4 `/diagnose` —— 诊断疑难 bug 和性能回归 ⭐⭐⭐

**作用**：把"调试"这件事拆成 6 个阶段，每个阶段强制完成才能进下一个。

**六阶段流程**：

```
Phase 1  构建反馈回路        ←【整个 skill 的核心】
Phase 2  复现 bug
Phase 3  生成 3-5 个假设
Phase 4  设计探针验证假设
Phase 5  写回归测试 + 修复
Phase 6  清理 + 复盘
```

**Phase 1 是灵魂**：

> "如果你有一个快速、确定、agent 可跑的 pass/fail 信号，bug 就找到 90%了。
>  bisection、假设验证、加日志，这些都只是消费这个信号。
>  没有信号，盯着代码看一万年也没用。"

10 种构造反馈回路的方法（按优先级降级）：

| 方法 | 适用场景 |
|---|---|
| 1. Failing test | 任何能写测试的层（unit/integration/e2e）|
| 2. Curl / HTTP 脚本 | 跑着 dev server 的 API 问题 |
| 3. CLI fixture diff | 命令行工具，对比 stdout 与已知结果 |
| 4. Headless browser | UI bug |
| 5. Replay 抓的 trace | 网络请求/事件流问题 |
| 6. 抛弃式 harness | 单服务+mock 依赖 |
| 7. Property/fuzz loop | "时不时输出错"类 bug |
| 8. Bisection harness | 介于两个已知状态之间的回归 |
| 9. Differential loop | 新版 vs 旧版同输入对比 |
| 10. HITL bash 脚本 | 必须人参与时的最后手段 |

**对回路本身的迭代**：

> "把回路当产品来打磨。"
> - 能更快吗？（缓存初始化、跳过无关 init）
> - 信号能更准吗？（断言精确症状，而不是"没崩就行"）
> - 能更确定吗？（固定时间、seed RNG、隔离文件系统）

> "30 秒还会抽风的回路，比没有回路强不到哪去。
>  2 秒确定性回路是调试超能力。"

**Phase 3 假设的纪律**：必须**3-5 个**排序假设，单一假设容易锚定第一个想法。每个假设必须可证伪：

> 格式："如果 X 是原因，那么改 Y 会让 bug 消失，改 Z 会让 bug 加重。"

**Tagged debug log**：

> 所有调试日志加唯一前缀，例如 `[DEBUG-a4f2]`。
> 清理时一个 grep 搞定。

---

### 6.5 `/improve-codebase-architecture` —— 找深化机会 ⭐⭐⭐

**作用**：扫描代码库，找出**浅模块**，建议把它们合并成**深模块**。

**核心术语**（Ousterhout 体系）：

| 术语 | 定义 |
|---|---|
| **模块（module）** | 任何"接口+实现"的东西（函数、类、包、切片） |
| **接口（interface）** | 调用方使用模块需要知道的全部：类型、不变式、错误模式、顺序、配置 |
| **实现（implementation）** | 接口背后的代码 |
| **深度（depth）** | 接口窄、实现厚 = 深；接口和实现一样复杂 = 浅 |
| **接缝（seam）** | 接口所在位置；可以在不修改实现的情况下替换行为的地方 |
| **适配器（adapter）** | 在接缝处实现接口的具体类 |
| **杠杆（leverage）** | 调用方从模块深度获得的好处 |
| **局部性（locality）** | 维护者从模块深度获得的好处：变更、bug、知识集中在一处 |

**判断浅模块的工具——"删除测试"**：

> 假装把这个模块删了：
> - 复杂度消失了 → 它是 pass-through，浅模块
> - 复杂度涌现到 N 个调用方 → 它在挣钱，深模块

**典型浅模块例子**：

```typescript
// 这个 isOrderEligible 函数只有一行：
function isOrderEligible(order: Order): boolean {
  return order.status === 'confirmed' && order.amount > 0
}

// 调用方一堆这种代码：
if (isOrderEligible(order)) { ... }

// 删除测试：删掉它，调用方变成
if (order.status === 'confirmed' && order.amount > 0) { ... }
// 复杂度没增加 → isOrderEligible 是浅模块
```

**深化的几种手法**：

1. **合并强耦合的模块**：A 总是和 B 一起改 → 合并成一个
2. **隐藏组合细节**：把"先校验、再变状态、再发事件"隐藏到一个方法后面
3. **Ports & Adapters**：把外部依赖（DB、HTTP、消息队列）封装在适配器后
4. **状态机封装**：分散在各处的 if-else 状态跳转 → 一个状态机模块

**两条铁律**：

> - **接口就是测试面。** 接口没设计好，测试写起来就别扭。
> - **一个适配器 = 假想接缝；两个适配器 = 真实接缝。** 不要预设可替换性。

**子文档**：
- `LANGUAGE.md` —— 完整术语表+反义词（不要漂移到 component/service/API）
- `DEEPENING.md` —— 四类依赖、Ports & Adapters
- `INTERFACE-DESIGN.md` —— "Design It Twice" 并行子 agent 模式

---

### 6.6 `/to-prd` —— 把对话凝练成 PRD

**作用**：你和 AI 谈了半天某个改动，让它把这次对话浓缩成一份 PRD（产品需求文档）并提交为一个 issue。

**关键点**：**不再做新的访谈**，只综合已经讨论过的内容。

**适用场景**：

```
你：和 AI 通过 /grill-with-docs 谈了 30 分钟某个新功能。
你：现在我去开会了，把这次讨论存成 PRD。
你：/to-prd
AI：[把对话里讨论过的需求、决策、约束、不在范围内的事项凝练成一份 PRD]
    [创建为一个 GitHub issue]
```

**为什么和 grill 分开**：盘问需要你在场，PRD 凝练不需要。分开就能错峰使用。

---

### 6.7 `/to-issues` —— 把计划拆成可独立认领的 issue

**作用**：把一份 PRD 或计划拆成**可独立认领**的 issue。

**核心拆分原则**：**垂直切片（vertical slice）**，不是水平切片。

```
错（水平切片，按层拆）：
  Issue 1: 加 DB 表
  Issue 2: 写 API
  Issue 3: 做前端
  Issue 4: 加测试
  问题：单独完成 Issue 1 没法 demo，必须四个都完成才有价值

对（垂直切片，按用户价值拆）：
  Issue 1: 用户能创建订单（最小路径：DB+API+UI+test）
  Issue 2: 用户能查看自己的订单
  Issue 3: 用户能取消订单
  优势：每个 issue 独立交付，单独可以 ship
```

**HITL vs AFK**：

- **HITL（human-in-the-loop）**：需要人工干预的切片（架构决策、设计评审）
- **AFK（away-from-keyboard）**：可以无人值守完成的切片

> 优先 AFK 切片。

---

### 6.8 `/triage` —— issue 状态机分诊

**作用**：把 issue 当作状态机里的对象，给它打上规范的"分诊角色"标签。

**为什么不直接用 GitHub label**：因为每个团队的 label 字符串都不同。把"逻辑角色"和"实际 label 字符串"分开维护：

```
逻辑角色（skill 内部）  ↔  实际 label（项目里）
─────────────────────────────────────────
needs-triage            ↔  "to-be-triaged"
ready-for-afk           ↔  "ai-ready"
needs-design            ↔  "needs-architecture"
blocked                 ↔  "wontfix-for-now"
```

映射在 `setup-matt-pocock-skills` 里配置一次。

---

### 6.9 `/zoom-out` —— 拉高视角

**作用**：当你不熟悉某段代码时，让 AI 给你"画一张地图"——这块代码涉及哪些模块？谁在调用它？属于领域里哪一块？

**完整指令**（这是项目里最短的 skill）：

```
我对这块代码不熟。往上抽一层。
用项目的领域语言（ubiquitous language）词汇表，
给我一张所有相关模块和调用方的地图。
```

**适用场景**：进入老项目、接手别人的代码、debug 时需要全局视角。

---

### 6.10 `/prototype` —— 快速做一次性原型

**作用**：在做正式实现前，先做一个**抛弃式原型**来回答某个具体问题。

**两条分支**：

| 分支 | 适用问题 | 产物 |
|---|---|---|
| **Logic 原型** | 状态/业务逻辑问题 | 可运行的终端应用（TUI） |
| **UI 原型** | 视觉/交互问题 | 几个差异极大的 UI 变体，一个路由切换 |

**关键纪律**：原型是**抛弃式**的。不要因为"反正写都写了"就把它合进主分支。原型的价值在于学习，不在于代码本身。

---

## 八、Productivity 桶——4 个生产力类 skill 详解

### 7.1 `/grill-me` —— 通用盘问

**作用**：和 `/grill-with-docs` 是同一个核心，但**不维护文档**。适合非代码任务（写文章、做规划、产品决策）。

**完整指令**：

```
对我这个计划的每个方面进行无情的盘问，直到我们达成共识。
逐个分支走完决策树，一个一个解决依赖。
每个问题给出你推荐的答案。
一次只问一个问题，等我反馈了再继续。
如果某个问题可以通过探索代码库回答，去探索代码库而不是问我。
```

最后一条很重要——它告诉 AI **能自己查就别问**。

---

### 7.2 `/caveman` —— 原始人模式 ⭐

**作用**：把 AI 切换成**超压缩通讯模式**，token 消耗减少约 75%，但保留全部技术准确性。

**对比示例**：

```
普通模式：
  "Sure! I'd be happy to help you with that.
   The issue you're experiencing is likely caused by..."

caveman 模式：
  "Bug in auth middleware. Token expiry check use `<` not `<=`. Fix:"
```

**规则**：

- 砍冠词（a/an/the）
- 砍填充词（just/really/basically/actually/simply）
- 砍寒暄（sure/certainly/of course）
- 砍犹豫（maybe/perhaps）
- 用箭头表因果（X → Y）
- 缩写常见术语（DB/auth/config/req/res/fn/impl）

**会保留的内容**：

- 技术术语精确不变
- 代码块原样
- 错误信息原文引用
- 安全警告会临时退出 caveman 给完整说明，然后继续

**适用场景**：

- 长会话省 token
- 速成沟通（你已经知道 AI 在干嘛了）
- 团队内部协作（大家都懂上下文）

---

### 7.3 `/handoff` —— 压缩交接

**作用**：把当前对话压缩成一份"交接文档"，保存到临时文件，让另一个 AI session 可以接着干。

**用法示例**：

```bash
/handoff "下一个 session 用来实现 PRD-123"
# AI 会写出一份 mktemp 路径下的 markdown 交接文档
# 包含：
#   - 当前任务背景
#   - 已经做了什么
#   - 接下来该做什么
#   - 推荐用哪些 skill
#   - 需要避开的坑
```

**关键纪律**：**不要重复**已经存在于其他工件里的内容（PRD、commit、diff）。只引用路径或 URL。

**适用场景**：

- 上下文窗口快爆了，需要 reset
- 切换不同的 AI 工具继续工作
- 把任务移交给同事

---

### 7.4 `/write-a-skill` —— 创建新 skill

**作用**：教 AI 怎么帮你创建新 skill。

**它会引导你**：

1. 想清楚 skill 的"使用时机"——什么场景下应该触发它
2. 写 frontmatter（特别是 description 字段，要包含触发关键词）
3. 写正文指令——具体步骤、决策规则、检查清单
4. 决定要不要拆子文档（progressive disclosure）
5. 准备 bundled resources（脚本、模板）

**关键原则**：

- **写得越具体越好**。"做个好 PR 评审"是垃圾指令；"先看 diff 范围、再读测试覆盖、再检查命名一致性..."才是好指令。
- **触发词覆盖要广**。description 里要包含用户可能用到的同义词、变体说法。

---

## 九、Misc 桶——4 个杂项 skill 详解

### 8.1 `/git-guardrails-claude-code` —— git 安全护栏

**作用**：装一组 Claude Code hooks，**拦截危险 git 命令**。

**会被拦截的命令**：

- `git push --force` / `git push -f`
- `git reset --hard`
- `git clean -fd`
- 任何 `branch -D` 强制删除分支

**机制**：在 git 命令执行前，hook 脚本检查模式，匹配则拒绝。

**为什么需要**：AI 在 debug 时可能"自作聪明"地用 `git reset --hard` 清掉它认为没用的本地改动。这种事一旦发生不可逆。

---

### 8.2 `/migrate-to-shoehorn` —— 类型断言迁移

**作用**：把测试里的 `as` 类型断言迁移到 `@total-typescript/shoehorn`。

**适用项目**：作者自己的 TypeScript 项目，对外通用度低。

**迁移示例**：

```typescript
// Before
const user = { id: 1 } as User

// After
import { fromPartial } from '@total-typescript/shoehorn'
const user = fromPartial<User>({ id: 1 })
```

为啥这样改：`as` 完全跳过类型检查，`fromPartial` 仍会校验你提供的字段类型，只是允许字段缺失。

---

### 8.3 `/scaffold-exercises` —— 练习题脚手架

**作用**：作者用来给自己的 TypeScript 课程生成练习题目录结构。

**产物**：sections / problems / solutions / explainers 四档目录。

**通用度**：低，主要是作者本人在用。

---

### 8.4 `/setup-pre-commit` —— 预提交钩子

**作用**：装 Husky + lint-staged，在 git commit 前自动跑 Prettier、type check、test。

**典型产物**：

```
.husky/pre-commit:
  pnpm lint-staged
  pnpm typecheck
  pnpm test --run

package.json:
  "lint-staged": {
    "*.{ts,tsx}": ["prettier --write", "eslint --fix"]
  }
```

**为什么有价值**：和 `/tdd`、`/diagnose` 一脉相承——**让反馈在最早的位置发生**。提交前发现错，比 CI 跑挂、比同事 review 时发现都要好。

---

## 十、推荐工作流：从想法到上线

把所有 skill 串起来，作者推荐的完整工作流是这样的：

```
┌──────────────────────────────────────────┐
│ 阶段 1：对齐意图                          │
│  /grill-with-docs                         │
│  └─ 盘问 + 维护 CONTEXT.md / ADR          │
└────────────────┬─────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────┐
│ 阶段 2：凝练成文档                        │
│  /to-prd                                  │
│  └─ 把对话变成 PRD issue                  │
└────────────────┬─────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────┐
│ 阶段 3：拆解为可执行单元                  │
│  /to-issues                               │
│  └─ PRD 拆成垂直切片 issue                │
│                                            │
│  /triage                                  │
│  └─ 给 issue 打分诊标签                   │
└────────────────┬─────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────┐
│ 阶段 4：实现                              │
│  /tdd          —— 红绿重构写新功能        │
│  /diagnose     —— 修 bug                  │
│  /zoom-out     —— 不熟代码时拉视角        │
│  /prototype    —— 不确定方案时做原型      │
└────────────────┬─────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────┐
│ 阶段 5：维护                              │
│  /improve-codebase-architecture           │
│  └─ 每隔几天扫一遍，找深化机会            │
└──────────────────────────────────────────┘

辅助：
  /handoff   —— 切换 session 时压缩上下文
  /caveman   —— 节省 token 的紧凑模式
```

### 实战示例：给已有项目加新功能

假设要给 order-service 加一个"批量审批订单"功能：

```bash
# 第 1 步：和 AI 对齐细节
/grill-with-docs
# AI 会盘问：
#   - "批量审批"是同时审批多个 job，还是按队列依次审批？
#   - 失败的 job 应该回滚整批还是独立处理？
#   - CONTEXT.md 里现有的 Approval 概念要不要扩展为 BatchApproval？
#   ...
# 同时把敲定的术语写进 CONTEXT.md

# 第 2 步：凝练出 PRD
/to-prd
# 自动创建一个 GitHub issue，包含完整 PRD

# 第 3 步：拆切片
/to-issues
# 拆成 5-7 个 GitHub issue：
#   - 批量审批 API 骨架（垂直切片，最小 happy path）
#   - 批量审批失败回滚
#   - 批量审批审计日志
#   ...

# 第 4 步：开始干
/tdd
# 一次一个 cycle 推进
# 遇到难复现的 bug：
/diagnose
# 不懂 task 模块怎么和 contract 模块联动：
/zoom-out

# 第 5 步：上线后定期跑
/improve-codebase-architecture
# 看看新加的 BatchApproval 是不是浅模块
```

---

## 十一、落地建议

### 10.1 快速开始

```bash
# 30 秒安装
npx skills@latest add mattpocock/skills

# 选 skill 时一定要勾上 setup-matt-pocock-skills
# 然后在 agent 里跑一次：
/setup-matt-pocock-skills
```

### 10.2 选哪些 skill 装

**全员必装**：
- `/grill-me` 或 `/grill-with-docs` —— 投入产出比最高
- `/diagnose` —— bug 一来就值回票价
- `/tdd` —— 长期质量的根基

**强烈推荐**：
- `/improve-codebase-architecture` —— 每两周跑一次
- `/zoom-out` —— 接手陌生代码必备
- `/handoff` —— 长任务必备

**按需装**：
- `/caveman` —— token 敏感场景
- `/prototype` —— 探索性工作多的项目
- `/git-guardrails-claude-code` —— 担心 AI 误删的项目

### 10.3 最佳实践

**1. 先 `/setup-matt-pocock-skills`，再用别的**
配置文件没建，其他 skill 跑出来效果会打折扣。

**2. CONTEXT.md 要勤维护**
建议每次 grill 完都让 AI 顺手更新。代码改了术语含义也要同步。

**3. ADR 宁缺毋滥**
作者明确说："只有满足三个条件才建 ADR。"不要把 ADR 当随手笔记。

**4. 别只用 `/tdd`，要先跑 `/grill-with-docs`**
先把"写什么"对齐，再用 TDD 写。直接跑 TDD 容易写出"想象中的行为"。

**5. `/improve-codebase-architecture` 不要照单全收**
它给的是建议，不是命令。每条建议都要过你自己的判断。

### 10.4 常见误区

| 误区 | 现实 |
|---|---|
| "skill 越多越好" | skill 越多 description 越多，agent 越容易选错 |
| "TDD 就是先写所有测试" | 那叫水平切片，是反模式 |
| "ADR 多多益善" | 90% 的决策不值得写 ADR |
| "Skill 装上就完事了" | CONTEXT.md 不维护等于没装 |
| "AI 加速 = 我能写更多代码" | AI 加速也加速烂代码生成，要主动管控 |

---

## 十二、附录：核心理论出处

如果想深入理解 skill 背后的设计哲学，建议读以下经典：

| Skill | 核心理论 | 出处 |
|---|---|---|
| `/grill-me` `/grill-with-docs` | 通用语言、苏格拉底式提问 | 《Domain-Driven Design》Eric Evans |
| `/tdd` | 红绿重构、追踪弹 | 《Test Driven Development》Kent Beck、《Pragmatic Programmer》|
| `/diagnose` | 反馈回路、Bug 隔离 | 《Debugging》David Agans |
| `/improve-codebase-architecture` | 深模块、复杂性管理 | 《A Philosophy of Software Design》John Ousterhout |
| `/to-issues` | 垂直切片、最小可行交付 | 《User Story Mapping》Jeff Patton |
| 整体架构哲学 | 持续设计、拥抱变化 | 《Extreme Programming Explained》Kent Beck |

---

## 结语

> "AI 加速了一切，包括烂代码的产出速度。
>  所以，软件工程基本功在 AI 时代比以往任何时候都更重要。
>  这套 skill 是我对'怎么把基本功翻译成可重复实践'的最好答案。"
>
> — Matt Pocock

这套 skill 的真正价值不在于命令本身，而在于**它把数十年软件工程经验翻译成了 AI 能直接 follow 的指令**。

学会用它，本质上就是把自己变成更好的工程师——只不过是通过 AI 这面镜子来照出自己的盲区。

---

**分享链接**：
- 项目：[github.com/mattpocock/skills](https://github.com/mattpocock/skills)
- 作者 newsletter：[aihero.dev/s/skills-newsletter](https://www.aihero.dev/s/skills-newsletter)

---
title: Claude Agent Skills 怎么选:superpowers、everything-claude-code 与高 star 方案横评
date: 2026-07-08
tags: [AI, Agent, 工具]
summary: 两大流派横评:方法论包管做得对,能力包管做得了,附按场景选型决策表
---

你说"写个登录接口",AI 直接开写。不澄清需求、不设计方案、不写测试。跑起来能用,但你不敢合。

这是 2026 年 Agent 编程最大的痛点:AI 不是不会写代码,而是**跳步**。GitHub 上 star 最高的一批 Agent Skills 仓库,几乎都在回答同一个问题——怎么给 AI 套上工程纪律的轨道。

本文以 `obra/superpowers` 和 `affaan-m/everything-claude-code` 两个头部项目为主轴对比,再横向拉入其他高 star skill,最后给一张按场景选型的决策表。

## 先分清:两种完全不同的"skill"

高 star 仓库其实分两大流派,解决的问题正交,别混着比。

**流派一:方法论(教 AI 怎么做事)**。不扩展能力,而是约束流程——先想清楚、再隔离干、测着干、查根因、评审验证。代表是 superpowers。

**流派二:能力包(教 AI 会做事)**。给 AI 塞进具体本领——写 PPT、调 Docker、做 SEO、审计安全。代表是 everything-claude-code 里的大部分内容。

<svg viewBox="0 0 680 260" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
<defs>
<marker id="sd-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" stroke="#888780" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker>
</defs>
<rect x="40" y="30" width="280" height="200" rx="12" fill="#EEEDFE" stroke="#534AB7" stroke-width="0.5"/>
<text x="60" y="58" font-family="sans-serif" font-size="14" font-weight="500" fill="#3C3489">方法论流派</text>
<text x="60" y="82" font-family="sans-serif" font-size="12" fill="#5F5E5A">约束 AI 的工作顺序</text>
<text x="60" y="112" font-family="sans-serif" font-size="12" fill="#2C2C2A">· 先澄清需求再动手</text>
<text x="60" y="134" font-family="sans-serif" font-size="12" fill="#2C2C2A">· 强制 TDD 红绿循环</text>
<text x="60" y="156" font-family="sans-serif" font-size="12" fill="#2C2C2A">· 找根因、再评审</text>
<text x="60" y="186" font-family="sans-serif" font-size="12" fill="#3C3489">代表:superpowers</text>
<text x="60" y="210" font-family="sans-serif" font-size="11" fill="#5F5E5A">解决"跳步"</text>
<rect x="360" y="30" width="280" height="200" rx="12" fill="#E1F5EE" stroke="#0F6E56" stroke-width="0.5"/>
<text x="380" y="58" font-family="sans-serif" font-size="14" font-weight="500" fill="#085041">能力包流派</text>
<text x="380" y="82" font-family="sans-serif" font-size="12" fill="#5F5E5A">扩展 AI 的具体本领</text>
<text x="380" y="112" font-family="sans-serif" font-size="12" fill="#2C2C2A">· 生成 PPT / Word / PDF</text>
<text x="380" y="134" font-family="sans-serif" font-size="12" fill="#2C2C2A">· 调工具、做设计</text>
<text x="380" y="156" font-family="sans-serif" font-size="12" fill="#2C2C2A">· 安全审计、求职</text>
<text x="380" y="186" font-family="sans-serif" font-size="12" fill="#085041">代表:everything-claude-code</text>
<text x="380" y="210" font-family="sans-serif" font-size="11" fill="#5F5E5A">解决"不会"</text>
</svg>

一句话:superpowers 管"做得对",能力包管"做得了"。两者可以叠加使用。

## 主角一:superpowers —— 给 AI 装工程纪律

superpowers 由 Jesse Vincent(obra)创建,是目前 star 最高的方法论技能包,已被 Claude 官方插件市场收录。它只有 14 个 skill,却串成一条完整的开发管线。

核心逻辑很简单:**把资深工程师的工作顺序,变成 AI 无法绕过的硬规则**。

它的七步管线从头脑风暴开始,依次是:澄清需求出设计 → 拆成可执行计划 → git worktree 隔离分支 → 子代理逐任务执行 → TDD 红绿重构 → 代码评审 → 收尾合并。

<svg viewBox="0 0 680 130" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
<defs>
<marker id="sp-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" stroke="#888780" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker>
</defs>
<rect x="40" y="40" width="90" height="46" rx="8" fill="#EEEDFE" stroke="#534AB7" stroke-width="0.5"/>
<text x="85" y="60" font-family="sans-serif" font-size="12" font-weight="500" fill="#3C3489" text-anchor="middle">头脑风暴</text>
<text x="85" y="76" font-family="sans-serif" font-size="11" fill="#5F5E5A" text-anchor="middle">出设计</text>
<rect x="160" y="40" width="90" height="46" rx="8" fill="#EEEDFE" stroke="#534AB7" stroke-width="0.5"/>
<text x="205" y="60" font-family="sans-serif" font-size="12" font-weight="500" fill="#3C3489" text-anchor="middle">写计划</text>
<text x="205" y="76" font-family="sans-serif" font-size="11" fill="#5F5E5A" text-anchor="middle">拆任务</text>
<rect x="280" y="40" width="90" height="46" rx="8" fill="#E6F1FB" stroke="#185FA5" stroke-width="0.5"/>
<text x="325" y="60" font-family="sans-serif" font-size="12" font-weight="500" fill="#0C447C" text-anchor="middle">隔离分支</text>
<text x="325" y="76" font-family="sans-serif" font-size="11" fill="#5F5E5A" text-anchor="middle">worktree</text>
<rect x="400" y="40" width="90" height="46" rx="8" fill="#E1F5EE" stroke="#0F6E56" stroke-width="0.5"/>
<text x="445" y="60" font-family="sans-serif" font-size="12" font-weight="500" fill="#085041" text-anchor="middle">子代理</text>
<text x="445" y="76" font-family="sans-serif" font-size="11" fill="#5F5E5A" text-anchor="middle">TDD 执行</text>
<rect x="520" y="40" width="90" height="46" rx="8" fill="#EAF3DE" stroke="#3B6D11" stroke-width="0.5"/>
<text x="565" y="60" font-family="sans-serif" font-size="12" font-weight="500" fill="#27500A" text-anchor="middle">评审</text>
<text x="565" y="76" font-family="sans-serif" font-size="11" fill="#5F5E5A" text-anchor="middle">收尾合并</text>
<line x1="130" y1="63" x2="158" y2="63" stroke="#888780" stroke-width="1.5" marker-end="url(#sp-arrow)"/>
<line x1="250" y1="63" x2="278" y2="63" stroke="#888780" stroke-width="1.5" marker-end="url(#sp-arrow)"/>
<line x1="370" y1="63" x2="398" y2="63" stroke="#888780" stroke-width="1.5" marker-end="url(#sp-arrow)"/>
<line x1="490" y1="63" x2="518" y2="63" stroke="#888780" stroke-width="1.5" marker-end="url(#sp-arrow)"/>
</svg>

它的杀手锏是**防钻空子设计**。每个纪律型 skill 都带三件套:铁律(Iron Law)、借口对照表(把 AI 偷懒时说的每句借口和反驳列出来)、红旗清单(让 AI 自查是否正要违规)。

比如 TDD 那条的铁律是:"没有失败的测试,不许写生产代码。先写了代码?删掉重来——不许留作参考。"

**优点**:轻量、聚焦、跨平台(支持 Claude Code / Codex / Cursor / Gemini CLI / Copilot CLI 等约 10 种);纪律约束是目前做得最狠的。

**代价**:它会显著拖慢"随手写个脚本"这种小活。哪怕改一行配置,它也要求走一遍设计流程。急活场景会嫌它啰嗦。

## 主角二:everything-claude-code —— 大而全的全家桶

everything-claude-code(简称 ECC)是黑客松获奖项目,定位完全不同:**一站式配齐**。

它的规模是 superpowers 的近 20 倍:261 个 skill + 64 个 agent + 84 个命令 shim。从写代码、调工具到做设计、审安全,几乎覆盖日常所有场景。

| 维度 | superpowers | everything-claude-code |
|---|---|---|
| 定位 | 工程方法论 | 能力全家桶 |
| skill 数量 | 14 | 261 |
| 附带 agent | 无(靠子代理机制) | 64 个 |
| 安全机制 | 无内置 | 内置 AgentShield 审计 |
| 上手成本 | 低,概念集中 | 高,内容庞杂 |
| 适合场景 | 严肃工程、团队规范 | 个人全能工作台 |
| 主要风险 | 拖慢小活 | 质量参差、context 占用大 |

ECC 还带了两个 superpowers 没有的东西:内置 AgentShield 安全审计(上千项测试、静态分析规则),以及带置信度评分的持续学习系统。

**优点**:开箱即用,想要的本领基本都有;有安全兜底。

**代价**:261 个 skill 良莠不齐,不是每个都经过 superpowers 那种压力测试;全量加载对 context 是负担,需要按需裁剪。

## 配角阵容:其他值得看的高 star skill

除了两个主角,还有几类高 star 项目各有专精。

**官方与格式参考**。想学 skill 标准写法看这两个:

- `anthropics/skills`——Anthropic 官方出品,含 pdf / docx / pptx / xlsx 那套 office 能力,权威可信。
- `mattpocock/skills`——TypeScript 圈知名人物的真实世界配置,SKILL.md 写法示范价值高。

**方法论同类竞品**:

- `garrytan/gstack`——覆盖执行、设计、工程、文档、QA 的完整团队工作流配置。
- `addyosmani/agent-skills`——Google 的 Addy Osmani 出品,面向 agent 的生产级工程技能,口碑扎实。

**单点尖刀**(解决一个具体痛点):

- `JuliusBrussee/caveman`——"穴居人说话"压缩术,把 AI 回复压缩约 75% 但技术信息不丢,每次会话省 token。理念鲜明。
- `trailofbits/skills`——知名安全公司 Trail of Bits 的安全审计技能包,做加密 / 密钥相关工作值得一看。
- `nextlevelbuilder/ui-ux-pro-max-skill`——提升 UI/UX 产出的设计智能,前端场景实用。

**淘货用的目录**:

- `ComposioHQ/awesome-claude-skills`——1000+ skill 目录,集成 500+ 应用。
- `hesreallyhim/awesome-claude-code`——只收录 1K+ star 项目的权威 awesome-list,当索引起点最合适。

## 怎么选:按场景决策

不存在"最好的 skill",只有"最匹配你场景的组合"。方法论包和能力包本就该叠加。

<svg viewBox="0 0 680 240" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
<defs>
<marker id="dec-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" stroke="#888780" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker>
</defs>
<rect x="250" y="20" width="180" height="44" rx="8" fill="#F1EFE8" stroke="#5F5E5A" stroke-width="0.5"/>
<text x="340" y="47" font-family="sans-serif" font-size="13" font-weight="500" fill="#2C2C2A" text-anchor="middle">你的核心诉求?</text>
<rect x="40" y="120" width="180" height="56" rx="8" fill="#EEEDFE" stroke="#534AB7" stroke-width="0.5"/>
<text x="130" y="144" font-family="sans-serif" font-size="12" font-weight="500" fill="#3C3489" text-anchor="middle">要 AI 守工程纪律</text>
<text x="130" y="162" font-family="sans-serif" font-size="11" fill="#5F5E5A" text-anchor="middle">superpowers</text>
<rect x="250" y="120" width="180" height="56" rx="8" fill="#E1F5EE" stroke="#0F6E56" stroke-width="0.5"/>
<text x="340" y="144" font-family="sans-serif" font-size="12" font-weight="500" fill="#085041" text-anchor="middle">要一站式全能</text>
<text x="340" y="162" font-family="sans-serif" font-size="11" fill="#5F5E5A" text-anchor="middle">everything-claude-code</text>
<rect x="460" y="120" width="180" height="56" rx="8" fill="#FAEEDA" stroke="#854F0B" stroke-width="0.5"/>
<text x="550" y="144" font-family="sans-serif" font-size="12" font-weight="500" fill="#633806" text-anchor="middle">解决单一痛点</text>
<text x="550" y="162" font-family="sans-serif" font-size="11" fill="#5F5E5A" text-anchor="middle">caveman / trailofbits</text>
<line x1="300" y1="64" x2="150" y2="118" stroke="#888780" stroke-width="1.5" marker-end="url(#dec-arrow)"/>
<line x1="340" y1="64" x2="340" y2="118" stroke="#888780" stroke-width="1.5" marker-end="url(#dec-arrow)"/>
<line x1="380" y1="64" x2="535" y2="118" stroke="#888780" stroke-width="1.5" marker-end="url(#dec-arrow)"/>
<rect x="140" y="200" width="400" height="30" rx="8" fill="#E6F1FB" stroke="#185FA5" stroke-width="0.5"/>
<text x="340" y="220" font-family="sans-serif" font-size="12" fill="#0C447C" text-anchor="middle">学写法:anthropics/skills + mattpocock/skills</text>
</svg>

给严肃后端 / 团队开发的一套推荐组合:

| 目的 | 选择 |
|---|---|
| 让 AI 守工程纪律 | superpowers(方法论底座) |
| 补齐具体能力 | 从 ECC 或官方 skills 里按需挑,别全量装 |
| 学标准写法 | anthropics/skills + mattpocock/skills |
| 安全审计 | trailofbits/skills |
| 淘更多现成 skill | awesome-claude-skills 当目录 |

## 一个绕不开的提醒:装之前先审计

高 star 不等于安全。第三方大合集里的 skill 良莠不齐,且 SKILL.md 常携带可执行脚本——它们能读你的文件、跑你的命令。

**安装前务必过一遍安全审计**:看清 SKILL.md 及 scripts 目录里到底会执行什么,尤其警惕联网上传、读取密钥、删除文件这类动作。star 数只代表流行度,不代表它不会在你机器上干坏事。

选 skill 的心法和选依赖一样:**先看它解决什么问题,再看它可能带来什么风险**。方法论包解决"做得对",能力包解决"做得了",而审计这一步,决定你敢不敢把机器交给它。

## 参考文献

| # | 来源 | 标题 / 用途 |
|---|---|---|
| 1 | [obra/superpowers](https://github.com/obra/superpowers) | superpowers 仓库、14 个 skill、支持平台、七步管线 |
| 2 | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) | ECC 仓库、skill/agent 数量、AgentShield 安全审计 |
| 3 | [anthropics/skills](https://github.com/anthropics/skills) | Anthropic 官方 skill、office 能力、格式参考 |
| 4 | [mattpocock/skills](https://github.com/mattpocock/skills) | SKILL.md 格式参考实现 |
| 5 | [garrytan/gstack](https://github.com/garrytan/gstack) | 覆盖执行/设计/工程/文档/QA 的配置 |
| 6 | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 生产级 agent 工程技能 |
| 7 | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | AI 回复压缩、token 节省 |
| 8 | [trailofbits/skills](https://github.com/trailofbits/skills) | 安全审计技能包 |
| 9 | [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) | 1000+ skill 目录 |
| 10 | [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | 权威 awesome-list(仅收 1K+ star) |

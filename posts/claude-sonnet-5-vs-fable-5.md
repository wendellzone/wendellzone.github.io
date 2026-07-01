---
title: Sonnet 5 vs Fable 5 vs Sonnet 4.7：三档 Claude 选型指南
date: 2026-07-01
tags: [Claude, AI模型, 选型]
summary: Anthropic 同日发布 Sonnet 5 并解禁 Fable 5，本文对比三档 Claude 模型的能力、价格与安全机制，给出选型决策。
---

今天（2026年7月1日）Anthropic 一口气干了两件大事：发布中端新主力 **Claude Sonnet 5**，同时宣布旗舰 **Fable 5** 全球解禁、明日恢复访问。

这一下把三档 Claude 模型同时摆上了桌面：

- **Sonnet 4.7**（2026-04-22）：上一代中端基线
- **Sonnet 5**（2026-07-01）：新一代中端主力，agentic 能力逼近 Opus 旗舰
- **Fable 5**（2026-06-09）：Mythos 级旗舰，能力天花板但贵且带安全降权

本文不堆发布会通稿，直接给同行工程师一份选型指南：三者在能力、价格、安全机制上的真实差距，以及什么场景该用哪个。

## 一、先理清三档模型在 Anthropic 序列里的位置

Anthropic 当前模型体系按能力从高到低分四档：

| 档位 | 代表模型 | 定位 | 访问范围 |
|---|---|---|---|
| 神话级（受限） | Mythos 5 | 取消部分安全限制，最强网络安全能力 | 仅政府/关键基础设施 |
| 神话级（公开） | Fable 5 | Mythos 5 + 安全分类器，降权限版 | 全球解禁，7月2日恢复 |
| 旗舰 | Opus 4.8 | 日常旗舰标杆 | 全平台开放 |
| 中端主力 | Sonnet 5（新）/ Sonnet 4.7（旧） | 高频工作流默认选型 | 全平台开放 |
| 轻量 | Haiku 5 | 低延迟、低成本 | 全平台开放 |

几个关键关系要先记牢：

- **Fable 5 ≠ 普通旗舰**，它是"被降权限的 Mythos 级"。底层是 Mythos 5，外层套了分类器，敏感查询自动转给 Opus 4.8。
- **Sonnet 5 的对标不是 Fable 5**，而是 Opus 4.8——官方反复强调它在 agentic 任务上"逼近旗舰"，价格只有 Opus 的 60%。
- **Sonnet 4.7 是过渡版**，公开 benchmark 数据有限，官方主推的对比基线其实是 Sonnet 4.6。下文涉及上一代数据，以 Sonnet 4.6 作为"上一代中端"的近似参照。

下面这张图把三者放进完整体系里看更清楚：

<svg viewBox="0 0 680 420" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
<rect x="0" y="0" width="680" height="420" fill="#fafafa"/>
<text x="340" y="32" font-family="sans-serif" font-size="16" font-weight="700" fill="#1f2937" text-anchor="middle">Anthropic Claude 模型分层（2026-07）</text>
<text x="340" y="52" font-family="sans-serif" font-size="11" fill="#6b7280" text-anchor="middle">从轻量到神话级，能力 ↑ 价格 ↑ 访问限制 ↑</text>
<line x1="180" y1="75" x2="180" y2="395" stroke="#e5e7eb" stroke-width="1"/>
<line x1="180" y1="395" x2="650" y2="395" stroke="#e5e7eb" stroke-width="1"/>
<text x="60" y="395" font-family="sans-serif" font-size="9" fill="#9ca3af" text-anchor="middle">能力低</text>
<text x="640" y="395" font-family="sans-serif" font-size="9" fill="#9ca3af" text-anchor="middle">能力高</text>
<rect x="195" y="80" width="200" height="34" rx="4" fill="#8b5cf6" opacity="0.9"/>
<text x="205" y="102" font-family="sans-serif" font-size="12" font-weight="700" fill="#ffffff">Mythos 5</text>
<text x="385" y="102" font-family="sans-serif" font-size="10" fill="#ffffff" text-anchor="end">受限访问 · 政府关键设施</text>
<rect x="195" y="124" width="300" height="34" rx="4" fill="#ef4444" opacity="0.9"/>
<text x="205" y="146" font-family="sans-serif" font-size="12" font-weight="700" fill="#ffffff">Fable 5</text>
<text x="485" y="146" font-family="sans-serif" font-size="10" fill="#ffffff" text-anchor="end">$10/$50 · 降权限神话级</text>
<rect x="195" y="168" width="260" height="34" rx="4" fill="#3b82f6" opacity="0.9"/>
<text x="205" y="190" font-family="sans-serif" font-size="12" font-weight="700" fill="#ffffff">Opus 4.8</text>
<text x="445" y="190" font-family="sans-serif" font-size="10" fill="#ffffff" text-anchor="end">$5/$25 · 日常旗舰标杆</text>
<rect x="195" y="212" width="230" height="34" rx="4" fill="#10b981"/>
<text x="205" y="234" font-family="sans-serif" font-size="12" font-weight="700" fill="#ffffff">Sonnet 5</text>
<text x="415" y="234" font-family="sans-serif" font-size="10" fill="#ffffff" text-anchor="end">$2-3/$10-15 · 新中端主力</text>
<rect x="345" y="222" width="38" height="14" rx="3" fill="#fbbf24"/>
<text x="364" y="232" font-family="sans-serif" font-size="9" font-weight="700" fill="#1f2937" text-anchor="middle">NEW</text>
<rect x="195" y="256" width="200" height="34" rx="4" fill="#9ca3af" opacity="0.85"/>
<text x="205" y="278" font-family="sans-serif" font-size="12" font-weight="700" fill="#ffffff">Sonnet 4.7</text>
<text x="385" y="278" font-family="sans-serif" font-size="10" fill="#ffffff" text-anchor="end">$3/$15 · 上一代中端</text>
<rect x="195" y="300" width="120" height="34" rx="4" fill="#cbd5e1" opacity="0.9"/>
<text x="205" y="322" font-family="sans-serif" font-size="12" font-weight="700" fill="#475569">Haiku 5</text>
<text x="305" y="322" font-family="sans-serif" font-size="10" fill="#475569" text-anchor="end">低成本轻量</text>
<text x="340" y="380" font-family="sans-serif" font-size="10" fill="#6b7280" text-anchor="middle">条长 ≈ 能力定位 · Sonnet 5 已成免费/Pro 默认模型</text>
</svg>

## 二、能力横评：benchmark 摆数据

直接上核心指标，三档模型 + Opus 4.8 旗舰参照：

| 基准 | Sonnet 4.6（旧中端近似） | Sonnet 5（新中端） | Opus 4.8（旗舰参照） |
|---|---|---|---|
| SWE-bench Pro（agentic 编程） | 58.1% | **63.2%** | 69.2% |
| SWE-bench Verified | 80.8%* | **92.4%** | — |
| OSWorld-Verified（电脑操控） | 78.5% | **81.2%** | 83.4% |
| GDPval-AA v2（知识工作） | — | **1618** | 1615 |
| Humanity's Last Exam（无工具） | 34.6% | **43.2%** | 49.8% |
| Humanity's Last Exam（开工具） | — | **57.4%** | — |
| CursorBench 3.1 | 49% | **57%** | — |

*Opus 4.6 数据，作参照。

几个值得关注的信号：

- Sonnet 5 在 **GDPval-AA v2** 上 1618 分，反超 Opus 4.8 的 1615——这是中端模型在单项上压过旗舰的少见案例。
- **开工具后的 HLE** 从 43.2% 跳到 57.4%，已贴近 Opus 4.8（49.8% 无工具）。agentic 场景下，工具调用红利比裸模型能力更关键。
- SWE-bench Verified 92.4% 超过 Opus 4.6（80.8%），但注意 Verified 和 Pro 是不同难度档，Pro 才是 agentic 真实场景。

Fable 5 没进这张表，原因有二：它和 Opus 4.8 不在同一评测口径；它的强项是**长周期、多步骤、高复杂度**任务，短基准测不出代差。Stripe 那个案例更有说服力——5000 万行 Ruby 代码库，一天完成原本需要整个团队两个月的迁移。这种任务 Sonnet 5 现在还接不动。

<svg viewBox="0 0 680 380" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
<rect x="0" y="0" width="680" height="380" fill="#fafafa"/>
<text x="340" y="30" font-family="sans-serif" font-size="16" font-weight="700" fill="#1f2937" text-anchor="middle">核心 Benchmark 对比</text>
<text x="340" y="50" font-family="sans-serif" font-size="11" fill="#6b7280" text-anchor="middle">Sonnet 4.6 旧中端 · Sonnet 5 新中端 · Opus 4.8 旗舰</text>
<line x1="120" y1="80" x2="120" y2="340" stroke="#9ca3af" stroke-width="1"/>
<line x1="120" y1="340" x2="640" y2="340" stroke="#9ca3af" stroke-width="1"/>
<text x="115" y="84" font-family="sans-serif" font-size="9" fill="#9ca3af" text-anchor="end">100</text>
<text x="115" y="152" font-family="sans-serif" font-size="9" fill="#9ca3af" text-anchor="end">75</text>
<text x="115" y="220" font-family="sans-serif" font-size="9" fill="#9ca3af" text-anchor="end">50</text>
<text x="115" y="288" font-family="sans-serif" font-size="9" fill="#9ca3af" text-anchor="end">25</text>
<text x="115" y="344" font-family="sans-serif" font-size="9" fill="#9ca3af" text-anchor="end">0</text>
<line x1="120" y1="152" x2="640" y2="152" stroke="#e5e7eb" stroke-width="1" stroke-dasharray="3,3"/>
<line x1="120" y1="220" x2="640" y2="220" stroke="#e5e7eb" stroke-width="1" stroke-dasharray="3,3"/>
<line x1="120" y1="288" x2="640" y2="288" stroke="#e5e7eb" stroke-width="1" stroke-dasharray="3,3"/>
<text x="180" y="358" font-family="sans-serif" font-size="11" font-weight="600" fill="#475569" text-anchor="middle">SWE-bench Pro</text>
<text x="300" y="358" font-family="sans-serif" font-size="11" font-weight="600" fill="#475569" text-anchor="middle">OSWorld</text>
<text x="420" y="358" font-family="sans-serif" font-size="11" font-weight="600" fill="#475569" text-anchor="middle">HLE(开工具)</text>
<text x="540" y="358" font-family="sans-serif" font-size="11" font-weight="600" fill="#475569" text-anchor="middle">CursorBench</text>
<rect x="158" y="182" width="20" height="158" fill="#9ca3af" opacity="0.85"/>
<text x="168" y="176" font-family="sans-serif" font-size="9" fill="#6b7280" text-anchor="middle">58.1</text>
<rect x="182" y="169" width="20" height="171" fill="#10b981"/>
<text x="192" y="163" font-family="sans-serif" font-size="9" font-weight="700" fill="#10b981" text-anchor="middle">63.2</text>
<rect x="206" y="153" width="20" height="187" fill="#3b82f6" opacity="0.85"/>
<text x="216" y="147" font-family="sans-serif" font-size="9" fill="#3b82f6" text-anchor="middle">69.2</text>
<rect x="278" y="127" width="20" height="213" fill="#9ca3af" opacity="0.85"/>
<text x="288" y="121" font-family="sans-serif" font-size="9" fill="#6b7280" text-anchor="middle">78.5</text>
<rect x="302" y="120" width="20" height="220" fill="#10b981"/>
<text x="312" y="114" font-family="sans-serif" font-size="9" font-weight="700" fill="#10b981" text-anchor="middle">81.2</text>
<rect x="326" y="114" width="20" height="226" fill="#3b82f6" opacity="0.85"/>
<text x="336" y="108" font-family="sans-serif" font-size="9" fill="#3b82f6" text-anchor="middle">83.4</text>
<rect x="398" y="247" width="20" height="93" fill="#9ca3af" opacity="0.85"/>
<rect x="422" y="185" width="20" height="155" fill="#10b981"/>
<text x="432" y="179" font-family="sans-serif" font-size="9" font-weight="700" fill="#10b981" text-anchor="middle">57.4</text>
<rect x="446" y="205" width="20" height="135" fill="#3b82f6" opacity="0.85"/>
<rect x="518" y="208" width="20" height="132" fill="#9ca3af" opacity="0.85"/>
<text x="528" y="202" font-family="sans-serif" font-size="9" fill="#6b7280" text-anchor="middle">49</text>
<rect x="542" y="186" width="20" height="154" fill="#10b981"/>
<text x="552" y="180" font-family="sans-serif" font-size="9" font-weight="700" fill="#10b981" text-anchor="middle">57</text>
<rect x="40" y="75" width="14" height="14" fill="#9ca3af" opacity="0.85"/>
<text x="60" y="86" font-family="sans-serif" font-size="10" fill="#475569">Sonnet 4.6/4.7</text>
<rect x="40" y="95" width="14" height="14" fill="#10b981"/>
<text x="60" y="106" font-family="sans-serif" font-size="10" font-weight="700" fill="#1f2937">Sonnet 5（新）</text>
<rect x="40" y="115" width="14" height="14" fill="#3b82f6" opacity="0.85"/>
<text x="60" y="126" font-family="sans-serif" font-size="10" fill="#475569">Opus 4.8 旗舰</text>
</svg>

## 三、价格与成本：差的不只是标价

API 定价三档拉开明显：

| 模型 | 输入（$/M token） | 输出（$/M token） | 备注 |
|---|---|---|---|
| Fable 5 | 10 | 50 | 旗舰级，不到 Mythos Preview 一半 |
| Opus 4.8 | 5 | 25 | 旗舰标杆 |
| Sonnet 5（优惠期，至8/31） | 2 | 10 | Opus 4.8 的约 40% |
| Sonnet 5（优惠后） | 3 | 15 | Opus 4.8 的约 60% |
| Sonnet 4.7 | 3 | 15 | 与 Sonnet 5 优惠后持平 |

定价之外，三个变量更影响真实账单：

- **effort 档位**：Sonnet 5 在 high/xhigh/max 档用更低成本拿到接近 Opus 4.8 的效果，部分档位甚至更优。
- **token 效率**：Fable 5 在 Cognition FrontierCode 上 token 效率领先，复杂任务总 token 数更少，能抵消一部分单价差。
- **缓存与上下文**：三者都支持 1M context，长 agent 任务上下文复用率高的场景，边际成本下降明显。

一句话：**看单价 Fable 5 是 Sonnet 5 的 5 倍，但按"完成任务的总成本"算，差距会被 token 效率和能力密度收窄。** 成本敏感的批量 agent 工作流，仍然优先 Sonnet 5。

## 四、安全与可用性：Fable 5 的"降权限"机制

Fable 5 最特别的是它的安全分流。底层 Mythos 5 在网络安全、生物、化学上能力超出 Anthropic 自设安全阈值，直接放开有滥用风险。于是 Fable 5 加了一层分类器：

| 触发主题 | 命中后行为 |
|---|---|
| 网络安全 | 转交 Opus 4.8 响应 |
| 生物学 | 转交 Opus 4.8 响应 |
| 化学 | 转交 Opus 4.8 响应 |
| 蒸馏尝试（批量抓取模型输出） | 转交 Opus 4.8 响应 |
| 加速前沿 AI 开发 | 转交 Opus 4.8 响应 |

官方说法是平均不到 5% 的 session 会触发，但分类器偏保守，偶尔会误伤无害请求。这个机制对企业部署有两层影响：

- **合规利好**：敏感领域自动降级，等于内置了一道护栏，安全审计好讲。
- **稳定性隐患**：同一个应用里用户可能突然拿到不同模型的回复，体验割裂；分类器是黑盒，难调试。

<svg viewBox="0 0 680 300" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
<defs>
<marker id="fb-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
<path d="M0,0 L10,5 L0,10 z" fill="#6b7280"/>
</marker>
</defs>
<rect x="0" y="0" width="680" height="300" fill="#fafafa"/>
<text x="340" y="28" font-family="sans-serif" font-size="16" font-weight="700" fill="#1f2937" text-anchor="middle">Fable 5 安全分流机制</text>
<rect x="40" y="120" width="120" height="50" rx="6" fill="#ffffff" stroke="#9ca3af" stroke-width="1.5"/>
<text x="100" y="142" font-family="sans-serif" font-size="11" font-weight="700" fill="#1f2937" text-anchor="middle">用户请求</text>
<text x="100" y="158" font-family="sans-serif" font-size="9" fill="#6b7280" text-anchor="middle">Fable 5 入口</text>
<rect x="240" y="120" width="140" height="50" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
<text x="310" y="142" font-family="sans-serif" font-size="11" font-weight="700" fill="#92400e" text-anchor="middle">安全分类器</text>
<text x="310" y="158" font-family="sans-serif" font-size="9" fill="#92400e" text-anchor="middle">5 类主题检测</text>
<line x1="160" y1="145" x2="234" y2="145" stroke="#6b7280" stroke-width="1.5" marker-end="url(#fb-arrow)"/>
<text x="310" y="200" font-family="sans-serif" font-size="10" fill="#6b7280" text-anchor="middle">是否命中敏感主题？</text>
<path d="M 380 145 Q 440 145 460 100" fill="none" stroke="#10b981" stroke-width="1.5" marker-end="url(#fb-arrow)"/>
<path d="M 380 145 Q 440 145 460 190" fill="none" stroke="#ef4444" stroke-width="1.5" marker-end="url(#fb-arrow)"/>
<text x="430" y="105" font-family="sans-serif" font-size="10" font-weight="700" fill="#10b981">否（约 95%）</text>
<text x="430" y="185" font-family="sans-serif" font-size="10" font-weight="700" fill="#ef4444">是（约 5%）</text>
<rect x="470" y="65" width="180" height="55" rx="6" fill="#d1fae5" stroke="#10b981" stroke-width="1.5"/>
<text x="560" y="88" font-family="sans-serif" font-size="11" font-weight="700" fill="#065f46" text-anchor="middle">Fable 5 正常响应</text>
<text x="560" y="104" font-family="sans-serif" font-size="9" fill="#065f46" text-anchor="middle">Mythos 级完整能力</text>
<rect x="470" y="170" width="180" height="55" rx="6" fill="#fee2e2" stroke="#ef4444" stroke-width="1.5"/>
<text x="560" y="193" font-family="sans-serif" font-size="11" font-weight="700" fill="#991b1b" text-anchor="middle">转交 Opus 4.8</text>
<text x="560" y="209" font-family="sans-serif" font-size="9" fill="#991b1b" text-anchor="middle">用户被通知模型切换</text>
<text x="340" y="265" font-family="sans-serif" font-size="10" fill="#6b7280" text-anchor="middle">命中主题：网络安全 · 生物学 · 化学 · 蒸馏 · 前沿 AI 开发</text>
<text x="340" y="282" font-family="sans-serif" font-size="10" fill="#9ca3af" text-anchor="middle">6/12 曾被暂停 · 7/1 商务部解禁 · 7/2 恢复访问</text>
</svg>

还有一段插曲值得记一笔：Fable 5 6月9日发布，6月12日就被 Anthropic 自己暂停访问（官方未详述原因），随后被美国商务部纳入出口管制。直到今天（7月1日）商务部长 Lutnick 签字解禁，7月2日恢复全球访问。这 18 天里不少依赖 Fable 5 的 vibe coding 流水线被迫切回 Opus 4.8。Sonnet 5 选在解禁同日发布，时机微妙。

Sonnet 5 和 Sonnet 4.7 没有这套分流机制，企业部署链路更简单可预测。

## 五、选型决策：什么场景用哪个

落到工程决策，给一张选型表：

| 场景 | 推荐模型 | 理由 |
|---|---|---|
| 日常 coding、agent 工作流、成本敏感的批量任务 | **Sonnet 5** | agentic 逼近旗舰，价格 60%，1M 上下文够用 |
| 超长周期、高复杂度任务（大型代码库迁移、跨系统自动化） | **Fable 5** | 长任务代差明显，token 效率高 |
| 视觉 SOTA 需求（截图重建代码、复杂图表解析） | **Fable 5** | 视觉能力断档领先 |
| 已在用 Sonnet 4.7 且无强 agentic 需求 | **迁到 Sonnet 5** | 成本持平、能力跳升，无理由留旧版 |
| 网络安全防御、生物科研（受信机构） | **Mythos 5** | 唯一放开相关能力的通道 |
| 纯聊天、低延迟问答 | Haiku 5 | 别用 Sonnet 5 杀鸡 |

三条决策原则收尾：

1. **预算够 + 任务长 + 能接受偶尔被分流** → Fable 5，能力上限最高。
2. **成本敏感 + 高频 agent + 要稳定** → Sonnet 5，新一代默认选型。
3. **Sonnet 4.7** → 没有留它的理由，趁迁移成本持平赶紧换 Sonnet 5。

Sonnet 5 今天起已是 Claude 免费版和 Pro 用户的默认模型，Cursor 也已上线。如果你的 agent 工作流还在跑 Sonnet 4.7，今天是个该动手迁移的日子。

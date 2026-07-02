---
title: 走近Fable 5
date: 2026-07-02
tags: [AI, 大模型, Anthropic]
summary: Anthropic 首个公开 Mythos 级模型，发布三天遭出口管制封禁，18 天后解禁。用数据拆解能力代差、安全分流与监管风波。
---

2026 年 6 月 9 日，Anthropic 发布了 Claude Fable 5——公司首个向公众开放的 **Mythos 级**模型。官方一句话定位："任务越长、越复杂，Fable 5 的优势就越大。"

但这个故事并不平滑：发布仅三天，它就被美国政府以国家安全为由紧急封禁，全球下架近三周后才解禁恢复。一篇关于 Fable 5 的介绍，绕不开能力、安全、监管三条线。下面用数据把这三条线串起来。

## 一、同源双轨：Fable 5 与 Mythos 5

Fable 5 不是独立模型，而是 Anthropic"同源双轨"策略的公开那一半。它和 Mythos 5 共享同一底层基础模型，差异只在安全护栏的开关。

| 维度 | Fable 5 | Mythos 5 |
|---|---|---|
| 定位 | 面向公众的 Mythos 级 | 定向开放，仅限合作伙伴/安全机构 |
| 安全护栏 | 搭载分类器，高危请求降级至 Opus 4.8 | 无额外限制，保留全部原生能力 |
| 访问范围 | 全球用户（解禁后） | Project Glasswing 计划，与美国政府共管 |
| 强项场景 | 编程、知识工作、视觉 | 网络安全、生物科研、零日漏洞挖掘 |
| 价格 | $10/$50 per M token | 同上 |

产品梯队排序很清晰：**Mythos 5 > Fable 5 > Opus 4.8 > Sonnet > Haiku**。Fable 5 是普通用户能接触到的能力天花板。它的前代是 2026 年 4 月发布的 Claude Mythos Preview——那个模型因能发现复杂网络安全漏洞而备受关注，但只定向开放。

<svg viewBox="0 0 680 400" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
<rect x="0" y="0" width="680" height="400" fill="#fafafa"/>
<text x="340" y="30" font-family="sans-serif" font-size="16" font-weight="700" fill="#1f2937" text-anchor="middle">Anthropic Claude 模型梯队（2026-07）</text>
<text x="340" y="50" font-family="sans-serif" font-size="11" fill="#6b7280" text-anchor="middle">能力 ↑ · 价格 ↑ · 访问限制 ↑</text>
<line x1="170" y1="70" x2="170" y2="370" stroke="#e5e7eb" stroke-width="1"/>
<line x1="170" y1="370" x2="660" y2="370" stroke="#e5e7eb" stroke-width="1"/>
<text x="60" y="370" font-family="sans-serif" font-size="9" fill="#9ca3af" text-anchor="middle">能力低</text>
<text x="650" y="370" font-family="sans-serif" font-size="9" fill="#9ca3af" text-anchor="middle">能力高</text>
<rect x="185" y="75" width="210" height="38" rx="4" fill="#8b5cf6" opacity="0.9"/>
<text x="195" y="99" font-family="sans-serif" font-size="12" font-weight="700" fill="#ffffff">Mythos 5</text>
<text x="385" y="99" font-family="sans-serif" font-size="10" fill="#ffffff" text-anchor="end">受限 · 政府共管</text>
<rect x="185" y="123" width="310" height="38" rx="4" fill="#ef4444" opacity="0.9"/>
<text x="195" y="147" font-family="sans-serif" font-size="12" font-weight="700" fill="#ffffff">Fable 5</text>
<text x="485" y="147" font-family="sans-serif" font-size="10" fill="#ffffff" text-anchor="end">$10/$50 · 降权限神话级</text>
<rect x="185" y="171" width="270" height="38" rx="4" fill="#3b82f6" opacity="0.9"/>
<text x="195" y="195" font-family="sans-serif" font-size="12" font-weight="700" fill="#ffffff">Opus 4.8</text>
<text x="445" y="195" font-family="sans-serif" font-size="10" fill="#ffffff" text-anchor="end">$5/$25 · 日常旗舰</text>
<rect x="185" y="219" width="230" height="38" rx="4" fill="#10b981"/>
<text x="195" y="243" font-family="sans-serif" font-size="12" font-weight="700" fill="#ffffff">Sonnet 5</text>
<text x="405" y="243" font-family="sans-serif" font-size="10" fill="#ffffff" text-anchor="end">$2-3/$10-15 · 中端主力</text>
<rect x="185" y="267" width="120" height="38" rx="4" fill="#cbd5e1" opacity="0.9"/>
<text x="195" y="291" font-family="sans-serif" font-size="12" font-weight="700" fill="#475569">Haiku 5</text>
<text x="295" y="291" font-family="sans-serif" font-size="10" fill="#475569" text-anchor="end">轻量</text>
<text x="340" y="355" font-family="sans-serif" font-size="10" fill="#6b7280" text-anchor="middle">条长 ≈ 能力定位 · Fable 5 是公众可用的能力天花板</text>
</svg>

数据源：Anthropic 官方发布公告（2026-06-09）、华尔街见闻、aitop100.cn 报道。

## 二、跑分一览：代差级领先

Fable 5 在编程能力上的提升最为显眼。SWE-Bench Pro 得分 **80.3%**，相比 Opus 4.8 的 69.2% 拉开 11 个百分点，相比 GPT 5.5 的 58.6% 高出 21.7 个百分点。

| 基准测试 | Fable 5 | Opus 4.8 | GPT 5.5 | Gemini 3.1 Pro |
|---|---|---|---|---|
| SWE-Bench Pro（编程） | **80.3%** | 69.2% | 58.6% | 54.2% |
| FrontierCode Diamond（生产级编码） | **29.3%** | 13.4% | 5.7% | — |
| Terminal-Bench 2.1 | **88.0%** | — | — | — |
| OSWorld（电脑操控） | **85.0%** | — | — | — |
| GDPval-AA（知识工作） | **1932** | — | — | — |
| Humanity's Last Exam（无工具） | **59.0%** | — | — | — |
| Humanity's Last Exam（含工具） | **64.5%** | — | — | — |
| ExploitBench（网络安全） | 78.0%* | 40.0% | — | — |
| Legal Agent Benchmark（法律） | **13.3%** | — | — | — |
| Blueprint-Bench 2（蓝图理解） | **38.6%** | — | — | 26.5% |

*ExploitBench 78.0% 为 Mythos 5 成绩；Fable 5 因安全分流在此项会降级。Mythos Preview 预览版为 69%。

几个值得注意的信号：

- **FrontierCode Diamond 差距最悬殊**：Fable 5 的 29.3% 是 Opus 4.8（13.4%）的两倍多，是 GPT 5.5（5.7%）的五倍以上。这项评测专门考验生产级代码库难题，最能体现"代差"。
- **文档图表理解提升 32%**，GDP.pdf 文档审阅基准比 Opus 4.8 高 7.3%。
- 视觉能力断档领先：能从复杂科学插图提取精确数据，仅凭截图重建网页源码，甚至独立通关"宝可梦火红"——以往模型需借助辅助框架才能做到。

数据源：Anthropic 官方发布公告、chooseai.net、aitop100.cn、sohu.com 报道（均为 2026-06-09/10）。

## 三、长任务为王：Stripe 与 IMC 的实战

跑分之外，两个真实案例更能说明 Fable 5 的价值定位。

**Stripe：5000 万行 Ruby，一天迁完。** 支付巨头 Stripe 在早期测试中，让 Fable 5 对一个 5000 万行的 Ruby 代码库做全量迁移。这项工作原本预估需要整支工程团队两个多月。Fable 5 用了一天。Stripe 的表述是"把数月工程压缩为数天"。

**IMC Trading：金融推理稳定性 100%。** 量化交易机构 IMC 反馈，Fable 5 在高级金融推理场景的输出稳定性达到 100%——多次重复结果完全一致，可替代核心团队高级分析师完成复杂投研任务。调用成本仅为原有人力的十分之一。

为什么长任务能拉开差距？三项底层能力支撑：

- **1M token 上下文窗口**：能在工作视野中保留 5000 万行代码库的有意义切片，这是以往模型无法维持的会话长度。
- **持久化文件记忆系统**：Anthropic 内部测试显示，该机制让 Fable 5 长任务性能比 Opus 4.8 高约 3 倍。普通模型"看了就忘"，Fable 5 会边看边写笔记并主动调用。
- **自适应思考 + effort 参数**：开发者可用 `effort="high"` 等参数动态调整推理资源投入，简单题不浪费算力，复杂题全力投入。

Lyzr CTO Fabian Hedin 的对比很直白："一年前需要上百条提示的应用，它现在一次就能完成。"OpenAI 前首席科学家 Andrej Karpathy 评价其"完全配得上大版本升级的跨越式进展"。

数据源：Anthropic 官方发布公告、claude5.ai、cloud.tencent.com.cn、toutiao.com 报道。

## 四、安全分流：5% 的代价

Fable 5 最特殊的设计是安全分类器。底层 Mythos 5 在网络安全、生物、化学上能力超出 Anthropic 自设安全阈值，直接放开有滥用风险。于是 Fable 5 加了一层护栏。

| 触发主题 | 命中后行为 |
|---|---|
| 网络安全 | 转交 Opus 4.8 响应 |
| 生物学 | 转交 Opus 4.8 响应 |
| 化学 | 转交 Opus 4.8 响应 |
| 模型蒸馏尝试（批量抓取输出） | 转交 Opus 4.8 响应 |
| 加速前沿 AI 开发 | 转交 Opus 4.8 响应 |

官方说法是平均**不到 5% 的 session** 会触发。但分类器调得偏保守，偶尔会误伤无害请求——Anthropic 自己承认"有时会拦截无害的查询"。配套的还有一项 **30 天客户数据保留政策**，专门用于研究和缓解越狱攻击，但这政策对企业客户有真实成本。

<svg viewBox="0 0 680 320" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg">
<defs>
<marker id="fb5-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
<path d="M0,0 L10,5 L0,10 z" fill="#6b7280"/>
</marker>
</defs>
<rect x="0" y="0" width="680" height="320" fill="#fafafa"/>
<text x="340" y="28" font-family="sans-serif" font-size="16" font-weight="700" fill="#1f2937" text-anchor="middle">Fable 5 安全分流机制</text>
<rect x="40" y="130" width="120" height="50" rx="6" fill="#ffffff" stroke="#9ca3af" stroke-width="1.5"/>
<text x="100" y="152" font-family="sans-serif" font-size="11" font-weight="700" fill="#1f2937" text-anchor="middle">用户请求</text>
<text x="100" y="168" font-family="sans-serif" font-size="9" fill="#6b7280" text-anchor="middle">Fable 5 入口</text>
<rect x="230" y="130" width="150" height="50" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
<text x="305" y="152" font-family="sans-serif" font-size="11" font-weight="700" fill="#92400e" text-anchor="middle">安全分类器</text>
<text x="305" y="168" font-family="sans-serif" font-size="9" fill="#92400e" text-anchor="middle">5 类主题检测</text>
<line x1="160" y1="155" x2="224" y2="155" stroke="#6b7280" stroke-width="1.5" marker-end="url(#fb5-arrow)"/>
<text x="305" y="210" font-family="sans-serif" font-size="10" fill="#6b7280" text-anchor="middle">是否命中敏感主题？</text>
<path d="M 380 155 Q 440 155 460 105" fill="none" stroke="#10b981" stroke-width="1.5" marker-end="url(#fb5-arrow)"/>
<path d="M 380 155 Q 440 155 460 200" fill="none" stroke="#ef4444" stroke-width="1.5" marker-end="url(#fb5-arrow)"/>
<text x="430" y="110" font-family="sans-serif" font-size="10" font-weight="700" fill="#10b981">否（约 95%）</text>
<text x="430" y="195" font-family="sans-serif" font-size="10" font-weight="700" fill="#ef4444">是（约 5%）</text>
<rect x="470" y="70" width="180" height="55" rx="6" fill="#d1fae5" stroke="#10b981" stroke-width="1.5"/>
<text x="560" y="93" font-family="sans-serif" font-size="11" font-weight="700" fill="#065f46" text-anchor="middle">Fable 5 正常响应</text>
<text x="560" y="109" font-family="sans-serif" font-size="9" fill="#065f46" text-anchor="middle">Mythos 级完整能力</text>
<rect x="470" y="180" width="180" height="55" rx="6" fill="#fee2e2" stroke="#ef4444" stroke-width="1.5"/>
<text x="560" y="203" font-family="sans-serif" font-size="11" font-weight="700" fill="#991b1b" text-anchor="middle">转交 Opus 4.8</text>
<text x="560" y="219" font-family="sans-serif" font-size="9" fill="#991b1b" text-anchor="middle">用户被通知模型切换</text>
<text x="340" y="275" font-family="sans-serif" font-size="10" fill="#6b7280" text-anchor="middle">命中主题：网络安全 · 生物学 · 化学 · 蒸馏 · 前沿 AI 开发</text>
<text x="340" y="293" font-family="sans-serif" font-size="10" fill="#9ca3af" text-anchor="middle">配套：30 天客户数据保留政策</text>
</svg>

数据源：Anthropic 官方发布公告、Anthropic 暂停访问声明（2026-06-12）。

## 五、18 天封禁：从发布到出口管制

Fable 5 的公开可用时间，第一段只有三天。这是一段值得记录的监管风波。

| 时间 | 事件 |
|---|---|
| 6月9日 | Anthropic 发布 Fable 5 与 Mythos 5 |
| 6月11日深夜 | 亚马逊（Anthropic 最大外部投资方，累计投资逾 130 亿美元）向白宫通报 Fable 5 安全防护绕过漏洞；当晚至少 5 家关联企业表达类似隐患 |
| 6月12日上午 | 白宫紧急召集财政部长、网络安全主管、幕僚长等内阁级官员磋商，越狱报告移交 NSA 审查 |
| 6月12日下午 | 白宫与 Anthropic CEO 阿莫代伊三轮电话交锋；阿莫代伊以"漏洞范围狭窄""GPT-5.5 也有类似问题"抗辩，拒绝主动下架 |
| 6月12日 17:21 ET | 收到商务部出口管制指令 |
| 6月12日晚 | Anthropic 全面关停 Fable 5 与 Mythos 5 全球访问 |
| 管制范围 | 覆盖美国境外一切目的地，穿透至美国境内所有外国人（含 Anthropic 外籍员工） |
| 6月下旬 | 先允许向部分"受信任"美国机构开放 Mythos 5 |
| 7月1日 | 商务部长 Lutnick 签字撤销出口管制 |
| 7月2日 | 全球恢复访问 |

关键争议点：Anthropic 认为政府发现的是"窄域、非通用越狱"——本质上是让模型读特定代码库并修复漏洞，这种能力其他公开模型（含 GPT-5.5）也具备。Anthropic 公开表态："如果这个标准推广到全行业，将实质上叫停所有前沿模型提供商的新模型部署。"

但政府的立场不同：Anthropic 长期把自身 AI 风险对标"核武器"并高调呼吁严苛监管，却在面临真实漏洞修复指令时推诿。这种言行悖离耗尽了白宫耐心。值得注意的是，同期 OpenAI 也应美国政府要求推迟了 GPT-5.6 的全面公开发布，暂只向少数审查过的合作伙伴开放。

OpenAI CEO Altman 在 X 上表态："全面安全测试并不是坏主意，我只是不喜欢由政府挑选客户。"这场风波标志着前沿 AI 正式成为受国家安全管控的"战略基础设施"。

数据源：Anthropic 暂停访问声明、路透社报道（经新浪/网易转载）、segg.sh.gov.cn 监管动态、chatsworthgroup.com 分析。

## 六、定价与定位：贵在哪里

Fable 5 的 API 定价是 Opus 4.8 的两倍，但 Anthropic 强调投入产出比。

| 模型 | 输入（$/M token） | 输出（$/M token） | 备注 |
|---|---|---|---|
| Fable 5 | 10 | 50 | 不到 Mythos Preview 一半 |
| Opus 4.8 | 5 | 25 | 日常旗舰标杆 |
| GPT 5.5 | 5 | 30 | 竞品参照 |
| Sonnet 5（优惠期至 8/31） | 2 | 10 | 中端主力 |

高价能成立的逻辑有三层：

- **能力上限**：长周期、高复杂度任务上代差明显，Stripe 把两个月团队工作压到一天。
- **Token 效率**：在 Cognition FrontierCode 评测上，Fable 5 即便在 medium effort 档也拿到前沿模型最高分——同样任务用更少 token 完成，部分抵消单价差。
- **IMC 的成本账**：调用成本仅为原有人力的十分之一，却能完成同质量的复杂投研任务。

一句判断：**看单价 Fable 5 贵，但按"完成任务的总成本"算，差距会被 token 效率和能力密度收窄。** 成本敏感的批量高频 agent 工作流，仍应优先中端模型。

数据源：Anthropic 官方发布公告、claude5.ai、toutiao.com 报道。

## 结语：能力、安全、监管的三角

Fable 5 的故事不是单纯的"模型变强了"。它同时是三件事的交汇：

- **能力的代差**——FrontierCode Diamond 上对 GPT 5.5 领先五倍，长任务能压到一天顶两月。
- **安全的妥协**——用 5% 的分流换 95% 的可用，代价是偶尔误伤和体验割裂。
- **监管的入场**——18 天封禁证明，前沿 AI 已是政府可直接叫停的战略基础设施。

Anthropic 在 Series H（2026年5月28日）以 $965B 估值融资 $65B，年化收入 $47B。Fable 5 能否撑起这个身价，取决于这三条线能否长期平衡。对工程团队而言，现在的结论很实际：长任务、视觉 SOTA、大型迁移，Fable 5 是当前最优选；高频成本敏感的 agent 工作流，中端模型仍是默认。

> **主要数据源汇总**：Anthropic 官方发布公告（2026-06-09）；Anthropic 暂停/恢复访问声明（2026-06-12 / 2026-07-01）；路透社报道（经新浪、网易转载）；segg.sh.gov.cn 国际投融资与贸易监管动态；chatsworthgroup.com 证券分析；chooseai.net、aitop100.cn、sohu.com、claude5.ai、cloud.tencent.com.cn、toutiao.com 等媒体二次报道。

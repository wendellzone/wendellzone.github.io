---
title: Sonnet 5 vs Opus 4.8：中端新主力对决旗舰标杆
date: 2026-07-02
tags: [Claude, AI模型, 选型]
summary: Sonnet 5 agentic 能力逼近 Opus 4.8、价格只有 60%。本文对比两者能力、价格与安全机制，给出选型决策。
---

昨天（2026年7月1日）Anthropic 发布 **Claude Sonnet 5**，官方反复强调一句：agentic 任务逼近旗舰 **Opus 4.8**，价格只有它的 60%。

这把一个老问题重新摆上桌面：当中端新主力已经能打到旗舰九成力，还要不要为 Opus 4.8 多付那 40%？

本文不堆发布会通稿，直接给同行工程师一份 Sonnet 5 vs Opus 4.8 的双模选型指南——能力、价格、什么场景该用哪个。

## 一、先理清两者在 Anthropic 体系里的位置

Anthropic 当前模型体系按能力从高到低分四档，Sonnet 5 和 Opus 4.8 相邻但不重叠：

| 档位 | 模型 | 定位 | 发布 |
|---|---|---|---|
| 神话级（受限） | Mythos 5 | 取消部分安全限制，最强网络安全能力 | 仅政府/关键基础设施 |
| 神话级（公开） | Fable 5 | Mythos 5 + 安全分类器，降权限版 | 2026-06-09 |
| 旗舰 | **Opus 4.8** | 日常旗舰标杆 | 2026-05-28 |
| 中端主力 | **Sonnet 5** | 高频工作流默认选型 | 2026-07-01 |
| 轻量 | Haiku 5 | 低延迟、低成本 | — |

两个关键关系先记牢：

- **Sonnet 5 的对标对象就是 Opus 4.8**，不是 Fable 5。官方 benchmark 全程拿 Sonnet 5 跟 Opus 4.8 比，价格对标也是 Opus 4.8。
- **Opus 4.8 仍是日常旗舰标杆**。Fable 5 虽然能力更强（底层是 Mythos 5），但有安全分流机制、价格更高、稳定性打折，不适合做通用旗舰对比的锚点。

下图把两者放进完整体系里看更清楚：

<svg viewBox="0 0 680 360" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg"><rect x="0" y="0" width="680" height="360" fill="#fafafa"/><text x="340" y="30" font-family="sans-serif" font-size="16" font-weight="700" fill="#1f2937" text-anchor="middle">Anthropic Claude 模型分层（2026-07）</text><text x="340" y="50" font-family="sans-serif" font-size="11" fill="#6b7280" text-anchor="middle">从轻量到神话级，能力 ↑ 价格 ↑ 访问限制 ↑</text><line x1="180" y1="70" x2="180" y2="335" stroke="#e5e7eb" stroke-width="1"/><line x1="180" y1="335" x2="650" y2="335" stroke="#e5e7eb" stroke-width="1"/><text x="60" y="335" font-family="sans-serif" font-size="9" fill="#9ca3af" text-anchor="middle">能力低</text><text x="640" y="335" font-family="sans-serif" font-size="9" fill="#9ca3af" text-anchor="middle">能力高</text><rect x="195" y="75" width="200" height="34" rx="4" fill="#8b5cf6" opacity="0.9"/><text x="205" y="97" font-family="sans-serif" font-size="12" font-weight="700" fill="#ffffff">Mythos 5</text><text x="385" y="97" font-family="sans-serif" font-size="10" fill="#ffffff" text-anchor="end">受限访问 · 政府关键设施</text><rect x="195" y="119" width="300" height="34" rx="4" fill="#ef4444" opacity="0.9"/><text x="205" y="141" font-family="sans-serif" font-size="12" font-weight="700" fill="#ffffff">Fable 5</text><text x="485" y="141" font-family="sans-serif" font-size="10" fill="#ffffff" text-anchor="end">$10/$50 · 降权限神话级</text><rect x="195" y="163" width="260" height="38" rx="4" fill="#3b82f6"/><text x="205" y="187" font-family="sans-serif" font-size="13" font-weight="700" fill="#ffffff">Opus 4.8</text><text x="445" y="187" font-family="sans-serif" font-size="10" fill="#ffffff" text-anchor="end">$5/$25 · 日常旗舰标杆</text><rect x="465" y="170" width="38" height="14" rx="3" fill="#fbbf24"/><text x="484" y="180" font-family="sans-serif" font-size="9" font-weight="700" fill="#1f2937" text-anchor="middle">对A</text><rect x="195" y="211" width="230" height="38" rx="4" fill="#10b981"/><text x="205" y="235" font-family="sans-serif" font-size="13" font-weight="700" fill="#ffffff">Sonnet 5</text><text x="415" y="235" font-family="sans-serif" font-size="10" fill="#ffffff" text-anchor="end">$2-3/$10-15 · 新中端主力</text><rect x="435" y="218" width="38" height="14" rx="3" fill="#fbbf24"/><text x="454" y="228" font-family="sans-serif" font-size="9" font-weight="700" fill="#1f2937" text-anchor="middle">NEW</text><rect x="195" y="255" width="120" height="34" rx="4" fill="#cbd5e1" opacity="0.9"/><text x="205" y="277" font-family="sans-serif" font-size="12" font-weight="700" fill="#475569">Haiku 5</text><text x="305" y="277" font-family="sans-serif" font-size="10" fill="#475569" text-anchor="end">低成本轻量</text><rect x="40" y="295" width="14" height="14" fill="#3b82f6"/><text x="60" y="306" font-family="sans-serif" font-size="10" font-weight="700" fill="#1f2937">Opus 4.8（本文主角 A）</text><rect x="220" y="295" width="14" height="14" fill="#10b981"/><text x="240" y="306" font-family="sans-serif" font-size="10" font-weight="700" fill="#1f2937">Sonnet 5（本文主角 B）</text></svg>

## 二、能力横评：benchmark 摆数据

直接上核心指标，双模正面对比：

| 基准 | Sonnet 5 | Opus 4.8 | 差距 |
|---|---|---|---|
| SWE-bench Pro（agentic 编程） | 63.2% | **69.2%** | -6.0pp |
| SWE-bench Verified | **92.4%** | —（Opus 4.6 为 80.8%） | Sonnet 5 反超旧旗舰 |
| OSWorld-Verified（电脑操控） | 81.2% | **83.4%** | -2.2pp |
| GDPval-AA v2（知识工作） | **1618** | 1615 | +3（反超） |
| Humanity's Last Exam（无工具） | 43.2% | **49.8%** | -6.6pp |
| Humanity's Last Exam（开工具） | **57.4%** | — | 开工具后逼近 |
| CursorBench 3.1 | 57% | —（同档位接近） | 高 effort 下贴平 |

几个值得关注的信号：

- **GDPval-AA v2 上 Sonnet 5 以 1618 反超 Opus 4.8 的 1615**——这是中端模型在单项上压过旗舰的少见案例。知识工作类 agent，Sonnet 5 不亏。
- **开工具后的 HLE** 从 43.2% 跳到 57.4%，已超过 Opus 4.8 无工具的 49.8%。agentic 场景下，工具调用红利比裸模型能力更关键。
- **SWE-bench Verified 92.4% 超过 Opus 4.6 的 80.8%**，但注意 Verified 和 Pro 是不同难度档，Pro 才是 agentic 真实场景。Pro 上 Opus 4.8 仍领先 6 个百分点。

简单说：**纯推理 Opus 4.8 仍占优，agentic + 工具调用场景 Sonnet 5 已经能咬住甚至反超。**

<svg viewBox="0 0 680 340" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg"><rect x="0" y="0" width="680" height="340" fill="#fafafa"/><text x="340" y="28" font-family="sans-serif" font-size="16" font-weight="700" fill="#1f2937" text-anchor="middle">核心 Benchmark：Sonnet 5 vs Opus 4.8</text><text x="340" y="48" font-family="sans-serif" font-size="11" fill="#6b7280" text-anchor="middle">数字为得分，越高越好</text><line x1="120" y1="75" x2="120" y2="300" stroke="#9ca3af" stroke-width="1"/><line x1="120" y1="300" x2="640" y2="300" stroke="#9ca3af" stroke-width="1"/><text x="115" y="79" font-family="sans-serif" font-size="9" fill="#9ca3af" text-anchor="end">100</text><text x="115" y="137" font-family="sans-serif" font-size="9" fill="#9ca3af" text-anchor="end">75</text><text x="115" y="195" font-family="sans-serif" font-size="9" fill="#9ca3af" text-anchor="end">50</text><text x="115" y="253" font-family="sans-serif" font-size="9" fill="#9ca3af" text-anchor="end">25</text><text x="115" y="304" font-family="sans-serif" font-size="9" fill="#9ca3af" text-anchor="end">0</text><line x1="120" y1="137" x2="640" y2="137" stroke="#e5e7eb" stroke-width="1" stroke-dasharray="3,3"/><line x1="120" y1="195" x2="640" y2="195" stroke="#e5e7eb" stroke-width="1" stroke-dasharray="3,3"/><line x1="120" y1="253" x2="640" y2="253" stroke="#e5e7eb" stroke-width="1" stroke-dasharray="3,3"/><text x="200" y="318" font-family="sans-serif" font-size="11" font-weight="600" fill="#475569" text-anchor="middle">SWE-bench Pro</text><text x="340" y="318" font-family="sans-serif" font-size="11" font-weight="600" fill="#475569" text-anchor="middle">OSWorld</text><text x="480" y="318" font-family="sans-serif" font-size="11" font-weight="600" fill="#475569" text-anchor="middle">HLE(无工具)</text><rect x="184" y="154" width="24" height="146" fill="#10b981"/><text x="196" y="148" font-family="sans-serif" font-size="9" font-weight="700" fill="#10b981" text-anchor="middle">63.2</text><rect x="212" y="140" width="24" height="160" fill="#3b82f6" opacity="0.9"/><text x="224" y="134" font-family="sans-serif" font-size="9" font-weight="700" fill="#3b82f6" text-anchor="middle">69.2</text><rect x="324" y="112" width="24" height="188" fill="#10b981"/><text x="336" y="106" font-family="sans-serif" font-size="9" font-weight="700" fill="#10b981" text-anchor="middle">81.2</text><rect x="352" y="107" width="24" height="193" fill="#3b82f6" opacity="0.9"/><text x="364" y="101" font-family="sans-serif" font-size="9" font-weight="700" fill="#3b82f6" text-anchor="middle">83.4</text><rect x="464" y="200" width="24" height="100" fill="#10b981"/><text x="476" y="194" font-family="sans-serif" font-size="9" font-weight="700" fill="#10b981" text-anchor="middle">43.2</text><rect x="492" y="184" width="24" height="116" fill="#3b82f6" opacity="0.9"/><text x="504" y="178" font-family="sans-serif" font-size="9" font-weight="700" fill="#3b82f6" text-anchor="middle">49.8</text><rect x="40" y="70" width="14" height="14" fill="#10b981"/><text x="60" y="81" font-family="sans-serif" font-size="10" font-weight="700" fill="#1f2937">Sonnet 5</text><rect x="140" y="70" width="14" height="14" fill="#3b82f6" opacity="0.9"/><text x="160" y="81" font-family="sans-serif" font-size="10" font-weight="700" fill="#1f2937">Opus 4.8</text></svg>

## 三、价格与成本：差的不只是标价

API 定价两档拉开明显：

| 模型 | 输入（$/M token） | 输出（$/M token） | 相对 Opus 4.8 |
|---|---|---|---|
| Opus 4.8 | 5 | 25 | 100% |
| Sonnet 5（优惠期，至8/31） | 2 | 10 | **约 40%** |
| Sonnet 5（优惠后） | 3 | 15 | 约 60% |

定价之外，三个变量更影响真实账单：

- **effort 档位**：Sonnet 5 在 high/xhigh/max 档用更低成本拿到接近 Opus 4.8 的效果，部分档位甚至更优。Cursor 官方给的 CursorBench 3.1 数据显示，Sonnet 5 high default 已经接近 Opus 4.8 high，但平均单任务成本更低。
- **token 效率**：Opus 4.8 在复杂任务上 token 效率略高，能抵消一部分单价差；但 Sonnet 5 的单价优势太大，多数场景仍是 Sonnet 5 总成本更低。
- **缓存与上下文**：两者都支持 1M context，长 agent 任务上下文复用率高的场景，边际成本下降明显。

一句话：**看单价 Sonnet 5 是 Opus 4.8 的 40%~60%，按"完成任务的总成本"算，Sonnet 5 在多数 agentic 场景仍是更省的那个。**

<svg viewBox="0 0 680 320" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg"><rect x="0" y="0" width="680" height="320" fill="#fafafa"/><text x="340" y="28" font-family="sans-serif" font-size="16" font-weight="700" fill="#1f2937" text-anchor="middle">价格 vs 能力：Sonnet 5 的性价比位置</text><line x1="80" y1="60" x2="80" y2="280" stroke="#9ca3af" stroke-width="1"/><line x1="80" y1="280" x2="640" y2="280" stroke="#9ca3af" stroke-width="1"/><text x="75" y="64" font-family="sans-serif" font-size="9" fill="#9ca3af" text-anchor="end">高</text><text x="75" y="284" font-family="sans-serif" font-size="9" fill="#9ca3af" text-anchor="end">低</text><text x="75" y="60" font-family="sans-serif" font-size="10" fill="#6b7280" text-anchor="end" transform="rotate(-90 75 60)">能力</text><text x="80" y="300" font-family="sans-serif" font-size="9" fill="#9ca3af" text-anchor="middle">低</text><text x="640" y="300" font-family="sans-serif" font-size="9" fill="#9ca3af" text-anchor="middle">高</text><text x="360" y="312" font-family="sans-serif" font-size="10" fill="#6b7280" text-anchor="middle">价格（输入+输出 $/M token）</text><line x1="80" y1="170" x2="640" y2="170" stroke="#e5e7eb" stroke-width="1" stroke-dasharray="3,3"/><line x1="360" y1="60" x2="360" y2="280" stroke="#e5e7eb" stroke-width="1" stroke-dasharray="3,3"/><rect x="200" y="130" width="24" height="24" rx="12" fill="#cbd5e1"/><text x="212" y="146" font-family="sans-serif" font-size="9" fill="#475569" text-anchor="middle">Haiku5</text><rect x="200" y="195" width="24" height="24" rx="12" fill="#10b981"/><text x="212" y="211" font-family="sans-serif" font-size="9" font-weight="700" fill="#ffffff" text-anchor="middle">S5</text><text x="212" y="230" font-family="sans-serif" font-size="9" font-weight="700" fill="#10b981" text-anchor="middle">Sonnet 5</text><rect x="490" y="85" width="24" height="24" rx="12" fill="#3b82f6"/><text x="502" y="101" font-family="sans-serif" font-size="9" font-weight="700" fill="#ffffff" text-anchor="middle">O4.8</text><text x="502" y="120" font-family="sans-serif" font-size="9" font-weight="700" fill="#3b82f6" text-anchor="middle">Opus 4.8</text><rect x="560" y="70" width="24" height="24" rx="12" fill="#ef4444" opacity="0.9"/><text x="572" y="86" font-family="sans-serif" font-size="9" font-weight="700" fill="#ffffff" text-anchor="middle">F5</text><text x="572" y="105" font-family="sans-serif" font-size="9" fill="#ef4444" text-anchor="middle">Fable 5</text><path d="M 212 207 Q 350 150 502 97" fill="none" stroke="#10b981" stroke-width="1.5" stroke-dasharray="4,3"/><text x="350" y="145" font-family="sans-serif" font-size="10" font-weight="700" fill="#10b981" text-anchor="middle">性价比优势区</text><text x="340" y="255" font-family="sans-serif" font-size="10" fill="#6b7280" text-anchor="middle">Sonnet 5：能力贴近 Opus 4.8，价格仅 40%~60%</text></svg>

## 四、选型决策：什么场景用哪个

落到工程决策，给一张选型表：

| 场景 | 推荐模型 | 理由 |
|---|---|---|
| 日常 coding、agent 工作流、成本敏感的批量任务 | **Sonnet 5** | agentic 逼近旗舰，价格 40%~60%，1M 上下文够用 |
| 高难度单步推理、纯数学/逻辑难题 | **Opus 4.8** | HLE 无工具领先 6.6pp，裸推理仍是旗舰强项 |
| 长周期、跨系统大型迁移任务 | **Opus 4.8** | 长任务上 Opus 稳定性更优（更高难度档有优势） |
| 视觉 SOTA 需求（截图重建代码、复杂图表解析） | **Opus 4.8** | 视觉能力仍是旗舰级 |
| 高频客服/问答、低延迟场景 | Haiku 5 | 别用 Sonnet 5 杀鸡 |
| 已在用 Opus 4.8 且预算充足 | **保持 Opus 4.8** | 旗舰能力天花板，省心 |
| 已在用 Sonnet 4.x 旧中端 | **迁到 Sonnet 5** | 能力跳升，成本持平或更低 |

三条决策原则收尾：

1. **预算够 + 任务难 + 要稳** → Opus 4.8，旗舰能力天花板，推理/视觉/长任务都占优。
2. **成本敏感 + 高频 agent + 工具调用密集** → Sonnet 5，新一代默认选型，agentic 场景已能咬住旗舰。
3. **判断分水岭**：任务是否依赖"裸模型推理能力"？是 → Opus 4.8；否（靠工具调用 + 多步骤）→ Sonnet 5。

Sonnet 5 今天起已是 Claude 免费版和 Pro 用户的默认模型，Cursor 也已上线。如果你的 agent 工作流还在跑旧中端，今天是个该动手迁移的日子；如果一直用 Opus 4.8，不妨拿一批真实任务跑 Sonnet 5 A/B，多数 agentic 场景你会惊喜。

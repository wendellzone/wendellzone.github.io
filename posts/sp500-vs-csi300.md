---
title: 指数生而不平等
date: 2026-07-02
tags: [投资, 指数, 标普500, 沪深300]
summary: 标普500 vs 沪深300：从编制机制、行业结构、龙头集中度、退市净化到估值折价，用数据拆解大A涨幅为什么没那么高。
---

同样是"宽基指数之王"，标普500和沪深300的境遇却像两个平行世界。

把时间拉到 20 年，两者年化收益几乎贴在一起——标普500约 8.9%、沪深300约 8.4%。但只要把窗口收窄到最近 10 年，差距立刻裂开到 10 个百分点：标普500年化 12.8%、沪深300仅 2.2%。近 15 年更悬殊：标普500年化 12.0%、沪深300只有 2.6%[1]。

<svg viewBox="0 0 680 380" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg"><rect width="680" height="380" fill="#ffffff"/><text x="340" y="30" text-anchor="middle" font-family="sans-serif" font-size="15" font-weight="bold" fill="#111827">标普500 vs 沪深300：不同时间窗口的年化收益率</text><text x="340" y="48" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#6b7280">价格指数年化收益（%），数据截至 2026 年初</text><line x1="80" y1="290" x2="640" y2="290" stroke="#9ca3af" stroke-width="1"/><line x1="80" y1="70" x2="640" y2="70" stroke="#e5e7eb" stroke-width="1" stroke-dasharray="3,3"/><line x1="80" y1="101.6" x2="640" y2="101.6" stroke="#e5e7eb" stroke-width="1" stroke-dasharray="3,3"/><line x1="80" y1="133" x2="640" y2="133" stroke="#e5e7eb" stroke-width="1" stroke-dasharray="3,3"/><line x1="80" y1="164.4" x2="640" y2="164.4" stroke="#e5e7eb" stroke-width="1" stroke-dasharray="3,3"/><line x1="80" y1="195.8" x2="640" y2="195.8" stroke="#e5e7eb" stroke-width="1" stroke-dasharray="3,3"/><line x1="80" y1="227.2" x2="640" y2="227.2" stroke="#e5e7eb" stroke-width="1" stroke-dasharray="3,3"/><line x1="80" y1="258.6" x2="640" y2="258.6" stroke="#e5e7eb" stroke-width="1" stroke-dasharray="3,3"/><text x="72" y="294" text-anchor="end" font-family="sans-serif" font-size="10" fill="#6b7280">0</text><text x="72" y="262" text-anchor="end" font-family="sans-serif" font-size="10" fill="#6b7280">2</text><text x="72" y="230" text-anchor="end" font-family="sans-serif" font-size="10" fill="#6b7280">4</text><text x="72" y="199" text-anchor="end" font-family="sans-serif" font-size="10" fill="#6b7280">6</text><text x="72" y="168" text-anchor="end" font-family="sans-serif" font-size="10" fill="#6b7280">8</text><text x="72" y="137" text-anchor="end" font-family="sans-serif" font-size="10" fill="#6b7280">10</text><text x="72" y="105" text-anchor="end" font-family="sans-serif" font-size="10" fill="#6b7280">12</text><text x="72" y="74" text-anchor="end" font-family="sans-serif" font-size="10" fill="#6b7280">14</text><rect x="149" y="89" width="42" height="201" fill="#dc2626"/><text x="170" y="82" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#dc2626">12.8%</text><rect x="197" y="255.5" width="42" height="34.5" fill="#16a34a"/><text x="218" y="249" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#16a34a">2.2%</text><rect x="336" y="101.6" width="42" height="188.4" fill="#dc2626"/><text x="357" y="95" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#dc2626">12.0%</text><rect x="384" y="249.2" width="42" height="40.8" fill="#16a34a"/><text x="405" y="243" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#16a34a">2.6%</text><rect x="523" y="150.3" width="42" height="139.7" fill="#dc2626"/><text x="544" y="144" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#dc2626">8.9%</text><rect x="571" y="158.1" width="42" height="131.9" fill="#16a34a"/><text x="592" y="152" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#16a34a">8.4%</text><text x="193" y="310" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#1f2937">过去 10 年</text><text x="380" y="310" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#1f2937">过去 15 年</text><text x="567" y="310" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#1f2937">过去 20 年</text><rect x="210" y="332" width="14" height="14" fill="#dc2626"/><text x="230" y="344" font-family="sans-serif" font-size="11" fill="#1f2937">标普500</text><rect x="410" y="332" width="14" height="14" fill="#16a34a"/><text x="430" y="344" font-family="sans-serif" font-size="11" fill="#1f2937">沪深300</text></svg>

[1]

这不是"运气"问题，而是两个指数从出生那天起，就被写进了不同的基因。下面用数据拆解：大A 的宽基为什么跑不动。

## 一、编制基因：优等生俱乐部 vs 年级前300名

先看两个指数怎么选股。一张表说清核心差异。

| 维度 | 沪深300 | 标普500 |
|---|---|---|
| 选股逻辑 | 总市值排名前 300 | 委员会筛选 + 行业均衡 |
| 盈利门槛 | 无硬性要求 | 连续 4 季度盈利为正 + 最近 1 季度为正 |
| 行业约束 | 无 | 各 GICS 行业权重匹配全市场 |
| 调整频率 | 半年 1 次 | 季度 1 次 |
| 权重计算 | 调整市值分级靠档 | 自由流通市值 |
| 年换手率 | 10%–20% | 5%–6% |

[2][3][4]

标普500像个"优等生俱乐部"。它不是简单按市值拉前 500 名，而是由指数委员会把关：必须是美国公司、市值达标（约 227 亿美元门槛）、连续盈利、自由流通比例 ≥ 0.5、流动性达标，还要保持行业代表性均衡。特斯拉为了满足盈利门槛，足足等了 10 年才被纳入[3]。

沪深300更像"年级前 300 名"。规则机械透明：剔除成交额后 50%，按总市值取前 300。不卡盈利，不卡行业，只要够大够活跃就能进[2]。

两套机制的直接后果：标普500每年换血 5–6%[3]，留下的多是穿越周期的龙头；沪深300每年换血 10–20%[4]，但不少是市值涨上去才被纳入、跌下来又被踢出的"高位接盘"。被动资金因此被反复拖拽，而非稳定沉淀在优质资产上。

## 二、行业引擎：科技收税 vs 金融扛旗

编制机制不同，最终沉淀成完全不同的行业结构。标普500由科技驱动，沪深300由金融扛旗。

<svg viewBox="0 0 680 320" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg"><rect width="680" height="320" fill="#ffffff"/><text x="340" y="28" text-anchor="middle" font-family="sans-serif" font-size="15" font-weight="bold" fill="#111827">行业权重分布对比（%）</text><text x="340" y="46" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#6b7280">标普500 vs 沪深300，2026 年最新口径</text><text x="90" y="108" text-anchor="end" font-family="sans-serif" font-size="12" font-weight="bold" fill="#1f2937">标普500</text><rect x="100" y="86" width="187.2" height="44" fill="#3b82f6"/><text x="193" y="112" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#ffffff">信息技术 36</text><rect x="287.2" y="86" width="67.6" height="44" fill="#dc2626"/><text x="321" y="112" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#ffffff">金融 13</text><rect x="354.8" y="86" width="62.4" height="44" fill="#16a34a"/><text x="386" y="112" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#ffffff">医疗 12</text><rect x="417.2" y="86" width="57.2" height="44" fill="#f59e0b"/><text x="445" y="112" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#ffffff">可选消费 11</text><rect x="474.4" y="86" width="46.8" height="44" fill="#06b6d4"/><text x="497" y="112" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#ffffff">通信 9</text><rect x="521.2" y="86" width="41.6" height="44" fill="#6b7280"/><text x="542" y="112" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#ffffff">工业 8</text><rect x="562.8" y="86" width="57.2" height="44" fill="#d1d5db"/><text x="591" y="112" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#6b7280">其他 11</text><text x="90" y="188" text-anchor="end" font-family="sans-serif" font-size="12" font-weight="bold" fill="#1f2937">沪深300</text><rect x="100" y="166" width="119.6" height="44" fill="#dc2626"/><text x="159" y="192" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="bold" fill="#ffffff">金融 23</text><rect x="219.6" y="166" width="88.4" height="44" fill="#6b7280"/><text x="263" y="192" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#ffffff">工业 17</text><rect x="308" y="166" width="78" height="44" fill="#3b82f6"/><text x="347" y="192" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#ffffff">信息技术 15</text><rect x="386" y="166" width="78" height="44" fill="#8b5cf6"/><text x="425" y="192" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#ffffff">主要消费 15</text><rect x="464" y="166" width="52" height="44" fill="#f59e0b"/><text x="490" y="192" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#ffffff">可选消费 10</text><rect x="516" y="166" width="52" height="44" fill="#16a34a"/><text x="542" y="192" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#ffffff">医药 10</text><rect x="568" y="166" width="52" height="44" fill="#d1d5db"/><text x="594" y="192" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#6b7280">其他 10</text><rect x="80" y="240" width="12" height="12" fill="#3b82f6"/><text x="96" y="250" font-family="sans-serif" font-size="10" fill="#1f2937">信息技术</text><rect x="170" y="240" width="12" height="12" fill="#dc2626"/><text x="186" y="250" font-family="sans-serif" font-size="10" fill="#1f2937">金融</text><rect x="240" y="240" width="12" height="12" fill="#16a34a"/><text x="256" y="250" font-family="sans-serif" font-size="10" fill="#1f2937">医疗/医药</text><rect x="330" y="240" width="12" height="12" fill="#f59e0b"/><text x="346" y="250" font-family="sans-serif" font-size="10" fill="#1f2937">可选消费</text><rect x="420" y="240" width="12" height="12" fill="#8b5cf6"/><text x="436" y="250" font-family="sans-serif" font-size="10" fill="#1f2937">主要消费</text><rect x="510" y="240" width="12" height="12" fill="#06b6d4"/><text x="526" y="250" font-family="sans-serif" font-size="10" fill="#1f2937">通信</text><rect x="580" y="240" width="12" height="12" fill="#6b7280"/><text x="596" y="250" font-family="sans-serif" font-size="10" fill="#1f2937">工业</text></svg>

[3][2]

标普500第一大权重是信息技术，占比约 36%[3]。前十大成分股里，英伟达、苹果、微软、Alphabet、亚马逊、Meta 清一色科技平台，合计权重已超 40%[5]。这些公司赚的是全球市场的钱。

沪深300第一大权重是金融，占比约 23%（早年一度达 35%）；信息技术仅约 15%，且多为硬件制造和软件服务，缺乏全球性平台[2]。

| | 标普500 | 沪深300 |
|---|---|---|
| 第一大行业 | 信息技术 36% | 金融 23% |
| 增长引擎 | 全球科技平台 | 银行 / 券商 / 地产 |
| 收入来源 | 全球化 | 内需为主 |

科技是长坡厚雪的复利生意，金融是强周期、重资产、受政策高度约束的生意。引擎不同，长期天花板自然不同。

## 三、谁在拉车：集中度与龙头效应

指数涨幅，本质是少数龙头拉的。两个指数的龙头集中度，差出一个量级。

标普500前十大成分股占比已升至 43%，超越 2000 年互联网泡沫时期的 33% 峰值[6]。前十大的科技板块 ROE 高达 35%，远超泡沫期 21%[6]。沪深300前十大合计仅约 23%，权重分散，缺乏单一扛旗者[2]。

| 标普500前三大 | 权重 | 沪深300前三大（示意） | 权重 |
|---|---|---|---|
| 英伟达 | ~7.2% | 贵州茅台 | ~5% |
| 苹果 | ~6.4% | 招商银行 | ~3% |
| 微软 | ~4.1% | 宁德时代 | ~2% |

[7][5]

更关键的是龙头质量。标普500的龙头是全球收税的科技垄断者——英伟达 ROE 约 109%、苹果约 141%、微软约 34%[8]。沪深300的龙头以银行、白酒、新能源为主，ROE 普遍在 15–30% 区间，且周期性更强[9]。

龙头集中度高本身是双刃剑：高盛首席美国股票策略师 David Kostin 警告，当前集中度水平下标普500未来十年年化回报率约为负 5%[6]。但过去十年的事实是：高集中度 + 高 ROE 龙头，跑赢了低集中度 + 周期龙头。

## 四、吐故纳新：退市率决定指数生命力

前三节讲的是"谁进来"，这一节讲"谁出去"。这才是两个指数长期分化的根本。

<svg viewBox="0 0 680 280" width="100%" style="max-width:680px;" xmlns="http://www.w3.org/2000/svg"><rect width="680" height="280" fill="#ffffff"/><text x="340" y="28" text-anchor="middle" font-family="sans-serif" font-size="15" font-weight="bold" fill="#111827">年退市率对比：美股 vs A股</text><text x="340" y="46" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#6b7280">2010 年以来平均年退市率（%）</text><line x1="80" y1="210" x2="640" y2="210" stroke="#9ca3af" stroke-width="1"/><line x1="80" y1="100" x2="640" y2="100" stroke="#e5e7eb" stroke-width="1" stroke-dasharray="3,3"/><line x1="80" y1="155" x2="640" y2="155" stroke="#e5e7eb" stroke-width="1" stroke-dasharray="3,3"/><text x="72" y="214" text-anchor="end" font-family="sans-serif" font-size="10" fill="#6b7280">0</text><text x="72" y="159" text-anchor="end" font-family="sans-serif" font-size="10" fill="#6b7280">4</text><text x="72" y="104" text-anchor="end" font-family="sans-serif" font-size="10" fill="#6b7280">8</text><text x="72" y="74" text-anchor="end" font-family="sans-serif" font-size="10" fill="#6b7280">12</text><rect x="190" y="107" width="100" height="103" fill="#2563eb"/><text x="240" y="100" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#2563eb">9.3%</text><text x="240" y="230" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#1f2937">美股</text><rect x="390" y="203" width="100" height="7" fill="#f59e0b"/><text x="440" y="196" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#f59e0b">0.6%</text><text x="440" y="230" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#1f2937">A股</text><text x="340" y="258" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#dc2626">差距约 15 倍</text></svg>

[10][11]

美股的退市机器常年高速运转：

- 2010 年以来平均年退市率约 9.3%，海通策略口径 7.1%[10][11]
- 2024 年退市率约 10%（551 家退市 / 5437 家上市公司）[9]
- 年均退市 / IPO 比率达 140%——退得比进得还多[10]
- 累计退市数是当前上市数的 3.45 倍，总退市率 345%[12]

A股的退市几乎是另一个极端：

- 当前年退市率不足 1%[10]
- 累计退市率仅 6%[12]
- 2024 年退市 52 家，已是历史新高[10]
- 从首次风险警示到真正退市，平均要 3.3 年[10]

| 指标 | 美股 | A股 |
|---|---|---|
| 年退市率 | ~9.3% | <1% |
| 累计退市率 | 345% | 6% |
| 退市 / IPO 比 | 140% | 远低于 100% |
| 主动退市占比 | 97.5%（并购 + 自愿） | ~12% |

退市率差异的本质是"指数能否自我净化"。标普500每年把表现不佳的公司清出去、换进新龙头，成分股越来越精；沪深300长期"只进不出"，低效公司沉淀在池子里，拖累整体 ROE 和成长性。

这正是标普500全收益长期年化 10.6%（1990–2024，盈利增长 6.3% + 分红回购 2.1%）能持续的根本——它不是一篮子不变的公司，而是一个不断换血的优胜者集合[13]。

## 五、估值的镜像：便宜不等于划算

到这里，一个反直觉的现象浮现：沪深300长期涨幅低，估值也长期低。便宜是不是机会？

| 估值指标 | 沪深300 | 标普500 |
|---|---|---|
| PE（TTM） | ~14.6 倍 | ~28 倍 |
| PB | ~1.5 倍 | ~5.4 倍 |
| 股息率 | ~2.8% | ~1.1% |
| 席勒 PE | — | ~39.6 倍（历史峰值区间） |
| PE 历史分位（近 20 年） | ~65% | >95% |

[9][13]

沪深300的 PE 只有标普500的一半，PB 不到三分之一，股息率却高一倍多。单看这些数字，沪深300"性价比"似乎远超标普500。但便宜有便宜的原因：

- **成长性折价**：标普500靠全球科技龙头的高增长消化高估值，沪深300缺乏同体量的成长引擎。
- **确定性折价**：美股回购常态化（标普500年回购规模数千亿美元[3]），A股分红虽在提升但回购仍少。
- **生态折价**：低退市率意味着池子里有更多低效公司，拉低整体质量。

便宜可以是机会，也可以是陷阱。当"便宜"源于结构性短板而非短期情绪，它就更接近价值陷阱而非安全边际。

## 生而平等是幻觉

指数生而不平等。

标普500从出生起就被设计成一台"优胜劣汰的复利机器"：委员会把关盈利、季度换血、行业均衡、全球科技龙头集中、9% 以上的年退市率持续净化。沪深300则更像"按市值排序的快照"：无盈利门槛、半年调整、金融主导、退市率不到 1%，自我净化能力弱。

20 年看两者接近，是因为都吃到了各自时代的红利；近 10 年 / 15 年差距拉到 10 个百分点，是因为美股的换血机器 + 科技龙头红利，撞上了 A 股的池子沉淀 + 周期股拖累。

大A 涨幅为什么没那么高？答案不在某一年的牛市熊市，而在这套从编制到退市的底层制度里。便宜本身不是买入理由，制度进化才是。

---

## 附录：标普500 五十六年全收益年度回报（1970–2025）

56 个完整年度摊开：**41 年正收益、15 年下跌**；最惨 2008 年 -37.00%（金融危机），最佳 1995 年 +37.58%。**红色为涨跌超 ±30% 的年份**（共 10 个）。56 年累计约 200 倍、全收益年化约 10.5%[14]。

| 年份 | 回报 | 年份 | 回报 | 年份 | 回报 | 年份 | 回报 |
|---|---|---|---|---|---|---|---|
| 1970 | +4.01% | 1984 | +6.27% | 1998 | +28.58% | 2012 | +16.00% |
| 1971 | +14.31% | 1985 | <span style="color:#dc2626">+31.73%</span> | 1999 | +21.04% | 2013 | <span style="color:#dc2626">+32.39%</span> |
| 1972 | +18.98% | 1986 | +18.67% | 2000 | -9.10% | 2014 | +13.69% |
| 1973 | -14.66% | 1987 | +5.25% | 2001 | -11.89% | 2015 | +1.38% |
| 1974 | -26.47% | 1988 | +16.61% | 2002 | -22.10% | 2016 | +11.96% |
| 1975 | <span style="color:#dc2626">+37.20%</span> | 1989 | <span style="color:#dc2626">+31.69%</span> | 2003 | +28.68% | 2017 | +21.83% |
| 1976 | +23.84% | 1990 | -3.10% | 2004 | +10.88% | 2018 | -4.38% |
| 1977 | -7.18% | 1991 | <span style="color:#dc2626">+30.47%</span> | 2005 | +4.91% | 2019 | <span style="color:#dc2626">+31.49%</span> |
| 1978 | +6.56% | 1992 | +7.62% | 2006 | +15.79% | 2020 | +18.40% |
| 1979 | +18.44% | 1993 | +10.08% | 2007 | +5.49% | 2021 | +28.71% |
| 1980 | <span style="color:#dc2626">+32.42%</span> | 1994 | +1.32% | 2008 | <span style="color:#dc2626">-37.00%</span> | 2022 | -18.11% |
| 1981 | -4.91% | 1995 | <span style="color:#dc2626">+37.58%</span> | 2009 | +26.46% | 2023 | +26.29% |
| 1982 | +21.55% | 1996 | +22.96% | 2010 | +15.06% | 2024 | +25.02% |
| 1983 | +22.56% | 1997 | <span style="color:#dc2626">+33.36%</span> | 2011 | +2.11% | 2025 | +17.88% |

---

本文不构成投资建议。

## 数据来源

| # | 来源 | 标题 / 用途 / 截至 |
|---|---|---|
| 1 | [雪球专栏](https://xueqiu.com/) | @6306568950 / @7083498723 历年收益率，截至 2026-01-02 |
| 2 | [中证指数公司](https://www.csindex.com.cn/) | 沪深300编制规则、行业权重、前十大成分股权重，2026 年 |
| 3 | [S&P Dow Jones Indices](https://www.spglobal.com/spdji/) | 标普500编制规则、行业权重、回购数据，2026 年 |
| 4 | 山西证券研究所《股票指数与被动投资》 | 编制方法对比表、年换手率 |
| 5 | [格隆汇《拆解标普500指数成分股》](https://gelonghui.com/live/2402195) | 前十大集中度 40%+，截至 2026-03-30 |
| 6 | [edgen.tech《标普500集中度达43%》](https://www.edgen.tech/news/post/sp-500-concentration-hits-43-exceeding-dot-com-peak-as-ai-reshapes-markets) | 集中度 43%、科技板块 ROE 35%、高盛警告，截至 2026-06 |
| 7 | [us500.com S&P 500 Companies By Weight](https://www.us500.com/tools/data/sp500-companies-by-weight) | 标普500前三大成分股权重 |
| 8 | westock 数据 | 标普500龙头 ROE（英伟达 / 苹果 / 微软），TTM 截至 2026-07-01 |
| 9 | Wind | 历年指数点位、估值数据、退市数、沪深300龙头 ROE，2026 年 |
| 10 | [国泰海通证券《股市制度比较研究系列2》](https://www.fxbaogao.com/detail/5151842) | 退市率数据、退市渠道占比、退市时长 |
| 11 | [海通策略李影/荀玉根研报](https://finance.sina.com.cn/stock/roll/2022-12-23/doc-imxxqhas1015770.shtml) | 退市率历史数据 |
| 12 | [东方财富《为什么美股5万点,而大a常年在3000点?》](https://caifuhao.eastmoney.com/news/20260207124112548294460) | 累计退市率 345% / 6% 对比，截至 2026-02 |
| 13 | [理杏仁](https://www.lixinger.com/) | 长期收益率分解、估值分位，截至 2024-12-31 / 2026-06-30 |
| 14 | [Slickcharts S&P 500 Total Returns](http://slickcharts.com/sp500/returns) | 标普500 1970–2025 全收益年度回报，含分红再投资，截至 2025-12-31 |

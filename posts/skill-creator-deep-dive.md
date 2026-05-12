---
title: skill-creator 深度解析：一个教模型如何造技能的技能
date: 2026-05-12
tags: [工具, AI, 复盘]
summary: 按阅读顺序拆解 skill-creator 的 SKILL.md，看清每条指令背后的设计意图与权衡。
---


> 本文按照 `SKILL.md` 的实际阅读顺序，逐段拆解 skill-creator 的设计意图：作者为什么这么写、这么写解决了什么问题、每个决定背后的权衡是什么。读完之后你再回去看原文，应该能看到隐藏在措辞背后的那套方法论。

---

## 0. 先理解大背景：skill-creator 到底是什么

skill-creator 是一个 **"meta-skill"**——它不是解决某个具体业务问题的技能，而是专门用来创建、改进、评估其他技能的工作流封装。

它要同时解决四件事：

1. 帮用户从零起草一个新 skill
2. 帮用户改进一个已有的 skill
3. 把"skill 到底好不好用"这件事量化（跑评测、对比 baseline）
4. 优化 skill 的 `description` 字段，让它在 Claude 的技能列表里被正确触发

理解这个四合一的定位，才能看懂后文为什么会在不同章节反复切换视角——一会儿像教程、一会儿像操作手册、一会儿又像写给 AI 的心法口诀。

---

## 1. 文件头：frontmatter 的两行决定了这个 skill 能不能被召唤

```yaml
---
name: skill-creator
description: Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy.
---
```

**为什么这么写？**

skill 的触发机制决定了 `description` 是唯一入口——Claude 在决定"要不要打开这个 skill"时，只看 name + description 这 ~100 词元数据，不会去读正文。所以作者做了两件事：

- **动词密集**：`Create / modify / improve / measure / run evals / benchmark / optimize`，几乎把用户可能说出的所有意图动词都堆了进去。
- **上下文提示**："Use when users want to..." 这种半引导式的句式，是作者在正文里明确建议的"pushy"写法——直接告诉模型"遇到这些场景时就触发我"，对抗 Claude 默认的「undertrigger」倾向。

这不是随便堆关键词，而是把后面正文里讲的 description 优化原则，**用在自己身上**。skill-creator 是自举的：它自己就是它推荐写法的范例。

---

## 2. 开头的 High-level 流程图：先给一个"鸟瞰图"

```
- 决定这个 skill 要做什么
- 写一版草稿
- 写几个测试 prompt，跑 claude-with-skill
- 帮用户从定性和定量两个维度评估结果
- 根据反馈改写
- 重复直到满意
- 扩大测试集再来一遍
```

**为什么这么写？**

作者很清楚一件事：**如果让模型一上来就啃后面 400 多行的细节，它会迷失**。所以他先给一个 6 步概览，相当于一张目录索引。后面所有"具体怎么做"的章节，都是在展开这 6 步里的某一步。

紧接着的这段话是全文的"使用说明"：

> "Your job when using this skill is to figure out where the user is in this process and then jump in and help them progress through these stages."

这一句把 skill-creator 从一个线性剧本转成了**状态机**——模型要先判断用户当前处于循环的哪一环，再决定跳进去帮忙。这是一种非常高阶的 prompt 设计：不命令模型"按顺序做 1→2→3"，而是授权模型"根据上下文选择合适的入口"。

结尾那句 "Cool? Cool." 也是有意为之——作者在后文专门说过，skill 的写作风格要避免 MUST 型的僵硬指令，改用有温度、解释性的叙述。开头这个"Cool? Cool"就是在给模型示范语气。

---

## 3. 与用户沟通：把"读者画像"摆到台面上

```
- "evaluation" 和 "benchmark" 算是边缘词汇
- "JSON" 和 "assertion" 要看到用户明显懂才直接用
```

**为什么要有这一段？**

这是全文里最容易被忽略但又最见功力的一节。作者意识到：skill-creator 的用户既可能是工程师，也可能是第一次打开终端的家长。**同一个模型面对这两类人，默认讲话方式不能一样**。

与其写一句空洞的"please adjust tone to audience"（这种话 Claude 早就在系统提示里吃过一万次了），不如**给几个具体词例**：哪些词在"理解边界"上，哪些词要验证用户水平再用。这就是后文反复强调的「explain the why, don't just say what」的活例子。

---

## 4. 创建 skill 三步曲：Capture Intent → Interview → Write

这一段按"真实流程"排列：

### 4.1 Capture Intent（捕获意图）

> "The current conversation might already contain a workflow the user wants to capture."

**这句话解决了一个真实场景**：用户经常在干完活之后才说"把刚才这个过程做成 skill 吧"。skill-creator 被设计成能从已有对话里反向提取步骤、工具、修正点，而不是强迫用户重新描述一遍。

四个必问问题（做什么/何时触发/输出格式/要不要测试用例）被放在这里，是因为它们**覆盖了 skill 定义的全部维度**：功能、触发、契约、质量保证。

值得注意的是第 4 条——要不要做测试用例，作者没有一刀切，而是给了启发式：**客观可验证的 skill 适合，主观风格类的不适合**。这是非常成熟的产品决策，避免了"所有 skill 都必须跑评测"这种教条。

### 4.2 Interview and Research

这里引入了 **subagent 并行调研**的模式。作者不是为了炫技，而是因为 skill 创作往往需要先搞懂一个陌生领域——如果能并行调研，就能"come prepared with context to reduce burden on the user"。这个短语精准抓住了好助手的核心：**少问，多查，带着答案回来**。

### 4.3 Write the SKILL.md

关键段落是 description 字段的写法建议，作者直接甩出一个反面/正面对比：

- 反面：`"How to build a simple fast dashboard to display internal Anthropic data."`
- 正面：`"... Make sure to use this skill whenever the user mentions dashboards, data visualization, internal metrics, or wants to display any kind of company data, even if they don't explicitly ask for a 'dashboard.'"`

**为什么要"pushy"？**

因为作者观察到一个真实偏差：Claude 有 "undertrigger" 倾向——明明 skill 能帮忙，它却选择自己硬搞。这不是模型坏，是模型保守。所以 description 里要**主动授权触发**，甚至列出隐式的场景词。这个"pushy"策略和后面的「描述优化循环」是一体两面：前者是启发式手写，后者是定量迭代。

---

## 5. Skill 写作指南：Anatomy 与 Progressive Disclosure

### 5.1 文件结构树

```
skill-name/
├── SKILL.md (required)
└── Bundled Resources (optional)
    ├── scripts/    - 确定性/重复任务的可执行代码
    ├── references/ - 按需加载的文档
    └── assets/     - 输出中使用的文件（模板、图标、字体）
```

**这三个子目录的语义边界非常重要**——它们对应三种不同的加载方式：

| 目录         | 加载方式        | 典型用途             |
|------------|-------------|------------------|
| scripts/   | 执行时调用，不进上下文 | 避免模型重复造轮子        |
| references/| 需要时 Read 进来 | 大块文档、schema、变体分支 |
| assets/    | 作为产物被嵌入     | HTML 模板、字体、图片    |

### 5.2 Progressive Disclosure（渐进式披露）

```
1. Metadata           - 始终在上下文（~100 词）
2. SKILL.md body      - 触发后加载（<500 行）
3. Bundled resources  - 按需读取（无上限）
```

**为什么要分三层？**

因为上下文窗口是有限的，而 skill 总量可以无限增长。如果把所有内容都塞进 SKILL.md，要么超长被截断，要么挤占其他 skill 的预算。三层结构的本质是**成本分级**：常用的放在便宜的地方，重的放在按需付费的地方。

后面的 "Domain organization" 举了 `cloud-deploy/aws.md`、`gcp.md`、`azure.md` 的例子，正是这个思路——模型只读当前用得上的那个 reference，不读另外两个。

### 5.3 Principle of Lack of Surprise

这是安全边界。一段话的目的是防止用户拿 skill-creator 生成恶意 skill。措辞很克制：没说"绝对禁止"，而是说"skill 的内容不应让用户对其意图感到意外"——这把判断权交给了"一个讲理的用户会不会介意"，比硬性黑名单更灵活。

### 5.4 Writing Patterns

两个模板块：「Report structure」和「Examples」。作者把**格式约束示例直接贴进正文**，而不是空口说"你要定义输出格式"。这种"授人以渔"的写法，让模型下次自己生成 skill 时有样可抄。

---

## 6. Writing Style：整篇文档最核心的一段「心法」

```
Try to explain to the model why things are important 
in lieu of heavy-handed musty MUSTs.
```

这一段短短几句话，是全文价值密度最高的部分。它反复出现在后面的「improving the skill」章节里，几乎是作者的"写作宪法"：

1. **解释 why，不要堆 MUST**——模型有 theory of mind，你告诉它原因，它能举一反三；你只给命令，它只会机械执行。
2. **避免过度具体的例子**——写 skill 是要被"用一百万次"的，太贴某个案例会 overfit。
3. **发现自己在写 ALWAYS/NEVER 就是黄灯**——说明你在硬堵一个症状，而没解决病因。

这段话是 skill-creator 的灵魂。后面几百行看似繁琐的操作步骤，全都是这条原则在不同场景下的具体化。

---

## 7. 测试用例与评估工作流：一段"连续流程，中途不许停"

从「Test Cases」到「Step 5: Read the feedback」，作者明确说：

> "This section is one continuous sequence — don't stop partway through."

**为什么要这么强调？**

因为模型特别容易在工具调用密集的地方"跑偏"或者"自作主张"。作者用了三种手段把它钉死在流程里：

### 7.1 文件结构先定死

```
<skill-name>-workspace/
├── iteration-1/
│   ├── eval-0/
│   │   ├── with_skill/outputs/
│   │   └── without_skill/outputs/
```

workspace 作为 skill 的"同级兄弟"放置，而不是嵌进 skill 内部。这样 skill 本身保持干净可分发，测试产物独立演进。每个 iteration 独立目录，让"改进史"可回溯。

### 7.2 Parallel 强制

> "For each test case, spawn two subagents in the same turn — one with the skill, one without. ... don't spawn the with-skill runs first and then come back for baselines later."

这是针对一个具体偏差的纠正：模型倾向于串行——先跑完 with_skill 看看效果再决定要不要跑 baseline。但串行会让两批次的机器状态、网络延迟、模型版本差异污染对比。**强制同一个 turn 内并发启动**，是为了让 baseline 和实验组在尽可能一致的环境下完成。

### 7.3 Timing 数据必须即时捕获

> "This is the only opportunity to capture this data — it comes through the task notification and isn't persisted elsewhere."

这句话是**作者踩过坑的痕迹**。subagent 完成时的 token/duration 数据只在通知里出现一次，过了就拿不回来。写在这里是为了让未来的模型不要犯同样的错——宁可打断流程也要先存盘。

### 7.4 Baseline 的选择分叉

```
- 创建新 skill：baseline = 不带任何 skill
- 改进已有 skill：baseline = 旧版 snapshot
```

这个分叉设计避免了一个常见误用：改版 skill 时若用"无 skill"作为 baseline，会错把"有 skill 就好"当成"新版本更好"。真正的问题是新版比旧版好吗——所以要 snapshot 旧版做对照。

### 7.5 Grading 的字段名洁癖

> "The grading.json expectations array must use the fields `text`, `passed`, and `evidence` (not `name`/`met`/`details` or other variants) — the viewer depends on these exact field names."

这句话表面上在谈字段命名，本质是在处理 **LLM 的"同义词漂移"问题**。模型在生成 JSON 时会自作主张把 `passed` 改成 `met`、`text` 改成 `name`，因为这些都是语义相近的词。但下游 viewer 是硬编码的 Python 代码，不认同义词。作者把这件事用感叹号的方式钉下来，是对模型这种"善意创造"的反制。

### 7.6 Viewer 有两个 tab，作用不同

- **Outputs tab**：定性评审，让人**感觉对不对**
- **Benchmark tab**：定量对比，让人**判断值不值**

两个维度并列，不是冗余，而是**主观与客观互为校验**。单看定量会掉进"过拟合指标"陷阱；单看定性会掉进"只见树木"陷阱。

---

## 8. 改进 skill：四条"思维法则"

这一段从命令式完全切换到哲理式，作者像在对未来的 skill 作者谆谆教导：

### 8.1 Generalize from feedback

> "The big picture thing that's happening here is that we're trying to create skills that can be used a million times... If the skill you and the user are codeveloping works only for those examples, it's useless."

这是一个**反 overfitting** 的直接提醒。用户看着 3 个测试用例跑来跑去，很容易让 skill 变成"对这三个例子最优"而非"对一切场景都可用"。作者让模型自觉跳出样本，用更通用的隐喻和模式。

### 8.2 Keep the prompt lean

> "Make sure to read the transcripts, not just the final outputs..."

这句非常关键：只看输出结果看不出 skill 中哪段文字在浪费 token。要**读过程** (transcript)，看看模型是不是被 skill 里的某段文字带到了歧路上。如果是，删掉，看会不会变坏；不会变坏就是冗余。

### 8.3 Explain the why

这条是 Writing Style 那段话的重复，作者为了强调又说了一遍。而且这次加了更强的措辞：

> "If you find yourself writing ALWAYS or NEVER in all caps, or using super rigid structures, that's a yellow flag."

ALWAYS/NEVER 是"我不相信模型能理解"的表现。作者认为这种不信任才是技能低效的根因——真正的好 skill 是"说服模型"，不是"绑架模型"。

### 8.4 Look for repeated work

> "If all 3 test cases resulted in the subagent writing a `create_docx.py` or a `build_chart.py`, that's a strong signal the skill should bundle that script."

这条是纯工程判断：**重复劳动 = bundling 信号**。三个 subagent 独立写出相似脚本，说明这段逻辑是领域常识，属于 skill 的"公设"，应该写一次、打包进 scripts/，而不是让每次调用都重新发明。

---

## 9. Blind Comparison 与 Description Optimization：两个"高阶"分支

从这里开始，文档语气明显转为可选项：

> "This is optional, requires subagents, and most users won't need it."

**为什么放在后面？**

因为这两个工具化的流程学习成本高，不是人人都用得上。作者的结构哲学是**"轻主干 + 重侧枝"**——主流程（起草→测→改）必须每个人都跟着走；blind comparison 和 description optimization 是工具箱里的可选利器，等主流程都熟了再用。

### 9.1 描述优化的设计细节

- **20 条 trigger eval queries**，should_trigger 与 not 各 8-10 条
- 必须像**真实用户那样写**：文件路径、行话、错别字、缩写、背景故事都要有
- 反面例子：`"Format this data"` —— 太抽象
- 正面例子：整段关于 Q4 sales xlsx 的吐槽 —— 够具体

**为什么强调真实感？**

因为 description 是在 Claude 路由层被判断的，而 Claude 路由层看到的真实输入就是口语化的、带背景的、不规整的。拿"完美测试句"训练出的 description，部署后碰到真实用户就废。

- **Train/Test split (60/40)**：防过拟合。改进循环只看 train，但选最优 description 用 test 分。这和 ML 的 train/test split 完全同构。
- **Trigger rate 用 3 次投票聚合**：因为 LLM 触发决策本身带随机性，单次结果不稳定。3 次投票把信号噪比拉上去。
- **"Simple queries 不会触发 skill"的提醒**：这是对新手的重要警告——不是 description 写不好，是 query 本身不复杂到需要 skill。

---

## 10. Claude.ai / Cowork / Claude Code 三环境适配

文档后半段专门给三个运行环境写了差异条款：

- **Claude.ai**：没有 subagent，没法 parallel，没法跑 description optimization
- **Cowork**：有 subagent 但没浏览器，viewer 要用 `--static` 写 HTML 文件
- **Claude Code**：完整能力

**为什么要把这段单独抽出来？**

因为主流程预设了"有 subagent + 有浏览器"的理想环境，但 skill-creator 会在多环境里被调用。如果一套流程塞到文中，模型会不知道在自己的环境里哪些步骤该跳过。**分环境条款 = 环境适配层**，让模型能先自检再执行。

Cowork 那段还出现了全文唯一一处全大写：

> "GENERATE THE EVAL VIEWER *BEFORE* evaluating inputs yourself."

作者自己在前面反复告诫"不要用 MUST/ALWAYS/NEVER 大写句"，这里却破例。说明这条是**反复观察到的 Cowork 行为偏差**——模型在 Cowork 里就是喜欢跳过 viewer 自己评审，怎么劝都劝不住，只能用这种例外手段强调。这是规则之上的经验主义补丁。

---

## 11. 结尾的重复：不是啰嗦，是检查表

```
- Figure out what the skill is about
- Draft or edit the skill
- Run claude-with-access-to-the-skill on test prompts
- With the user, evaluate the outputs...
- Repeat until you and the user are satisfied
- Package the final skill and return it to the user.
```

文档最后又把 6 步流程念了一遍。**不是作者健忘，是这 6 步太容易被中途抛弃**。长文档的模型使用者（不管是人类还是 LLM）都会"看到后面忘了前面"。结尾的清单是一次定锚——无论你刚才读了多少细节，最终交付物的骨架永远是这六步。

最后一句 "Good luck!" 看起来像口头禅，其实也是刻意的——让模型以放松的态度接手任务，而不是被 400 行细节压住喘不过气。与开头的 "Cool? Cool." 首尾呼应，贯彻了"有温度、解释性、非命令式"的写作宪法。

---

## 12. 整篇设计哲学的三个支柱

把前文归纳一下，skill-creator 之所以能成立，靠的是三根柱子：

### 柱一：Progressive Disclosure（渐进式披露）

从 description 到 SKILL.md 到 bundled resources，信息按需展开。这让 skill 可以无限丰富，但每次调用成本可控。

### 柱二：Explain Why, Not What（解释为什么）

整份文档几乎没有纯粹的命令，每条指令都附带了"为什么要这么做"。这让模型不是死记硬背，而是理解原则后自主决策——即使在作者没预料到的场景里，也能做出正确选择。

### 柱三：量化 + 定性双轨评估

benchmark.json 负责定量，viewer 的 Outputs tab 负责定性，feedback.json 串联用户判断。三者闭环，避免了"跑了一堆指标但结果依然不好"或"主观感觉不错但经不起复现"的两种单边失败。

---

## 13. 为什么它本身就是一个"合格 skill"的范例

最后回头看：skill-creator 自己是不是符合它定义的好 skill 标准？

| 原则                 | 自己做到了吗？                                |
|--------------------|----------------------------------------|
| description 要 pushy | ✓ 罗列了 create/modify/optimize/benchmark 等全部动词和场景 |
| 主干 ≤ 500 行         | SKILL.md 约 486 行，踩线合格                   |
| 大文件分到 references/  | schemas.md、grader.md、comparator.md 都抽出去了 |
| scripts/ 封装重复工作    | aggregate_benchmark、run_loop、package_skill 都是避免每次重造轮子 |
| assets/ 存模板        | eval_review.html 作为 UI 模板              |
| Explain why        | 几乎每一条指令都跟着"because..." / "这样做是为了..."    |
| 避免过度 MUST          | 全文只在 Cowork 补丁那里破例一次，其余都用叙述式           |

它用自己证明自己的方法论是可执行的。这是一份优秀的 meta-skill 应有的样子——**既是产品，也是产品说明书**。

---

## 附：阅读这份 SKILL.md 的建议顺序

如果你要重读原文，建议分三轮：

1. **第一轮**：只读各级标题和开头 6 步概览，建立骨架感知。
2. **第二轮**：聚焦 Writing Style、Improving the skill 四条原则——这是方法论核心。
3. **第三轮**：按需查阅具体操作段落（评测目录结构、grading.json 字段、description optimization 参数）——这些是查表用的，不用通读。

这样既能抓住作者的"写作宪法"，又不会被工程细节淹没。

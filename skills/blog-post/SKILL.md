---
name: blog-post
description: 用于发布、修改、删除 wendellzone.github.io 博客文章的 skill。触发词：「发一篇博客」「写篇博客讲 xxx」「博客加文章」「改一下博客 xxx 的标题/摘要」「更新博客」「删掉那篇博客」「列出我的博客文章」。本 skill 维护本地 Markdown 源文件、自动同步 posts/index.json、自动计算阅读时间，并以独立 commit 推送到 GitHub，Pages 在一分钟内重建上线。**发布前必须执行强制内容审查**：扫描敏感词（在职公司项目名/客户名/内部域名/邮箱）并征得用户明确确认，否则不允许 push。
agent_created: true
---

# blog-post

管理 <https://wendellzone.github.io/> 个人博客（仓库 `wendellzone/wendellzone.github.io`）。

每次操作都是一次独立的 git commit（author `wendellzone <wendellzone@users.noreply.github.com>`），自动 push 到 `origin main`，编辑历史完整保留，站点自动重建。

## 何时使用本 skill

任一意图触发即可：

- 发布新文章："发篇博客"、"写一篇关于 xxx 的博客"、"add a post"、"新建博客文章"
- 修改现有文章："改博客里那篇 xxx"、"把博客 xxx 的标题换成 yyy"、"update post"
- 删除文章："删掉博客的 xxx"、"删除那篇博客"
- 列出文章："列出我所有博客文章"、"show my blog posts"

不要为以下场景激活：
- 修改 `index.html`、CSS、站点结构 —— 这些走普通 git 操作即可
- 另一个个人站 —— 本 skill 只管本博客

## 前置检查

执行任何子命令前，先确认：

1. `gh auth status -h github.com` 显示当前账号是 `wendellzone`。如果不是，请用户跑 `gh auth switch --user wendellzone` 切回。
2. 本地仓库存在于约定路径下。可用 `--repo <path>` 或环境变量 `BLOG_REPO` 覆盖。
3. 工作区干净（仓库内 `git status --porcelain` 为空）。如果有未提交改动，先报告给用户，不要混进文章 commit。

## 发布前内容审查（强制）

> ⚠️ **`new` 和 `edit --body-file` 在执行前必须做这一步。** 不能跳过、不能"我看过了"敷衍过。一旦推送出去，commit 就进入公开 git 历史，rewrite 历史违反本 skill 安全约束（禁止 force push）。

完整的可执行 checklist 见 [`references/pre-publish-checklist.md`](references/pre-publish-checklist.md)。下面给出最关键的核心要点。

### 必查清单

发布/更新前，agent **必须**用 grep 跑一遍下列敏感词扫描，**任一命中就停下来询问用户**，不允许直接发：

| 类别 | 处理方式 |
|---|---|
| 在职公司内部项目名/服务名 | 替换为通用业务示例（order-service / user-service / payment-service 等）|
| 在职/前任公司名 | 改用"前公司"或具体技术领域抽象描述 |
| 客户/合作方真实名称 | 一律抽象成"某 xxx 行业客户" |
| 内部 URL/IP/域名 | 删除或替换为示例域 |
| 真实邮箱 | 删除或脱敏成 `xxx@example.com` |
| 内部仓库 URL | 删除或脱敏 |
| 项目代号/产品代号 | 用通用名替换 |

> 💡 具体的敏感词清单（包含真实关键词）保存在用户本地的 skill 副本中，不放进公开仓库。本仓库展示的是脱敏后的"模式描述"。

### 扫描命令模板

发布前 agent 必须执行（替换 `<body-file>` 为实际路径，敏感词清单从本地 skill 副本读取）：

```bash
# 1. 敏感词扫描（关键词从本地 skill 副本的扫描脚本读取）
grep -nE "<sensitive-pattern-list>" <body-file> && echo "⚠️  发现敏感词，停止发布" || echo "✓ 敏感词扫描通过"

# 2. 列出可疑英文标识符（连字符命名的内部服务名形态）
grep -oE "\b[a-z]+-[a-z]+-(service|system|backend)\b" <body-file> | sort -u

# 3. 让用户确认
echo "以上识别出的标识符是否包含工作内部信息？请用户确认。"
```

### 工作流硬性约束

agent **必须**按这个顺序：

1. ✅ 先做完上面的敏感词扫描
2. ✅ 把扫描结果展示给用户（即使 grep 命中数为 0，也要明确报告"已扫描，0 命中"）
3. ✅ 主动询问："正文里提及了 [具体内容/示例场景]，是否包含不能公开的工作信息？"
4. ✅ **得到用户明确"可以发"答复后再调用 publish.py**
5. ❌ 即使用户说"快点发"或"不用问"，依然要走完前 3 步——这是不可跳过的合规步骤

### 用户没回应时

如果用户未在合理时间内确认，**不要"为了帮用户省事"擅自推送**。改为：把准备好的 markdown 文件路径告诉用户，让用户用 `--no-push` 自己跑或回头确认后再推。

### 发布后兜底校验

push 之后用 curl 拉远端文件，再扫一次敏感词，确认无残留。

## 执行方式

**始终调用 `scripts/publish.py`，不要手动改 markdown + index.json + git。** 脚本是保证 `posts/*.md` 与 `posts/index.json` 一致性的唯一入口。

**脚本路径**：`publish.py` 放在 **skill 目录** 而非博客仓库里，调用时用绝对路径，工作目录要 `cd` 到博客仓库根（或通过 `BLOG_REPO` 环境变量指定），脚本以当前工作目录定位仓库。下文示例为简洁起见写成 `scripts/publish.py`。

### 新建文章

```bash
scripts/publish.py new \
  --title "文章标题" \
  --tags "Go,后端" \
  --summary "一句话摘要" \
  --body-file /tmp/body.md
```

参数：
- `--title` 必填
- `--slug` 可选；不传则从标题自动生成（英文走 kebab-case；纯中文标题 fallback 到 `post-<时间戳>`）
- `--date` 默认今天（`YYYY-MM-DD`）
- `--tags` 逗号分隔
- `--summary` 一句话摘要，列表页展示
- `--body-file` 正文 markdown 文件路径。如果文件已含 frontmatter，会被剥掉换成由 CLI 参数生成的版本。建议把正文先写到临时文件（如 `/tmp/new-post.md`），不要在命令行传大段字符串。
- `--no-push` 只改本地不推送（dry-run）

用户只给主题时的推荐流程：
1. 标题、标签、摘要任一缺失则补问。
2. 把 markdown 正文写到 `/tmp/<slug>.md`。
3. **跑"发布前内容审查"流程，得到用户确认后**才进入下一步。
4. 调用 `publish.py new ... --body-file /tmp/<slug>.md`。
5. 报告线上 URL：`https://wendellzone.github.io/#/post/<slug>`。
6. 跑"发布后兜底校验"。

### 修改文章

```bash
# 只改 frontmatter
scripts/publish.py edit <slug> --title "新标题" --tags "Go,工具" --summary "…"

# 替换正文（输入文件可带 frontmatter，也可不带）
scripts/publish.py edit <slug> --body-file /tmp/new-body.md
```

行为：
- 没在命令行传的 frontmatter 字段保持原值。
- `--body-file` 替换正文。文件以 `---` 起始则整体采用其 frontmatter；否则保留旧 frontmatter，仅换正文。
- `index.json` 自动从最终 frontmatter 同步。

> ⚠️ 用 `--body-file` 替换正文等同于发新内容到公开仓库，**必须先跑"发布前内容审查"**。仅改 frontmatter（`--title` / `--tags` / `--summary`）也建议扫一遍 summary 里有没有敏感词。

### 删除文章

```bash
scripts/publish.py delete <slug>
```

软删：
- `.md` 移到 `_trash/<slug>-<时间戳>.md`，**不是物理删除**，git 历史也仍可追回。
- 同步从 `posts/index.json` 移除。
- 提交一次 commit `post: remove '<title>' (<slug>)` 并推送。

恢复：`git mv _trash/<slug>-<ts>.md posts/<slug>.md`，再加回 `index.json` 一条，最后 `publish.py edit <slug>` 同步元数据。

### 列出文章

```bash
scripts/publish.py list
```

打印 slug / title / date / tags / summary / readingTime。

### 重算阅读时间

```bash
scripts/publish.py resync
```

读每篇文章正文重算 `readingTime`，写回 `index.json`，提交并推送。手工批量编辑过 markdown 后跑一遍；任何时候跑都安全，没变化时不会产生 commit。

## 约定与不变量

会话内首次发文前先读一遍 `references/posting-conventions.md`。要点：

- 文件 frontmatter 字段固定：`title / date / tags / summary`，markdown 文件里别加其他 key。
- `index.json` 比 markdown 多一个 `readingTime` 字段（脚本自动算，不要手编；漂移了用 `resync`）。
- `date` 用 ISO `YYYY-MM-DD`。
- `tags` 是简短主题标签数组，不要加时间类标签。
- `summary` ≤ 50 个汉字 / 80 个英文字符，纯文本（不含 markdown）。
- 正文支持 GFM、`highlight.js` 代码高亮、PlantUML / Mermaid 围栏块。
- 正文里不必再写一级标题 `# xxx`，页面头已经从 frontmatter 渲染了标题；想加结构就从 `##` 开始。
- 跨文章链接不要用 `./other.md` 相对路径 —— 站点用 hash 路由。需要交叉引用时写 `[文字](#/post/other-slug)`。

## 安全

- **务必**先确认工作区干净（参见"前置检查"）。脚本提交时会带上当时所有已暂存的改动，工作区脏会把无关变更混进文章 commit。
- **务必**做发布前内容审查（参见"发布前内容审查（强制）"章节）。一旦内部信息进入公开 git 历史，清理代价巨大。
- 调 `delete` 前**与用户确认**。虽然是软删，明示意图能避免误删错 slug。
- **绝不**给 git 加 `--force`。脚本不重写历史；远端有新 commit 时通过 rebase-on-push 处理。这条约束意味着：**事前审查比事后清理更便宜，绝对不能依赖"出问题再 force push"兜底**。
- **不要**暴露真实邮箱。commit 用脚本内置的 `@users.noreply.github.com` 别名。

## 验证发布

push 后 GitHub Pages 重建大约 30~60 秒。验证：

```bash
curl -sI https://wendellzone.github.io/posts/<slug>.md | head -1   # 期望 HTTP/2 200
```

几分钟仍失败时检查 Pages 构建：

```bash
gh api /repos/wendellzone/wendellzone.github.io/pages/builds/latest --jq '.status,.error.message'
```

常见 Pages 坑：`.md` 已 commit 但访问 404，多半是仓库根缺 `.nojekyll`。没有这个文件 Jekyll 会吞掉 `.md`。

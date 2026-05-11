---
name: blog-post
description: 用于发布、修改、删除 wendellzone.github.io 博客文章的 skill。触发词：「发一篇博客」「写篇博客讲 xxx」「博客加文章」「改一下博客 xxx 的标题/摘要」「更新博客」「删掉那篇博客」「列出我的博客文章」。本 skill 维护本地 Markdown 源文件、自动同步 posts/index.json、自动计算阅读时间，并以独立 commit 推送到 GitHub，Pages 在一分钟内重建上线。
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
- 另一个个人站 `jiashuwang0/live-preview` —— 本 skill 只管博客

## 前置检查

执行任何子命令前，先确认：

1. `gh auth status -h github.com` 显示当前账号是 `wendellzone`。如果不是，请用户跑 `gh auth switch --user wendellzone` 切回。
2. 本地仓库存在于 `~/WorkBuddy/2026-05-09-task-1/wendellzone-blog/`。可用 `--repo <path>` 或环境变量 `BLOG_REPO` 覆盖。
3. 工作区干净（仓库内 `git status --porcelain` 为空）。如果有未提交改动，先报告给用户，不要混进文章 commit。

## 执行方式

**始终调用 `scripts/publish.py`，不要手动改 markdown + index.json + git。** 脚本是保证 `posts/*.md` 与 `posts/index.json` 一致性的唯一入口。

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
3. 调用 `publish.py new ... --body-file /tmp/<slug>.md`。
4. 报告线上 URL：`https://wendellzone.github.io/#/post/<slug>`。

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
- 正文支持 GFM、`highlight.js` 代码高亮、PlantUML 围栏块：

  <pre>
  ```plantuml
  @startuml
  Alice -> Bob: hi
  @enduml
  ```
  </pre>

- 正文里不必再写一级标题 `# xxx`，页面头已经从 frontmatter 渲染了标题；想加结构就从 `##` 开始。
- 跨文章链接不要用 `./other.md` 相对路径 —— 站点用 hash 路由。需要交叉引用时写 `[文字](#/post/other-slug)`。

## 安全

- **务必**先确认工作区干净（参见"前置检查"）。脚本提交时会带上当时所有已暂存的改动，工作区脏会把无关变更混进文章 commit。
- 调 `delete` 前**与用户确认**。虽然是软删，明示意图能避免误删错 slug。
- **绝不**给 git 加 `--force`。脚本不重写历史；远端有新 commit 时通过 rebase-on-push 处理。
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

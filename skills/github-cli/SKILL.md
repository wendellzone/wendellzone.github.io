---
name: github-cli
description: GitHub 仓库、Issue、Pull Request、Workflow 等操作的本地代理。基于本机 gh CLI 调用 GitHub REST/GraphQL API，提供登录态管理、仓库浏览、Issue/PR 创建与查询、release 与 workflow 触发、代码搜索等能力。当用户请求涉及 "GitHub"、"PR"、"issue"、"仓库"、"clone/fork"、"release"、"workflow"、"@用户名/仓库名" 形式的资源时，应使用本 skill。
agent_created: true
---

# github-cli

通过本机 `gh` CLI 操作 GitHub。所有动作走当前登录态，不接收明文 token，不修改 shell 配置。

## When to Use This Skill

- 用户要求查询、创建、修改 GitHub 上的仓库 / Issue / PR / Release / Workflow。
- 用户给出 `owner/repo`、PR 号、issue 号、GitHub URL，并要求获取或操作其内容。
- 用户要求在本地 clone、fork、或创建新仓库。
- 用户要求触发或查看 GitHub Actions 运行状态。
- 用户要求搜索 GitHub 代码、issue、用户。

不适用：纯 git 本地操作（commit / rebase / push 单纯本地仓库）— 用普通 git 命令即可。

## Prerequisites

执行任何动作前，按顺序确认：

1. `gh` 是否安装：`command -v gh`。未装则停止并提示用户 `brew install gh`。
2. 登录态：`gh auth status -h github.com 2>&1`。若返回 `not logged into`，提示用户运行 `gh auth login`，**绝不**代为执行（涉及交互式登录与浏览器）。
3. 当前仓库上下文：在已 clone 的仓库内调用时优先用 `gh` 默认上下文；跨仓库操作必须显式带 `--repo owner/name`。

## Core Workflows

### 1. 用户身份与登录态

```bash
gh auth status            # 检查登录与 scope
gh api user --jq '.login' # 当前用户名
```

### 2. 仓库浏览与详情

```bash
gh repo list <owner_or_org> --limit 30 --json name,description,stargazerCount,updatedAt
gh repo view owner/repo --json name,description,defaultBranchRef,stargazerCount,licenseInfo,url
gh repo clone owner/repo [target_dir]
```

要列出"我自己的仓库"用 `gh repo list` 不带 owner。

### 3. Issue

```bash
gh issue list   --repo owner/repo --state open --limit 20 --json number,title,state,labels,author
gh issue view   <num> --repo owner/repo --json number,title,body,state,comments
gh issue create --repo owner/repo --title "..." --body "..." --label bug --label p1
gh issue close  <num> --repo owner/repo --comment "fixed in #123"
gh issue comment <num> --repo owner/repo --body "..."
```

创建带长内容的 issue 时，将 body 写入临时文件再 `--body-file /tmp/x.md`，避免 shell 转义问题。

### 4. Pull Request

```bash
gh pr list   --repo owner/repo --state open --limit 20 --json number,title,headRefName,baseRefName,author,isDraft
gh pr view   <num> --repo owner/repo --json number,title,body,state,files,reviews,comments
gh pr diff   <num> --repo owner/repo
gh pr create --repo owner/repo --title "..." --body-file /tmp/pr.md --head feature/x --base main [--draft]
gh pr review <num> --repo owner/repo --approve|--request-changes|--comment --body "..."
gh pr merge  <num> --repo owner/repo --squash|--merge|--rebase --delete-branch
gh pr checkout <num>     # 在已 clone 的仓库内切到 PR 分支
```

PR body 同样推荐 `--body-file`。

### 5. Release

```bash
gh release list   --repo owner/repo --limit 10
gh release view   <tag> --repo owner/repo
gh release create <tag> --repo owner/repo --title "..." --notes-file /tmp/notes.md [asset1 asset2]
gh release upload <tag> --repo owner/repo file1 file2
```

### 6. GitHub Actions / Workflow

```bash
gh workflow list  --repo owner/repo
gh workflow view  <name_or_id> --repo owner/repo
gh workflow run   <name_or_id> --repo owner/repo --ref main -f key=value
gh run list       --repo owner/repo --limit 10 --workflow=<name>
gh run view       <run_id> --repo owner/repo --log-failed
gh run watch      <run_id> --repo owner/repo
```

### 7. 搜索

```bash
gh search repos "topic:rust stars:>1000" --limit 20
gh search issues "is:open author:@me" --limit 20
gh search code   "func main" --language go --owner owner --limit 30
```

### 8. 通用 API（兜底）

任何 `gh` 子命令未覆盖的接口走 `gh api`：

```bash
gh api repos/owner/repo/contributors --jq '.[].login'
gh api graphql -f query='query { viewer { login } }'
gh api -X POST repos/owner/repo/issues/123/comments -f body='hello'
```

## Output Conventions

- 默认用 `--json <fields>` 取结构化输出，再 `--jq` 或在 Bash 后处理；避免依赖人类可读的彩色表格。
- 数据量较大时优先 `--limit`，必要时分页 `--paginate`。
- 长结果写入临时文件给用户预览，不要全量打印到对话。

## Safety Rules

- **绝不**主动执行 `gh auth login` / `gh auth logout` / `gh auth refresh`：涉及交互或登录态变更，必须由用户本人操作。
- **绝不**在没有用户确认的情况下执行写操作：`pr merge` / `pr close` / `issue close` / `release create` / `repo delete` / `repo create --public` 这类行为。先列出将执行的命令并请用户确认。
- **绝不**记录或回显 token；不要执行 `cat ~/.config/gh/hosts.yml` 或 `gh auth token` 把 token 打到聊天里。
- 涉及 `--public` 仓库或公开 release 前，明确告知用户"此操作会公开可见"。
- 跨仓库操作必须显式带 `--repo`，避免误操作当前目录的仓库。

## Troubleshooting

| 报错 | 原因 | 处理 |
|------|------|------|
| `gh: command not found` | 未安装 | 提示 `brew install gh`，停止 |
| `You are not logged into ...` | 未登录或 token 过期 | 提示用户 `gh auth login`，停止 |
| `HTTP 403: API rate limit exceeded` | 触发限流 | 等待 reset，或换登录态 |
| `HTTP 404` on `--repo X/Y` | 仓库名错或没权限 | 确认拼写与可见性 |
| `HTTP 422 Validation Failed` | 参数格式错（PR head/base、issue label 不存在等） | 校对参数，特别是 head 是否已 push |

## References

- 详细的 jq 提取片段、GraphQL 例子、批量脚本：见 `references/recipes.md`。
- 更多排查项与 scope 说明：见 `references/auth-and-scopes.md`。
- GitHub 用户名改名 SOP（含坑点与验证命令）：见 `references/rename-user-sop.md`。

## Helper Scripts

- `scripts/precheck.sh` —— 一键检查 `gh` 安装与登录态，输出可读报告。优先在每个会话开始时跑一次。
- `scripts/rename-user-remotes.sh <old> <new> [--apply]` —— GitHub 改名后批量重写本地所有 git remote。默认 dry-run，加 `--apply` 才真正写入。会同时处理 SSH 与 HTTPS 两种协议。

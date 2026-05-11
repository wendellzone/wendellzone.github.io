# gh CLI Recipes

进阶用法集合。SKILL.md 已覆盖常规操作，本文件聚焦少见但实用的片段。按需 grep。

## 1. 用 jq 提取常用字段

```bash
# 当前仓库的所有 open PR 标题与作者
gh pr list --json number,title,author --jq '.[] | "#\(.number) \(.title)  by \(.author.login)"'

# 取某 PR 的所有变更文件
gh pr view 42 --json files --jq '.files[].path'

# issue 按 label 分组计数
gh issue list --state open --limit 200 --json labels \
  --jq '[.[].labels[].name] | group_by(.) | map({label: .[0], count: length})'
```

## 2. GraphQL 示例

```bash
# 取仓库 README + 默认分支
gh api graphql -f query='
query($owner:String!, $name:String!) {
  repository(owner:$owner, name:$name) {
    defaultBranchRef { name }
    object(expression:"HEAD:README.md") { ... on Blob { text } }
  }
}' -F owner=octocat -F name=Hello-World
```

```bash
# 列出 viewer 最近 contribute 过的仓库
gh api graphql -f query='
{ viewer { contributionsCollection {
    commitContributionsByRepository(maxRepositories: 10) {
      repository { nameWithOwner }
      contributions { totalCount }
} } } }'
```

## 3. 批量操作

```bash
# 批量给所有 open issue 加 needs-triage 标签
gh issue list --state open --limit 100 --json number --jq '.[].number' \
  | xargs -I{} gh issue edit {} --add-label needs-triage

# 批量关闭含特定关键字的 issue
gh issue list --search "stale in:title" --state open --json number --jq '.[].number' \
  | xargs -I{} gh issue close {} --comment "Closing as stale."
```

## 4. PR 模板化创建

```bash
cat > /tmp/pr.md <<'EOF'
## What
<!-- 一句话描述 -->

## Why
<!-- 背景 -->

## How tested
- [ ] unit
- [ ] e2e
EOF

gh pr create \
  --repo owner/repo \
  --title "feat: ..." \
  --body-file /tmp/pr.md \
  --head feature/x \
  --base main \
  --draft
```

## 5. Workflow 触发与监听

```bash
# 触发 dispatch 并等待完成
gh workflow run deploy.yml -f env=staging -f version=1.2.3
sleep 3
RID=$(gh run list --workflow=deploy.yml --limit 1 --json databaseId --jq '.[0].databaseId')
gh run watch "$RID" --exit-status
```

## 6. 搜索 + 输出 markdown 报告

```bash
{
  echo "# Open issues 我被 cc 的"
  echo
  gh search issues "is:open mentions:@me" --limit 50 \
    --json number,title,repository,url \
    --jq '.[] | "- [\(.repository.nameWithOwner)#\(.number)](\(.url)) \(.title)"'
} > /tmp/cc-report.md
```

## 7. 速率限制查看

```bash
gh api rate_limit --jq '.resources | {core: .core, search: .search, graphql: .graphql}'
```

## 8. 跨仓库 cherry-pick PR 关联

```bash
# 在 PR body 引用其他仓库的 issue（自动建立反向链接）
echo "Closes owner1/repo1#123" >> /tmp/pr.md
```

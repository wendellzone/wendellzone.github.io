# GitHub 用户名改名 SOP（实测有效）

## 前置约束

- gh CLI **不支持**改 username，必须本人在浏览器 https://github.com/settings/admin 操作。
- 改名是不可逆的；旧名 90 天后可被任何人注册。

## 改名前

1. 跑 `gh repo list --limit 200 --json nameWithOwner` 备份仓库清单。
2. `find $HOME -maxdepth 6 -name .git -type d` + `git remote get-url` 列出受影响本地仓库。
3. 记录依赖旧 URL 的外部服务：CI/CD、Webhook、PaaS 部署、Docker registry、Go modules、文档外链。
4. 不需要动：SSH key（绑账号 id）、PAT（id 不变还有效）、全局 git user.email。

## 改名后立即操作

```bash
# 1. 验证新名生效
gh api user --jq '{login, id}'

# 2. 修 gh hosts.yml（gh 不会自动更新这一项！）
sed -i '' "s/<old>/<new>/g" ~/.config/gh/hosts.yml
gh auth status   # 应当显示 <new>

# 3. 一键重写本地所有 git remote（dry-run + apply 两步）
bash scripts/rename-user-remotes.sh <old> <new>            # dry-run
bash scripts/rename-user-remotes.sh <old> <new> --apply    # apply

# 4. 修复 HTTPS push 凭证（keychain 缓存的旧凭证会失效）
gh auth setup-git

# 5. 抽几个仓库 fetch 验证
git -C <repo> fetch origin
```

## 关键坑

| 坑 | 表现 | 解法 |
|----|------|------|
| GitHub Pages 旧域名直接 404，不做 301 跳转 | 改名当日实测 `<old>.github.io/<repo>/` 直接 404 | 主动替换所有外链；尽量把博客/简历/README 中的旧 URL 修掉 |
| `gh auth status` 还显示旧名 | gh hosts.yml 缓存了 user 字段 | sed 替换该字段 |
| HTTPS push 报 "Invalid username or token" | macOS Keychain 旧凭证 | `gh auth setup-git` |
| 用户主页（`<user>.github.io`）失效 | 仓库名跟账号名不匹配后 Pages 关闭 | `gh repo rename <new>.github.io --repo <new>/<old>.github.io` |
| 代码 / README hardcode 旧 URL | 跳转不可用，访客看到死链 | `grep -rn <old> --exclude-dir=.git` 全量扫一遍 |

## 验证用 curl

```bash
# 新地址应该 200
curl -s -o /dev/null -w "%{http_code}\n" "https://<new>.github.io/<repo>/"

# 旧账号 profile 应该 404，确认释放
curl -s -o /dev/null -w "%{http_code}\n" "https://github.com/<old>"
```

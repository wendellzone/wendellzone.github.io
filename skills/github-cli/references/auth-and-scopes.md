# gh 认证与 Scope 参考

## 登录方式

```bash
# 浏览器交互（推荐，最常用）
gh auth login

# 用环境变量传 PAT（仅本会话）
echo "$GITHUB_TOKEN" | gh auth login --with-token

# 切换默认账号
gh auth switch
```

## 常用 scope 对照

| 操作 | 必要 scope |
|------|------------|
| 读公开仓库 | `public_repo` 或匿名 |
| 读私有仓库 | `repo` |
| 创建/合并 PR、写 issue | `repo` |
| 触发 workflow_dispatch | `repo` + `workflow` |
| 管理 release 资产 | `repo` |
| 读用户邮箱 | `read:user` 或 `user:email` |
| 操作组织成员 | `admin:org` 或 `read:org` |
| 操作 GH Packages | `read:packages` / `write:packages` |
| GitHub Apps token | 取决于 App 安装权限 |

## 常见 scope 错误自查

- `403: Resource not accessible by integration` — token 没有目标资源的权限。
- `403: must have admin rights` — 仓库管理类操作需 admin。
- `401: Bad credentials` — token 失效或被吊销，重新 `gh auth login`。
- `gh auth refresh -s workflow` — 不重登录的前提下追加 scope。

## token 在哪

- macOS：默认存 Keychain（`gh` 装好后无明文）；`~/.config/gh/hosts.yml` 仅存非敏感信息。
- 其他系统：`~/.config/gh/hosts.yml` 可能含 token；不要将该文件 commit 或粘贴到对话。

## 多账号

```bash
gh auth login -h github.com           # 个人
gh auth login -h github.enterprise.io # 企业
gh auth switch                        # 切换
gh auth status                        # 查看所有
```

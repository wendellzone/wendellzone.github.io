# 发布前 checklist（强制）

> 本文档是 `SKILL.md` 中"发布前内容审查（强制）"章节的延伸，提供完整的可执行 checklist。
> agent 在 `new` 或 `edit --body-file` 之前**必须**完整跑过一遍。

> 💡 本仓库展示的是脱敏后的模式描述。具体真实关键词清单保存在用户本地 skill 副本（`~/.workbuddy/skills/blog-post/references/pre-publish-checklist.md`），不放进公开仓库。

## 一、自动化扫描脚本（脱敏模板）

复制以下命令对正文 markdown 文件做快速扫描（替换 `<body-file>` 为实际路径，`<sensitive-pattern>` 为真实关键词，模式由本地 skill 副本注入）：

```bash
BODY=<body-file>

echo "=== 1. 在职公司内部项目名/服务名 ==="
grep -nE "<在职项目代号-pattern>" "$BODY" || echo "  ✓ 无命中"

echo ""
echo "=== 2. 在职/前任公司名 ==="
grep -nE "<公司名-pattern>" "$BODY" || echo "  ✓ 无命中"

echo ""
echo "=== 3. 内部域名/邮箱 ==="
grep -nE "<内部域名-pattern>|<内部邮箱-pattern>" "$BODY" || echo "  ✓ 无命中"

echo ""
echo "=== 4. 内部 GitLab/代码仓库 ==="
grep -nE "<内部仓库-pattern>" "$BODY" || echo "  ✓ 无命中"

echo ""
echo "=== 5. 可疑英文标识符（kebab-case 服务名形态）==="
grep -oE "\b[a-z]+-[a-z]+-(service|system|backend|api|gateway|worker|consumer)\b" "$BODY" | sort -u

echo ""
echo "=== 6. 可疑中文敏感片段（人工复核）==="
grep -nE "我们(团队|项目|组|公司).{0,30}" "$BODY" | head -20

echo ""
echo "=== 7. 内网 IP 段 ==="
grep -nE "\b(10|172\.16|192\.168)\.[0-9]+\.[0-9]+" "$BODY" || echo "  ✓ 无命中"
```

## 二、人工复核清单

光跑 grep 不够，agent 还要**逐条确认**：

- [ ] 正文是否提及"我现在做的项目"？如有，项目名是不是已经替换成中性示例？
- [ ] 是否提及"我们团队"、"我们组"？这些表述本身没事，但**后面跟的具体内容**有没有内部信息？
- [ ] 代码示例里的目录路径、文件名、类名、函数名是否暴露内部架构？
- [ ] 出现具体数字时（QPS、节点数、带宽、用户量），有没有非公开口径？
- [ ] 引用第三方文章/项目时，链接是不是公开 URL（github.com / 公开博客）？
- [ ] 截图、配置文件示例里有没有泄露 token、密钥、内网地址？

## 三、向用户的强制确认话术模板

跑完扫描后，agent **不能直接 publish**，必须用类似下面的话向用户确认：

```
我已对正文做发布前敏感词扫描，结果：
  - 自动扫描：[N 处命中 / 全部通过]
  - 详情：[列出命中行] 或 [无]
  - 文中举的示例场景：[简述，如"批量审批订单系统"]

请确认：
  1. 上述示例场景是否包含工作内部信息？
  2. 是否同意现在 push 到公开仓库？

得到您明确同意后我才会调用 publish.py。
```

## 四、命中后的处理流程

如果扫描有命中：

1. **停止 publish**，不能边推边问
2. 把命中行号和内容列给用户
3. 给出替换建议（参考 `posting-conventions.md` 的替换表）
4. 替换后**重新跑扫描**，直到 0 命中
5. 再请用户确认

## 五、不能依赖事后清理的理由

- 一旦 push，commit 进入公开 git 历史，`git clone` 任何人都能 `git log` 翻到
- 本 skill 安全约束**禁止 `git push --force`**，意味着无法重写历史
- 即使强行 force push 改写历史，GitHub 仍会通过 reflog 保留旧 commit 一段时间
- 已经被搜索引擎或 archive.org 抓取过的内容，事后已无法收回

**结论：事前审查的成本是 30 秒，事后兜底的成本可能是几个月，不可对换。**

## 六、个例豁免

如果用户明确说"这篇就是要写公司内部技术博客"或"这篇内容已经过公司公开材料披露"——

- agent 仍要**显式记录**这次豁免的理由（写到 commit message 或对话里），保留追溯
- 仍要做基础扫描（邮箱、内网 IP 这类绝对不能写的），不能因为豁免就完全跳过
- 豁免不能由 agent 自己决定，必须由用户明确发起

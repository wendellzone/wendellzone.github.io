---
title: 你好，世界
date: 2026-05-11
tags: [杂记]
summary: 第一篇文章，介绍这个博客的技术栈与发文流程。
---

写博客的人多半都有写过第一篇《你好，世界》的经验。这个站点就从这里开始。

## 技术栈

- **静态 SPA**：一个 `index.html`，没有构建步骤，打开即用
- **Markdown 渲染**：[marked](https://marked.js.org/) + [DOMPurify](https://github.com/cure53/DOMPurify)
- **代码高亮**：[highlight.js](https://highlightjs.org/)
- **PlantUML**：本地 `pako` 压缩 + 自定义 base64 编码，调 `plantuml.com/plantuml/svg/` 拿回 SVG
- **托管**：GitHub Pages（`wendellzone.github.io`）

发一篇新文章只做三件事：

1. 在 `posts/` 下写一个 `my-post.md`
2. 在 `posts/index.json` 加一条元数据
3. `git push`

没有构建，没有 CI，GitHub Pages 部署秒级生效。

## 这个博客会写什么

- **项目复盘**：做过的事情拆开讲，流程 / 设计决策 / 取舍
- **技术笔记**：读源码、踩坑、小工具
- **日常思考**：不是技术的那种

## 代码高亮示例

```go
func encryptAndUpload(ctx context.Context, data []byte) error {
    kek, err := kms.Derive(ctx, userID)
    if err != nil {
        return err
    }
    ciphertext := aesGCM(kek, data)
    return oss.Put(ctx, key, ciphertext)
}
```

```json
{
  "blog": "wendellzone.github.io",
  "posts": 3,
  "built_with": "vanilla JS"
}
```

下一篇见。

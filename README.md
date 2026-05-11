# wendellzone.github.io

Wendell 的个人博客。纯静态单页应用，托管在 GitHub Pages。

线上：**https://wendellzone.github.io/**

## 技术栈

- 单文件 `index.html`（无构建）
- Markdown：marked@4.3.0 + DOMPurify@3.1.6
- 代码高亮：highlight.js@11.9.0
- PlantUML：pako@2.1.0 + 自定义 base64，调 plantuml.com 渲 SVG
- 路由：hash 路由（`#/`、`#/post/<slug>`、`#/about`）

## 发一篇新文章

1. 在 `posts/` 下新建 `<slug>.md`，开头用 YAML frontmatter：

   ```markdown
   ---
   title: 我的新文章
   date: 2026-05-20
   tags: [标签一, 标签二]
   summary: 一句话摘要
   ---

   正文……
   ```

2. 在 `posts/index.json` 数组里加一条（和 frontmatter 同字段 + `slug`）：

   ```json
   {
     "slug": "my-new-post",
     "title": "我的新文章",
     "date": "2026-05-20",
     "tags": ["标签一", "标签二"],
     "summary": "一句话摘要"
   }
   ```

3. `git push`，GitHub Pages 几十秒内上线。

## 特殊语法支持

**PlantUML 代码块**会被自动渲染成 SVG：

    ```plantuml
    @startuml
    Alice -> Bob: hi
    @enduml
    ```

**代码高亮**覆盖主流语言（go / js / python / rust / shell / json / yaml …），走 `highlight.js` common 包。

## 本地预览

```bash
cd wendellzone.github.io
python3 -m http.server 8080
```

打开 http://localhost:8080 。

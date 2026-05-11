---
name: blog-post
description: This skill should be used whenever the user wants to publish, edit, or delete articles on the personal blog at wendellzone.github.io. Trigger phrases include "发一篇博客 / 博客加文章 / 写篇博客", "改一下博客文章 / 更新博客", "删掉那篇博客文章", "列出我的博客文章". The skill manages the local Markdown sources under wendellzone-blog/posts/, keeps posts/index.json in sync, and pushes every change to GitHub so the Pages site updates automatically within a minute.
agent_created: true
---

# blog-post

Manage the personal blog hosted at <https://wendellzone.github.io/> (repo: `wendellzone/wendellzone.github.io`).

Every operation creates a git commit (author `wendellzone <wendellzone@users.noreply.github.com>`) and pushes to `origin main`, so the full edit history is preserved and the site rebuilds automatically.

## When to use this skill

Activate this skill on any of these intents:

- Publishing a new article: "发篇博客", "写一篇新博客", "add a post", "新建博客文章"
- Editing an existing article: "改博客里那篇 X", "把博客 xxx 的标题换成 yyy", "update post"
- Removing an article: "删掉博客的 xxx", "删除那篇博客"
- Listing articles: "列出我所有博客文章", "show my blog posts"

Do NOT activate for:
- Editing `index.html`, CSS, or site structure — those are plain `git` edits, use normal tools
- The other personal site `jiashuwang0/live-preview` — this skill is blog-only

## Prerequisites

Before running any subcommand, verify:

1. `gh auth status -h github.com` shows `wendellzone` is the active account. If active is `jiashuwang0`, run `gh auth switch --user wendellzone` and ask the user to confirm.
2. Local repo exists at `~/WorkBuddy/2026-05-09-task-1/wendellzone-blog/`. Override with `--repo <path>` or env `BLOG_REPO` if the user has moved it.
3. Working tree is clean (`git status` inside the repo shows nothing). If dirty, stop and surface what's uncommitted before mutating anything.

## How to execute

Always call `scripts/publish.py`, never hand-edit the markdown + index.json + git directly. The script is the single source of truth for keeping `posts/*.md` and `posts/index.json` consistent.

### New post

```bash
scripts/publish.py new \
  --title "文章标题" \
  --tags "Go,后端" \
  --summary "一句话摘要" \
  --body-file /tmp/body.md
```

Options:
- `--title` required
- `--slug` optional. If omitted, auto-generated from title (English kebab-case; pure-Chinese title falls back to `post-<timestamp>`)
- `--date` defaults to today (`YYYY-MM-DD`)
- `--tags` comma-separated
- `--summary` one-line summary shown on the list page
- `--body-file` path to a `.md` file containing the article body. If the file already has a frontmatter block, it will be stripped and replaced with one generated from the CLI arguments. Prefer writing the body to a temp file (e.g. `/tmp/new-post.md`) rather than passing huge strings on the command line.
- `--no-push` to skip git add/commit/push (useful for dry-run or when the user wants to review first)

Recommended flow when the user gives just a topic:
1. Ask for title, tags, and summary if not provided.
2. Draft the markdown body to `/tmp/<slug>.md`.
3. Call `publish.py new ... --body-file /tmp/<slug>.md`.
4. Report the live URL: `https://wendellzone.github.io/#/post/<slug>`.

### Edit post

```bash
# Change frontmatter only
scripts/publish.py edit <slug> --title "新标题" --tags "Go,工具" --summary "…"

# Replace the body (with or without a frontmatter in the source file)
scripts/publish.py edit <slug> --body-file /tmp/new-body.md
```

Behavior:
- Frontmatter fields not passed as args keep their old values.
- `--body-file` replaces the article body. If the file starts with `---`, that frontmatter is adopted verbatim; otherwise the existing frontmatter is preserved and only the body changes.
- `index.json` is re-synced from the resulting frontmatter.

### Delete post

```bash
scripts/publish.py delete <slug>
```

Soft delete:
- The `.md` file is moved to `_trash/<slug>-<timestamp>.md` (not hard-deleted), so the content remains recoverable via git history.
- The slug is removed from `posts/index.json`.
- A commit `post: remove '<title>' (<slug>)` is pushed.

To undo a delete: `git mv _trash/<slug>-<ts>.md posts/<slug>.md` and re-add the entry to `index.json`, then `publish.py edit <slug>` to sync.

### List posts

```bash
scripts/publish.py list
```

Dumps slug / title / date / tags / summary / readingTime for all entries in `index.json`.

### Resync reading time

```bash
scripts/publish.py resync
```

Recompute `readingTime` for every post by actually reading its `.md` body, write back to `index.json`, commit and push. Run this after bulk-editing markdown files by hand, or if you suspect `index.json` drifted out of sync. Safe to run anytime — commits only if something changed.

## Conventions and invariants

Read `references/posting-conventions.md` once per session before drafting content. Highlights:

- Frontmatter shape is fixed: `title / date / tags / summary`. No extra keys in the markdown file.
- `index.json` entries carry an extra `readingTime` field computed by the script (do not hand-edit); use `resync` if it drifts.
- `date` is ISO `YYYY-MM-DD`.
- `tags` is a short flat list of topical labels; avoid time-based tags.
- `summary` is ≤ 50 Chinese chars / 80 English chars, plain text (no markdown).
- Markdown body supports GFM, code highlighting (`highlight.js`), and PlantUML fenced blocks:

  <pre>
  ```plantuml
  @startuml
  Alice -> Bob: hi
  @enduml
  ```
  </pre>

- First-level `# 标题` inside the body is optional; the site already renders the title from frontmatter. Prefer starting the body with a paragraph.
- Don't reference `posts/*.md` files across articles via relative links — the site uses hash routing, not file paths. Use `[text](#/post/other-slug)` if cross-linking is needed.

## Safety

- **Always** ensure git working tree is clean before mutating (see Prerequisites). The script commits whatever is staged plus its own changes; a dirty tree would mix unrelated edits into the post commit.
- **Confirm with the user** before calling `delete`. Even though it's a soft delete, surfacing the intent prevents the wrong slug from being removed.
- **Never** pass `--force` to git. The script doesn't rewrite history; rebase-on-push handles the case of the remote having newer commits.
- **Don't** expose the real email address. Commits use the `@users.noreply.github.com` alias hardcoded in the script.

## Verifying the deploy

After a push, the GitHub Pages rebuild takes ~30–60s. To verify:

```bash
curl -sI https://wendellzone.github.io/posts/<slug>.md | head -1   # expect HTTP/2 200
```

If the check fails for several minutes, check the Pages build:

```bash
gh api /repos/wendellzone/wendellzone.github.io/pages/builds/latest --jq '.status,.error.message'
```

Common Pages gotcha: if a `.md` returns 404 even though it's committed, verify `.nojekyll` is at the repo root. Without it, Jekyll swallows `.md` files.

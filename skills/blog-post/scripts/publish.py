#!/usr/bin/env python3
"""
blog-post · publish.py

管理 wendellzone.github.io 博客文章的本地+远端状态。零依赖，只需 python3 + git + gh。

子命令：
  list                           列出当前所有文章
  new --title "..." [options]    新建文章
  edit <slug> [options]          修改现有文章的 frontmatter 或正文
  delete <slug>                  删除文章（同步从 index.json 移除）

约定：
  - 仓库路径：~/WorkBuddy/2026-05-09-task-1/wendellzone-blog
    可用 --repo 覆盖，或环境变量 BLOG_REPO
  - 文章文件：<repo>/posts/<slug>.md
  - 索引文件：<repo>/posts/index.json
  - 每次变更自动 git add/commit/push，commit author = wendellzone <wendellzone@users.noreply.github.com>

示例：
  # 新建
  publish.py new --title "我的新文章" --tags 前端,Go --summary "讲点前端工具"
  # 新建时直接带正文（读文件）
  publish.py new --title "新" --body-file /tmp/a.md
  # 改标题
  publish.py edit my-post --title "改后的新标题"
  # 改正文（用本地文件整篇替换）
  publish.py edit my-post --body-file /tmp/new.md
  # 删除
  publish.py delete my-post
  # 列出
  publish.py list
"""
import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path


# ---------- 基础工具 ----------

DEFAULT_REPO = Path.home() / "WorkBuddy" / "2026-05-09-task-1" / "wendellzone-blog"
AUTHOR_NAME  = "wendellzone"
AUTHOR_EMAIL = "wendellzone@users.noreply.github.com"


def repo_root(cli_repo: str | None) -> Path:
    if cli_repo:
        p = Path(cli_repo).expanduser().resolve()
    elif os.environ.get("BLOG_REPO"):
        p = Path(os.environ["BLOG_REPO"]).expanduser().resolve()
    else:
        p = DEFAULT_REPO
    if not (p / "posts").is_dir():
        die(f"仓库路径不对或缺少 posts/: {p}")
    return p


def die(msg: str, code: int = 1) -> None:
    print(f"✗ {msg}", file=sys.stderr)
    sys.exit(code)


def run(cmd: list[str], cwd: Path, *, check: bool = True, env: dict | None = None) -> subprocess.CompletedProcess:
    env_full = {**os.environ, **(env or {})}
    r = subprocess.run(cmd, cwd=cwd, env=env_full, capture_output=True, text=True)
    if check and r.returncode != 0:
        die(f"命令失败 {' '.join(cmd)}\nstdout: {r.stdout}\nstderr: {r.stderr}")
    return r


def git_env() -> dict:
    return {
        "GIT_AUTHOR_NAME":     AUTHOR_NAME,
        "GIT_AUTHOR_EMAIL":    AUTHOR_EMAIL,
        "GIT_COMMITTER_NAME":  AUTHOR_NAME,
        "GIT_COMMITTER_EMAIL": AUTHOR_EMAIL,
    }


def git_commit_and_push(repo: Path, message: str) -> None:
    # 检查是否有变动
    diff = run(["git", "status", "--porcelain"], cwd=repo, check=False)
    if not diff.stdout.strip():
        print("  (nothing to commit)")
        return
    run(["git", "add", "-A"], cwd=repo)
    run(["git", "commit", "-m", message], cwd=repo, env=git_env())
    push = run(["git", "push"], cwd=repo, check=False)
    if push.returncode != 0:
        # 先尝试拉后再推，避免远端有新提交
        pull = run(["git", "pull", "--rebase"], cwd=repo, check=False)
        if pull.returncode != 0:
            die(f"git push 失败且 rebase 失败:\n{push.stderr}\n---\n{pull.stderr}")
        push2 = run(["git", "push"], cwd=repo, check=False)
        if push2.returncode != 0:
            die(f"git push 仍失败:\n{push2.stderr}")
    print(f"✓ pushed: {message}")


def slugify(title: str) -> str:
    # 英文直接 kebab-case，中文转拼音字母集外的去掉后用时间戳兜底
    s = unicodedata.normalize("NFKC", title).strip().lower()
    s = re.sub(r"[^a-z0-9\u4e00-\u9fa5\-_ ]+", "", s)
    s = re.sub(r"[\s_]+", "-", s).strip("-")
    # 如果纯中文 slug，用 post-<date>-<hash> 替代避免 URL 不友好
    if not re.search(r"[a-z0-9]", s):
        stamp = dt.datetime.now().strftime("%Y%m%d%H%M")
        return f"post-{stamp}"
    return s[:60] or f"post-{dt.datetime.now().strftime('%Y%m%d%H%M')}"


def today_str() -> str:
    return dt.date.today().isoformat()


def reading_time(md: str) -> int:
    """中文 350 字/分 + 英文 250 词/分，向上取整，最少 1 分钟"""
    if not md:
        return 1
    stripped = re.sub(r"```[\s\S]*?```", "", md)
    stripped = re.sub(r"`[^`]*`", "", stripped)
    cn = len(re.findall(r"[\u4e00-\u9fa5]", stripped))
    en = len(re.findall(r"[A-Za-z]+(?:['\-][A-Za-z]+)*", stripped))
    import math
    return max(1, math.ceil(cn / 350 + en / 250))


# ---------- frontmatter 解析 ----------

FRONTMATTER_RE = re.compile(r"^---\n([\s\S]*?)\n---\n?", re.MULTILINE)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """支持最小子集 YAML：key: value, 列表写成 [a, b] 或多行缩进以 - 开头"""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    block = m.group(1)
    data: dict = {}
    current_key = None
    for line in block.splitlines():
        if not line.strip():
            continue
        if line.startswith("  - ") and current_key:
            data[current_key].append(line[4:].strip())
            continue
        if ":" in line:
            k, _, v = line.partition(":")
            k = k.strip()
            v = v.strip()
            if v == "":
                data[k] = []
                current_key = k
                continue
            if v.startswith("[") and v.endswith("]"):
                inner = v[1:-1].strip()
                data[k] = [x.strip().strip("'\"") for x in inner.split(",")] if inner else []
            else:
                data[k] = v.strip().strip("'\"")
            current_key = None
    body = text[m.end():]
    return data, body


def format_frontmatter(meta: dict) -> str:
    lines = ["---"]
    for k in ("title", "date", "tags", "summary"):
        if k not in meta:
            continue
        v = meta[k]
        if isinstance(v, list):
            if v:
                lines.append(f"{k}: [{', '.join(v)}]")
            else:
                lines.append(f"{k}: []")
        else:
            lines.append(f"{k}: {v}")
    lines.append("---\n")
    return "\n".join(lines)


# ---------- 操作 ----------

def cmd_list(repo: Path, _args):
    idx_path = repo / "posts" / "index.json"
    index = json.loads(idx_path.read_text(encoding="utf-8"))
    index.sort(key=lambda p: p.get("date", ""), reverse=True)
    print(f"共 {len(index)} 篇文章：\n")
    for p in index:
        tags = ", ".join(p.get("tags", []))
        rt = p.get("readingTime")
        rt_str = f"  (~{rt} 分钟)" if rt else ""
        print(f"  [{p['date']}] {p['slug']:<28} {p['title']}{rt_str}")
        if tags:
            print(f"              tags: {tags}")
        if p.get("summary"):
            print(f"              summary: {p['summary']}")
    print()


def cmd_resync(repo: Path, args):
    """重算所有文章的 readingTime 字段（需要正文文件存在）"""
    idx_path = repo / "posts" / "index.json"
    index = json.loads(idx_path.read_text(encoding="utf-8"))
    changed = 0
    for item in index:
        post_path = repo / "posts" / f"{item['slug']}.md"
        if not post_path.exists():
            print(f"  skip (missing file): {item['slug']}")
            continue
        _, body = parse_frontmatter(post_path.read_text(encoding="utf-8"))
        rt = reading_time(body)
        if item.get("readingTime") != rt:
            item["readingTime"] = rt
            changed += 1
            print(f"  update {item['slug']}: readingTime = {rt} 分钟")
    idx_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"✓ 共更新 {changed} 条")
    if changed and not args.no_push:
        git_commit_and_push(repo, "chore: resync readingTime for all posts")


def cmd_new(repo: Path, args):
    if not args.title:
        die("--title 必填")

    slug = args.slug or slugify(args.title)
    date = args.date or today_str()
    tags = [t.strip() for t in (args.tags or "").split(",") if t.strip()]
    summary = args.summary or ""

    post_path = repo / "posts" / f"{slug}.md"
    if post_path.exists():
        die(f"文章已存在：{post_path}。用 `edit {slug}` 修改；或换个 slug。")

    # 正文来源
    if args.body_file:
        body = Path(args.body_file).read_text(encoding="utf-8")
        # 如果用户传来的文件已经有 frontmatter，就剥掉（下面会重写）
        _, body_only = parse_frontmatter(body)
        body = body_only
    else:
        body = f"# {args.title}\n\n（正文待写）\n"

    meta = {
        "title": args.title,
        "date": date,
        "tags": tags,
        "summary": summary,
    }
    content = format_frontmatter(meta) + "\n" + body
    post_path.write_text(content, encoding="utf-8")

    # 更新 index.json
    idx_path = repo / "posts" / "index.json"
    index = json.loads(idx_path.read_text(encoding="utf-8"))
    index = [p for p in index if p.get("slug") != slug]  # 去重
    index.append({
        "slug": slug, "title": args.title, "date": date,
        "tags": tags, "summary": summary,
        "readingTime": reading_time(body),
    })
    index.sort(key=lambda p: p.get("date", ""), reverse=True)
    idx_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"✓ 新建：{post_path}")
    if not args.no_push:
        git_commit_and_push(repo, f"post: add '{args.title}' ({slug})")
    else:
        print("  (--no-push 模式，未推送)")


def cmd_edit(repo: Path, args):
    slug = args.slug
    post_path = repo / "posts" / f"{slug}.md"
    if not post_path.exists():
        die(f"文章不存在：{post_path}")

    # 用 body-file 整篇替换
    if args.body_file:
        new_body = Path(args.body_file).read_text(encoding="utf-8")
        fm_check, body_only = parse_frontmatter(new_body)
        if fm_check:
            # 如果新文件自带 frontmatter，就整体替换
            post_path.write_text(new_body if new_body.endswith("\n") else new_body + "\n", encoding="utf-8")
            meta = fm_check
            body = body_only
        else:
            old_text = post_path.read_text(encoding="utf-8")
            meta, _ = parse_frontmatter(old_text)
            body = new_body
            post_path.write_text(format_frontmatter(meta) + "\n" + body, encoding="utf-8")
    else:
        old_text = post_path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(old_text)
        if args.title is not None:   meta["title"] = args.title
        if args.date is not None:    meta["date"] = args.date
        if args.summary is not None: meta["summary"] = args.summary
        if args.tags is not None:
            meta["tags"] = [t.strip() for t in args.tags.split(",") if t.strip()]
        post_path.write_text(format_frontmatter(meta) + "\n" + body, encoding="utf-8")

    # 回写 index.json
    idx_path = repo / "posts" / "index.json"
    index = json.loads(idx_path.read_text(encoding="utf-8"))
    # 重新计算 reading time（正文可能变了）
    final_text = post_path.read_text(encoding="utf-8")
    _, final_body = parse_frontmatter(final_text)
    rt = reading_time(final_body)
    for item in index:
        if item["slug"] == slug:
            item["title"]       = meta.get("title", item["title"])
            item["date"]        = meta.get("date", item["date"])
            item["tags"]        = meta.get("tags", item.get("tags", []))
            item["summary"]     = meta.get("summary", item.get("summary", ""))
            item["readingTime"] = rt
            break
    else:
        # 文件存在但索引没这条，顺手补上
        index.append({
            "slug": slug, "title": meta.get("title", slug),
            "date": meta.get("date", today_str()),
            "tags": meta.get("tags", []), "summary": meta.get("summary", ""),
            "readingTime": rt,
        })
    index.sort(key=lambda p: p.get("date", ""), reverse=True)
    idx_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"✓ 已更新：{post_path}")
    if not args.no_push:
        git_commit_and_push(repo, f"post: update '{meta.get('title', slug)}' ({slug})")
    else:
        print("  (--no-push 模式，未推送)")


def cmd_delete(repo: Path, args):
    slug = args.slug
    post_path = repo / "posts" / f"{slug}.md"
    idx_path  = repo / "posts" / "index.json"

    index = json.loads(idx_path.read_text(encoding="utf-8"))
    meta = next((p for p in index if p["slug"] == slug), None)
    title_for_msg = (meta or {}).get("title", slug)

    existed_file = post_path.exists()
    existed_index = meta is not None
    if not existed_file and not existed_index:
        die(f"没有找到文章：{slug}")

    # 软删：移到 _trash/，保留历史可恢复
    if existed_file:
        trash_dir = repo / "_trash"
        trash_dir.mkdir(exist_ok=True)
        target = trash_dir / f"{slug}-{dt.datetime.now().strftime('%Y%m%d%H%M%S')}.md"
        shutil.move(str(post_path), str(target))
        print(f"✓ 已移至回收站：{target.relative_to(repo)}")

    new_index = [p for p in index if p["slug"] != slug]
    idx_path.write_text(json.dumps(new_index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"✓ 已从 index.json 移除（剩 {len(new_index)} 篇）")

    if not args.no_push:
        git_commit_and_push(repo, f"post: remove '{title_for_msg}' ({slug})")
    else:
        print("  (--no-push 模式，未推送)")


# ---------- CLI ----------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Manage wendellzone.github.io blog posts")
    p.add_argument("--repo", help="博客仓库本地路径（默认 ~/WorkBuddy/2026-05-09-task-1/wendellzone-blog）")
    p.add_argument("--no-push", action="store_true", help="只改本地，不自动 git push")

    sub = p.add_subparsers(dest="cmd", required=True)

    sp_list = sub.add_parser("list", help="列出所有文章")

    sp_resync = sub.add_parser("resync", help="重算所有文章的 readingTime（修 index.json）")

    sp_new = sub.add_parser("new", help="新建文章")
    sp_new.add_argument("--title", required=True)
    sp_new.add_argument("--slug",  help="URL slug，不传则从标题自动生成")
    sp_new.add_argument("--date",  help="YYYY-MM-DD，不传则用今天")
    sp_new.add_argument("--tags",  help="逗号分隔，例：Go,后端")
    sp_new.add_argument("--summary")
    sp_new.add_argument("--body-file", help="正文 markdown 文件路径；支持已带 frontmatter，frontmatter 会被本命令重写")

    sp_edit = sub.add_parser("edit", help="修改现有文章")
    sp_edit.add_argument("slug")
    sp_edit.add_argument("--title")
    sp_edit.add_argument("--date")
    sp_edit.add_argument("--tags")
    sp_edit.add_argument("--summary")
    sp_edit.add_argument("--body-file", help="用该文件整篇替换正文（可含 frontmatter）")

    sp_del = sub.add_parser("delete", help="删除文章")
    sp_del.add_argument("slug")

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    repo = repo_root(args.repo)
    handlers = {"list": cmd_list, "new": cmd_new, "edit": cmd_edit, "delete": cmd_delete, "resync": cmd_resync}
    handlers[args.cmd](repo, args)


if __name__ == "__main__":
    main()

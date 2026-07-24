#!/usr/bin/env python3
"""灰域 / Gray Domain — 靜態小說網站建置腳本（零依賴）。

用法：
    python3 build.py

流程：
    1. 掃描 chapters/*.md（依檔名排序，建議命名 ep01.md, ep02.md ...）
    2. 每一話轉成排版好的 HTML（chapters/epNN.html）
    3. 產生 index.html 目錄頁，並串好上一話／下一話導覽

Markdown 慣例（作者的排版語彙，會自動處理）：
    # 標題            → 章節標題（自動去掉《灰域》與「・」後綴，例：第一話）
    ---               → 場景分隔線
    *   *   *         → 較大的段落／視角切換（星號裝飾）
    **文字**          → 粗體（心聲／內心獨白）
    空行分段          → 段落
"""

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHAPTERS_DIR = ROOT / "chapters"

NOVEL_TITLE = "灰域"
NOVEL_TITLE_EN = "Gray Domain"
NOVEL_SUBTITLE = ""  # 想放一句話介紹可填這裡

# ---------------------------------------------------------------------------
# Markdown 解析
# ---------------------------------------------------------------------------

RULE_RE = re.compile(r"^-{3,}$")
ASTERISM_RE = re.compile(r"^\s*\*(\s+\*)+\s*$")  # 例如：*    *    *
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def clean_title(raw: str) -> str:
    """把 H1 清成給讀者看的章節標題。

    '《灰域》第一話・散文稿' → '第一話'
    '第二話' → '第二話'
    """
    t = raw.strip()
    t = re.sub(r"《[^》]*》", "", t)      # 去掉《灰域》這類書名號
    t = t.split("・")[0]                  # 去掉「・散文稿」這類後綴
    return t.strip()


def inline(text: str) -> str:
    """行內語法：先跳脫 HTML，再處理 **粗體**。"""
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return text


def parse_body(lines):
    """把去掉 H1 後的正文行，轉成 block 清單。

    每個 block 是 ('rule',) / ('asterism',) / ('h', level, text) / ('p', text)。
    """
    blocks = []
    buf = []

    def flush():
        if buf:
            # CJK 段落內換行直接相接（不補空格）
            text = "".join(s.strip() for s in buf)
            blocks.append(("p", text))
            buf.clear()

    for line in lines:
        stripped = line.strip()
        if stripped == "":
            flush()
            continue
        if ASTERISM_RE.match(stripped):
            flush()
            blocks.append(("asterism",))
            continue
        if RULE_RE.match(stripped):
            flush()
            blocks.append(("rule",))
            continue
        m = HEADING_RE.match(stripped)
        if m:
            flush()
            blocks.append(("h", len(m.group(1)), m.group(2).strip()))
            continue
        buf.append(line)
    flush()

    # 相鄰的分隔符收斂成一個；星號優先於細線
    collapsed = []
    for b in blocks:
        if b[0] in ("rule", "asterism") and collapsed and collapsed[-1][0] in ("rule", "asterism"):
            if b[0] == "asterism":
                collapsed[-1] = b
            continue
        collapsed.append(b)

    # 去掉開頭／結尾多餘的分隔符
    while collapsed and collapsed[0][0] in ("rule", "asterism"):
        collapsed.pop(0)
    while collapsed and collapsed[-1][0] in ("rule", "asterism"):
        collapsed.pop()

    return collapsed


def render_blocks(blocks) -> str:
    out = []
    for b in blocks:
        if b[0] == "rule":
            out.append('<hr class="scene">')
        elif b[0] == "asterism":
            out.append('<div class="asterism" aria-hidden="true">✳&emsp;✳&emsp;✳</div>')
        elif b[0] == "h":
            level = min(max(b[1], 2), 4)
            out.append(f"<h{level}>{inline(b[2])}</h{level}>")
        else:
            out.append(f"<p>{inline(b[1])}</p>")
    return "\n".join(out)


def load_chapter(md_path: Path):
    raw = md_path.read_text(encoding="utf-8")
    lines = raw.split("\n")

    title = md_path.stem
    body_lines = []
    found_title = False
    for line in lines:
        m = HEADING_RE.match(line.strip())
        if m and not found_title and len(m.group(1)) == 1:
            title = clean_title(m.group(2))
            found_title = True
            continue
        body_lines.append(line)

    blocks = parse_body(body_lines)
    return {
        "slug": md_path.stem,
        "title": title,
        "html": render_blocks(blocks),
    }


# ---------------------------------------------------------------------------
# HTML 模板
# ---------------------------------------------------------------------------

def chapter_page(ch, prev_ch, next_ch) -> str:
    nav_top = _nav(prev_ch, next_ch, "../index.html")
    nav_bottom = _nav(prev_ch, next_ch, "../index.html")
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(ch['title'])}｜{NOVEL_TITLE}</title>
<link rel="stylesheet" href="../assets/style.css">
</head>
<body class="reader">
<div class="toolbar">
  <a class="home" href="../index.html">← 目錄</a>
  <div class="controls">
    <button data-action="font-dec" title="縮小字級">A−</button>
    <button data-action="font-inc" title="放大字級">A+</button>
    <button data-action="theme" title="切換明暗">☾</button>
  </div>
</div>

<article class="chapter">
  <header class="chapter-head">
    <p class="novel-name">{NOVEL_TITLE}</p>
    <h1>{html.escape(ch['title'])}</h1>
  </header>

  <nav class="chapter-nav top">{nav_top}</nav>

  <div class="prose">
{ch['html']}
  </div>

  <nav class="chapter-nav bottom">{nav_bottom}</nav>
</article>

<footer class="site-foot">{NOVEL_TITLE} · {NOVEL_TITLE_EN}</footer>
<script src="../assets/reader.js"></script>
</body>
</html>
"""


def _nav(prev_ch, next_ch, index_href) -> str:
    left = (
        f'<a class="nav-prev" href="{prev_ch["slug"]}.html">← {html.escape(prev_ch["title"])}</a>'
        if prev_ch else '<span class="nav-prev disabled">← 沒有上一話</span>'
    )
    mid = f'<a class="nav-index" href="{index_href}">目錄</a>'
    right = (
        f'<a class="nav-next" href="{next_ch["slug"]}.html">{html.escape(next_ch["title"])} →</a>'
        if next_ch else '<span class="nav-next disabled">敬請期待 →</span>'
    )
    return f"{left}{mid}{right}"


def index_page(chapters) -> str:
    items = []
    for i, ch in enumerate(chapters, 1):
        items.append(
            f'<li><a href="chapters/{ch["slug"]}.html">'
            f'<span class="ep-no">{i:02d}</span>'
            f'<span class="ep-title">{html.escape(ch["title"])}</span>'
            f"</a></li>"
        )
    listing = "\n".join(items) if items else '<li class="empty">尚未發佈章節</li>'
    subtitle = f'<p class="tagline">{html.escape(NOVEL_SUBTITLE)}</p>' if NOVEL_SUBTITLE else ""
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{NOVEL_TITLE}｜{NOVEL_TITLE_EN}</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body class="home">
<div class="toolbar">
  <span class="home-mark">{NOVEL_TITLE}</span>
  <div class="controls">
    <button data-action="theme" title="切換明暗">☾</button>
  </div>
</div>

<header class="hero">
  <h1 class="novel-title">{NOVEL_TITLE}</h1>
  <p class="novel-title-en">{NOVEL_TITLE_EN}</p>
  {subtitle}
</header>

<main class="toc">
  <h2>目錄</h2>
  <ol class="chapter-list">
{listing}
  </ol>
</main>

<footer class="site-foot">{NOVEL_TITLE} · {NOVEL_TITLE_EN}</footer>
<script src="assets/reader.js"></script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def main():
    md_files = sorted(CHAPTERS_DIR.glob("*.md"))
    chapters = [load_chapter(p) for p in md_files]

    for i, ch in enumerate(chapters):
        prev_ch = chapters[i - 1] if i > 0 else None
        next_ch = chapters[i + 1] if i + 1 < len(chapters) else None
        out = CHAPTERS_DIR / f"{ch['slug']}.html"
        out.write_text(chapter_page(ch, prev_ch, next_ch), encoding="utf-8")
        print(f"  chapters/{ch['slug']}.html  ← {ch['title']}")

    (ROOT / "index.html").write_text(index_page(chapters), encoding="utf-8")
    print(f"  index.html  ({len(chapters)} 話)")
    print("完成。")


if __name__ == "__main__":
    main()

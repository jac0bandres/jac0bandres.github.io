#!/usr/bin/env python3
"""Build crawlable blog pages from Markdown sources."""

from __future__ import annotations

import html
import json
import math
import re
from datetime import date
from pathlib import Path
from urllib.parse import quote, unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "blog" / "posts"
BLOG_DIR = ROOT / "blog"
SITE_URL = "https://jacobandres.com"
AUTHOR = "Jacob Andrés Navarrete"
RAW_IMAGE_PREFIX = "https://raw.githubusercontent.com/jac0bandres/jac0bandres.github.io/main/blog/images/"


def parse_source(path: Path) -> tuple[dict, str]:
    source = path.read_text(encoding="utf-8").lstrip("\ufeff\r\n")
    if not source.startswith("---\n"):
        raise ValueError(f"{path}: missing YAML front matter")
    _, front_matter, body = source.split("---", 2)
    metadata: dict[str, object] = {}
    active_list: str | None = None
    for raw_line in front_matter.splitlines():
        if not raw_line.strip():
            continue
        list_item = re.match(r"^\s+-\s+(.+)$", raw_line)
        if list_item and active_list:
            metadata[active_list].append(list_item.group(1).strip())
            continue
        key, separator, value = raw_line.partition(":")
        if not separator:
            raise ValueError(f"{path}: unsupported front matter line: {raw_line}")
        key, value = key.strip(), value.strip()
        if value:
            metadata[key] = value
            active_list = None
        else:
            metadata[key] = []
            active_list = key
    required = {"title", "slug", "description", "date", "image", "tags"}
    missing = sorted(required - metadata.keys())
    if missing:
        raise ValueError(f"{path}: missing metadata: {', '.join(missing)}")
    return metadata, body.lstrip()


def normalize_title(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def remove_duplicate_title(body: str, title: str) -> str:
    match = re.match(r"^(#{1,6})\s+(.+?)\s*\n+", body)
    if match and normalize_title(match.group(2)) == normalize_title(title):
        return body[match.end():]
    return body


def localize_images(body: str) -> str:
    body = re.sub(
        r"!\[\[([^\]]+)\]\]",
        lambda match: f"![{Path(match.group(1)).stem}](/blog/images/{quote(match.group(1))})",
        body,
    )

    def replace_image(match: re.Match[str]) -> str:
        alt, target = match.group(1), match.group(2).strip()
        if target.startswith(RAW_IMAGE_PREFIX):
            filename = unquote(target[len(RAW_IMAGE_PREFIX):])
            target = f"/blog/images/{quote(filename)}"
        elif target.startswith("../images/") or target.startswith("images/"):
            prefix = "../images/" if target.startswith("../images/") else "images/"
            filename = unquote(target[len(prefix):])
            target = f"/blog/images/{quote(filename)}"
        elif not urlparse(target).scheme and not target.startswith("/"):
            target = f"/blog/images/{quote(unquote(target))}"
        return f"![{alt}]({target})"

    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace_image, body)


def reading_minutes(body: str) -> int:
    prose = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
    prose = re.sub(r"[`*_#>\[\]()$]", " ", prose)
    return max(1, math.ceil(len(prose.split()) / 220))


def render_inline(value: str) -> str:
    rendered = html.escape(value, quote=False)
    rendered = re.sub(
        r"`([^`]+)`",
        lambda match: f"<code>{match.group(1)}</code>",
        rendered,
    )
    rendered = re.sub(
        r"!\[([^\]]*)\]\(([^)]+)\)",
        lambda match: (
            f'<img src="{match.group(2)}" alt="{html.escape(match.group(1), quote=True)}" '
            'loading="lazy" decoding="async">'
        ),
        rendered,
    )
    rendered = re.sub(
        r"(?<!!)\[([^\]]+)\]\(([^)]+)\)",
        lambda match: f'<a href="{match.group(2)}">{match.group(1)}</a>',
        rendered,
    )
    rendered = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", rendered)
    rendered = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", rendered)
    rendered = re.sub(r"(?<!\w)_([^_]+?)_(?!\w)", r"<em>\1</em>", rendered)
    if re.fullmatch(r"https?://[^\s]+", rendered):
        rendered = f'<a href="{rendered}">{rendered}</a>'
    return rendered


def render_markdown(body: str) -> str:
    """Render the Markdown subset used by this site's posts with no dependencies."""
    output: list[str] = []
    paragraph: list[str] = []
    list_type: str | None = None
    in_code = False
    code_language = ""
    code_lines: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            output.append(f"<p>{render_inline(' '.join(paragraph))}</p>")
            paragraph.clear()

    def close_list() -> None:
        nonlocal list_type
        if list_type:
            output.append(f"</{list_type}>")
            list_type = None

    for line in body.splitlines():
        fence = re.match(r"^```\s*([\w+-]*)", line)
        if fence:
            flush_paragraph()
            close_list()
            if in_code:
                language_class = f' class="language-{html.escape(code_language)}"' if code_language else ""
                output.append(f"<pre><code{language_class}>{html.escape(chr(10).join(code_lines))}</code></pre>")
                code_lines.clear()
                in_code = False
            else:
                in_code = True
                code_language = fence.group(1)
            continue
        if in_code:
            code_lines.append(line)
            continue

        if not line.strip():
            flush_paragraph()
            close_list()
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            flush_paragraph()
            close_list()
            level = len(heading.group(1))
            output.append(f"<h{level}>{render_inline(heading.group(2))}</h{level}>")
            continue

        if re.match(r"^\s*(---+|\*\*\*+)\s*$", line):
            flush_paragraph()
            close_list()
            output.append("<hr>")
            continue

        unordered = re.match(r"^\s*[-+*]\s+(.+)$", line)
        ordered = re.match(r"^\s*\d+[.)]\s+(.+)$", line)
        if unordered or ordered:
            flush_paragraph()
            requested = "ul" if unordered else "ol"
            if list_type != requested:
                close_list()
                list_type = requested
                output.append(f"<{list_type}>")
            match = unordered or ordered
            output.append(f"<li>{render_inline(match.group(1))}</li>")
            continue

        quote_match = re.match(r"^>\s?(.*)$", line)
        if quote_match:
            flush_paragraph()
            close_list()
            output.append(f"<blockquote><p>{render_inline(quote_match.group(1))}</p></blockquote>")
            continue

        close_list()
        paragraph.append(line.strip())

    flush_paragraph()
    close_list()
    if in_code:
        language_class = f' class="language-{html.escape(code_language)}"' if code_language else ""
        output.append(f"<pre><code{language_class}>{html.escape(chr(10).join(code_lines))}</code></pre>")
    return "\n".join(output)


def iso_date(value: object) -> str:
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def human_date(value: str) -> str:
    return date.fromisoformat(value).strftime("%B %-d, %Y")


def render_post(post: dict) -> str:
    title = html.escape(post["title"])
    description = html.escape(post["description"])
    canonical = f"{SITE_URL}/blog/{post['slug']}/"
    image_url = f"{SITE_URL}{post['image']}"
    tags = "".join(f"<li>{html.escape(tag)}</li>" for tag in post["tags"])
    schema = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post["title"],
        "description": post["description"],
        "image": image_url,
        "datePublished": post["date"],
        "dateModified": post["date"],
        "author": {"@type": "Person", "name": AUTHOR, "url": SITE_URL},
        "publisher": {"@type": "Person", "name": AUTHOR, "url": SITE_URL},
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
        "keywords": post["tags"],
        "wordCount": post["word_count"],
    }
    schema_json = json.dumps(schema, ensure_ascii=False).replace("</", "<\\/")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — Jacob Andrés</title>
  <meta name="description" content="{description}">
  <meta name="author" content="{html.escape(AUTHOR)}">
  <link rel="canonical" href="{canonical}">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{image_url}">
  <meta property="article:published_time" content="{post['date']}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{description}">
  <meta name="twitter:image" content="{image_url}">
  <link rel="alternate" type="application/rss+xml" title="Jacob Andrés — Field Notes" href="{SITE_URL}/feed.xml">
  <link rel="stylesheet" href="/blog/blog.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
  <script type="application/ld+json">{schema_json}</script>
  <script>
    window.MathJax = {{ tex: {{ inlineMath: [['$', '$'], ['\\\\(', '\\\\)']], displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']], processEscapes: true }} }};
  </script>
  <script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>
  <canvas id="complex-plane" aria-hidden="true"></canvas>
  <header class="site-header">
    <a class="site-name" href="/">JACOB ANDR<span>É</span>S</a>
    <nav aria-label="Primary navigation"><a href="/">Home</a><a href="/blog/">Field notes</a></nav>
  </header>
  <main class="post-shell">
    <article class="post">
      <header class="post-header">
        <a class="back-link" href="/blog/">← Field notes</a>
        <h1>{title}</h1>
        <p class="dek">{description}</p>
        <div class="post-meta"><time datetime="{post['date']}">{human_date(post['date'])}</time><span>{post['reading_minutes']} min read</span></div>
        <ul class="tags" aria-label="Topics">{tags}</ul>
      </header>
      <div class="post-content">{post['content_html']}</div>
    </article>
  </main>
  <footer><a href="mailto:jacob@jacobandres.com">jacob@jacobandres.com</a></footer>
  <script src="/blog/blog.js"></script>
</body>
</html>
"""


def render_index(posts: list[dict]) -> str:
    cards = []
    for post in posts:
        cards.append(f"""
      <article class="post-card">
        <a href="/blog/{post['slug']}/">
          <time datetime="{post['date']}">{human_date(post['date'])}</time>
          <h2>{html.escape(post['title'])}</h2>
          <p>{html.escape(post['description'])}</p>
        </a>
      </article>""")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Field Notes — Jacob Andrés</title>
  <meta name="description" content="Field notes by Jacob Andrés on mathematics, engineering, electronics, and additive manufacturing.">
  <link rel="canonical" href="{SITE_URL}/blog/">
  <meta property="og:type" content="website">
  <meta property="og:title" content="Field Notes — Jacob Andrés">
  <meta property="og:description" content="Writing on mathematics, engineering, electronics, and additive manufacturing.">
  <meta property="og:url" content="{SITE_URL}/blog/">
  <link rel="alternate" type="application/rss+xml" title="Jacob Andrés — Field Notes" href="{SITE_URL}/feed.xml">
  <link rel="stylesheet" href="/blog/blog.css">
</head>
<body>
  <canvas id="complex-plane" aria-hidden="true"></canvas>
  <header class="site-header">
    <a class="site-name" href="/">JACOB ANDR<span>É</span>S</a>
    <nav aria-label="Primary navigation"><a href="/">Home</a><a href="/blog/" aria-current="page">Field notes</a></nav>
  </header>
  <main class="index-shell">
    <h1>Field notes</h1>
    <div class="post-grid">{''.join(cards)}
    </div>
  </main>
  <footer><a href="mailto:jacob@jacobandres.com">jacob@jacobandres.com</a></footer>
  <script src="/blog/blog.js"></script>
</body>
</html>
"""


def write_sitemap(posts: list[dict]) -> None:
    urls = [
        (f"{SITE_URL}/", None),
        (f"{SITE_URL}/blog/", max(post["date"] for post in posts)),
        (f"{SITE_URL}/projects.html", None),
    ]
    urls.extend((f"{SITE_URL}/blog/{post['slug']}/", post["date"]) for post in posts)
    entries = []
    for location, modified in urls:
        lastmod = f"<lastmod>{modified}</lastmod>" if modified else ""
        entries.append(f"  <url><loc>{location}</loc>{lastmod}</url>")
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries)
        + "\n</urlset>\n",
        encoding="utf-8",
    )


def write_feed(posts: list[dict]) -> None:
    items = []
    for post in posts:
        url = f"{SITE_URL}/blog/{post['slug']}/"
        items.append(f"""  <entry>
    <title>{html.escape(post['title'])}</title>
    <link href="{url}"/>
    <id>{url}</id>
    <updated>{post['date']}T12:00:00-04:00</updated>
    <summary>{html.escape(post['description'])}</summary>
  </entry>""")
    updated = max(post["date"] for post in posts)
    feed = f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Jacob Andrés — Field Notes</title>
  <link href="{SITE_URL}/feed.xml" rel="self"/>
  <link href="{SITE_URL}/blog/"/>
  <id>{SITE_URL}/blog/</id>
  <updated>{updated}T12:00:00-04:00</updated>
  <author><name>{AUTHOR}</name></author>
{chr(10).join(items)}
</feed>
"""
    (ROOT / "feed.xml").write_text(feed, encoding="utf-8")


def main() -> None:
    posts = []
    for source_path in POSTS_DIR.glob("*.md"):
        metadata, body = parse_source(source_path)
        metadata["date"] = iso_date(metadata["date"])
        body = remove_duplicate_title(body, metadata["title"])
        body = localize_images(body)
        content_html = render_markdown(body)
        post = {
            **metadata,
            "source": source_path.name,
            "content_html": content_html,
            "reading_minutes": reading_minutes(body),
            "word_count": len(re.sub(r"```.*?```", "", body, flags=re.DOTALL).split()),
        }
        posts.append(post)

    posts.sort(key=lambda post: (post["date"], post["title"]), reverse=True)
    seen_slugs: set[str] = set()
    for post in posts:
        if post["slug"] in seen_slugs:
            raise ValueError(f"Duplicate slug: {post['slug']}")
        seen_slugs.add(post["slug"])
        output_dir = BLOG_DIR / post["slug"]
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "index.html").write_text(render_post(post), encoding="utf-8")

    (BLOG_DIR / "index.html").write_text(render_index(posts), encoding="utf-8")
    manifest = [
        {
            "filename": post["source"],
            "title": post["title"],
            "slug": post["slug"],
            "url": f"/blog/{post['slug']}/",
            "description": post["description"],
            "date": post["date"],
            "image": post["image"],
            "tags": post["tags"],
        }
        for post in posts
    ]
    (POSTS_DIR / "posts.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_sitemap(posts)
    write_feed(posts)
    print(f"Built {len(posts)} posts and blog index")


if __name__ == "__main__":
    main()

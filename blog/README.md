# Publishing field notes

Posts are written in `blog/posts/` and compiled into crawlable HTML pages for GitHub Pages.

## Add a post

Create a Markdown file with this metadata block:

```yaml
---
title: A descriptive post title
slug: descriptive-post-title
description: One specific sentence summarizing the post for search results and link previews.
date: 2026-09-29
image: /blog/images/cover-image.jpg
tags:
  - Mathematics
  - Engineering
---
```

Place local images in `blog/images/`. Use descriptive alternative text:

```markdown
![Four-axis printer following a curved toolpath](/blog/images/toolpath.jpg)
```

Build the site from the repository root:

```bash
python3 scripts/build_blog.py
```

Commit the Markdown source and the generated changes together. The build updates:

- `blog/<slug>/index.html`
- `blog/index.html`
- `blog/posts/posts.json`
- `sitemap.xml`
- `feed.xml`

After the first deployment, add `https://jacobandres.com/sitemap.xml` in Google Search Console. New posts will then appear in the sitemap automatically after each build.

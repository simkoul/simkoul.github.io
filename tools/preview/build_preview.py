#!/usr/bin/env python3
"""Render the real repo pages into one static preview file.

Jekyll cannot build on this machine, so this resolves the small amount of
Liquid the pages actually use and stitches the result into preview.html with
a working tab bar. It reads the real _pages/ and _data/ files, so what you
see is what the site will say.

    python3 tools/preview/build_preview.py

Writes tools/preview/preview.html. Open it in a browser, or publish it.
"""

import os
import re
import html
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

# about-page.md, publications.html and open-tabs.md are retired
# (published: false); their content lives on Home and Research.
PAGES = [
    ("Home",         "about.md"),
    ("Publications", "publications.html"),
    ("Recognitions", "recognitions.md"),
    ("Teaching",     "teaching.html"),
    ("Contact",      "contact.md"),
]

AUTHOR = {
    "googlescholar": "https://scholar.google.com/citations?user=KoitZBkAAAAJ&hl=en",
    "orcid": "https://orcid.org/0009-0003-3502-3165",
    "github": "https://github.com/simkoul",
}


# ---------------------------------------------------------------- yaml (tiny)
def load_yaml_list(path):
    """Enough YAML for our _data files: a list of flat `key: value` maps, an
    inline list (`tags: [a, b]`), and folded/literal block scalars — `note: >`
    followed by an indented paragraph. Jekyll handles all of these; the parser
    has to as well, or the preview quietly misreports the content."""
    if not os.path.exists(path):
        return []

    items, cur, pending = [], None, None   # pending = (key, style, indent, [lines])

    def flush():
        if not pending:
            return
        key, style, _, lines = pending
        text = "\n".join(lines).rstrip("\n")
        if style == ">":
            # folded: blank lines are paragraph breaks, single newlines are spaces
            text = "\n\n".join(" ".join(b.split())
                                for b in re.split(r"\n\s*\n", text) if b.strip())
        cur[key] = text

    for raw in open(path):
        line = raw.rstrip("\n")

        # inside a block scalar: keep consuming while indented (or blank)
        if pending is not None:
            _, _, indent, lines = pending
            if not line.strip():
                lines.append("")
                continue
            if len(line) - len(line.lstrip()) > indent:
                lines.append(line.strip())
                continue
            flush()
            pending = None

        if not line.strip() or line.strip().startswith("#"):
            continue

        if line.startswith("- "):
            if cur:
                items.append(cur)
            cur = {}
            line = "  " + line[2:]

        if cur is None:
            continue

        m = re.match(r"(\s+)([A-Za-z_]+):\s*(.*)$", line)
        if not m:
            continue
        indent, k, v = len(m.group(1)), m.group(2), m.group(3).strip()

        if v in (">", "|", ">-", "|-"):
            pending = (k, v[0], indent, [])
        elif v.startswith("[") and v.endswith("]"):
            cur[k] = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
        else:
            cur[k] = v.strip("'\"")

    flush()
    if cur:
        items.append(cur)
    return items


DATA = {
    "thoughts": load_yaml_list(os.path.join(REPO, "_data/thoughts.yml")),
    "reading": load_yaml_list(os.path.join(REPO, "_data/reading.yml")),
    "photographs": load_yaml_list(os.path.join(REPO, "_data/photographs.yml")),
    "conferences": load_yaml_list(os.path.join(REPO, "_data/conferences.yml")),
}


# ---------------------------------------------------------------- stand-ins
# Shown only while _data/photographs.yml is empty, so the gallery layout can
# still be judged. Mixed aspect ratios on purpose — nothing gets cropped.
DEMO_PHOTOS = [
    ("Fieldwork", 4, 3, "#c9b48a",
     "Coal belt, Jharkhand, 2024. Sampling within a kilometre of an open-cast pit."),
    ("Fieldwork", 3, 4, "#9fb3a4", "Motihari, Bihar, 2023."),
    ("Fieldwork", 3, 2, "#c2a3a0", "Weighing station at dawn."),
    ("Fieldwork", 4, 5, "#a8b2c4", "The enumerator team, second round."),
    ("Elsewhere", 3, 2, "#d3bfa0",
     "Delhi, December 2022. The week the AQI stopped being a number "
     "and started being weather."),
    ("Elsewhere", 4, 5, "#a9c0b8", "Santa Barbara, 2025."),
    ("Elsewhere", 16, 9, "#c8b0b8", "The drive up the 154."),
    ("Elsewhere", 1, 1, "#b6b9a2", "Kitchen table, mid-analysis."),
]


def demo_tile(w, h, colour, label):
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d">'
        '<rect width="%d" height="%d" fill="%s"/>'
        '<text x="50%%" y="50%%" font-family="Inter,sans-serif" font-size="%.0f" '
        'fill="rgba(35,42,51,.4)" text-anchor="middle" dominant-baseline="middle">'
        '%s</text></svg>'
        % (w * 100, h * 100, w * 100, h * 100, colour, min(w, h) * 16, label)
    )
    return "data:image/svg+xml," + urllib.parse.quote(svg, safe="")


# ---------------------------------------------------------------- renderers
def render_thought(n, extra_style=""):
    tags = ""
    if n.get("tags"):
        tags = '<div class="tags">%s</div>' % "".join(
            '<span class="tag">%s</span>' % html.escape(t) for t in n["tags"]
        )
    return (
        '<div class="think"%s><span class="when">%s</span>'
        '<div><div class="what">%s</div>%s</div></div>'
        % (extra_style, html.escape(n.get("when", "")), n.get("what", ""), tags)
    )


def render_book(b):
    out = ['<div class="book"><div class="book__title">%s'
           '<span class="book__author">%s</span></div>'
           % (html.escape(b.get("title", "")), html.escape(b.get("author", "")))]
    if b.get("note"):
        out.append('<p class="book__note">%s</p>' % b["note"])
    if b.get("quote"):
        out.append('<blockquote class="book__quote">%s</blockquote>' % b["quote"])
    out.append("</div>")
    return "".join(out)


DEMO_SHOTS = {
    "cottage-health-2026": [("#c6bda8", "Collaborative Research Symposium | Cottage Health Research Institute | Santa Barbara, 2026")],
    "aag-2026": [("#b0bcc6", "Presenting in the Kasperson award session | AAG Annual Meeting | San Francisco, 2026"),
                 ("#c9bcb4", "")],
    "agu-2025": [("#bcc4b6", "Poster session | AGU Annual Meeting | New Orleans, 2025")],
}


def shots_html(slug):
    """The photo strip under one conference citation. Uses _data/conferences.yml
    when it has rows for this talk, and stand-in tiles when it does not."""
    rows = [r for r in DATA["conferences"] if r.get("talk") == slug]
    if rows:
        items = [(img_uri("/images/conferences/" + r.get("image", "")), r.get("caption", ""))
                 for r in rows]
    else:
        items = [(demo_tile(3, 2, c, "photo"), cap) for c, cap in DEMO_SHOTS.get(slug, [])]
    if not items:
        return ""
    imgs = "".join('<img src="%s" alt="%s">' % (src, html.escape(cap))
                   for src, cap in items)
    cap = next((c for _, c in items if c), "")
    out = '<div class="shots">%s</div>' % imgs
    if cap:
        out += '<p class="shots__cap">%s</p>' % html.escape(cap)
    return out


def gallery_html():
    groups, order = {}, []
    if DATA["photographs"]:
        for p in DATA["photographs"]:
            g = p.get("group", "Photographs")
            if g not in groups:
                groups[g] = []
                order.append(g)
            groups[g].append((img_uri("/images/elsewhere/" + p.get("image", "")),
                              p.get("caption", "")))
        note = ""
    else:
        for g, w, h, c, cap in DEMO_PHOTOS:
            if g not in groups:
                groups[g] = []
                order.append(g)
            groups[g].append((demo_tile(w, h, c, "%d:%d" % (w, h)), cap))
        note = ('<div class="band"><div class="todo">Stand-in tiles, showing the grid at '
                'mixed aspect ratios. Nothing is cropped, and the caption sits under '
                'each photo. Your real photographs go in <code>images/elsewhere/</code> and '
                '<code>_data/photographs.yml</code>.</div></div>')

    out = [note]
    for g in order:
        items = "".join(
            '<figure class="gal__item"><img src="%s" alt="%s">'
            '<figcaption>%s</figcaption></figure>'
            % (src, html.escape(cap), html.escape(cap))
            for src, cap in groups[g])
        out.append('<div class="band"><div class="shead"><h2>%s</h2></div>'
                   '<div class="gal">%s</div></div>' % (html.escape(g), items))
    return "".join(out)


# ---------------------------------------------------------------- liquid-ish
# Liquid blocks nest. A non-greedy regex for {% endfor %} matches the *inner*
# loop's closer, which silently leaves the outer loop's closing </div>s behind
# and lets a page break out of its container. So find the matching tag by
# walking forward and counting depth.
TAG_RE = re.compile(r"\{%-?\s*(\w+)[^%]*?-?%\}")


def find_block(body, start, opener, closer):
    """`start` indexes the opening tag. Returns (inner_start, inner_end, block_end)."""
    m = TAG_RE.match(body, start)
    if not m:
        return None
    depth = 0
    for t in TAG_RE.finditer(body, start):
        kw = t.group(1)
        if kw == opener:
            depth += 1
        elif kw == closer:
            depth -= 1
            if depth == 0:
                return m.end(), t.start(), t.end()
    return None


def replace_blocks(body, pattern, opener, closer, render, once=False):
    """Replace every `pattern` block, opener through its matching closer, with
    render(match). Scans right to left so earlier offsets stay valid. With
    once=True only the first block is replaced."""
    found_all = list(re.finditer(pattern, body))
    if once:
        found_all = found_all[:1]
    for m in reversed(found_all):
        found = find_block(body, m.start(), opener, closer)
        if not found:
            continue
        _, _, block_end = found
        body = body[:m.start()] + render(m) + body[block_end:]
    return body


def expand(body):
    # Gallery page — the whole grouped grid, built in one go
    if "site.data.photographs | group_by" in body:
        body = re.sub(r"\{%\s*assign\s+groups[^%]*%\}", "", body, count=1)
        body = replace_blocks(body, r"\{%\s*if\s+groups\.size[^%]*%\}",
                              "if", "endif", lambda m: gallery_html())

    # Conference photo strips: {% assign shots = ... where "talk", "<slug>" %}
    # followed by {% if shots.size > 0 %} ... {% endif %}
    while True:
        m = re.search(r'\{%\s*assign\s+shots\s*=\s*site\.data\.conferences'
                      r'[^%]*?"talk",\s*"([\w-]+)"[^%]*%\}', body)
        if not m:
            break
        slug = m.group(1)
        body = body[:m.start()] + body[m.end():]
        body = replace_blocks(body, r"\{%\s*if\s+shots\.size[^%]*%\}",
                              "if", "endif", lambda _m, sl=slug: shots_html(sl), once=True)

    # {% for x in site.data.<collection> %} ... {% endfor %}
    def do_for(m):
        coll = m.group(1)
        items = DATA.get(coll, [])
        if coll == "thoughts":
            return "".join(render_thought(i) for i in items)
        if coll == "reading":
            return "".join(render_book(i) for i in items)
        return ""

    body = replace_blocks(body, r"\{%\s*for\s+\w+\s+in\s+site\.data\.(\w+)\s*%\}",
                          "for", "endfor", do_for)

    # the home page's single latest note, if that block is ever used again
    if "site.data.thoughts | first" in body:
        latest = DATA["thoughts"][0] if DATA["thoughts"] else None
        block = render_thought(latest, ' style="border:0;padding-top:0"') if latest else ""
        body = re.sub(r"\{%\s*assign\s+latest[^%]*%\}", "", body, count=1)
        body = replace_blocks(body, r"\{%\s*if\s+latest\s*%\}",
                              "if", "endif", lambda m: block)

    body = body.replace("{{ base_path }}", "").replace("{{ site.title }}", "Simran Koul")

    # the portrait is a CSS background, so it needs inlining like the rest
    body = re.sub(r"url\('(/images/[^']+)'\)",
                  lambda m: "url('%s')" % img_uri(m.group(1)), body)
    for k, v in AUTHOR.items():
        body = body.replace("{{ site.author.%s }}" % k, v)
    body = re.sub(r"\{%\s*include[^%]*%\}", "", body)
    body = re.sub(r"\{%[^%]*%\}", "", body)
    body = re.sub(r"\{\{.*?\}\}", "", body)
    return body


def strip_front_matter(text):
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            return parts[2]
    return text


def img_uri(relpath):
    """Real photographs have to travel inline: the preview is a single file, so
    a /images/... path would not resolve wherever it is opened."""
    import base64
    full = os.path.join(REPO, relpath.lstrip("/"))
    if not os.path.exists(full):
        return relpath
    ext = os.path.splitext(full)[1].lower()
    mime = {".jpg": "jpeg", ".jpeg": "jpeg", ".png": "png", ".webp": "webp"}.get(ext, "jpeg")
    with open(full, "rb") as f:
        return "data:image/%s;base64,%s" % (mime, base64.b64encode(f.read()).decode())


def data_uri(name):
    """The preview may be viewed somewhere that blocks external requests, so
    the doodle tiles travel inline."""
    svg = open(os.path.join(REPO, "images", name)).read()
    return "data:image/svg+xml," + urllib.parse.quote(svg, safe="")


# ---------------------------------------------------------------- build
def main():
    panels, tabs = [], []
    for i, (label, fname) in enumerate(PAGES):
        path = os.path.join(REPO, "_pages", fname)
        if not os.path.exists(path):
            print("skipped (missing):", fname)
            continue
        body = expand(strip_front_matter(open(path).read()))
        slug = re.sub(r"[^a-z]+", "-", label.lower())
        active = " is-active" if i == 0 else ""
        tabs.append('<a href="#" class="tab%s" data-p="%s">%s</a>' % (active, slug, label))
        panels.append('<div class="panel%s" id="%s"><div class="page__content">%s</div></div>'
                      % (active, slug, body))

    shell = open(os.path.join(HERE, "preview_shell.html")).read()
    out = (shell
           .replace("<!--TABS-->", "".join(tabs))
           .replace("<!--PANELS-->", "\n".join(panels))
           .replace("__DOODLE_A__", data_uri("doodles-a.svg"))
           .replace("__DOODLE_B__", data_uri("doodles-b.svg")))

    dest = os.path.join(HERE, "preview.html")
    with open(dest, "w") as f:
        f.write(out)
    print("wrote", dest, len(out), "bytes")


if __name__ == "__main__":
    main()

"""Build a side-by-side review page: each scan page next to its transcription.

For every page the left column shows the scan and the right column shows the page Markdown,
rendered, with each music reference replaced by an engraving of the systems printed on that page
(a unit that crosses pages is split at its `% -- page … --` markers). Each page also lists its
uncertainty (`?`) and misprint (`sic`) marks and has the Markdown and ABC source.

Examples:
  python tools/review.py rochut                  # every transcribed page of a work
  python tools/review.py rochut b2-p004 b2-p005  # chosen pages
  python tools/review.py rochut-b2-01            # every transcribed page in a chunk

Writes .render/<work>/review-<target>.html (git-ignored) and prints its path; open it in a browser.
"""

import argparse
import copy
import html
import re
import xml.etree.ElementTree as ET

import pymupdf
import verovio

from build_music import convert_tune
from common import MUSIC_ID_RE, MUSIC_REF_RE, RENDER, WORK_NAMES, WORKS, load_pages, resolve_pages, split_tunes

SCAN_PX = 1400
PAGE_MARK_RE = re.compile(r"^%\s*--\s*page\s+(\S+)\s*--")
ATTR_ORDER = ["divisions", "key", "time", "staves", "part-symbol", "instruments", "clef", "staff-details", "transpose"]
FLAG_RE = re.compile(r"%\s*(\?|sic\b).*$|<!--\s*(\?|sic\b).*?-->")


# ---------------------------------------------------------------- music

def tune_pages(tune: str) -> tuple[int, list[tuple[str | None, int, int]]]:
    """Return (number of music lines, [(page label, first system, first source line)]).

    The first entry has label None (the page where the unit starts); each later one comes from a
    `% -- page … --` marker."""
    lines = tune.splitlines()
    body_start = next(i for i, ln in enumerate(lines) if ln.startswith("K:")) + 1
    n_systems, pages = 0, [(None, 0, 0)]
    for i, ln in enumerate(lines[body_start:], body_start):
        s = ln.strip()
        if m := PAGE_MARK_RE.match(s):
            pages.append((m.group(1), n_systems, i))
        elif s and not s.startswith("%") and not re.match(r"^[A-Za-z+]:", s):
            n_systems += 1
    return n_systems, pages


def slice_measures(xml_text: str, first: int, last: int) -> str:
    """Keep measures first..last (1-based, inclusive) of every part, carrying the clef, key and
    time in force into the first kept measure (the time signature hidden, as a printed page
    continuing a piece does not repeat it)."""
    root = ET.fromstring(xml_text)
    if first > 1:  # the title belongs to the page where the unit starts
        for tag in ("work", "movement-number", "movement-title", "credit"):
            for el in root.findall(tag):
                root.remove(el)
    for part in root.findall("part"):
        measures = part.findall("measure")
        state = {}
        for meas in measures[:first - 1]:
            for attrs in meas.findall("attributes"):
                for child in attrs:
                    state[child.tag + child.get("number", "")] = child
        for meas in measures[:first - 1] + measures[last:]:
            part.remove(meas)
        if not state:
            continue
        head = measures[first - 1]
        own = head.find("attributes")
        merged = {k: copy.deepcopy(v) for k, v in state.items()}
        if "time" in merged:
            merged["time"].set("print-object", "no")
        if own is not None:
            merged.update({c.tag + c.get("number", ""): c for c in own})
            head.remove(own)
        attrs = ET.Element("attributes")
        attrs.extend(sorted(merged.values(), key=lambda el: ATTR_ORDER.index(el.tag) if el.tag in ATTR_ORDER else 99))
        pr = head.find("print")
        head.insert(0 if pr is None else list(head).index(pr) + 1, attrs)
    return ET.tostring(root, encoding="unicode")


def system_measures(xml_text: str) -> tuple[list[int], int]:
    """(1-based index of the first measure of each system, number of measures) in the first part."""
    part = ET.fromstring(xml_text).find("part")
    firsts = [1]
    for i, meas in enumerate(part.findall("measure"), 1):
        pr = meas.find("print")
        if i > 1 and pr is not None and pr.get("new-system") == "yes":
            firsts.append(i)
    return firsts, i


def engrave(xml_text: str) -> list[str]:
    tk = verovio.toolkit()
    tk.setOptions({
        "pageWidth": 2100, "pageHeight": 2970, "adjustPageHeight": True,
        "pageMarginLeft": 150, "pageMarginRight": 60, "pageMarginTop": 40,
        "scale": 45, "breaks": "encoded", "footer": "none",
    })
    if not tk.loadData(xml_text):
        raise ValueError("verovio could not load the MusicXML")
    return [tk.renderToSVG(n) for n in range(1, tk.getPageCount() + 1)]


class Music:
    """Converts tunes on demand, keyed by music id, and engraves the part printed on one page."""

    def __init__(self):
        self.cache = {}

    def tune(self, mid: str):
        if mid in self.cache:
            return self.cache[mid]
        m = MUSIC_ID_RE.match(mid)
        work, label, x = m.group(1), m.group(2), int(m.group(3))
        abc_path = WORKS / work / "abc" / f"{label}.abc"
        result = None
        if abc_path.exists():
            _, tunes = split_tunes(abc_path.read_text(encoding="utf-8"))
            for n, text in tunes:
                if n == x:
                    xml_text, _ = convert_tune(text)
                    result = (label, text, xml_text)
        self.cache[mid] = result
        return result

    def segment(self, mid: str, page_label: str) -> tuple[list[str], str, str]:
        """(SVGs, ABC source, warning) for the part of unit `mid` printed on `page_label`."""
        found = self.tune(mid)
        if found is None:
            return [], "", f"no ABC tune found for {mid}"
        start_label, text, xml_text = found
        n_systems, pages = tune_pages(text)
        labels = [start_label if lab is None else lab for lab, _, _ in pages]
        if page_label not in labels:
            return engrave(xml_text), text, f"no `% -- page {page_label} --` marker in the ABC; showing the whole unit"
        k = labels.index(page_label)
        _, a, line_a = pages[k]
        b, line_b = (pages[k + 1][1], pages[k + 1][2]) if k + 1 < len(pages) else (n_systems, None)
        abc_part = "\n".join(text.splitlines()[line_a:line_b]).strip("\n")
        firsts, n_measures = system_measures(xml_text)
        if len(firsts) != n_systems:
            warn = (f"the ABC has {n_systems} music lines but the engraving has {len(firsts)} systems, "
                    "so the page split is unknown; showing the whole unit")
            return engrave(xml_text), abc_part, warn
        if len(pages) > 1:
            last = firsts[b] - 1 if b < n_systems else n_measures
            xml_text = slice_measures(xml_text, firsts[a], last)
        return engrave(xml_text), abc_part, ""


# ---------------------------------------------------------------- markdown

def inline(text: str) -> str:
    out = []
    for i, part in enumerate(re.split(r"(<!--.*?-->)", text)):
        if i % 2:
            body = part[4:-3].strip()
            cls = "flag" if body.startswith("?") or body.startswith("sic") else "comment"
            out.append(f'<span class="{cls}">{html.escape(body)}</span>')
            continue
        s = html.escape(part, quote=False)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", s)
        s = re.sub(r"\[\^(\w+)\]", r"<sup>[\1]</sup>", s)
        s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)
        out.append(s)
    return "".join(out)


def front_matter(md: str) -> tuple[dict[str, str], list[str]]:
    lines = md.splitlines()
    meta = {}
    if lines and lines[0] == "---":
        end = lines.index("---", 1)
        for ln in lines[1:end]:
            key, _, val = ln.partition(":")
            meta[key.strip()] = val.strip().strip('"')
        lines = lines[end + 1:]
    return meta, lines


def render_body(lines: list[str], music_html) -> str:
    out, para, i = [], [], 0

    def flush():
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
            para.clear()

    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if not s:
            flush()
        elif m := re.match(r"^(#{1,6})\s+(.*)$", s):
            flush()
            n = len(m.group(1))
            out.append(f"<h{n + 1}>{inline(m.group(2))}</h{n + 1}>")
        elif (m := MUSIC_REF_RE.match(s)) and m.end() == len(s.replace(" (continued)", "")):
            flush()
            out.append(music_html(m.group(1), s.endswith("(continued)")))
        elif m := re.match(r"^<!--\s*lang:\s*(\w+)\s*-->$", s):
            flush()
            out.append(f'<div class="lang">{html.escape(m.group(1))}</div>')
        elif re.match(r"^(\d+\.|[-*+])\s", s):
            flush()
            tag = "ol" if s[0].isdigit() else "ul"
            items = []
            while i < len(lines) and re.match(r"^(\d+\.|[-*+])\s", lines[i].strip()):
                items.append(re.sub(r"^(\d+\.|[-*+])\s+", "", lines[i].strip()))
                i += 1
                while i < len(lines) and lines[i].startswith("   ") and lines[i].strip():
                    items[-1] += " " + lines[i].strip()
                    i += 1
            out.append(f"<{tag}>" + "".join(f"<li>{inline(t)}</li>" for t in items) + f"</{tag}>")
            continue
        elif s.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            body = "".join(
                "<tr>" + "".join(f"<{'th' if r == 0 else 'td'}>{inline(c)}</{'th' if r == 0 else 'td'}>" for c in row) + "</tr>"
                for r, row in enumerate(rows))
            out.append(f"<table>{body}</table>")
            continue
        elif m := re.match(r"^\[\^(\w+)\]:\s*(.*)$", s):
            flush()
            out.append(f'<p class="footnote"><sup>[{m.group(1)}]</sup> {inline(m.group(2))}</p>')
        else:
            para.append(s)
        i += 1
    flush()
    return "\n".join(out)


# ---------------------------------------------------------------- page

def scan_png(page, out_dir) -> str:
    out = out_dir / f"{page.label}.png"
    doc = pymupdf.open(page.pdf_path)
    pg = doc[page.pdf_page - 1]
    dpi = round(SCAN_PX / max(pg.rect.width, pg.rect.height) * 72)
    pg.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY).save(out)
    return f"{out_dir.name}/{out.name}"


def flags_in(text: str) -> list[str]:
    found = []
    for ln in text.splitlines():
        for m in FLAG_RE.finditer(ln):
            mark = m.group(0).strip()
            if mark.startswith("<!--"):  # show the words the text mark refers to
                before = re.sub(r"<!--.*?-->", "", ln[:m.start()]).rstrip()
                mark = f"…{before[-40:]} {mark}"
            found.append(mark)
    return found


def page_section(page, music: Music, out_dir) -> str:
    md = page.md_path.read_text(encoding="utf-8")
    meta, body = front_matter(md)
    abc_sources, flags, warnings = [], flags_in(md), []

    def music_html(mid, continued):
        try:
            svgs, abc_part, warn = music.segment(mid, page.label)
        except Exception as err:  # show conversion errors on the page rather than stopping
            svgs, abc_part, warn = [], "", f"{type(err).__name__}: {err}"
        if warn:
            warnings.append(f"{mid}: {warn}")
        if abc_part:
            abc_sources.append((mid, abc_part))
            flags.extend(f"{mid}: {f}" for f in flags_in(abc_part))
        imgs = []
        for n, svg in enumerate(svgs, 1):
            name = f"{mid}--{page.label}-{n}.svg"
            (out_dir / name).write_text(svg, encoding="utf-8")
            imgs.append(f'<img class="music" src="{out_dir.name}/{name}" alt="{mid}">')
        tag = " (continued)" if continued else ""
        return f'<figure><figcaption>♪ {html.escape(mid)}{tag}</figcaption>{"".join(imgs)}</figure>'

    rendered = render_body(body, music_html)
    shown = {k: v for k, v in meta.items() if k not in ("work", "page", "source", "pdf_page", "printed")}
    meta_html = "".join(f"<dt>{html.escape(k)}</dt><dd>{html.escape(v)}</dd>" for k, v in shown.items())
    flag_html = "".join(f"<li>{html.escape(f)}</li>" for f in flags)
    warn_html = "".join(f'<p class="warn">⚠ {html.escape(w)}</p>' for w in warnings)
    abc_html = "".join(f"<h4>{html.escape(mid)}</h4><pre>{highlight(src)}</pre>" for mid, src in abc_sources)
    badge = f'<span class="badge">{len(flags)} flagged</span>' if flags else ""
    return f"""
<section class="page" id="{page.label}">
  <header>
    <h2>{page.label}</h2>
    <span>printed {html.escape(page.printed or "–")} · PDF page {page.pdf_page} · {page.chunk}</span>
    {badge}
  </header>
  <div class="cols">
    <div class="scan"><img src="{scan_png(page, out_dir)}" alt="scan of {page.label}" loading="lazy"></div>
    <div class="text">
      {warn_html}
      {f'<dl class="meta">{meta_html}</dl>' if meta_html else ""}
      {f'<ul class="flags">{flag_html}</ul>' if flags else ""}
      <div class="md">{rendered}</div>
      <details><summary>Markdown source</summary><pre>{highlight(md)}</pre></details>
      {f'<details><summary>ABC for this page</summary>{abc_html}</details>' if abc_html else ""}
    </div>
  </div>
</section>"""


def highlight(src: str) -> str:
    out = []
    for ln in src.splitlines():
        esc = html.escape(ln)
        out.append(f'<mark>{esc}</mark>' if FLAG_RE.search(ln) else esc)
    return "\n".join(out)


CSS = """
:root { --scan: 50%; }
* { box-sizing: border-box; }
body { margin: 0; font: 16px/1.5 Georgia, serif; background: #e9e7e2; color: #222; }
nav { position: sticky; top: 0; z-index: 2; background: #2b2b2b; color: #eee; padding: 8px 16px;
      display: flex; flex-wrap: wrap; gap: 6px 14px; align-items: center; font: 14px system-ui, sans-serif; }
nav a { color: #9fd0ff; text-decoration: none; }
nav a.flagged::after { content: " •"; color: #ffb347; }
nav label { margin-left: auto; }
.page { margin: 16px; background: #fff; border-radius: 6px; box-shadow: 0 1px 3px #0003; scroll-margin-top: 48px; }
.page > header { display: flex; gap: 12px; align-items: baseline; padding: 8px 16px; border-bottom: 1px solid #ddd;
                 font: 14px system-ui, sans-serif; color: #555; }
.page > header h2 { margin: 0; font-size: 18px; color: #222; }
.badge { background: #ffb347; color: #222; border-radius: 10px; padding: 0 8px; }
.cols { display: grid; grid-template-columns: var(--scan) 1fr; }
body.noscan .cols { grid-template-columns: 1fr; }
body.noscan .scan { display: none; }
.scan { border-right: 1px solid #ddd; padding: 8px; }
.scan img { width: 100%; display: block; position: sticky; top: 48px; }
.text { padding: 8px 24px 24px; min-width: 0; }
.md h2 { font-size: 1.8em; text-align: center; margin: .6em 0 .2em; }
.md h3 { font-size: 1.35em; margin: 1em 0 .3em; }
.md h4 { font-size: 1.1em; }
figure { margin: 12px 0; }
figcaption { font: 12px system-ui, sans-serif; color: #888; }
img.music { width: 100%; display: block; }
.lang { font: bold 12px system-ui, sans-serif; text-transform: uppercase; color: #fff; background: #557;
        display: inline-block; padding: 1px 8px; border-radius: 3px; margin-top: 16px; }
.flag { background: #ffe0a8; border: 1px solid #ffb347; border-radius: 3px; padding: 0 4px; font: 12px system-ui, sans-serif; }
.comment { color: #888; font: 12px system-ui, sans-serif; }
.flags { background: #fff6e5; border-left: 4px solid #ffb347; padding: 6px 12px 6px 28px; font: 13px system-ui, sans-serif; }
.warn { background: #fde8e8; border-left: 4px solid #d33; padding: 6px 12px; font: 13px system-ui, sans-serif; }
dl.meta { display: grid; grid-template-columns: max-content 1fr; gap: 0 12px; font: 13px system-ui, sans-serif; color: #555; }
dl.meta dt { font-weight: 600; } dl.meta dd { margin: 0; }
table { border-collapse: collapse; } td, th { border: 1px solid #ccc; padding: 2px 8px; }
details { margin-top: 12px; font: 13px system-ui, sans-serif; }
pre { white-space: pre-wrap; word-break: break-word; background: #f6f6f6; padding: 8px; font: 12px/1.45 Consolas, monospace; }
mark { background: #ffe0a8; }
.footnote { font-size: .9em; }
@media (max-width: 800px) {
  .page { margin: 8px 0; border-radius: 0; }
  .cols, body.noscan .cols { grid-template-columns: 1fr; }
  .scan { border-right: 0; border-bottom: 1px solid #ddd; }
  .scan img { position: static; }
  .text { padding: 8px 12px 20px; }
  nav label:has(#split) { display: none; }
}
"""

JS = """
const body = document.body, cb = document.getElementById('showscan'), rng = document.getElementById('split');
function apply() {
  body.classList.toggle('noscan', !cb.checked);
  document.documentElement.style.setProperty('--scan', rng.value + '%');
  try { localStorage.setItem('review', JSON.stringify({scan: cb.checked, split: rng.value})); } catch (e) {}
}
try { const s = JSON.parse(localStorage.getItem('review')); if (s) { cb.checked = s.scan; rng.value = s.split; } } catch (e) {}
cb.onchange = rng.oninput = apply; apply();
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", help="work name (arban, clarke, rochut) or chunk id (e.g. rochut-b2-01)")
    ap.add_argument("labels", nargs="*", help="page labels, e.g. b2-p004")
    args = ap.parse_args()

    verovio.enableLog(verovio.LOG_ERROR)
    all_pages = load_pages()
    if args.target in WORK_NAMES and not args.labels:
        pages = [p for p in all_pages if p.work == args.target]
    else:
        pages = resolve_pages(all_pages, args.target, args.labels)
    pages = [p for p in pages if p.md_path.exists()]
    if not pages:
        raise SystemExit("no transcribed pages to review")

    work = pages[0].work
    name = "-".join([args.target, *args.labels]) if args.labels else args.target
    out_html = RENDER / work / f"review-{name}.html"
    out_dir = RENDER / work / f"review-{name}"
    out_dir.mkdir(parents=True, exist_ok=True)

    music = Music()
    sections = [page_section(p, music, out_dir) for p in pages]
    links = []
    for p, s in zip(pages, sections):
        cls = ' class="flagged"' if '<span class="badge">' in s else ""
        links.append(f'<a href="#{p.label}"{cls}>{p.label}</a>')
    nav = " ".join(links)
    out_html.write_text(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Review {html.escape(name)}</title><style>{CSS}</style></head>
<body>
<nav><strong>{html.escape(name)}</strong> {nav}
  <label><input type="checkbox" id="showscan" checked> scans</label>
  <label>split <input type="range" id="split" min="25" max="75" value="50"></label></nav>
{''.join(sections)}
<script>{JS}</script>
</body></html>
""", encoding="utf-8", newline="\n")
    print(out_html.relative_to(RENDER.parent).as_posix())


if __name__ == "__main__":
    main()

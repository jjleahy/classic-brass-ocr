"""Check the repository for consistency. Run before every commit; CI runs it on every PR.

Checks:
  - catalog/pages.csv and catalog/sources.csv are consistent with the scans
  - every page Markdown file has front matter matching the catalog
  - every music reference in Markdown points at a tune that exists, and every tune is referenced
  - committed MusicXML matches what tools/build_music.py generates from the ABC

  python tools/validate.py
"""

import csv
import hashlib
import re
import sys

from build_music import build_page
from common import (CATALOG, LABEL_RE, MUSIC_ID_RE, MUSIC_REF_RE, ROOT, SCANS, WORK_NAMES, WORKS, load_pages,
                    split_tunes)

FRONT_KEYS = ("work", "page", "printed", "source", "pdf_page")
LANG_MARK_RE = re.compile(r"^<!-- lang: ([a-z]{2}) -->$", re.M)
ALLOWED_TOP = {"README.md", "pages", "abc", "musicxml"}

errors: list[str] = []


def err(msg):
    errors.append(msg)


def parse_front_matter(text):
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return None, text
    fm = {}
    for line in text[4:end].splitlines():
        line = line.split(" #", 1)[0].rstrip()
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"bad front matter line: {line!r}")
        key, val = (s.strip() for s in line.split(":", 1))
        if val.startswith("[") and val.endswith("]"):
            val = [v.strip().strip("\"'") for v in val[1:-1].split(",") if v.strip()]
        else:
            val = val.strip("\"'")
        fm[key] = val
    return fm, text[end + 5:]


def check_catalog(pages):
    with open(CATALOG / "sources.csv", newline="", encoding="utf-8") as fh:
        sources = {r["file"]: r for r in csv.DictReader(fh)}
    for name, row in sources.items():
        path = SCANS / name
        if not path.exists():
            err(f"catalog/sources.csv: missing scan {name}")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
            err(f"catalog/sources.csv: sha256 mismatch for {name}")
    seen = set()
    for p in pages:
        key = (p.work, p.label)
        if key in seen:
            err(f"catalog/pages.csv: duplicate {p.work}/{p.label}")
        seen.add(key)
        if p.work not in WORK_NAMES or not LABEL_RE.match(p.label):
            err(f"catalog/pages.csv: bad work/label {p.work}/{p.label}")
        src = sources.get(p.source)
        if not src:
            err(f"catalog/pages.csv: {p.work}/{p.label} names unknown source {p.source}")
        elif not 1 <= p.pdf_page <= int(src["pages"]):
            err(f"catalog/pages.csv: {p.work}/{p.label} pdf_page {p.pdf_page} out of range")
        if not p.chunk:
            err(f"catalog/pages.csv: {p.work}/{p.label} has no chunk")


def tunes_by_work(pages):
    """{work: {music id: page}} for every tune in every ABC file."""
    out = {w: {} for w in WORK_NAMES}
    for p in pages:
        if p.abc_path.exists():
            try:
                _, tunes = split_tunes(p.abc_path.read_text(encoding="utf-8"))
            except ValueError as e:
                err(f"{p.abc_path.relative_to(ROOT).as_posix()}: {e}")
                continue
            for x, _ in tunes:
                out[p.work][p.music_id(x)] = p
    return out


def check_pages(pages, tunes):
    referenced = set()
    for p in pages:
        if not p.md_path.exists():
            continue
        rel = p.md_path.relative_to(ROOT).as_posix()
        text = p.md_path.read_text(encoding="utf-8")
        if "\r" in text:
            err(f"{rel}: use LF line endings")
            text = text.replace("\r\n", "\n")
        try:
            fm, body = parse_front_matter(text)
        except ValueError as e:
            err(f"{rel}: {e}")
            continue
        if fm is None:
            err(f"{rel}: missing front matter")
            continue
        want = {"work": p.work, "page": p.label, "printed": p.printed, "source": p.source,
                "pdf_page": str(p.pdf_page)}
        for k in FRONT_KEYS:
            if fm.get(k) != want[k]:
                err(f"{rel}: front matter {k}={fm.get(k)!r}, catalog says {want[k]!r}")
        langs = fm.get("languages", [])
        if isinstance(langs, str):
            langs = [langs]
        marks = LANG_MARK_RE.findall(body)
        if fm.get("parallel") == "true":
            if len(langs) < 2 or marks != langs:
                err(f"{rel}: parallel page needs one <!-- lang: xx --> marker per language, in order "
                    f"(languages {langs}, markers {marks})")
        elif marks:
            err(f"{rel}: lang markers are only used on pages with parallel: true")
        for mid, target in MUSIC_REF_RE.findall(body):
            m = MUSIC_ID_RE.match(mid)
            if not m or m.group(1) != p.work:
                err(f"{rel}: bad music id {mid}")
                continue
            if target != f"../musicxml/{mid}.musicxml":
                err(f"{rel}: link for {mid} should be ../musicxml/{mid}.musicxml")
            if mid not in tunes[p.work]:
                err(f"{rel}: references {mid}, but no such tune in works/{p.work}/abc/")
            referenced.add(mid)
        if "[♪" in MUSIC_REF_RE.sub("", body):
            err(f"{rel}: malformed music reference (format is [♪ id](../musicxml/id.musicxml))")
    for work, ids in tunes.items():
        for mid in sorted(set(ids) - referenced):
            err(f"works/{work}/abc/{ids[mid].label}.abc: tune {mid} is not referenced from any page")


def check_tree(pages):
    known = {(p.work, p.label) for p in pages}
    for wdir in sorted(WORKS.iterdir()):
        if wdir.name == "LICENSE.md" or not wdir.is_dir():
            continue
        if wdir.name not in WORK_NAMES:
            err(f"works/{wdir.name}: unknown work")
            continue
        for child in wdir.iterdir():
            if child.name not in ALLOWED_TOP and not child.name.startswith("."):
                err(f"works/{wdir.name}/{child.name}: unexpected file or folder")
        for sub, ext in (("pages", ".md"), ("abc", ".abc")):
            for f in (wdir / sub).glob("*"):
                if f.name.startswith("."):
                    continue
                if f.suffix != ext or (wdir.name, f.stem) not in known:
                    err(f"works/{wdir.name}/{sub}/{f.name}: not a {ext} file for a catalogued page")


def main():
    pages = load_pages()
    check_catalog(pages)
    check_tree(pages)
    tunes = tunes_by_work(pages)
    check_pages(pages, tunes)
    for p in pages:
        if p.abc_path.exists() or any((WORKS / p.work / "musicxml").glob(f"{p.work}-{p.label}-*.musicxml")):
            errors.extend(build_page(p, check=True))
    done = sum(p.md_path.exists() for p in pages)
    for e in errors:
        print(f"ERROR {e}")
    print(f"{len(errors)} error(s); {done}/{len(pages)} pages transcribed")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()

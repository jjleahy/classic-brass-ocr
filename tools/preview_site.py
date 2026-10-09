"""Build the static site that the PR preview deploys (see .github/workflows/preview.yml).

For every chunk with transcribed pages changed relative to a base ref, runs tools/review.py and
collects its review page into .render/site/, with an index page and a `_headers` file that keeps
the preview out of search engines.

Examples:
  python tools/preview_site.py --base origin/develop   # chunks changed since the merge base
  python tools/preview_site.py clarke-01 arban-03      # chosen chunks

Prints the chunk ids it built, one per line; prints nothing and writes nothing if there are none.
"""

import argparse
import html
import re
import shutil
import subprocess
import sys

from common import RENDER, ROOT, load_pages

SITE = RENDER / "site"
CHANGED_RE = re.compile(r"^works/(arban|clarke|rochut)/(?:pages|abc)/([^/]+)\.(?:md|abc)$")
HEADERS = "/*\n  X-Robots-Tag: noindex, nofollow\n"


def changed_chunks(base: str) -> list[str]:
    diff = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...HEAD", "--", "works"],
        cwd=ROOT, check=True, capture_output=True, text=True, encoding="utf-8",
    ).stdout.split()
    changed = {(m.group(1), m.group(2)) for f in diff if (m := CHANGED_RE.match(f))}
    chunks = {p.chunk for p in load_pages() if (p.work, p.label) in changed}
    return sorted(chunks)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("chunks", nargs="*", help="chunk ids to build (default: those changed since --base)")
    ap.add_argument("--base", help="git ref to compare against, e.g. origin/develop")
    args = ap.parse_args()
    if bool(args.chunks) == bool(args.base):
        ap.error("give chunk ids or --base, not both or neither")

    chunks = args.chunks or changed_chunks(args.base)
    if not chunks:
        return

    shutil.rmtree(SITE, ignore_errors=True)
    SITE.mkdir(parents=True)
    pages = load_pages()
    built = []
    for chunk in chunks:
        work = next((p.work for p in pages if p.chunk == chunk), None)
        if work is None:
            raise SystemExit(f"unknown chunk: {chunk}")
        subprocess.run([sys.executable, str(ROOT / "tools" / "review.py"), chunk], cwd=ROOT, check=True, stdout=sys.stderr)
        shutil.copy(RENDER / work / f"review-{chunk}.html", SITE / f"{chunk}.html")
        shutil.copytree(RENDER / work / f"review-{chunk}", SITE / f"review-{chunk}")
        built.append(chunk)

    items = "\n".join(f'<li><a href="{html.escape(c)}.html">{html.escape(c)}</a></li>' for c in built)
    (SITE / "index.html").write_text(
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Review previews</title>'
        '<style>body{font:18px/1.6 system-ui,sans-serif;margin:24px auto;max-width:36em;padding:0 16px}</style>'
        f"</head><body><h1>Review previews</h1><ul>\n{items}\n</ul></body></html>\n",
        encoding="utf-8", newline="\n",
    )
    (SITE / "_headers").write_text(HEADERS, encoding="utf-8", newline="\n")
    print("\n".join(built))


if __name__ == "__main__":
    main()

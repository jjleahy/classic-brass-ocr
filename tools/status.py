"""Show transcription progress, computed from which page files exist (no status file to keep in sync).

  python tools/status.py               # one line per chunk
  python tools/status.py arban-07      # the pages in one chunk, with scan locations and notes
  python tools/status.py --markdown    # chunk table as Markdown (used to refresh docs/PLAN.md)
"""

import argparse
from collections import OrderedDict

from common import load_pages


def page_span(pages):
    return pages[0].label if len(pages) == 1 else f"{pages[0].label}–{pages[-1].label}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("chunk", nargs="?")
    ap.add_argument("--markdown", action="store_true")
    args = ap.parse_args()
    pages = load_pages()

    if args.chunk:
        sel = [p for p in pages if p.chunk == args.chunk]
        if not sel:
            raise SystemExit(f"unknown chunk {args.chunk}")
        for p in sel:
            mark = "x" if p.md_path.exists() else " "
            printed = f"printed {p.printed}" if p.printed else "unnumbered"
            note = f"  — {p.note}" if p.note else ""
            print(f"[{mark}] {p.work} {p.label:9} {printed:14} {p.source} page {p.pdf_page}{note}")
        return

    chunks = OrderedDict()
    for p in pages:
        chunks.setdefault(p.chunk, []).append(p)
    if args.markdown:
        print("| Chunk | Pages | Count | Notes |")
        print("|---|---|---:|---|")
    for cid, ps in chunks.items():
        done = sum(p.md_path.exists() for p in ps)
        status = "done" if done == len(ps) else ("todo" if done == 0 else f"{done}/{len(ps)}")
        notes = "; ".join(f"{p.label}: {p.note}" for p in ps if p.note and p.note != "blank")
        if args.markdown:
            print(f"| `{cid}` | {page_span(ps)} | {len(ps)} | {notes} |")
        else:
            print(f"{cid:14} {page_span(ps):22} {len(ps):3} pages  {status}")
    if not args.markdown:
        total = len(pages)
        done = sum(p.md_path.exists() for p in pages)
        print(f"\n{done}/{total} pages transcribed")


if __name__ == "__main__":
    main()

"""Render scan pages to PNG so they can be read and transcribed.

Examples:
  python tools/render_page.py arban p005                 # whole-page overview
  python tools/render_page.py arban p005 --grid 3x3      # 3 rows x 3 columns of zoomed tiles
  python tools/render_page.py arban p005 --crop 0,0.4,1,0.6   # one region (fractions x0,y0,x1,y1)
  python tools/render_page.py arban-07                   # overviews of every page in a chunk

Output goes to .render/<work>/ (git-ignored). The paths written are printed.
Tiles overlap slightly so nothing is lost at a tile edge.
"""

import argparse

import pymupdf

from common import RENDER, load_pages, resolve_pages

OVERVIEW_PX = 1600  # long edge of a whole-page overview
TILE_PX = 1800      # long edge of a zoomed tile or crop
OVERLAP = 0.03      # fraction of the page added around each tile


def render(page, clip_frac, out_path, target_px, dpi=None):
    doc = pymupdf.open(page.pdf_path)
    pg = doc[page.pdf_page - 1]
    r = pg.rect
    x0, y0, x1, y1 = clip_frac
    clip = pymupdf.Rect(r.x0 + x0 * r.width, r.y0 + y0 * r.height, r.x0 + x1 * r.width, r.y0 + y1 * r.height)
    if dpi is None:
        dpi = min(600, max(72, round(target_px / max(clip.width, clip.height) * 72)))
    pix = pg.get_pixmap(dpi=dpi, clip=clip, colorspace=pymupdf.csGRAY)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pix.save(out_path)
    print(f"{out_path.relative_to(RENDER.parent).as_posix()}  ({pix.width}x{pix.height}, {dpi} dpi)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", help="chunk id (e.g. arban-07) or work name (arban, clarke, rochut)")
    ap.add_argument("labels", nargs="*", help="page labels from catalog/pages.csv, e.g. p005 or b2-p004")
    ap.add_argument("--grid", help="RxC tiles, e.g. 4x1 for horizontal bands, 3x3 for trilingual columns")
    ap.add_argument("--crop", help="x0,y0,x1,y1 as fractions of the page")
    ap.add_argument("--dpi", type=int, help="override the automatic resolution")
    args = ap.parse_args()

    for page in resolve_pages(load_pages(), args.target, args.labels):
        base = RENDER / page.work / page.label
        if args.crop:
            frac = tuple(float(v) for v in args.crop.split(","))
            tag = "-".join(f"{v:g}" for v in frac)
            render(page, frac, base.with_name(f"{page.label}-crop-{tag}.png"), TILE_PX, args.dpi)
        elif args.grid:
            rows, cols = (int(v) for v in args.grid.lower().split("x"))
            for i in range(rows):
                for j in range(cols):
                    frac = (
                        max(0.0, j / cols - OVERLAP), max(0.0, i / rows - OVERLAP),
                        min(1.0, (j + 1) / cols + OVERLAP), min(1.0, (i + 1) / rows + OVERLAP),
                    )
                    render(page, frac, base.with_name(f"{page.label}-r{i + 1}c{j + 1}.png"), TILE_PX, args.dpi)
        else:
            render(page, (0, 0, 1, 1), base.with_name(f"{page.label}.png"), OVERVIEW_PX, args.dpi)


if __name__ == "__main__":
    main()

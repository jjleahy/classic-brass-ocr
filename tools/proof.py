"""Engrave the ABC transcription of a page so it can be compared visually with the scan.

Each tune is converted to MusicXML in memory (exactly as build_music.py does), engraved with
Verovio, and written to .render/<work>/<id>-proof[-N].png. System breaks follow the ABC line
breaks, so a proof whose lines match the printed systems can be checked line by line.

Examples:
  python tools/proof.py arban p005
  python tools/proof.py rochut-b2-01
"""

import argparse

import resvg_py
import verovio

from build_music import convert_tune
from common import RENDER, load_pages, resolve_pages, split_tunes


def engrave(xml_text: str) -> list[bytes]:
    tk = verovio.toolkit()
    tk.setOptions({
        "pageWidth": 2100, "pageHeight": 2970, "adjustPageHeight": True,
        "pageMarginLeft": 150, "pageMarginRight": 60, "pageMarginTop": 40,
        "scale": 45, "breaks": "encoded", "footer": "none",
    })
    if not tk.loadData(xml_text):
        raise ValueError("verovio could not load the MusicXML")
    pngs = []
    for n in range(1, tk.getPageCount() + 1):
        pngs.append(bytes(resvg_py.svg_to_bytes(svg_string=tk.renderToSVG(n), background="#ffffff", zoom=1.8)))
    return pngs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", help="chunk id or work name")
    ap.add_argument("labels", nargs="*")
    args = ap.parse_args()

    verovio.enableLog(verovio.LOG_ERROR)
    for page in resolve_pages(load_pages(), args.target, args.labels):
        if not page.abc_path.exists():
            continue
        _, tunes = split_tunes(page.abc_path.read_text(encoding="utf-8"))
        for x, tune in tunes:
            mid = page.music_id(x)
            try:
                xml_text, _ = convert_tune(tune)
                pngs = engrave(xml_text)
            except Exception as err:
                print(f"ERROR {mid}: {err}")
                continue
            for i, png in enumerate(pngs, 1):
                suffix = "" if len(pngs) == 1 else f"-{i}"
                out = RENDER / page.work / f"{mid}-proof{suffix}.png"
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(png)
                print(out.relative_to(RENDER.parent).as_posix())


if __name__ == "__main__":
    main()

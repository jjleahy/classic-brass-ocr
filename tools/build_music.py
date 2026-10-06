"""Convert ABC sources (works/<work>/abc/<label>.abc) into MusicXML (works/<work>/musicxml/<id>.musicxml).

Each ABC file is the music for one printed page and may hold several tunes. Tune X:n becomes the
MusicXML file <work>-<label>-<nn>.musicxml. The MusicXML files are generated and should not be edited by hand.

Examples:
  python tools/build_music.py                # build everything
  python tools/build_music.py arban p005     # build specific pages
  python tools/build_music.py arban-07       # build every page in a chunk
  python tools/build_music.py --check        # verify committed MusicXML matches the ABC (used by CI)
"""

import argparse
import re
import sys
import xml.etree.ElementTree as ET

from common import ROOT, WORKS, find_page, load_pages, resolve_pages, split_tunes

sys.path.insert(0, str(ROOT / "tools" / "vendor" / "abc2xml"))
import abc2xml  # noqa: E402  (vendored, LGPL; see tools/vendor/abc2xml/README.md)


METER_RE = re.compile(r"^M:[ \t]*([^\s%]+)|\[M:[ \t]*([^\]\s]+)\]", re.M)
TIME_SYMBOLS = {"C": "common", "C|": "cut"}


def restore_time_symbols(score, tune_text: str) -> str:
    """abc2xml turns M:C / M:C| into plain 4/4 and 2/2; put the printed symbol back.

    Each part's <time> elements are matched, in order, with the M: fields of the tune. When the
    counts differ (e.g. several voices), a C is restored on every 4/4 provided the tune never writes
    4/4 explicitly (likewise C| and 2/2). Returns a warning if neither rule applies."""
    meters = [a or b for a, b in METER_RE.findall(tune_text)]
    if not any(m in TIME_SYMBOLS for m in meters):
        return ""
    by_value = {"4/4": "C" in meters and "4/4" not in meters, "2/2": "C|" in meters and "2/2" not in meters}
    for part in score.iter("part"):
        times = list(part.iter("time"))
        if len(times) == len(meters):
            for el, meter in zip(times, meters):
                if meter in TIME_SYMBOLS:
                    el.set("symbol", TIME_SYMBOLS[meter])
            continue
        for el in times:
            value = f"{el.findtext('beats')}/{el.findtext('beat-type')}"
            if value in ("4/4", "2/2") and by_value[value]:
                el.set("symbol", "common" if value == "4/4" else "cut")
            elif value in ("4/4", "2/2") and ("C" if value == "4/4" else "C|") in meters:
                return "could not restore C / C| time symbols: tune mixes C with 4/4 (or C| with 2/2)"
    return ""


def convert_tune(tune_text: str) -> tuple[str, str]:
    """Return (musicxml text, abc2xml diagnostics) for one tune."""
    abc2xml.getInfo()  # clear old messages
    docs = abc2xml.getXmlDocs(tune_text, 0, 1, False, True, False, False)  # bOpt: line break at EOL
    messages = abc2xml.getInfo()
    if len(docs) != 1:
        raise ValueError(f"abc2xml produced {len(docs)} scores\n{messages}")
    score = docs[0]
    for enc in score.iter("encoding"):  # drop the date so builds are reproducible
        for el in list(enc):
            if el.tag == "encoding-date":
                enc.remove(el)
    warning = restore_time_symbols(score, tune_text)
    if warning:
        messages += f"-- {warning}\n"
    return abc2xml.fixDoctype(score) + "\n", messages


def build_page(page, check: bool) -> list[str]:
    """Build (or check) the MusicXML for one page. Returns a list of problems."""
    problems = []
    out_dir = WORKS / page.work / "musicxml"
    expected = {}
    if page.abc_path.exists():
        _, tunes = split_tunes(page.abc_path.read_text(encoding="utf-8"))
        numbers = [x for x, _ in tunes]
        if numbers != list(range(1, len(numbers) + 1)):
            problems.append(f"{page.abc_path.name}: X: numbers must run 1, 2, 3, ... (found {numbers})")
        for x, tune in tunes:
            mid = page.music_id(x)
            try:
                xml_text, messages = convert_tune(tune)
            except Exception as err:  # abc2xml raises on malformed input
                problems.append(f"{mid}: abc2xml failed: {err}")
                continue
            for line in messages.splitlines():
                if line.startswith("-- ") and "skipped header" not in line and "decoded from" not in line:
                    print(f"  {mid}: {line[3:]}")
            expected[out_dir / f"{mid}.musicxml"] = xml_text
            ET.fromstring(xml_text.split("\n", 2)[2])  # well-formedness check (skip XML decl + doctype)

    existing = set(out_dir.glob(f"{page.work}-{page.label}-[0-9][0-9].musicxml"))
    for path, text in expected.items():
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current != text:
            if check:
                problems.append(f"{path.relative_to(ROOT).as_posix()} is missing or stale; run tools/build_music.py")
            else:
                out_dir.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8", newline="\n")
                print(f"wrote {path.relative_to(ROOT).as_posix()}")
    for path in existing - set(expected):
        if check:
            problems.append(f"{path.relative_to(ROOT).as_posix()} has no matching ABC tune")
        else:
            path.unlink()
            print(f"removed {path.relative_to(ROOT).as_posix()}")
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", nargs="?", help="chunk id or work name (default: everything)")
    ap.add_argument("labels", nargs="*")
    ap.add_argument("--check", action="store_true", help="do not write; fail if MusicXML is stale")
    args = ap.parse_args()

    pages = load_pages()
    if args.target:
        selected = resolve_pages(pages, args.target, args.labels)
    else:
        selected = list(pages)
        # also catch ABC files whose label is not in the catalog
        for abc in sorted(WORKS.glob("*/abc/*.abc")):
            find_page(pages, abc.parent.parent.name, abc.stem)

    problems = []
    for page in selected:
        problems += build_page(page, args.check)
    for p in problems:
        print(f"ERROR {p}")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()

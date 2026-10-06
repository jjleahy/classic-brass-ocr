# abc2xml (vendored)

`abc2xml.py` converts ABC notation to MusicXML. It is used by `tools/build_music.py`.

| | |
|---|---|
| Author | Willem G. Vree, with contributors listed in the file header |
| Source | <https://wim.vree.org/svgParse/abc2xml.html> |
| Version | 268 (`abc2xml.py-268.zip`, SHA-256 `7beb1483e1a5c1f744a1faff71dda8f6cd68e1e9c75ab5b44eeeadc30754461f`) |
| Licence | GNU Lesser General Public License. The file header names no version, so LGPL 2.1 is included in [COPYING.LESSER](COPYING.LESSER). |

`abc2xml.py` is included unmodified. This repository's own changes to the output are made
in `tools/build_music.py`:

- the encoding date is removed, so builds are reproducible
- the C and C| time-signature symbols are restored

To update: download a newer `abc2xml.py-NNN.zip` from the source page, replace `abc2xml.py`,
update this file, then run `python tools/build_music.py` and review the diff.

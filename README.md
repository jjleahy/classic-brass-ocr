# classic-brass-ocr

Open, machine-readable transcriptions of three classic public-domain brass methods, made from
the scans on [IMSLP](https://imslp.org/):

| Work | Edition scanned | Pages |
|---|---|---:|
| **Arban**: *Complete Celebrated Method for the Cornet* (*Grande méthode complète de cornet à pistons*) | Carl Fischer, New York; ed. Edwin Franko Goldman; English, German and French text | 355 |
| **Clarke**: *Technical Studies for the Cornet* (Second Series) | L. B. Clarke, Elkhart, Ind., 1912 | 58 |
| **Rochut**: *120 Melodious Etudes for Trombone* (from the Vocalises of Marco Bordogni), Books 1–3 | Carl Fischer, New York, 1928 | 229 |

The transcriptions are **as printed**. They keep the original wording, all three languages
of the Arban, and the original spelling, notation and misprints. Prose reflows freely, and
music need not keep the printed staff layout.

**Status:** in progress. See [docs/PLAN.md](docs/PLAN.md) or run
`python tools/status.py`.

## Formats

- **Text** is in Markdown, one file per printed page: `works/<work>/pages/<label>.md`.
- **Music** is in MusicXML, one file per exercise, etude, song or example:
  `works/<work>/musicxml/<id>.musicxml`. Each Markdown page links its music at the point
  where it appears, for example `[♪ arban-p005-01](../musicxml/arban-p005-01.musicxml)`.
- The MusicXML is generated from hand-written ABC in `works/<work>/abc/`. ABC is compact and
  easy to review in a diff; `tools/build_music.py` converts it.
- [catalog/pages.csv](catalog/pages.csv) maps every page label to its printed page number
  and to the exact page of the source PDF.

The conventions are documented in
[docs/TRANSCRIPTION_GUIDE.md](docs/TRANSCRIPTION_GUIDE.md).

## Provenance

All source scans are in [`original-pdf-scans/`](original-pdf-scans/), unmodified as
downloaded from IMSLP. Each file's SHA-256 checksum is recorded in
[catalog/sources.csv](catalog/sources.csv). Edition and scan details below are as listed on
IMSLP and as printed in the scans.

### Arban: *Grande méthode complète de cornet à pistons*

- IMSLP work page:
  [Grande méthode complète de cornet à pistons (Arban, Jean-Baptiste)](https://imslp.org/wiki/Grande_m%C3%A9thode_compl%C3%A8te_de_cornet_%C3%A0_pistons_(Arban%2C_Jean-Baptiste))
- **Edition.** *Arban's Complete Celebrated Method for the Cornet*, "New Revised and
  Authentic Edition", newly revised and edited by Edwin Franko Goldman. Published by Carl
  Fischer, New York.
- **Printed notices.** Plate 3654-290. Pages carry "Copyright 1893 by Carl Fischer, New
  York"; the fantasias carry "Copyright MCMXII by Carl Fischer, New York".
- **Scan.** Sibley Music Library, Eastman School of Music (Sibley Mirroring Project). IMSLP
  lists the scan as Public Domain.

| File | Printed pages |
|---|---|
| [#180028](https://imslp.org/wiki/Special:ImagefromIndex/180028) `IMSLP180028-SIBLEY1802.7272.57c3-39087017795040pp1-56.pdf` | front matter (I–VI), 1–56 |
| [#180029](https://imslp.org/wiki/Special:ImagefromIndex/180029) `IMSLP180029-SIBLEY1802.7272.f7ba-39087017795040pp57-122.pdf` | 57–122 |
| [#180030](https://imslp.org/wiki/Special:ImagefromIndex/180030) `IMSLP180030-SIBLEY1802.7272.6b1d-39087017795040pp123-190.pdf` | 123–190 |
| [#180031](https://imslp.org/wiki/Special:ImagefromIndex/180031) `IMSLP180031-SIBLEY1802.7272.e604-39087017795040pp191-282.pdf` | 191–282 |
| [#180032](https://imslp.org/wiki/Special:ImagefromIndex/180032) `IMSLP180032-SIBLEY1802.7272.c9b6-39087017795040pp283-347.pdf` | 283–347 |

### Clarke: *Technical Studies for the Cornet*

- IMSLP work page:
  [Clarke's Technical Studies for the Cornet (Clarke, Herbert Lincoln)](https://imslp.org/wiki/Clarke's_Technical_Studies_for_the_Cornet_(Clarke%2C_Herbert_Lincoln))
- **Edition.** *Clarke's Technical Studies for the Cornet*, Second Series. Published by
  L. B. Clarke, Elkhart, Ind., 1912.
- **Scan.** Sibley Music Library, Eastman School of Music (Sibley Mirroring Project). IMSLP
  lists the scan as Public Domain.
- **File.** [#340778](https://imslp.org/wiki/Special:ImagefromIndex/340778)
  `IMSLP340778-SIBLEY1802.28663.653c-MT445.C598_T25_1912.pdf` (complete).

### Rochut: *120 Melodious Etudes for Trombone*

- IMSLP work page:
  [120 Melodious Etudes (Rochut, Joannes)](https://imslp.org/wiki/120_Melodious_Etudes_(Rochut,_Joannes))
- **Edition.** *120 Melodious Etudes for Trombone*, from the Vocalises of Marco Bordogni,
  selected and transcribed by Joannès Rochut. Published by Carl Fischer, New York, 1928.
- **Scan.** IMSLP lists the scan as Public Domain.

| File | Contents |
|---|---|
| [#971510](https://imslp.org/wiki/Special:ImagefromIndex/971510) `IMSLP971510-PMLP1519677-Rochut_-_120_Melodious_Etudes_-_Book_1.pdf` | Book One (Nos. 1–60) |
| [#971511](https://imslp.org/wiki/Special:ImagefromIndex/971511) `IMSLP971511-PMLP1519677-Rochut_-_120_Melodious_Etudes_-_Book_2.pdf` | Book Two (Nos. 61–90) |
| [#971512](https://imslp.org/wiki/Special:ImagefromIndex/971512) `IMSLP971512-PMLP1519677-Rochut_-_120_Melodious_Etudes_-_Book_3.pdf` | Book Three (Nos. 91–120) |

## Licensing

| What | Licence |
|---|---|
| **Transcriptions**: everything under [`works/`](works/) (Markdown, ABC, MusicXML) | Dedicated to the public domain under [CC0 1.0 Universal](LICENSE-CC0) |
| **Code**: [`tools/`](tools/), CI and repository configuration | [MIT License](LICENSE) |
| **Source scans** in [`original-pdf-scans/`](original-pdf-scans/) | Public domain, as listed on IMSLP; included unmodified for provenance |
| **Vendored [abc2xml](https://wim.vree.org/svgParse/abc2xml.html)** in [`tools/vendor/abc2xml/`](tools/vendor/abc2xml/) | © Willem G. Vree; GNU LGPL; see [its README](tools/vendor/abc2xml/README.md) |

The transcriptions were produced with AI assistance (Claude) and checked against the scans,
but they may still contain errors. Corrections are welcome as issues or pull requests;
please cite the page label and the scan.

## Tools

Requires Python 3.10+ and `pip install -r requirements.txt`.

```sh
python tools/status.py                         # progress by chunk
python tools/render_page.py arban p005 --grid 3x3   # render a scan page into zoomed tiles (.render/)
python tools/build_music.py                    # regenerate MusicXML from ABC
python tools/proof.py arban p005               # engrave the transcribed music for comparison with the scan
python tools/validate.py                       # consistency checks (run in CI)
```

For how the work is organised into Claude Code cloud sessions, one pull request per chunk,
see [docs/PLAN.md](docs/PLAN.md).

# classic-brass-ocr

This repository transcribes three public-domain brass methods from scanned PDFs into
Markdown (text) and ABC → MusicXML (music):

- Arban, *Complete Celebrated Method for the Cornet*
- Clarke, *Technical Studies for the Cornet*
- Rochut, *120 Melodious Etudes*

The work is split into chunks of pages, and each chunk is one pull request.

## Must read before transcribing

- [docs/TRANSCRIPTION_GUIDE.md](docs/TRANSCRIPTION_GUIDE.md): the conventions. Transcribe
  as printed; never translate, modernise or correct.
- [docs/PLAN.md](docs/PLAN.md): the chunks and their order.
- The `transcribe-chunk` skill (`/transcribe-chunk <chunk>`): the workflow for one chunk.

## Layout

| Path | Contents |
|---|---|
| `original-pdf-scans/` | The source PDFs from IMSLP. Read-only. |
| `catalog/pages.csv` | Every scanned page: its label, printed number, source PDF, PDF page and chunk. |
| `catalog/sources.csv` | The PDFs, their IMSLP indexes and SHA-256 checksums. |
| `works/<work>/pages/<label>.md` | Page text, with `[♪ id](../musicxml/id.musicxml)` music references. |
| `works/<work>/abc/<label>.abc` | Music that starts on that page, one tune per unit. Hand-written. |
| `works/<work>/musicxml/<id>.musicxml` | Generated from the ABC. Never edit by hand. |
| `tools/` | Python tools. `tools/vendor/abc2xml/` is third-party (LGPL); don't modify it. |

## Commands

```sh
pip install -r requirements.txt                       # installed automatically in cloud sessions
python tools/status.py [chunk]                        # progress / pages in a chunk
python tools/render_page.py <work> <label> [--grid RxC | --crop x0,y0,x1,y1]   # scan → .render/
python tools/build_music.py [<work> <label>...]       # ABC → MusicXML
python tools/proof.py <work> <label>                  # engrave the ABC → .render/ for visual comparison
python tools/review.py <work|chunk> [<label>...]      # side-by-side review page: scan | transcription
python tools/validate.py                              # must pass before committing (CI runs it)
```

## Reviewing

The user reviews transcriptions in the page that `tools/review.py` writes to
`.render/<work>/review-<target>.html`. Each row shows a scan page beside its rendered Markdown,
the engraved music for that page's systems, its `?`/`sic` flags, and its Markdown and ABC source.

- When the user asks to review transcribed pages, build the page and open it in their
  browser (on Windows: `Start-Process msedge <file:///…html>`).
- **After making changes from review feedback, rerun the same `tools/review.py` command**
  (and `tools/build_music.py` for ABC changes) so the open page can simply be reloaded.
- The page shows only what is on the current branch, so check out the branch under review first.
- Pull requests also get a public preview (for reviewing on a phone): `.github/workflows/preview.yml`
  builds the review page for each chunk the PR changes (`tools/preview_site.py`), deploys it as a
  Cloudflare Workers Preview named `pr-<number>` (`wrangler.jsonc`) and comments the link on the PR.
  Pushing to the PR rebuilds it; closing the PR deletes it.

## Rules

- **Licences.** Transcriptions under `works/` are CC0 1.0 (`LICENSE-CC0`); code is MIT
  (`LICENSE`).
- **Scope.** A transcription PR changes only its own chunk's files under `works/`, plus
  catalog rows for its own pages if they need correcting.
- **Line endings.** Use LF and UTF-8 everywhere.

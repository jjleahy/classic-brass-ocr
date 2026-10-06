---
name: transcribe-chunk
description: Transcribe one chunk of scanned pages (text to Markdown, music to ABC/MusicXML) following the repository's transcription guide, verify it, and open a pull request. Use when asked to transcribe a chunk such as arban-07, clarke-02 or rochut-b2-03, or specific pages of a work.
---

# Transcribe a chunk

Chunk to transcribe: **$ARGUMENTS**. If it is empty, ask which chunk; `docs/PLAN.md` lists
them.

## 0. Prepare

1. Read `docs/TRANSCRIPTION_GUIDE.md` in full. Every convention there applies.
2. Run `python tools/status.py <chunk>` to list the pages, their scan files and notes.
   - If any page is already marked `[x]`, stop and report rather than overwriting it.
   - If imports fail, run `pip install -r requirements.txt`.
3. Run `python tools/render_page.py <work> <label>` on the page **before** your first page
   and on the page **after** your last. You need them to tell whether the chunk opens
   mid-unit and to finish a unit that runs past your last page (guide §6). Do not
   transcribe those neighbouring pages.

## 1. Each page, in order

Work through one page at a time. Images are expensive: render and read only what you need.

1. **Overview.** Run `python tools/render_page.py <work> <label>` and read the PNG. Decide
   what kind of page it is: parallel prose (Arban), music with headings, mixed, title or
   blank.
2. **Zoom.** Read the page in tiles that make every note and accent legible:
   - three-column prose: `--grid 3x3`
   - music: `--grid 5x1` or `--grid 6x1`, so each tile holds about 2 systems
   - anything still unclear: `--crop x0,y0,x1,y1`
3. **Write** `works/<work>/pages/<label>.md`, and `works/<work>/abc/<label>.abc` if music
   starts on the page. Copy the front matter values from `catalog/pages.csv`. Write one ABC
   line per printed system.
4. **Build.** Run `python tools/build_music.py <work> <label>` and fix any errors or
   warnings.
5. **Proof.** Run `python tools/proof.py <work> <label>` and compare each proof PNG with the
   scan tiles **system by system**:
   - the clef, key and time signature, and the octave after every clef change
   - the number of bars per system
   - pitches and accidentals
   - rhythms (each bar must add up)
   - ties and slurs
   - dynamics, hairpins, articulations and text

   Fix the ABC, rebuild and re-proof until the proof matches.
6. **Proofread the text** against the tiles one more time. Check accents, umlauts, archaic
   spellings, punctuation, numbers and the order of the language sections.

## 2. Finish

1. `python tools/validate.py` must print `0 error(s)`.
2. **Stay in scope.** Change only the files for your chunk's pages under `works/`. If a
   catalog row for one of your pages is wrong, for example its printed page number, you may
   correct that row in `catalog/pages.csv`; say so in the PR. Do not change the guide or
   the tools; suggest improvements in the PR description instead.
3. **Commit** with the message `Transcribe <chunk>: <work> <first label>–<last label>`.
   Push, and open a pull request against `develop` with the same title. In the PR
   description, list:
   - the pages and music units transcribed (count)
   - every uncertain reading and suspected misprint (`<!-- ? -->`, `% ?`, `% sic`)
   - any unit that continues into the next chunk, or that this chunk picked up from the
     previous one
   - judgement calls not covered by the guide, so the guide can be updated for later chunks

# Transcription plan

The three works total **642 scanned pages**:

| Work | Pages | Files |
|---|---:|---|
| Arban | 355 | 5 PDFs |
| Clarke | 58 | 1 PDF |
| Rochut | 229 | 3 books |

They are split into **70 chunks**. Each chunk is transcribed in its own Claude Code session
and becomes one pull request. Chunks are independent: each PR changes only the files for its
own pages. So chunks can run in parallel, and there is no shared status file to cause merge
conflicts. Progress is computed from the files that exist:

```sh
python tools/status.py
```

**Chunk sizes.**

| Kind of page | Pages per chunk |
|---|---:|
| Dense trilingual prose (Arban front matter and explanations) | 4–5 |
| Dense music | 8–10 |
| Simpler music (First Studies, songs) | about 12 |

To re-chunk, edit the `chunk` column in [`catalog/pages.csv`](../catalog/pages.csv). Do this
only for chunks that have not been started.

## Phase 0: setup (done)

- Scans committed, with SHA-256 checksums (`catalog/sources.csv`).
- Page catalog with printed page numbers and chunk assignments (`catalog/pages.csv`).
- Conventions in [`TRANSCRIPTION_GUIDE.md`](TRANSCRIPTION_GUIDE.md).
- Tools to render scans, build MusicXML, engrave proofs, validate and report status.
- A CI check on every PR (`.github/workflows/validate.yml`).

## Phase 1: pilot (run one at a time and review closely)

Run these three chunks first. Together they cover the hardest kinds of material:

1. **`arban-03`**: trilingual three-column prose with music examples and tables.
2. **`rochut-b2-01`**: a prose foreword, then etudes with bass/tenor clef changes.
3. **`clarke-02`**: dense numbered technical exercises.

After each pilot PR, review it carefully against the scans. Fold anything the guide got
wrong or left unclear into `docs/TRANSCRIPTION_GUIDE.md` **before** starting the next
chunk. Changing a convention later means reworking every chunk already merged.

## Phase 2: fan-out

Once the pilots are merged and the guide is stable, start the remaining chunks. Run as many
sessions in parallel as you like. A good order is:

1. the rest of Rochut, which is the most uniform
2. Clarke
3. the Arban music chunks
4. the prose-heavy Arban chunks last, after the pilot lessons

**Starting a cloud session** at [claude.ai/code](https://claude.ai/code):

1. Choose this repository and the `develop` branch.
2. Keep the network access default. The session-start hook installs the Python
   dependencies from PyPI.
3. Prompt with the chunk ID:

   ```text
   /transcribe-chunk arban-07
   ```

   or: *Transcribe chunk arban-07 following the transcribe-chunk skill.*

The skill handles rendering, transcribing, proofing, validating, committing and opening the
PR against `develop`.

**Reviewing a chunk PR:**

- CI (`validate`) is green.
- Pick two or three pages. Open the scan page next to the Markdown, and run
  `python tools/proof.py <work> <label>` to compare the engraved music with the scan.
- Read the PR's list of uncertain readings and misprints; resolve what you can.
- Check where the chunk meets its neighbours: a unit that continues across pages belongs to
  the page where it starts (guide §6).

## Phase 3: finishing (after all chunks merge)

- A second, independent proofreading pass: one session per chunk, comparing proofs and
  text against the scans and fixing errors.
- A table of contents for each work in `works/<work>/README.md`, mapping exercise, etude and
  song numbers to music IDs.
- An assembler tool, to produce one continuous Markdown file per work (and per language for
  the Arban) from the page files.
- A tagged release.

## Chunks

| Chunk | Pages | Count | Content | Pilot |
|---|---|---:|---|---|
| `arban-01` | f01–r02 | 4 | Cover; glossary of musical terms (table); Report of the Conservatoire committee and biographical sketch (trilingual prose) **(prose-heavy)** |  |
| `arban-02` | r03–r06 | 4 | Preface (trilingual prose); instrument illustrations and fingering chart; diagram of the cornet **(prose-heavy)** |  |
| `arban-03` | p001–p005 | 5 | Introduction: trilingual prose with music examples and tables **(prose-heavy)** | 1 |
| `arban-04` | p006–p010 | 5 | Introduction continued: trilingual prose with music examples **(prose-heavy)** |  |
| `arban-05` | p011–p022 | 12 | First Studies (p. 11) |  |
| `arban-06` | p023–p032 | 10 | Studies on Syncopation (p. 23) |  |
| `arban-07` | p033–p042 | 10 | Exercises; trilingual explanation on p. 37–38 |  |
| `arban-08` | p043–p052 | 10 | Exercises |  |
| `arban-09` | p053–p060 | 8 | Scale Studies title (p. 57) and trilingual introduction (p. 58); Major Scales from p. 59 |  |
| `arban-10` | p061–p070 | 10 | Exercises |  |
| `arban-11` | p071–p080 | 10 | Exercises |  |
| `arban-12` | p081–p086 | 6 | Exercises |  |
| `arban-13` | p087–p094 | 8 | Trilingual explanations (p. 87–90); ornament studies begin **(prose-heavy)** |  |
| `arban-14` | p095–p104 | 10 | Exercises |  |
| `arban-15` | p105–p114 | 10 | Exercises |  |
| `arban-16` | p115–p122 | 8 | Exercises |  |
| `arban-17` | p123–p130 | 8 | Trilingual prose (p. 123–124), then exercises |  |
| `arban-18` | p131–p140 | 10 | Exercises |  |
| `arban-19` | p141–p150 | 10 | Exercises |  |
| `arban-20` | p151–p160 | 10 | Trilingual prose on tonguing (p. 153–154), then exercises |  |
| `arban-21` | p161–p170 | 10 | Exercises |  |
| `arban-22` | p171–p180 | 10 | Exercises |  |
| `arban-23` | p181–p190 | 10 | Exercises |  |
| `arban-24` | p191–p202 | 12 | The Art of Phrasing: 150 songs and operatic airs (p. 191) |  |
| `arban-25` | p203–p214 | 12 | The Art of Phrasing (songs) |  |
| `arban-26` | p215–p226 | 12 | The Art of Phrasing (songs) |  |
| `arban-27` | p227–p238 | 12 | The Art of Phrasing (songs) |  |
| `arban-28` | p239–p245 | 7 | The Art of Phrasing (songs) |  |
| `arban-29` | p246–p255 | 10 | Sixty-eight Duets for two cornets (p. 246), two staves |  |
| `arban-30` | p256–p264 | 9 | Duets (two staves) |  |
| `arban-31` | p265–p273 | 9 | Duets (two staves) |  |
| `arban-32` | p274–p282 | 9 | Duets (two staves) |  |
| `arban-33` | p283–p292 | 10 | Last Part title (p. 283); trilingual preface (p. 284); Fourteen Characteristic Studies **(prose-heavy)** |  |
| `arban-34` | p293–p300 | 8 | Characteristic Studies; Twelve Celebrated Fantaisies title and contents (p. 300) |  |
| `arban-35` | p301–p308 | 8 | Fantaisies and Airs Variés (Cornet in B♭) |  |
| `arban-36` | p309–p316 | 8 | Fantaisies and Airs Variés |  |
| `arban-37` | p317–p324 | 8 | Fantaisies and Airs Variés |  |
| `arban-38` | p325–p332 | 8 | Fantaisies and Airs Variés |  |
| `arban-39` | p333–p340 | 8 | Fantaisies and Airs Variés |  |
| `arban-40` | p341–p347 | 7 | Fantaisies and Airs Variés |  |
| `clarke-01` | f01–p008 | 11 | Cover, blanks, title page, Introduction (prose); First Study |  |
| `clarke-02` | p009–p017 | 9 | Studies and etudes | 3 |
| `clarke-03` | p018–p026 | 9 | Studies and etudes |  |
| `clarke-04` | p027–p035 | 9 | Studies and etudes |  |
| `clarke-05` | p036–p044 | 9 | Studies and etudes |  |
| `clarke-06` | p045–z02 | 11 | Studies; An Irish Ballad; An Old German Folksong; publisher's advertisements (z01–z02) |  |
| `rochut-b1-01` | b1-p002–b1-p011 | 10 | Book One title block; Nos. 1 ff. |  |
| `rochut-b1-02` | b1-p012–b1-p021 | 10 | Etudes |  |
| `rochut-b1-03` | b1-p022–b1-p031 | 10 | Etudes |  |
| `rochut-b1-04` | b1-p032–b1-p041 | 10 | Etudes |  |
| `rochut-b1-05` | b1-p042–b1-p051 | 10 | Etudes |  |
| `rochut-b1-06` | b1-p052–b1-p061 | 10 | Etudes |  |
| `rochut-b1-07` | b1-p062–b1-p071 | 10 | Etudes |  |
| `rochut-b1-08` | b1-p072–b1-p081 | 10 | Etudes |  |
| `rochut-b1-09` | b1-p082–b1-p087 | 6 | Etudes |  |
| `rochut-b2-01` | b2-p001–b2-p010 | 10 | Foreword (prose); Book Two title block; Nos. 61 ff. | 2 |
| `rochut-b2-02` | b2-p011–b2-p020 | 10 | Etudes |  |
| `rochut-b2-03` | b2-p021–b2-p030 | 10 | Etudes |  |
| `rochut-b2-04` | b2-p031–b2-p040 | 10 | Etudes |  |
| `rochut-b2-05` | b2-p041–b2-p050 | 10 | Etudes |  |
| `rochut-b2-06` | b2-p051–b2-p060 | 10 | Etudes |  |
| `rochut-b2-07` | b2-p061–b2-p065 | 5 | Etudes |  |
| `rochut-b3-01` | b3-p002–b3-p011 | 10 | Book Three title block; Nos. 91 ff. |  |
| `rochut-b3-02` | b3-p012–b3-p021 | 10 | Etudes |  |
| `rochut-b3-03` | b3-p022–b3-p031 | 10 | Etudes |  |
| `rochut-b3-04` | b3-p032–b3-p041 | 10 | Etudes |  |
| `rochut-b3-05` | b3-p042–b3-p051 | 10 | Etudes |  |
| `rochut-b3-06` | b3-p052–b3-p061 | 10 | Etudes |  |
| `rochut-b3-07` | b3-p062–b3-p071 | 10 | Etudes |  |
| `rochut-b3-08` | b3-p072–b3-p079 | 8 | Etudes |  |

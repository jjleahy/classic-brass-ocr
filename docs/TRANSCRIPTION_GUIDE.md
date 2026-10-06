# Transcription guide

These conventions apply to every transcription in this repository. Their goal is that
transcriptions made in many separate sessions fit together into one consistent edition.

## 1. Principles

**Transcribe as printed.**

- Keep the original language, spelling, capitalisation, punctuation and accents. That
  includes archaic or inconsistent forms such as German *Ueber*, *athmen* and *Theil*, or
  French *Fantaisie*.
- Do not translate, modernise, normalise or correct.
- Keep printer's errors. Record anything you believe is a misprint in a comment (see §5);
  never fix it silently.
- Transcribe musical pitch and rhythm exactly as printed. Do not transpose; cornet music
  stays in its written (B♭) pitch.

**Layout may change.** Prose reflows into paragraphs. Music does not have to keep the
printed staff layout, but by convention each printed system becomes one line of ABC
(see §4), because that makes proofreading much easier.

**Leave out** things that are not part of the printed edition:

- library stamps and shelf marks
- handwritten marks, such as pencil ticks or circled numbers
- show-through from the other side of the page and scanner artifacts

**Mark uncertainty rather than guessing silently** (see §5).

## 2. Files and identifiers

Every scanned page has a row in [`catalog/pages.csv`](../catalog/pages.csv). That row gives
the page's **label**, its printed page number, the scan file and page index it comes from,
and the chunk it belongs to.

| Label | Meaning |
|---|---|
| `p005` | printed page 5 (the Arban's numbering runs continuously across its 5 PDFs) |
| `b2-p004` | Rochut Book 2, page 4 (numbering restarts in each book) |
| `r03` | front matter page with a roman number (Arban I–VI) |
| `f01` | unnumbered front matter: covers, title pages, blank pages |
| `z01` | unnumbered back matter |

The `printed` column holds the page number as printed. A value in `[brackets]` was
inferred from the sequence and is not printed on the page.

For each page that has been transcribed:

```text
works/<work>/pages/<label>.md            text of the page, with references to its music
works/<work>/abc/<label>.abc             music that starts on the page (ABC, hand-written)
works/<work>/musicxml/<id>.musicxml      generated from the ABC by tools/build_music.py
```

A **music unit** is one numbered exercise, etude, song, example or piece. Each unit is one
ABC tune, and units on a page are numbered `X:1`, `X:2`, … in reading order. A unit's ID is
`<work>-<label>-<NN>`, for example `arban-p005-01` or `rochut-b2-p004-01`.

Never edit MusicXML files by hand. Edit the ABC and run `python tools/build_music.py`.

## 3. Page Markdown

### Front matter

Every page file starts with front matter. Copy `work`, `page`, `printed`, `source` and
`pdf_page` exactly from the page's row in `catalog/pages.csv`; `tools/validate.py` checks
them.

```yaml
---
work: arban
page: p005
printed: "5"
source: IMSLP180028-SIBLEY1802.7272.57c3-39087017795040pp1-56.pdf
pdf_page: 13
languages: [en, de, fr]
parallel: true
running_head: "Cornet in B♭"
plate: "3654-290"
notice: "Copyright 1893 by Carl Fischer, New York."
note: "Pencil marks in the margin omitted."
---
```

| Field | Use |
|---|---|
| `languages` | Languages of the printed text, in printed left-to-right order (`en`, `de`, `fr`). Omit it on pages with no text. |
| `parallel: true` | Use it only when the page sets the same prose side by side in columns (see below). |
| `running_head` | Optional. A running head, as printed. |
| `plate` | Optional. The plate number at the foot of the page, as printed. |
| `notice` | Optional. A copyright line or similar footer, as printed. |
| `note` | Optional. A remark from the transcriber. |

The page number itself is not transcribed in the body; it is already in `printed`.

### Body

- **Headings.** Use `#` for the title of a whole part or book, such as "THE ART OF
  PHRASING" or "120 Melodious Etudes". Use `##` for section headings, such as "Method of
  Breathing.", "FIRST STUDY" or "No. 62". Use `###` for minor headings, such as a song
  title. Keep the printed wording, capitalisation and final full stop.
- **Paragraphs.** Put a blank line between paragraphs. Join words that are hyphenated across
  a line break (`instru-` + `ment` → `instrument`). Keep a hyphen that belongs to the word.
- **Emphasis.** Write italics as `*text*` and bold as `**text**`. Letter-spaced emphasis
  (German *Sperrsatz*) counts as italics. Small capitals are written in ordinary
  capitalisation.
- **Symbols.** Use Unicode: ♭ ♯ ♮ 𝅝 𝅗𝅥 ♩ ♪ ´ ` ^ ä ö ü ß é è ê ç œ «» „“ — –.
- **Footnotes.** Use `[^1]` at the mark. Put the note text at the end of the same language
  section.
- **Tables** (for example the Arban glossary or a fingering table) become Markdown tables.
- **Figures and illustrations** become an editorial placeholder in italic square brackets:
  `*[Figure: cornet with parts labelled 1–12; captions transcribed below]*`. Then transcribe
  any printed captions and labels as text.
- **Blank pages.** The body is the single line `*[Blank page]*`.
- **Editorial insertions.** Anything not printed in the source goes in `*[…]*`, and only
  where needed.

### Music references

Put a music reference at the point where the music appears in the text, on its own line:

```markdown
[♪ arban-p005-01](../musicxml/arban-p005-01.musicxml)
```

The link text is always `♪ ` followed by the ID, and the target is always
`../musicxml/<id>.musicxml`. Do not add other text inside the link.

When a unit started on an earlier page and continues on this one, reference it again and add
`(continued)` after the link:

```markdown
[♪ arban-p012-03](../musicxml/arban-p012-03.musicxml) (continued)
```

### Pages with parallel languages (Arban)

The Arban prints its prose in three parallel columns: English, German and French. On these
pages, set `parallel: true` and write each language as a complete section, introduced by a
marker:

```markdown
<!-- lang: en -->
## Method of Breathing.

The mouthpiece having been placed on the lips, …

[♪ arban-p005-02](../musicxml/arban-p005-02.musicxml)

<!-- lang: de -->
## Ueber die Art zu athmen.

Ist das Mundstück einmal auf die Lippen gesetzt, …

[♪ arban-p005-02](../musicxml/arban-p005-02.musicxml)

<!-- lang: fr -->
## Manière de respirer.
…
```

- Each section holds that column's text in reading order, including its headings and
  footnotes.
- Music shared by all columns is referenced in **every** section, at the place where that
  language's text refers to it. That way each language reads correctly on its own.
- The markers must appear in the same order as `languages`.

Pages that are mostly music, with only short parallel headings or captions such as "Major
Scales. Dur-Tonleitern. Gammes Majeures.", are **not** `parallel`. Write them as a single
flow and join the parallel versions in one line with ` / ` in printed order:

```markdown
## Major Scales. / Dur-Tonleitern. / Gammes Majeures.
```

### Text or music?

- **Sentences** printed above or between systems (instructions, explanations) go in the
  Markdown, just before the music reference.
- **Musical directions** attached to the staff go in the ABC (see §4). These include tempo
  words, metronome marks, dynamics, *dolce*, *rall.*, *a tempo*, *Var. I*, *Coda*, *Fine*
  and syllables printed under notes.
- **Labels** printed at the start of a staff, such as exercise numbers ("12") or "No. 62",
  go in the ABC `T:` field. Use the per-work notes (§7) for whether to also write a heading.

## 4. Music (ABC)

Write music in [ABC 2.1](https://abcnotation.com/wiki/abc:standard:v2.1); the converter
used here is abc2xml. Write one file per page, with one tune per music unit that **starts**
on that page.

```abc
% illustrative example (not a real transcription)
X:1
T:No. 1
Q:"Andante" 1/4=72
M:C
L:1/8
K:F clef=bass
!p!(F,6 {/A,}G,3/2F,/ | E,4 C,2) z2 | !<(!(A,2 c2- (3cBA!<)! G,2 | !f!F,6) z2 |
!>(!(D,2 E,2 F,2 G,2!>)! | "_rall."!fermata!F,8) |]
```

The first line of music is the first printed system; the second line is the second system.

### Header fields

| Field | Content |
|---|---|
| `X:` | 1, 2, 3, … in reading order on the page. |
| `T:` | The printed number or title of the unit, as printed (`T:No. 62`, `T:12`, `T:HOW FAIR THOU ART.`). Omit it if nothing is printed. |
| `C:` | A composer or attribution printed with the unit, as printed (`C:Mendelssohn`). |
| `Q:` | The tempo as printed: text in quotes, plus a metronome mark only if one is printed (`Q:"Andante cantabile" 1/4=69`, `Q:"Allegro moderato."`). |
| `M:` | The time signature as printed: `C` for common time, `C\|` for cut time, otherwise numbers (`3/4`, `6/8`). |
| `L:` | Any convenient default note length. |
| `K:` | The key as printed **and always an explicit clef**: `K:Bb clef=treble`, `K:Eb clef=bass`, `K:C clef=tenor`. Use `K:C` (or `K:none`) when there is no key signature. |

### Pitch

**ABC pitch is absolute; the clef does not change it.** `C` is middle C (C4), `c` is C5,
`c'` is C6, `C,` is C3 and `C,,` is C2. Music in bass or tenor clef is still written at its
real pitch. For example, the G on the top space of the bass staff is `G,`. Check this in the
proof every time.

### Layout

- **One ABC line per printed system.** Never use `\` to continue a line.
- **Beaming follows spacing.** Notes written together are beamed; a space breaks the beam.
  Match the printed beam groups.
- **Bar lines as printed:** `|`, `||`, `|]`, `|:`, `:|`, `::`. Endings are `[1` and `[2`.

### Changes inside a piece

| Change | ABC |
|---|---|
| Clef | `[K:clef=tenor]` (the key signature is kept) |
| Key | `[K:Eb]`, or `[K:Eb clef=bass]` |
| Meter | `[M:3/4]` |
| Tempo | `[Q:"Allegro"]` |

### Notation

| Notation | ABC |
|---|---|
| Dynamics | `!pp! !p! !mp! !mf! !f! !ff! !sfz!`, before the note |
| Hairpins | `!<(!` … `!<)!` crescendo; `!>(!` … `!>)!` diminuendo |
| Accent / staccato / tenuto | `!>!` / `.` / `!tenuto!` |
| Fermata / breath mark | `!fermata!` / `!breath!` |
| Trill / turn / mordent | `!trill!` / `!turn!`, `!invertedturn!` / `!mordent!`, `!uppermordent!` |
| Slur / tie | `( … )` / `-` |
| Triplet (or any n-tuplet) | `(3abc` (general form `(p:q:r`) |
| Appoggiatura / acciaccatura | `{g}` / `{/g}` (several grace notes: `{ga}`) |
| Text above / below the staff | `"^dolce"` / `"_rall."` |
| Segno, coda, Fine | `!segno!`, `!coda!`, `!fine!` |
| D.C. / D.S. | `!D.C.!`, `!D.S.!`, or the printed text as `"^D.C. al Fine"` |
| Multi-measure rest | `Z4` (4 bars) |
| Syllables under notes | a `w:` line, e.g. `w: tu tu tu ku`. Write a literal hyphen as `\-`. |
| Valve fingerings | `!1!`, `!2!`, `!3!` for single digits, or text such as `"_1 3"` |

Write accidentals exactly as printed, including courtesy accidentals: `^` sharp, `_` flat,
`=` natural.

**Two or more staves** (for example the Arban duets):

```abc
%%score 1 2
V:1 clef=treble
V:2 clef=treble
K:Bb clef=treble
[V:1] B2 d2 | f4 |
[V:2] D2 F2 | B,4 |
```

Add `name="…"` to a `V:` line only when a part name is printed.

**Things ABC cannot express.** For an ossia, cue notes, or an unusual mark, transcribe the
main text and describe the rest in a `%` comment, for example:
`% ossia above bars 5-6: small notes e f g`.

## 5. Uncertainty and misprints

| Case | How to mark it |
|---|---|
| An uncertain reading in text | Your best reading, followed by `<!-- ? -->` |
| Illegible text | `*[illegible]*` |
| Uncertain or illegible music | Your best reading, plus a `%` comment at the end of the line: `% ? bar 3: second note may be F or G` |
| A suspected misprint | Transcribe it as printed and add a comment: `% sic: bar 7 B natural as printed (B flat expected)`, or `<!-- sic -->` in text |

List every uncertainty and misprint in the pull request description as well.

## 6. Units that cross pages and chunks

- A unit belongs to the page where it **starts**. That page's ABC file holds the whole unit,
  even when it continues onto the next page or into the next chunk. Add a comment line
  `% -- page p013 --` where the next page begins.
- The continuation page's Markdown references the unit with `(continued)`. If no music
  starts on that page, it has no ABC file.
- If your chunk's first page opens with music that started on the previous page, do **not**
  transcribe that music. The previous chunk owns it; just add the `(continued)` reference.
- If your chunk's last unit runs past your last page, transcribe it to the end. Render the
  following page to do so.

## 7. Per-work notes

### Arban: *Complete Celebrated Method for the Cornet* (Carl Fischer)

- **Columns.** Prose pages are trilingual in three columns (English, German, French). Use
  `parallel: true` with `languages: [en, de, fr]`. Short parallel headings on music pages
  are written with ` / ` (§3).
- **Exercise numbers** in the margin go in `T:`. Don't repeat them as headings.
- **The Art of Phrasing** (p. 191–245). Each song is a unit. Put its printed title in both a
  `###` heading and `T:`, and the printed composer in `C:`.
- **Sixty-eight duets** (p. 246–282). Use two voices (§4).
- **Fantasias** (p. 300–347). Put "Cornet in B♭" in `running_head`. Each piece is one unit
  that runs over several pages; it belongs to its first page (§6). For long pieces you may
  instead start a new unit at each printed section (Introduction, Thema, Var. I, …). Note
  which you chose in the PR description.
- **Footers.** Plate `3654-290` and footers such as "Copyright 1893 by Carl Fischer, New
  York." go in `plate` and `notice`.
- **Front matter.** On the cover (`f01`), transcribe the printed lines in order, keeping
  their capitalisation. Render the glossary (`f02`) as a table. The fingering charts and
  "tables" (`r05`, `p001`–`p002`) are music units, with valve numbers given as fingerings or
  text (§4).

### Clarke: *Technical Studies for the Cornet* (Second Series, 1912)

- English only.
- Studies are headed "FIRST STUDY", "SECOND STUDY", … (`##`), followed by instructions
  (Markdown paragraphs). The exercises are numbered continuously through the book; put each
  exercise number in `T:`.
- Each "ETUDE I", "ETUDE II", … is a unit with a `###` heading and the same `T:`.
- Instructions printed over a staff, such as "Play the entire page in one breath." and
  "Met. ♩ = 176", are a Markdown paragraph before the reference. The metronome mark also
  goes in `Q:`.
- The footer code (for example `H.L.C. II 49`) goes in `plate`.
- Pencil ticks and handwritten numbers in this copy are omitted.
- `z01`–`z02` are the publisher's advertisements; transcribe them as text.

### Rochut: *120 Melodious Etudes for Trombone* (Carl Fischer, 1928)

- Book 1 contains Nos. 1–60, Book 2 Nos. 61–90 and Book 3 Nos. 91–120. Labels carry the book
  (`b1-`, `b2-`, `b3-`).
- Each etude is a unit. Write `## No. 62` as a heading and `T:No. 62` in the ABC.
- **Clefs.** Bass clef with tenor-clef passages: `[K:clef=tenor]` … `[K:clef=bass]`. Pitch
  is absolute (§4); this is the most common source of errors, so check every clef change in
  the proof.
- Breath marks (printed as a comma) are `!breath!`.
- The book title block (title, "For Trombone", "From the Vocalises of Marco Bordogni",
  "Book One", "Selected & Transcribed by Joannès Rochut") is Markdown at the top of the
  page where it appears. The Book 2 foreword (`b2-p001`) is prose.

## 8. Checking your work

The [`transcribe-chunk`](../.claude/skills/transcribe-chunk/SKILL.md) skill sets out the
full workflow. Before you commit, `python tools/validate.py` must report `0 error(s)`.
Proofread:

- **Text.** Re-read every line against a zoomed tile of the scan. Check diacritics,
  archaic spellings, punctuation and numbers.
- **Music.** Compare the proof (`tools/proof.py`) with the scan system by system. Check:
  - the clef, key and time signature
  - the number of bars per system
  - every pitch, its octave and accidental
  - every rhythm (each bar's durations must add up)
  - slurs and ties
  - dynamics, articulations and text directions

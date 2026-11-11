# Beetle: brand and identity

Working spec for Beetle's identity on `beetle.html`, the docs site (beetlelm.github.io) and the GitHub repo.
Files in this folder:

| file | use |
|---|---|
| `beetle-mark.svg` | primary mark, colour (forest + vermilion), transparent background |
| `beetle-mark-mono.svg` | single colour (`currentColor`); the varied segment becomes an outline |
| `beetle-favicon.svg` | favicon, avatar and social tile: ivory mark on a forest square, no legs |

Implementation on the website: `assets/css/beetle.css`, scoped to `body.beetle-page`.

---

## 1. Positioning

**Statement.** Beetle makes language-model development experimentally observable and controllable.

Beetle is a scientific instrument. It sets the conditions under which language models learn (which
languages, in what order, how much data, which tokeniser, what corpus) and records the run densely
enough that change can be measured as it happens. The 330 released models are the first experiment
run with the instrument. They are not the product.

**Say:** experimental framework, controlled conditions, language experience, developmental trajectory,
matched models, reproducible.
**Avoid:** "a multilingual model collection", "a benchmark", "another open LLM", "an interpretability
toolkit", "a language-learning app", and launch-speak such as revolutionary or game-changing.

**Closing idea**, used at the end of the page and in talks:
> Language models are not simply trained. They develop under particular experiences. Beetle lets us
> control those experiences and study what they produce.

**Personality:** scientific rather than corporate, playful but never childish, precise without being
sterile, open. The beetle stands for development, variation, adaptation and observation, in the sense
of a natural-history collection of specimens. It should never look like a cartoon bug, a children's
product or a conservation charity.

---

## 2. Three identity directions

### A. Specimen plate (recommended)
A top-down beetle built from modular geometry: head, pronotum and eight elytral segments divided by a
central seam. The segments read top to bottom as stages of training. The mark is symmetric except for one
segment in vermilion, which stands for the one condition an experiment changes. The rest of the system
borrows from natural-history plates: ivory paper, forest ink, hairline rules, mono labels ("Plate 1").
*Why:* it carries the core idea (one body plan with controlled variation, development in stages) without
any AI clichés, and it extends into a working diagram language, since the same body can be recoloured to
show a curriculum (see §6).

### B. Instar
Named after the stages between moults. The mark is a stack of four rounded bars that widen from top to
bottom, one stage per bar, with a small head. The identity is mostly typographic: a large Newsreader
wordmark, near-black ground and a chartreuse accent (#c6d93a). *Strength:* it is the most abstract and
the easiest to scale. *Weakness:* it reads as a generic "layers" or "stack" icon, loses the beetle, and
chartreuse is hard to make accessible on light backgrounds.

### C. Elytra matrix
A beetle silhouette drawn on a square grid, 6 × 8 cells, where each cell is one experimental condition
and filled cells show which conditions a run uses. Orange accent on graphite. *Strength:* it maps
directly to the condition matrix and looks very "infrastructure". *Weakness:* it is pixel-art adjacent
and reads as playful-retro rather than scientific, and the grid falls apart below 24 px.

**Recommendation: A.** It is the only direction that works at 16 px and on slides, holds both monochrome
and colour, and explains itself once the caption is read.

---

## 3. Logo

- **Construction** (64-unit grid, see `beetle-mark.svg`): antennae and six legs are 2-unit round-capped
  strokes; head 9 × 6 (r 3); pronotum 26 × 7.5 (r 3); elytra are 34 wide with straight sides from y 25 to 40,
  then an elliptical base (rx 17, ry 19). There are four bands per side with 1.5-unit gaps, and the seam is
  1.5 units wide.
- **The varied segment** is right-hand band 3 (`R3`) in the primary mark. In the monochrome mark it is an
  outline, so the asymmetry survives without colour.
- **Sizes:** use the full mark from 24 px up. Below 24 px, use `beetle-favicon.svg`, which drops the legs
  and thickens the antennae. Clear space is one head-width (9 units) on all sides.
- **Lockup:** mark + "Beetle" in Newsreader SemiBold, cap height ≈ 45% of the mark height, gap = one
  head-width. On the site the hero headline does this job, so no separate lockup is used there.
- **Don'ts:** no gradients, glow, outlines around the whole mark, rotation, or extra coloured segments in
  the logo itself. Multiple coloured segments are for diagrams only.

---

## 4. Palette

| token | light | dark | role |
|---|---|---|---|
| `--bt-paper` | `#f6f2e7` ivory | `#0f1914` | page |
| `--bt-paper-2` | `#fffdf7` | `#16231c` | plates, raised surfaces |
| `--bt-ink` | `#13241c` forest | `#ece6d4` | mark, headings |
| `--bt-ink-2` | `#4d5a50` | `#a9b0a2` | secondary text |
| `--bt-rule` | `#d9d2bf` | `#2c3a32` | hairlines |
| `--bt-accent` | `#d4431f` vermilion | `#ff6f4a` | graphics only |
| `--bt-accent-text` | `#b03514` | `#ff8a6a` | links, accent text |
| `--bt-b1` … `--bt-b5` | `#5e7a4f` moss, `#a87a26` ochre, `#4f6f84` slate, `#a35d48` clay, `#76668a` heather | `#93b37f`, `#d6a94f`, `#8fb0c6`, `#d98f78`, `#b4a3c9` | curricula B1–B5 |

**Contrast, checked with the WCAG 2.x formula** against `--bt-paper` (light) and `#0f1914` (dark):

- ink 14.5:1 (light) and 14.4:1 (dark); ink-2 6.5:1 and 8.1:1; accent-text 5.6:1 and 7.8:1. All pass AA for
  body text.
- Vermilion `#d4431f` reaches 4.1:1 on ivory. That passes for graphics and large text (3:1), but not for
  body text, so text uses `--bt-accent-text`. Ivory on vermilion is also 4.1:1, which is fine for large
  labels only.
- Condition colours on ivory: moss 4.3, ochre 3.4, slate 4.8, clay 4.5, heather 4.7. All clear the 3:1
  non-text threshold. They are never used for body text, and every one of them is labelled ("B1"…), so
  colour is never the only cue.
- Ivory mark on the forest favicon tile: 14.5:1.

---

## 5. Typography

The site already loads these three Google Fonts, so Beetle adds no new font requests:

- **Newsreader** (600, italic 400): headline and section titles. It has the editorial, natural-history
  voice. The hero headline sits at 34–52 px with −0.018em tracking and balanced wrapping.
- **Inter** (400/600): UI text, captions and the two primary links.
- **IBM Plex Mono** (400/600): specimen labels, variable values, the release spec line, axis notes and
  curriculum codes (B1–B5).

A dedicated display face, for example Fraunces, was considered and rejected. It would add a request and
weaken the link to the rest of the site, and Newsreader at 600 is already distinctive enough.

---

## 6. Graphic system

- **Specimen plate:** an ivory panel with a 1 px rule and 3 px radius, a mono label row ("Plate 1 · Beetle"),
  the specimen, then a caption. Use it for any figure that shows the mark or its variants.
- **Body-plan encoding:** the specimen row in the hero recolours the same body for each curriculum. Bands
  run from early to late training, top to bottom, and the right-hand column shows second-language
  exposure, coloured `--bt-bN`. It is schematic and must be captioned as such.
- **Strip charts:** one row per condition. A mono code and a plain label sit on the left; on the right is a
  thin SVG strip (time runs left to right, height is the exposure ratio), with a dashed reference line and
  a shared "start of training / end" axis note. Strokes are non-scaling and there are no gridboxes or
  legends. The same strip shows checkpoint schedules (ticks) and single end-point evaluation (one
  vermilion block).
- **Configuration sheet:** a numbered list of the six variables, each a segment of a 4 px forest "spine".
  The segment for the variable under discussion turns vermilion. Each row gives the name (Newsreader),
  one line of meaning, and the released values in mono. It is not a dashboard: no numbers in boxes, no
  icons.
- **Spec line:** release facts in one mono line separated by vermilion middots, with no stat banners.
- **Motion:** none. Focus states use a 2 px accent-text outline with a 3 px offset.

---

## 7. Hero (as built on `beetle.html`)

On the left: breadcrumb (mono), headline with "Beetle:" in accent-text, the italic question line, the
fixed body paragraph, and two underlined text links ("Explore the Beetle framework →", "Read our EMNLP
2026 paper →"), each with a mono sub-label. On the right is a 330 px specimen plate holding the primary
mark and the B1–B5 specimen row. Below 960 px the plate stacks under the text.

---

## 8. Docs site and GitHub (spec only; nothing outside this website repo has been changed)

**Docs site (beetlelm.github.io)**
- Reuse the tokens in §4 and the fonts in §5. Body text in Inter at 16–17 px, headings in Newsreader,
  code in IBM Plex Mono on `--bt-paper-2` with a `--bt-rule` border.
- Header: favicon-style mark at 28 px + "Beetle" wordmark; nav in Inter.
- Landing page: the same headline, question line and two links as the website hero, followed by the
  configuration sheet as the docs index, one segment per variable linking to its config reference page.
- Curriculum pages: each starts with its strip chart in the matching `--bt-bN` colour.
- Admonitions: a left rule only (forest for notes, vermilion for warnings), with no filled boxes.

**GitHub README header**
- A 1280 × 320 banner on `--bt-paper`: the mark at left (160 px), "Beetle" in Newsreader SemiBold, and one
  line below it: "Make language-model development experimentally observable and controllable." Provide a
  dark variant using `<picture>` with `prefers-color-scheme`.
- Directly beneath: the two links (framework, paper) as plain Markdown links, then the mono spec line.

**Badges**
- Use shields.io "flat" style, label colour `13241c`, value colour `d4431f` for the paper badge and
  `5e7a4f` for the rest. Keep it to four badges: paper (EMNLP 2026), docs, models, licence.

**Social preview (1280 × 640)**
- Forest ground (`#13241c`) with the ivory mark at 280 px on the left and, on the right, the headline in
  ivory Newsreader (two lines). Below the headline, the spec line in Plex Mono at 60% ivory. Keep 80 px
  margins, use no screenshots, and show the vermilion segment as the only accent.

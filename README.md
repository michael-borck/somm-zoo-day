# UDL Lens — session companion

Companion site for two Curtin sessions in August 2026 on [UDL Lens](https://udllens.eduserver.au/),
an AI-assisted audit of unit assessments against the UDL Guidelines 3.0.

- **Assessment 2030 Showcase** — Thursday 20 August
- **SoMM Zoo Day** — Friday 21 August

**Site:** https://michael-borck.github.io/somm-zoo-day/
**Tool:** https://udllens.eduserver.au/ · [source](https://github.com/michael-borck/udl-lens)

## What's here

`docs/` is published by GitHub Pages. It is a single self-contained page — no build
step, no dependencies, no analytics, no cookies.

| | |
|---|---|
| `docs/index.html` | The site. All CSS and JS inline; the coverage data is inlined as JSON. |
| `docs/assets/` | QR codes (SVG for print, PNG for the page) and `coverage.json`. |
| `docs/files/` | The handouts and slides offered for download. |

Two interactive pieces, both client-side — nothing is recorded and no responses leave
the browser:

- **Could you have caught it?** Eight UDL considerations, four real and four invented.
  The invented ones include two verbatim from an early UDL Lens build, where a language
  model produced 21 checkpoints and 16 of the codes were wrong.
- **What can your assessments actually show?** Pick assessment types, see which of the
  nine UDL guidelines they can put in play. No single type reaches more than four.

## Regenerating

The coverage data and QR codes are derived, not hand-written:

```
python3 scripts/build.py
```

Coverage comes from `data/udl-checkpoints.json` in the
[udl-lens](https://github.com/michael-borck/udl-lens) repo, so the site cannot drift
from what the tool actually asks.

## What is deliberately not in this repo

This repo is public, because GitHub Pages on a free account only serves public repos.
Working notes, my co-presenter's slides, and anything derived from them are excluded in
`.gitignore` and stay local. The joint deck goes up when it is agreed, not before.

## Credits

Michael Borck · <michael.borck@curtin.edu.au> — the build and the AI design
Luke Butcher · School of Management and Marketing — UDL, pedagogy, and Assessment 2030

UDL Guidelines 3.0 © CAST (2024), [udlguidelines.cast.org](https://udlguidelines.cast.org/).
The consideration mapping is a first pass under review; treat the tool's output as a
prompt for a conversation, not a compliance score.

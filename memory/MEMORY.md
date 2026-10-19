# pjox-website memory

## Project overview
Static personal academic website for Pedro Ortiz Suarez (pjox.co, moved from portizs.eu in Oct 2026).
Built from scratch to replace the old Hugo/HugoBlox site.

## Tech stack
- Pure HTML/CSS/JS — no build step, no framework
- Google Fonts: Newsreader (display serif) + Hanken Grotesk (text); Academicons from cdnjs
- No external JS libraries
- Deployable to GitHub Pages directly from repo root

## File structure
```
index.html            — main page (about, research, publications)
blog/_template.html   — blog post template (copy & fill in)
publications.bib      — all papers as BibTeX
scripts/bib_to_html.py — updates publications section from .bib
assets/avatar.jpg     — profile photo (user must add this)
```

## Design system ("Folio", Indigo & Amber — chosen Oct 2026)
- Light editorial theme: --bg #F7F7FB, --paper #FFFFFF, --ink #141C4A (indigo)
- Text: --text #2E3456, --muted #5A6080, --faint #7F84A3 (large text only)
- Links: --link #3B4CC0; amber: --accent #9C5800 (text), --accent-fill #EDAA3C (underlines)
- Author name highlight: ink + bold + amber underline (never color alone)
- Colorblind-safe: only blue/indigo vs amber; all text >= 4.5:1
- Fonts: Newsreader for headings/hero/titles, Hanken Grotesk for body
- Favicon: white Hanken Grotesk "P" on indigo rounded square
  (assets/favicon.svg, favicon-32.png, apple-touch-icon.png)
- Social card: scripts/og-card.html -> assets/og-image.png (render with headless Chrome)

## Publication system
Publications are between markers in index.html:
  <!-- PUBLICATIONS_START ... -->
  <!-- PUBLICATIONS_END -->

To update from .bib:
  pip install "bibtexparser<2"   (script uses the v1 API)
  python scripts/bib_to_html.py

Year filter buttons are built by JS from the generated year groups.

Custom .bib fields: url_pdf, url_acl, url_arxiv, url_doi, url_code, url_project, url_hal, url_ceur, badge_class

## User info
- Pedro Ortiz Suarez — Senior Research Scientist at Common Crawl Foundation
- GitHub: pjox, ORCID: 0000-0003-0343-8852
- Colorblind — design avoids red/green information encoding

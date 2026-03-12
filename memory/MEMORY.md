# pjox-website memory

## Project overview
Static personal academic website for Pedro Ortiz Suarez (portizs.eu).
Built from scratch to replace the old Hugo/HugoBlox site.

## Tech stack
- Pure HTML/CSS/JS — no build step, no framework
- Google Fonts: Inter (400,500,600) + Playfair Display (400,600)
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

## Design system
- Dark navy theme: --bg #080e1c, --bg-2 #0d1528, --bg-3 #132040
- Accent blue: --accent #4a9eff, --accent-2 #6fb5ff
- Author name highlight: --gold #d4a832 (amber — colorblind-safe, no red/green)
- Text: --text #d4e4f8 (near-white), --text-2 #8ba0c0 (secondary)
- Fonts: Playfair Display for headings, Inter for body

## Publication system
Publications are between markers in index.html:
  <!-- PUBLICATIONS_START ... -->
  <!-- PUBLICATIONS_END -->

To update from .bib:
  pip install bibtexparser
  python scripts/bib_to_html.py

Custom .bib fields: url_pdf, url_acl, url_arxiv, url_doi, url_code, url_project, url_hal, url_ceur, badge_class

## User info
- Pedro Ortiz Suarez — Senior Research Scientist at Common Crawl Foundation
- GitHub: pjox, ORCID: 0000-0003-0343-8852
- Colorblind — design avoids red/green information encoding

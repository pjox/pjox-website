#!/usr/bin/env python3
"""
bib_to_html.py — Update the publications section of index.html
from a .bib file.

Usage:
    python scripts/bib_to_html.py
    python scripts/bib_to_html.py my.bib
    python scripts/bib_to_html.py my.bib my.html

Requirements:
    pip install bibtexparser

The script finds the markers in index.html:
    <!-- PUBLICATIONS_START ... -->
    <!-- PUBLICATIONS_END -->
and replaces everything between them with freshly generated HTML.

Custom .bib fields (all optional):
    url_pdf      — direct PDF URL
    url_acl      — ACL Anthology page URL
    url_arxiv    — arXiv URL (or bare ID like 2107.07253)
    url_doi      — full DOI URL (https://doi.org/...)
    url_code     — code repository URL
    url_project  — project / demo website URL
    url_hal      — HAL preprint URL
    url_ceur     — CEUR-WS URL
    badge_class  — extra CSS class on the venue badge
"""

from __future__ import annotations

import html
import re
import sys
import textwrap
from collections import defaultdict
from pathlib import Path

try:
    import bibtexparser
    from bibtexparser.bparser import BibTexParser
    from bibtexparser.customization import convert_to_unicode
except ImportError:
    sys.exit(
        "bibtexparser not found.\n"
        "Install it with:  pip install bibtexparser\n"
    )

# ─── Configuration ────────────────────────────────────────────────────────────

# Author name as it appears in BibTeX author fields (Last, First)
HIGHLIGHT_AUTHOR = "Ortiz Suarez, Pedro"

# Display form used in the rendered HTML
HIGHLIGHT_DISPLAY = "Pedro Ortiz Suarez"

# Delimiters in index.html
MARKER_START = "<!-- PUBLICATIONS_START"
MARKER_END = "<!-- PUBLICATIONS_END -->"

# Venue shorthands: lowercase substrings → badge label
VENUE_MAP: list[tuple[str, str]] = [
    (
        "transactions of the association for computational linguistics",
        "TACL",
    ),
    (
        "annual meeting of the association for computational linguistics",
        "ACL",
    ),
    ("empirical methods in natural language processing", "EMNLP"),
    ("north american chapter", "NAACL"),
    ("european chapter", "EACL"),
    (
        "international conference on computational linguistics",
        "COLING",
    ),
    ("language resources and evaluation", "LREC"),
    ("traitement automatique des langues naturelles", "TALN"),
    ("findings of the association", "Findings"),
    ("challenges in the management of large corpora", "CMLC"),
    ("clef", "CLEF"),
    ("text encoding initiative", "TEI"),
    ("workshop", "Workshop"),
]

# Clipboard icon SVG used in the BibTeX copy button
_COPY_ICON = (
    '<svg viewBox="0 0 12 12" aria-hidden="true" '
    'style="width:10px;height:10px;fill:none;stroke:currentColor;'
    'stroke-width:1.8;flex-shrink:0;vertical-align:middle">'
    '<rect x="4" y="4" width="7" height="7" rx="1"/>'
    '<path d="M1 8V1h7" stroke-linecap="round" stroke-linejoin="round"/>'
    "</svg>"
)

# ─── Helpers ──────────────────────────────────────────────────────────────────


def parse_authors(raw: str) -> list[str]:
    """Parse a BibTeX author string into display-order name strings."""
    authors = []
    for part in raw.split(" and "):
        part = part.strip()
        if not part:
            continue
        if "," in part:
            last, _, first = part.partition(",")
            authors.append(f"{first.strip()} {last.strip()}")
        else:
            authors.append(part)
    return authors


def highlight_author(name: str) -> str:
    """Wrap Pedro's name in a highlight span."""
    key = HIGHLIGHT_AUTHOR.lower()
    reversed_key = " ".join(reversed(key.split(", ")))
    if name.lower() in (key, reversed_key):
        return f'<span class="me">{html.escape(HIGHLIGHT_DISPLAY)}</span>'
    return html.escape(name)


def format_authors(raw: str) -> str:
    """Return HTML author string with Pedro's name highlighted."""
    return ", ".join(highlight_author(a) for a in parse_authors(raw))


def infer_venue_badge(entry: dict) -> str:
    """Derive a short venue label from the entry."""
    etype = entry.get("ENTRYTYPE", "")
    if etype == "phdthesis":
        return "Thesis"
    if etype == "misc" and not entry.get("booktitle"):
        return "Preprint"

    source = (
        entry.get("booktitle", "") + " " + entry.get("journal", "")
    ).lower()

    for substring, label in VENUE_MAP:
        if substring in source:
            if label == "CMLC":
                m = re.search(r"cmlc[- ]?(\d+)", source)
                if m:
                    label = f"CMLC-{m.group(1)}"
            return label

    raw = entry.get("booktitle") or entry.get("journal") or "Publication"
    return " ".join(w.capitalize() for w in raw.split()[:3])


def build_links(entry: dict) -> list[tuple[str, str]]:
    """Return (label, url) pairs for the links row."""
    field_labels = [
        ("url_pdf", "PDF"),
        ("url_acl", "ACL"),
        ("url_arxiv", "arXiv"),
        ("url_doi", "DOI"),
        ("url_code", "Code"),
        ("url_project", "Project"),
        ("url_hal", "HAL"),
        ("url_ceur", "CEUR"),
    ]
    links = []
    for field, label in field_labels:
        value = entry.get(field, "").strip()
        if value:
            if field == "url_arxiv" and not value.startswith("http"):
                value = f"https://arxiv.org/abs/{value}"
            links.append((label, value))
    if not links:
        url = entry.get("url", "").strip()
        if url:
            links.append(("Link", url))
    return links


def format_bibtex(entry: dict) -> str:
    """Serialise a parsed entry back to a minimal BibTeX string."""
    etype = entry.get("ENTRYTYPE", "misc")
    key = entry.get("ID", "key")

    doi_val = entry.get("doi", "") or (
        entry.get("url_doi", "").replace("https://doi.org/", "")
        if entry.get("url_doi")
        else ""
    )
    arxiv_val = entry.get("eprint", "") or (
        entry.get("url_arxiv", "").split("/abs/")[-1]
        if entry.get("url_arxiv")
        else ""
    )
    url_val = (
        entry.get("url_acl", "")
        or entry.get("url", "")
        or entry.get("url_hal", "")
    )

    fields = [
        ("author", entry.get("author", "")),
        ("title", entry.get("title", "")),
        ("booktitle", entry.get("booktitle", "")),
        ("journal", entry.get("journal", "")),
        ("school", entry.get("school", "")),
        ("year", entry.get("year", "")),
        ("doi", doi_val),
        ("eprint", arxiv_val),
        ("url", url_val),
    ]

    lines = [f"@{etype}{{{key},"]
    for field, value in fields:
        value = value.strip()
        if not value:
            continue
        if field == "title":
            value = re.sub(r"\{([^{}]*)\}", r"\1", value).strip()
            value = "{" + value + "}"
        lines.append(f"  {field:<10}= {{{value}}},")
    lines.append("}")
    return "\n".join(lines)


# ─── HTML rendering ───────────────────────────────────────────────────────────


def render_pub(entry: dict) -> str:
    """Render a single publication <article> element."""
    year = entry.get("year", "").strip()
    title = entry.get("title", "Untitled").strip()
    title = re.sub(r"^\{(.*)\}$", r"\1", title)
    title = re.sub(r"\{([^}]*)\}", r"\1", title)

    authors = format_authors(entry.get("author", ""))
    badge = infer_venue_badge(entry)

    badge_cls = "pub-badge"
    if entry.get("badge_class"):
        badge_cls += f" {entry['badge_class'].strip()}"
    elif entry.get("ENTRYTYPE") == "phdthesis":
        badge_cls += " badge-thesis"
    elif entry.get("ENTRYTYPE") == "misc" and not entry.get("booktitle"):
        badge_cls += " badge-preprint"

    links = build_links(entry)

    title_url = (
        entry.get("url_acl")
        or entry.get("url_doi")
        or entry.get("url_arxiv")
        or entry.get("url_project")
        or entry.get("url_pdf")
        or entry.get("url_hal")
        or ""
    ).strip()
    if title_url and not title_url.startswith("http"):
        title_url = f"https://arxiv.org/abs/{title_url}"

    safe_title = html.escape(title)
    title_html = (
        f'<a href="{html.escape(title_url)}" '
        f'target="_blank" rel="noopener">{safe_title}</a>'
        if title_url
        else safe_title
    )

    link_tags = "".join(
        f'\n              <a href="{html.escape(url)}" '
        f'class="pub-link" target="_blank" rel="noopener">'
        f"{html.escape(label)}</a>"
        for label, url in links
    )

    copy_btn = (
        '\n              <button class="pub-copy-btn" type="button" '
        f'aria-label="Copy BibTeX citation">{_COPY_ICON} BibTeX</button>'
    )

    bibtex_raw = html.escape(format_bibtex(entry))

    return textwrap.dedent(
        f"""\
          <article class="pub fade-in" data-year="{html.escape(year)}">
            <div class="pub-header">
              <span class="{badge_cls}">{html.escape(badge)}</span>
              <h3 class="pub-title">{title_html}</h3>
            </div>
            <p class="pub-authors">{authors}</p>
            <div class="pub-footer">
              <div class="pub-links">{link_tags}
              </div>{copy_btn}
            </div>
            <pre class="pub-bibtex">{bibtex_raw}</pre>
          </article>"""
    )


# ─── Main ─────────────────────────────────────────────────────────────────────


def main() -> None:
    args = sys.argv[1:]

    script_dir = Path(__file__).parent
    root_dir = script_dir.parent

    bib_path = Path(args[0]) if len(args) > 0 else root_dir / "publications.bib"
    html_path = Path(args[1]) if len(args) > 1 else root_dir / "index.html"

    # ── Parse .bib ────────────────────────────────────────────
    if not bib_path.exists():
        sys.exit(f"Error: bib file not found: {bib_path}")

    parser = BibTexParser(common_strings=True)
    parser.customization = convert_to_unicode

    with bib_path.open(encoding="utf-8") as f:
        db = bibtexparser.load(f, parser=parser)

    if not db.entries:
        sys.exit("Error: no entries found in the bib file.")

    print(f"Parsed {len(db.entries)} entries from {bib_path.name}")

    # ── Group by year ──────────────────────────────────────────
    by_year: dict[str, list[dict]] = defaultdict(list)
    for entry in db.entries:
        year = entry.get("year", "0000").strip()
        by_year[year].append(entry)

    sorted_years = sorted(by_year.keys(), reverse=True)

    # ── Build HTML ─────────────────────────────────────────────
    lines: list[str] = [""]

    for year in sorted_years:
        entries = sorted(
            by_year[year],
            key=lambda e: e.get("author", "").split(",")[0].lower(),
        )
        lines.append(
            f'      <div class="pub-year-group" data-year="{html.escape(year)}">'
        )
        lines.append(
            f'        <div class="pub-year-heading" '
            f'aria-label="Publications from {html.escape(year)}">'
            f"{html.escape(year)}</div>"
        )
        lines.append('        <div class="pub-list">')
        lines.append("")
        for entry in entries:
            lines.append(render_pub(entry))
            lines.append("")
        lines.append("        </div>")
        lines.append(f"      </div><!-- /{year} -->")
        lines.append("")

    new_block = "\n".join(lines)

    # ── Splice into index.html ─────────────────────────────────
    if not html_path.exists():
        sys.exit(f"Error: HTML file not found: {html_path}")

    content = html_path.read_text(encoding="utf-8")

    start_pattern = re.compile(
        r"(" + re.escape(MARKER_START) + r"[^\n]*\n)",
        re.DOTALL,
    )
    end_pattern = re.compile(re.escape(MARKER_END))

    start_match = start_pattern.search(content)
    end_match = end_pattern.search(content)

    if not start_match:
        sys.exit(
            f"Error: start marker '{MARKER_START}' not found in "
            f"{html_path.name}"
        )
    if not end_match:
        sys.exit(
            f"Error: end marker '{MARKER_END}' not found in "
            f"{html_path.name}"
        )
    if start_match.end() > end_match.start():
        sys.exit("Error: start marker appears after end marker.")

    new_content = (
        content[: start_match.end()]
        + new_block
        + "\n      "
        + content[end_match.start():]
    )

    html_path.write_text(new_content, encoding="utf-8")
    total = len(db.entries)
    nyears = len(sorted_years)
    print(
        f"Updated {html_path.name} with {total} publications "
        f"across {nyears} year(s)."
    )


if __name__ == "__main__":
    main()

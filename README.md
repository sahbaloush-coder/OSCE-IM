# Qassim Internal Medicine OSCE — Summary

A browsable study summary of the Qassim Internal Medicine Board OSCE checklists (2021–2025), organized by specialty.

Each specialty has: core history → history add-ons by presentation → core exam → exam add-ons → case scenarios (clues, DDx, grouped workup, results with values in both unit systems, diagnosis, management, examiner questions) → a **Data interpretation** section with the station images (ECGs, X-rays, CT/MRI, smears, urine microscopy, photos).

Extra tabs: **Communication & Counseling** (with Arabic exam phrases) and **Data Interpretation** (PFT, smears, urinalysis).

## Open it

- **Online:** enable GitHub Pages (see below) and open the site link.
- **Offline:** download the repo and open `index.html` in any browser. Keep the `images/` folder next to it.

Features: specialty dashboard, collapsible sections, *Expand all / Collapse all / Sections only*, search within a specialty, dark mode, works on phones.

## Publish with GitHub Pages

1. Create a new repository on GitHub (consider making it **private** — see the note below).
2. Upload everything in this folder (drag and drop on the repo page, or `git push`).
3. Go to **Settings → Pages**, set **Source: Deploy from a branch**, branch `main`, folder `/ (root)`, and save.
4. After a minute the site is live at `https://<your-username>.github.io/<repo-name>/`.

GitHub Pages on a private repository needs a paid GitHub plan; on a free plan, a private repo still works as an offline download.

## Repository layout

```
index.html        the built site (open this)
images/           station images used by the site
content/          one Markdown file per specialty (the source text)
figures/          image captions per specialty (finding + diagnosis)
build.py          rebuilds index.html from content/ and figures/
```

## Editing

Edit the Markdown in `content/` or the captions in `figures/`, then rebuild:

```bash
python3 build.py
```

No packages are needed (Python 3 standard library only).

Markdown conventions used by the builder:

- `## Section`, `### Subsection`, `#### Case` → collapsible levels.
- `- **Label:** item; item; item` → a labeled box; items split on `; ` (or `, ` if there is no semicolon). Commas or semicolons inside parentheses don't split.
- `![caption](image_name)` → shows `images/image_name.jpg`.
- In `figures/<Specialty>.txt`: a line `@ image_name | Title` starts an entry, followed by `- **Findings:** …` and `- **Diagnosis:** …` lines.

## Note on content

This is a personal study aid summarizing course checklists. Some pages were OCR'd from scans, so double-check numbers. Several images come from third-party atlases (watermarks visible) — keep the repo private or remove those images before sharing publicly. Not medical advice.

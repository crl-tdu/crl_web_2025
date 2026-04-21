#!/usr/bin/env python3
"""Convert a thesis PDF into a markdown file under proc/txt/.

Wraps `markitdown` (pdfminer/pdfplumber based) and post-processes the raw
output so the result matches the repository convention used in
proc/txt/*.md:

  * YAML frontmatter identifying the record (file_id, author, year, degree)
  * H1 title line followed by a single-line metadata band
  * Chapter headings promoted to '#', '##### N.M' sections,
    '#### N.M.L' subsections
  * TOC block between '目 次' and the body-side 'N章' heading is dropped
    so the heading promotion does not double-count TOC entries
  * (cid:XXXX) glyph artifacts from uncommon fonts are mapped to real
    characters where a mapping is known, otherwise stripped

Usage:
    python scripts/convert_thesis.py <pdf_path> [<out_md_path>]

If <out_md_path> is omitted, the output is written to
proc/txt/<pdf_stem>.md next to the repo.
"""

from __future__ import annotations

import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

CID_REPLACEMENTS = {
    "(cid:20291)": "鞭",
}

DEGREE_LABEL = {"B": "学士論文", "M": "修士論文", "D": "博士論文"}

CHAPTER_RE = re.compile(r"^第\s*\d+\s*章\s+.+$")
SECTION_RE = re.compile(r"^\d+\.\d+\s+\S.*$")
SUBSECTION_RE = re.compile(r"^\d+\.\d+\.\d+\s+\S.*$")
TOC_HEAD_RE = re.compile(r"^目\s?次\s*$")
CHAPTER_1_RE = re.compile(r"^第\s*1\s*章\s+.+$")


def clean_cid(text: str) -> str:
    for needle, repl in CID_REPLACEMENTS.items():
        text = text.replace(needle, repl)
    return re.sub(r"\(cid:\d+\)", "", text)


def drop_toc_block(lines: list[str]) -> list[str]:
    """Remove the TOC block that runs from the '目 次' line to the SECOND
    occurrence of a '第 1 章 ...' heading. Markitdown emits the chapter 1
    title twice (once inside the TOC, once as the real body start)."""
    toc_start: int | None = None
    chapter1_hits: list[int] = []
    for i, line in enumerate(lines):
        s = line.strip()
        if toc_start is None and TOC_HEAD_RE.match(s):
            toc_start = i
        if CHAPTER_1_RE.match(s):
            chapter1_hits.append(i)
    if toc_start is None or len(chapter1_hits) < 2:
        return lines
    return lines[:toc_start] + lines[chapter1_hits[1]:]


def promote_headings(lines: list[str]) -> list[str]:
    out: list[str] = []
    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped:
            out.append("")
            continue
        if SUBSECTION_RE.match(stripped):
            out.append(f"#### {stripped}")
        elif SECTION_RE.match(stripped):
            out.append(f"##### {stripped}")
        elif CHAPTER_RE.match(stripped):
            out.append(f"# {stripped}")
        else:
            out.append(line)
    return out


def build_frontmatter(author: str, year: int, degree_code: str, filename: str) -> str:
    degree = DEGREE_LABEL[degree_code]
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return (
        "---\n"
        f'title: "{degree} - {author} ({year})"\n'
        f'author: "{author}"\n'
        f"year: {year}\n"
        f'degree: "{degree}"\n'
        f'degree_code: "{degree_code}"\n'
        f'filename: "{filename}"\n'
        f'generated: "{generated}"\n'
        "---\n\n"
    )


def convert(pdf_path: Path, out_path: Path) -> None:
    stem = pdf_path.stem  # e.g. 2025_M_g.otsuka
    year_str, degree_code, author = stem.split("_", 2)
    if degree_code not in DEGREE_LABEL:
        raise SystemExit(f"unrecognised degree code in filename: {stem}")
    year = int(year_str)
    filename = f"{stem}.md"

    raw = subprocess.run(
        ["markitdown", str(pdf_path)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    raw = clean_cid(raw)
    lines = raw.splitlines()
    lines = drop_toc_block(lines)
    lines = promote_headings(lines)

    degree = DEGREE_LABEL[degree_code]
    header = build_frontmatter(author, year, degree_code, filename)
    body_heading = f"# {degree} - {author} ({year})\n\n"
    meta_line = f"**{degree}** | **{year}年度** | **著者**: {author}\n\n"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(header + body_heading + meta_line + "\n".join(lines).rstrip() + "\n")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: convert_thesis.py <pdf> [<out_md>]", file=sys.stderr)
        return 2
    pdf_path = Path(argv[1])
    if len(argv) >= 3:
        out_path = Path(argv[2])
    else:
        repo_root = Path(__file__).resolve().parent.parent
        out_path = repo_root / "proc" / "txt" / f"{pdf_path.stem}.md"
    convert(pdf_path, out_path)
    print(f"wrote: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

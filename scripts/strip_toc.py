#!/usr/bin/env python3
"""Strip table-of-contents content from proc/txt/*.md thesis markdown files.

Detection rules are applied uniformly across all files:
  1. TOC entry lines that contain a dot-space ellipsis run of 4+ repetitions,
     e.g. '### 背景 *. . . . . . . .* 2'
  2. TOC entry lines that contain the Unicode horizontal-ellipsis sequence
     '………' (3+ chars), e.g. '##### 第1章 Intro … 2'
  3. TOC header lines: '## ## 目次', '## 目次', '#### 目 次',
     or a standalone '目 次' / '目次' line
  4. Chapter TOC entries like '第 **1** 章 緒論 **1**' (with or without
     a leading '- ' bullet)
  5. The 'publications' TOC line (本研究に関する発表文献 **N**)

After removal, consecutive blank lines are collapsed to a single blank
line. The operation is idempotent — running the script twice produces
the same output as running it once.

Usage:
    python scripts/strip_toc.py <md> [<md> ...]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

DOT_ELLIPSIS = re.compile(r"\.\s\.\s\.\s\.")
HORIZONTAL_ELLIPSIS = re.compile(r"………")
TOC_HEADER = re.compile(r"^(##\s?##\s?目次|##\s?目次|####\s?目\s?次|目\s?次|目次)\s*$")
CHAPTER_TOC = re.compile(r"^(- )?第\s?\*\*\d+\*\*\s?章\s.*\*\*\d+\*\*\s*$")
PUBLICATION_TOC = re.compile(r"^本研究に関する発表文献\s*\*\*\d+\*\*\s*$")


def is_toc_line(line: str) -> bool:
    stripped = line.rstrip()
    if not stripped:
        return False
    if TOC_HEADER.match(stripped):
        return True
    if CHAPTER_TOC.match(stripped):
        return True
    if PUBLICATION_TOC.match(stripped):
        return True
    if DOT_ELLIPSIS.search(stripped):
        return True
    if HORIZONTAL_ELLIPSIS.search(stripped):
        return True
    return False


def collapse_blanks(lines: list[str]) -> list[str]:
    out: list[str] = []
    prev_blank = False
    for line in lines:
        blank = line.strip() == ""
        if blank and prev_blank:
            continue
        out.append(line)
        prev_blank = blank
    return out


def strip_toc(text: str) -> tuple[str, int]:
    kept: list[str] = []
    removed = 0
    for line in text.splitlines():
        if is_toc_line(line):
            removed += 1
            continue
        kept.append(line)
    kept = collapse_blanks(kept)
    result = "\n".join(kept)
    if not result.endswith("\n"):
        result += "\n"
    return result, removed


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: strip_toc.py <md> [<md> ...]", file=sys.stderr)
        return 2
    total = 0
    for arg in argv[1:]:
        p = Path(arg)
        original = p.read_text()
        new_text, removed = strip_toc(original)
        if new_text != original:
            p.write_text(new_text)
        total += removed
        print(f"{p}: -{removed} lines")
    print(f"total removed: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

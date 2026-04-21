#!/usr/bin/env python3
"""Rebuild derived artifacts from dataset/research and dataset/members.

Walks dataset/research/records/*/index.md and dataset/members/records/*.md,
parses their YAML frontmatter, and writes:

  * dataset/quality.md          — quality report (record counts by degree,
                                   skeleton / generic records, missing
                                   thumbnails / symbolic / extracted images,
                                   doctoral record status)
  * data/thesis.json            — flat list of thesis records
  * data/members.json           — flat list of member records

Derived artifacts are considered disposable: re-running this script
produces a deterministic result from the current dataset/ state. If these
files drift from the dataset, run this script to refresh them.

Usage:
    python scripts/build_derived.py
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
DS_RESEARCH = REPO / "dataset" / "research" / "records"
DS_MEMBERS = REPO / "dataset" / "members" / "records"
PROC_IMG = REPO / "proc" / "img"
PROC_IMG_ALL = REPO / "proc" / "img_all"

DATA_DIR = REPO / "data"
QUALITY_MD = REPO / "dataset" / "quality.md"
THESIS_JSON = DATA_DIR / "thesis.json"
MEMBERS_JSON = DATA_DIR / "members.json"

DEGREE_LABEL = {"B": "学士論文", "M": "修士論文", "D": "博士論文"}


# ---------- tiny YAML frontmatter parser --------------------------------

_SCALAR_RE = re.compile(r'^"(.*)"\s*$')


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return ""
    if value == "null":
        return None
    if value == "[]":
        return []
    m = _SCALAR_RE.match(value)
    if m:
        return m.group(1)
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d+\.\d+", value):
        return float(value)
    return value


def parse_frontmatter(text: str) -> dict[str, Any]:
    """Parse the simple YAML frontmatter dialect used in this repo.

    Supports:
      * scalar: key: "value" / key: value / key: 123
      * flow sequence: key: []
      * block sequence of scalars: key:\n  - "a"\n  - "b"
      * block mapping: key:\n  inner: "v"
      * list of mappings (e.g. degree_records): key:\n  -\n    a: 1\n    b: 2
    """
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end < 0:
        return {}
    body = text[4:end]

    lines = body.splitlines()
    result: dict[str, Any] = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, rest = m.group(1), m.group(2)
        if rest.strip():
            result[key] = _parse_scalar(rest)
            i += 1
            continue
        # block follows — look ahead
        j = i + 1
        block: list[str] = []
        while j < len(lines):
            nxt = lines[j]
            if nxt and not nxt.startswith(" ") and nxt != "":
                break
            block.append(nxt)
            j += 1
        result[key] = _parse_block(block)
        i = j
    return result


def _parse_block(block: list[str]) -> Any:
    # Strip trailing blank lines
    while block and not block[-1].strip():
        block.pop()
    if not block:
        return None
    # List of scalars: lines like '  - "abc"'
    if all(re.match(r"^\s*-\s+\S", line) for line in block if line.strip()):
        return [_parse_scalar(re.sub(r"^\s*-\s+", "", line))
                for line in block if line.strip()]
    # List of mappings: lines start with '  -\n    key: value'
    if any(re.match(r"^\s*-\s*$", line) for line in block):
        return _parse_list_of_maps(block)
    # Block mapping (inner keys at +2 indent)
    return _parse_block_mapping(block)


def _parse_list_of_maps(block: list[str]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for line in block:
        if re.match(r"^\s*-\s*$", line):
            if current is not None:
                items.append(current)
            current = {}
            continue
        m = re.match(r"^\s+([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
        if m and current is not None:
            current[m.group(1)] = _parse_scalar(m.group(2))
    if current is not None:
        items.append(current)
    return items


def _parse_block_mapping(block: list[str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for line in block:
        m = re.match(r"^\s+([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
        if m:
            out[m.group(1)] = _parse_scalar(m.group(2))
    return out


# ---------- scan dataset -------------------------------------------------

def scan_research() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for d in sorted(DS_RESEARCH.iterdir()):
        if not d.is_dir():
            continue
        idx = d / "index.md"
        if not idx.exists():
            continue
        fm = parse_frontmatter(idx.read_text())
        fm["_dir"] = d
        records.append(fm)
    return records


def scan_members() -> list[dict[str, Any]]:
    members: list[dict[str, Any]] = []
    for f in sorted(DS_MEMBERS.iterdir()):
        if not f.is_file() or f.suffix != ".md":
            continue
        fm = parse_frontmatter(f.read_text())
        if fm:
            members.append(fm)
    return members


# ---------- builders -----------------------------------------------------

def build_thesis_json(records: list[dict[str, Any]]) -> None:
    theses = []
    bachelor = master = doctor = 0
    for r in records:
        code = r.get("degree_code", "")
        entry = {
            "file_id": r.get("research_id", ""),
            "title": r.get("title", ""),
            "title_en": r.get("title_en", ""),
            "author": r.get("member_name", ""),
            "member_id": r.get("member_id", ""),
            "student_id": r.get("student_id", ""),
            "year": r.get("year", 0),
            "degree_type": r.get("degree_type", ""),
            "degree_code": code,
            "detail_quality": r.get("detail_quality", ""),
        }
        theses.append(entry)
        if code == "B":
            bachelor += 1
        elif code == "M":
            master += 1
        elif code == "D":
            doctor += 1

    out = {
        "metadata": {
            "description": "論文データベース（dataset/research から build_derived.py で生成）",
            "generated": date.today().isoformat(),
            "source": "dataset/research/records/*/index.md",
            "total_records": len(theses),
            "bachelor_count": bachelor,
            "master_count": master,
            "doctor_count": doctor,
        },
        "theses": theses,
    }
    THESIS_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")


def build_members_json(members: list[dict[str, Any]]) -> None:
    out = {
        "metadata": {
            "description": "研究室メンバーデータベース（dataset/members から build_derived.py で生成）",
            "generated": date.today().isoformat(),
            "source": "dataset/members/records/*.md",
            "total_members": len(members),
        },
        "members": members,
    }
    MEMBERS_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")


def build_quality_md(records: list[dict[str, Any]]) -> None:
    by_degree: dict[str, int] = {"B": 0, "M": 0, "D": 0}
    generic: list[str] = []
    skeleton: list[str] = []
    missing_thumb: list[str] = []
    missing_symbolic: list[str] = []
    missing_extracted: list[str] = []

    for r in records:
        rid = r.get("research_id", "")
        code = r.get("degree_code", "")
        by_degree[code] = by_degree.get(code, 0) + 1
        q = r.get("detail_quality", "")
        if q == "generic":
            generic.append(rid)
        elif q == "skeleton":
            skeleton.append(rid)

        thumb = r.get("thumbnail_path")
        if thumb and not (REPO / thumb).exists():
            missing_thumb.append(rid)
        sym_paths = r.get("symbolic_image_paths") or []
        if not sym_paths or any(not (REPO / p).exists() for p in sym_paths):
            missing_symbolic.append(rid)
        # Extracted images live in proc/img_all/ under one of two naming
        # conventions: '<file_id>-p<NN>-img<NN>.png' or
        # '<file_id>_page<NN>_img<NN>.png'.
        extracted: list[Path] = []
        if PROC_IMG_ALL.exists():
            extracted = (
                list(PROC_IMG_ALL.glob(f"{rid}-p*-img*.png"))
                + list(PROC_IMG_ALL.glob(f"{rid}_page*_img*.png"))
            )
        if not extracted:
            missing_extracted.append(rid)

    total = len(records)

    def listing(title: str, ids: list[str]) -> str:
        lines = [f"## {title}", "", f"- Count: {len(ids)}", ""]
        if not ids:
            lines.append("- None")
        else:
            for rid in ids:
                lines.append(f"- [`{rid}`](research/records/{rid}/index.md)")
        lines.append("")
        return "\n".join(lines)

    doctoral_section = (
        "## Doctoral Records\n\n"
        + ("- No doctoral thesis record was found in the current source dataset.\n"
           if by_degree.get("D", 0) == 0
           else f"- Doctoral records: {by_degree['D']}\n")
    )

    parts = [
        "# Dataset Quality Report",
        "",
        f"- Generated: {date.today().isoformat()}",
        f"- Research records: {total}",
        f"- Bachelor records: {by_degree.get('B', 0)}",
        f"- Master records: {by_degree.get('M', 0)}",
        f"- Doctoral records: {by_degree.get('D', 0)}",
        "",
        listing("Skeleton Records", skeleton),
        listing("Generic Detail Records", generic),
        listing("Missing Thumbnails", missing_thumb),
        listing("Missing Symbolic Images", missing_symbolic),
        listing("Missing Extracted Images", missing_extracted),
        doctoral_section,
    ]
    QUALITY_MD.write_text("\n".join(parts))


def main(argv: list[str]) -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    research = scan_research()
    members = scan_members()
    build_thesis_json(research)
    build_members_json(members)
    build_quality_md(research)
    print(f"research records: {len(research)} → {THESIS_JSON.relative_to(REPO)}")
    print(f"members: {len(members)} → {MEMBERS_JSON.relative_to(REPO)}")
    print(f"quality report: {QUALITY_MD.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

#!/usr/bin/env python3
"""Build web-facing view JSONs (cards.json, facets.json) from dataset/.

These are derived artifacts introduced by ADR-0004 (派生戦略: 凍結
スナップショットと新規派生の並走). The frozen JSONs under data/
(project.json, keywords.json, portfolio_research.json,
legacy_project_index.json) are NOT touched by this script.

Outputs:
  * data/cards.json   — minimal card view (one entry per visible research
                        record, lightweight enough for client-side filtering)
  * data/facets.json  — facet aggregations for navigation (themes, keywords,
                        years, degrees) with empty facets stripped

Inputs:
  * dataset/research/records/*/index.md   (frontmatter: titles, tagline,
                                            themes, visibility, relations,
                                            consent override, etc.)
  * dataset/research/records/*/assets.md  (frontmatter: images[] with role
                                            field, ADR-0004 Web Designer req)
  * dataset/members/records/*.md          (frontmatter: display_consent_default)

The parser from build_derived.py is reused as-is.

Usage:
    python scripts/build_web_views.py
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))
from build_derived import DS_MEMBERS, DS_RESEARCH, parse_frontmatter  # noqa: E402

REPO = THIS_DIR.parent
DATA_DIR = REPO / "data"
CARDS_JSON = DATA_DIR / "cards.json"
FACETS_JSON = DATA_DIR / "facets.json"

# Closed set of themes per ADR-0001. Ordered as the canonical
# navigation order (coverage desc, with wellness placed last as a
# growing focus area).
ADR_THEMES = [
    "human-sensing",
    "cooperation-theory",
    "skill-acquisition",
    "haptic-interaction",
    "teamwork-and-swarm",
    "wellness-engineering",
]

# Visibility values that hide a record from public web views.
HIDDEN_VISIBILITY = {"members_only", "draft", "embargoed"}

def _today_iso() -> str:
    # Date-only string keeps `make check` deterministic within a day,
    # matching the convention used by build_derived.py.
    return date.today().isoformat()


# ---------- loaders ------------------------------------------------------

def _strip_frontmatter(md: str) -> str:
    """Return the body of a markdown file with YAML frontmatter removed."""
    if not md.startswith("---\n"):
        return md.strip()
    end = md.find("\n---", 4)
    if end < 0:
        return md.strip()
    return md[end + 4:].strip()


def _strip_heading_and_meta(body: str) -> str:
    """For detail.md bodies that lead with `# Title` + meta lines, drop those
    so the summary modal doesn't show duplicated heading info."""
    lines = body.splitlines()
    out: list[str] = []
    skipping = True
    for line in lines:
        if skipping:
            s = line.strip()
            if not s:
                continue
            # Skip H1 + metadata lines like '**研究者**: …', '---', '**キーワード**: …'
            if s.startswith("#") or s.startswith("**") or s == "---":
                continue
            skipping = False
        out.append(line)
    return "\n".join(out).strip()


def load_research_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for d in sorted(DS_RESEARCH.iterdir()):
        if not d.is_dir():
            continue
        idx = d / "index.md"
        if not idx.exists():
            continue
        fm = parse_frontmatter(idx.read_text(encoding="utf-8"))
        af = d / "assets.md"
        fm["_assets"] = (
            parse_frontmatter(af.read_text(encoding="utf-8")) if af.exists() else {}
        )
        sf = d / "summary.md"
        if sf.exists():
            body = _strip_frontmatter(sf.read_text(encoding="utf-8"))
            fm["_summary_body"] = _strip_heading_and_meta(body)
        else:
            fm["_summary_body"] = ""
        records.append(fm)
    return records


def load_members() -> dict[str, dict[str, Any]]:
    members: dict[str, dict[str, Any]] = {}
    for f in sorted(DS_MEMBERS.iterdir()):
        if not f.is_file() or f.suffix != ".md":
            continue
        fm = parse_frontmatter(f.read_text(encoding="utf-8"))
        mid = fm.get("member_id")
        if mid:
            members[mid] = fm
    return members


# ---------- helpers ------------------------------------------------------

def find_card_image(assets_fm: dict[str, Any]) -> dict[str, Any] | None:
    """Return the entry in images[] whose role is 'card', or None."""
    images = assets_fm.get("images")
    if not isinstance(images, list):
        return None
    for img in images:
        if isinstance(img, dict) and img.get("role") == "card":
            return img
    return None


def effective_consent(
    research_fm: dict[str, Any], member_fm: dict[str, Any] | None
) -> dict[str, Any]:
    """ADR-0003: research.display_consent_override beats member.display_consent_default,
    field-by-field. Missing fields fall back to the member default."""
    default = (member_fm or {}).get("display_consent_default") or {}
    override = research_fm.get("display_consent_override")
    if not isinstance(override, dict):
        override = {}
    merged: dict[str, Any] = {}
    for key in (
        "show_full_name",
        "show_face_photo",
        "show_thesis_body",
        "display_name_preference",
    ):
        if key in override:
            merged[key] = override[key]
        elif key in default:
            merged[key] = default[key]
    return merged


# ---------- builders -----------------------------------------------------

def build_cards_json(
    records: list[dict[str, Any]], members: dict[str, dict[str, Any]]
) -> None:
    cards: list[dict[str, Any]] = []
    skipped_hidden = 0
    for r in records:
        visibility = r.get("visibility", "public")
        if visibility in HIDDEN_VISIBILITY:
            skipped_hidden += 1
            continue
        member_fm = members.get(r.get("member_id", ""))
        consent = effective_consent(r, member_fm)
        card_img = find_card_image(r.get("_assets") or {}) or {}
        cards.append(
            {
                "file_id": r.get("research_id", ""),
                "title_ja": r.get("title_ja") or r.get("title", ""),
                "title_en": r.get("title_en", ""),
                "tagline_ja": r.get("tagline_ja", ""),
                "tagline_en": r.get("tagline_en", ""),
                "member_name": r.get("member_name", ""),
                "member_id": r.get("member_id", ""),
                "year": r.get("year", 0),
                "degree_code": r.get("degree_code", ""),
                "research_themes": r.get("research_themes") or [],
                "keywords": r.get("keywords") or [],
                "summary": r.get("_summary_body") or "",
                "card_image": card_img.get("src"),
                "card_image_alt_ja": card_img.get("alt_ja", ""),
                "card_image_alt_en": card_img.get("alt_en", ""),
                "card_image_status": card_img.get("generated_status", ""),
                "visibility": visibility,
                "featured": bool(r.get("featured", False)),
                "predecessor_file_id": r.get("predecessor_file_id"),
                "successor_file_id": r.get("successor_file_id"),
                "detail_quality": r.get("detail_quality", ""),
                "effective_consent": consent,
                "schema_version": r.get("schema_version", "1.x-legacy"),
            }
        )

    out = {
        "metadata": {
            "description": "カード型ポートフォリオ用ビューデータ (ADR-0004)",
            "generated_at": _today_iso(),
            "source": "dataset/research/records/*/index.md + assets.md",
            "schema_version": "1.0",
            "total_cards": len(cards),
            "skipped_hidden_records": skipped_hidden,
        },
        "cards": cards,
    }
    CARDS_JSON.write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"cards: {len(cards)} visible / {skipped_hidden} hidden "
        f"→ {CARDS_JSON.relative_to(REPO)}"
    )


def build_facets_json(records: list[dict[str, Any]]) -> None:
    themes_counter: Counter[str] = Counter()
    keywords_counter: Counter[str] = Counter()
    years_counter: Counter[int] = Counter()
    degrees_counter: Counter[str] = Counter()
    visible_records = 0
    unrecognized_themes: Counter[str] = Counter()

    for r in records:
        if r.get("visibility", "public") in HIDDEN_VISIBILITY:
            continue
        visible_records += 1
        for t in r.get("research_themes") or []:
            themes_counter[t] += 1
            if t not in ADR_THEMES:
                unrecognized_themes[t] += 1
        for k in r.get("keywords") or []:
            keywords_counter[k] += 1
        y = r.get("year")
        if isinstance(y, int) and y > 0:
            years_counter[y] += 1
        d = r.get("degree_code")
        if d:
            degrees_counter[d] += 1

    themes_out = [
        {"slug": s, "count": themes_counter.get(s, 0)}
        for s in ADR_THEMES
        if themes_counter.get(s, 0) > 0
    ]
    keywords_out = [
        {"value": v, "count": c} for v, c in keywords_counter.most_common(50)
    ]
    years_out = [
        {"year": y, "count": c} for y, c in sorted(years_counter.items(), reverse=True)
    ]
    degrees_out = [
        {"code": d, "count": degrees_counter.get(d, 0)}
        for d in ("B", "M", "D")
        if degrees_counter.get(d, 0) > 0
    ]

    out = {
        "metadata": {
            "description": "ファセット検索用集計 (ADR-0004)",
            "generated_at": _today_iso(),
            "source": "dataset/research/records/*/index.md",
            "schema_version": "1.0",
            "visible_records": visible_records,
            "unrecognized_themes": dict(unrecognized_themes),
        },
        "themes": themes_out,
        "keywords": keywords_out,
        "years": years_out,
        "degrees": degrees_out,
    }
    FACETS_JSON.write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"facets: {len(themes_out)} themes / {len(keywords_out)} keywords / "
        f"{len(years_out)} years → {FACETS_JSON.relative_to(REPO)}"
    )
    if unrecognized_themes:
        print(
            f"  ⚠ unrecognized theme slugs (not in ADR-0001): {dict(unrecognized_themes)}"
        )


# ---------- main ---------------------------------------------------------

def main() -> int:
    records = load_research_records()
    members = load_members()
    build_cards_json(records, members)
    build_facets_json(records)
    return 0


if __name__ == "__main__":
    sys.exit(main())

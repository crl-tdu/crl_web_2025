#!/usr/bin/env python3
"""Generate a dataset skeleton under dataset/research/records/<file_id>/
and refresh the corresponding member record.

The skeleton includes:
  * summary.md  — card-facing metadata + placeholder body
  * detail.md   — section placeholders for 研究背景 / 目的 / 提案 / 実験 / 成果
  * assets.md   — expected image paths, flagged as pending_image_generation
  * index.md    — manifest

The member record at dataset/members/records/<member_id>.md is updated to
include the new degree entry in `degree_records:` and its `active_years`
/ `highest_degree` / `research_period` are bumped accordingly.

Usage:
    python scripts/scaffold_record.py \\
        --file-id 2025_M_g.otsuka \\
        --title '...' \\
        --title-en '...' \\
        --student-id 24KMH04 \\
        --member-name '大塚 凱'

file_id format: <year>_<degree_code>_<member_id>, where degree_code is
one of B (学士論文) / M (修士論文) / D (博士論文).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RESEARCH_DIR = REPO / "dataset" / "research" / "records"
MEMBERS_DIR = REPO / "dataset" / "members" / "records"

DEGREE_LABEL = {"B": "学士論文", "M": "修士論文", "D": "博士論文"}


def frontmatter_common(record_type: str, file_id: str, member_id: str, member_name: str,
                       student_id: str, title: str, title_en: str, year: int,
                       degree_code: str, extra_tail: str = "") -> str:
    return (
        "---\n"
        f'record_type: "{record_type}"\n'
        f'research_id: "{file_id}"\n'
        f'title: "{title}"\n'
        f'title_en: "{title_en}"\n'
        f'member_id: "{member_id}"\n'
        f'member_name: "{member_name}"\n'
        f'student_id: "{student_id}"\n'
        f"year: {year}\n"
        f'degree_type: "{DEGREE_LABEL[degree_code]}"\n'
        f'degree_code: "{degree_code}"\n'
        "keywords: []\n"
        "display_tags: []\n"
        'detail_quality: "skeleton"\n'
        f'thumbnail_path: "proc/img/{file_id}_thumbnail.png"\n'
        "symbolic_image_paths:\n"
        f'  - "proc/img/{file_id}_overview.png"\n'
        f'  - "proc/img/{file_id}_result.png"\n'
        "source_paths:\n"
        f'  fulltext_markdown: "proc/txt/{file_id}.md"\n'
        f'  pdf: "pdfs/{file_id}.pdf"\n'
        f"{extra_tail}"
        "---\n\n"
    )


def write_summary(dir_path: Path, args_bundle: dict) -> None:
    fm = frontmatter_common("research_summary", **args_bundle)
    body = (
        f"# {args_bundle['title']}\n\n"
        f"{args_bundle['year']}年度 {DEGREE_LABEL[args_bundle['degree_code']]}。"
        f"（カード向け要約本文は後続タスクで作成する。全文は "
        f"`proc/txt/{args_bundle['file_id']}.md` を参照。）\n"
    )
    (dir_path / "summary.md").write_text(fm + body)


def write_detail(dir_path: Path, args_bundle: dict) -> None:
    fm = frontmatter_common("research_detail", **args_bundle)
    body = (
        f"# {args_bundle['title']}\n\n"
        f"**English Title**: {args_bundle['title_en']}\n\n"
        f"**研究者**: {args_bundle['member_name']} ({args_bundle['member_id']}, "
        f"{args_bundle['year']})  \n"
        "**キーワード**: （未設定）\n\n"
        "---\n\n"
        "## 研究背景・動機\n\n"
        f"（全文 `proc/txt/{args_bundle['file_id']}.md` から要点を整理する。）\n\n"
        "## 研究目的・課題設定\n\n（未記載）\n\n"
        "## 提案手法・システム\n\n（未記載）\n\n"
        "## 実験・評価\n\n（未記載）\n\n"
        "## 成果・貢献\n\n（未記載）\n"
    )
    (dir_path / "detail.md").write_text(fm + body)


def write_assets(dir_path: Path, args_bundle: dict) -> None:
    file_id = args_bundle["file_id"]
    content = (
        "---\n"
        'record_type: "research_assets"\n'
        f'research_id: "{file_id}"\n'
        f'title: "{args_bundle["title"]}"\n'
        f'thumbnail_path: "proc/img/{file_id}_thumbnail.png"\n'
        "symbolic_image_paths:\n"
        f'  - "proc/img/{file_id}_overview.png"\n'
        f'  - "proc/img/{file_id}_result.png"\n'
        "symbolic_image_count: 0\n"
        "extracted_image_count: 0\n"
        'status: "pending_image_generation"\n'
        "---\n\n"
        f"# Assets for {args_bundle['title']}\n\n"
        "## Thumbnail\n\n"
        f"- `proc/img/{file_id}_thumbnail.png` (未生成)\n\n"
        "## Symbolic Images\n\n"
        f"- `proc/img/{file_id}_overview.png` (未生成)\n"
        f"- `proc/img/{file_id}_result.png` (未生成)\n\n"
        "## Extracted Images\n\n"
        "- （未生成。必要に応じて PDF からページ画像を抽出する。）\n"
    )
    (dir_path / "assets.md").write_text(content)


def write_index(dir_path: Path, args_bundle: dict) -> None:
    extra = (
        "extracted_image_count: 0\n"
        "issues:\n"
        '  - "skeleton"\n'
        '  - "pending_image_generation"\n'
    )
    fm = frontmatter_common("research_record", extra_tail=extra, **args_bundle)
    file_id = args_bundle["file_id"]
    body = (
        f"# {args_bundle['title']}\n\n"
        f"- Research ID: `{file_id}`\n"
        f"- Member: {args_bundle['member_name']} (`{args_bundle['member_id']}`)\n"
        f"- Student ID: `{args_bundle['student_id']}`\n"
        f"- Year: {args_bundle['year']}\n"
        f"- Degree: {DEGREE_LABEL[args_bundle['degree_code']]} "
        f"(`{args_bundle['degree_code']}`)\n"
        "- Detail quality: `skeleton`\n"
        "- Status: skeleton / pending_image_generation\n\n"
        "## Files\n\n"
        "- [summary.md](summary.md)\n"
        "- [detail.md](detail.md)\n"
        "- [assets.md](assets.md)\n"
        f"- [member record](../../../members/records/{args_bundle['member_id']}.md)\n\n"
        "## Source Files\n\n"
        f"- `fulltext_markdown`: [`proc/txt/{file_id}.md`]"
        f"(../../../../proc/txt/{file_id}.md)\n"
        f"- `pdf`: [`pdfs/{file_id}.pdf`](../../../../pdfs/{file_id}.pdf)\n"
    )
    (dir_path / "index.md").write_text(fm + body)


def update_member(member_id: str, file_id: str, title: str, year: int, degree_code: str) -> None:
    path = MEMBERS_DIR / f"{member_id}.md"
    if not path.exists():
        print(f"note: member record not found, skipping member update: {path}",
              file=sys.stderr)
        return
    text = path.read_text()
    degree_label = DEGREE_LABEL[degree_code]

    text = re.sub(r'highest_degree:\s*"[^"]*"',
                  f'highest_degree: "{degree_label}"', text, count=1)

    def rp_repl(m: re.Match[str]) -> str:
        start = m.group(1)
        return f'research_period: "{start}-{year}"'
    text = re.sub(r'research_period:\s*"(\d{4})-(\d{4}|現在)"',
                  rp_repl, text, count=1)

    def ay_repl(m: re.Match[str]) -> str:
        block = m.group(0)
        existing = {int(y) for y in re.findall(r"-\s*(\d+)", block)}
        start = min(existing) if existing else year
        years = sorted(set(existing) | set(range(start, year + 1)))
        return "active_years:\n" + "".join(f"  - {y}\n" for y in years)
    text = re.sub(r"active_years:\n(?:  - \d+\n)+", ay_repl, text, count=1)

    new_entry = (
        "  -\n"
        f'    file_id: "{file_id}"\n'
        f'    title: "{title}"\n'
        f'    degree_type: "{degree_label}"\n'
        f"    year: {year}\n"
        f'    research_record: "../../research/records/{file_id}/index.md"\n'
    )
    if new_entry not in text:
        text = re.sub(
            r"(degree_records:\n(?:(?:  -\n(?:    \S+:.*\n)+)+))",
            lambda m: m.group(1) + new_entry,
            text,
            count=1,
        )

    text = re.sub(r"- Highest Degree:\s*\S+", f"- Highest Degree: {degree_label}",
                  text, count=1)
    text = re.sub(r"- Research Period:\s*(\d{4})-(\d{4}|現在)",
                  lambda m: f"- Research Period: {m.group(1)}-{year}", text, count=1)

    body_bullet = (
        f"- [`{file_id}`](../../research/records/{file_id}/index.md): "
        f"{year} / {degree_label} / {title}\n"
    )
    if body_bullet.rstrip() not in text:
        text = text.rstrip() + "\n" + body_bullet

    path.write_text(text)


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--file-id", required=True,
                   help="e.g. 2025_M_g.otsuka")
    p.add_argument("--title", required=True)
    p.add_argument("--title-en", default="")
    p.add_argument("--student-id", required=True)
    p.add_argument("--member-name", required=True)
    return p.parse_args(argv[1:])


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    m = re.fullmatch(r"(\d{4})_([BMD])_(\S+)", args.file_id)
    if not m:
        raise SystemExit(f"invalid file_id format: {args.file_id}")
    year = int(m.group(1))
    degree_code = m.group(2)
    member_id = m.group(3)

    bundle = dict(
        file_id=args.file_id,
        member_id=member_id,
        member_name=args.member_name,
        student_id=args.student_id,
        title=args.title,
        title_en=args.title_en,
        year=year,
        degree_code=degree_code,
    )

    dir_path = RESEARCH_DIR / args.file_id
    dir_path.mkdir(parents=True, exist_ok=True)

    write_summary(dir_path, bundle)
    write_detail(dir_path, bundle)
    write_assets(dir_path, bundle)
    write_index(dir_path, bundle)

    update_member(member_id, args.file_id, args.title, year, degree_code)

    print(f"scaffolded: {dir_path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

# scripts/

Annual ingestion and dataset-maintenance scripts for this repository.
All scripts are plain Python 3.11+ and take no dependencies outside the
standard library, except `convert_thesis.py` which shells out to the
`markitdown` CLI.

## Overview

| Script | 役割 |
|---|---|
| `convert_thesis.py` | PDF → `proc/txt/<file_id>.md`（markitdown + 見出し昇格 + 目次ブロック除外 + CIDクリーンアップ） |
| `strip_toc.py` | 既存 `proc/txt/*.md` の TOC 行を冪等に削除 |
| `scaffold_record.py` | `dataset/research/records/<file_id>/` と対応メンバーレコードを生成・更新 |
| `build_derived.py` | `dataset/` から `data/thesis.json` / `data/members.json` / `dataset/quality.md` を再生成 |

## 年次ワークフロー（論文1本を追加するとき）

```bash
# 1. PDFをリネームして pdfs/ に置く  →  pdfs/2026_M_foo.pdf
# 2. 本文マークダウン化
make convert PDF=pdfs/2026_M_foo.pdf
make strip-toc

# 3. datasetレコード骨組み生成（PDF表紙から拾ったメタ情報を流し込む）
make scaffold \
  FILE_ID=2026_M_foo \
  TITLE='心拍情報を用いた…' \
  TITLE_EN='Sleep State …' \
  STUDENT_ID=25KMH01 \
  MEMBER_NAME='山田 太郎'

# 4. 派生ファイルを更新
make derive
```

## 品質維持フロー

- `make derive`: `dataset/` の変更を `data/*.json` と `dataset/quality.md` に反映
- `make check`: 派生ファイルが `dataset/` と整合しているかだけ検証（差分があれば exit 1）

`data/` および `dataset/quality.md` は**派生ファイル**として扱う方針です。
手作業で編集せず、必要に応じて `make derive` を実行してください。

## データ設計の責任分担

- `proc/txt/*.md` — 生データ（全文検索・LLM入力用）。`convert_thesis.py` で
  PDFから再生成可能。人が直接編集するのは非推奨
- `dataset/research/records/<file_id>/` — キュレーション済みレコード。
  `summary.md` と `detail.md` の本文は人が書く。`detail_quality` の段階
  （`skeleton` → `generic` → `draft` → `reviewed`）で進捗を管理
- `dataset/members/records/<member_id>.md` — メンバーレコード。
  `degree_records` が研究レコードへのポインタ
- `data/*.json`, `dataset/quality.md` — 派生ファイル。常に再生成可能

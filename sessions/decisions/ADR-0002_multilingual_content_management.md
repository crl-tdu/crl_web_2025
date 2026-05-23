---
adr_number: "0002"
title: "多言語コンテンツ（日本語/英語）の管理規約"
status: "Draft"
decision_type: "architecture"
date_created: "2026-05-23"
date_modified: "2026-05-23"
review_date: "2026-11-23"
tags:
  - "status/draft"
  - "domain/dataset-schema"
  - "domain/i18n"
supersedes: null
superseded_by: null
---

# ADR-0002: 多言語コンテンツ（日本語/英語）の管理規約

## Context

ホームページの想定構成（研究室概要・研究紹介・活動報告・発表業績・Privacy Policy）について、海外からの問い合わせ、国際学会経由の流入、共同研究先（海外含む）への発信を考慮すると、英語コンテンツのカバレッジが必要になる。

ただし、現実的な運用としては以下の制約がある:
- 翻訳作業は段階的にしか進まない（一度に全件英訳は不可能）
- 「タイトル」「1 行説明」レベルの短いフィールドは英訳しやすいが、論文要旨レベルの長文は時間がかかる
- どこまで英訳が進んでいるかを `dataset/quality.md` で追跡したい

スキーマ設計の選択肢は以下:
- **A**: frontmatter にサフィックス（`title_ja` / `title_en`）で並置
- **B**: `lang/{ja,en}/` サブディレクトリで完全分離
- **C**: 全フィールド拡張子分離（`summary.md` / `summary.en.md`）

A は短いフィールド向きでレビュー時に対訳が見やすい。B/C は長文向きで翻訳着手単位が明確だがファイル数が増える。

## Decision

**ハイブリッド方式**を採用する: 短いフィールドは frontmatter サフィックス併用、長文本文は拡張子分離。

### 短いフィールド: frontmatter サフィックス（`_ja` / `_en`）

以下のフィールドは `dataset/research/records/<file_id>/index.md` および `summary.md` の frontmatter に併置する:

```yaml
title_ja: "心拍と体温の相関性を用いたストレス軽減デバイスの開発"
title_en: "Development of a Stress-Reduction Device Using Heart Rate and Body Temperature"
tagline_ja: "心拍と体温の関係から眠気を測るデバイス"
tagline_en: "A wearable that detects drowsiness from HR and skin temperature"
meta_description_ja: "..."     # SEO 用、120-155 字
meta_description_en: "..."
alt_ja: "..."                    # assets.md 内の画像 alt
alt_en: "..."
```

既存の `title` / `title_en` フィールドは `title_ja` にリネームする（マイグレーション必要）。

### 長文本文: 拡張子による別ファイル

長文の本文（research record では `summary.md` / `detail.md`、テーマ説明では `themes/records/<slug>.md` 等）は以下の規約で英訳ファイルを並置する:

```
dataset/research/records/<file_id>/
├── index.md          # マニフェスト（多言語フィールドはサフィックス）
├── summary.md        # 日本語 (canonical)
├── summary.en.md     # 英訳（あれば）
├── detail.md         # 日本語 (canonical)
├── detail.en.md      # 英訳（あれば）
└── assets.md         # 画像マニフェスト（alt は frontmatter サフィックス）
```

日本語版を canonical とし、英訳ファイルはオプショナル。`.en.md` が存在しない場合、英語サイト側ではフォールバックを表示する（日本語をそのまま出すか、「英訳準備中」を出すかは UI レイヤの判断）。

### 翻訳進捗の追跡

`make derive` の派生処理に「英訳カバレッジ集計」を追加し、`dataset/quality.md` の新セクションとして以下を出す:

- `title_en` が未記入のレコード一覧
- `summary.en.md` が存在しないレコード一覧
- `detail.en.md` が存在しないレコード一覧

これによりレビュー会で翻訳優先順位を議論できる。

### Frontmatter の中立フィールド

言語に依存しないフィールド（`research_id`, `member_id`, `student_id`, `year`, `degree_code`, `research_themes`, `keywords`, `display_consent`, `visibility` 等）はサフィックスを付けず単一の値を持つ。

`keywords` は研究内のテクニカル用語で、現状ほぼ日本語。SEO 用の検索意図ワードは別フィールド `keywords_seo` を新設し、こちらは多言語サフィックス併用（`keywords_seo_ja[]` / `keywords_seo_en[]`）。

## Alternatives Considered

| 案 | メリット | デメリット | 採否 |
|---|---|---|---|
| 全フィールド frontmatter サフィックス | ファイル数最少 | 長文を frontmatter に入れるのは YAML 的に苦しい | ✗ |
| 全フィールド拡張子分離 | 翻訳境界が極めて明確 | frontmatter の重複が多く、ペアの一貫性を人間が保証する必要 | ✗ |
| `lang/{ja,en}/` サブディレクトリ | 翻訳着手率の追跡が `lang/en/` の有無で一発 | レコードあたりファイル数が 3 倍化、git diff が分散 | ✗ |
| **短フィールド=サフィックス + 長文=拡張子分離（ハイブリッド）** | 短文は対訳レビュー容易、長文は翻訳着手境界明確 | 規約が 2 種類で覚える必要あり | ✓ |

## Consequences

### Positive
- 短いフィールドはレビュー時に日英対訳が同じ画面で見られる
- 長文の翻訳着手率を「ファイルの有無」で機械的に追跡可能
- 既存の build_derived.py YAML パーサが Unicode 対応している（検証済み）ため、新フィールド追加の追加実装は不要
- 英語サイト・日本語サイトの両方を同一データから派生可能

### Negative / Risk
- 既存全レコードの `title` フィールドを `title_ja` にリネームするマイグレーションが必要
- `summary.md` を `summary.ja.md` にリネームするかは議論の余地（現状は日本語が canonical なので拡張子なしのまま、英訳のみ `.en.md` 規約を採用）
- 規約が「短=サフィックス、長=拡張子」と 2 種類存在することによる学習コスト

### Implementation Notes
- マイグレーション順序: (1) 新規スキーマで `2025_M_g.otsuka` 試験適用 → (2) `build_derived.py` を新スキーマ対応 → (3) 残り 89 件を機械的に `title` → `title_ja` リネーム → (4) `tagline_ja` / `meta_description_ja` 等を順次手書き
- `make derive` 拡張で英訳カバレッジ集計を追加
- `make scaffold` 拡張で `title_ja` / `title_en` を必須引数化（英訳は空文字許容）

## Open Questions

- 日本語 canonical のファイル名を `.ja.md` で明示するか、無印のままにするか → 無印が短くて済むが、後から英語 canonical のテーマ（例: 英語論文の和訳）が出てきた場合に逆転する。当面無印で進め、必要に応じて再検討。
- テーマ説明（`themes/records/<slug>.md`）は短文のみなので frontmatter サフィックスで完結する想定だが、将来テーマごとに長文紹介を書きたくなる可能性あり → その時に再検討

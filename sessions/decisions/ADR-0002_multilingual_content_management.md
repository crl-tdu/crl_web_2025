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

> **責任分担とスコープ注記**: `keywords`（ADR-0001 で「自由語彙として維持」）は研究内容のテクニカル語彙（タグクラウド・フリーテキスト検索用）、`keywords_seo` は検索エンジン向けの検索意図フレーズ（人間が読む文章に近い）であり、用途が異なるため重複を許容する。ただし `keywords_seo` の**キーワード戦略**（どの語を選ぶか、どの派生 JSON に載せるか、`build_derived.py`/`build_web_views.py` のどちらが出力するか）は本 ADR のスコープ外とし、SEO 戦略 ADR（別途）で定義する。本 ADR では `keywords_seo` の**置き場所と多言語規約のみ**を決める（現状スクリプトは未参照＝未実装）。

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
- 既存の build_derived.py YAML パーサは Python 3 の文字列仕様により Unicode を扱うため、新フィールド追加に追加実装は不要（これは正式なテストスイートによる検証ではなく、Python 3 仕様と試験適用レコード `2025_M_g.otsuka/index.md` の派生成功による確認）
- 英語サイト・日本語サイトの両方を同一データから派生可能

### Negative / Risk
- 既存全レコードの `title` フィールドを `title_ja` にリネームするマイグレーションが必要
- `summary.md` を `summary.ja.md` にリネームするかは議論の余地（現状は日本語が canonical なので拡張子なしのまま、英訳のみ `.en.md` 規約を採用）
- 規約が「短=サフィックス、長=拡張子」と 2 種類存在することによる学習コスト

### Implementation Notes
- マイグレーション順序: (1) `2025_M_g.otsuka` 試験適用（`index.md` は `title_ja`/`title_en` 適用済み、ただし旧 `title` も併存。`summary.md` は **未移行**で旧 `title`/`title_en`/`display_tags` が残存）→ (2) `build_derived.py` を新スキーマ対応 → (3) 残り 89 件を機械的に `title` → `title_ja` リネーム → (4) `tagline_ja` / `meta_description_ja` 等を順次手書き
- **移行中間状態の挙動**: `build_derived.py` は `title_ja` を優先し未存在なら旧 `title` にフォールバックする（`r.get("title_ja") or r.get("title", "")`、`build_web_views.py:188` 実装済み）。これによりリネーム未完了レコードでもフィールド欠損は起きない。旧 `title` はリネーム完了後にレコードから削除する（`index.md` の `title`/`title_ja` 併存は過渡的状態）。
- **規約違反の検出（linter）**: 「短文=frontmatter サフィックス、長文=拡張子分離」の 2 規約を人間の記憶に委ねないため `make check` に linter を追加する: (a) 長文本文相当のキー（`summary`/`detail`）が frontmatter に出現したら警告、(b) `*.en.md` に対応する canonical（無印）が無ければ警告、(c) `_ja`/`_en` サフィックスのキーが対で存在するか確認（英訳の値は空文字許容だが、キーの対存在を要求）。
- **フィールドの型・制約（コメントではなく本 Notes を SSOT とする）**: `meta_description_ja` は 120–155 字、`meta_description_en` は 150–160 characters（英語 SERP 標準）。`keywords_seo_ja[]`/`keywords_seo_en[]` は各最大 10 要素・1 要素 40 字以内。`make check` で検証する。
- **`assets.md` のスキーマ所有権**: 画像 `alt_ja`/`alt_en` は `assets.md` の frontmatter サフィックスで持ち、その frontmatter スキーマ定義は本 ADR-0002 が所有する（ADR-0004 の派生 `card_image_alt_ja`/`card_image_alt_en` はこれを集計したもの）。
- `make derive` 拡張で英訳カバレッジ集計を追加
- `make scaffold` 拡張で `title_ja` / `title_en` を必須引数化（英訳は空文字許容）

## Open Questions

- **英訳未整備時のフォールバック方針（研究成果への公正なアクセス）**: `.en.md` 不在時に英語サイトで「日本語をそのまま出す」か「英訳準備中を出す」かは、海外研究者への公正なアクセスに関わる倫理的選択である。既定を **(a) `title_en`/`tagline_en` が存在すればそれを表示、(b) 長文本文が未英訳なら「英訳準備中」+ 日本語原文への明示リンク** とし、英語ユーザに「劣化した自動翻訳」ではなく「原文への明示的導線」を提供する。UI 実装時に確定。
- 日本語 canonical のファイル名を `.ja.md` で明示するか、無印のままにするか → 無印が短くて済むが、後から英語 canonical のコンテンツ（例: 英語論文の和訳）が出た場合に逆転する。**逆転の発生条件を「英語が原著で日本語が翻訳であるレコードが 1 件でも現れた時点」と定義し、その時点で `.ja.md`/`.en.md` 両明示の規約へ全面移行する**。それまでは無印で進める。
- テーマ説明（`themes/records/<slug>.md`）は短文のみなので frontmatter サフィックスで完結する想定だが、将来テーマごとに長文紹介を書きたくなる可能性あり → その時に再検討

---
adr_number: "0004"
title: "派生ファイル戦略 — 凍結スナップショットと新規派生の並走"
status: "Draft"
decision_type: "architecture"
date_created: "2026-05-23"
date_modified: "2026-05-23"
review_date: "2026-11-23"
tags:
  - "status/draft"
  - "domain/dataset-schema"
  - "domain/build-pipeline"
supersedes: null
superseded_by: null
---

# ADR-0004: 派生ファイル戦略 — 凍結スナップショットと新規派生の並走

## Context

`data/` 配下には現在 7 個の JSON ファイルが存在する:

| ファイル | 生成元 | 現状 |
|---|---|---|
| `data/thesis.json` | `build_derived.py` | アクティブな派生（毎回再生成） |
| `data/members.json` | `build_derived.py` | アクティブな派生（毎回再生成） |
| `data/project.json` | 不明（リポジトリに残っていない旧スクリプト） | **2025-06 凍結スナップショット** |
| `data/keywords.json` | 不明（同上） | **2025-06 凍結スナップショット** |
| `data/publish.json` | 不明（同上） | **2025-06 凍結スナップショット** |
| `data/portfolio_research.json` | 不明（同上） | **2026-03 凍結スナップショット** |
| `data/legacy_project_index.json` | 不明（同上） | **凍結スナップショット** |

凍結 JSON の生成スクリプトは README.md にあるように「`dataset/` を将来のホームページ生成の基準データとして扱う」方針で、リポジトリから除外されている。これらを現在の `make derive` で再生成しようとしても、生成元の処理ロジックが失われているため不可能。

ホームページ実装に向けて、カード型ポートフォリオ・ファセット検索・タイムライン表示等のビュー専用派生ファイルが追加で必要となる。これらを既存凍結 JSON とどう関係付けるかが論点。

## Decision

**並走戦略（二系統運用）** を採用する: 既存凍結 JSON は歴史的スナップショットとして手を加えず凍結維持。Web 用の派生ファイルは新規系統として `make derive` で生成する。

### 凍結維持するファイル（手を加えない）

以下は **歴史的スナップショット** として現状のまま維持する:

- `data/project.json`（2025-06 時点のスナップショット）
- `data/keywords.json`（2025-06 時点）
- `data/publish.json`（2025-06 時点）
- `data/portfolio_research.json`（2026-03 時点）
- `data/legacy_project_index.json`

これらは過去ビルドとの互換性のために残し、将来削除する場合は別 ADR で判断。

### `make derive` で再生成するファイル（アクティブ）

既存:
- `data/thesis.json`
- `data/members.json`
- `dataset/quality.md`

**新規追加**（Web 実装に向け）:
- `data/cards.json` — カード型ポートフォリオ用ビュー（軽量、card 画像 + tagline + degree + year + themes + member_name）
- `data/facets.json` — ファセット検索用集計（themes / keywords / years / degrees の度数、空ファセット除外）
- `data/timeline.json` — 活動報告タイムライン用（年×種別、`dataset/activities/` 配下から集計）
- `data/themes.json` — テーマ別ナビゲーション用（各 theme の表示名・説明・件数・代表画像）
- `data/sitemap_seed.json` — サイト生成器用、各 URL の lastmod / priority

これらは全て **dataset/ から再生される派生物** として扱い、CLAUDE.md の規約に従い手編集禁止。

### スキーマ責任分担

| ファイル | データソース | 用途 |
|---|---|---|
| `cards.json` | `research/records/*/index.md` の frontmatter | カード一覧 UI |
| `facets.json` | `research/records/*/index.md` の `research_themes`/`keywords`/`year`/`degree_code` 集計 | ファセット絞り込み |
| `timeline.json` | `activities/records/*.md`（ADR-別途で定義予定の新エンティティ）| 活動報告タイムライン |
| `themes.json` | `themes/records/*.md` + 各テーマに属する research 件数 | テーマナビゲーション |
| `sitemap_seed.json` | 全エンティティの `last_updated` フィールド | サイト生成器入力 |

### `cards.json` の最小スキーマ

カード UI で必須となる最小フィールドのみを含める（情報過多を避ける）:

```json
{
  "metadata": {
    "generated_at": "2026-05-23T17:30:00+09:00",
    "total_cards": 90,
    "schema_version": "1.0"
  },
  "cards": [
    {
      "file_id": "2019_B_h.emori",
      "tagline_ja": "心拍と体温の関係から眠気を測るデバイス",
      "tagline_en": "...",
      "member_name": "江森 弘樹",
      "year": 2019,
      "degree_code": "B",
      "research_themes": ["human-sensing", "wellness-engineering"],
      "card_image": "../proc/img/2019_B_h.emori/card_4x3.webp",
      "card_image_alt_ja": "脈波センサ装着の様子",
      "visibility": "public",
      "featured": false
    }
  ]
}
```

### `make derive` の Makefile 拡張

```makefile
derive:
	$(PY) $(SCRIPTS)/build_derived.py
	$(PY) $(SCRIPTS)/build_web_views.py    # 新規スクリプト

check:
	# 既存の check + 新規派生ファイルの整合性チェックを追加
```

新規スクリプト `scripts/build_web_views.py` を追加。`build_derived.py` の YAML パーサを再利用する（モジュールとして import）。

### `make check` の拡張

新規派生ファイル群も整合性チェック対象に含める:

```
$(PY) $(SCRIPTS)/build_web_views.py >/dev/null
diff -q $$tmp/cards.json data/cards.json && \
diff -q $$tmp/facets.json data/facets.json && \
...
```

## Alternatives Considered

| 案 | メリット | デメリット | 採否 |
|---|---|---|---|
| 既存凍結 JSON を全て `make derive` で置き換え | 一貫性最大、データソース単一化 | 生成ロジックが失われており、過去ビルドとの差分が読めない。再現責任が重い | ✗ |
| 段階移行（新規 cards.json から始め、後で旧 JSON を順次再生成切り替え） | 段階的に整合性向上 | 中間状態が長期化、どの JSON が canonical かが時期により変動 | ✗ |
| **並走（既存凍結維持 + 新規派生で並列追加）** | 履歴と現用を明確に分離、新規実装に集中可能 | `data/` 配下が混在するため、フォルダ整理が必要 | ✓ |

## Consequences

### Positive
- 過去ビルドとの差分が出ない（履歴保全）
- 新規派生ファイル群の設計に集中でき、旧スクリプトのリバースエンジニアリングが不要
- カード UI に必要な軽量データを `cards.json` として最適化できる（既存 `portfolio_research.json` は重い）
- 凍結スナップショットは「2025-06 時点で project.json をどう設計していたか」を学ぶ参考資料として残る

### Negative / Risk
- `data/` 配下に「アクティブ」と「凍結」のファイルが混在する見た目の悪さ
- 凍結ファイルを誤って手編集してしまうリスク（ファイル名から識別困難）
- 将来「凍結」と「アクティブ」の境界が曖昧化する可能性

### Mitigation
- `data/` 配下を以下のサブディレクトリに整理することを検討:
  ```
  data/
  ├── active/           # make derive で生成（手編集禁止）
  │   ├── thesis.json
  │   ├── members.json
  │   ├── cards.json
  │   ├── facets.json
  │   ├── timeline.json
  │   ├── themes.json
  │   └── sitemap_seed.json
  └── snapshots/        # 凍結スナップショット（編集禁止、参照のみ）
      ├── 2025-06_project.json
      ├── 2025-06_keywords.json
      ├── 2025-06_publish.json
      ├── 2026-03_portfolio_research.json
      └── legacy_project_index.json
  ```
  このフォルダ整理は別 ADR（実装時）に分離する。

### Implementation Notes
- `scripts/build_web_views.py` は `build_derived.py` の `parse_frontmatter` を import して再利用
- ADR-0003 で定義した `display_consent` の実効値計算は `build_web_views.py` 内で実装
- `visibility: "members_only"` / `"draft"` / `"embargoed"` のレコードは `cards.json` から除外
- `featured: true` のレコードは `cards.json` 内でフラグ保持、UI 側でヒーロー昇格

## Open Questions

- `data/` のサブディレクトリ整理（active / snapshots 分離）は今すぐ実施するか、別 ADR に分離して後でやるか → 別 ADR で段階実施
- 凍結 JSON は将来「歴史的価値が薄れた」と判断された時点で削除するか、永続保存するか → 5 年保管を目安に再判断
- `cards.json` の画像パス表記は相対パスか絶対 URL か → サイト生成器の規約次第、実装時に決める

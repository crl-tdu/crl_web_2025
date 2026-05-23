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

> **本 ADR の位置づけ（重要）**: 本 ADR は「これから実装する設計」ではなく、**既に試験実装された内容（schema 2.0-pilot）を事後文書化し、設計判断として確定する** ものである。`scripts/build_web_views.py` は既に存在し `make derive`/`make check` に統合済み、`data/cards.json`・`data/facets.json` は生成済み、`2025_M_g.otsuka/index.md` は本 ADR のスキーマを反映済みである。記述は現状の実態に合わせる。

## Context

`data/` 配下には現在 **9 個**の JSON ファイルが存在する:

| ファイル | 生成元 | 種別 |
|---|---|---|
| `data/thesis.json` | `build_derived.py` | アクティブ派生（既存・毎回再生成） |
| `data/members.json` | `build_derived.py` | アクティブ派生（既存・毎回再生成） |
| `data/cards.json` | `build_web_views.py` | **アクティブ派生（試験実装済み）** |
| `data/facets.json` | `build_web_views.py` | **アクティブ派生（試験実装済み）** |
| `data/project.json` | 旧スクリプト（消失） | 2025-06 凍結スナップショット |
| `data/keywords.json` | 旧スクリプト（消失） | 2025-06 凍結スナップショット |
| `data/publish.json` | 旧スクリプト（消失） | 2025-06 凍結スナップショット |
| `data/portfolio_research.json` | 旧スクリプト（消失） | 2026-03 凍結スナップショット |
| `data/legacy_project_index.json` | 旧スクリプト（消失） | 凍結スナップショット |

凍結 JSON の生成スクリプトはリポジトリから除外されており、現在の `make derive` では再生成不可能。一方ホームページ実装に向けて、カード型ポートフォリオ・ファセット検索・タイムライン表示等のビュー専用派生が必要となり、その一部（`cards.json`/`facets.json`）は既に試験生成済みである。これらを既存凍結 JSON とどう関係付けるかが論点。

## Decision

**並走戦略（二系統運用）** を採用する: 既存凍結 JSON は歴史的スナップショットとして手を加えず維持。Web 用の派生は新規系統として `make derive` で生成する。さらに、両系統の混在を見た目で識別できるよう **`data/` のサブディレクトリ分離を本 ADR の昇格と同時に実施する**（後述。先送りしない）。

### 凍結維持するファイル（手を加えない）

- `data/project.json`（2025-06）/ `data/keywords.json`（2025-06）/ `data/publish.json`（2025-06）/ `data/portfolio_research.json`（2026-03）/ `data/legacy_project_index.json`
- 過去ビルドとの互換性のため残し、削除は別 ADR で判断。

### `make derive` で再生成するファイル（アクティブ）

実装済み: `data/thesis.json` / `data/members.json` / `data/cards.json` / `data/facets.json` / `dataset/quality.md`

未実装（生成の前提エンティティが未作成）:
- `data/timeline.json` — `dataset/activities/records/*.md`（**未作成エンティティ**）から集計。activities エンティティの定義 ADR が前提。
- `data/themes.json` — `dataset/themes/records/*.md`（**未作成**、ADR-0001 で作成予定）+ 各テーマ件数。
- `data/sitemap_seed.json` — 全エンティティの `last_updated` から URL の lastmod/priority を生成。

これらは全て dataset/ からの派生物であり、CLAUDE.md の規約どおり手編集禁止。

### `visibility` 閉集合の SSOT 定義（本 ADR が所有）

`visibility` の有効値は以下の閉集合に固定する。これが唯一の正式定義であり、ADR-0003 はこれを参照する。`build_web_views.py:HIDDEN_VISIBILITY` の実装はこの定義に従う:

| 値 | 公開派生（cards/thesis 等）での扱い |
|---|---|
| `public` | 公開（既定） |
| `members_only` | **全公開派生から除外**（cards.json だけでなく thesis.json 等すべて）|
| `draft` | 全公開派生から除外 |
| `embargoed` | `embargo_until` 到達まで除外（後述の自動切替） |

### `embargo_until` の自動切替

`embargo_until`（ISO 8601 日付 / null）が設定され `visibility: "embargoed"` のレコードは、`make derive` 時点で `embargo_until <= today` なら自動的に `public` 相当として派生に含める（実装要件・現状未実装）。embargo 明けの手動操作忘れを防ぐため機械化する。

### `cards.json` のスキーマ（実装に合わせた確定スキーマ）

旧版は「最小フィールドのみ」を標榜していたが、実装（`build_web_views.py`）は以下 23 フィールドを出力する。**本 ADR は実装を正とし、これを確定スキーマとする**（「最小」表現は撤回）。情報過多を避ける最適化は将来のフィールド削減 ADR で別途検討する。

```
file_id, title_ja, title_en, tagline_ja, tagline_en, member_name, member_id,
year, degree_code, research_themes, keywords, summary, card_image,
card_image_alt_ja, card_image_alt_en, card_image_status, visibility, featured,
predecessor_file_id, successor_file_id, detail_quality, effective_consent,
schema_version
```

- `member_name` は ADR-0003 の実効同意マスクの対象（`show_full_name: false` ならマスク。実装ブロッカー）。
- `card_image` のパスは **`proc/img/<file_id>/...` 形式のリポジトリルート相対**に確定する（旧 Open Question を解消。サイト生成器側で絶対 URL へ解決）。
- `featured: true` の最大件数は UI のヒーロー段に合わせ **3 件**を上限とし、`make check` で超過を警告する。

### `facets.json` のスキーマ

`research_themes` / `keywords` / `year` / `degree_code` の度数集計。`keywords` は出現頻度**上位 50 件**まで（ロングテール除外）、空ファセットは除外。

### 実効同意計算の責務（ADR-0003 との一元化）

`effective_consent()` の計算と派生フィールドへのマスク適用は **`build_web_views.py` に一元化する**（ADR-0003 と整合）。`build_derived.py` が生成する `thesis.json` にも同マスクを効かせる必要があるため、`effective_consent()` および YAML パーサ（`parse_frontmatter`）は **`scripts/lib/` の共通モジュールに切り出し**、`build_derived.py` と `build_web_views.py` の双方が import する（下記 Mitigation）。二重実装・ロジック乖離を防ぐ。

### `make` ターゲット（実装済み）

```makefile
derive:
	$(PY) $(SCRIPTS)/build_derived.py
	$(PY) $(SCRIPTS)/build_web_views.py

check:
	# build_derived + build_web_views を一時生成し data/ との diff で drift 検出
```

## Alternatives Considered

| 案 | メリット | デメリット | 採否 |
|---|---|---|---|
| 既存凍結 JSON を全て `make derive` で置換 | 一貫性最大 | 生成ロジック消失、過去ビルドとの差分が読めない | ✗ |
| 段階移行（新規から始め旧 JSON を順次置換）| 段階的に整合性向上 | 中間状態が長期化、canonical が時期で変動 | ✗ |
| **並走（凍結維持 + 新規派生並列）+ サブディレクトリ即時分離** | 履歴と現用を明確分離、混在の見た目問題も同時解消 | 分離作業が発生 | ✓ |

## Consequences

### Positive
- 過去ビルドとの差分が出ない（履歴保全）
- 新規派生の設計に集中でき、旧スクリプトのリバースエンジニアリング不要
- `visibility` 閉集合の SSOT が本 ADR に集約され、ADR-0003 と実装の三者が一致
- 実効同意計算の一元化により ADR-0003 との責務矛盾が解消

### Negative / Risk
- `data/` 配下の active/snapshots 混在 → **本 ADR で分離を決定し解消**（下記 Mitigation）
- 未実装派生（timeline/themes/sitemap）は前提エンティティ（activities/themes）の作成待ち

### Mitigation（本 ADR で実施を決定）
- **`data/` サブディレクトリ分離**（昇格後の最初のステップとして実施。先送りしない）:
  ```
  data/
  ├── active/      # make derive 生成（手編集禁止）
  │   ├── thesis.json / members.json / cards.json / facets.json
  │   └── (将来) timeline.json / themes.json / sitemap_seed.json
  └── snapshots/   # 凍結（編集禁止・参照のみ）
      ├── 2025-06_project.json / 2025-06_keywords.json / 2025-06_publish.json
      ├── 2026-03_portfolio_research.json
      └── legacy_project_index.json
  ```
  移動に伴う参照（`prototype/` 等）の更新も同時に行う。
- **共通ライブラリ化**: `parse_frontmatter` / `effective_consent` を `scripts/lib/frontmatter.py`（仮）へ切り出し、`build_derived.py` と `build_web_views.py` が import。スクリプト間の直接 import（`sys.path` 依存）の脆さを解消し、stdlib-only 制約は維持。

## Implementation Notes
- `scripts/build_web_views.py` は実装済み。**未実装の要件**: (1) 実効同意のフィールドマスク適用（ADR-0003、最優先）、(2) `embargo_until` 自動切替、(3) `featured` 上限 3 件チェック、(4) `data/active`・`data/snapshots` 分離、(5) `scripts/lib/` への共通モジュール切り出し。
- `timeline.json` は `dataset/activities/` エンティティ ADR、`themes.json` は ADR-0001 の `dataset/themes/` 作成が前提。
- `make check` は新規派生（cards/facets）も diff 対象に含む（実装済み）。分離後はパス更新が必要。

## Open Questions
- 凍結 JSON の保管期間（5 年目安で再判断）。
- `sitemap_seed.json` の priority 算出規則 → サイト生成器の要件確定時に定義。

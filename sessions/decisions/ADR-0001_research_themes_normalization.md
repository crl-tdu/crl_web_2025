---
adr_number: "0001"
title: "research_themes の正規化と display_tags の廃止"
status: "Draft"
decision_type: "architecture"
date_created: "2026-05-23"
date_modified: "2026-05-23"
review_date: "2026-08-23"
tags:
  - "status/draft"
  - "domain/dataset-schema"
  - "domain/navigation"
supersedes: null
superseded_by: null
---

# ADR-0001: research_themes の正規化と display_tags の廃止

## Context

ホームページ実装に向け、研究紹介を「カード型ポートフォリオ」として提示する設計に進む。これに伴い、ナビゲーションの大カテゴリと、研究レコードのメタデータの整合性を取る必要が生じた。

既存スキーマでは `display_tags`（自由語彙、76 種類）と `keywords`（自由語彙、307 種類）の 2 つのタグ系統が存在しているが、90 件のレコードを集計した結果、以下が判明:

- `display_tags` の上位 4 つ（人間機械系 72 件 / 人間センシング 48 件 / 協調理論 32 件 / チームワーク 11 件）で記録の約 95% をカバーしている
- 上位 4 つの `display_tags` は `keywords` の上位 4 つと完全に重複しており、両フィールドが機能的に重複している
- 残り 72 種類の `display_tags` は出現頻度 1〜4 件の long tail で、ナビゲーション設計に使えない
- 「人間機械系」は 80% の研究に付与されており、L0（研究室全体の傘）として機能しているが、L1 ナビゲーションには細分化が必要

ナビゲーション・ファセット検索・SEO の各観点から、テーマは閉集合（少数・命名管理された）である必要がある。

## Decision

以下を決定する:

1. **`research_themes`** という新フィールドを `dataset/research/records/<file_id>/index.md` および `summary.md` の frontmatter に導入する。値は以下 6 種類の英語 kebab-case slug の閉集合とする。多重所属を許容（1 レコードが複数テーマに属してよい）。

   | slug | 日本語表示名 | 集計件数 |
   |---|---|---|
   | `human-sensing` | 人間センシング | 49 |
   | `cooperation-theory` | 協調理論 | 32 |
   | `skill-acquisition` | 熟達支援・運動学習 | 26 |
   | `haptic-interaction` | 力覚・触覚インタラクション | 23 |
   | `teamwork-and-swarm` | チームワーク・群知能 | 22 |
   | `wellness-engineering` | ウェルネス工学 | 3 |

2. **`display_tags`** フィールドは廃止する。既存レコードからは段階的に削除し、`research_themes` に置き換える。

3. テーマ表示名・説明文・代表画像は新規エンティティ `dataset/themes/records/<slug>.md` に格納する。frontmatter に `display_name_ja` / `display_name_en` / `description_ja` / `description_en` / `representative_image` を持つ。

4. 「人間機械系」（L0）は `dataset/about/lab.md` で研究室全体のキャッチコピーとして語り、`research_themes` の値には含めない。

5. `keywords` フィールドは自由語彙として維持する（フリーテキスト検索・タグクラウド用途）。`research_themes` とは独立した軸として扱う。

6. テーマ未分類の既存 8 件（うち 4 件は skeleton、4 件は手動分類対象）は移行作業時に個別判定する。

## Alternatives Considered

| 案 | メリット | デメリット | 採否 |
|---|---|---|---|
| 5 テーマに絞る（wellness 統合） | シンプル | 研究室の重点研究方向性 (Dr.Wellness 担当領域) が見えなくなる | ✗ |
| 10-15 テーマの中粒度 | ファセット検索が豊か | ナビゲーションのトップ階層には多すぎる | ✗ |
| display_tags を維持・併用 | 後方互換性最大 | 二系統運用で意味的境界が曖昧化、コード変更コストを後で払う | ✗ |
| 日本語 slug 使用 | 表記が直接的 | URL エンコード必要、英語サイト側で別マッピング必要 | ✗ |
| **英語 kebab-case slug + 日本語表示名を themes/ に持つ** | URL・コードに優しく多言語対応の素地、表示は柔軟 | テーマ実体ファイル管理が必要 | ✓ |

## Consequences

### Positive
- ナビゲーション設計が決定論的になる（6 個の閉集合）
- 英語サイト・SEO・URL 設計が同一データから派生可能
- 研究室の「重点研究方向性」をデータレベルで明示できる
- ファセット検索 UI の設計が単純化される

### Negative / Risk
- 既存 90 レコード全てに対する `research_themes` 付与の移行作業が発生（display_tags → themes のマッピング規則が必要）
- テーマ閉集合の変更（追加・削除・名称変更）は ADR 更新を伴う重い操作になる
- `wellness-engineering` は現状 3 件と少なく、ユーザから「存在意義が薄い」と見える可能性 → about/lab.md で研究室の方向性として明示することで補う

### Implementation Notes
- 移行は `2025_M_g.otsuka` を試験適用としてサンプル運用 → 残り 89 件は別 ADR で計画
- `scripts/scaffold_record.py` を更新し、新規レコード作成時に `research_themes` を必須引数化
- `scripts/build_derived.py` の派生処理に「テーマ集計」を追加し、`data/facets.json`（ADR-0004 で定義）に出力

## Open Questions

- テーマの並び順（カバー率順 / 研究室の重点順 / アルファベット順）はどれが UI 上望ましいか → ナビゲーション実装時に再検討
- `wellness-engineering` の件数が今後 1 年で増えなかった場合、再評価して `human-sensing` に統合する閾値を決めるべきか → 次回 review 時の論点

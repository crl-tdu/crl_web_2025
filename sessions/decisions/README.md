# Decisions

プロジェクトの設計判断記録（Architecture Decision Records）。
研究手法・ソフトウェア設計の意思決定とその根拠を追跡します。

## ステータス凡例

| ステータス | 説明 |
|-----------|------|
| Draft | AI が下書き作成。レビュー待ち |
| Proposed | 人間がレビュー済み。承認待ち |
| Accepted | 承認・適用中 |
| Superseded | 後継 ADR により置換 |
| Deprecated | 無効化 |

## 目次

| ADR | タイトル | ステータス | 種別 | Review Date |
|-----|---------|-----------|------|-------------|
| [ADR-0001](./ADR-0001_research_themes_normalization.md) | research_themes の正規化と display_tags の廃止 | Draft | architecture | 2026-08-23 |
| [ADR-0002](./ADR-0002_multilingual_content_management.md) | 多言語コンテンツ（日本語/英語）の管理規約 | Draft | architecture | 2026-11-23 |
| [ADR-0003](./ADR-0003_student_consent_two_layer_model.md) | 学生公開同意フラグの二層モデル（member ベース + research 上書き） | Draft | architecture | 2026-11-23 |
| [ADR-0004](./ADR-0004_derived_artifacts_dual_track_strategy.md) | 派生ファイル戦略 — 凍結スナップショットと新規派生の並走 | Draft | architecture | 2026-11-23 |

## 依存関係

- ADR-0001 (themes) → ADR-0004 (派生戦略): facets.json / themes.json のテーマ集計に依存
- ADR-0002 (多言語) → ADR-0004 (派生戦略): 英訳カバレッジ集計に依存
- ADR-0003 (公開同意) → ADR-0004 (派生戦略): 実効公開同意計算で `cards.json` の出力対象を決定

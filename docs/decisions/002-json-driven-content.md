# ADR-002: JSON-Driven Dynamic Content

**Date**: 2026-03-08
**Status**: accepted

## Context

研究室Webサイトのコンテンツ管理方式の選定。CMSの導入、静的HTML、JSON駆動の3案を検討した。

## Decision

`data/*.json` ファイルでコンテンツを管理し、フロントエンドのJavaScriptで動的にレンダリングする。`data/project.json` は `proc/` パイプラインから自動生成する。

## Consequences

### Positive
- CMS不要でインフラが簡素
- JSONファイルはGit管理可能
- フロントエンドとデータの明確な分離
- データパイプラインによる自動生成で手動ミスを防止

### Negative
- SEOに不利（JSレンダリング必須）
- `project.json` は手動編集禁止の制約が必要

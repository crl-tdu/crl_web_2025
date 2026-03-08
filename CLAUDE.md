# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

CRL（Cooperative Robotics Laboratory）研究室Webサイト。卒論・修論プロジェクト、論文、メンバー、活動を紹介するSPA。Vanilla JavaScript + Vite構成、UDC（ユニバーサルデザインカラー）準拠。

## Architecture

### JSON-Driven Dynamic Content

すべてのコンテンツは `data/` 配下のJSONから動的にロードされる。

```
index.html → src/js/main.js → 各モジュールが対応JSONをfetch → DOM描画

data/project.json  ←→ portfolio.js  → #portfolioGrid
data/members.json  ←→ members.js    → #membersGrid
data/publish.json  ←→ publications.js → #publicationList
data/activity.json ←→ activities.js  → #activityList
```

### Data Pipeline

```
proc/txt_refined/*.md → scripts/generate-project-data.js → data/project.json
                                                          → data/project.json は自動生成。手動編集禁止。
```

詳細: [docs/architecture.md](docs/architecture.md)

### Directory Structure

```
src/js/          # フロントエンドモジュール（ES6, async/await）
data/            # フロントエンド用JSON（自動生成あり）
proc/            # データ処理パイプライン（Python, PyMuPDF4LLM）
project/         # 卒論・修論のソースMarkdown・画像
scripts/         # データ同期スクリプト（Node.js）
assets/css/      # スタイルシート（UDC準拠）
docs/            # 設計判断、運用手順
```

## Commands

```bash
# Development
npm run dev                    # 開発サーバ起動（localhost:5173）
npm install                    # 依存インストール

# Build
npm run build                  # 本番ビルド（→ dist/）

# Data sync
npm run generate:projects      # project.json 再生成
npm run generate:html          # プロジェクトHTML生成
npm run generate:all           # 上記両方（prebuildで自動実行）
```

## Rules

- `data/project.json` は自動生成ファイル。手動編集禁止。`npm run generate:projects` で再生成する
- UIテキストはすべて日本語。コメントは日英可
- ファイルID命名: `YYYY_X_author`（例: `2024_B_h.tanaka`、X=B:学士/M:修士）
- ES6 modules、async/await、event delegation パターンを使用
- ARIA属性を必ず付与（`aria-pressed`, `aria-expanded` 等）
- 画像: 500KB以下、PNG、アスペクト比 16:9 or 4:3
- UDCカラー準拠（高コントラスト、色覚多様性対応）
- 現在のタスク状態は `CURRENT_TASK.md` を参照

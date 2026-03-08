# CLAUDE.md — scripts/

## What this module does

データ同期スクリプト群（Node.js）。`proc/` の精製Markdownから `data/` のJSONとHTMLを生成する。

## Critical invariants

- `generate-project-data.js` の出力は `data/project.json`
- `generate-project-html.js` の出力はプロジェクト個別HTML
- `npm run build` の `prebuild` で `generate:all` が自動実行される

## Before changing this code

- [ ] 出力JSONの構造変更は `src/js/` の対応モジュールも要更新
- [ ] 変更後 `npm run generate:all && npm run dev` で動作確認

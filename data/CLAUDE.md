# CLAUDE.md — data/

## What this module does

フロントエンドが読み込むJSONデータファイル群。

## Critical invariants

- `project.json` は `scripts/generate-project-data.js` による**自動生成ファイル**

## Before changing this code

- [ ] `project.json` を直接編集していないか確認。ソースは `proc/txt_refined/*.md`
- [ ] 変更後 `npm run dev` でフロントエンド表示を確認

## Do NOT

- `project.json` を手動編集しない。`npm run generate:projects` で再生成する
- JSON構造（キー名・ネスト構造）を変更する場合、対応する `src/js/` のモジュールも更新する

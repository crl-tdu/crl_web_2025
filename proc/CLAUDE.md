# CLAUDE.md — proc/

## What this module does

PDF論文からMarkdownと画像を抽出するデータ処理パイプライン（Python, PyMuPDF4LLM）。

## Critical invariants

- `txt_refined/` が `data/project.json` の上流ソース
- 画像は `img_all/` に抽出される（990枚以上）

## Before changing this code

- [ ] Pythonの仮想環境が有効か確認
- [ ] 変更後 `npm run generate:all` でデータ再生成
- [ ] `data/project.json` の内容が正しいことを確認

## Do NOT

- `txt_refined/` のファイルを削除しない（復元にはPDF再処理が必要）
- 抽出済み画像のファイル名規則 `YYYY_X_author_*.png` を変更しない

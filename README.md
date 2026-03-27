# crl_web_2025 Dataset

このリポジトリは、研究室ホームページ用のコードではなく、研究データだけを保持するデータセットです。

## 残しているもの

- `dataset/`
  - 今後のサイト生成に使う正規化済み Markdown データ
- `data/`
  - 正規化済み JSON データ
- `project/abst/`, `project/detail/`, `project/detail_legacy/`, `project/publish.md`
  - 研究概要、研究詳細、業績の Markdown ソース
- `proc/txt/`, `proc/img/`, `proc/img_all/`
  - 抽出済み本文、サムネイル、代表画像、ページ画像
- `pdfs/`
  - 元 PDF / 処理済み PDF

## データ設計

- 研究レコードの主キーは学生名ではなく `file_id` です。
- 学士から修士へ進学した同一人物は、1人のメンバーに対して複数の研究レコードを持ちます。
- 博士論文も扱える構造ですが、現行データには博士レコードは含まれていません。

## 方針

- このリポジトリには HTML/CSS/JavaScript、生成スクリプト、作業用 prompt、一時ファイルは残していません。
- `dataset/` を将来のホームページ生成の基準データとして扱います。

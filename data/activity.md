# 活動報告データ管理

このファイルは `index2.html` の活動報告セクションに表示されるデータの管理ガイドです。実際の表示データは下記の構成で管理しています。

- `data/activity.json` : 構造化されたメタデータ（タイトル、日付、タグ、ノートへのパスなど）
- `activity/notes/*.md` : 各活動の本文（YAML Front Matter 付き Markdown）
- `activity/img/*.svg` : サムネイル画像（1200×675, 16:9）

## 追加・更新手順

1. `activity/notes/` に `<slug>.md` を追加し、以下の Front Matter を記述します。
   ```yaml
   ---
   title: "タイトル"
   date: YYYY-MM-DD
   original_url: https://...
   location: 開催場所
   tags:
     - conference
     - ...
   summary: "カードに表示する短い要約"
   ---
   
   本文をここに記載します。
   ```
2. `activity/img/` に 1200×675 の画像を配置します（`<slug>.svg` または `.png` など）。
3. `data/activity.json` に新しいエントリを追加します（`note_path` と `image_path` で上記ファイルを参照）。
4. ブラウザで `index2.html` を開き表示を確認します。モーダルの本文は `activity/notes/*.md` が自動で読み込まれます。

## 既存データ一覧

| ID | 日付 | タイトル | タグ |
| --- | --- | --- | --- |
| jsme-annual-2025 | 2025-09-17 | 日本機械学会 2025年度年次大会 に参加 | conference / jsme / presentations |
| robomech-2025-yamagata | 2025-08-02 | ロボティクス・メカトロニクス講演会 2025 in Yamagata | conference / jsme / robomech |
| iip-2025 | 2025-04-17 | 情報・知能・精密機器部門講演会（IIP2025） | conference / iip / jsme |
| samcon-2025 | 2025-04-17 | SAMCON2025 | conference / samcon |
| sice-si-2024 | 2025-02-01 | SICE SI2024 | conference / sice / system-integration |
| vr-psychology-2024 | 2024-11-20 | VR心理学研究委員会 | workshop / virtual-reality |
| ceatec-2024 | 2024-10-11 | CEATEC2024 | exhibition / ceatec / public-outreach |
| vr-conference-2024 | 2024-09-17 | 第29回日本バーチャルリアリティ学会 | conference / virtual-reality |
| ies2024 | 2024-09-17 | 電気学会 電子・情報・システム部門大会 | conference / iee-japan |
| robomech-2024-utsunomiya | 2024-06-04 | ロボティクス・メカトロニクス講演会2024 in Utsunomiya | conference / jsme / robomech |

## 備考

- `activity/img/*.svg` は現状のプレースホルダーです。実写を利用する場合は同じファイル名で差し替えてください。
- 外部記事へのリンクは `source_url` に保持し、モーダル内の「公式記事を見る」ボタンから参照できます。
- JSON の `presentation_count` フィールドは任意ですが、集計等に利用しやすくするため保持しています。

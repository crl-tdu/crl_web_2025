# BASELINE.md - 卒業論文・修士論文プロジェクト画像自動抽出システム

## 🎯 プロジェクト概要

五十嵐研究室の卒業論文・修士論文（2019-2024年度）から研究プロジェクト紹介用の代表画像を自動抽出・整理するシステム。Chain-of-Thought (CoT) アプローチによる段階的処理と継続可能な設計を採用。

## 📋 基本前提条件

### 実行環境
- **OS**: macOS (Kawasaki, Kanagawa, JP)
- **Python管理**: conda環境（miniforge3）
- **メインPython**: `/Users/igarashi/miniforge3/bin/python3` (Python 3.9)
- **conda base環境**: PyMuPDF 1.26.0 利用可能
- **実行ユーザー**: 五十嵐教授 ("五十嵐"と呼称)

### 技術スタック
- **PDF処理**: PyMuPDF (fitz) 1.26.0
- **プログラミング言語**: Python 3.9, bash
- **数式多用**: 理論説明での数式活用推奨
- **開発アプローチ**: Chain-of-Thought (CoT) でステップバイステップ

### conda環境アクティベーション方法
```bash
source /Users/igarashi/miniforge3/etc/profile.d/conda.sh
conda activate base
python [script.py]
```

## 📁 現在のディレクトリ構造

```
/Users/igarashi/local/crl_web_2025/
├── CURRENT_TASK.md                  # 📋 現在の作業状況管理ファイル
├── BASELINE.md                      # 📋 本ファイル（前提条件・状況）
├── prompt/
│   └── image_extract_process.md     # システム設計仕様書
├── tmp/                             # 一時作業・ログファイル
│   ├── logs/                        # 実行ログ
│   ├── results/                     # 処理結果JSON
│   └── *.py                         # 実行スクリプト
├── proc/                            # 📊 処理済みデータ
│   ├── img_all/                     # 🎯 **990枚** 純粋画像のみ（メイン）
│   ├── img_images_only/             # 990枚 埋め込み画像（バックアップ）
│   ├── img_all_BACKUP_20250611_*/   # 3,802枚 完全バックアップ（安全保存）
│   ├── img/                         # 🎯 **最終出力先** 代表画像
│   ├── txt/                         # PDFテキスト抽出結果
│   └── data/                        # その他データ
└── pdfs/                            # 📚 元PDFファイル
    ├── pdf_B_2019/ ... pdf_B_2024/  # 学士論文（年度別）
    └── pdf_M_2019/ ... pdf_M_2024/  # 修士論文（年度別）
```

## 🔄 作業状況管理

### CURRENT_TASK.mdの重要性
- **必須参照**: 作業開始時に必ず `CURRENT_TASK.md` を参照
- **継続的更新**: 作業進捗に応じて適宜更新
- **状況共有**: 他のAIセッションとの状況同期に活用

### 現在の作業フェーズ
```bash
cat /Users/igarashi/local/crl_web_2025/CURRENT_TASK.md
```
で最新状況を確認可能。

## 📊 現在のデータ状況（2025年6月11日時点）

### 処理完了項目
1. **PDF画像抽出**: 91件のPDFから3,802枚のページ画像抽出済み
2. **埋め込み画像抽出**: 990枚の純粋な画像・図表・グラフを抽出済み
3. **img_all再構築**: 文章ページを除去し、純粋画像990枚で再構築完了

### データ統計
```
対象期間: 2019-2024年度（6年間）
対象論文: 91件（学士論文 + 修士論文）
純粋画像: 990枚（proc/img_all/）
最終目標: 各論文の代表画像選定（proc/img/）
```

### 年度別画像統計
| 年度 | 学士論文 | 修士論文 | 合計 |
|------|----------|----------|------|
| 2024 | 150枚 | 125枚 | 275枚 |
| 2022 | 132枚 | 54枚 | 186枚 |
| 2020 | 58枚 | 110枚 | 168枚 |
| 2021 | 88枚 | 39枚 | 127枚 |
| 2023 | 71枚 | 49枚 | 120枚 |
| 2019 | 80枚 | 34枚 | 114枚 |

## 🔧 技術仕様

### ファイル命名規則
**現在の形式**: `YYYY_X_author-PPP_NN.png`
- `YYYY`: 年度（2019-2024）
- `X`: 学位種別（B=学士, M=修士）
- `author`: 著者名
- `PPP`: 元ページ番号（000-999）
- `NN`: 画像番号（01-99、同一ページ内複数画像対応）

**例**: `2024_B_mi.nakamura-035_01.png`

### 画像品質基準
- **解像度**: DPI 200以上
- **形式**: PNG（非圧縮）
- **最小サイズ**: 150x150ピクセル
- **内容**: 埋め込み画像のみ（テキストページ除外済み）

## 🎯 次の目標

### 代表画像選定フェーズ【実行中】
現在の990枚から各論文の代表画像を以下のカテゴリで選定：

1. **サムネイル画像**: 論文を代表する1枚
2. **概要画像**: 研究手法・システム概要を示す画像
3. **結果画像**: 実験結果・成果を示す画像

### Phase別実行計画
- **Phase 1**: 画像内容分析システム【実行中】
- **Phase 2**: AI画像分類器【待機中】  
- **Phase 3**: 代表性評価アルゴリズム【待機中】
- **Phase 4**: 統合・品質保証システム【待機中】

### 最終出力先
```
proc/img/
├── YYYY_X_author_thumbnail.png     # サムネイル
├── YYYY_X_author_overview.png      # 概要
└── YYYY_X_author_result.png        # 結果
```

## 🔄 AIへの指示

### 作業開始時の必須手順
1. **CURRENT_TASK.md確認**: 現在の作業状況を必ず確認
   ```bash
   cat /Users/igarashi/local/crl_web_2025/CURRENT_TASK.md
   ```

2. **ディレクトリ状況確認**: 最新のファイル数・状況を把握
   ```bash
   cd /Users/igarashi/local/crl_web_2025
   find proc/img_all -name "*.png" | wc -l
   ```

3. **conda環境活用**: Python実行時は必ずconda base環境を使用
   ```bash
   source /Users/igarashi/miniforge3/etc/profile.d/conda.sh && conda activate base
   ```

### 開発方針
- **Chain-of-Thought**: 段階的思考プロセスで問題解決
- **数式活用**: 五十嵐教授の専門性に合わせた理論的説明
- **継続性重視**: 処理中断・再開に対応した堅牢な設計
- **品質保証**: バックアップ・検証を含む安全な処理

### コミュニケーション
- **呼称**: 五十嵐先生、五十嵐教授
- **専門分野**: 人工知能、ヒューマンインタフェース、ロボティクス、認知科学、生体信号処理
- **プログラミング**: C++, Python精通

## 📄 関連ファイル

- `CURRENT_TASK.md`: 現在の作業状況（必須参照）
- `prompt/image_extract_process.md`: システム設計詳細
- `tmp/img_all_rebuild_final_report.json`: 最新処理結果
- `tmp/embedded_images_report.json`: 埋め込み画像抽出結果

---
**作成日**: 2025年6月11日  
**バージョン**: 1.0  
**作成者**: Claude (Anthropic)  
**指導**: 五十嵐教授  
**プロジェクト**: 卒業論文・修士論文プロジェクト画像自動抽出システム

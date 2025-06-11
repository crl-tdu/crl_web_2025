# 卒業論文・修士論文からプロジェクト画像自動抽出システム（継続可能版）

## システム概要
卒業論文・修士論文PDFから研究プロジェクト紹介用の代表画像を **Chain-of-Thought (CoT)** アプローチにより段階的に自動抽出・整理する継続可能なシステムです。

## 🔄 継続性設計
- **作業状況管理**: `CURRENT_TASK.md`で進捗追跡
- **チェックポイント**: 各段階で処理状況保存
- **再開機能**: 途中停止からの安全な再開
- **既存リソース活用**: 処理済みデータの効率的再利用

## 📁 ディレクトリ構造
```
/Users/igarashi/local/crl_web_2025/
├── prompt/
│   └── image_extract_process.md      # このファイル
├── CURRENT_TASK.md                   # 作業進捗管理
├── tmp/                              # 一時作業ファイル
├── proc/
│   ├── img_all/                      # 全抽出画像（既存）
│   ├── img/                          # 代表画像（出力先）
│   └── txt/                          # PDFテキスト（既存）
└── pdfs/                             # 元PDFファイル
```

## 🎯 作業フェーズ

### Phase 1: 環境確認・準備
```bash
#!/bin/bash
# tmp/phase1_setup.sh

set -e
BASE_DIR="/Users/igarashi/local/crl_web_2025"
cd "$BASE_DIR"

echo "🔍 Phase 1: 環境確認・準備"

# 現在の状況確認
check_current_status() {
    echo "📊 現在の状況:"
    
    # 既存画像数確認
    img_all_count=$(find proc/img_all -name "*.png" 2>/dev/null | wc -l | tr -d ' ')
    img_output_count=$(find proc/img -name "*.png" 2>/dev/null | wc -l | tr -d ' ')
    txt_count=$(find proc/txt -name "*.txt" 2>/dev/null | wc -l | tr -d ' ')
    
    echo "  全抽出画像: ${img_all_count}枚"
    echo "  代表画像: ${img_output_count}枚"
    echo "  テキストファイル: ${txt_count}件"
    
    # 年度別確認
    echo "📅 年度別状況:"
    for year in 2019 2020 2021 2022 2023 2024; do
        year_img_all=$(find proc/img_all -name "${year}_*.png" 2>/dev/null | wc -l | tr -d ' ')
        year_img_out=$(find proc/img -name "${year}_*.png" 2>/dev/null | wc -l | tr -d ' ')
        echo "  ${year}年度: 抽出${year_img_all}枚 → 代表${year_img_out}枚"
    done
}

# 依存ツール確認
check_dependencies() {
    echo "🔧 依存ツール確認:"
    local missing_tools=()
    
    command -v python3 >/dev/null || missing_tools+=("python3")
    command -v convert >/dev/null || missing_tools+=("imagemagick")
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        echo "❌ 不足ツール: ${missing_tools[*]}"
        echo "💡 インストール: brew install ${missing_tools[*]}"
        exit 1
    else
        echo "✅ 依存ツール確認完了"
    fi
}

# Python環境確認
check_python_environment() {
    echo "🐍 Python環境確認:"
    python3 -c "
import sys
try:
    import cv2
    import numpy as np
    from pathlib import Path
    print('✅ 必要なライブラリ確認完了')
except ImportError as e:
    print(f'❌ ライブラリ不足: {e}')
    sys.exit(1)
"
}

# 作業ディレクトリ準備
setup_workspace() {
    echo "📁 作業ディレクトリ準備:"
    mkdir -p tmp/logs tmp/results
    
    # チェックポイントファイル初期化
    cat > tmp/checkpoint.json << EOF
{
    "phase": 1,
    "last_update": "$(date -Iseconds)",
    "status": "setup_complete",
    "processed_years": [],
    "remaining_years": [2019, 2020, 2021, 2022, 2023, 2024]
}
EOF
    echo "✅ 作業環境準備完了"
}

# 実行
check_current_status
check_dependencies  
check_python_environment
setup_workspace

echo "✅ Phase 1 完了: 環境準備完了"
```

### Phase 2: 画像品質フィルタリング
```python
#!/usr/bin/env python3
# tmp/phase2_quality_filter.py

import cv2
import numpy as np
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class QualityFilterSystem:
    """既存画像品質フィルタリングシステム"""
    
    def __init__(self, base_dir: str = "/Users/igarashi/local/crl_web_2025"):
        self.base_dir = Path(base_dir)
        self.checkpoint_file = self.base_dir / "tmp" / "checkpoint.json"
        self.log_file = self.base_dir / "tmp" / "logs" / "quality_filter.log"
        
        # 品質閾値設定
        self.quality_thresholds = {
            'min_width': 200,
            'min_height': 150, 
            'min_area': 30000,
            'max_whiteness': 0.85,
            'min_complexity': 0.1,
            'text_ratio_threshold': 0.7,
            'min_edge_density': 0.02
        }
    
    def load_checkpoint(self) -> Dict:
        """チェックポイント読み込み"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        return {"phase": 2, "processed_images": [], "deleted_images": []}
    
    def save_checkpoint(self, data: Dict):
        """チェックポイント保存"""
        data["last_update"] = datetime.now().isoformat()
        with open(self.checkpoint_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def log_message(self, message: str):
        """ログ出力"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_file, 'a') as f:
            f.write(log_entry + "\n")
    
    def evaluate_image_quality(self, image_path: Path) -> Dict:
        """
        Chain-of-Thought画像品質評価
        
        数学的品質モデル:
        Q(I) = w1·Q_size(I) + w2·Q_color(I) + w3·Q_complexity(I) + w4·Q_text(I)
        """
        try:
            img = cv2.imread(str(image_path))
            if img is None:
                return {'is_valid': False, 'reason': 'imread_failed'}
            
            height, width = img.shape[:2]
            
            # Step 1: 基本次元評価
            size_score = self._evaluate_size_quality(width, height)
            
            # Step 2: 色彩品質評価  
            color_score = self._evaluate_color_quality(img)
            
            # Step 3: 構造複雑性評価
            complexity_score = self._evaluate_complexity(img)
            
            # Step 4: テキスト密度評価
            text_score = self._evaluate_text_density(img)
            
            # 統合品質スコア計算
            weights = [0.3, 0.3, 0.25, 0.15]  # [size, color, complexity, text]
            scores = [size_score['score'], color_score['score'], 
                     complexity_score['score'], text_score['score']]
            
            overall_score = sum(w * s for w, s in zip(weights, scores))
            
            # 除外条件チェック
            exclusions = []
            if not size_score['valid']:
                exclusions.append("size_invalid")
            if not color_score['valid']:
                exclusions.append("color_invalid") 
            if not complexity_score['valid']:
                exclusions.append("complexity_low")
            if not text_score['valid']:
                exclusions.append("text_heavy")
            
            is_valid = len(exclusions) == 0 and overall_score >= 0.6
            
            return {
                'is_valid': is_valid,
                'overall_score': overall_score,
                'exclusions': exclusions,
                'details': {
                    'size': size_score,
                    'color': color_score,
                    'complexity': complexity_score,
                    'text': text_score
                }
            }
            
        except Exception as e:
            return {'is_valid': False, 'reason': f'evaluation_error: {e}'}
    
    def _evaluate_size_quality(self, width: int, height: int) -> Dict:
        """サイズ品質評価"""
        area = width * height
        aspect_ratio = width / height
        
        size_valid = (
            width >= self.quality_thresholds['min_width'] and
            height >= self.quality_thresholds['min_height'] and
            area >= self.quality_thresholds['min_area']
        )
        
        aspect_valid = 0.2 <= aspect_ratio <= 5.0
        
        # スコア計算 (0-1)
        size_score = min(area / 100000, 1.0) if area > 0 else 0
        aspect_score = 1.0 if aspect_valid else 0.2
        
        return {
            'valid': size_valid and aspect_valid,
            'score': (size_score + aspect_score) / 2,
            'width': width,
            'height': height,
            'area': area,
            'aspect_ratio': aspect_ratio
        }
    
    def _evaluate_color_quality(self, img: np.ndarray) -> Dict:
        """色彩品質評価"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 白色占有率
        white_pixels = np.sum(gray > 240)
        total_pixels = gray.size
        whiteness_ratio = white_pixels / total_pixels
        
        # 色分散
        color_variance = np.var(gray)
        
        # HSV彩度
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        saturation_mean = np.mean(hsv[:, :, 1])
        
        # 評価
        whiteness_valid = whiteness_ratio <= self.quality_thresholds['max_whiteness']
        variance_valid = color_variance > 100  # 十分な色分散
        saturation_valid = saturation_mean > 20  # 十分な彩度
        
        # スコア計算
        whiteness_score = max(0, 1 - whiteness_ratio * 2)
        variance_score = min(color_variance / 1000, 1.0)
        saturation_score = min(saturation_mean / 100, 1.0)
        
        overall_score = (whiteness_score + variance_score + saturation_score) / 3
        
        return {
            'valid': whiteness_valid and (variance_valid or saturation_valid),
            'score': overall_score,
            'whiteness_ratio': whiteness_ratio,
            'color_variance': color_variance,
            'saturation_mean': saturation_mean
        }
    
    def _evaluate_complexity(self, img: np.ndarray) -> Dict:
        """構造複雑性評価"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # エッジ密度
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # ラプラシアン分散（焦点明瞭度）
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # 構造複雑性評価
        complexity_valid = edge_density >= self.quality_thresholds['min_edge_density']
        focus_valid = laplacian_var > 100
        
        # スコア計算
        edge_score = min(edge_density * 10, 1.0)
        focus_score = min(laplacian_var / 1000, 1.0)
        
        return {
            'valid': complexity_valid and focus_valid,
            'score': (edge_score + focus_score) / 2,
            'edge_density': edge_density,
            'laplacian_variance': laplacian_var
        }
    
    def _evaluate_text_density(self, img: np.ndarray) -> Dict:
        """テキスト密度評価"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # MSER文字領域検出
        mser = cv2.MSER_create()
        regions, _ = mser.detectRegions(gray)
        
        # テキスト領域推定
        text_area = sum(len(region) for region in regions if len(region) > 10)
        total_area = gray.shape[0] * gray.shape[1]
        text_ratio = text_area / total_area if total_area > 0 else 0
        
        # 評価
        text_valid = text_ratio <= self.quality_thresholds['text_ratio_threshold']
        
        # スコア計算（テキストが少ないほど高スコア）
        text_score = max(0, 1 - text_ratio * 2)
        
        return {
            'valid': text_valid,
            'score': text_score,
            'text_ratio': text_ratio,
            'text_regions': len(regions)
        }
    
    def filter_images_by_year(self, year: int) -> Dict:
        """年度別画像フィルタリング"""
        self.log_message(f"🎯 {year}年度画像品質フィルタリング開始")
        
        year_pattern = f"{year}_*.png"
        image_files = list(self.base_dir.glob(f"proc/img_all/{year_pattern}"))
        
        results = {
            'year': year,
            'total_images': len(image_files),
            'valid_images': [],
            'deleted_images': [],
            'quality_stats': {}
        }
        
        for img_file in image_files:
            quality = self.evaluate_image_quality(img_file)
            
            if quality['is_valid']:
                results['valid_images'].append(str(img_file))
                self.log_message(f"  ✅ 有効: {img_file.name} (スコア: {quality['overall_score']:.2f})")
            else:
                # 低品質画像を削除
                try:
                    os.remove(img_file)
                    results['deleted_images'].append(str(img_file))
                    self.log_message(f"  ❌ 削除: {img_file.name} (理由: {quality.get('exclusions', ['unknown'])})")
                except Exception as e:
                    self.log_message(f"  ⚠️  削除失敗: {img_file.name} - {e}")
        
        self.log_message(f"✅ {year}年度完了: {len(results['valid_images'])}枚有効, {len(results['deleted_images'])}枚削除")
        return results
    
    def run_quality_filtering(self):
        """品質フィルタリングメイン実行"""
        self.log_message("🚀 Phase 2: 画像品質フィルタリング開始")
        
        checkpoint = self.load_checkpoint()
        checkpoint["phase"] = 2
        
        all_results = []
        years = [2019, 2020, 2021, 2022, 2023, 2024]
        
        for year in years:
            year_results = self.filter_images_by_year(year)
            all_results.append(year_results)
            
            # チェックポイント更新
            checkpoint["processed_years"] = checkpoint.get("processed_years", [])
            if year not in checkpoint["processed_years"]:
                checkpoint["processed_years"].append(year)
            self.save_checkpoint(checkpoint)
        
        # 最終統計
        total_valid = sum(len(r['valid_images']) for r in all_results)
        total_deleted = sum(len(r['deleted_images']) for r in all_results)
        
        self.log_message(f"🎉 Phase 2 完了: 全体で{total_valid}枚有効, {total_deleted}枚削除")
        
        # 結果保存
        results_file = self.base_dir / "tmp" / "results" / "quality_filter_results.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)
        with open(results_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        return all_results

if __name__ == "__main__":
    filter_system = QualityFilterSystem()
    results = filter_system.run_quality_filtering()
```

## 🔄 継続性機能

### 作業再開方法
```bash
# 作業状況確認
cat CURRENT_TASK.md

# チェックポイント確認  
cat tmp/checkpoint.json

# 特定フェーズから再開
python3 tmp/phase2_quality_filter.py  # Phase 2から
python3 tmp/phase3_ai_classifier.py   # Phase 3から
bash tmp/phase4_integration.sh        # Phase 4から

# 完全パイプライン実行
bash tmp/phase4_integration.sh
```

### チェックポイント仕様
```json
{
    "phase": 3,
    "last_update": "2025-06-11T15:30:00+09:00",
    "status": "ai_classification_in_progress",
    "processed_years": [2019, 2020, 2021],
    "remaining_years": [2022, 2023, 2024],
    "current_year": 2022,
    "processed_pdfs": ["2022_B_i.kato", "2022_B_k.ohya"],
    "errors": [],
    "statistics": {
        "total_processed": 25,
        "thumbnails_created": 20,
        "overviews_created": 18,
        "results_created": 22
    }
}
```

### エラー回復機能
```python
# tmp/recovery_utils.py

def resume_from_checkpoint():
    """チェックポイントから作業再開"""
    with open('tmp/checkpoint.json', 'r') as f:
        checkpoint = json.load(f)
    
    phase = checkpoint.get('phase', 1)
    
    if phase == 2:
        # 品質フィルタリング再開
        remaining_years = checkpoint.get('remaining_years', [])
        filter_system = QualityFilterSystem()
        for year in remaining_years:
            filter_system.filter_images_by_year(year)
    
    elif phase == 3:
        # AI分類再開
        current_year = checkpoint.get('current_year')
        processed_pdfs = checkpoint.get('processed_pdfs', [])
        classifier = AdvancedImageClassifier()
        classifier.resume_year_processing(current_year, processed_pdfs)
```

## 📊 品質保証機能

### 自動検証スクリプト
```bash
#!/bin/bash
# tmp/quality_assurance.sh

# 出力画像検証
validate_output_images() {
    echo "🔍 出力画像検証"
    
    # 必須ファイル確認
    missing_files=()
    for year in 2019 2020 2021 2022 2023 2024; do
        for type in B M; do
            pattern="proc/img/${year}_${type}_*"
            if ! ls $pattern >/dev/null 2>&1; then
                missing_files+=("${year}_${type}")
            fi
        done
    done
    
    if [ ${#missing_files[@]} -eq 0 ]; then
        echo "✅ 全年度・全種別の画像確認完了"
    else
        echo "⚠️  不足画像: ${missing_files[*]}"
    fi
}

# ファイルサイズ検証
validate_file_sizes() {
    echo "📏 ファイルサイズ検証"
    
    # 異常に小さいファイル検出
    small_files=$(find proc/img -name "*.png" -size -5k)
    if [ -n "$small_files" ]; then
        echo "⚠️  小サイズファイル検出:"
        echo "$small_files"
    else
        echo "✅ ファイルサイズ正常"
    fi
}

validate_output_images
validate_file_sizes
```

## 🎯 実行手順

### 初回実行
```bash
# 1. プロンプトファイル確認
cat prompt/image_extract_process.md

# 2. 現在の状況確認  
cat CURRENT_TASK.md

# 3. 完全パイプライン実行
bash tmp/phase4_integration.sh

# 4. 結果確認
cat tmp/results/final_report.md
```

### 途中再開
```bash
# 1. チェックポイント確認
cat tmp/checkpoint.json

# 2. 該当フェーズから再開
python3 tmp/phase{N}_{script}.py

# 3. 作業状況更新
# CURRENT_TASK.md を手動更新
```

### トラブルシューティング
```bash
# ログ確認
tail -f tmp/logs/quality_filter.log
tail -f tmp/logs/ai_classifier.log

# エラー詳細確認
cat tmp/checkpoint.json | jq '.errors'

# 手動修復
python3 tmp/recovery_utils.py
```

## 📈 性能最適化

### メモリ効率化
- **バッチ処理**: 年度別分割処理
- **画像サイズ制限**: 大容量画像の事前リサイズ
- **キャッシュ管理**: テキストデータの適切な解放

### 処理速度向上
- **並列処理**: CPU集約タスクのマルチプロセス化
- **早期終了**: 明らかな低品質画像の即座スキップ
- **インデックス活用**: ファイル検索の最適化

### エラー耐性
- **例外ハンドリング**: 個別ファイルエラーでも処理継続
- **ロールバック機能**: 失敗時の状態復旧
- **冗長性確保**: 重要データの複数箇所保存

## 🔮 将来拡張

### 新機能追加
- **Deep Learning分類**: CNN による画像分類精度向上
- **自動キャプション生成**: OCR + NLP による図表説明自動生成
- **Webインターフェース**: ブラウザベース管理画面

### データ形式拡張
- **動画対応**: MP4 からの静止画抽出
- **3Dモデル**: STL/OBJ ファイルからのレンダリング画像生成
- **インタラクティブ図**: SVG/HTML5 Canvas 形式出力

## 📚 参考資料

### 技術仕様
- **画像処理**: OpenCV 4.x
- **数値計算**: NumPy 1.21+
- **ファイル操作**: pathlib + subprocess
- **データ形式**: JSON (チェックポイント), Markdown (レポート)

### 数学的基盤
- **品質評価関数**: $Q(I) = \sum_{i} w_i \cdot Q_i(I)$
- **信頼度計算**: $C = \frac{\sum_{j} s_j \cdot w_j}{\sum_{j} w_j}$
- **分類決定**: $\text{class} = \arg\max_c P(c|I,T)$

### アルゴリズム詳細
- **エッジ検出**: Canny法 + Hough変換
- **特徴抽出**: Harris角点 + MSER領域
- **分類手法**: ルールベース + 重み付きスコアリング

---

**最終更新**: 2025年6月11日
**バージョン**: 継続可能版 v1.0
**作成者**: 五十嵐研究室

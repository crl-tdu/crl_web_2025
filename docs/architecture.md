# Architecture Overview

## システム全体図

```mermaid
graph TD
    subgraph "Data Pipeline (proc/)"
        PDF[PDF論文] -->|PyMuPDF4LLM| MD[Markdown抽出]
        MD -->|txt_refined/| REFINED[精製Markdown]
    end

    subgraph "Data Sync (scripts/)"
        REFINED -->|generate-project-data.js| PJ_JSON[data/project.json]
        REFINED -->|generate-project-html.js| PJ_HTML[プロジェクトHTML]
    end

    subgraph "Frontend Data (data/)"
        PJ_JSON
        MEM_JSON[data/members.json]
        PUB_JSON[data/publish.json]
        ACT_JSON[data/activity.json]
        KW_JSON[data/keywords.json]
    end

    subgraph "Frontend SPA (src/js/)"
        MAIN[main.js] --> PORT[portfolio.js]
        MAIN --> MEMB[members.js]
        MAIN --> PUBL[publications.js]
        MAIN --> ACTV[activities.js]
        MAIN --> NAV[nav.js]
    end

    PJ_JSON --> PORT
    MEM_JSON --> MEMB
    PUB_JSON --> PUBL
    ACT_JSON --> ACTV

    subgraph "Rendering"
        PORT --> |"#portfolioGrid"| HTML[index.html]
        MEMB --> |"#membersGrid"| HTML
        PUBL --> |"#publicationList"| HTML
        ACTV --> |"#activityList"| HTML
    end
```

## データフロー

1. **Upstream**: PDF論文 → PyMuPDF4LLMでMarkdown抽出 → `proc/txt_refined/` に保存
2. **Sync**: `scripts/generate-project-data.js` が精製Markdownを読み込み → `data/project.json` を生成
3. **Frontend**: 各JSモジュールが対応JSONをfetch → DOMに描画
4. **Build**: `npm run build` 時に `prebuild` フックで `generate:all` が自動実行

## フィルタリングパターン

全セクション共通のフィルタリング設計:

- **Tag filter buttons**: `data-tag` / `data-*-category` 属性
- **Search input**: `#projectSearch`, `#memberSearch`, `#publicationSearch`
- **Active state**: `aria-pressed="true"`
- **Expand/Collapse**: "残りを表示" ボタン + `data-*-toggle`

## 技術スタック

| レイヤー | 技術 |
|---------|------|
| ビルド | Vite 7.x |
| フロントエンド | Vanilla JavaScript (ES6 modules) |
| Markdown処理 | marked 17.x |
| スタイル | CSS (SCSS → CSS) |
| データ処理 | Python (PyMuPDF4LLM), Node.js |
| アクセシビリティ | WCAG AA, UDC準拠 |

## デザインシステム

- **UDC (Universal Design Color)** 準拠
- レスポンシブ: Mobile (<768px) / Tablet (768-1024px) / Desktop (>1024px)
- CSS Grid + Flexbox（`.grid--columns-3` で3カラム）
- コンポーネント: `.card`, `.filter-chip`, `.btn-primary`, `.section`

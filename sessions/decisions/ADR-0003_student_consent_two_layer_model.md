---
adr_number: "0003"
title: "学生公開同意フラグの二層モデル（member ベース + research 上書き）"
status: "Draft"
decision_type: "architecture"
date_created: "2026-05-23"
date_modified: "2026-05-23"
review_date: "2026-11-23"
tags:
  - "status/draft"
  - "domain/dataset-schema"
  - "domain/privacy"
  - "domain/legal"
supersedes: null
superseded_by: null
---

# ADR-0003: 学生公開同意フラグの二層モデル（member ベース + research 上書き）

## Context

ホームページに学生（卒業生含む）の氏名・顔写真・論文本文を掲載することは、本人同意の元に行う必要がある。卒業生数が累積していくなか、以下の現実的なリスクが存在する:

- **取り下げ要求**: 卒業生から「自分の名前/顔写真/論文を消してほしい」と将来連絡がくる可能性
- **同意粒度の差**: 同じ学生でも「学士は公開してよいが、修士は企業共同研究で非公開」のようなケース
- **取り下げ追跡の難しさ**: 現状スキーマには公開同意フラグが存在せず、誰がどの研究の何について同意しているかが追跡不能

外部公開（PR・広報）の観点からも、この点は法的リスクの累積として最優先で着手すべき項目と位置づける（※ 本記述の根拠は本 ADR 執筆時の検討であり、特定の外部レビュー記録を参照したものではない。誤って「ペルソナレビューで指摘済み」とする旧記述を撤回し訂正した）。

### 用語定義（本 ADR で固定する）

本 ADR が扱う重要概念は、技術設計の前に意味を固定する必要がある:

- **同意（consent）**: 本人が「何を・どの範囲に・いつまで公開してよいか」を理解した上で与えた許諾。本 ADR は同意の*記録と適用*を扱うが、インフォームド・コンセントの三要件（情報提供・理解・自発性）の充足は紙の同意書取得プロセス側の責任とする。
- **公開（publish）**: 不特定多数がアクセス可能な状態に置くこと。「メンバー限定閲覧」（`visibility: members_only`、ADR-0004）とは区別する。
- **安全側（fail-safe default）**: 同意が不明・未確認の場合に、**学生個人の情報的自己決定を優先する方向**（＝より非公開寄り）を既定値とすること。「研究室の記録・広報の利益」ではなく「学生の利益」を基準とする、と本 ADR で明示的に定義する（下記デフォルト値の非対称はこの定義に照らして正当化する）。

スキーマ設計の選択肢:
- **A**: `member` レコード側のみで管理（人物単位）
- **B**: `research` レコード側のみで管理（研究単位）
- **C**: 両方持つ（member にデフォルト + research で上書き可能）

A はシンプルだが研究単位の制御不能。B は柔軟だが取り下げ時に複数レコード更新が必要。C は最も柔軟だが解決ロジックが複雑。

## Decision

**二層モデル（C）** を採用する: `member` レコードに既定値を持ち、`research` レコードで個別上書きを許容する。

### `member` レコード側: 既定値

`dataset/members/records/<member_id>.md` の frontmatter に以下を追加する。

> **重要（パーサ制約）**: 値の後ろにインラインコメント（`true  # …`）を**付けないこと**。本リポジトリの自作 YAML パーサ（`build_derived.py:_parse_scalar`）は `#` を除去せず、`show_full_name: true  # 氏名` を文字列 `'true  # 氏名'` として読み、ブール判定を破綻させる（CLAUDE.md「YAML frontmatter dialect」節参照）。各フィールドの意味は下表で定義し、YAML 自体にはコメントを書かない。

```yaml
display_consent_default:
  show_full_name: true
  show_face_photo: false
  show_thesis_body: false
  display_name_preference: "full"
  consent_date: "2026-05-23"
  consent_revocation_years: 5
contact_consent_default:
  contact_after_graduation: false
```

| フィールド | 型 / 有効値 | 既定 | 意味 |
|---|---|---|---|
| `show_full_name` | bool | `true` | 氏名（フルネーム）表示の可否 |
| `show_face_photo` | bool | `false` | 顔写真表示の可否 |
| `show_thesis_body` | bool | `false` | 論文本文（`detail.md`）公開の可否 |
| `display_name_preference` | `full` \| `initials` \| `nickname` | `full` | 氏名の表示形式 |
| `consent_date` | ISO 8601 日付文字列 | — | 紙の同意書を取得した日 |
| `consent_revocation_years` | int（年数） | `5` | 再確認サイクル（後述の根拠あり）|
| `contact_after_graduation` | bool | `false` | 卒業後の研究室からの連絡可否（display とは独立ドメイン）|

### デフォルト値の価値判断（非対称性の根拠）

`show_face_photo: false` だが `show_full_name: true` という非対称は、無自覚な設定ではなく以下の明示的な価値判断による（研究室主宰者の決定）:

- **氏名フルネーム = 既定公開（`true`）**: 学術研究の帰属（attribution）は研究者本人に紐づくべきで、氏名表示が研究業績の本人への正当な帰属に資する。研究室の記録・広報上も既定公開を妥当とする。
- **論文本文 = 既定非公開（`false`）**: 本文は研究内容・思想・能力の詳細な記録であり、企業共同研究・特許・未発表データを含みうる。**安全側（学生の利益優先）の定義に従い既定を `false`** とし、明示同意があれば `true` に上書きする。
- **顔写真 = 既定非公開（`false`）**: 生体情報であり個人特定リスクが高く、明示同意なしの掲載は安全側に反する。

この三者は「氏名は帰属の便益が大きく既定公開、本文・顔写真は個人リスクが大きく既定非公開」という一貫した基準で決定している。

### `research` レコード側: 上書き

`dataset/research/records/<file_id>/index.md` の frontmatter で、特定研究のみ既定値を上書きする場合に記述する（同じくインラインコメント禁止）:

```yaml
display_consent_override:
  show_thesis_body: false
  reason: "企業共同研究のため本文非公開（タイトル・概要のみ）"
```

`display_consent_override` が `null`/省略の場合は、`member.display_consent_default` がそのまま適用される。

### 解決ロジック（決定論的）

`build_web_views.py:effective_consent()`（実装済み）で、各 research レコードの「実効公開同意」をフィールド単位で計算する:

```
effective_consent[field] = research.display_consent_override[field]
                            if exists
                          else member.display_consent_default[field]
```

`data/cards.json` / `data/thesis.json` には実効値を `effective_consent` として書き出す。

### 実効同意の派生ファイルへの強制適用（プライバシー漏洩防止）

実効同意は「計算して書き出す」だけでは不十分で、**派生ファイルの各フィールドにマスクとして適用**しなければならない。現行実装にはこのマスクが欠落している（`build_web_views.py:192` は `member_name` を無条件出力）。実装時に以下を必須要件とする:

| 実効同意 | 全派生ファイル（cards.json / thesis.json 等）での扱い |
|---|---|
| `show_full_name: false` | `member_name` を `display_name_preference` に従いマスク（`initials` → "S.I."、空 → `""`）。生氏名を一切出力しない |
| `show_face_photo: false` | `card_image` 等の顔写真パスを出力しない |
| `show_thesis_body: false` | `detail.md` 由来フィールド・本文リンクを出力しない（`summary` までは可）|
| `visibility ∈ {members_only, draft, embargoed}`（ADR-0004）| レコード自体を全公開派生から除外（`thesis.json` も含む。`cards.json` だけの除外では不十分）|

評価優先順位: **`visibility` を先に評価**（除外なら以降不問）→ 残ったレコードに `effective_consent` のフィールドマスクを適用。`effective_consent` と `visibility` の SSOT 定義は ADR-0004 が所有する。

### 視覚的差分の優先順位（UI レイヤ）

| 設定 | UI 上の挙動 |
|---|---|
| `show_face_photo: false` | プレースホルダーアイコン |
| `display_name_preference: "initials"` | "S.I." 形式 |
| `display_name_preference: "nickname"` | member レコードの `nickname` フィールド値を表示（未設定なら `initials` にフォールバック）|
| `show_thesis_body: false` | 概要（`summary.md`）まで表示、`detail` リンク非表示 |
| `visibility: "members_only"` | レコード自体を一覧から除外 |

### 同意取得・取り下げの運用

- **新規入学時**: `make scaffold` で member レコード作成と同時に紙ベースの同意書を取得し、`consent_date` を記録
- **卒業時**: 卒業前に再確認し、必要なら override 設定
- **再確認サイクル（`consent_revocation_years: 5`）の根拠**: 学位記録の長期保存と本人状況の変化（就職・改姓・方針変更）のバランスから 5 年を採用する。これは法的義務に基づく値ではなく研究室の運用ポリシーであり、個人情報保護法・関連ガイドラインの改定で変更を要する可能性がある。値変更時は全 member レコードの一括書き換えスクリプトで対応する（散在ハードコードを避ける）。`make derive` で `consent_date + consent_revocation_years 年 < today` のレコードを `dataset/quality.md` に「再確認推奨」として集計する（`consent_revocation_years` は整数型なので日付演算可能）。
- **5 年再確認が無応答だった場合**: 「沈黙＝継続同意」とは見なさず、**実効同意を安全側（`show_*: false`）に倒し、`visibility: members_only` へ落とす**。再度の明示同意で復帰させる。
- **取り下げ申請**: `member.display_consent_default`（必要なら `research.display_consent_override`）を更新。**取り下げ申請受領から実際の公開停止完了までの目標を「派生再生成 + サイト再デプロイで 3 営業日以内、検索エンジン等の外部キャッシュからの消失も能動的に依頼」とする**（下記キャッシュ伝播の注記参照）。
- **同意の証跡**: `consent_date` は単独では証跡たり得ない。紙の同意書のスキャン PDF を研究室内の所定保管場所に保存し、ファイル名に `<member_id>_<consent_date>` を含めて `consent_date` と対応付ける運用 SOP を別途整備する（本 ADR はフィールド定義まで、SOP は運用文書側）。

## Alternatives Considered

| 案 | メリット | デメリット | 採否 |
|---|---|---|---|
| member 側のみ | シンプル、取り下げ時の更新が 1 箇所 | 研究ごとに公開可否が異なるケースに対応不能 | ✗ |
| research 側のみ | 研究単位で完全に柔軟 | 取り下げ時に全研究を一括更新、default の置き場が無い | ✗ |
| **二層（member default + research override）** | 既定値で大半をカバー、例外のみ override | 解決ロジックの実装が必要 | ✓ |
| 同意フラグなし（現状維持） | 実装ゼロ | 法的リスク累積、取り下げ時に追跡不能 | ✗ |

## Consequences

### Positive
- 取り下げ申請に対し `member` の 1 レコード更新 + `make derive` 再実行で全研究に反映可能（既定の安全側挙動）
- 例外的なケース（企業共同研究等）に研究単位で対応可能
- `consent_date` + `consent_revocation_years` の追跡により再確認運用が機械化可能
- UI レイヤは派生済みの実効値・マスク済みフィールドのみを参照すればよい

### Negative / Risk
- 71 名の既存メンバー全員に対し、同意の遡及確認が現実的に必要（卒業生への連絡コスト）
- **キャッシュ伝播の限界**: フラグ更新は派生ファイルにしか効かない。検索エンジンのインデックス・CDN・ブラウザキャッシュに残った氏名/顔写真は派生更新後も一定期間残存しうる。取り下げの実効性は技術設計だけでは完結せず、外部キャッシュへの削除依頼を含む運用が必要（上記目標を運用 SOP に明記）。
- **ネスト 2 段の機械的強制**: `display_consent_default` / `contact_consent_default` はネスト 2 段。パーサはネスト 3 段以上を解釈できないため、`make check` に「frontmatter のネスト深度が 2 を超えたら exit 1」のチェックを追加し、「設計規律」に依存しない（人間の記憶に委ねない）。
- **member_name 露出リスク（実装欠落）**: 現行 `build_web_views.py` は `show_full_name: false` でも `member_name` を出力する。上記マスク要件の実装が完了するまで、`show_full_name: false` の同意設定は実効性を持たない。

## Implementation Notes
- 試験適用は `2025_M_g.otsuka`（在学中、同意取得済み想定）。現状 `index.md` は `display_consent_override: null`、member レコード側の `display_consent_default` は**未実装**（要追加）。
- `build_web_views.py` に **実効同意のフィールドマスク**（上表）を実装する（最優先・実装ブロッカー）。`effective_consent()` の計算は実装済みだが適用が欠落している。
- サンプル YAML は**インラインコメント禁止**。`make check` にコメント混入検出（`: true #` 等のパターン）を追加。
- `consent_revocation_policy: "5y"`（文字列）は廃し `consent_revocation_years: 5`（整数）に確定。
- `make check` にネスト深度 2 超過チェックを追加。
- 既存メンバーへの遡及同意取得は別タスク（運用 SOP として整備、ADR 化はしない）。

## Open Questions
- ~~同意取得できなかった卒業生の既定値~~ → **決定済み（下記 Decision に格上げ）**: 連絡不能・死亡を含め同意確認できない過去の卒業生のデータは **`dataset/` に保持しつつ、実効同意を全フィールド `false`・`visibility: members_only` として一切公開しない**。データ削除はせず研究記録として保全するが、公開はしない。これは「先送り＝現状維持（公開し続ける）」を避けるための能動的決定である。
- 死亡卒業生の同意主権（遺族・研究機関・本人生前同意の永続性）の法的扱いは、上記「保持・非公開」を当面の安全側措置としつつ、法的助言を得て別途方針化する。
- `consent_witnesses`（証人記録）の要否は法的助言の上で判断（現時点は未実装）。

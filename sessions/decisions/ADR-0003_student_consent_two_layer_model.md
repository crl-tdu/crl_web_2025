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

PR・広報担当ペルソナのレビューでも、この点は法的リスクの累積として最優先で着手すべきと指摘されている。

スキーマ設計の選択肢:
- **A**: `member` レコード側のみで管理（人物単位）
- **B**: `research` レコード側のみで管理（研究単位）
- **C**: 両方持つ（member にデフォルト + research で上書き可能）

A はシンプルだが研究単位の制御不能。B は柔軟だが取り下げ時に複数レコード更新が必要。C は最も柔軟だが解決ロジックが複雑。

## Decision

**二層モデル（C）** を採用する: `member` レコードに既定値を持ち、`research` レコードで個別上書きを許容する。

### `member` レコード側: 既定値

`dataset/members/records/<member_id>.md` の frontmatter に以下を追加:

```yaml
display_consent_default:
  show_full_name: true              # 氏名（フルネーム）表示の可否
  show_face_photo: false            # 顔写真表示の可否（既定は安全側に false）
  show_thesis_body: true            # 論文本文（detail.md）公開の可否
  display_name_preference: "full"   # full | initials | nickname
  consent_date: "2026-05-23"        # 同意取得日
  consent_revocation_policy: "5y"   # 5年ごとに再確認するポリシー
  contact_consent: false            # 卒業後の連絡可否（オプショナル）
```

### `research` レコード側: 上書き

`dataset/research/records/<file_id>/index.md` の frontmatter で、特定研究のみ既定値を上書きする場合に記述:

```yaml
display_consent_override:
  show_thesis_body: false           # この研究の論文本文だけ非公開
  reason: "企業共同研究のため本文非公開（タイトル・概要のみ）"
```

`display_consent_override` が省略された場合は、`member.display_consent_default` がそのまま適用される。

### 解決ロジック（決定論的）

`make derive` での派生処理で、各 research レコードの「実効公開同意」を計算する:

```
effective_consent[field] = research.display_consent_override[field]
                            if exists
                          else member.display_consent_default[field]
```

`data/cards.json` / `data/thesis.json` には実効値のみを書き出す（override の有無は派生ファイルには出さない）。

### 視覚的差分の優先順位

UI レイヤでは以下の優先順で表現を切り替える:

| 設定 | UI 上の挙動 |
|---|---|
| `show_face_photo: false` | プレースホルダーアイコン（イニシャル） |
| `show_full_name: false` + `display_name_preference: "initials"` | "S.I." 形式 |
| `show_thesis_body: false` | 概要（summary.md）まで表示し、detail へのリンクは非表示 |
| `visibility: "members_only"`（ADR-0004 で定義） | レコード自体を一覧から除外 |

### 同意取得の運用

- 新規入学時: `make scaffold` で member レコード作成と同時に紙ベースの同意書を取得し、`consent_date` を記録
- 卒業時: 卒業前に再度確認し、必要なら override 設定
- 5 年後: `make derive` の派生処理で `consent_date + 5y < today` のレコードを `dataset/quality.md` に「再確認推奨」として出す
- 取り下げ申請: `member.display_consent_default` を更新し、必要なら `research.display_consent_override` を追加

## Alternatives Considered

| 案 | メリット | デメリット | 採否 |
|---|---|---|---|
| member 側のみ | シンプル、取り下げ時の更新が 1 箇所で済む | 同じ学生で研究ごとに公開可否が異なるケースに対応不能 | ✗ |
| research 側のみ | 研究単位で完全に柔軟 | 取り下げ申請時に当該人物の全研究を一括更新する手間。default 設定する場所が無い | ✗ |
| **二層（member default + research override）** | 既定値で大半をカバー、例外のみ override で柔軟性確保 | 解決ロジックの実装が必要 | ✓ |
| 同意フラグなし（現状維持） | 実装ゼロ | 法的リスク累積、取り下げ時に追跡不能 | ✗ |

## Consequences

### Positive
- 取り下げ申請に対し、`member` の 1 レコード更新で全研究に反映可能（既定の安全側挙動）
- 例外的なケース（企業共同研究等）に研究単位で対応可能
- `consent_date` の追跡により「5 年ごとの再確認」運用が機械化可能
- UI レイヤが実効値のみを参照すれば良く、複雑なロジックを持たなくて済む

### Negative / Risk
- 71 名の既存メンバー全員に対し、同意の遡及確認が現実的に必要（卒業生への連絡コスト）
- 同意取得できなかった卒業生の扱い（既定で安全側 `false` にする vs データ削除）は別途判断が必要
- ネスト 2 段の frontmatter は `build_derived.py` の現行パーサで動作する（検証済み）が、ネスト 3 段以上に発展させない設計規律が必要

### Implementation Notes
- 試験適用は `2025_M_g.otsuka`（在学中、同意取得済み想定）で実施
- `build_derived.py` に「実効公開同意計算」関数を追加し、`thesis.json` に展開
- `make derive` の派生処理で `consent_date + 5y < today` を `quality.md` に集計
- 既存メンバーへの遡及同意取得は、別タスク（ADR 化はしない、運用 SOP として整備）
- 顔写真は既定 `false` にしているが、これは「安全側既定」であり、明示同意があれば `true` に上書きする運用

## Open Questions

- 同意取得できなかった卒業生（連絡不能）の既定値を「`false` で残す」か「データ削除する」かはポリシー判断（プライバシーポリシー文書側で決める）
- `consent_witnesses`（同意の証人記録）は将来必要になる可能性があるが、現時点では未実装。法的助言を仰いだ上で要否判断
- 「公開」と「閲覧可（メンバー限定）」を分ける必要があるか → ADR-0004 の `visibility` フィールドと組み合わせて表現する想定

---
record_type: "research_detail"
research_id: "2020_M_b.poitrimol"
title: "Grasping Interface for Virtual Reality Using Wire-Driven Positioning Interface"
title_en: ""
member_id: "b.poitrimol"
member_name: "Poitrimol Bastien"
student_id: "19KMH06"
year: 2020
degree_type: "修士論文"
degree_code: "M"
keywords:
  - "仮想空間"
  - "ワイヤ駆動"
  - "ハプティクス"
  - "グラスピング"
  - "人間機械系"
  - "人間センシング"
display_tags:
  - "人間機械系"
  - "人間センシング"
  - "仮想空間"
detail_quality: "custom"
thumbnail_path: "proc/img/2020_M_b.poitrimol_thumbnail.png"
symbolic_image_paths:
  - "proc/img_all/2020_M_b.poitrimol_page10_img0.png"
source_paths:
  abstract_markdown: "project/abst/2020_M_b.poitrimol_abst.md"
  detail_markdown: "project/detail/2020_M_b.poitrimol_detail.md"
  preferred_detail_markdown: "project/detail_legacy/2020_M_b.poitrimol_detail.md"
  legacy_detail_markdown: "project/detail_legacy/2020_M_b.poitrimol_detail.md"
  fulltext_markdown: "proc/txt/2020_M_b.poitrimol.md"
  pdf: "pdfs/2020_M_b.poitrimol.pdf"
---

# Grasping Interface for Virtual Reality Using Wire-Driven Positioning Interface

**研究者**: Poitrimol Bastien (修士, 2020)  
**キーワード**: バーチャルリアリティ, 力覚インタフェース, ワイヤ駆動, 把持インタフェース, ハプティクス, ケーブル駆動並列ロボット, VRインタラクション, マルチモーダルインタフェース

---

## 研究背景・動機

バーチャルリアリティ（VR）技術の急速な発展に伴い、視覚・聴覚だけでなく触覚フィードバックを統合したマルチモーダルインタフェースの需要が高まっている。従来のVRシステムは主に視覚情報に依存しており、物体との物理的インタラクションにおけるリアリティが不足している。特に、バーチャル環境での把持動作や力の感覚は、産業設計、医療訓練、教育分野において重要な要素である。既存の力覚インタフェースは、可動範囲の制約、コスト、複雑性、安全性の課題を抱えており、実用的なVRシステムへの統合が困難であった。ワイヤ駆動メカニズムは軽量性、安全性、拡張性の利点を持つが、VR環境での把持インタフェースとしての応用は限定的であった。ユーザーが直感的に操作でき、高い没入感を提供する次世代VRインタフェースの開発が急務となっている。

## 研究目的・課題設定

本研究は、ワイヤ駆動機構を用いた革新的なVR把持インタフェースの開発を目的とする。従来の剛体リンク機構に比べて軽量で安全なワイヤ駆動システムを活用し、VR環境での自然な把持動作と力覚フィードバックを実現する。特に、ケーブル駆動並列ロボット（Cable-Driven Parallel Robot: CDPR）の利点を活かし、大きな作業空間と高い応答性を持つハプティックインタフェースを構築する。ワイヤのテンション制御による力覚レンダリング技術を確立し、バーチャル物体の材質感、重量感、形状を忠実に再現する。また、リニアアクチュエータとの統合によりワークスペースの拡張を図り、実用的なVRアプリケーションでの有効性を実証する。最終的には、産業設計、医療シミュレーション、教育訓練分野での実用展開を目指す。

## 提案手法・システム

**ハイブリッドケーブル駆動ハプティックシステム**: ワイヤ駆動機構とリニアアクチュエータを統合したハイブリッド構成により、従来のワイヤ駆動システムの作業空間制約を克服した。4本のケーブルによる平面内制御と垂直方向リニアアクチュエータにより、3次元空間での力覚フィードバックを実現し、ワークスペースを大幅に拡張した。

**アドミッタンス制御による力覚レンダリング**: ワイヤテンション制御とアドミッタンス制御を組み合わせた力覚レンダリングアルゴリズムを開発した。バーチャル物体との接触検出、衝突応答計算、力覚フィードバック生成を統合し、リアルタイムでの触覚感覚提示を可能にした。外乱オブザーバを用いたセンサレス力推定により、システムの簡素化と安全性向上を図った。

**VR統合インタフェースシステム**: Oculus RiftとUnity 3Dエンジンを用いたVR環境と、開発したハプティックインタフェースをシームレスに統合するシステムを構築した。リアルタイム位置追跡、力覚レンダリング、視覚フィードバックの同期制御により、高い没入感を持つVR体験を実現した。

## 実験・評価

**ワークスペース拡張効果の検証**: リニアアクチュエータの統合により、従来のワイヤ駆動システムと比較してワークスペースが約300%拡張されることを確認した。垂直方向の移動範囲は300mmから900mmに向上し、実用的なVRインタラクションに必要な空間を確保した。

**力覚レンダリング性能の評価**: 様々な仮想物体（剛体、弾性体、粘性体）に対する力覚レンダリング精度を評価した。周波数応答解析により、10Hz以下の低周波数帯域で高い再現性を示し、人間の力覚認知に必要な性能を満たすことを確認した。アドミッタンス制御により、安定した力覚フィードバックが実現された。

**ユーザビリティ評価**: 12名の被験者による主観評価実験において、提案システムの直感性、没入感、操作性を従来システムと比較評価した。没入感スコアは従来システムより25%向上し、操作の自然さについても有意な改善が確認された。VR酔いの症状も軽減され、長時間利用での快適性が向上した。

## 成果・貢献

本研究により、ワイヤ駆動機構を基盤とした実用的なVR力覚インタフェースの基盤技術が確立され、従来の高コスト・複雑なハプティックシステムの課題を解決する革新的な手法が提供された。ハイブリッド構成によるワークスペース拡張技術は、ワイヤ駆動システムの実用性を大幅に向上させ、VR分野での普及可能性を高めた。アドミッタンス制御とセンサレス力推定の統合により、安全性と性能を両立する制御技術を確立した。

開発したシステムは、産業分野での製品設計・プロトタイピング、医療分野での手術シミュレーション・リハビリテーション訓練、教育分野での技能訓練・科学教育、エンターテインメント分野での高没入感VRゲームなど、幅広い応用が期待される。特に、従来の高価なハプティックデバイスでは導入困難だった分野での普及により、VR技術の社会実装を加速する可能性を持つ。ワイヤ駆動力覚インタフェースの設計指針として、今後の関連研究の発展にも重要な貢献をなしている。

## 発表業績

- B. Poitrimol and H. Igarashi: "Haptic Interface for Virtual Reality based on Hybrid Cable-Driven Parallel Robot," 2020 IEEE 16th International Workshop on Advanced Motion Control (AMC), Kristiansand, Norway, 2020, pp. 351-356.

- Bastien Poitrimol, Hiroshi Igarashi: "Haptic Rendering and Manipulability of Cable-Based Planar Haptic Interface," The Proceedings of JSME annual Conference on Robotics and Mechatronics (Robomec), 2020.

- Bastien Poitrimol, Hiroshi Igarashi: "Workspace Enlargement of Cable-Based Haptic Device Using Linear Actuator," Journal of Signal Processing, 2020, Vol. 24, No. 4, pp. 149-152.

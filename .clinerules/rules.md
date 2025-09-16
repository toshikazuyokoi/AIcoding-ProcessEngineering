# Core Rules (compressed for runtime)

- Principles
  1) 段階的詳細化 / 2) 1ファイル=1タスク / 3) 品質の作り込み / 4) トレーサビリティ

- STEP 判定（ヒューリスティック）
  - 要件未完: @workflows/step1-requirements.md
  - 設計未完: @workflows/step2-system-design.md → @workflows/step3-detailed-design.md
  - テスト設計未完: @workflows/step4-test-design.md
  - 実装計画未完: @workflows/step5-implementation-planning.md
  - コーディング: @workflows/step7-coding-execution.md

- 参照パターン
  - Workflows: @workflows/[name].md
  - Quality Gates: @workflows/quality-gate-[target].md

- 自律運用モード（要旨）
  1) 成果物から現在STEPを自動判定
  2) 人間の要求をメタ変換（@workflows/meta-workflow-orchestrator.md）
  3) 選択WF 1本だけ注入・実行
  4) 対応Gate 1本だけ注入・チェック
  5) 理論は各WFの Source Mapping の該当節のみ最小抜粋（<=200 tokens）

- コンテキスト最適化
  - 常駐: 本ルールのみ
  - 実行: 現在WF 1本のみ
  - 完了: 対応Gate 1本のみ
  - 禁止: 複数WF同時/ theory丸読み/ Gateの事前多重注入

- 緊急対応
  1) 対象 Gate を即時実行→ 2) 根本原因特定 → 3) 必要なら前段階に戻る → 4) 再発防止策を文書化

- Canonical
  - docs-agent/core-rules.md（本ファイルは圧縮版）


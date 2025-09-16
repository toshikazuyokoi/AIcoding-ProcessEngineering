# AGENTS.md 連携検討レポート（設計・方針・移行計画）

## 要旨（結論）
- AGENTS.md は「エージェント向け README」として、エージェントが最初に参照する単一の入口を提供するオープンな慣習（標準 Markdown／必須項目なし）。
- 既存の docs-agent（Core Rules／Workflows／Quality Gates／Meta Orchestrator／Context Protocol）は、AGENTS.md と高い親和性がある。
- 最適解は「薄い AGENTS.md（数KB）」をリポジトリ直下に置き、詳細は docs-agent に委譲する“ゲートウェイ化”。
- これにより .clinerules（Cline 用）と AGENTS.md（汎用エージェント用）の両輪で、ほぼ全てのコーディングエージェントに対応できる。

---

## agents.md（AGENTS.md）の要点
- 目的：エージェントに必要な文脈・手順・規約を、予測可能な単一ファイルに集約（人向け README とは分離）。
- 仕様：
  - ルート（必要に応じてサブプロジェクト配下にもネスト可、近接優先で読み取られる）
  - Markdown で任意の章立て（必須項目なし）
  - 記載コマンドは自動実行の対象になりやすい（安全設計が重要）
- 推奨セクション（例）：セットアップ・テスト・コード規約・PR ルール・大規模リポのナビ・セキュリティなど

---

## docs-agent との整合性（ギャップ分析）
- 強い整合：
  - Core Rules（常駐）と Context Protocol（最小注入）→ AGENTS.md の「Context policy」へ要約
  - Workflows／Quality Gates → AGENTS.md の「Workflow index」「Quality gate policy」でリンク
  - Meta Orchestrator（自律選択）→ AGENTS.md の「Process mode」で 1〜2 行に要約し docs-agent に誘導
- 補うべき点：
  - AGENTS.md は“薄く”保ち、詳細は docs-agent へ委譲（肥大化はコンテキスト最適化思想に反する）
  - 自動実行の安全境界（許可・禁止）を明記

---

## 推奨アーキテクチャ（役割分担）
- AGENTS.md（root, 薄いゲートウェイ）
  - Agent Quickstart（5〜10 行）
  - Process mode（自律運用モードの超要約）
  - Workflow index / Quality gate policy（docs-agent へのリンク）
  - Context policy（最小注入の原則・禁止事項）
  - Testing/Checks（安全に自動実行してよい範囲）
  - Safety & permissions（要承認の境界）
  - Monorepo note（ネスト AGENTS.md 方針）
- docs-agent（正本）
  - core-rules.md（詳細）
  - workflows/*.md と quality-gate-*.md（実行手順と検収）
  - meta-workflow-orchestrator.md / context-management-protocol.md（自律選択・最小注入）
- .clinerules（Cline 高速運用）
  - 既に整備済みの圧縮ルール・ワークフローラッパーを併存

---

## AGENTS.md 章立て案（ドラフト反映済みの構成）
1) Project overview for agents（1 段落）
2) Process mode（Autonomous Mode）
   - Core Rules 要約（5 行程度）→ docs-agent/core-rules.md
   - Meta Orchestrator（1〜2 行）→ docs-agent/workflows/meta-workflow-orchestrator.md
   - Context Protocol（1〜2 行）→ docs-agent/workflows/context-management-protocol.md
3) Workflow index（docs-agent/workflows）
   - STEP ワークフローと Quality Gate を一覧リンク
4) Context policy（最小注入／禁止事項）
5) Testing/Checks（安全に自動実行可な範囲だけ明記）
6) Safety & permissions（常に明示）
7) Monorepo note（将来のネスト運用）
8) Tooling integration（任意）

---

## 移行計画（変更なし段階の計画）
- Phase 0：要件分析と設計（本レポート）
- Phase 1：AGENTS.md ドラフトを root に追加（薄く／docs-agent へリンク誘導）
- Phase 2：自動実行コマンドの安全確認（存在・危険性・コスト境界）
- Phase 3：運用改善（エージェントログから曖昧要求の定型化を AGENTS.md に反映）
- Phase 4：モノレポ化時にサブディレクトリへ AGENTS.md をネスト（近接優先を活用）

---

## 安全設計（重要）
- 自動実行ポリシー：
  - 許可：ローカルの安全な静的チェック・テスト（存在すれば）
  - 要承認：依存インストール／DB変更／デプロイ／外部課金 API／長時間ジョブ
  - 禁止：破壊的操作・本番データ変更・秘匿情報の外部送信
- コンテキスト方針：
  - 常駐＝ Core Rules 圧縮要旨、JIT 注入＝「現在 WF 1 本＋必要時 Gate 1 本」、理論は Source Mapping に従い最小抜粋

---

## 期待効果
- 多様なエージェントが最初に見る統一入口（.clinerules 非対応エージェントにも対応）
- docs-agent の再利用（正本）を保ちながら、導入ハードルを最低限に
- 近接優先ルールにより将来の package 指向にもスムーズに拡張

---

## オープン項目
- 自動実行コマンドの粒度（プロジェクトの実情と安全性のバランス）
- モノレポ化時の AGENTS.md ネスト・運用フロー
- 他エージェント固有の補足（必要生じたら追加）

---

## 参考リンク
- 公式サイト: https://agents.md/
- docs-agent（本リポ正本）: core-rules / workflows / quality-gates / meta / protocol

> 注：本レポートは「まだ修正はしない」方針での設計検討結果です。次段で root に AGENTS.md（薄いゲートウェイ）を追加します。

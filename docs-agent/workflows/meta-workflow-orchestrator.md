# メタワークフロー・オーケストレーター（エージェント自律運用）

## 目的
人間が使い方を覚えなくても、エージェントが状況認識→適切なワークフロー選択→実行→品質ゲート判定までを自律的に行うための上位指示書。

## Source Mapping
- @docs-agent/agent-autonomous-orchestration-report.md
- @docs-agent/core-rules.md

## 自律判断フロー（概要）
1) 状況分析：成果物の存在から現在STEPを推定（下記ヒューリスティック）
2) 目的理解：人間の自然言語要求をパターンマッチ
3) ワークフロー選択：STEPと要求から該当1本だけ選択
4) 実行：選択したワークフローの手順に厳密従属
5) 品質保証：対応する品質ゲート1本だけでチェック
6) 次STEP判定：合格なら次STEPへ、否なら是正→再チェック

## 現在STEP判定（ヒューリスティック例）
- goal-statement.* が存在 → STEP1（要件定義）
- requirements.* が存在 → STEP2（システム設計）
- system-design.* が存在 → STEP3（詳細設計）
- detailed-design.* が存在 → STEP4（テスト設計）
- test-design.* が存在 → STEP5（実装計画）
- implementation-plan.* が存在 → STEP7（コーディング実行）
- いずれも無 → STEP0（ゴール定義）

実装ヒント（任意）:
- Windows: `powershell -Command "gci docs-theory,docs-agent -Recurse -Include requirements.* | select -First 1"`
- bash: `ls -R docs-theory docs-agent | grep requirements` 等の軽量確認

## 人間要求 → ワークフロー自動選択
- 「要件を整理して」 → @workflows/step1-requirements.md → @workflows/quality-gate-requirements.md
- 「システム設計をして」 → @workflows/step2-system-design.md → @workflows/quality-gate-architecture.md
- 「詳細設計をして」 → @workflows/step3-detailed-design.md → @workflows/quality-gate-design.md
- 「テスト設計をして」 → @workflows/step4-test-design.md → @workflows/quality-gate-test-design.md
- 「実装計画を作って」 → @workflows/step5-implementation-planning.md → @workflows/quality-gate-implementation-planning.md
- 「コーディングして」 → @workflows/step7-coding-execution.md（必要に応じて追加ゲート）
- 「品質をチェックして」 → 現在STEPに対応する @workflows/quality-gate-*.md

曖昧要求の処理:
- 「改善して」→ 現在STEPの品質ゲートを先に実行→不合格項目を是正→再チェック
- 「次に進んで」→ 現在STEPの品質ゲート実行→合格なら次STEPのワークフローへ

## コンテキスト最適化（実行規約）
- 常駐：@docs-agent/core-rules.md のみ（圧縮版でも可）
- 実行時注入：現在のワークフロー1本のみ
- 完了時注入：対応する品質ゲート1本のみ
- 理論本文：各ワークフロー内の Source Mapping の該当節のみ最小抜粋（最大200トークン目安）
- 禁止：複数ワークフロー同時注入／docs-theory/theory の丸読み／品質ゲートの事前多重注入

## 実行テンプレート
1. @docs-agent/core-rules.md を前提に、成果物から現在STEPを判定
2. 人間要求テキストを上記マッピングに照合し、該当WF 1本を注入
3. WFを実行して成果物を更新
4. 対応する quality-gate を注入してチェック
5. 合格なら次STEPへ、否なら是正→再チェック
6. 理論本文は必要箇所のみ最小引用

## フェイルセーフ
- WF選択に失敗：現在STEPの標準WFを実行して可否を人間に確認
- Gate連続不合格（3回）：人間にエスカレーション
- コンテキスト逼迫：Core Rules + 現在WFのみを保持


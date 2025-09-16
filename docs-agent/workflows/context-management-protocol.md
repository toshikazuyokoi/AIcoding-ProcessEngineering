# コンテキスト管理プロトコル（エージェント自動実行ルール）

## 目的
コンテキスト溢れを防ぎつつ、プロセスエンジニアリング理論を再現可能に運用するための、最小注入ルールを定義する。

## Source Mapping
- @docs-agent/agent-autonomous-orchestration-report.md
- @docs-agent/core-rules.md

## 基本原則
- 常駐は Core Rules のみ
- 実行時に現在のワークフロー1本を注入
- 完了時に対応する品質ゲート1本を注入
- 理論本文は Source Mapping の該当節のみ最小抜粋

## 実行ルール（エージェントが毎回行う）
1) @docs-agent/core-rules.md を前提に、成果物から現在STEPを判定
2) 人間要求→ワークフロー変換（@workflows/meta-workflow-orchestrator.md を参照）
3) ワークフロー1本のみ注入して実行
4) 完了後に対応する品質ゲート1本のみ注入してチェック
5) 理論本文は必要時のみ該当節の最小抜粋（最大200トークン）

## 禁止事項（コンテキスト肥大化防止）
- 複数のワークフローを同時に注入
- docs-theory/theory の丸読み
- 品質ゲートの事前多重注入（実行直前に1本だけ）
- 過去STEP成果物の全文引用（必要箇所のみの抜粋に限定）

## 推奨事項
- チェックリスト（品質ゲート）の Yes/No 判断は厳格に
- ワークフローの「次STEP移行条件」を満たしてから移行
- 参照の際は常にファイルパスと節名を明記（トレーサビリティ維持）

## 実行テンプレート（雛形）
```
1. Core Rules 常駐
2. 成果物確認→現在STEP判定
3. {選択WF} を読み込み実行
4. {対応Gate} を読み込みチェック
5. 合格→次STEP／不合格→是正→再チェック
6. 理論は Source Mapping 該当節のみ引用
```

## Cline 等の運用メモ（任意）
- .clinerules/rules.md に Core Rules 圧縮版を配置
- .clinerules/workflows/ に docs-agent/workflows と同名で配置（またはラッパー）
- チャット中は `/stepN-...` や `/quality-gate-...` で1本だけ注入


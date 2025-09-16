# docs-theory / docs-agent の名称再設計に関する検討レポート（まだ変更しない）

## 要旨（結論）
- 目的に適うフォルダ名は「役割」と「利用者（人間/エージェント）」が一目で分かること。
- 現状の `docs-theory`（原典/理論）と `docs-agent`（再編/運用）は役割が不透明。命名を見直す価値が高い。
- 推奨は「理論」と「運用（エージェント/プレイブック）」を直観的に切り分ける英語短語。
- 物理的リネームはリンク影響が大きいため、決定前に移行計画と影響範囲を明確化し、段階的に実施する。

提案トップ3（どれも英語・短く・役割が明快）
- A. `docs-theory`（理論原典） と `docs-agent`（エージェント運用）
- B. `process-theory`（理論） と `agent-playbooks`（運用手順＝WF群）
- C. `theory`（理論） と `playbooks`（運用）

補足：GitHub Pages や既存 CI が `docs/` を前提にしている場合は A（docs-接頭）の方が安全性が高い。

---

## 命名原則（評価軸）
1) 意味の明瞭性
   - 見ただけで「何が入っているか」が分かる（原典か運用か）。
2) 一貫性と拡張性
   - 将来のモノレポ化/パッケージ分割でも破綻しない。
3) 機械親和性（ツール/エージェント）
   - 短く英語、スペース/大文字/特殊文字を避ける。
4) 変更コスト最小化
   - 既存リンクや自動化（CI, Pages）への影響を抑える命名。
5) コンテキスト安全性
   - エージェントが理論（大容量）へ迷い込みにくい構造（入口と警告の併設）。

---

## 候補セットとメリット/デメリット

### セットA：docs-theory / docs-agent（総合バランス型）
- 概要：既存 `docs` を理論に特化して `docs-theory` に改名、`docs2` は `docs-agent` に改名。
- 長所：
  - docs 接頭で「文書」系であることを揃えつつ、役割が明瞭。
  - Pages/CI が `docs/` 固定でなければ影響は中程度。
- 短所：
  - 両方リネームのため参照更新が広範囲。

### セットB：process-theory / agent-playbooks（意味重視・語感強）
- 概要：用途に踏み込んだ語を採用。運用側を Playbooks として「実行手順集」を明示。
- 長所：
  - 概念が明快（理論 vs 実務プレイブック）。
  - 将来的に `agent-*` を増やす拡張も容易。
- 短所：
  - 既存の `docs` 慣習から外れるため、Pages/自動化の前提調整が必要になる場合あり。

### セットC：theory / playbooks（最短・最直観）
- 概要：シンプル最短。人にも機械にも覚えやすい。
- 長所：
  - 短く覚えやすい。IDE 検索も楽。
- 短所：
  - リポジトリ規約次第で「文書は docs/ に置くべき」などと衝突の可能性。

---

## 命名と運用の整合（docs-agent の設計前提）
- 運用側（現 docs-agent）は、Core Rules / Workflows / Quality Gates / Meta Orchestrator / Context Protocol を包含。
- よって `docs-agent` or `agent-playbooks` は、
  - エージェント入口（AGENTS.md）との整合が良く、
  - 「最小注入」「WF1本＋Gate1本」「Source Mapping」を想起しやすい。

---

## 既存ツール/自動化との互換
- GitHub Pages 等が `docs/` 固定の場合：
  - `docs` をそのまま theory 用に使うと混乱。代わりに `docs-site/` を公開用に用意する等の選択肢も。
  - Pages 要件なしなら、`docs-theory` などに改名しても問題は少ない。
- CI/スクリプト：
  - パスベタ書きがある場合は置換が必要。リンクチェッカーで事前検証。

---

## 推奨（条件別）
- 条件1：Pages/CI が `docs/` 前提でない → セットA または B を推奨。
  - デフォルト：A. `docs-theory` / `docs-agent`（バランス良）
  - 概念を強調：B. `process-theory` / `agent-playbooks`
- 条件2：`docs/` を他用途で固定利用 → セットC も選択肢。
  - `theory` / `playbooks`（最短・明快）。

---

## 移行計画（実施する場合の段取り）
1) 影響調査
   - リンク（相対/絶対）、AGENTS.md、.clinerules、README 群、レポート群、CI 設定。
2) 試験的ブランチで一括置換＋リンクチェッカー
   - 内部リンク・外部参照・画像/図表パスを検証。
3) ガードレール文言の追加
   - 運用側各文書の先頭に「最小注入、theory 丸読み禁止」。
   - theory 側 README に「人間向け。エージェントは Source Mapping で最小抜粋のみ」。
4) マージ後の監視
   - 404/リンク切れ監視。AGENTS.md/.clinerules の差分同期手順を README に明記。

---

## 決定のためのチェックリスト
- [ ] GitHub Pages 等の `docs/` 依存はあるか？
- [ ] 参照更新に耐えられる CI とレビュー体制があるか？
- [ ] 将来、モノレポ化やサブパッケージ増加時の命名一貫性は保てるか？
- [ ] 人間/エージェント双方にとって混乱がないか？

---

## 結論
- 名前は「役割」を語るべき。現状の `docs`/`docs2` はその点で改善余地が大きい。
- 現時点の第一候補は `docs-theory`（原典）と `docs-agent`（運用）の組合せ。要件次第で `process-theory`/`agent-playbooks` も有力。
- 実施の際は、リンク影響の可視化・段階移行・ガードレール明記を必ずセットで行う。

（本レポートは検討用。まだ修正は行いません）


---

## セットA（docs→docs-theory, docs2→docs-agent）リネーム時の影響調査（洗い出し）

- 置換指針
  - docs-agent/ を正に、@docs-agent/ を正に
  - docs-theory/ を理論原典への参照に使用
  - @docs-theory/ を理論原典への参照に使用
  - 注意: テンプレート内の「他プロジェクト向けサンプルとしての docs/」は原則据え置き（例示のため）。

### A) エージェント入口・ランタイムラッパー
- AGENTS.md
  - docs-agent/core-rules.md, docs-agent/workflows/*, meta/context へのリンク全般
- .clinerules/workflows/*.md（全ファイル）
  - canonical コメントと本文に @docs-agent/workflows/... を複数箇所（例: step2-system-design.md 行1,5-6）
- .clinerules/rules.md
  - docs-agent/core-rules.md 等への参照（圧縮要約内）。

### B) docs-agent 直下の正本ドキュメント
- docs-agent/README.md
  - docs-agent/core-rules.md, docs-agent/workflows/*, docs-agent/agent-... への複数参照
  - docs-theory/theory/* の注記（理論最小抜粋の説明）
- docs-agent/current-status.md
  - `@docs-agent/core-rules.md`（行90-93 近辺）
  - `@docs-agent/current-status.md`（行99-101 近辺）
  - 参考資料: `docs-theory/templates/`, `docs-theory/theory/`（行115-117 近辺）
  - 命名規則: `docs-agent/...` プレフィックス（行65-68）
- docs-agent/agents-md-adaptation-report.md
  - docs-agent への構造参照（多数）
- docs-agent/agent-autonomous-orchestration-report.md
  - `@docs-agent/core-rules.md`（行81付近）
  - 禁止事項: `docs-theory/theory` 丸読み（行90-93付近）
- docs-agent/docs-structure-consolidation-report.md
  - 本文中に docs-theory/ と docs-agent/ の対比参照（多数）
- docs-agent/docs-folder-naming-report.md（本レポート）
  - 文中の候補・解説に docs-theory / docs-agent の記述（多数）

### C) ワークフロー（docs-agent/workflows）内の参照
- meta-workflow-orchestrator.md
  - Source Mapping: `@docs-agent/agent-autonomous-orchestration-report.md`, `@docs-agent/core-rules.md`
  - コンテキスト最適化: `@docs-agent/core-rules.md`、禁止に `docs-theory/theory` 丸読み（行45-50）
- context-management-protocol.md
  - Source Mapping: `@docs-agent/...`
  - 禁止事項: `docs-theory/theory` 丸読み（行23-27）
- step0-goal-definition.md
  - アウトプット: `docs-agent/goal-statement.md`, `docs-agent/stakeholders.md`, `docs-agent/constraints.md`（行15-18）
  - Source Mapping: `@docs-theory/theory/...`（行19-23）
- step1-requirements.md
  - アウトプット: `docs-agent/requirements/...`（行15-17）
  - Source Mapping: `@docs-theory/theory/...`（行20-23）
- step2-system-design.md
  - アウトプット: `docs-agent/design/system-architecture.md`, `docs-agent/design/tech-stack.md`（行15-17）
  - Source Mapping: `@docs-theory/theory/...`（行18-22）
- quality-gate-requirements.md
  - チェック手順: `ls docs-agent/requirements/`, `node ... docs-agent/requirements/`（行63-70）
- quality-gate-architecture.md
  - チェック手順: `grep -n "```mermaid" docs-agent/design/*.md`（行68-69）
- quality-gate-design.md
  - チェック手順: `ls docs-agent/detailed-design/`（行68-71）

注記: 上記以外の step3/4/5/7 等にも「アウトプット先として docs-agent/...」の指示が含まれる可能性が高く、同様の置換／方針決定が必要です（網羅検索を実施予定）。

### D) 原典側（docs-theory）に残る参照
- docs-theory/theory/reproducibility-validation-plan.md
  - `docs-theory/ai-coding-development-process-v1.1.md`, `docs-theory/cline-process-engineering-rules.md` 等、repo 直下 `docs-theory/` への相対参照（複数）
- docs-theory.back/*, docs-theory/templates/*, docs-theory/templates/en/*, docs-theory/templates/…（多数）
  - これらの多くは「他プロジェクト向けの雛形・サンプルコード」。
  - 例: Node スクリプト内の `const docsDir = path.join(__dirname, '../docs-theory');` や、初期化スクリプトの `mkdir -p docs-theory/{...}` 等。
  - 方針: 雛形としての一般性を保つため原則据え置き（本リポのフォルダ名に合わせて強制変更しない）。

---

## 影響度評価と論点

- 高影響（要修正確定）
  - AGENTS.md（入口のため表記ズレは即混乱）
  - .clinerules/workflows/*（ランタイム呼び出しが直撃）
  - docs-agent/README.md・current-status.md（正本ガイド）
  - docs-agent/workflows/* の Source Mapping と禁止事項の `docs-theory/theory` 記述
- 中〜高影響（要方針決定）
  - ワークフロー内「アウトプット先が docs/...」の指定
    - セットAでは「理論=docs-theory」「運用=docs-agent」へ分離するため、成果物の出力先は原則 `docs-agent/...` へ変更するのが整合的。
    - ただし既存のプロジェクト慣習で `docs/` を「プロジェクト文書」一般として用いる場合は、別フォルダ（例: `project-docs/`）に分離する選択も検討。
- 低影響（据え置き）
  - docs/templates/* 系の「他プロジェクト向け汎用サンプル」の中の `docs/` 記述（例示のため現状維持）。

---

## 次アクション（まだ修正しない）
1) 追加の網羅検索
   - パターン: `docs-agent/|@docs-agent/|\bdocs-theory/|@docs-theory/|docs-theory\(\\|/\)theory` を対象に、全リポジトリで再走査し、一覧を更新（行番号付き）。
2) 出力先ディレクトリの最終決定
   - ワークフロー成果物の標準出力先を `docs-agent/` に統一するか、`project-docs/` を新設するかを決定。
3) 置換計画のドラフト
   - 影響度の高い順にコミットを分割（入口→正本→WF→報告類）。
   - 一時的に旧パス案内の薄いラッパー（README リダイレクト）を用意するか検討。


# プロセスエンジニアリング理論のルール・ワークフロー分割再構成レポート

## 1. 現状分析

### 1.1 現在の理論構造の問題点

**コンテキスト圧迫要因**：
- `ai-coding-development-process-v1.3-complete.md`：包括的すぎる（全STEP詳細）
- `cline-process-engineering-rules.md`：ルールとワークフローが混在
- 品質ゲート、チェックリスト、フロー図が一体化
- 実装時に不要な理論背景まで読み込み

**使用パターン分析**：
- **常時必要**：基本原則、現在STEP判定、品質基準
- **STEP開始時のみ**：具体的手順、テンプレート、チェックリスト
- **問題発生時のみ**：品質ゲート、トラブルシューティング
- **振り返り時のみ**：改善プロセス、メトリクス

## 2. 分割戦略

### 2.1 Core Rules（常時読み込み：1-2KB以内）

**含むべき内容**：
```
基本原則（4つ）
現在STEP判定ロジック
品質基準（最小限）
ワークフロー参照方法
緊急時対応
```

**除外すべき内容**：
- 詳細手順
- 具体的テンプレート
- 理論背景
- 実装例

### 2.2 Workflow Files（必要時@参照）

#### A. STEP別ワークフロー（7ファイル）
- `step0-goal-definition-workflow.md`
- `step1-requirements-workflow.md`
- `step2-system-design-workflow.md`
- `step3-detailed-design-workflow.md`
- `step4-test-design-workflow.md`
- `step5-implementation-planning-workflow.md`
- `step7-coding-execution-workflow.md`

#### B. 品質保証ワークフロー（4ファイル）
- `quality-gate-requirements.md`
- `quality-gate-architecture.md`
- `quality-gate-design.md`
- `quality-gate-implementation.md`

#### C. 管理ワークフロー（3ファイル）
- `task-management-workflow.md`
- `3phase-implementation-workflow.md`
- `continuous-improvement-workflow.md`

## 3. 詳細設計

### 3.1 Core Rules設計

**構造**：
```markdown
# Core Rules (1.5KB)
## 基本原則（200文字）
## 現在STEP判定（300文字）
## 品質基準（400文字）
## ワークフロー参照法（300文字）
## 緊急対応（300文字）
```

**判定ロジック例**：
```
IF 要件仕様書未作成 → @step1-requirements-workflow.md
IF 設計書作成中 → @step2-system-design-workflow.md
IF コーディング中 → @step7-coding-execution-workflow.md
IF 品質問題発生 → @quality-gate-*.md
```

### 3.2 ワークフローファイル設計

**標準構造**（各2-3KB）：
```markdown
# [STEP名] Workflow
## 目的・スコープ（200文字）
## インプット・アウトプット（300文字）
## 具体的手順（1000-1500文字）
## チェックリスト（500文字）
## 次STEP移行条件（200文字）
```

### 3.3 参照パターン設計

**段階的参照**：
1. **開始時**：Core Rules → STEP判定 → 該当ワークフロー
2. **実行中**：Core Rules + 現在ワークフローのみ
3. **問題時**：Core Rules + 品質ゲートワークフロー
4. **完了時**：Core Rules + 次STEPワークフロー

## 4. 実装上の考慮事項

### 4.1 ファイル命名規則
```
core-rules.md                    # 常時読み込み
workflows/
  ├── step0-goal-definition.md
  ├── step1-requirements.md
  ├── step2-system-design.md
  ├── step3-detailed-design.md
  ├── step4-test-design.md
  ├── step5-implementation-planning.md
  ├── step7-coding-execution.md
  ├── quality-gate-requirements.md
  ├── quality-gate-architecture.md
  ├── quality-gate-design.md
  ├── quality-gate-implementation.md
  ├── task-management.md
  ├── 3phase-implementation.md
  └── continuous-improvement.md
```

### 4.2 相互参照メカニズム
- Core Rulesから`@workflows/xxx.md`で参照
- ワークフロー間は`@workflows/xxx.md`で相互参照
- 品質ゲートは`@quality-gate-xxx.md`で参照

### 4.3 バージョン管理
- Core Rules：v1.3-modular
- 各ワークフロー：独立バージョニング
- 互換性マトリックス管理

## 5. 期待効果

### 5.1 コンテキスト効率化
- **現在**：20-30KB → **改善後**：2-5KB（60-80%削減）
- 必要な情報のみ動的ロード
- AIの推論能力向上

### 5.2 保守性向上
- 各ワークフローの独立更新
- 理論進化への柔軟対応
- 部分的適用の容易化

### 5.3 実用性向上
- 段階的学習の促進
- 特定STEP専門化の支援
- トラブルシューティングの高速化

## 6. 移行戦略

### Phase 1：Core Rules抽出
- 現在の理論から基本原則を抽出
- 1.5KB以内に圧縮
- 参照メカニズム設計

### Phase 2：ワークフロー分割
- STEP別に詳細手順を分離
- 標準テンプレート化
- 相互参照関係構築

### Phase 3：検証・最適化
- 実際のコーディングで検証
- コンテキスト使用量測定
- フィードバック反映

この再構成により、理論の優秀性を保ちながら実用性を大幅に向上させることができると考えられます。
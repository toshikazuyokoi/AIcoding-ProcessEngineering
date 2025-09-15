# STEP 4: テスト設計ワークフロー

## 目的・スコープ

詳細設計を基に、包括的なテスト戦略を策定し、具体的なテストケースを設計する。品質保証の基盤となるテスト体系を確立する。

## インプット・アウトプット

**インプット**：
- クラス設計表
- メソッドI/Fリスト
- データベース設計

**アウトプット**：
- テスト戦略書（`docs-agent/test-design/strategy.md`）
- テスト対象一覧（`docs-agent/test-design/targets.md`）
- テストケース定義書（`docs-agent/test-design/test-cases.md`）

## Source Mapping
- @docs-theory/theory/ai-coding-development-process-v1.3-deliverable-flow.md § テスト設計位置づけ
- @docs-theory/theory/quality-gate-detailed-specifications-v1.3.md § Test設計
- @docs-theory/theory/quality-assurance-integration.md
- @docs-theory/theory/reproducibility-validation-plan.md

## 具体的手順

### 1. テスト戦略策定
```markdown
# テスト戦略

## テストレベル
- **単体テスト**: 個別クラス・メソッドの動作確認
- **結合テスト**: コンポーネント間の連携確認
- **E2Eテスト**: エンドユーザー視点での動作確認

## テスト手法
- **ホワイトボックステスト**: コード構造に基づくテスト
- **ブラックボックステスト**: 仕様に基づくテスト
- **境界値テスト**: 境界条件での動作確認
```

### 2. カバレッジ目標設定
| テストレベル | カバレッジ目標 | 測定方法 |
|--------------|----------------|----------|
| 単体テスト | 行カバレッジ 90%以上 | Jest coverage |
| 単体テスト | 分岐カバレッジ 85%以上 | Jest coverage |
| 結合テスト | API カバレッジ 100% | 手動確認 |
| E2Eテスト | 主要シナリオ 100% | Playwright |

### 3. テスト対象一覧作成
| 対象 | テストレベル | 優先度 | 担当 |
|------|--------------|--------|------|
| UserService | 単体テスト | 高 | 開発者 |
| TaskService | 単体テスト | 高 | 開発者 |
| UserController | 結合テスト | 高 | 開発者 |
| TaskController | 結合テスト | 高 | 開発者 |
| ログイン機能 | E2Eテスト | 高 | QA |
| タスク管理機能 | E2Eテスト | 高 | QA |

### 4. 単体テストケース設計
```typescript
// UserService テストケース例
describe('UserService', () => {
  describe('createUser', () => {
    it('正常なユーザーデータで作成成功', async () => {
      // Given
      const userData = { name: 'Test User', email: 'test@example.com' };
      
      // When
      const result = await userService.createUser(userData);
      
      // Then
      expect(result.id).toBeDefined();
      expect(result.name).toBe('Test User');
    });
    
    it('重複メールアドレスで作成失敗', async () => {
      // Given
      const userData = { name: 'Test User', email: 'existing@example.com' };
      
      // When & Then
      await expect(userService.createUser(userData))
        .rejects.toThrow('Email already exists');
    });
  });
});
```

### 5. 結合テストケース設計
| テストケースID | テスト内容 | 前提条件 | 実行手順 | 期待結果 |
|----------------|------------|----------|----------|----------|
| IT-001 | ユーザー作成API | DBが空 | POST /api/users | 201 Created |
| IT-002 | タスク作成API | ユーザーが存在 | POST /api/tasks | 201 Created |
| IT-003 | 認証失敗 | 無効なトークン | GET /api/tasks | 401 Unauthorized |

### 6. E2Eテストシナリオ設計
```typescript
// E2Eテストシナリオ例
test('タスク管理の基本フロー', async ({ page }) => {
  // 1. ログイン
  await page.goto('/login');
  await page.fill('[data-testid=email]', 'user@example.com');
  await page.fill('[data-testid=password]', 'password');
  await page.click('[data-testid=login-button]');
  
  // 2. タスク作成
  await page.click('[data-testid=create-task-button]');
  await page.fill('[data-testid=task-title]', 'New Task');
  await page.fill('[data-testid=task-description]', 'Task description');
  await page.click('[data-testid=save-task-button]');
  
  // 3. タスク確認
  await expect(page.locator('[data-testid=task-list]')).toContainText('New Task');
});
```

### 7. テストデータ設計
```typescript
// テストデータファクトリー
export const TestDataFactory = {
  createUser: (overrides = {}) => ({
    id: 'user-123',
    name: 'Test User',
    email: 'test@example.com',
    ...overrides
  }),
  
  createTask: (overrides = {}) => ({
    id: 'task-123',
    title: 'Test Task',
    description: 'Test Description',
    status: 'pending',
    userId: 'user-123',
    ...overrides
  })
};
```

## チェックリスト

- [ ] テスト戦略が策定されている
- [ ] カバレッジ目標が定量的に設定されている
- [ ] テスト対象一覧が作成されている
- [ ] 単体テストケースが設計されている
- [ ] 結合テストケースが設計されている
- [ ] E2Eテストシナリオが設計されている
- [ ] テストデータ設計が完了している
- [ ] 標準テーブル形式が使用されている

## 次STEP移行条件

- 全テストケースが設計されている
- カバレッジ目標が明確に設定されている
- テストデータ準備が完了している
- `@workflows/quality-gate-test-design.md`での品質確認完了
- `@workflows/step5-implementation-planning.md`への移行準備完了
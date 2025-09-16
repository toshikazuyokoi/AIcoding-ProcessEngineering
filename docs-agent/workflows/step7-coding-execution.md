# STEP 7: コーディング実行ワークフロー

## 目的・スコープ

実装計画に基づいて実際のコーディングを実行する。3フェーズ実装モデルに従い、段階的に品質の高いコードを作成し、継続的にテストを実行する。

## インプット・アウトプット

**インプット**：
- 実装コンポーネント一覧
- 開発工程表
- ディレクトリ構造マップ
- クラス設計表
- テストケース定義書

**アウトプット**：
- 実装済みソースコード
- 単体テストコード
- 結合テストコード
- E2Eテストコード
- テスト実行結果レポート

## Source Mapping
- @docs-theory/theory/ai-coding-development-process-v1.3-deliverable-flow.md § 実装/テスト
- @docs-theory/theory/quality-assurance-integration.md
- @docs-theory/theory/process-engineering-v1.3-complete-definition.md § STEP7

## 具体的手順

### 1. Phase 1: 実装・単体テスト実行

#### 1.1 Domain層実装
```typescript
// src/domain/entities/User.ts
export class User {
  constructor(
    public readonly id: string,
    public readonly name: string,
    public readonly email: Email,
    public readonly createdAt: Date = new Date()
  ) {}

  updateName(newName: string): User {
    return new User(this.id, newName, this.email, this.createdAt);
  }

  updateEmail(newEmail: Email): User {
    return new User(this.id, this.name, newEmail, this.createdAt);
  }
}
```

#### 1.2 単体テスト作成・実行
```typescript
// tests/unit/domain/entities/User.test.ts
describe('User', () => {
  it('should create user with valid data', () => {
    const email = new Email('test@example.com');
    const user = new User('123', 'Test User', email);
    
    expect(user.id).toBe('123');
    expect(user.name).toBe('Test User');
    expect(user.email.value).toBe('test@example.com');
  });

  it('should update name correctly', () => {
    const email = new Email('test@example.com');
    const user = new User('123', 'Test User', email);
    const updatedUser = user.updateName('Updated User');
    
    expect(updatedUser.name).toBe('Updated User');
    expect(updatedUser.id).toBe('123'); // 他の属性は変更されない
  });
});
```

#### 1.3 Application層実装
```typescript
// src/application/services/UserService.ts
export class UserService implements IUserService {
  constructor(private userRepository: IUserRepository) {}

  async createUser(userData: CreateUserDto): Promise<User> {
    const email = new Email(userData.email);
    const existingUser = await this.userRepository.findByEmail(email);
    
    if (existingUser) {
      throw new Error('Email already exists');
    }

    const user = new User(
      generateId(),
      userData.name,
      email
    );

    return await this.userRepository.save(user);
  }

  async updateUser(userId: string, updateData: UpdateUserDto): Promise<User> {
    const user = await this.userRepository.findById(userId);
    if (!user) {
      throw new Error('User not found');
    }

    let updatedUser = user;
    if (updateData.name) {
      updatedUser = updatedUser.updateName(updateData.name);
    }
    if (updateData.email) {
      updatedUser = updatedUser.updateEmail(new Email(updateData.email));
    }

    return await this.userRepository.save(updatedUser);
  }
}
```

### 2. Phase 2: 結合テスト実行

#### 2.1 Presentation層実装
```typescript
// src/presentation/controllers/UserController.ts
export class UserController {
  constructor(private userService: IUserService) {}

  async createUser(req: Request, res: Response): Promise<void> {
    try {
      const userData: CreateUserDto = req.body;
      const user = await this.userService.createUser(userData);
      res.status(201).json(user);
    } catch (error) {
      if (error.message === 'Email already exists') {
        res.status(409).json({ error: error.message });
      } else {
        res.status(500).json({ error: 'Internal server error' });
      }
    }
  }

  async updateUser(req: Request, res: Response): Promise<void> {
    try {
      const userId = req.params.id;
      const updateData: UpdateUserDto = req.body;
      const user = await this.userService.updateUser(userId, updateData);
      res.json(user);
    } catch (error) {
      if (error.message === 'User not found') {
        res.status(404).json({ error: error.message });
      } else {
        res.status(500).json({ error: 'Internal server error' });
      }
    }
  }
}
```

#### 2.2 結合テスト実行
```typescript
// tests/integration/api/users.test.ts
describe('Users API', () => {
  beforeEach(async () => {
    await setupTestDatabase();
  });

  afterEach(async () => {
    await cleanupTestDatabase();
  });

  it('POST /api/users should create user', async () => {
    const userData = {
      name: 'Test User',
      email: 'test@example.com'
    };

    const response = await request(app)
      .post('/api/users')
      .send(userData)
      .expect(201);

    expect(response.body.name).toBe('Test User');
    expect(response.body.email).toBe('test@example.com');
    expect(response.body.id).toBeDefined();
  });

  it('POST /api/users should return 409 for duplicate email', async () => {
    const userData = {
      name: 'Test User',
      email: 'existing@example.com'
    };

    // 最初のユーザー作成
    await request(app).post('/api/users').send(userData);

    // 重複メールでの作成試行
    const response = await request(app)
      .post('/api/users')
      .send(userData)
      .expect(409);

    expect(response.body.error).toBe('Email already exists');
  });
});
```

### 3. Phase 3: E2Eテスト実行

#### 3.1 E2Eテストシナリオ実行
```typescript
// tests/e2e/user-management.spec.ts
import { test, expect } from '@playwright/test';

test.describe('User Management', () => {
  test('should complete user registration flow', async ({ page }) => {
    // 1. 登録ページへ移動
    await page.goto('/register');

    // 2. ユーザー情報入力
    await page.fill('[data-testid=name-input]', 'Test User');
    await page.fill('[data-testid=email-input]', 'test@example.com');
    await page.fill('[data-testid=password-input]', 'password123');

    // 3. 登録ボタンクリック
    await page.click('[data-testid=register-button]');

    // 4. 成功メッセージ確認
    await expect(page.locator('[data-testid=success-message]'))
      .toContainText('Registration successful');

    // 5. ダッシュボードへリダイレクト確認
    await expect(page).toHaveURL('/dashboard');
  });

  test('should handle registration with existing email', async ({ page }) => {
    // 事前にユーザーを作成
    await createTestUser('existing@example.com');

    await page.goto('/register');
    await page.fill('[data-testid=name-input]', 'Another User');
    await page.fill('[data-testid=email-input]', 'existing@example.com');
    await page.fill('[data-testid=password-input]', 'password123');
    await page.click('[data-testid=register-button]');

    // エラーメッセージ確認
    await expect(page.locator('[data-testid=error-message]'))
      .toContainText('Email already exists');
  });
});
```

### 4. 継続的品質管理

#### 4.1 コード品質チェック
```bash
# 静的解析実行
npm run lint
npm run type-check

# テストカバレッジ確認
npm run test:coverage

# セキュリティ監査
npm audit
```

#### 4.2 品質メトリクス監視
| メトリクス | 目標値 | 現在値 | ステータス |
|------------|--------|--------|------------|
| 行カバレッジ | 90%以上 | 92% | ✅ |
| 分岐カバレッジ | 85%以上 | 87% | ✅ |
| 関数カバレッジ | 90%以上 | 94% | ✅ |
| ESLintエラー | 0件 | 0件 | ✅ |
| TypeScriptエラー | 0件 | 0件 | ✅ |

### 5. STEP 5・7整合性チェック

#### 5.1 計画vs実績確認
| 項目 | 計画 | 実績 | 差異 | 対応 |
|------|------|------|------|------|
| 実装ファイル数 | 15ファイル | 15ファイル | 0 | - |
| 単体テスト数 | 45ケース | 47ケース | +2 | 追加テストケース |
| 開発期間 | 4週間 | 4週間 | 0 | - |
| 品質目標達成 | 90%以上 | 92% | +2% | 目標超過達成 |

#### 5.2 品質ゲート通過確認
- [ ] Phase 1品質ゲート: 単体テスト90%以上 → 92%達成 ✅
- [ ] Phase 2品質ゲート: 結合テスト100% → 100%達成 ✅
- [ ] Phase 3品質ゲート: E2Eテスト全シナリオ通過 → 100%達成 ✅
- [ ] 最終品質ゲート: 全品質基準クリア → 達成 ✅

## チェックリスト

- [ ] Phase 1実装が完了している
- [ ] 単体テストが90%以上のカバレッジを達成している
- [ ] Phase 2実装が完了している
- [ ] 結合テストが100%通過している
- [ ] Phase 3実装が完了している
- [ ] E2Eテストが全シナリオ通過している
- [ ] STEP 5・7整合性が確認されている
- [ ] 全品質ゲートを通過している
- [ ] コード品質基準を満たしている

## 次STEP移行条件

- 全実装が完了している
- 全テストが通過している
- 品質基準を満たしている
- STEP 5との整合性が確認されている
- `@workflows/continuous-improvement.md`での振り返り準備完了
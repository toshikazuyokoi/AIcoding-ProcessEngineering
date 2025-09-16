# TSK-XXX タスク仕様書

## メタデータ
| 項目 | 内容 |
|------|------|
| ドキュメントID | SPEC-TSK-XXX |
| タスクID | TSK-XXX-[レイヤー]-[ファイル名] |
| バージョン | 1.0 |
| 作成日 | YYYY-MM-DD |
| 最終更新日 | YYYY-MM-DD |
| ステータス | ドラフト/レビュー中/承認済み |
| 作成者 | [作成者名] |
| レビュー者 | [レビュー者名] |
| 承認者 | [承認者名] |
| 関連文書 | CLASS-001 (クラス設計表) |
| 変更履歴 | 1.0: 初版作成 (YYYY-MM-DD) |

## 1. タスク概要

### 1.1 基本情報
| 項目 | 内容 |
|------|------|
| 実装対象 | [クラス名] エンティティクラス |
| ファイルパス | src/[レイヤー]/[ファイル名].ts |
| 責任 | [責任の説明] |
| 見積時間 | Xh |

### 1.2 実装仕様
#### クラス定義
```typescript
export class [クラス名] {
  private readonly id: [ID型];
  private name: [Name型];
  private createdAt: Date;
  private updatedAt: Date;

  constructor(
    id: [ID型],
    name: [Name型]
  ) {
    this.id = id;
    this.name = name;
    this.createdAt = new Date();
    this.updatedAt = new Date();
  }

  // ゲッター・セッター
  getId(): [ID型] { return this.id; }
  getName(): [Name型] { return this.name; }
  
  // ビジネスロジック
  updateName(name: [Name型]): void;
  isActive(): boolean;
}
```

#### 値オブジェクト
```typescript
export class [ID型] {
  constructor(private readonly value: string) {
    if (!value || value.length === 0) {
      throw new Error('[ID型] cannot be empty');
    }
  }
  
  getValue(): string { return this.value; }
  equals(other: [ID型]): boolean { return this.value === other.value; }
}

export class [Name型] {
  constructor(private readonly value: string) {
    if (!value || value.length < 2 || value.length > 50) {
      throw new Error('[Name型] must be between 2 and 50 characters');
    }
  }
  
  getValue(): string { return this.value; }
}
```

## 2. テスト要件

### 2.1 テストケース一覧
| テストケースID | テスト観点 | 入力 | 期待結果 |
|----------------|------------|------|----------|
| TC-001 | 正常系 - オブジェクト作成 | 有効な値 | オブジェクト作成成功 |
| TC-002 | 異常系 - 無効なID | 空文字 | エラー発生 |
| TC-003 | 異常系 - 無効な名前 | 1文字 | エラー発生 |
| TC-004 | 境界値 - 名前最小値 | 2文字 | 正常作成 |
| TC-005 | 境界値 - 名前最大値 | 50文字 | 正常作成 |

### 2.2 テスト実装例
```typescript
describe('[クラス名]', () => {
  describe('constructor', () => {
    it('should create object with valid parameters', () => {
      // Arrange
      const id = new [ID型]('[テストID]');
      const name = new [Name型]('[テスト名]');

      // Act
      const obj = new [クラス名](id, name);

      // Assert
      expect(obj.getId()).toEqual(id);
      expect(obj.getName()).toEqual(name);
    });
  });

  describe('updateName', () => {
    it('should update name successfully', () => {
      // Arrange
      const obj = createTestObject();
      const newName = new [Name型]('[新しい名前]');

      // Act
      obj.updateName(newName);

      // Assert
      expect(obj.getName()).toEqual(newName);
    });
  });
});
```

## 3. 実装チェックリスト

### 3.1 設計準拠
- [ ] ドメイン駆動設計の原則に従っている
- [ ] 不変条件が適切に保護されている
- [ ] 値オブジェクトが適切に実装されている
- [ ] ビジネスルールがエンティティに含まれている

### 3.2 コード品質
- [ ] TypeScript型定義が適切
- [ ] エラーハンドリングが実装されている
- [ ] 命名規約に準拠している
- [ ] コメントが適切に記述されている

### 3.3 テスト品質
- [ ] 単体テストカバレッジ90%以上
- [ ] 正常系・異常系・境界値テストを網羅
- [ ] テストコードが保守しやすい
- [ ] モックが適切に使用されている

## 4. 完了確認
- [ ] 全メソッドの実装完了
- [ ] 単体テスト実装完了
- [ ] テストカバレッジ90%以上達成
- [ ] コーディング規約準拠
- [ ] レビュー完了
- [ ] ドキュメント更新完了

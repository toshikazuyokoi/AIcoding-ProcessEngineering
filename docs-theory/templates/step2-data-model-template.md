# データモデル設計書（エンティティ定義書）

## メタデータ
| 項目 | 内容 |
|------|------|
| 文書ID | ENT-001 |
| 関連文書 | REQ-001 (要求仕様書)<br>UC-001 (ユースケース一覧)<br>ARCH-001 (システム構成図)<br>UI-001 (UI構成定義書) |
| 作成日 | YYYY-MM-DD |
| 最終更新日 | YYYY-MM-DD |
| 作成者 | [データアーキテクト名] |
| 承認者 | [システムアーキテクト名] |
| バージョン | 1.0 |
| ステータス | ドラフト |

## 1. データモデル概要

### 1.1 設計方針
| 項目 | 方針 |
|------|------|
| 正規化レベル | [第3正規形 / BCNF / 非正規化] |
| 主キー戦略 | [UUID / 自然キー / 代理キー] |
| 外部キー制約 | [厳密 / 緩和 / アプリケーション制御] |
| 論理削除 | [使用する / 使用しない] |
| 監査ログ | [全テーブル / 重要テーブルのみ / なし] |

### 1.2 データベース技術仕様
| 項目 | 仕様 |
|------|------|
| DBMS | [PostgreSQL / MySQL / Oracle / SQL Server] |
| バージョン | [具体的バージョン] |
| 文字コード | [UTF-8 / UTF-16] |
| 照合順序 | [具体的照合順序] |
| タイムゾーン | [UTC / ローカル] |

## 2. エンティティ一覧

### 2.1 エンティティ分類
| 分類 | 説明 | エンティティ数 |
|------|------|--------------|
| マスターエンティティ | 基本情報・設定情報 | [数] |
| トランザクションエンティティ | 業務データ・履歴データ | [数] |
| 関連エンティティ | 多対多関連の中間テーブル | [数] |
| システムエンティティ | ログ・監査・設定 | [数] |

### 2.2 エンティティ一覧表
| エンティティID | エンティティ名 | 論理名 | 分類 | 主要属性数 | 関連数 |
|----------------|----------------|--------|------|------------|--------|
| E-001 | [Entity1] | [論理名1] | マスター | [数] | [数] |
| E-002 | [Entity2] | [論理名2] | トランザクション | [数] | [数] |
| E-003 | [Entity3] | [論理名3] | 関連 | [数] | [数] |

## 3. エンティティ詳細定義

### 3.1 E-001: [エンティティ名]
**概要**: [エンティティの概要説明]
**分類**: [マスター/トランザクション/関連/システム]
**用途**: [主な用途・目的]

#### 3.1.1 属性定義
| 属性名 | 論理名 | 型 | 長さ | NULL | デフォルト | 説明 |
|--------|--------|----|----- |------|-----------|------|
| id | [論理名] | UUID | - | NOT NULL | uuid_generate_v4() | 主キー |
| [attribute1] | [論理名1] | VARCHAR | [長さ] | [NULL/NOT NULL] | [デフォルト値] | [説明1] |
| [attribute2] | [論理名2] | INTEGER | - | [NULL/NOT NULL] | [デフォルト値] | [説明2] |
| created_at | 作成日時 | TIMESTAMP | - | NOT NULL | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | 更新日時 | TIMESTAMP | - | NOT NULL | CURRENT_TIMESTAMP | 更新日時 |

#### 3.1.2 制約条件
**主キー制約**:
- PRIMARY KEY: id

**一意制約**:
- UNIQUE: [一意制約対象属性]

**外部キー制約**:
- FOREIGN KEY: [外部キー属性] REFERENCES [参照テーブル]([参照属性])

**チェック制約**:
- CHECK: [チェック条件1]
- CHECK: [チェック条件2]

**インデックス**:
- INDEX: [インデックス対象属性] (検索性能向上)
- UNIQUE INDEX: [一意インデックス対象属性]

#### 3.1.3 ビジネスルール
| ルールID | ルール内容 | 実装方法 |
|----------|------------|----------|
| BR-001 | [ビジネスルール1] | [DB制約/アプリケーション制御] |
| BR-002 | [ビジネスルール2] | [DB制約/アプリケーション制御] |

### 3.2 E-002: [エンティティ名2]
**概要**: [エンティティの概要説明]
**分類**: [マスター/トランザクション/関連/システム]
**用途**: [主な用途・目的]

#### 3.2.1 属性定義
| 属性名 | 論理名 | 型 | 長さ | NULL | デフォルト | 説明 |
|--------|--------|----|----- |------|-----------|------|
| id | [論理名] | UUID | - | NOT NULL | uuid_generate_v4() | 主キー |
| [foreign_key_id] | [外部キー論理名] | UUID | - | NOT NULL | - | 外部キー |
| [attribute1] | [論理名1] | VARCHAR | [長さ] | [NULL/NOT NULL] | [デフォルト値] | [説明1] |
| created_at | 作成日時 | TIMESTAMP | - | NOT NULL | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | 更新日時 | TIMESTAMP | - | NOT NULL | CURRENT_TIMESTAMP | 更新日時 |

#### 3.2.2 制約条件
**主キー制約**:
- PRIMARY KEY: id

**外部キー制約**:
- FOREIGN KEY: [foreign_key_id] REFERENCES [参照テーブル](id) ON DELETE [CASCADE/RESTRICT/SET NULL]

**チェック制約**:
- CHECK: [チェック条件]

## 4. エンティティ関連図（ER図）

### 4.1 全体ER図
````mermaid
erDiagram
    Entity1 {
        uuid id PK
        varchar attribute1
        integer attribute2
        timestamp created_at
        timestamp updated_at
    }
    
    Entity2 {
        uuid id PK
        uuid entity1_id FK
        varchar attribute1
        enum status
        timestamp created_at
        timestamp updated_at
    }
    
    Entity3 {
        uuid id PK
        varchar name UK
        text description
        timestamp created_at
    }
    
    RelationEntity {
        uuid entity2_id FK
        uuid entity3_id FK
        timestamp created_at
    }
    
    Entity1 ||--o{ Entity2 : "1対多"
    Entity2 }o--o{ Entity3 : "多対多"
    Entity2 ||--o{ RelationEntity : "関連"
    Entity3 ||--o{ RelationEntity : "関連"
````

### 4.2 主要エンティティ関連図
````mermaid
erDiagram
    [MainEntity1] {
        uuid id PK
        varchar key_attribute
    }
    
    [MainEntity2] {
        uuid id PK
        uuid main_entity1_id FK
        varchar important_attribute
    }
    
    [MainEntity1] ||--o{ [MainEntity2] : "主要関連"
````

## 5. データ型・制約定義

### 5.1 カスタムデータ型定義
```sql
-- ENUM型定義
CREATE TYPE [enum_name] AS ENUM ('[value1]', '[value2]', '[value3]');

-- 複合型定義（必要に応じて）
CREATE TYPE [composite_type] AS (
    [field1] [type1],
    [field2] [type2]
);
```

### 5.2 共通制約パターン
| 制約パターン | 定義 | 適用対象 |
|-------------|------|----------|
| メールアドレス | CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$') | email属性 |
| 正の整数 | CHECK ([column] > 0) | 数量・金額属性 |
| 日付範囲 | CHECK ([end_date] >= [start_date]) | 期間属性 |
| 文字列長 | CHECK (LENGTH([column]) >= [min_length]) | 文字列属性 |

### 5.3 拡張機能
```sql
-- UUID生成関数の有効化
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 全文検索機能（必要に応じて）
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 暗号化機能（必要に応じて）
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
```

## 6. データ整合性・品質管理

### 6.1 参照整合性ルール
| 関連 | 削除時動作 | 更新時動作 | 理由 |
|------|------------|------------|------|
| [Parent] → [Child] | CASCADE | CASCADE | [理由] |
| [Master] → [Transaction] | RESTRICT | CASCADE | [理由] |
| [Entity] → [Log] | SET NULL | CASCADE | [理由] |

### 6.2 データ品質ルール
| 品質ルール | 実装方法 | 検証方法 |
|------------|----------|----------|
| 必須データの完全性 | NOT NULL制約 | 定期チェック |
| データ形式の統一性 | CHECK制約・正規表現 | バリデーション |
| 参照整合性の維持 | 外部キー制約 | 整合性チェック |
| 重複データの防止 | UNIQUE制約 | 重複検出 |

### 6.3 監査・履歴管理
| 対象 | 監査方法 | 保存期間 |
|------|----------|----------|
| 重要マスターデータ | 更新履歴テーブル | [期間] |
| トランザクションデータ | 論理削除 | [期間] |
| ユーザー操作 | 操作ログテーブル | [期間] |

## 7. パフォーマンス考慮事項

### 7.1 インデックス戦略
| テーブル | インデックス対象 | 種類 | 目的 |
|----------|------------------|------|------|
| [Table1] | [column1] | B-tree | 検索性能向上 |
| [Table2] | [column1, column2] | 複合 | 複合条件検索 |
| [Table3] | [text_column] | GIN | 全文検索 |

### 7.2 パーティショニング戦略
| テーブル | パーティション方法 | 分割基準 | 目的 |
|----------|-------------------|----------|------|
| [LargeTable] | 範囲パーティション | 日付 | 性能向上・保守性 |
| [LogTable] | リストパーティション | ログレベル | 管理効率化 |

## 8. セキュリティ考慮事項

### 8.1 機密データ保護
| データ種別 | 保護方法 | 実装 |
|------------|----------|------|
| パスワード | ハッシュ化 | bcrypt/scrypt |
| 個人情報 | 暗号化 | AES-256 |
| 機密情報 | アクセス制御 | RLS (Row Level Security) |

### 8.2 アクセス制御
| ロール | 権限 | 対象テーブル |
|--------|------|-------------|
| [app_user] | SELECT, INSERT, UPDATE | [業務テーブル] |
| [app_admin] | ALL | [全テーブル] |
| [readonly] | SELECT | [参照用ビュー] |

## 9. 完了確認チェックリスト
- [ ] 全エンティティが要求仕様書の要件を満たしている
- [ ] ER図が論理的に整合している
- [ ] 制約条件が適切に定義されている
- [ ] インデックス戦略が検討されている
- [ ] セキュリティ要件が考慮されている
- [ ] パフォーマンス要件が考慮されている
- [ ] データ整合性ルールが定義されている
- [ ] 監査・履歴管理方針が決定されている
- [ ] 関連文書との整合性が確認されている
- [ ] 次工程（STEP 3: 詳細設計）への引き継ぎ情報が整理されている

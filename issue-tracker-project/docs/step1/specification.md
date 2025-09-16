# 要求仕様書 - Issue Tracking System

## メタデータ

- ドキュメントID: DOC-REQ-003
- 作成日: 2025-09-15
- 作成者: GitHub Copilot
- プロジェクト: Issue Tracking System MVP
- バージョン: 1.0
- 関連文書: use-cases.md, non-functional.md, goal-statement.md

## 1. 機能要件仕様

### 1.1 ユーザー管理機能

#### FR-001: ユーザー登録

**仕様詳細**:

- **入力項目**: ユーザー名（3-20文字、英数字）、メールアドレス、パスワード（8-50文字）
- **バリデーション**: メール形式チェック、ユーザー名・メール重複チェック
- **出力**: 登録成功・失敗メッセージ、ログイン画面へのリダイレクト
- **データベース影響**: Usersテーブルへのレコード追加

```sql
-- Users テーブル構造
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### FR-002: ユーザー認証

**仕様詳細**:

- **入力項目**: ユーザー名またはメール、パスワード
- **認証処理**: bcryptによるパスワードハッシュ検証
- **セッション管理**: 30分間のセッション維持、自動延長
- **出力**: 認証成功時にダッシュボードリダイレクト、失敗時にエラー表示

#### FR-003: ログアウト

**仕様詳細**:

- **処理内容**: セッション破棄、認証状態クリア
- **出力**: ログイン画面へのリダイレクト

### 1.2 プロジェクト管理機能

#### FR-004: プロジェクト作成

**仕様詳細**:

- **入力項目**: プロジェクト名（1-100文字）、説明（0-1000文字）
- **権限**: ログインユーザーのみ作成可能
- **データベース影響**: Projectsテーブルへのレコード追加、作成者を管理者として設定

```sql
-- Projects テーブル構造
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Project Members テーブル構造
CREATE TABLE project_members (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    user_id INTEGER REFERENCES users(id),
    role VARCHAR(20) DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### FR-005: プロジェクト一覧表示

**仕様詳細**:

- **表示内容**: ユーザーが参加するプロジェクト一覧
- **ソート**: 作成日降順
- **ページング**: 20プロジェクト/ページ
- **表示項目**: プロジェクト名、説明（50文字まで）、作成者、参加日

### 1.3 チケット管理機能

#### FR-006: チケット作成

**仕様詳細**:

- **入力項目**: タイトル（1-200文字）、説明（0-5000文字）、優先度、担当者
- **デフォルト値**: 状態=新規、作成者=ログインユーザー、優先度=中
- **バリデーション**: タイトル必須、担当者はプロジェクトメンバーのみ

```sql
-- Issues テーブル構造
CREATE TABLE issues (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'open',
    priority VARCHAR(20) DEFAULT 'medium',
    created_by INTEGER REFERENCES users(id),
    assigned_to INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### FR-007: チケット一覧表示

**仕様詳細**:

- **表示範囲**: 選択プロジェクト内のチケット
- **デフォルトソート**: 更新日降順
- **フィルター**: 状態、優先度、担当者（MVP後）
- **ページング**: 50チケット/ページ
- **表示項目**: ID、タイトル、状態、優先度、担当者、更新日

#### FR-008: チケット詳細表示

**仕様詳細**:

- **表示内容**: 全チケット情報、作成・更新履歴
- **アクション**: 編集、状態変更、削除（権限に応じて）
- **履歴表示**: 変更履歴の時系列表示

#### FR-009: チケット編集

**仕様詳細**:

- **編集権限**: 作成者、担当者、プロジェクト管理者
- **編集項目**: タイトル、説明、優先度、担当者
- **変更履歴**: 編集内容の自動記録

#### FR-010: チケット状態変更

**仕様詳細**:

- **状態遷移**: 新規 → 進行中 → 完了 → クローズ
- **権限**: 担当者、作成者、プロジェクト管理者
- **制約**: 逆向き遷移も可能（再オープンなど）

```sql
-- Issue History テーブル構造
CREATE TABLE issue_history (
    id SERIAL PRIMARY KEY,
    issue_id INTEGER REFERENCES issues(id),
    field_name VARCHAR(50),
    old_value TEXT,
    new_value TEXT,
    changed_by INTEGER REFERENCES users(id),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 2. インターフェース要件

### 2.1 ユーザーインターフェース

#### UI-001: レイアウト基本設計

**仕様**:

- **フレームワーク**: Bootstrap 5を使用したレスポンシブデザイン
- **ナビゲーション**: 上部固定ナビゲーションバー
- **メニュー構成**: ダッシュボード、プロジェクト、チケット、プロファイル
- **カラーテーマ**: 青基調のモダンなUI

#### UI-002: ページ構成

| ページ | URL | 主要要素 |
|--------|-----|----------|
| ログイン | `/login` | ログインフォーム、新規登録リンク |
| ダッシュボード | `/dashboard` | 最近のチケット、プロジェクト概要 |
| プロジェクト一覧 | `/projects` | プロジェクトカード一覧、新規作成ボタン |
| プロジェクト詳細 | `/projects/{id}` | チケット一覧、プロジェクト情報 |
| チケット詳細 | `/issues/{id}` | チケット情報、編集フォーム |
| チケット作成 | `/issues/new` | チケット作成フォーム |

### 2.2 API仕様（Phase 2）

#### API-001: RESTful API基本設計

**エンドポイント設計**:

```
GET    /api/v1/projects           # プロジェクト一覧
POST   /api/v1/projects           # プロジェクト作成
GET    /api/v1/projects/{id}      # プロジェクト詳細
PUT    /api/v1/projects/{id}      # プロジェクト更新

GET    /api/v1/projects/{id}/issues     # チケット一覧
POST   /api/v1/projects/{id}/issues     # チケット作成
GET    /api/v1/issues/{id}              # チケット詳細
PUT    /api/v1/issues/{id}              # チケット更新
DELETE /api/v1/issues/{id}              # チケット削除
```

### 2.3 データベースインターフェース

#### DB-001: データベース接続

**仕様**:

- **開発環境**: SQLite 3.x
- **本番環境**: PostgreSQL 12+
- **ORM**: Django ORM使用
- **マイグレーション**: Django migrations使用

## 3. システム要件

### 3.1 技術アーキテクチャ

#### ARCH-001: 基本アーキテクチャ

**技術スタック**:

- **Backend**: Python 3.9+, Django 4.2+
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript (Vanilla)
- **Database**: SQLite (開発), PostgreSQL (本番)
- **Web Server**: Django development server (開発), Gunicorn (本番)

#### ARCH-002: ディレクトリ構造

```
issue-tracker/
├── manage.py
├── requirements.txt
├── issue_tracker/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── users/
│   ├── projects/
│   └── issues/
├── templates/
├── static/
├── tests/
└── docs/
```

### 3.2 セキュリティアーキテクチャ

#### SEC-001: 認証・認可

**実装方針**:

- **認証方式**: Django標準のセッション認証
- **パスワード**: bcryptハッシュ化
- **CSRF**: Django標準のCSRF保護
- **XSS**: Djangoテンプレートの自動エスケープ

#### SEC-002: データ保護

**実装方針**:

- **SQL Injection**: Django ORMのパラメータ化クエリ
- **セッション**: セキュアCookie、HTTPOnly設定
- **HTTPS**: 本番環境での強制HTTPS

## 4. 品質要件

### 4.1 テスト要件

#### TEST-001: テスト戦略

**テストレベル**:

- **単体テスト**: 全モデル・ビュー・フォームのテスト
- **統合テスト**: API・データベース連携テスト
- **機能テスト**: ユーザーシナリオベースのE2Eテスト

**カバレッジ目標**: 80%以上

#### TEST-002: テスト実装

**テストフレームワーク**:

- **Backend**: Django TestCase, pytest
- **Frontend**: Selenium WebDriver
- **API**: Django REST Framework test client

### 4.2 パフォーマンス要件

#### PERF-001: 応答性能

**目標値**:

- **ページ読み込み**: 3秒以内
- **CRUD操作**: 1秒以内
- **検索処理**: 2秒以内

#### PERF-002: 最適化手法

**実装方針**:

- **データベース**: 適切なインデックス設定
- **クエリ**: N+1問題の回避
- **静的ファイル**: CSS/JS最小化

## 5. 運用要件

### 5.1 デプロイメント

#### DEPLOY-001: デプロイメント戦略

**環境構成**:

- **開発環境**: ローカル開発サーバー
- **ステージング**: 本番類似環境でのテスト
- **本番環境**: クラウドまたはVPS上での運用

#### DEPLOY-002: 設定管理

**実装方針**:

- **環境変数**: 機密情報の外部化
- **設定ファイル**: 環境別設定の分離
- **デプロイメント**: 手動デプロイ（CI/CDはPhase2）

### 5.2 監視・ログ

#### LOG-001: ログ出力

**ログレベル**:

- **ERROR**: システムエラー、例外
- **WARNING**: 注意が必要な状況
- **INFO**: 重要な処理結果
- **DEBUG**: 開発時の詳細情報

## 6. 制約・前提条件

### 6.1 技術制約

- Python 3.9以上必須
- Django 4.2以上使用
- SQLite（開発）/ PostgreSQL（本番）
- ブラウザ：Chrome/Firefox/Edge最新版対応

### 6.2 運用制約

- 初期ユーザー数：50名以下
- 初期データ量：1,000チケット以下
- 稼働時間：平日9:00-18:00
- 保守時間：土日祝日メンテナンス可

## 7. 受け入れ基準

### 7.1 機能受け入れ基準

- [ ] 全ユースケースが正常に動作する
- [ ] 非機能要件の目標値を満たす
- [ ] セキュリティテストに合格する
- [ ] ユーザビリティテストに合格する

### 7.2 品質受け入れ基準

- [ ] 単体テストカバレッジ80%以上
- [ ] 静的解析エラー0件
- [ ] パフォーマンステスト合格
- [ ] セキュリティスキャン合格

## 完了確認チェックリスト

- [x] 全機能要件が詳細に定義されている
- [x] インターフェース要件が明確に規定されている
- [x] システム要件・技術要件が具体的である
- [x] 品質要件が測定可能な形で定義されている
- [x] 運用要件が現実的に設定されている
- [x] 制約・前提条件が明確である
- [x] 受け入れ基準が具体的に定義されている
- [x] データベーススキーマが設計されている
- [x] ユースケースとの整合性が確保されている

## 次のアクション

1. STEP1品質ゲート（要件完全性チェック）の実行
2. ステークホルダーレビューと要件承認
3. STEP2（システム設計）への移行準備
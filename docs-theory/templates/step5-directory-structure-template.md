# ディレクトリ構造マップ

## メタデータ
| 項目 | 内容 |
|------|------|
| ドキュメントID | DIR-001 |
| バージョン | 1.0 |
| 作成日 | YYYY-MM-DD |
| 最終更新日 | YYYY-MM-DD |
| ステータス | ドラフト/レビュー中/承認済み |
| 作成者 | [作成者名] |
| レビュー者 | [レビュー者名] |
| 承認者 | [承認者名] |
| 関連文書 | TECH-001 (技術スタック選定書), COMP-001 (実装コンポーネント一覧) |
| 変更履歴 | 1.0: 初版作成 (YYYY-MM-DD) |

## 1. プロジェクト全体構造

```
project-root/
├── README.md                          # プロジェクト概要
├── package.json                       # 依存関係定義
├── tsconfig.json                       # TypeScript設定
├── .env.example                        # 環境変数テンプレート
├── docker-compose.yml                 # 開発環境定義
├── .github/                           # GitHub設定
│   └── workflows/                     # CI/CDワークフロー
│       ├── test.yml                   # テスト実行
│       ├── build.yml                  # ビルド・デプロイ
│       └── security.yml               # セキュリティスキャン
├── docs/                              # プロジェクト文書
│   ├── api/                           # API仕様書
│   ├── architecture/                  # アーキテクチャ文書
│   └── deployment/                    # デプロイメント手順
├── src/                               # ソースコード
│   ├── presentation/                  # プレゼンテーション層
│   │   ├── controllers/               # REST APIコントローラ
│   │   ├── dto/                       # データ転送オブジェクト
│   │   │   ├── request/               # リクエストDTO
│   │   │   └── response/              # レスポンスDTO
│   │   ├── middleware/                # ミドルウェア
│   │   └── validators/                # 入力値検証
│   ├── application/                   # アプリケーション層
│   │   ├── services/                  # ビジネスロジック
│   │   ├── usecases/                  # ユースケース実装
│   │   └── interfaces/                # アプリケーションインターフェース
│   ├── domain/                        # ドメイン層
│   │   ├── entities/                  # エンティティ
│   │   ├── repositories/              # リポジトリインターフェース
│   │   ├── services/                  # ドメインサービス
│   │   └── value-objects/             # 値オブジェクト
│   ├── infrastructure/                # インフラ層
│   │   ├── database/                  # データベース実装
│   │   │   ├── repositories/          # リポジトリ実装
│   │   │   ├── migrations/            # マイグレーション
│   │   │   └── seeds/                 # シードデータ
│   │   ├── external/                  # 外部API連携
│   │   ├── config/                    # 設定管理
│   │   └── logging/                   # ログ管理
│   ├── shared/                        # 共通モジュール
│   │   ├── constants/                 # 定数定義
│   │   ├── enums/                     # 列挙型
│   │   ├── types/                     # 型定義
│   │   ├── utils/                     # ユーティリティ
│   │   └── exceptions/                # 例外クラス
│   └── main.ts                        # アプリケーションエントリポイント
├── tests/                             # テストコード
│   ├── unit/                          # 単体テスト
│   │   ├── controllers/               # コントローラテスト
│   │   ├── services/                  # サービステスト
│   │   ├── repositories/              # リポジトリテスト
│   │   └── utils/                     # ユーティリティテスト
│   ├── integration/                   # 結合テスト
│   │   ├── api/                       # API結合テスト
│   │   ├── database/                  # DB結合テスト
│   │   └── external/                  # 外部連携テスト
│   ├── e2e/                           # E2Eテスト
│   │   ├── scenarios/                 # テストシナリオ
│   │   ├── fixtures/                  # テストデータ
│   │   └── helpers/                   # テストヘルパー
│   └── performance/                   # パフォーマンステスト
├── scripts/                           # 運用スクリプト
│   ├── build.sh                       # ビルドスクリプト
│   ├── deploy.sh                      # デプロイスクリプト
│   ├── backup.sh                      # バックアップスクリプト
│   └── migration.sh                   # マイグレーションスクリプト
└── dist/                              # ビルド成果物（Git管理外）
```

## 2. 命名規則

### 2.1 ファイル命名規則
| 種別 | 規則 | 例 |
|------|------|-----|
| クラス | PascalCase + サフィックス | UserController.ts |
| インターフェース | I + PascalCase | IUserRepository.ts |
| DTO | PascalCase + Request/Response | UserCreateRequest.ts |
| テスト | 対象ファイル名 + .spec.ts | UserService.spec.ts |
| 設定 | kebab-case | database.config.ts |

### 2.2 ディレクトリ命名規則
| 種別 | 規則 | 例 |
|------|------|-----|
| 複数単語 | kebab-case | detailed-design |
| 単数形 | エンティティ関連 | entity, service |
| 複数形 | 集合を表すもの | controllers, repositories |

### 2.3 パッケージ構造
| パッケージ | 目的 | 命名規則 |
|------------|------|----------|
| @/presentation | プレゼンテーション層 | PascalCase |
| @/application | アプリケーション層 | PascalCase |
| @/domain | ドメイン層 | PascalCase |
| @/infrastructure | インフラ層 | PascalCase |
| @/shared | 共通モジュール | PascalCase |

## 3. インポート規則

### 3.1 インポート順序
```typescript
// 1. 外部ライブラリ（Node.js標準 → サードパーティ）
import { Controller, Get, Post, Body } from '@nestjs/common';
import { Repository } from 'typeorm';
import express from 'express';

// 2. 内部モジュール（相対パス禁止、絶対パス使用）
import { UserService } from '@/application/services/UserService';
import { User } from '@/domain/entities/User';
import { IUserRepository } from '@/domain/repositories/IUserRepository';

// 3. 型定義（type-only import）
import type { UserCreateRequest } from '@/presentation/dto/request/UserCreateRequest';
import type { UserResponse } from '@/presentation/dto/response/UserResponse';

// 4. 設定・定数
import { DATABASE_CONFIG } from '@/infrastructure/config/database.config';
import { HTTP_STATUS } from '@/shared/constants/http-status';
```

### 3.2 パスエイリアス設定
```json
{
  "compilerOptions": {
    "baseUrl": "./src",
    "paths": {
      "@/*": ["*"],
      "@/presentation/*": ["presentation/*"],
      "@/application/*": ["application/*"],
      "@/domain/*": ["domain/*"],
      "@/infrastructure/*": ["infrastructure/*"],
      "@/shared/*": ["shared/*"],
      "@/tests/*": ["../tests/*"]
    }
  }
}
```

## 4. 完了確認
- [ ] ディレクトリ構造が適切に設計されている
- [ ] 命名規則が統一されている
- [ ] インポート規則が明確に定義されている
- [ ] パスエイリアスが適切に設定されている

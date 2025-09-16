# レイヤー構成マップ

## メタデータ
| 項目 | 内容 |
|------|------|
| 文書ID | LAYER-001 |
| 関連文書 | ARCH-001 (システム構成図)<br>TECH-001 (技術選定・依存関係定義書)<br>ENT-001 (エンティティ定義書)<br>UI-001 (UI構成定義書) |
| 作成日 | YYYY-MM-DD |
| 最終更新日 | YYYY-MM-DD |
| 作成者 | [ソフトウェアアーキテクト名] |
| 承認者 | [テクニカルリード名] |
| バージョン | 1.0 |
| ステータス | ドラフト |

## 1. レイヤー構成概要

### 1.1 アーキテクチャパターン
| 項目 | 内容 |
|------|------|
| アーキテクチャパターン | [レイヤードアーキテクチャ / ヘキサゴナルアーキテクチャ / クリーンアーキテクチャ] |
| レイヤー数 | [3層 / 4層 / 5層] |
| 依存方向 | [上位→下位の単方向 / 双方向] |
| 横断的関心事 | [AOP / Middleware / 専用レイヤー] |

### 1.2 レイヤー一覧
| レイヤーID | レイヤー名 | 英語名 | 順序 | 主要責任 |
|------------|------------|--------|------|----------|
| L-001 | プレゼンテーション層 | Presentation Layer | 1 | UI表示・ユーザー操作 |
| L-002 | アプリケーション層 | Application Layer | 2 | HTTP処理・制御・調整 |
| L-003 | ドメイン層 | Domain Layer | 3 | ビジネスロジック・業務ルール |
| L-004 | インフラストラクチャ層 | Infrastructure Layer | 4 | データ永続化・外部連携 |

## 2. レイヤー詳細定義

### 2.1 L-001: プレゼンテーション層（Presentation Layer）

#### 2.1.1 基本情報
| 項目 | 内容 |
|------|------|
| **主要責任** | ユーザーインターフェースの提供、ユーザー操作の受付、画面表示制御 |
| **技術スタック** | [React + TypeScript / Vue.js / Angular] |
| **配置場所** | [frontend/ / src/presentation/] |
| **依存先** | アプリケーション層（L-002） |
| **依存元** | なし（最上位層） |

#### 2.1.2 含まれるコンポーネント
| コンポーネント種別 | 説明 | 例 |
|-------------------|------|-----|
| **UIコンポーネント** | 画面表示・ユーザー操作 | LoginForm, TaskList, Dashboard |
| **ページコンポーネント** | 画面全体の構成 | LoginPage, TasksPage, ProfilePage |
| **レイアウトコンポーネント** | 共通レイアウト | Header, Sidebar, Footer |
| **ルーティング** | 画面遷移制御 | AppRouter, PrivateRoute |
| **状態管理** | UI状態・グローバル状態 | Redux Store, Context API |

#### 2.1.3 責任範囲
**含むもの**:
- ユーザー入力の受付・バリデーション（フォーマット）
- 画面表示・レンダリング
- ユーザー操作イベントの処理
- 画面遷移制御
- UI状態管理

**含まないもの**:
- ビジネスロジック
- データ永続化
- 外部API呼び出し（直接）
- 業務ルールの実装

#### 2.1.4 インターフェース定義
**上位層への提供**:
- なし（最上位層）

**下位層への要求**:
```typescript
// アプリケーション層への要求例
interface ApplicationLayerInterface {
  // 認証関連
  login(credentials: LoginRequest): Promise<AuthResponse>;
  logout(): Promise<void>;
  
  // 業務機能
  getTasks(filter: TaskFilter): Promise<Task[]>;
  createTask(task: CreateTaskRequest): Promise<Task>;
  updateTask(id: string, task: UpdateTaskRequest): Promise<Task>;
  deleteTask(id: string): Promise<void>;
}
```

### 2.2 L-002: アプリケーション層（Application Layer）

#### 2.2.1 基本情報
| 項目 | 内容 |
|------|------|
| **主要責任** | HTTP処理、認証・認可、入力検証、レスポンス生成、トランザクション制御 |
| **技術スタック** | [Express + TypeScript / Fastify / Koa] |
| **配置場所** | [backend/src/application/ / src/controllers/] |
| **依存先** | ドメイン層（L-003） |
| **依存元** | プレゼンテーション層（L-001） |

#### 2.2.2 含まれるコンポーネント
| コンポーネント種別 | 説明 | 例 |
|-------------------|------|-----|
| **コントローラー** | HTTPリクエスト処理 | UserController, TaskController |
| **ミドルウェア** | 横断的関心事 | AuthMiddleware, ValidationMiddleware |
| **DTOクラス** | データ転送オブジェクト | CreateTaskDTO, UserResponseDTO |
| **バリデーター** | 入力検証 | TaskValidator, UserValidator |
| **ルーター** | エンドポイント定義 | UserRoutes, TaskRoutes |

#### 2.2.3 責任範囲
**含むもの**:
- HTTPリクエスト・レスポンス処理
- 認証・認可の実行
- 入力データの検証・変換
- ドメイン層の調整・組み合わせ
- トランザクション境界の制御
- エラーハンドリング・ログ出力

**含まないもの**:
- ビジネスロジックの実装
- データ永続化の詳細
- UI表示ロジック
- 外部システムとの通信詳細

#### 2.2.4 インターフェース定義
**上位層への提供**:
```typescript
// プレゼンテーション層への提供例
interface PresentationLayerInterface {
  // REST API エンドポイント
  'POST /api/auth/login': (req: LoginRequest) => Promise<AuthResponse>;
  'GET /api/tasks': (req: GetTasksRequest) => Promise<TaskListResponse>;
  'POST /api/tasks': (req: CreateTaskRequest) => Promise<TaskResponse>;
}
```

**下位層への要求**:
```typescript
// ドメイン層への要求例
interface DomainLayerInterface {
  // ユーザー管理
  userService: UserService;
  authService: AuthService;
  
  // タスク管理
  taskService: TaskService;
  categoryService: CategoryService;
}
```

### 2.3 L-003: ドメイン層（Domain Layer）

#### 2.3.1 基本情報
| 項目 | 内容 |
|------|------|
| **主要責任** | ビジネスロジック、業務ルール、ドメインエンティティ、ビジネス不変条件 |
| **技術スタック** | [TypeScript Classes / Pure Functions] |
| **配置場所** | [backend/src/domain/ / src/services/] |
| **依存先** | インフラストラクチャ層（L-004）※インターフェースのみ |
| **依存元** | アプリケーション層（L-002） |

#### 2.3.2 含まれるコンポーネント
| コンポーネント種別 | 説明 | 例 |
|-------------------|------|-----|
| **エンティティ** | ビジネスオブジェクト | User, Task, Category |
| **値オブジェクト** | 不変の値 | Email, Password, TaskStatus |
| **ドメインサービス** | ビジネスロジック | UserService, TaskService |
| **リポジトリインターフェース** | データアクセス抽象化 | IUserRepository, ITaskRepository |
| **ドメインイベント** | ビジネスイベント | TaskCreated, UserRegistered |

#### 2.3.3 責任範囲
**含むもの**:
- ビジネスルールの実装
- ドメインエンティティの管理
- 業務不変条件の保証
- ドメイン固有の計算・判定
- ビジネスイベントの発行

**含まないもの**:
- データ永続化の実装
- 外部システムとの通信
- HTTP処理
- UI表示ロジック
- インフラストラクチャの詳細

#### 2.3.4 インターフェース定義
**上位層への提供**:
```typescript
// アプリケーション層への提供例
interface DomainLayerInterface {
  // ビジネスサービス
  userService: {
    createUser(userData: CreateUserData): Promise<User>;
    authenticateUser(email: string, password: string): Promise<AuthResult>;
  };
  
  taskService: {
    createTask(userId: string, taskData: CreateTaskData): Promise<Task>;
    updateTaskStatus(taskId: string, status: TaskStatus): Promise<Task>;
  };
}
```

**下位層への要求**:
```typescript
// インフラストラクチャ層への要求例（インターフェース）
interface InfrastructureLayerInterface {
  // リポジトリ
  userRepository: IUserRepository;
  taskRepository: ITaskRepository;
  
  // 外部サービス
  emailService: IEmailService;
  cacheService: ICacheService;
}
```

### 2.4 L-004: インフラストラクチャ層（Infrastructure Layer）

#### 2.4.1 基本情報
| 項目 | 内容 |
|------|------|
| **主要責任** | データ永続化、外部システム連携、技術的詳細の実装 |
| **技術スタック** | [PostgreSQL + Prisma / MongoDB / Redis] |
| **配置場所** | [backend/src/infrastructure/ / src/repositories/] |
| **依存先** | なし（最下位層） |
| **依存元** | ドメイン層（L-003）※依存性逆転 |

#### 2.4.2 含まれるコンポーネント
| コンポーネント種別 | 説明 | 例 |
|-------------------|------|-----|
| **リポジトリ実装** | データアクセス実装 | UserRepository, TaskRepository |
| **データベース接続** | DB接続・設定 | DatabaseConnection, PrismaClient |
| **外部API連携** | 外部サービス連携 | EmailService, NotificationService |
| **キャッシュ** | データキャッシュ | RedisCache, MemoryCache |
| **ファイルシステム** | ファイル操作 | FileStorage, ImageUpload |

#### 2.4.3 責任範囲
**含むもの**:
- データベースへのCRUD操作
- 外部APIとの通信
- ファイルシステムアクセス
- キャッシュ管理
- ログ出力の実装
- 設定管理

**含まないもの**:
- ビジネスロジック
- HTTP処理
- UI表示ロジック
- 業務ルールの判定

#### 2.4.4 インターフェース定義
**上位層への提供**:
```typescript
// ドメイン層への提供例（インターフェース実装）
class UserRepository implements IUserRepository {
  async findById(id: string): Promise<User | null>;
  async findByEmail(email: string): Promise<User | null>;
  async save(user: User): Promise<User>;
  async delete(id: string): Promise<void>;
}
```

## 3. レイヤー間依存関係

### 3.1 依存関係図
````mermaid
graph TD
    subgraph "L-001: Presentation Layer"
        UI[UI Components]
        PAGES[Pages]
        ROUTER[Router]
    end
    
    subgraph "L-002: Application Layer"
        CTRL[Controllers]
        MIDDLEWARE[Middleware]
        DTO[DTOs]
    end
    
    subgraph "L-003: Domain Layer"
        ENTITY[Entities]
        SERVICE[Domain Services]
        REPO_IF[Repository Interfaces]
    end
    
    subgraph "L-004: Infrastructure Layer"
        REPO_IMPL[Repository Implementations]
        DB[Database]
        EXTERNAL[External APIs]
    end
    
    UI --> CTRL
    PAGES --> CTRL
    ROUTER --> CTRL
    
    CTRL --> SERVICE
    MIDDLEWARE --> SERVICE
    DTO --> ENTITY
    
    SERVICE --> REPO_IF
    ENTITY --> REPO_IF
    
    REPO_IF -.-> REPO_IMPL
    REPO_IMPL --> DB
    REPO_IMPL --> EXTERNAL
````

### 3.2 依存性逆転の原則
| 関係 | 依存方向 | 実装方法 |
|------|----------|----------|
| Domain → Infrastructure | インターフェース依存 | Repository Pattern |
| Application → Domain | 直接依存 | Service Injection |
| Presentation → Application | 直接依存 | API Call |

### 3.3 禁止される依存関係
| 禁止パターン | 理由 | 代替手法 |
|-------------|------|----------|
| Infrastructure → Domain | 循環依存 | 依存性逆転 |
| Domain → Application | レイヤー逆転 | イベント駆動 |
| Infrastructure → Presentation | レイヤー飛び越し | 適切な経路 |

## 4. 横断的関心事

### 4.1 横断的関心事の分類
| 関心事 | 実装方法 | 配置レイヤー |
|--------|----------|-------------|
| **ログ出力** | Middleware / AOP | Application Layer |
| **認証・認可** | Middleware | Application Layer |
| **バリデーション** | Decorator / Middleware | Application Layer |
| **エラーハンドリング** | Global Handler | Application Layer |
| **トランザクション** | Decorator / AOP | Application Layer |
| **キャッシュ** | Decorator / Service | Infrastructure Layer |

### 4.2 実装パターン
````mermaid
graph LR
    subgraph "横断的関心事"
        LOG[ログ出力]
        AUTH[認証・認可]
        VALID[バリデーション]
        ERROR[エラーハンドリング]
    end
    
    subgraph "実装方法"
        MIDDLEWARE[Middleware]
        AOP[AOP/Decorator]
        HANDLER[Global Handler]
    end
    
    LOG --> MIDDLEWARE
    AUTH --> MIDDLEWARE
    VALID --> AOP
    ERROR --> HANDLER
````

## 5. 完了確認チェックリスト
- [ ] 全レイヤーの責任が明確に定義されている
- [ ] レイヤー間の依存関係が適切に設計されている
- [ ] 依存性逆転の原則が適用されている
- [ ] 横断的関心事が適切に分離されている
- [ ] 禁止される依存関係が存在しない
- [ ] インターフェース定義が明確である
- [ ] 技術スタックとレイヤーの対応が明確である
- [ ] 関連文書との整合性が確認されている
- [ ] 次工程（クラス設計）への引き継ぎ情報が整理されている
- [ ] アーキテクチャレビューが完了している

# STEP 3: 詳細設計ワークフロー

## 目的・スコープ

システム設計を基に、実装レベルの詳細設計を行う。クラス設計、インターフェース定義、データベース設計など、コーディングに直接必要な設計情報を作成する。

## インプット・アウトプット

**インプット**：
- システム構成図
- 技術選定・依存関係定義書

**アウトプット**：
- クラス設計表（`docs-agent/detailed-design/classes.md`）
- メソッドI/Fリスト（`docs-agent/detailed-design/interfaces.md`）

## Source Mapping
- @docs-theory/theory/ai-coding-development-process-v1.3-deliverable-flow.md § 詳細設計
- @docs-theory/theory/process-engineering-v1.3-complete-definition.md § STEP3
- @docs-theory/theory/quality-gate-detailed-specifications-v1.3.md § Design

## 具体的手順

### 1. クラス依存関係図作成
```mermaid
classDiagram
    class User {
        +string id
        +string name
        +string email
        +createTask()
        +updateProfile()
    }
    
    class Task {
        +string id
        +string title
        +string description
        +TaskStatus status
        +DateTime createdAt
        +updateStatus()
        +assignTo()
    }
    
    class TaskService {
        +createTask()
        +updateTask()
        +deleteTask()
        +getTasks()
    }
    
    User ||--o{ Task : creates
    TaskService --> Task : manages
```

### 2. クラス設計表作成
| クラス名 | 責務 | 属性 | メソッド | 依存関係 |
|----------|------|------|----------|----------|
| User | ユーザー情報管理 | id, name, email | createTask(), updateProfile() | Task |
| Task | タスク情報管理 | id, title, description, status | updateStatus(), assignTo() | User |
| TaskService | タスク業務処理 | - | createTask(), updateTask(), deleteTask() | Task, TaskRepository |

### 3. インターフェース仕様表作成
| インターフェース名 | メソッド | 引数 | 戻り値 | 例外 |
|-------------------|----------|------|--------|------|
| ITaskRepository | findById | id: string | Task \| null | RepositoryError |
| ITaskRepository | save | task: Task | Task | RepositoryError |
| ITaskRepository | delete | id: string | boolean | RepositoryError |

### 4. TypeScript形式メソッドシグネチャ
```typescript
interface ITaskService {
  createTask(userId: string, taskData: CreateTaskDto): Promise<Task>;
  updateTask(taskId: string, updateData: UpdateTaskDto): Promise<Task>;
  deleteTask(taskId: string): Promise<boolean>;
  getTasks(userId: string, filters?: TaskFilters): Promise<Task[]>;
}

interface IUserService {
  createUser(userData: CreateUserDto): Promise<User>;
  updateUser(userId: string, updateData: UpdateUserDto): Promise<User>;
  getUserById(userId: string): Promise<User | null>;
  authenticateUser(email: string, password: string): Promise<AuthResult>;
}
```

### 5. データベース詳細設計
```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 6. API設計詳細
```typescript
// REST API Endpoints
POST   /api/users          - Create user
GET    /api/users/:id      - Get user by ID
PUT    /api/users/:id      - Update user
DELETE /api/users/:id      - Delete user

POST   /api/tasks          - Create task
GET    /api/tasks          - Get tasks (with filters)
GET    /api/tasks/:id      - Get task by ID
PUT    /api/tasks/:id      - Update task
DELETE /api/tasks/:id      - Delete task
```

## チェックリスト

- [ ] クラス依存関係図が作成されている
- [ ] クラス設計表が完成している
- [ ] インターフェース仕様表が作成されている
- [ ] TypeScript形式のメソッドシグネチャが定義されている
- [ ] データベース設計が完成している
- [ ] API設計が詳細に定義されている
- [ ] Mermaid記法が正しく使用されている
- [ ] 標準テーブル形式が使用されている

## 次STEP移行条件

- 全クラス設計が完成している
- インターフェース定義が完了している
- データベース設計が確定している
- `@workflows/quality-gate-design.md`での品質確認完了
- `@workflows/step4-test-design.md`への移行準備完了
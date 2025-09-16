
# インターフェース定義書 - Issue Tracking System

## メタデータ
- ドキュメントID: INTERFACE-001
- 作成日: 2025-09-16
- 作成者: GitHub Copilot
- プロジェクト: Issue Tracking System MVP
- 関連文書: ../step3/class-design.md, ../step2/system-architecture.md

## 1. API/内部インターフェース一覧（網羅）
| API名 | メソッド | パス | 機能 | 認証 | 管理権限 |
|-------|----------|------|------|------|----------|
| CreateUser | POST | /api/users | ユーザー新規作成 | 不要 | 不要 |
| GetUser | GET | /api/users/{id} | ユーザー情報取得 | 必須 | 不要 |
| UpdateUser | PUT | /api/users/{id} | ユーザー情報更新 | 必須 | 不要 |
| ListUsers | GET | /api/users | ユーザー一覧取得 | 必須 | 管理者 |
| DeleteUser | DELETE | /api/users/{id} | ユーザー削除 | 必須 | 管理者 |
| CreateProject | POST | /api/projects | プロジェクト新規作成 | 必須 | 不要 |
| GetProject | GET | /api/projects/{id} | プロジェクト情報取得 | 必須 | 不要 |
| UpdateProject | PUT | /api/projects/{id} | プロジェクト情報更新 | 必須 | PM |
| ListProjects | GET | /api/projects | プロジェクト一覧取得 | 必須 | 不要 |
| DeleteProject | DELETE | /api/projects/{id} | プロジェクト削除 | 必須 | PM |
| AddProjectMember | POST | /api/projects/{id}/members | プロジェクト参加者追加 | 必須 | PM |
| RemoveProjectMember | DELETE | /api/projects/{id}/members/{uid} | 参加者削除 | 必須 | PM |
| ListProjectMembers | GET | /api/projects/{id}/members | 参加者一覧取得 | 必須 | 不要 |
| CreateIssue | POST | /api/issues | チケット新規作成 | 必須 | 不要 |
| GetIssue | GET | /api/issues/{id} | チケット情報取得 | 必須 | 不要 |
| UpdateIssue | PUT | /api/issues/{id} | チケット情報更新 | 必須 | 不要 |
| ListIssues | GET | /api/issues | チケット一覧取得 | 必須 | 不要 |
| DeleteIssue | DELETE | /api/issues/{id} | チケット削除 | 必須 | 不要 |
| ChangeIssueStatus | PATCH | /api/issues/{id}/status | 状態変更 | 必須 | 不要 |
| AddComment | POST | /api/issues/{id}/comments | コメント追加 | 必須 | 不要 |
| EditComment | PUT | /api/comments/{id} | コメント編集 | 必須 | 不要 |
| DeleteComment | DELETE | /api/comments/{id} | コメント削除 | 必須 | 不要 |
| ListComments | GET | /api/issues/{id}/comments | コメント一覧取得 | 必須 | 不要 |
| GetDashboard | GET | /api/dashboard | ダッシュボード表示 | 必須 | 不要 |
| GetStatistics | GET | /api/projects/{id}/stats | チケット統計表示 | 必須 | PM |
| GetNotifications | GET | /api/notifications | 通知一覧取得 | 必須 | 不要 |
| MarkNotificationRead | PATCH | /api/notifications/{id}/read | 通知既読化 | 必須 | 不要 |
| SystemSettings | GET/PUT | /api/settings | システム設定取得・更新 | 必須 | 管理者 |


## 2. API詳細設計（全インターフェース網羅・リクエスト/レスポンス定義）

### CreateUser
- メソッド: POST
- パス: /api/users
- リクエスト:
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```
- レスポンス:
```json
{
  "id": 1,
  "username": "string",
  "email": "string",
  "created_at": "2025-09-16T00:00:00Z"
}
```

### GetUser
- メソッド: GET
- パス: /api/users/{id}
- レスポンス:
```json
{
  "id": 1,
  "username": "string",
  "email": "string",
  "created_at": "2025-09-16T00:00:00Z",
  "updated_at": "2025-09-16T00:00:00Z"
}
```

### UpdateUser
- メソッド: PUT
- パス: /api/users/{id}
- リクエスト:
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```
- レスポンス:
```json
{
  "id": 1,
  "username": "string",
  "email": "string",
  "updated_at": "2025-09-16T00:00:00Z"
}
```

### ListUsers
- メソッド: GET
- パス: /api/users
- レスポンス:
```json
[
  {
    "id": 1,
    "username": "string",
    "email": "string"
  },
  ...
]
```

### DeleteUser
- メソッド: DELETE
- パス: /api/users/{id}
- レスポンス:
```json
{
  "result": "success"
}
```

### CreateProject
- メソッド: POST
- パス: /api/projects
- リクエスト:
```json
{
  "name": "string",
  "description": "string"
}
```
- レスポンス:
```json
{
  "id": 1,
  "name": "string",
  "description": "string",
  "created_by": 1,
  "created_at": "2025-09-16T00:00:00Z"
}
```

### GetProject
- メソッド: GET
- パス: /api/projects/{id}
- レスポンス:
```json
{
  "id": 1,
  "name": "string",
  "description": "string",
  "created_by": 1,
  "created_at": "2025-09-16T00:00:00Z",
  "updated_at": "2025-09-16T00:00:00Z"
}
```

### UpdateProject
- メソッド: PUT
- パス: /api/projects/{id}
- リクエスト:
```json
{
  "name": "string",
  "description": "string"
}
```
- レスポンス:
```json
{
  "id": 1,
  "name": "string",
  "description": "string",
  "updated_at": "2025-09-16T00:00:00Z"
}
```

### ListProjects
- メソッド: GET
- パス: /api/projects
- レスポンス:
[
  {
    "id": 1,
    "name": "string",
    "description": "string"
  },
  ...
]
```

### DeleteProject
- メソッド: DELETE
- パス: /api/projects/{id}
- レスポンス:
```json
{
  "result": "success"
}
```

### AddProjectMember
- メソッド: POST
- パス: /api/projects/{id}/members
- リクエスト:
```json
{
  "user_id": 2,
  "role": "member"
}
```
- レスポンス:
```json
{
  "id": 1,
  "project_id": 1,
  "user_id": 2,
  "role": "member",
  "joined_at": "2025-09-16T00:00:00Z"
}
```

### RemoveProjectMember
- メソッド: DELETE
- パス: /api/projects/{id}/members/{uid}
- レスポンス:
```json
{
  "result": "success"
}
```

### ListProjectMembers
- メソッド: GET
- パス: /api/projects/{id}/members
- レスポンス:
[
  {
    "id": 1,
    "user_id": 2,
    "role": "member",
    "joined_at": "2025-09-16T00:00:00Z"
  },
  ...
]
```

### CreateIssue
- メソッド: POST
- パス: /api/issues
- リクエスト:
```json
{
  "project_id": 1,
  "title": "string",
  "description": "string",
  "priority": "high|medium|low",
  "assigned_to": 2
}
```
- レスポンス:
```json
{
  "id": 1,
  "project_id": 1,
  "title": "string",
  "description": "string",
  "status": "open",
  "priority": "high",
  "created_by": 1,
  "assigned_to": 2,
  "created_at": "2025-09-16T00:00:00Z"
}
```

### GetIssue
- メソッド: GET
- パス: /api/issues/{id}
- レスポンス:
{
  "id": 1,
  "project_id": 1,
  "title": "string",
  "description": "string",
  "status": "open",
  "priority": "high",
  "created_by": 1,
  "assigned_to": 2,
  "created_at": "2025-09-16T00:00:00Z",
  "updated_at": "2025-09-16T00:00:00Z"
}
```

### UpdateIssue
- メソッド: PUT
- パス: /api/issues/{id}
- リクエスト:
{
  "title": "string",
  "description": "string",
  "priority": "high|medium|low",
  "assigned_to": 2,
  "status": "open|in_progress|closed"
}
```
- レスポンス:
{
  "id": 1,
  "title": "string",
  "description": "string",
  "priority": "high",
  "assigned_to": 2,
  "status": "in_progress",
  "updated_at": "2025-09-16T00:00:00Z"
}
```

### ListIssues
- メソッド: GET
- パス: /api/issues
- レスポンス:
[
  {
    "id": 1,
    "title": "string",
    "status": "open",
    "priority": "high"
  },
  ...
]
```

### DeleteIssue
- メソッド: DELETE
- パス: /api/issues/{id}
- レスポンス:
{
  "result": "success"
}
```

### ChangeIssueStatus
- メソッド: PATCH
- パス: /api/issues/{id}/status
- リクエスト:
{
  "status": "in_progress"
}
```
- レスポンス:
{
  "id": 1,
  "status": "in_progress",
  "updated_at": "2025-09-16T00:00:00Z"
}
```

### AddComment
- メソッド: POST
- パス: /api/issues/{id}/comments
- リクエスト:
{
  "content": "string"
}
```
- レスポンス:
{
  "id": 1,
  "issue_id": 1,
  "user_id": 2,
  "content": "string",
  "created_at": "2025-09-16T00:00:00Z"
}
```

### EditComment
- メソッド: PUT
- パス: /api/comments/{id}
- リクエスト:
{
  "content": "string"
}
```
- レスポンス:
{
  "id": 1,
  "content": "string",
  "updated_at": "2025-09-16T00:00:00Z"
}
```

### DeleteComment
- メソッド: DELETE
- パス: /api/comments/{id}
- レスポンス:
{
  "result": "success"
}
```

### ListComments
- メソッド: GET
- パス: /api/issues/{id}/comments
- レスポンス:
[
  {
    "id": 1,
    "user_id": 2,
    "content": "string",
    "created_at": "2025-09-16T00:00:00Z"
  },
  ...
]
```

### GetDashboard
- メソッド: GET
- パス: /api/dashboard
- レスポンス:
{
  "user_id": 2,
  "open_issues": 5,
  "closed_issues": 10,
  "projects": [
    {
      "id": 1,
      "name": "string"
    }
  ]
}
```

### GetStatistics
- メソッド: GET
- パス: /api/projects/{id}/stats
- レスポンス:
{
  "project_id": 1,
  "total_issues": 20,
  "open": 5,
  "closed": 15,
  "by_priority": { "high": 2, "medium": 10, "low": 8 }
}
```

### GetNotifications
- メソッド: GET
- パス: /api/notifications
- レスポンス:
[
  {
    "id": 1,
    "user_id": 2,
    "message": "string",
    "is_read": false,
    "created_at": "2025-09-16T00:00:00Z"
  },
  ...
]
```

### MarkNotificationRead
- メソッド: PATCH
- パス: /api/notifications/{id}/read
- レスポンス:
{
  "id": 1,
  "is_read": true,
  "updated_at": "2025-09-16T00:00:00Z"
}
```

### SystemSettings
- メソッド: GET/PUT
- パス: /api/settings
- リクエスト（PUT時）:
{
  "maintenance_mode": false,
  "email_sender": "noreply@example.com"
}
```
- レスポンス:
{
  "maintenance_mode": false,
  "email_sender": "noreply@example.com"
}
```

## 3. インターフェース設計方針
- RESTful設計原則に従い、各リソースは独立したエンドポイントを持つ
- 認証は全APIで必須（JWTトークン等）
- 権限管理はロールベース（PM/管理者）
- エラー時はHTTPステータスコードとエラーメッセージを返却
- 内部インターフェースはDjango ORM/サービス層で実装

## 4. 完了確認チェックリスト
- [x] 全API/内部インターフェースが網羅されている
- [x] API詳細設計例が記載されている
- [x] 認証・権限・エラー設計が明記されている
- [x] STEP2/STEP3成果物との整合性が確認されている
- [x] 標準テーブル・JSON例が使用されている

## 次のアクション
1. 主要ユースケースごとのシーケンス図作成
2. STEP3品質ゲートでの検証準備

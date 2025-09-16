# シーケンス図集 - Issue Tracking System

## メタデータ
- ドキュメントID: SEQ-001
- 作成日: 2025-09-16
- 作成者: GitHub Copilot
- プロジェクト: Issue Tracking System MVP
- 関連文書: class-design.md, interfaces.md, use-cases.md

---

## 1. ユーザー登録（UC-001）
```mermaid
sequenceDiagram
    participant U as User
    participant W as WebUI
    participant API as API Controller
    participant S as UserService
    participant M as UserModel
    participant DB as DB
    U->>W: 新規登録フォーム表示
    W->>API: POST /api/users (username, email, password)
    API->>S: create_user(username, email, password)
    S->>M: save(username, email, password_hash)
    M->>DB: INSERT users
    DB-->>M: 保存結果
    M-->>S: Userオブジェクト返却
    S-->>API: Userオブジェクト返却
    API-->>W: 登録完了レスポンス
    W-->>U: 完了画面表示
```

---

## 2. チケット作成（UC-008）
```mermaid
sequenceDiagram
    participant U as User
    participant W as WebUI
    participant API as API Controller
    participant S as IssueService
    participant M as IssueModel
    participant DB as DB
    U->>W: チケット作成フォーム表示
    W->>API: POST /api/issues (title, description, priority, assigned_to)
    API->>S: create_issue(title, description, priority, assigned_to)
    S->>M: save(title, description, priority, assigned_to)
    M->>DB: INSERT issues
    DB-->>M: 保存結果
    M-->>S: Issueオブジェクト返却
    S-->>API: Issueオブジェクト返却
    API-->>W: 作成完了レスポンス
    W-->>U: チケット詳細画面表示
```

---

## 3. チケット状態変更（UC-013）
```mermaid
sequenceDiagram
    participant U as User
    participant W as WebUI
    participant API as API Controller
    participant S as IssueService
    participant M as IssueModel
    participant H as IssueHistoryModel
    participant DB as DB
    U->>W: チケット詳細画面表示
    U->>W: 状態変更操作
    W->>API: PATCH /api/issues/{id}/status (status)
    API->>S: update_status(issue_id, status)
    S->>M: update(issue_id, status)
    M->>DB: UPDATE issues SET status
    DB-->>M: 更新結果
    M-->>S: Issueオブジェクト返却
    S->>H: save(issue_id, field_name, old_value, new_value, changed_by)
    H->>DB: INSERT issue_history
    DB-->>H: 保存結果
    H-->>S: IssueHistoryオブジェクト返却
    S-->>API: 更新結果返却
    API-->>W: 更新完了レスポンス
    W-->>U: 状態変更反映
```

---

## 4. コメント追加（UC-009）
```mermaid
sequenceDiagram
    participant U as User
    participant W as WebUI
    participant API as API Controller
    participant S as CommentService
    participant M as CommentModel
    participant DB as DB
    U->>W: コメント入力
    W->>API: POST /api/issues/{id}/comments (content)
    API->>S: add_comment(issue_id, user_id, content)
    S->>M: save(issue_id, user_id, content)
    M->>DB: INSERT comments
    DB-->>M: 保存結果
    M-->>S: Commentオブジェクト返却
    S-->>API: Commentオブジェクト返却
    API-->>W: 追加完了レスポンス
    W-->>U: コメント表示
```

---

## 5. プロジェクトメンバー追加（UC-018）
```mermaid
sequenceDiagram
    participant PM as ProjectManager
    participant W as WebUI
    participant API as API Controller
    participant S as ProjectMemberService
    participant M as ProjectMemberModel
    participant DB as DB
    PM->>W: メンバー追加操作
    W->>API: POST /api/projects/{id}/members (user, role)
    API->>S: add_member(project_id, user_id, role)
    S->>M: save(project_id, user_id, role)
    M->>DB: INSERT project_members
    DB-->>M: 保存結果
    M-->>S: ProjectMemberオブジェクト返却
    S-->>API: ProjectMemberオブジェクト返却
    API-->>W: 追加完了レスポンス
    W-->>PM: メンバー一覧更新
```

---

## 6. ダッシュボード表示（UC-016）
```mermaid
sequenceDiagram
    participant U as User
    participant W as WebUI
    participant API as API Controller
    participant S as DashboardService
    participant M as StatisticsModel
    participant DB as DB
    U->>W: ダッシュボード画面表示
    W->>API: GET /api/dashboard
    API->>S: get_dashboard(user_id)
    S->>M: aggregate(user_id)
    M->>DB: SELECT/COUNT/AGGREGATE
    DB-->>M: 集計データ返却
    M-->>S: Statisticsオブジェクト返却
    S-->>API: ダッシュボードデータ返却
    API-->>W: ダッシュボードデータ返却
    W-->>U: ダッシュボード表示
```

---


## 7. 管理者によるユーザー削除（UC-020）
```mermaid
sequenceDiagram
    participant Admin as 管理者
    participant W as WebUI
    participant API as API Controller
    participant S as UserService
    participant M as UserModel
    participant DB as DB
    Admin->>W: ユーザー削除操作
    W->>API: DELETE /api/users/{id}
    API->>S: delete_user(user_id)
    S->>M: delete(user_id)
    M->>DB: DELETE users
    DB-->>M: 削除結果
    M-->>S: 削除結果返却
    S-->>API: 削除結果返却
    API-->>W: 削除完了レスポンス
    W-->>Admin: ユーザー一覧更新
```

---

## 8. チケット一覧取得（UC-009）
```mermaid
sequenceDiagram
    participant U as User
    participant W as WebUI
    participant API as API Controller
    participant S as IssueService
    participant M as IssueModel
    participant DB as DB
    U->>W: チケット一覧画面表示
    W->>API: GET /api/issues
    API->>S: list_issues()
    S->>M: find_all()
    M->>DB: SELECT * FROM issues
    DB-->>M: チケットデータ返却
    M-->>S: Issueリスト返却
    S-->>API: Issueリスト返却
    API-->>W: 一覧データ返却
    W-->>U: チケット一覧表示
```

---

## 9. チケット編集（UC-011）
```mermaid
sequenceDiagram
    participant U as User
    participant W as WebUI
    participant API as API Controller
    participant S as IssueService
    participant M as IssueModel
    participant DB as DB
    U->>W: 編集フォーム表示
    W->>API: PUT /api/issues/{id} (title, description, priority, assigned_to, status)
    API->>S: edit_issue(issue_id, issue_data)
    S->>M: update(issue_id, issue_data)
    M->>DB: UPDATE issues SET ...
    DB-->>M: 更新結果
    M-->>S: Issueオブジェクト返却
    S-->>API: Issueオブジェクト返却
    API-->>W: 更新完了レスポンス
    W-->>U: 編集結果表示
```

---

## 10. コメント編集・削除（UC-012）
```mermaid
sequenceDiagram
    participant U as User
    participant W as WebUI
    participant API as API Controller
    participant S as CommentService
    participant M as CommentModel
    participant DB as DB
    U->>W: コメント編集/削除操作
    W->>API: PUT /api/comments/{id} (content)
    API->>S: edit_comment(comment_id, content)
    S->>M: update(comment_id, content)
    M->>DB: UPDATE comments SET content
    DB-->>M: 更新結果
    M-->>S: Commentオブジェクト返却
    S-->>API: Commentオブジェクト返却
    API-->>W: 完了レスポンス
    W-->>U: コメント一覧更新
    W->>API: DELETE /api/comments/{id}
    API->>S: delete_comment(comment_id)
    S->>M: delete(comment_id)
    M->>DB: DELETE comments
    DB-->>M: 削除結果
    M-->>S: 削除結果返却
    S-->>API: 削除結果返却
    API-->>W: 完了レスポンス
    W-->>U: コメント一覧更新
```

---

## 11. 通知一覧・既読化（UC-021）
```mermaid
sequenceDiagram
    participant U as User
    participant W as WebUI
    participant API as API Controller
    participant S as NotificationService
    participant M as NotificationModel
    participant DB as DB
    U->>W: 通知画面表示
    W->>API: GET /api/notifications
    API->>S: get_notifications(user_id)
    S->>M: find_by_user(user_id)
    M->>DB: SELECT * FROM notifications WHERE user_id
    DB-->>M: 通知データ返却
    M-->>S: Notificationリスト返却
    S-->>API: Notificationリスト返却
    API-->>W: 一覧データ返却
    W-->>U: 通知一覧表示
    U->>W: 既読化操作
    W->>API: PATCH /api/notifications/{id}/read
    API->>S: mark_as_read(notification_id)
    S->>M: update(notification_id, is_read=true)
    M->>DB: UPDATE notifications SET is_read=true
    DB-->>M: 更新結果
    M-->>S: Notificationオブジェクト返却
    S-->>API: Notificationオブジェクト返却
    API-->>W: 完了レスポンス
    W-->>U: 通知一覧更新
```

---

## 12. 統計表示（UC-019）
```mermaid
sequenceDiagram
    participant PM as ProjectManager
    participant W as WebUI
    participant API as API Controller
    participant S as StatisticsService
    participant M as StatisticsModel
    participant DB as DB
    PM->>W: 統計画面表示
    W->>API: GET /api/projects/{id}/stats
    API->>S: get_statistics(project_id)
    S->>M: aggregate(project_id)
    M->>DB: SELECT/COUNT/AGGREGATE
    DB-->>M: 集計結果返却
    M-->>S: Statisticsオブジェクト返却
    S-->>API: 統計データ返却
    API-->>W: 統計データ返却
    W-->>PM: 統計表示
```

---

## 13. システム設定取得・更新（UC-022）
```mermaid
sequenceDiagram
    participant Admin as 管理者
    participant W as WebUI
    participant API as API Controller
    participant S as SystemSettingsService
    participant M as SystemSettingsModel
    participant DB as DB
    Admin->>W: 設定画面表示
    W->>API: GET /api/settings
    API->>S: get_settings()
    S->>M: find()
    M->>DB: SELECT * FROM system_settings
    DB-->>M: 設定データ返却
    M-->>S: SystemSettingsオブジェクト返却
    S-->>API: 設定データ返却
    API-->>W: 設定データ返却
    W-->>Admin: 設定表示
    Admin->>W: 設定変更操作
    W->>API: PUT /api/settings (maintenance_mode, email_sender)
    API->>S: update_settings(settings_data)
    S->>M: update(settings_data)
    M->>DB: UPDATE system_settings SET ...
    DB-->>M: 更新結果
    M-->>S: SystemSettingsオブジェクト返却
    S-->>API: 完了レスポンス
    API-->>W: 完了レスポンス
    W-->>Admin: 設定画面更新
```

---

## 完了確認チェックリスト
- [x] 主要ユースケース・APIごとにシーケンス図が網羅されている
- [x] クラス設計・インターフェース定義との整合性が確認されている
- [x] Mermaid記法でUMLが記述されている
- [x] STEP3成果物として設計内容の検証が可能

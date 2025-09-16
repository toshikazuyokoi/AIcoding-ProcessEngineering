# 単体テスト設計書 - Issue Tracking System

## メタデータ
- ドキュメントID: UNIT-TEST-001
- 作成日: 2025-09-16
- 作成者: GitHub Copilot
- プロジェクト: Issue Tracking System MVP
- 関連文書: ../class-design.md, ../interfaces.md

---

## 1. テスト対象一覧
- UserService（create, read, update, delete, authenticate, authorize）
- IssueService（create, read, update, delete, changeStatus, assign, comment, attachFile）
- NotificationService（create, read, markAsRead, delete）
- SystemSettingsService（getSettings, updateSettings, validateSettings）
- StatisticsService（getUserStats, getIssueStats, getSystemStats）

---

## 2. テストケース一覧（網羅度100%）

### UserService
| テストID | メソッド | 観点 | 入力 | 期待結果 |
|---------|----------|------|------|----------|
| UT-001  | create   | 正常系 | 有効なユーザー情報 | ユーザー作成成功 |
| UT-002  | create   | 異常系 | メール重複 | エラー（重複） |
| UT-003  | create   | 異常系 | 必須項目未入力 | エラー（未入力） |
| UT-004  | read     | 正常系 | 有効なID | ユーザー情報取得 |
| UT-005  | read     | 異常系 | 存在しないID | エラー（未存在） |
| UT-006  | update   | 正常系 | 有効な更新情報 | 更新成功 |
| UT-007  | update   | 異常系 | 無効な値 | エラー（バリデーション） |
| UT-008  | delete   | 正常系 | 有効なID | 削除成功 |
| UT-009  | delete   | 異常系 | 存在しないID | エラー（未存在） |
| UT-010  | authenticate | 正常系 | 正しい認証情報 | 認証成功 |
| UT-011  | authenticate | 異常系 | 誤った認証情報 | エラー（認証失敗） |
| UT-012  | authorize | 正常系 | 権限あり | 許可 |
| UT-013  | authorize | 異常系 | 権限なし | 拒否 |

### IssueService
| テストID | メソッド | 観点 | 入力 | 期待結果 |
|---------|----------|------|------|----------|
| UT-101  | create   | 正常系 | 有効なチケット情報 | 作成成功 |
| UT-102  | create   | 異常系 | 必須項目未入力 | エラー（未入力） |
| UT-103  | create   | 異常系 | 無効な値 | エラー（バリデーション） |
| UT-104  | read     | 正常系 | 有効なID | チケット情報取得 |
| UT-105  | read     | 異常系 | 存在しないID | エラー（未存在） |
| UT-106  | update   | 正常系 | 有効な更新情報 | 更新成功 |
| UT-107  | update   | 異常系 | 無効な値 | エラー（バリデーション） |
| UT-108  | delete   | 正常系 | 有効なID | 削除成功 |
| UT-109  | delete   | 異常系 | 存在しないID | エラー（未存在） |
| UT-110  | changeStatus | 正常系 | 有効な状態 | 状態変更成功 |
| UT-111  | changeStatus | 異常系 | 無効な状態 | エラー（状態不正） |
| UT-112  | assign   | 正常系 | 有効なユーザーID | 割当成功 |
| UT-113  | assign   | 異常系 | 存在しないユーザーID | エラー（未存在） |
| UT-114  | comment  | 正常系 | 有効なコメント | コメント追加成功 |
| UT-115  | comment  | 異常系 | 空コメント | エラー（未入力） |
| UT-116  | attachFile | 正常系 | 有効なファイル | 添付成功 |
| UT-117  | attachFile | 異常系 | 無効なファイル | エラー（ファイル不正） |

### NotificationService
| テストID | メソッド | 観点 | 入力 | 期待結果 |
|---------|----------|------|------|----------|
| UT-201  | create   | 正常系 | 有効な通知情報 | 作成成功 |
| UT-202  | create   | 異常系 | 必須項目未入力 | エラー（未入力） |
| UT-203  | read     | 正常系 | 有効なID | 通知情報取得 |
| UT-204  | read     | 異常系 | 存在しないID | エラー（未存在） |
| UT-205  | markAsRead | 正常系 | 有効なID | 既読化成功 |
| UT-206  | markAsRead | 異常系 | 存在しないID | エラー（未存在） |
| UT-207  | delete   | 正常系 | 有効なID | 削除成功 |
| UT-208  | delete   | 異常系 | 存在しないID | エラー（未存在） |

### SystemSettingsService
| テストID | メソッド | 観点 | 入力 | 期待結果 |
|---------|----------|------|------|----------|
| UT-301  | getSettings | 正常系 | 有効なリクエスト | 設定取得成功 |
| UT-302  | getSettings | 異常系 | 無効なリクエスト | エラー（不正） |
| UT-303  | updateSettings | 正常系 | 有効な設定値 | 更新成功 |
| UT-304  | updateSettings | 異常系 | 無効な値 | エラー（バリデーション） |
| UT-305  | validateSettings | 正常系 | 有効な値 | バリデーション成功 |
| UT-306  | validateSettings | 異常系 | 無効な値 | エラー（バリデーション） |

### StatisticsService
| テストID | メソッド | 観点 | 入力 | 期待結果 |
|---------|----------|------|------|----------|
| UT-401  | getUserStats | 正常系 | 有効なユーザーID | 統計取得成功 |
| UT-402  | getUserStats | 異常系 | 存在しないID | エラー（未存在） |
| UT-403  | getIssueStats | 正常系 | 有効なチケットID | 統計取得成功 |
| UT-404  | getIssueStats | 異常系 | 存在しないID | エラー（未存在） |
| UT-405  | getSystemStats | 正常系 | 有効なリクエスト | 統計取得成功 |
| UT-406  | getSystemStats | 異常系 | 無効なリクエスト | エラー（不正） |

---

## 3. 境界値・異常系テスト
- 各メソッドの入力値（最大長、最小長、空文字、NULL、型不一致、範囲外、重複、未存在、権限なし等）を網羅

---

## 4. トレーサビリティ
- 各テストケースはSTEP3のクラス設計・API定義・シーケンス図と紐付け

---

## 5. 完了確認チェックリスト
- [x] 全メソッド・分岐・異常系・境界値を網羅
- [x] テストID・観点・期待結果を明記
- [x] トレーサビリティを明記
- [x] Markdown記法・標準テーブルを使用
- [x] STEP3設計成果物との整合性

## 次のアクション
1. 単体テストケースの実装
2. STEP4品質ゲートでの検証

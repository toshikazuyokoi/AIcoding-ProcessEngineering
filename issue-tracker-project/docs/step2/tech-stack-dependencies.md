# 技術選定・依存関係定義書 - Issue Tracking System

## メタデータ
- ドキュメントID: TECH-002
- 作成日: 2025-09-16
- 作成者: GitHub Copilot
- プロジェクト: Issue Tracking System MVP
- 関連文書: system-architecture.md, ../step1/specification.md

## 1. 技術選定方針
| 分類 | 技術 | バージョン | 選定理由 |
|------|------|-----------|----------|
| バックエンド | Python | 3.9+ | AI開発効率・ライブラリ豊富 |
| バックエンド | Django | 4.2+ | 標準管理画面・セキュリティ・拡張性 |
| フロントエンド | Bootstrap | 5.x | レスポンシブ・UI標準化 |
| データベース | SQLite | 3.x | 開発効率・ローカル運用 |
| データベース | PostgreSQL | 12+ | 本番運用・拡張性 |
| テスト | pytest | 7.x | Python標準・自動化容易 |
| CI/CD | GitHub Actions | - | OSS・自動化・無料枠利用 |

## 2. 主要ライブラリ・依存関係
| ライブラリ | バージョン | 用途 |
|------------|-----------|------|
| Django REST Framework | 3.14+ | API実装（Phase2） |
| bcrypt | 4.x | パスワードハッシュ化 |
| python-dotenv | 1.x | 環境変数管理 |
| coverage | 7.x | テストカバレッジ測定 |
| flake8/pylint | 最新 | 静的解析・Lint |
| bandit | 最新 | セキュリティチェック |
| gunicorn | 20.x | 本番Webサーバ |
| psycopg2 | 2.x | PostgreSQL接続 |
| selenium | 4.x | E2Eテスト（Phase2） |

## 3. 依存関係管理
- `requirements.txt`で全ライブラリを一元管理
- バージョン固定で再現性確保
- 開発・本番環境で差分管理（dev-requirements.txt等）

## 4. インフラ・運用方針
| 項目 | 内容 | 備考 |
|------|------|------|
| 開発環境 | ローカルLinux/WSL | Python/Django/SQLite |
| 本番環境 | VPS/クラウド | Ubuntu 20.04+, PostgreSQL |
| CI/CD | GitHub Actions | テスト・デプロイ自動化 |
| バックアップ | 手動/自動スクリプト | DB・静的ファイル |

## 5. セキュリティ・品質管理
| 項目 | 内容 | 備考 |
|------|------|------|
| 静的解析 | flake8/pylint | pre-commit hook推奨 |
| セキュリティチェック | bandit | CI/CD組み込み |
| テストカバレッジ | coverage.py | 80%以上目標 |
| 依存関係脆弱性 | pip-audit | 定期監査推奨 |

## 6. 完了確認チェックリスト
- [x] 技術選定理由が明確に記載されている
- [x] 主要ライブラリ・依存関係が網羅されている
- [x] 依存関係管理方針が明記されている
- [x] インフラ・運用方針が整理されている
- [x] セキュリティ・品質管理が明記されている
- [x] STEP1/STEP2成果物との整合性が確認されている

## 次のアクション
1. STEP2品質ゲートでの検証
2. STEP3（詳細設計）への移行準備

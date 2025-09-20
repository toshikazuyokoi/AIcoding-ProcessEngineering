from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.messages.storage.fallback import FallbackStorage
import json
from tracker.models import Project, ProjectMember, Issue, IssueHistory, Comment, Notification, SystemSettings, Statistics
from tracker.services.user_service import UserService
from tracker.services.issue_service import IssueService
from tracker.services.notification_service import NotificationService
from tracker.services.system_settings_service import SystemSettingsService
from tracker.services.statistics_service import StatisticsService
from tracker.api.user_api import create_user, get_user, update_user, list_users, delete_user
from tracker.api.notification_api import list_notifications, mark_notification_read, delete_notification

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
    
    def test_create_user(self):
        """ユーザー作成テスト"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
    
    def test_unique_email(self):
        """メールアドレス一意性テスト"""
        User.objects.create_user(**self.user_data)
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='testuser2',
                email='test@example.com',
                password='testpass123'
            )
    
    def test_update_profile(self):
        """プロファイル更新テスト"""
        user = User.objects.create_user(**self.user_data)
        profile_data = {'first_name': 'Test', 'last_name': 'User'}
        user.update_profile(profile_data)
        
        user.refresh_from_db()
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
    
    def test_get_projects(self):
        """参加プロジェクト一覧取得テスト"""
        user = User.objects.create_user(**self.user_data)
        project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            created_by=user
        )
        
        projects = user.get_projects()
        self.assertIn(project, projects)


class ProjectModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            created_by=self.user
        )
    
    def test_create_project(self):
        """プロジェクト作成テスト"""
        self.assertEqual(self.project.name, 'Test Project')
        self.assertEqual(self.project.created_by, self.user)
    
    def test_add_member(self):
        """メンバー追加テスト"""
        new_user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='testpass123'
        )
        member = self.project.add_member(new_user, 'member')
        
        self.assertEqual(member.user, new_user)
        self.assertEqual(member.project, self.project)
        self.assertEqual(member.role, 'member')
    
    def test_get_members(self):
        """メンバー一覧取得テスト"""
        new_user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='testpass123'
        )
        self.project.add_member(new_user)
        
        members = self.project.get_members()
        self.assertEqual(members.count(), 1)
    
    def test_edit_project(self):
        """プロジェクト編集テスト"""
        new_data = {'name': 'Updated Project', 'description': 'Updated Description'}
        updated_project = self.project.edit_project(new_data)
        
        self.assertEqual(updated_project.name, 'Updated Project')
        self.assertEqual(updated_project.description, 'Updated Description')


class ProjectMemberModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            created_by=self.user
        )
        self.member = ProjectMember.objects.create(
            project=self.project,
            user=self.user,
            role='member'
        )
    
    def test_create_project_member(self):
        """プロジェクトメンバー作成テスト"""
        self.assertEqual(self.member.project, self.project)
        self.assertEqual(self.member.user, self.user)
        self.assertEqual(self.member.role, 'member')
    
    def test_change_role(self):
        """役割変更テスト"""
        result = self.member.change_role('admin')
        self.assertTrue(result)
        
        self.member.refresh_from_db()
        self.assertEqual(self.member.role, 'admin')
    
    def test_change_invalid_role(self):
        """無効な役割変更テスト"""
        result = self.member.change_role('invalid_role')
        self.assertFalse(result)


class IssueModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            created_by=self.user
        )
        self.issue = Issue.objects.create(
            project=self.project,
            title='Test Issue',
            description='Test Description',
            created_by=self.user,
            status='open',
            priority='medium'
        )
    
    def test_create_issue(self):
        """チケット作成テスト"""
        self.assertEqual(self.issue.title, 'Test Issue')
        self.assertEqual(self.issue.project, self.project)
        self.assertEqual(self.issue.created_by, self.user)
        self.assertEqual(self.issue.status, 'open')
        self.assertEqual(self.issue.priority, 'medium')
    
    def test_update_status(self):
        """状態更新テスト"""
        result = self.issue.update_status('in_progress', self.user)
        self.assertTrue(result)
        
        self.issue.refresh_from_db()
        self.assertEqual(self.issue.status, 'in_progress')
        
        # 履歴が作成されることを確認
        history = IssueHistory.objects.filter(issue=self.issue).first()
        self.assertIsNotNone(history)
        self.assertEqual(history.field_name, 'status')
        self.assertEqual(history.old_value, 'open')
        self.assertEqual(history.new_value, 'in_progress')
    
    def test_update_invalid_status(self):
        """無効な状態更新テスト"""
        result = self.issue.update_status('invalid_status', self.user)
        self.assertFalse(result)
    
    def test_add_comment(self):
        """コメント追加テスト"""
        comment = Comment(user=self.user, content='Test comment')
        result = self.issue.add_comment(comment)
        self.assertTrue(result)
        
        comment.refresh_from_db()
        self.assertEqual(comment.issue, self.issue)
    
    def test_edit_issue(self):
        """チケット編集テスト"""
        new_data = {'title': 'Updated Issue', 'priority': 'high'}
        updated_issue = self.issue.edit_issue(new_data, self.user)
        
        self.assertEqual(updated_issue.title, 'Updated Issue')
        self.assertEqual(updated_issue.priority, 'high')
        
        # 履歴が作成されることを確認
        histories = IssueHistory.objects.filter(issue=self.issue)
        self.assertEqual(histories.count(), 2)  # title and priority changes
    
    def test_get_history(self):
        """履歴取得テスト"""
        self.issue.update_status('in_progress', self.user)
        history = self.issue.get_history()
        
        self.assertEqual(history.count(), 1)
        self.assertEqual(history.first().field_name, 'status')


class IssueHistoryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            created_by=self.user
        )
        self.issue = Issue.objects.create(
            project=self.project,
            title='Test Issue',
            description='Test Description',
            created_by=self.user
        )
        self.history = IssueHistory.objects.create(
            issue=self.issue,
            field_name='status',
            old_value='open',
            new_value='in_progress',
            changed_by=self.user
        )
    
    def test_create_history(self):
        """履歴作成テスト"""
        self.assertEqual(self.history.issue, self.issue)
        self.assertEqual(self.history.field_name, 'status')
        self.assertEqual(self.history.old_value, 'open')
        self.assertEqual(self.history.new_value, 'in_progress')
        self.assertEqual(self.history.changed_by, self.user)
    
    def test_get_changes(self):
        """変更内容取得テスト"""
        changes = self.history.get_changes()
        
        self.assertEqual(changes['field'], 'status')
        self.assertEqual(changes['old_value'], 'open')
        self.assertEqual(changes['new_value'], 'in_progress')
        self.assertEqual(changes['changed_by'], self.user.username)


class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            created_by=self.user
        )
        self.issue = Issue.objects.create(
            project=self.project,
            title='Test Issue',
            description='Test Description',
            created_by=self.user
        )
        self.comment = Comment.objects.create(
            issue=self.issue,
            user=self.user,
            content='Test comment'
        )
    
    def test_create_comment(self):
        """コメント作成テスト"""
        self.assertEqual(self.comment.issue, self.issue)
        self.assertEqual(self.comment.user, self.user)
        self.assertEqual(self.comment.content, 'Test comment')
    
    def test_edit_content(self):
        """コメント編集テスト"""
        result = self.comment.edit_content('Updated comment')
        self.assertTrue(result)
        
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, 'Updated comment')
    
    def test_delete_comment(self):
        """コメント削除テスト"""
        comment_id = self.comment.id
        result = self.comment.delete_comment()
        self.assertTrue(result)
        
        # コメントが削除されていることを確認
        with self.assertRaises(Comment.DoesNotExist):
            Comment.objects.get(id=comment_id)


class NotificationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.notification = Notification.objects.create(
            user=self.user,
            message='Test notification message',
            is_read=False
        )

    def test_create_notification(self):
        """通知作成テスト"""
        self.assertEqual(self.notification.user, self.user)
        self.assertEqual(self.notification.message, 'Test notification message')
        self.assertFalse(self.notification.is_read)
        self.assertIsNotNone(self.notification.created_at)

    def test_mark_as_read(self):
        """既読化テスト"""
        result = self.notification.mark_as_read()
        self.assertTrue(result)
        
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)

    def test_get_notifications_all(self):
        """通知一覧取得テスト（全件）"""
        # 追加の通知を作成
        Notification.objects.create(
            user=self.user,
            message='Second notification',
            is_read=True
        )
        
        notifications = Notification.get_notifications(self.user)
        self.assertEqual(notifications.count(), 2)

    def test_get_notifications_unread_only(self):
        """通知一覧取得テスト（未読のみ）"""
        # 追加の通知を作成（既読）
        Notification.objects.create(
            user=self.user,
            message='Read notification',
            is_read=True
        )
        
        unread_notifications = Notification.get_notifications(self.user, unread_only=True)
        self.assertEqual(unread_notifications.count(), 1)
        self.assertFalse(unread_notifications.first().is_read)

    def test_delete_notification(self):
        """通知削除テスト"""
        notification_id = self.notification.id
        result = self.notification.delete_notification()
        self.assertTrue(result)
        
        # 通知が削除されていることを確認
        with self.assertRaises(Notification.DoesNotExist):
            Notification.objects.get(id=notification_id)

    def test_notification_ordering(self):
        """通知の並び順テスト（新しい順）"""
        # 追加の通知を作成
        newer_notification = Notification.objects.create(
            user=self.user,
            message='Newer notification'
        )
        
        notifications = Notification.objects.filter(user=self.user)
        self.assertEqual(notifications.first(), newer_notification)
        self.assertEqual(notifications.last(), self.notification)

    def test_notification_str_representation(self):
        """通知の文字列表現テスト"""
        expected = f"Notification for {self.user.username}: {self.notification.message[:50]}..."
        self.assertEqual(str(self.notification), expected)


class SystemSettingsModelTest(TestCase):
    def test_get_settings_creates_singleton(self):
        """get_settings は存在しない場合に作成し、単一オブジェクトを返す"""
        settings1 = SystemSettings.get_settings()
        self.assertIsInstance(settings1, SystemSettings)
        self.assertEqual(settings1.pk, 1)

        # 再取得しても同一PK
        settings2 = SystemSettings.get_settings()
        self.assertEqual(settings2.pk, 1)

    def test_update_settings(self):
        """update_settings でフィールド更新できる"""
        updated = SystemSettings.update_settings({
            'maintenance_mode': True,
            'email_sender': 'noreply@example.com',
        })
        self.assertTrue(updated.maintenance_mode)
        self.assertEqual(updated.email_sender, 'noreply@example.com')

        # 変更なしでも呼び出し可能
        again = SystemSettings.update_settings({
            'maintenance_mode': True,
            'email_sender': 'noreply@example.com',
        })
        self.assertEqual(again.pk, updated.pk)

    def test_singleton_enforced_on_save(self):
        """save 時に常に PK=1 に統一される（冗長対策）"""
        s = SystemSettings(maintenance_mode=False, email_sender='a@example.com')
        s.save()
        self.assertEqual(s.pk, 1)
        # 複数作成を試みても 1 つに収束
        t = SystemSettings(maintenance_mode=True, email_sender='b@example.com')
        t.save()
        self.assertEqual(SystemSettings.objects.count(), 1)
        self.assertEqual(SystemSettings.get_settings().email_sender, 'b@example.com')

    def test_str_representation(self):
        obj = SystemSettings.get_settings()
        text = str(obj)
        self.assertIn('SystemSettings(', text)


class StatisticsModelTest(TestCase):
    def setUp(self):
        # ユーザーとプロジェクト作成
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            created_by=self.user
        )
        
        # テスト用のIssueを作成
        self.issue1 = Issue.objects.create(
            project=self.project,
            title='Issue 1',
            description='Description 1',
            created_by=self.user,
            status='open',
            priority='high'
        )
        self.issue2 = Issue.objects.create(
            project=self.project,
            title='Issue 2',
            description='Description 2',
            created_by=self.user,
            status='closed',
            priority='medium'
        )
        self.issue3 = Issue.objects.create(
            project=self.project,
            title='Issue 3',
            description='Description 3',
            created_by=self.user,
            status='in_progress',
            priority='high'
        )

    def test_get_statistics_returns_correct_counts(self):
        """get_statistics が正しい統計情報を返す"""
        stats = Statistics.get_statistics(self.project.id)
        
        self.assertIsNotNone(stats)
        self.assertEqual(stats.project, self.project)
        self.assertEqual(stats.total_issues, 3)
        self.assertEqual(stats.open_issues, 2)  # open + in_progress
        self.assertEqual(stats.closed_issues, 1)  # closed

    def test_get_statistics_priority_breakdown(self):
        """get_statistics が優先度別統計を正しく返す"""
        stats = Statistics.get_statistics(self.project.id)
        
        priority_counts = stats.by_priority
        self.assertEqual(priority_counts['high'], 2)
        self.assertEqual(priority_counts['medium'], 1)
        self.assertNotIn('low', priority_counts)  # 0件のものは含まない

    def test_get_statistics_nonexistent_project(self):
        """存在しないプロジェクトIDでNoneを返す"""
        stats = Statistics.get_statistics(99999)
        self.assertIsNone(stats)

    def test_get_statistics_empty_project(self):
        """Issueがないプロジェクトで0統計を返す"""
        empty_project = Project.objects.create(
            name='Empty Project',
            description='No issues',
            created_by=self.user
        )
        
        stats = Statistics.get_statistics(empty_project.id)
        self.assertIsNotNone(stats)
        self.assertEqual(stats.total_issues, 0)
        self.assertEqual(stats.open_issues, 0)
        self.assertEqual(stats.closed_issues, 0)
        self.assertEqual(stats.by_priority, {})

    def test_by_priority_property(self):
        """by_priority プロパティが正しく動作する"""
        stats = Statistics(
            project=self.project,
            by_priority_json={'high': 3, 'low': 1}
        )
        
        # getter
        self.assertEqual(stats.by_priority['high'], 3)
        self.assertEqual(stats.by_priority['low'], 1)
        
        # setter
        stats.by_priority = {'medium': 5}
        self.assertEqual(stats.by_priority_json['medium'], 5)

    def test_str_representation(self):
        """Statistics の文字列表現をテスト"""
        stats = Statistics.get_statistics(self.project.id)
        text = str(stats)
        
        self.assertIn('Statistics(', text)
        self.assertIn('Test Project', text)
        self.assertIn('total=3', text)


class UserServiceTest(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }

    def test_create_user_success(self):
        """ユーザー作成成功テスト"""
        user = UserService.create_user(**self.user_data)
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertIsNotNone(user.created_at)

    def test_create_user_with_extra_fields(self):
        """追加フィールド付きユーザー作成テスト"""
        user = UserService.create_user(
            **self.user_data,
            first_name='Test',
            last_name='User'
        )
        
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')

    def test_create_user_duplicate_email(self):
        """重複メールアドレスでのエラーテスト"""
        # 最初のユーザー作成
        UserService.create_user(**self.user_data)
        
        # 同じメールアドレスで2回目作成
        with self.assertRaises(ValidationError) as context:
            UserService.create_user(
                username='testuser2',
                email='test@example.com',  # 重複
                password='testpass123'
            )
        self.assertIn('既に使用されています', str(context.exception))

    def test_create_user_duplicate_username(self):
        """重複ユーザー名でのエラーテスト"""
        # 最初のユーザー作成
        UserService.create_user(**self.user_data)
        
        # 同じユーザー名で2回目作成
        with self.assertRaises(ValidationError):
            UserService.create_user(
                username='testuser',  # 重複
                email='test2@example.com',
                password='testpass123'
            )

    def test_update_user_success(self):
        """ユーザー更新成功テスト"""
        user = UserService.create_user(**self.user_data)
        
        updated_user = UserService.update_user(
            user.id,
            first_name='Updated',
            last_name='Name'
        )
        
        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.last_name, 'Name')
        self.assertEqual(updated_user.id, user.id)

    def test_update_user_email_duplicate(self):
        """更新時のメール重複エラーテスト"""
        user1 = UserService.create_user(**self.user_data)
        user2 = UserService.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        
        # user2のメールをuser1のメールに変更しようとする
        with self.assertRaises(ValidationError):
            UserService.update_user(user2.id, email='test@example.com')

    def test_update_user_nonexistent(self):
        """存在しないユーザー更新エラーテスト"""
        with self.assertRaises(User.DoesNotExist):
            UserService.update_user(99999, first_name='Test')

    def test_delete_user_success(self):
        """ユーザー削除成功テスト"""
        user = UserService.create_user(**self.user_data)
        user_id = user.id
        
        result = UserService.delete_user(user_id)
        self.assertTrue(result)
        
        # 削除確認
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=user_id)

    def test_delete_user_with_projects(self):
        """プロジェクト作成者削除エラーテスト"""
        user = UserService.create_user(**self.user_data)
        
        # プロジェクト作成
        Project.objects.create(
            name='Test Project',
            description='Test',
            created_by=user
        )
        
        # 削除試行
        with self.assertRaises(ValidationError) as context:
            UserService.delete_user(user.id)
        self.assertIn('削除できません', str(context.exception))

    def test_get_user_by_id(self):
        """ID指定ユーザー取得テスト"""
        user = UserService.create_user(**self.user_data)
        
        found_user = UserService.get_user_by_id(user.id)
        self.assertEqual(found_user.id, user.id)
        
        # 存在しないID
        not_found = UserService.get_user_by_id(99999)
        self.assertIsNone(not_found)

    def test_get_user_by_email(self):
        """メール指定ユーザー取得テスト"""
        user = UserService.create_user(**self.user_data)
        
        found_user = UserService.get_user_by_email('test@example.com')
        self.assertEqual(found_user.email, user.email)
        
        # 存在しないメール
        not_found = UserService.get_user_by_email('notfound@example.com')
        self.assertIsNone(not_found)

    def test_authenticate_user_success(self):
        """認証成功テスト"""
        user = UserService.create_user(**self.user_data)
        
        authenticated = UserService.authenticate_user(
            'test@example.com',
            'testpass123'
        )
        self.assertEqual(authenticated.id, user.id)

    def test_authenticate_user_wrong_password(self):
        """認証失敗（間違いパスワード）テスト"""
        UserService.create_user(**self.user_data)
        
        authenticated = UserService.authenticate_user(
            'test@example.com',
            'wrongpass'
        )
        self.assertIsNone(authenticated)

    def test_authenticate_user_nonexistent_email(self):
        """認証失敗（存在しないメール）テスト"""
        authenticated = UserService.authenticate_user(
            'notfound@example.com',
            'testpass123'
        )
        self.assertIsNone(authenticated)

    def test_list_users(self):
        """ユーザー一覧取得テスト"""
        user1 = UserService.create_user(**self.user_data)
        user2 = UserService.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        
        users = UserService.list_users()
        self.assertEqual(users.count(), 2)
        self.assertIn(user1, users)
        self.assertIn(user2, users)

    def test_get_user_statistics(self):
        """ユーザー統計取得テスト"""
        user = UserService.create_user(**self.user_data)
        
        # プロジェクト作成
        project = Project.objects.create(
            name='Test Project',
            created_by=user
        )
        
        # チケット作成
        Issue.objects.create(
            project=project,
            title='Test Issue',
            description='Test',
            created_by=user
        )
        
        # 通知作成
        Notification.objects.create(
            user=user,
            message='Test notification'
        )
        
        stats = UserService.get_user_statistics(user.id)
        
        self.assertEqual(stats['created_projects_count'], 1)
        self.assertEqual(stats['created_issues_count'], 1)
        self.assertEqual(stats['total_notifications'], 1)
        self.assertEqual(stats['unread_notifications'], 1)

    def test_get_user_statistics_nonexistent(self):
        """存在しないユーザーの統計取得テスト"""
        stats = UserService.get_user_statistics(99999)
        self.assertIsNone(stats)


class IssueServiceTest(TestCase):
    def setUp(self):
        # テストデータ作成
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            created_by=self.user
        )
        self.issue_data = {
            'project_id': self.project.id,
            'created_by_id': self.user.id,
            'title': 'Test Issue',
            'description': 'Test Description',
            'priority': 'medium'
        }

    def test_create_issue_success(self):
        """チケット作成成功テスト"""
        issue = IssueService.create_issue(**self.issue_data)
        
        self.assertEqual(issue.title, 'Test Issue')
        self.assertEqual(issue.project, self.project)
        self.assertEqual(issue.created_by, self.user)
        self.assertEqual(issue.priority, 'medium')
        self.assertEqual(issue.status, 'open')  # デフォルト値

    def test_create_issue_with_assigned_to(self):
        """担当者付きチケット作成テスト"""
        issue = IssueService.create_issue(
            **self.issue_data,
            assigned_to_id=self.user2.id
        )
        
        self.assertEqual(issue.assigned_to, self.user2)

    def test_create_issue_nonexistent_project(self):
        """存在しないプロジェクトでのエラーテスト"""
        with self.assertRaises(ValidationError) as context:
            IssueService.create_issue(
                project_id=99999,
                created_by_id=self.user.id,
                title='Test',
                description='Test'
            )
        self.assertIn('プロジェクトが存在しません', str(context.exception))

    def test_create_issue_nonexistent_user(self):
        """存在しない作成者でのエラーテスト"""
        with self.assertRaises(ValidationError):
            IssueService.create_issue(
                project_id=self.project.id,
                created_by_id=99999,
                title='Test',
                description='Test'
            )

    def test_create_issue_empty_title(self):
        """空タイトルでのエラーテスト"""
        with self.assertRaises(ValidationError) as context:
            IssueService.create_issue(
                project_id=self.project.id,
                created_by_id=self.user.id,
                title='   ',  # 空白のみ
                description='Test Description',
                priority='medium'
            )
        self.assertIn('タイトルは必須です', str(context.exception))

    def test_create_issue_invalid_priority(self):
        """無効な優先度でのエラーテスト"""
        with self.assertRaises(ValidationError):
            IssueService.create_issue(
                project_id=self.project.id,
                created_by_id=self.user.id,
                title='Test Issue',
                description='Test Description',
                priority='invalid_priority'
            )

    def test_get_issue_by_id(self):
        """ID指定チケット取得テスト"""
        issue = IssueService.create_issue(**self.issue_data)
        
        found_issue = IssueService.get_issue_by_id(issue.id)
        self.assertEqual(found_issue.id, issue.id)
        
        # 存在しないID
        not_found = IssueService.get_issue_by_id(99999)
        self.assertIsNone(not_found)

    def test_list_issues(self):
        """チケット一覧取得テスト"""
        issue1 = IssueService.create_issue(**self.issue_data)
        issue2 = IssueService.create_issue(
            project_id=self.project.id,
            created_by_id=self.user.id,
            title='Issue 2',
            description='Test Description',
            priority='medium',
            assigned_to_id=self.user2.id
        )
        
        # 全体一覧
        all_issues = IssueService.list_issues()
        self.assertEqual(all_issues.count(), 2)
        
        # プロジェクト指定
        project_issues = IssueService.list_issues(project_id=self.project.id)
        self.assertEqual(project_issues.count(), 2)
        
        # 担当者指定
        assigned_issues = IssueService.list_issues(assigned_to_id=self.user2.id)
        self.assertEqual(assigned_issues.count(), 1)
        self.assertEqual(assigned_issues.first(), issue2)

    def test_update_issue_success(self):
        """チケット更新成功テスト"""
        issue = IssueService.create_issue(**self.issue_data)
        
        updated_issue = IssueService.update_issue(
            issue.id,
            self.user.id,
            title='Updated Title',
            priority='high'
        )
        
        self.assertEqual(updated_issue.title, 'Updated Title')
        self.assertEqual(updated_issue.priority, 'high')
        
        # 履歴が作成されることを確認
        history = IssueHistory.objects.filter(issue=issue)
        self.assertEqual(history.count(), 2)  # title と priority の変更

    def test_update_issue_assigned_to(self):
        """担当者変更テスト"""
        issue = IssueService.create_issue(**self.issue_data)
        
        updated_issue = IssueService.update_issue(
            issue.id,
            self.user.id,
            assigned_to_id=self.user2.id
        )
        
        self.assertEqual(updated_issue.assigned_to, self.user2)

    def test_update_issue_nonexistent(self):
        """存在しないチケット更新エラーテスト"""
        with self.assertRaises(Issue.DoesNotExist):
            IssueService.update_issue(99999, self.user.id, title='Test')

    def test_change_status_success(self):
        """ステータス変更成功テスト"""
        issue = IssueService.create_issue(**self.issue_data)
        
        updated_issue = IssueService.change_status(
            issue.id,
            'in_progress',
            self.user.id
        )
        
        self.assertEqual(updated_issue.status, 'in_progress')
        
        # 履歴確認
        history = IssueHistory.objects.filter(
            issue=issue,
            field_name='status'
        ).first()
        self.assertIsNotNone(history)
        self.assertEqual(history.old_value, 'open')
        self.assertEqual(history.new_value, 'in_progress')

    def test_change_status_invalid(self):
        """無効なステータス変更エラーテスト"""
        issue = IssueService.create_issue(**self.issue_data)
        
        with self.assertRaises(ValidationError):
            IssueService.change_status(
                issue.id,
                'invalid_status',
                self.user.id
            )

    def test_assign_issue_success(self):
        """担当者変更成功テスト"""
        issue = IssueService.create_issue(**self.issue_data)
        
        updated_issue = IssueService.assign_issue(
            issue.id,
            self.user2.id,
            self.user.id
        )
        
        self.assertEqual(updated_issue.assigned_to, self.user2)
        
        # 履歴確認
        history = IssueHistory.objects.filter(
            issue=issue,
            field_name='assigned_to'
        ).first()
        self.assertIsNotNone(history)

    def test_assign_issue_unassign(self):
        """担当者解除テスト"""
        issue = IssueService.create_issue(
            **self.issue_data,
            assigned_to_id=self.user2.id
        )
        
        updated_issue = IssueService.assign_issue(
            issue.id,
            None,  # 未割当
            self.user.id
        )
        
        self.assertIsNone(updated_issue.assigned_to)

    def test_delete_issue_success(self):
        """チケット削除成功テスト"""
        issue = IssueService.create_issue(**self.issue_data)
        issue_id = issue.id
        
        result = IssueService.delete_issue(issue_id, self.user.id)
        self.assertTrue(result)
        
        # 削除確認
        with self.assertRaises(Issue.DoesNotExist):
            Issue.objects.get(id=issue_id)

    def test_add_comment_success(self):
        """コメント追加成功テスト"""
        issue = IssueService.create_issue(**self.issue_data)
        
        comment = IssueService.add_comment(
            issue.id,
            self.user.id,
            'Test comment'
        )
        
        self.assertEqual(comment.issue, issue)
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.content, 'Test comment')

    def test_add_comment_empty(self):
        """空コメント追加エラーテスト"""
        issue = IssueService.create_issue(**self.issue_data)
        
        with self.assertRaises(ValidationError) as context:
            IssueService.add_comment(issue.id, self.user.id, '   ')
        self.assertIn('コメント内容は必須です', str(context.exception))

    def test_get_issue_history(self):
        """チケット履歴取得テスト"""
        issue = IssueService.create_issue(**self.issue_data)
        
        # 履歴を作るための変更
        IssueService.change_status(issue.id, 'in_progress', self.user.id)
        IssueService.assign_issue(issue.id, self.user2.id, self.user.id)
        
        history = IssueService.get_issue_history(issue.id)
        self.assertEqual(history.count(), 2)  # status と assigned_to の変更

    def test_get_issue_comments(self):
        """チケットコメント取得テスト"""
        issue = IssueService.create_issue(**self.issue_data)
        
        # コメント追加
        IssueService.add_comment(issue.id, self.user.id, 'Comment 1')
        IssueService.add_comment(issue.id, self.user2.id, 'Comment 2')
        
        comments = IssueService.get_issue_comments(issue.id)
        self.assertEqual(comments.count(), 2)
        self.assertEqual(comments.first().content, 'Comment 1')

    def test_get_issue_statistics(self):
        """チケット統計取得テスト"""
        # テストデータ作成
        IssueService.create_issue(**self.issue_data)  # medium, open
        IssueService.create_issue(
            project_id=self.project.id,
            created_by_id=self.user.id,
            title='Issue 2',
            description='Test Description',
            priority='high'
        )
        
        # プロジェクト指定統計
        project_stats = IssueService.get_issue_statistics(self.project.id)
        self.assertIsNotNone(project_stats)
        self.assertEqual(project_stats.total_issues, 2)
        
        # 全体統計
        global_stats = IssueService.get_issue_statistics()
        self.assertEqual(global_stats['total_issues'], 2)
        self.assertEqual(global_stats['by_status']['open'], 2)
        self.assertEqual(global_stats['by_priority']['medium'], 1)
        self.assertEqual(global_stats['by_priority']['high'], 1)


class NotificationServiceTest(TestCase):
    def setUp(self):
        # テストデータ作成
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        self.notification_message = "これはテスト通知です"

    def test_create_notification_success(self):
        """通知作成成功テスト"""
        notification = NotificationService.create_notification(
            self.user.id,
            self.notification_message
        )
        
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.message, self.notification_message)
        self.assertFalse(notification.is_read)
        self.assertIsNotNone(notification.created_at)

    def test_create_notification_nonexistent_user(self):
        """存在しないユーザーでのエラーテスト"""
        with self.assertRaises(ValidationError) as context:
            NotificationService.create_notification(99999, self.notification_message)
        self.assertIn('指定されたユーザーが存在しません', str(context.exception))

    def test_create_notification_empty_message(self):
        """空メッセージでのエラーテスト"""
        with self.assertRaises(ValidationError) as context:
            NotificationService.create_notification(self.user.id, '   ')
        self.assertIn('通知メッセージは必須です', str(context.exception))

    def test_get_notifications_success(self):
        """通知一覧取得成功テスト"""
        # テストデータ作成
        notification1 = NotificationService.create_notification(
            self.user.id, "通知1"
        )
        notification2 = NotificationService.create_notification(
            self.user.id, "通知2"
        )
        # 他のユーザーの通知も作成
        NotificationService.create_notification(
            self.user2.id, "他のユーザー通知"
        )
        
        # 全通知取得
        notifications = NotificationService.get_notifications(self.user.id)
        self.assertEqual(notifications.count(), 2)
        
        # 未読のみ取得
        unread_notifications = NotificationService.get_notifications(
            self.user.id, unread_only=True
        )
        self.assertEqual(unread_notifications.count(), 2)

    def test_get_notifications_nonexistent_user(self):
        """存在しないユーザーでのエラーテスト"""
        with self.assertRaises(ValidationError) as context:
            NotificationService.get_notifications(99999)
        self.assertIn('指定されたユーザーが存在しません', str(context.exception))

    def test_get_notification_by_id(self):
        """ID指定通知取得テスト"""
        notification = NotificationService.create_notification(
            self.user.id, self.notification_message
        )
        
        found_notification = NotificationService.get_notification_by_id(notification.id)
        self.assertEqual(found_notification.id, notification.id)
        
        # 存在しないID
        not_found = NotificationService.get_notification_by_id(99999)
        self.assertIsNone(not_found)

    def test_mark_as_read_success(self):
        """通知既読化成功テスト"""
        notification = NotificationService.create_notification(
            self.user.id, self.notification_message
        )
        
        # 既読化実行
        updated_notification = NotificationService.mark_as_read(notification.id)
        self.assertTrue(updated_notification.is_read)
        
        # 既に既読の場合
        already_read = NotificationService.mark_as_read(notification.id)
        self.assertTrue(already_read.is_read)

    def test_mark_as_read_nonexistent(self):
        """存在しない通知の既読化エラーテスト"""
        with self.assertRaises(Notification.DoesNotExist):
            NotificationService.mark_as_read(99999)

    def test_mark_all_as_read_success(self):
        """全通知既読化成功テスト"""
        # 複数の通知を作成
        NotificationService.create_notification(self.user.id, "通知1")
        NotificationService.create_notification(self.user.id, "通知2")
        NotificationService.create_notification(self.user.id, "通知3")
        
        # 全て既読化
        updated_count = NotificationService.mark_all_as_read(self.user.id)
        self.assertEqual(updated_count, 3)
        
        # 確認
        unread_count = NotificationService.get_unread_count(self.user.id)
        self.assertEqual(unread_count, 0)

    def test_mark_all_as_read_nonexistent_user(self):
        """存在しないユーザーの全既読化エラーテスト"""
        with self.assertRaises(ValidationError) as context:
            NotificationService.mark_all_as_read(99999)
        self.assertIn('指定されたユーザーが存在しません', str(context.exception))

    def test_delete_notification_success(self):
        """通知削除成功テスト"""
        notification = NotificationService.create_notification(
            self.user.id, self.notification_message
        )
        notification_id = notification.id
        
        # 削除実行
        result = NotificationService.delete_notification(notification_id, self.user.id)
        self.assertTrue(result)
        
        # 削除確認
        deleted_notification = NotificationService.get_notification_by_id(notification_id)
        self.assertIsNone(deleted_notification)

    def test_delete_notification_permission_denied(self):
        """権限なしでの削除エラーテスト"""
        notification = NotificationService.create_notification(
            self.user.id, self.notification_message
        )
        
        # 他のユーザーでの削除試行
        with self.assertRaises(ValidationError) as context:
            NotificationService.delete_notification(notification.id, self.user2.id)
        self.assertIn('この通知を削除する権限がありません', str(context.exception))

    def test_delete_notification_nonexistent(self):
        """存在しない通知の削除エラーテスト"""
        with self.assertRaises(Notification.DoesNotExist):
            NotificationService.delete_notification(99999)

    def test_get_unread_count(self):
        """未読通知数取得テスト"""
        # 通知作成
        NotificationService.create_notification(self.user.id, "通知1")
        NotificationService.create_notification(self.user.id, "通知2")
        notification3 = NotificationService.create_notification(self.user.id, "通知3")
        
        # 初期状態（全て未読）
        unread_count = NotificationService.get_unread_count(self.user.id)
        self.assertEqual(unread_count, 3)
        
        # 1つ既読化
        NotificationService.mark_as_read(notification3.id)
        unread_count = NotificationService.get_unread_count(self.user.id)
        self.assertEqual(unread_count, 2)

    def test_get_unread_count_nonexistent_user(self):
        """存在しないユーザーの未読数取得エラーテスト"""
        with self.assertRaises(ValidationError) as context:
            NotificationService.get_unread_count(99999)
        self.assertIn('指定されたユーザーが存在しません', str(context.exception))

    def test_bulk_create_notifications_success(self):
        """一括通知作成成功テスト"""
        user_ids = [self.user.id, self.user2.id]
        message = "一括通知テスト"
        
        notifications = NotificationService.bulk_create_notifications(user_ids, message)
        self.assertEqual(len(notifications), 2)
        
        # 各ユーザーの通知を確認
        user1_notifications = NotificationService.get_notifications(self.user.id)
        user2_notifications = NotificationService.get_notifications(self.user2.id)
        self.assertEqual(user1_notifications.count(), 1)
        self.assertEqual(user2_notifications.count(), 1)

    def test_bulk_create_notifications_empty_message(self):
        """一括通知作成空メッセージエラーテスト"""
        with self.assertRaises(ValidationError) as context:
            NotificationService.bulk_create_notifications([self.user.id], '   ')
        self.assertIn('通知メッセージは必須です', str(context.exception))

    def test_bulk_create_notifications_empty_users(self):
        """一括通知作成ユーザーなしエラーテスト"""
        with self.assertRaises(ValidationError) as context:
            NotificationService.bulk_create_notifications([], "テスト通知")
        self.assertIn('通知対象ユーザーが指定されていません', str(context.exception))

    def test_bulk_create_notifications_invalid_users(self):
        """一括通知作成無効ユーザーエラーテスト"""
        with self.assertRaises(ValidationError) as context:
            NotificationService.bulk_create_notifications(
                [self.user.id, 99999], "テスト通知"
            )
        self.assertIn('存在しないユーザーID', str(context.exception))

    def test_get_notification_statistics_user_specific(self):
        """ユーザー固有通知統計取得テスト"""
        # ユーザー1の通知
        NotificationService.create_notification(self.user.id, "通知1")
        notification2 = NotificationService.create_notification(self.user.id, "通知2")
        NotificationService.mark_as_read(notification2.id)
        
        # ユーザー2の通知
        NotificationService.create_notification(self.user2.id, "通知3")
        
        # ユーザー1の統計
        stats = NotificationService.get_notification_statistics(self.user.id)
        self.assertEqual(stats['total_notifications'], 2)
        self.assertEqual(stats['unread_notifications'], 1)
        self.assertEqual(stats['read_notifications'], 1)
        self.assertEqual(stats['unread_percentage'], 50.0)

    def test_get_notification_statistics_global(self):
        """全体通知統計取得テスト"""
        # 複数ユーザーの通知作成
        NotificationService.create_notification(self.user.id, "通知1")
        notification2 = NotificationService.create_notification(self.user.id, "通知2")
        NotificationService.create_notification(self.user2.id, "通知3")
        NotificationService.mark_as_read(notification2.id)
        
        # 全体統計
        stats = NotificationService.get_notification_statistics()
        self.assertEqual(stats['total_notifications'], 3)
        self.assertEqual(stats['unread_notifications'], 2)
        self.assertEqual(stats['read_notifications'], 1)
        self.assertAlmostEqual(stats['unread_percentage'], 66.67, places=1)

    def test_get_notification_statistics_nonexistent_user(self):
        """存在しないユーザーの統計取得エラーテスト"""
        with self.assertRaises(ValidationError) as context:
            NotificationService.get_notification_statistics(99999)
        self.assertIn('指定されたユーザーが存在しません', str(context.exception))


class SystemSettingsServiceTest(TestCase):
    def setUp(self):
        # 初期化（デフォルト値にリセット）
        SystemSettingsService.reset_to_defaults()

    def test_get_settings_default(self):
        """デフォルト設定取得テスト"""
        settings = SystemSettingsService.get_settings()
        self.assertFalse(settings.maintenance_mode)
        self.assertEqual(settings.email_sender, "")

    def test_update_settings_success(self):
        """設定更新成功テスト"""
        updated = SystemSettingsService.update_settings(
            maintenance_mode=True,
            email_sender="admin@example.com"
        )
        self.assertTrue(updated.maintenance_mode)
        self.assertEqual(updated.email_sender, "admin@example.com")

    def test_update_settings_invalid_email(self):
        """無効なメールアドレスでのエラーテスト"""
        with self.assertRaises(ValidationError) as context:
            SystemSettingsService.update_settings(
                email_sender="invalid-email"
            )
        self.assertIn("email_senderは有効なメールアドレス形式", str(context.exception))

    def test_update_settings_invalid_maintenance_mode(self):
        """maintenance_mode型不正エラーテスト"""
        with self.assertRaises(ValidationError) as context:
            SystemSettingsService.update_settings(
                maintenance_mode="yes"
            )
        self.assertIn("maintenance_modeはboolean値", str(context.exception))

    def test_update_settings_unknown_field(self):
        """未知フィールドエラーテスト"""
        with self.assertRaises(ValidationError) as context:
            SystemSettingsService.update_settings(
                unknown_field=True
            )
        self.assertIn("未知の設定項目", str(context.exception))

    def test_set_maintenance_mode(self):
        """メンテナンスモード設定テスト"""
        updated = SystemSettingsService.set_maintenance_mode(True)
        self.assertTrue(updated.maintenance_mode)
        updated = SystemSettingsService.set_maintenance_mode(False)
        self.assertFalse(updated.maintenance_mode)

    def test_set_email_sender(self):
        """送信元メールアドレス設定テスト"""
        updated = SystemSettingsService.set_email_sender("noreply@example.com")
        self.assertEqual(updated.email_sender, "noreply@example.com")

    def test_is_maintenance_mode(self):
        """メンテナンスモード状態取得テスト"""
        SystemSettingsService.set_maintenance_mode(True)
        self.assertTrue(SystemSettingsService.is_maintenance_mode())
        SystemSettingsService.set_maintenance_mode(False)
        self.assertFalse(SystemSettingsService.is_maintenance_mode())

    def test_get_email_sender(self):
        """送信元メールアドレス取得テスト"""
        SystemSettingsService.set_email_sender("info@example.com")
        self.assertEqual(SystemSettingsService.get_email_sender(), "info@example.com")

    def test_reset_to_defaults(self):
        """デフォルト値リセットテスト"""
        SystemSettingsService.update_settings(
            maintenance_mode=True,
            email_sender="admin@example.com"
        )
        reset = SystemSettingsService.reset_to_defaults()
        self.assertFalse(reset.maintenance_mode)
        self.assertEqual(reset.email_sender, "")

    def test_validate_settings_success(self):
        """バリデーション成功テスト"""
        valid = SystemSettingsService.validate_settings({
            "maintenance_mode": True,
            "email_sender": "test@example.com"
        })
        self.assertTrue(valid)

    def test_validate_settings_invalid(self):
        """バリデーション失敗テスト"""
        with self.assertRaises(ValidationError):
            SystemSettingsService.validate_settings({
                "maintenance_mode": "yes"
            })
        with self.assertRaises(ValidationError):
            SystemSettingsService.validate_settings({
                "email_sender": "invalid-email"
            })
        with self.assertRaises(ValidationError):
            SystemSettingsService.validate_settings({
                "unknown_field": True
            })

    def test_get_settings_dict(self):
        """設定辞書取得テスト"""
        SystemSettingsService.update_settings(
            maintenance_mode=True,
            email_sender="admin@example.com"
        )
        settings_dict = SystemSettingsService.get_settings_dict()
        self.assertEqual(settings_dict["maintenance_mode"], True)
        self.assertEqual(settings_dict["email_sender"], "admin@example.com")

    def test_update_from_dict_success(self):
        """辞書から設定更新成功テスト"""
        result = SystemSettingsService.update_from_dict({
            "maintenance_mode": True,
            "email_sender": "admin@example.com"
        })
        self.assertEqual(result["maintenance_mode"], True)
        self.assertEqual(result["email_sender"], "admin@example.com")

    def test_update_from_dict_invalid(self):
        """辞書から設定更新失敗テスト"""
        with self.assertRaises(ValidationError):
            SystemSettingsService.update_from_dict({
                "maintenance_mode": "yes"
            })
        with self.assertRaises(ValidationError):
            SystemSettingsService.update_from_dict({
                "email_sender": "invalid-email"
            })
        with self.assertRaises(ValidationError):
            SystemSettingsService.update_from_dict({
                "unknown_field": True
            })


class UserAPITest(TestCase):
    def setUp(self):
        # テストデータ作成
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='regularpass123'
        )

    def test_create_user_success(self):
        """ユーザー作成API成功テスト"""
        from django.test import RequestFactory
        import json
        
        factory = RequestFactory()
        request = factory.post(
            '/api/users/',
            data=json.dumps(self.user_data),
            content_type='application/json'
        )
        
        response = create_user(request)
        self.assertEqual(response.status_code, 201)
        
        response_data = json.loads(response.content)
        self.assertIn('id', response_data)
        self.assertEqual(response_data['username'], 'testuser')
        self.assertEqual(response_data['email'], 'test@example.com')
        self.assertIn('created_at', response_data)

    def test_create_user_missing_field(self):
        """ユーザー作成API必須フィールド不足エラーテスト"""
        from django.test import RequestFactory
        import json
        
        factory = RequestFactory()
        incomplete_data = {'username': 'testuser', 'email': 'test@example.com'}
        request = factory.post(
            '/api/users/',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        
        response = create_user(request)
        self.assertEqual(response.status_code, 400)
        
        response_data = json.loads(response.content)
        self.assertIn('Missing required field: password', response_data['error'])

    def test_create_user_invalid_json(self):
        """ユーザー作成API無効JSON エラーテスト"""
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.post(
            '/api/users/',
            data='invalid json',
            content_type='application/json'
        )
        
        response = create_user(request)
        self.assertEqual(response.status_code, 400)
        
        response_data = json.loads(response.content)
        self.assertEqual(response_data['error'], 'Invalid JSON format')

    def test_get_user_success(self):
        """ユーザー取得API成功テスト"""
        from django.test import RequestFactory
        import json
        
        factory = RequestFactory()
        request = factory.get(f'/api/users/{self.regular_user.id}/')
        request.user = self.regular_user
        
        response = get_user(request, self.regular_user.id)
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertEqual(response_data['id'], self.regular_user.id)
        self.assertEqual(response_data['username'], 'regular')
        self.assertEqual(response_data['email'], 'regular@example.com')

    def test_get_user_not_found(self):
        """ユーザー取得API存在しないユーザーエラーテスト"""
        from django.test import RequestFactory
        import json
        
        factory = RequestFactory()
        request = factory.get('/api/users/99999/')
        request.user = self.regular_user
        
        response = get_user(request, 99999)
        self.assertEqual(response.status_code, 404)
        
        response_data = json.loads(response.content)
        self.assertEqual(response_data['error'], 'User not found')


class NotificationAPITest(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        self.User = get_user_model()
        self.factory = RequestFactory()
        self.user = self.User.objects.create_user(
            username='notifyuser', email='notify@example.com', password='pass123'
        )
        self.admin = self.User.objects.create_user(
            username='admin', email='admin@example.com', password='admin123', is_staff=True
        )
        # Create sample notifications
        self.n1 = Notification.objects.create(user=self.user, message='Hello 1')
        self.n2 = Notification.objects.create(user=self.user, message='Hello 2')

    def test_list_notifications_self(self):
        request = self.factory.get('/api/notifications')
        request.user = self.user
        response = list_notifications(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)
        self.assertEqual({d['message'] for d in data}, {'Hello 1', 'Hello 2'})

    def test_list_notifications_unread_only(self):
        # mark one as read
        self.n1.mark_as_read()
        request = self.factory.get('/api/notifications?unread_only=true')
        request.user = self.user
        response = list_notifications(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], self.n2.id)

    def test_mark_notification_read_owner(self):
        request = self.factory.patch(f'/api/notifications/{self.n2.id}/read')
        request.user = self.user
        response = mark_notification_read(request, self.n2.id)
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertTrue(payload['is_read'])

    def test_mark_notification_read_not_found(self):
        request = self.factory.patch('/api/notifications/99999/read')
        request.user = self.user
        response = mark_notification_read(request, 99999)
        self.assertEqual(response.status_code, 404)
        payload = json.loads(response.content)
        self.assertIn('error', payload)

    def test_mark_notification_read_forbidden(self):
        other = self.User.objects.create_user(
            username='other', email='other@example.com', password='x'
        )
        other_n = Notification.objects.create(user=other, message='Other msg')
        request = self.factory.patch(f'/api/notifications/{other_n.id}/read')
        request.user = self.user
        response = mark_notification_read(request, other_n.id)
        self.assertEqual(response.status_code, 403)

    def test_delete_notification_owner(self):
        request = self.factory.delete(f'/api/notifications/{self.n1.id}')
        request.user = self.user
        response = delete_notification(request, self.n1.id)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Notification.objects.filter(id=self.n1.id).exists())

    def test_delete_notification_admin(self):
        request = self.factory.delete(f'/api/notifications/{self.n2.id}')
        request.user = self.admin
        response = delete_notification(request, self.n2.id)
        self.assertEqual(response.status_code, 200)

    def test_delete_notification_forbidden(self):
        other = self.User.objects.create_user(
            username='other2', email='other2@example.com', password='x'
        )
        other_n = Notification.objects.create(user=other, message='Other msg 2')
        request = self.factory.delete(f'/api/notifications/{other_n.id}')
        request.user = self.user
        response = delete_notification(request, other_n.id)
        self.assertEqual(response.status_code, 403)


class IssueAPITest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='iss', email='iss@example.com', password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='iss2', email='iss2@example.com', password='pass123'
        )
        self.project = Project.objects.create(
            name='P1', description='proj', created_by=self.user
        )

    def _create_issue(self):
        from tracker.api.issue_api import create_issue
        payload = {
            'project_id': self.project.id,
            'title': 'T',
            'description': 'D',
            'priority': 'medium',
        }
        req = self.factory.post('/api/issues', data=json.dumps(payload), content_type='application/json')
        req.user = self.user
        return create_issue(req)

    def test_create_issue_success(self):
        from tracker.api.issue_api import create_issue
        payload = {
            'project_id': self.project.id,
            'title': 'Title',
            'description': 'Desc',
            'priority': 'high',
            'assigned_to_id': self.user2.id,
        }
        req = self.factory.post('/api/issues', data=json.dumps(payload), content_type='application/json')
        req.user = self.user
        res = create_issue(req)
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.content)
        self.assertEqual(data['title'], 'Title')
        self.assertEqual(data['assigned_to'], self.user2.id)

    def test_get_update_delete_issue(self):
        from tracker.api.issue_api import get_issue, update_issue, delete_issue
        res = self._create_issue()
        issue_id = json.loads(res.content)['id']

        # get
        req = self.factory.get(f'/api/issues/{issue_id}')
        req.user = self.user
        r = get_issue(req, issue_id)
        self.assertEqual(r.status_code, 200)

        # update
        upd = {'title': 'New', 'priority': 'low'}
        req2 = self.factory.put(f'/api/issues/{issue_id}', data=json.dumps(upd), content_type='application/json')
        req2.user = self.user
        r2 = update_issue(req2, issue_id)
        self.assertEqual(r2.status_code, 200)
        data2 = json.loads(r2.content)
        self.assertEqual(data2['title'], 'New')
        self.assertEqual(data2['priority'], 'low')

        # delete
        req3 = self.factory.delete(f'/api/issues/{issue_id}')
        req3.user = self.user
        r3 = delete_issue(req3, issue_id)
        self.assertEqual(r3.status_code, 200)

    def test_list_and_status_and_assign_and_comments(self):
        from tracker.api.issue_api import list_issues, change_issue_status, assign_issue, add_comment, list_comments
        # create two issues
        self._create_issue()
        self._create_issue()

        # list
        req = self.factory.get('/api/issues')
        req.user = self.user
        r = list_issues(req)
        self.assertEqual(r.status_code, 200)
        arr = json.loads(r.content)
        self.assertGreaterEqual(len(arr), 2)

        # status change
        issue_id = arr[0]['id']
        req2 = self.factory.patch(f'/api/issues/{issue_id}/status', data=json.dumps({'status': 'in_progress'}), content_type='application/json')
        req2.user = self.user
        r2 = change_issue_status(req2, issue_id)
        self.assertEqual(r2.status_code, 200)

        # assign
        req3 = self.factory.patch(f'/api/issues/{issue_id}/assignee', data=json.dumps({'assigned_to_id': self.user2.id}), content_type='application/json')
        req3.user = self.user
        r3 = assign_issue(req3, issue_id)
        self.assertEqual(r3.status_code, 200)

        # add comment
        req4 = self.factory.post(f'/api/issues/{issue_id}/comments', data=json.dumps({'content': 'hello'}), content_type='application/json')
        req4.user = self.user
        r4 = add_comment(req4, issue_id)
        self.assertEqual(r4.status_code, 201)

        # list comments
        req5 = self.factory.get(f'/api/issues/{issue_id}/comments')
        req5.user = self.user
        r5 = list_comments(req5, issue_id)
        self.assertEqual(r5.status_code, 200)
        comms = json.loads(r5.content)
        self.assertEqual(comms[0]['content'], 'hello')


class StatisticsAPITest(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        self.User = get_user_model()
        self.factory = RequestFactory()
        self.user = self.User.objects.create_user(
            username='statsuser', email='stats@example.com', password='pass123'
        )
        self.other_user = self.User.objects.create_user(
            username='otheruser', email='other@example.com', password='pass123'
        )
        self.admin = self.User.objects.create_user(
            username='admin', email='admin@example.com', password='admin123', is_staff=True
        )
        
        # Create test project
        self.project = Project.objects.create(
            name='Test Project', description='Test project', created_by=self.user
        )
        
        # Create some test issues for statistics
        Issue.objects.create(
            project=self.project, title='Issue 1', description='Desc 1',
            created_by=self.user, status='open', priority='high'
        )
        Issue.objects.create(
            project=self.project, title='Issue 2', description='Desc 2',
            created_by=self.user, status='closed', priority='medium'
        )

    def test_get_project_statistics_owner(self):
        from tracker.api.statistics_api import get_project_statistics
        request = self.factory.get(f'/api/projects/{self.project.id}/stats')
        request.user = self.user  # Project owner
        response = get_project_statistics(request, self.project.id)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['project_id'], self.project.id)
        self.assertIn('total_issues', data)
        self.assertIn('open', data)  # Interface design uses 'open', not 'open_issues'
        self.assertIn('closed', data)
        self.assertIn('by_priority', data)

    def test_get_project_statistics_project_member(self):
        from tracker.api.statistics_api import get_project_statistics
        # Add other_user as project member
        ProjectMember.objects.create(project=self.project, user=self.other_user, role='member')
        
        request = self.factory.get(f'/api/projects/{self.project.id}/stats')
        request.user = self.other_user  # Project member
        response = get_project_statistics(request, self.project.id)
        self.assertEqual(response.status_code, 200)

    def test_get_project_statistics_admin(self):
        from tracker.api.statistics_api import get_project_statistics
        request = self.factory.get(f'/api/projects/{self.project.id}/stats')
        request.user = self.admin  # Admin user
        response = get_project_statistics(request, self.project.id)
        self.assertEqual(response.status_code, 200)

    def test_get_project_statistics_forbidden(self):
        from tracker.api.statistics_api import get_project_statistics
        unrelated_user = self.User.objects.create_user(
            username='unrelated', email='unrelated@example.com', password='pass123'
        )
        request = self.factory.get(f'/api/projects/{self.project.id}/stats')
        request.user = unrelated_user  # No permission
        response = get_project_statistics(request, self.project.id)
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.content)
        self.assertEqual(data['error'], 'Permission denied')

    def test_get_project_statistics_not_found(self):
        from tracker.api.statistics_api import get_project_statistics
        request = self.factory.get('/api/projects/99999/stats')
        request.user = self.admin  # Admin can access, but project doesn't exist
        response = get_project_statistics(request, 99999)
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertEqual(data['error'], 'Project not found')

    def test_get_project_statistics_authentication_required(self):
        from tracker.api.statistics_api import get_project_statistics
        from django.contrib.auth.models import AnonymousUser
        request = self.factory.get(f'/api/projects/{self.project.id}/stats')
        request.user = AnonymousUser()  # Not authenticated
        # @login_required decorator causes redirect (302) for AnonymousUser
        # In unit tests, we expect this behavior
        response = get_project_statistics(request, self.project.id)
        # The @login_required decorator returns 302 redirect for unauthenticated users
        self.assertEqual(response.status_code, 302)


class SystemSettingsAPITest(TestCase):
    """
    SystemSettings API のテストケース
    AT-301 to AT-304 as defined in api-test-design.md
    """
    
    def setUp(self):
        self.factory = RequestFactory()
        self.User = get_user_model()
        
        # テストユーザー作成
        self.admin = self.User.objects.create_user(
            username='admin', 
            email='admin@example.com', 
            password='adminpass123',
            is_staff=True,
            is_superuser=True
        )
        
        self.regular_user = self.User.objects.create_user(
            username='user', 
            email='user@example.com', 
            password='userpass123',
            is_staff=False
        )
    
    def test_get_system_settings_success(self):
        """AT-301: GET正常系 - 設定取得成功"""
        from tracker.api.system_settings_api import system_settings_api
        
        request = self.factory.get('/api/settings/')
        request.user = self.admin  # Staff user
        
        response = system_settings_api(request)
        self.assertEqual(response.status_code, 200)
        
        # レスポンス内容確認
        data = json.loads(response.content)
        self.assertIn('maintenance_mode', data)
        self.assertIn('email_sender', data)
        self.assertIsInstance(data['maintenance_mode'], bool)
        self.assertIsInstance(data['email_sender'], str)
    
    def test_get_system_settings_permission_denied(self):
        """AT-302: GET異常系 - 権限なし"""
        from tracker.api.system_settings_api import system_settings_api
        
        request = self.factory.get('/api/settings/')
        request.user = self.regular_user  # Non-staff user
        
        # @staff_member_required decorator causes redirect for non-staff users
        response = system_settings_api(request)
        self.assertEqual(response.status_code, 302)  # Redirect due to staff_member_required
    
    def test_update_system_settings_success(self):
        """AT-303: PUT正常系 - 設定更新成功"""
        from tracker.api.system_settings_api import system_settings_api
        
        # 更新データ
        update_data = {
            'maintenance_mode': True,
            'email_sender': 'admin@testsite.com'
        }
        
        request = self.factory.put(
            '/api/settings/',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        request.user = self.admin  # Staff user
        
        response = system_settings_api(request)
        self.assertEqual(response.status_code, 200)
        
        # レスポンス内容確認
        data = json.loads(response.content)
        self.assertEqual(data['maintenance_mode'], True)
        self.assertEqual(data['email_sender'], 'admin@testsite.com')
        
        # DB確認
        from tracker.services.system_settings_service import SystemSettingsService
        settings = SystemSettingsService.get_settings()
        self.assertTrue(settings.maintenance_mode)
        self.assertEqual(settings.email_sender, 'admin@testsite.com')
    
    def test_update_system_settings_invalid_data(self):
        """AT-304: PUT異常系 - 無効な値"""
        from tracker.api.system_settings_api import system_settings_api
        
        # 無効なデータ（maintenance_mode should be boolean）
        invalid_data = {
            'maintenance_mode': 'invalid_string',  # Should be boolean
            'email_sender': 'invalid-email-format'  # Invalid email
        }
        
        request = self.factory.put(
            '/api/settings/',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        request.user = self.admin  # Staff user
        
        response = system_settings_api(request)
        self.assertEqual(response.status_code, 400)
        
        # エラーメッセージ確認
        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Validation error')
    
    def test_system_settings_json_parse_error(self):
        """JSON パースエラーテスト"""
        from tracker.api.system_settings_api import system_settings_api
        
        request = self.factory.put(
            '/api/settings/',
            data='invalid json data',
            content_type='application/json'
        )
        request.user = self.admin
        
        response = system_settings_api(request)
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.content)
        self.assertEqual(data['error'], 'Invalid JSON format')
    
    def test_system_settings_authentication_required(self):
        """認証必須テスト"""
        from tracker.api.system_settings_api import system_settings_api
        from django.contrib.auth.models import AnonymousUser
        
        request = self.factory.get('/api/settings/')
        request.user = AnonymousUser()  # Not authenticated
        
        # @login_required decorator causes redirect for unauthenticated users
        response = system_settings_api(request)
        self.assertEqual(response.status_code, 302)  # Redirect due to login_required


class AuthenticationUITest(TestCase):
    """Login UI flow tests (Issue #17)"""
    def setUp(self):
        self.factory = RequestFactory()
        self.User = get_user_model()
        self.password = 'loginpass123'
        self.user = self.User.objects.create_user(
            username='loginuser', email='login@example.com', password=self.password
        )

    def _add_session(self, request):
        """Attach a session to a RequestFactory request."""
        from django.contrib.sessions.middleware import SessionMiddleware
        from django.contrib.messages.storage.fallback import FallbackStorage
        middleware = SessionMiddleware(lambda r: None)
        middleware.process_request(request)
        request.session.save()
        # Attach messages storage so views using django.contrib.messages work
        request._messages = FallbackStorage(request)

    def test_login_success_redirects_dashboard(self):
        # Use Django test client for full middleware (auth + messages)
        response = self.client.post('/login/', {
            'email': 'login@example.com',
            'password': self.password
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard', response.url)

    def test_login_failure_shows_error(self):
        response = self.client.post('/login/', {
            'email': 'login@example.com',
            'password': 'wrong'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('ログインに失敗しました', response.content.decode())

    def test_remember_me_sets_longer_expiry(self):
        response = self.client.post('/login/', {
            'email': 'login@example.com',
            'password': self.password,
            'remember_me': '1'
        })
        self.assertEqual(response.status_code, 302)
        # Access session via client
        session = self.client.session
        self.assertNotEqual(session.get_expiry_age(), 0)

    def test_non_remember_me_session_expires_on_browser_close(self):
        response = self.client.post('/login/', {
            'email': 'login@example.com',
            'password': self.password
        })
        self.assertEqual(response.status_code, 302)
        # Validate session is marked to expire at browser close
        session = self.client.session
        self.assertTrue(session.get_expire_at_browser_close())

    def test_dashboard_requires_login(self):
        from tracker.views import dashboard_view
        from django.contrib.auth.models import AnonymousUser
        request = self.factory.get('/dashboard/')
        request.user = AnonymousUser()
        response = dashboard_view(request)
        # login_required decorator redirects to login page
        self.assertEqual(response.status_code, 302)

    def test_logout_redirects_login(self):
        # Login first
        self.client.post('/login/', {
            'email': 'login@example.com',
            'password': self.password
        })
        # Then logout
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)


class UserManagementUITest(TestCase):
    """ユーザー管理UI機能のテストクラス"""
    
    def setUp(self):
        """テスト用データの準備"""
        self.factory = RequestFactory()
        
        # テスト用ユーザー作成
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True,
            is_superuser=False
        )
        
        self.regular_user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='regular123',
            is_staff=False
        )
        
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='test123',
            is_staff=False
        )

    def _setup_request_middleware(self, request, user):
        """RequestオブジェクトにSessionとMessageMiddlewareを設定"""
        # Session middleware setup
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        
        # User assignment
        request.user = user
        
        # Messages middleware setup
        messages_middleware = MessageMiddleware()
        messages_middleware.process_request(request)
        request._messages = FallbackStorage(request)
        
        return request

    def test_user_list_requires_staff_permission(self):
        """ユーザー一覧表示はスタッフ権限が必要"""
        # Regular user cannot access
        self.client.force_login(self.regular_user)
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, 302)  # Redirect due to permission denied
        
        # Staff user can access
        self.client.force_login(self.admin_user)
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, 200)

    def test_user_list_display(self):
        """ユーザー一覧の正常表示テスト (UT-101)"""
        self.client.force_login(self.admin_user)
        response = self.client.get('/users/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ユーザー管理')
        self.assertContains(response, self.admin_user.username)
        self.assertContains(response, self.regular_user.username)
        self.assertContains(response, self.test_user.username)

    def test_user_create_get(self):
        """ユーザー作成画面の表示テスト"""
        self.client.force_login(self.admin_user)
        response = self.client.get('/users/add/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '新規ユーザー作成')
        self.assertContains(response, 'ユーザー名')
        self.assertContains(response, 'メールアドレス')

    def test_user_create_success(self):
        """ユーザー作成の正常系テスト (UT-104)"""
        self.client.force_login(self.admin_user)
        
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'is_active': True,
            'is_staff': False
        }
        
        response = self.client.post('/users/add/', user_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        
        # Verify user was created
        new_user = User.objects.get(username='newuser')
        self.assertEqual(new_user.email, 'newuser@example.com')
        self.assertTrue(new_user.is_active)
        self.assertFalse(new_user.is_staff)

    def test_user_create_duplicate_email(self):
        """ユーザー作成での重複メールエラーテスト (UT-105)"""
        self.client.force_login(self.admin_user)
        
        user_data = {
            'username': 'duplicate',
            'email': 'admin@example.com',  # Already exists
            'password1': 'newpass123',
            'password2': 'newpass123',
            'is_active': True,
            'is_staff': False
        }
        
        response = self.client.post('/users/add/', user_data)
        self.assertEqual(response.status_code, 200)  # Form validation error, no redirect
        self.assertContains(response, 'このメールアドレスは既に使用されています')

    def test_user_create_validation_errors(self):
        """ユーザー作成での境界値・バリデーションテスト (UT-106)"""
        self.client.force_login(self.admin_user)
        
        # Empty username
        response = self.client.post('/users/add/', {
            'username': '',
            'email': 'empty@example.com',
            'password1': 'password123',
            'password2': 'password123',
        })
        self.assertEqual(response.status_code, 200)
        
        # Invalid email format
        response = self.client.post('/users/add/', {
            'username': 'validuser',
            'email': 'invalid-email',
            'password1': 'password123',
            'password2': 'password123',
        })
        self.assertEqual(response.status_code, 200)

    def test_user_edit_get(self):
        """ユーザー編集画面の表示テスト"""
        self.client.force_login(self.admin_user)
        response = self.client.get(f'/users/{self.test_user.id}/edit/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ユーザー編集')
        self.assertContains(response, self.test_user.username)

    def test_user_edit_success(self):
        """ユーザー編集の正常系テスト (UT-102)"""
        self.client.force_login(self.admin_user)
        
        edit_data = {
            'username': 'editeduser',
            'email': 'edited@example.com',
            'first_name': 'Edited',
            'last_name': 'User',
            'is_active': True,
            'is_staff': True
        }
        
        response = self.client.post(f'/users/{self.test_user.id}/edit/', edit_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful edit
        
        # Verify changes
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.username, 'editeduser')
        self.assertEqual(self.test_user.email, 'edited@example.com')
        self.assertEqual(self.test_user.first_name, 'Edited')
        self.assertTrue(self.test_user.is_staff)

    def test_user_delete_get(self):
        """ユーザー削除確認画面の表示テスト"""
        self.client.force_login(self.admin_user)
        response = self.client.get(f'/users/{self.test_user.id}/delete/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ユーザー削除確認')
        self.assertContains(response, self.test_user.username)
        self.assertContains(response, '危険な操作')

    def test_user_delete_success(self):
        """ユーザー削除の正常系テスト (UT-103)"""
        self.client.force_login(self.admin_user)
        user_id = self.test_user.id
        
        response = self.client.post(f'/users/{user_id}/delete/')
        self.assertEqual(response.status_code, 302)  # Redirect after deletion
        
        # Verify user was deleted
        self.assertFalse(User.objects.filter(id=user_id).exists())

    def test_user_delete_self_protection(self):
        """自分自身の削除防止テスト"""
        self.client.force_login(self.admin_user)
        
        response = self.client.post(f'/users/{self.admin_user.id}/delete/')
        self.assertEqual(response.status_code, 302)  # Redirects with error
        
        # Verify user was not deleted
        self.assertTrue(User.objects.filter(id=self.admin_user.id).exists())

    def test_user_password_reset_get(self):
        """パスワードリセット画面の表示テスト"""
        self.client.force_login(self.admin_user)
        response = self.client.get(f'/users/{self.test_user.id}/password-reset/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'パスワードリセット')
        self.assertContains(response, self.test_user.username)

    def test_user_password_reset_success(self):
        """パスワードリセットの正常系テスト"""
        self.client.force_login(self.admin_user)
        
        reset_data = {
            'new_password1': 'newpassword123',
            'new_password2': 'newpassword123'
        }
        
        response = self.client.post(f'/users/{self.test_user.id}/password-reset/', reset_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful reset
        
        # Verify password was changed
        self.test_user.refresh_from_db()
        self.assertTrue(self.test_user.check_password('newpassword123'))

    def test_user_search_functionality(self):
        """ユーザー検索機能のテスト"""
        self.client.force_login(self.admin_user)
        
        # Search by username
        response = self.client.get('/users/', {'search': 'admin'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.admin_user.username)
        self.assertNotContains(response, self.regular_user.username)

    def test_user_filter_by_status(self):
        """ユーザーステータスフィルターのテスト"""
        self.client.force_login(self.admin_user)
        
        # Create inactive user
        inactive_user = User.objects.create_user(
            username='inactive',
            email='inactive@example.com',
            password='inactive123',
            is_active=False
        )
        
        # Filter active users
        response = self.client.get('/users/', {'is_active': 'true'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, inactive_user.username)

    def test_user_toggle_active_ajax(self):
        """ユーザーアクティブ状態切り替えAJAXテスト"""
        self.client.force_login(self.admin_user)
        
        original_status = self.test_user.is_active
        response = self.client.post(f'/users/{self.test_user.id}/toggle-active/')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Verify status was toggled
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.is_active, not original_status)

    def test_user_management_pagination(self):
        """ユーザー一覧のページネーションテスト"""
        # Create many users to test pagination
        for i in range(25):
            User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password='password123'
            )
        
        self.client.force_login(self.admin_user)
        response = self.client.get('/users/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'page-link')  # Pagination controls present

    def test_user_management_requires_login(self):
        """ユーザー管理機能は認証が必要"""
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_user_management_permission_checks(self):
        """各ユーザー管理機能の権限チェック"""
        # Test all user management views require staff permission
        urls_to_test = [
            '/users/',
            '/users/add/',
            f'/users/{self.test_user.id}/edit/',
            f'/users/{self.test_user.id}/delete/',
            f'/users/{self.test_user.id}/password-reset/',
        ]
        
        # Regular user should be denied access
        self.client.force_login(self.regular_user)
        for url in urls_to_test:
            response = self.client.get(url)
            self.assertNotEqual(response.status_code, 200, f"Regular user should not access {url}")


class UserFormTest(TestCase):
    """ユーザー管理フォームのテストクラス"""
    
    def setUp(self):
        self.existing_user = User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='existing123'
        )

    def test_user_create_form_validation(self):
        """ユーザー作成フォームのバリデーションテスト"""
        from tracker.forms import UserCreateForm
        
        # Valid data
        valid_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'is_active': True,
            'is_staff': False
        }
        form = UserCreateForm(data=valid_data)
        self.assertTrue(form.is_valid())
        
        # Duplicate username
        duplicate_username = valid_data.copy()
        duplicate_username['username'] = 'existing'
        form = UserCreateForm(data=duplicate_username)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        
        # Duplicate email
        duplicate_email = valid_data.copy()
        duplicate_email['email'] = 'existing@example.com'
        form = UserCreateForm(data=duplicate_email)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_user_edit_form_validation(self):
        """ユーザー編集フォームのバリデーションテスト"""
        from tracker.forms import UserEditForm
        
        # Valid data
        valid_data = {
            'username': 'edited',
            'email': 'edited@example.com',
            'is_active': True,
            'is_staff': False
        }
        form = UserEditForm(data=valid_data, instance=self.existing_user)
        self.assertTrue(form.is_valid())
        
        # Same user can keep same username/email
        same_data = {
            'username': 'existing',
            'email': 'existing@example.com',
            'is_active': True,
            'is_staff': False
        }
        form = UserEditForm(data=same_data, instance=self.existing_user)
        self.assertTrue(form.is_valid())

    def test_user_search_form_filter(self):
        """ユーザー検索フォームのフィルター機能テスト"""
        from tracker.forms import UserSearchForm
        
        # Clear existing users to avoid interference
        User.objects.all().delete()
        
        # Create test users
        User.objects.create_user(username='testactive', email='testactive@example.com', is_active=True)
        User.objects.create_user(username='testinactive', email='testinactive@example.com', is_active=False)
        User.objects.create_user(username='teststaff', email='teststaff@example.com', is_staff=True, is_active=True)
        
        queryset = User.objects.all()
        
        # Test search filter
        form = UserSearchForm(data={'search': 'testactive'})
        self.assertTrue(form.is_valid())
        filtered = form.filter_queryset(queryset)
        # Should find exactly the 'testactive' user
        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first().username, 'testactive')
        
        # Test active filter
        form = UserSearchForm(data={'is_active': 'true'})
        self.assertTrue(form.is_valid())
        filtered = form.filter_queryset(queryset)
        active_count = User.objects.filter(is_active=True).count()
        self.assertEqual(filtered.count(), active_count)


class IssueListUITest(TestCase):
	"""チケット一覧画面UI機能のテストクラス"""
	
	def setUp(self):
		"""テスト用データの準備"""
		self.admin_user = User.objects.create_user(
			username='admin',
			email='admin@example.com',
			password='testpass123',
			is_staff=True
		)
		
		self.regular_user = User.objects.create_user(
			username='regular',
			email='regular@example.com',
			password='testpass123'
		)
		
		# テスト用プロジェクト作成
		from tracker.models import Project, Issue
		
		self.project1 = Project.objects.create(
			name='Test Project 1',
			description='Test project description',
			created_by=self.admin_user
		)
		
		self.project2 = Project.objects.create(
			name='Test Project 2', 
			description='Another test project',
			created_by=self.regular_user
		)
		
		# テスト用チケット作成
		self.issue1 = Issue.objects.create(
			title='Test Issue 1',
			description='Test issue description 1',
			project=self.project1,
			created_by=self.admin_user,
			assigned_to=self.regular_user,
			status='open',
			priority='high'
		)
		
		self.issue2 = Issue.objects.create(
			title='Test Issue 2',
			description='Test issue description 2',
			project=self.project2,
			created_by=self.regular_user,
			assigned_to=self.admin_user,
			status='in_progress',
			priority='medium'
		)
		
		self.issue3 = Issue.objects.create(
			title='Test Issue 3',
			description='Test issue description 3',
			project=self.project1,
			created_by=self.admin_user,
			status='closed',
			priority='low'
		)

	def test_issue_list_requires_login(self):
		"""チケット一覧表示はログインが必要"""
		response = self.client.get('/issues/')
		self.assertRedirects(response, '/login/?next=/issues/')

	def test_issue_list_display(self):
		"""チケット一覧の正常表示テスト (UT-201)"""
		self.client.force_login(self.admin_user)
		response = self.client.get('/issues/')
		
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'チケット一覧')
		self.assertContains(response, 'Test Issue 1')
		self.assertContains(response, 'Test Issue 2')
		self.assertContains(response, 'Test Issue 3')
		self.assertContains(response, 'Test Project 1')
		self.assertContains(response, 'Test Project 2')
		
		# 統計情報の確認
		self.assertContains(response, '全チケット')
		self.assertContains(response, '未完了')
		self.assertContains(response, '完了済み')
		
		# フィルターフォームの確認
		self.assertContains(response, '検索・フィルター')
		self.assertContains(response, 'name="search"')
		self.assertContains(response, 'name="status"')
		self.assertContains(response, 'name="priority"')
		self.assertContains(response, 'name="assigned_to"')

	def test_issue_list_search_filter(self):
		"""チケット一覧検索・フィルター機能テスト"""
		self.client.force_login(self.admin_user)
		
		# タイトル検索
		response = self.client.get('/issues/', {'search': 'Test Issue 1'})
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Test Issue 1')
		self.assertNotContains(response, 'Test Issue 2')
		
		# ステータスフィルター
		response = self.client.get('/issues/', {'status': 'open'})
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Test Issue 1')
		self.assertNotContains(response, 'Test Issue 2')
		
		# 優先度フィルター
		response = self.client.get('/issues/', {'priority': 'high'})
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Test Issue 1')
		self.assertNotContains(response, 'Test Issue 2')
		
		# 担当者フィルター
		response = self.client.get('/issues/', {'assigned_to': self.regular_user.id})
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Test Issue 1')
		self.assertNotContains(response, 'Test Issue 2')

	def test_issue_list_nonexistent_page(self):
		"""存在しないページ番号でのアクセステスト (UT-202)"""
		self.client.force_login(self.admin_user)
		
		# 存在しないページ番号
		response = self.client.get('/issues/', {'page': '999'})
		self.assertEqual(response.status_code, 200)  # 最後のページが表示される

	def test_issue_list_regular_user_access(self):
		"""一般ユーザーのアクセステスト"""
		self.client.force_login(self.regular_user)
		response = self.client.get('/issues/')
		
		self.assertEqual(response.status_code, 200)
		# 一般ユーザーでも全てのチケットが見える（設計通り）
		self.assertContains(response, 'チケット一覧')
		self.assertContains(response, 'Test Issue 1')
		self.assertContains(response, 'Test Issue 2')


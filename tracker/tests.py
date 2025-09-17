from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from tracker.models import Project, ProjectMember, Issue, IssueHistory, Comment, Notification, SystemSettings, Statistics
from tracker.services.user_service import UserService

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

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from tracker.models import Project, ProjectMember, Issue, IssueHistory, Comment, Notification

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

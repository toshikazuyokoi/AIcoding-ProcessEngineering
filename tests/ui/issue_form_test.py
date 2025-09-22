from django.test import TestCase
from django.contrib.auth import get_user_model


class IssueFormUITest(TestCase):
    """チケット作成・編集画面UI機能のテストクラス (modular)"""

    def setUp(self):
        User = get_user_model()
        self.admin_user = User.objects.create_user(
            username='admin3',
            email='admin3_issues@example.com',
            password='testpass123',
            is_staff=True
        )

        self.regular_user = User.objects.create_user(
            username='regular3',
            email='regular3_issues@example.com',
            password='testpass123'
        )

        from tracker.models import Project, Issue

        self.project = Project.objects.create(
            name='Form Test Project',
            description='Form test project description',
            created_by=self.admin_user
        )

        self.existing_issue = Issue.objects.create(
            title='Existing Issue for Edit',
            description='This is an existing issue for edit testing.',
            project=self.project,
            created_by=self.admin_user,
            priority='medium'
        )

    def test_issue_create_form_display(self):
        self.client.force_login(self.admin_user)
        response = self.client.get('/issues/new/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '新規チケット作成')
        self.assertContains(response, 'name="title"')
        self.assertContains(response, 'name="description"')
        self.assertContains(response, 'name="priority"')
        self.assertContains(response, 'name="assigned_to"')
        self.assertContains(response, 'name="due_date"')
        self.assertContains(response, 'name="project"')

        self.assertContains(response, '基本情報')
        self.assertContains(response, '割り当て情報')
        self.assertContains(response, '添付ファイル')

    def test_issue_create_success(self):
        self.client.force_login(self.admin_user)
        form_data = {
            'title': 'Test New Issue Title',
            'description': 'This is a test description for new issue creation.',
            'priority': 'high',
            'project': self.project.id,
            'assigned_to': self.regular_user.id,
            'due_date': '2025-12-31'
        }
        response = self.client.post('/issues/new/', form_data)

        self.assertEqual(response.status_code, 302)

        from tracker.models import Issue
        new_issue = Issue.objects.filter(title='Test New Issue Title').first()
        self.assertIsNotNone(new_issue)
        self.assertEqual(new_issue.created_by, self.admin_user)
        self.assertEqual(new_issue.project, self.project)

    def test_issue_create_validation_error(self):
        self.client.force_login(self.admin_user)
        form_data = {'title': '', 'description': '', 'priority': 'high'}
        response = self.client.post('/issues/new/', form_data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'この項目は必須です。')

    def test_issue_create_boundary_validation(self):
        self.client.force_login(self.admin_user)
        form_data = {'title': 'abc', 'description': 'Short description', 'priority': 'medium', 'project': self.project.id}
        response = self.client.post('/issues/new/', form_data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'タイトルは5文字以上で入力してください。')

    def test_issue_edit_form_display(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(f'/issues/{self.existing_issue.id}/edit/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'チケット編集')
        self.assertContains(response, f'#{self.existing_issue.id}')
        self.assertContains(response, 'Existing Issue for Edit')
        self.assertContains(response, 'value="medium" selected')

    def test_issue_edit_success(self):
        self.client.force_login(self.admin_user)
        form_data = {
            'title': 'Updated Issue Title',
            'description': 'This is an updated description for testing.',
            'priority': 'high',
            'project': self.project.id,
            'assigned_to': self.regular_user.id
        }
        response = self.client.post(f'/issues/{self.existing_issue.id}/edit/', form_data)

        self.assertEqual(response.status_code, 302)
        from tracker.models import Issue
        updated_issue = Issue.objects.get(id=self.existing_issue.id)
        self.assertEqual(updated_issue.title, 'Updated Issue Title')
        self.assertEqual(updated_issue.priority, 'high')

    def test_issue_edit_not_found(self):
        self.client.force_login(self.admin_user)
        response = self.client.get('/issues/999999/edit/')
        self.assertEqual(response.status_code, 404)

    def test_issue_form_requires_login(self):
        response = self.client.get('/issues/new/')
        self.assertRedirects(response, '/login/?next=/issues/new/')

        response = self.client.get(f'/issues/{self.existing_issue.id}/edit/')
        self.assertRedirects(response, f'/login/?next=/issues/{self.existing_issue.id}/edit/')
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class IssueFormUITest(TestCase):
    """Ported: チケット作成・編集画面UI機能のテストクラス"""

    def setUp(self):
        """テスト用データの準備"""
        self.admin_user = User.objects.create_user(
            username='admin3',
            email='admin3+ui@example.com',
            password='testpass123',
            is_staff=True
        )

        self.regular_user = User.objects.create_user(
            username='regular3',
            email='regular3+ui@example.com',
            password='testpass123'
        )

        # import models lazily to avoid top-level import cycles
        from tracker.models import Project, Issue

        self.project = Project.objects.create(
            name='Form Test Project',
            description='Form test project description',
            created_by=self.admin_user
        )

        self.existing_issue = Issue.objects.create(
            title='Existing Issue for Edit',
            description='This is an existing issue for edit testing.',
            project=self.project,
            created_by=self.admin_user,
            priority='medium'
        )

    def test_issue_create_form_display(self):
        """チケット作成フォームの正常表示テスト (UT-401)"""
        self.client.force_login(self.admin_user)
        response = self.client.get('/issues/new/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '新規チケット作成')
        self.assertContains(response, 'name="title"')
        self.assertContains(response, 'name="description"')
        self.assertContains(response, 'name="priority"')
        self.assertContains(response, 'name="assigned_to"')
        self.assertContains(response, 'name="due_date"')
        self.assertContains(response, 'name="project"')

        # フォームセクションの確認
        self.assertContains(response, '基本情報')
        self.assertContains(response, '割り当て情報')
        self.assertContains(response, '添付ファイル')

    def test_issue_create_success(self):
        """チケット作成成功テスト (UT-401)"""
        self.client.force_login(self.admin_user)
        form_data = {
            'title': 'Test New Issue Title',
            'description': 'This is a test description for new issue creation.',
            'priority': 'high',
            'project': self.project.id,
            'assigned_to': self.regular_user.id,
            'due_date': '2025-12-31'
        }
        response = self.client.post('/issues/new/', form_data)

        # 作成成功後は詳細画面にリダイレクト
        self.assertEqual(response.status_code, 302)

        from tracker.models import Issue
        new_issue = Issue.objects.filter(title='Test New Issue Title').first()
        self.assertIsNotNone(new_issue)
        self.assertEqual(new_issue.created_by, self.admin_user)
        self.assertEqual(new_issue.project, self.project)

    def test_issue_create_validation_error(self):
        """チケット作成バリデーションエラーテスト (UT-402)"""
        self.client.force_login(self.admin_user)

        form_data = {
            'title': '',  # 空
            'description': '',  # 空
            'priority': 'high'
        }
        response = self.client.post('/issues/new/', form_data)

        self.assertEqual(response.status_code, 200)  # フォーム再表示
        self.assertContains(response, 'この項目は必須です。')

    def test_issue_create_boundary_validation(self):
        """チケット作成境界値テスト (UT-403)"""
        self.client.force_login(self.admin_user)

        form_data = {
            'title': 'abc',  # 5文字未満
            'description': 'Short description',
            'priority': 'medium',
            'project': self.project.id
        }
        response = self.client.post('/issues/new/', form_data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'タイトルは5文字以上で入力してください。')

    def test_issue_edit_form_display(self):
        """チケット編集フォームの正常表示テスト (UT-404)"""
        self.client.force_login(self.admin_user)
        response = self.client.get(f'/issues/{self.existing_issue.id}/edit/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'チケット編集')
        self.assertContains(response, f'#{self.existing_issue.id}')

        # 既存値の確認
        self.assertContains(response, 'Existing Issue for Edit')
        self.assertContains(response, 'value="medium" selected')

    def test_issue_edit_success(self):
        """チケット編集成功テスト (UT-404)"""
        self.client.force_login(self.admin_user)
        form_data = {
            'title': 'Updated Issue Title',
            'description': 'This is an updated description for testing.',
            'priority': 'high',
            'project': self.project.id,
            'assigned_to': self.regular_user.id
        }
        response = self.client.post(f'/issues/{self.existing_issue.id}/edit/', form_data)

        self.assertEqual(response.status_code, 302)

        from tracker.models import Issue
        updated_issue = Issue.objects.get(id=self.existing_issue.id)
        self.assertEqual(updated_issue.title, 'Updated Issue Title')
        self.assertEqual(updated_issue.priority, 'high')

    def test_issue_edit_not_found(self):
        """存在しないチケット編集時のエラーハンドリングテスト (UT-405)"""
        self.client.force_login(self.admin_user)
        response = self.client.get('/issues/999999/edit/')
        self.assertEqual(response.status_code, 404)

    def test_issue_form_requires_login(self):
        """チケットフォームアクセス時のログイン要件テスト (UT-406)"""
        # 作成フォーム
        response = self.client.get('/issues/new/')
        self.assertRedirects(response, '/login/?next=/issues/new/')

        # 編集フォーム
        response = self.client.get(f'/issues/{self.existing_issue.id}/edit/')
        self.assertRedirects(response, f'/login/?next=/issues/{self.existing_issue.id}/edit/')

from django.test import TestCase
from django.contrib.auth import get_user_model


class IssueListUITest(TestCase):
    """チケット一覧画面UI機能のテストクラス (modular)"""

    def setUp(self):
        User = get_user_model()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin_issues@example.com',
            password='testpass123',
            is_staff=True
        )

        self.regular_user = User.objects.create_user(
            username='regular',
            email='regular_issues@example.com',
            password='testpass123'
        )

        # Create projects and issues
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
        response = self.client.get('/issues/')
        self.assertRedirects(response, '/login/?next=/issues/')

    def test_issue_list_display(self):
        self.client.force_login(self.admin_user)
        response = self.client.get('/issues/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'チケット一覧')
        self.assertContains(response, 'Test Issue 1')
        self.assertContains(response, 'Test Issue 2')
        self.assertContains(response, 'Test Issue 3')
        self.assertContains(response, 'Test Project 1')
        self.assertContains(response, 'Test Project 2')

        # Statistics presence
        self.assertContains(response, '全チケット')
        self.assertContains(response, '未完了')
        self.assertContains(response, '完了済み')

        # Filter form
        self.assertContains(response, '検索・フィルター')
        self.assertContains(response, 'name="search"')
        self.assertContains(response, 'name="status"')
        self.assertContains(response, 'name="priority"')
        self.assertContains(response, 'name="assigned_to"')

    def test_issue_list_search_filter(self):
        self.client.force_login(self.admin_user)

        response = self.client.get('/issues/', {'search': 'Test Issue 1'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Issue 1')
        self.assertNotContains(response, 'Test Issue 2')

        response = self.client.get('/issues/', {'status': 'open'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Issue 1')
        self.assertNotContains(response, 'Test Issue 2')

        response = self.client.get('/issues/', {'priority': 'high'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Issue 1')
        self.assertNotContains(response, 'Test Issue 2')

        response = self.client.get('/issues/', {'assigned_to': self.regular_user.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Issue 1')
        self.assertNotContains(response, 'Test Issue 2')

    def test_issue_list_nonexistent_page(self):
        self.client.force_login(self.admin_user)
        response = self.client.get('/issues/', {'page': '999'})
        self.assertEqual(response.status_code, 200)

    def test_issue_list_regular_user_access(self):
        self.client.force_login(self.regular_user)
        response = self.client.get('/issues/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'チケット一覧')
        self.assertContains(response, 'Test Issue 1')
        self.assertContains(response, 'Test Issue 2')

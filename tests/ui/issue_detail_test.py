from django.test import TestCase
from django.contrib.auth import get_user_model


class IssueDetailUITest(TestCase):
    """チケット詳細画面UI機能のテストクラス (modular)"""

    def setUp(self):
        User = get_user_model()
        self.admin_user = User.objects.create_user(
            username='admin2',
            email='admin2_issues@example.com',
            password='testpass123',
            is_staff=True
        )

        self.regular_user = User.objects.create_user(
            username='regular2',
            email='regular2_issues@example.com',
            password='testpass123'
        )

        from tracker.models import Project, Issue, Comment

        self.project = Project.objects.create(
            name='Detail Project',
            description='Detail project description',
            created_by=self.admin_user
        )

        self.issue = Issue.objects.create(
            title='Detail Test Issue',
            description='This is a detailed description for testing.\nSecond line.',
            project=self.project,
            created_by=self.admin_user,
            assigned_to=self.regular_user,
            status='open',
            priority='high'
        )

        # create two comments
        Comment.objects.create(
            issue=self.issue,
            user=self.admin_user,
            content='First comment content'
        )
        Comment.objects.create(
            issue=self.issue,
            user=self.regular_user,
            content='Second comment content'
        )

    def test_issue_detail_requires_login(self):
        response = self.client.get(f'/issues/{self.issue.id}/')
        self.assertRedirects(response, f'/login/?next=/issues/{self.issue.id}/')

    def test_issue_detail_display(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(f'/issues/{self.issue.id}/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'チケット詳細')
        self.assertContains(response, 'Detail Test Issue')
        self.assertContains(response, f'#{self.issue.id}')
        self.assertContains(response, self.issue.get_status_display())
        self.assertContains(response, self.issue.get_priority_display())

        # basic info
        self.assertContains(response, self.admin_user.username)
        self.assertContains(response, self.regular_user.username)
        self.assertContains(response, self.project.name)

        # description with newline
        self.assertContains(response, 'This is a detailed description for testing.')
        self.assertContains(response, 'Second line.')

        # comments
        self.assertContains(response, 'コメント')
        self.assertContains(response, 'First comment content')
        self.assertContains(response, 'Second comment content')
        self.assertContains(response, 'badge bg-secondary')

    def test_issue_detail_not_found(self):
        self.client.force_login(self.admin_user)
        response = self.client.get('/issues/999999/')
        self.assertEqual(response.status_code, 404)

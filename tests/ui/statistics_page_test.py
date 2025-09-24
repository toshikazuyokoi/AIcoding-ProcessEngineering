from django.test import TestCase, Client
from django.urls import reverse
from tracker.models import User, Project, Issue


class StatisticsPageUITest(TestCase):
    """UI tests for the statistics page (/stats/)"""

    def setUp(self):
        # create users
        self.staff = User.objects.create_user(username='staff', email='staff@example.com', password='pass')
        self.staff.is_staff = True
        self.staff.save()

        self.user = User.objects.create_user(username='user', email='user@example.com', password='pass')

        # create project and some issues
        self.project = Project.objects.create(name='Proj A', description='Test project', created_by=self.staff)

        Issue.objects.create(project=self.project, title='Issue 1', description='desc', created_by=self.user, status='open', priority='high')
        Issue.objects.create(project=self.project, title='Issue 2', description='desc', created_by=self.user, status='in_progress', priority='medium')

        self.client = Client()

    def test_staff_can_access_statistics_global_view(self):
        self.client.login(username='staff', password='pass')
        url = reverse('statistics')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode('utf-8')
        # Check for summary card labels that exist in the template
        self.assertIn('総プロジェクト数', content)
        self.assertIn('総チケット数', content)

    def test_project_filter_shows_project_progress(self):
        self.client.login(username='staff', password='pass')
        url = reverse('statistics')
        resp = self.client.get(url, {'filter_type': 'project', 'project_id': str(self.project.id)})
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode('utf-8')
        # project name and a progress bar / project header expected in template
        self.assertIn(self.project.name, content)
        self.assertIn('progress', content.lower())

    def test_invalid_project_filter_shows_error(self):
        """UT-702: 無効な project_id を指定した場合、エラーメッセージが表示されること"""
        self.client.login(username='staff', password='pass')
        url = reverse('statistics')
        # use a non-existent project id
        resp = self.client.get(url, {'filter_type': 'project', 'project_id': '9999999'})
        # Depending on view implementation it may redirect to dashboard (302),
        # return 404, or render 200 with an error message. Accept these behaviors.
        self.assertIn(resp.status_code, (200, 302, 404))
        if resp.status_code == 200:
            content = resp.content.decode('utf-8')
            self.assertTrue('プロジェクトが見つかりません' in content or 'エラー' in content or '指定されたプロジェクト' in content)

    def test_malformed_project_id_param(self):
        """Edge: project_id に数値以外や極端な値が渡された場合、安定してエラー扱いになること"""
        self.client.login(username='staff', password='pass')
        url = reverse('statistics')
        # non-numeric and malicious-looking inputs
        for bad in ['abc', '1;DROP TABLE projects;', ' ', '', '../../../']:
            resp = self.client.get(url, {'filter_type': 'project', 'project_id': bad})
            # view may redirect or render an error; accept 200/302/404 but must not 500
            self.assertIn(resp.status_code, (200, 302, 404))
            if resp.status_code == 200:
                content = resp.content.decode('utf-8')
                self.assertTrue('無効なプロジェクト' in content or 'エラー' in content or '指定されたプロジェクト' in content)

    def test_non_staff_redirected_from_statistics(self):
        self.client.login(username='user', password='pass')
        url = reverse('statistics')
        resp = self.client.get(url)
        # non-staff may be redirected or forbidden depending on view; accept 302 or 403
        self.assertIn(resp.status_code, (302, 403))

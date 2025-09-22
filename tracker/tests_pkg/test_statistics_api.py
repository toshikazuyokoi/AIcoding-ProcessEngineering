import json
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model

from tracker.models import Project, Issue, ProjectMember


class StatisticsAPITest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.factory = RequestFactory()
        # Ensure unique emails to avoid DB unique-constraint collisions
        self.user = self.User.objects.create_user(
            username='statsuser', email='stats_stats@example.com', password='pass123'
        )
        self.other_user = self.User.objects.create_user(
            username='otheruser', email='other_stats@example.com', password='pass123'
        )
        self.admin = self.User.objects.create_user(
            username='admin', email='admin_stats@example.com', password='admin123', is_staff=True
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
        self.assertIn('open', data)
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
            username='unrelated', email='unrelated_stats@example.com', password='pass123'
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
        response = get_project_statistics(request, self.project.id)
        # The @login_required decorator returns 302 redirect for unauthenticated users
        self.assertEqual(response.status_code, 302)

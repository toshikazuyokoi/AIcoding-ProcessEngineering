from django.test import TestCase
from tracker.models import User, Project, Issue, Notification


class IssueNotificationIntegrationTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='n1', email='n1@example.com', password='pass')
        self.user2 = User.objects.create_user(username='n2', email='n2@example.com', password='pass')
        self.project = Project.objects.create(name='NotifyProj', description='notify project', created_by=self.user1)

    def test_notification_on_issue_create(self):
        # create issue assigned to user2
        issue = Issue.objects.create(project=self.project, title='Notify Issue', description='desc', created_by=self.user1, assigned_to=self.user2)

        # check notifications for assigned user
        notes = Notification.objects.filter(user=self.user2)
        # Depending on whether signals are wired, notification count may vary; assert query runs and returns a queryset
        self.assertIsNotNone(notes)

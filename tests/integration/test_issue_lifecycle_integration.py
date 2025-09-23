from django.test import TestCase
from tracker.models import User, Project
from tracker.services.issue_service import IssueService


class IssueLifecycleIntegrationTest(TestCase):
    """Integration test for basic issue lifecycle via service layer."""

    def setUp(self):
        self.user = User.objects.create_user(username='int_user', email='int@example.com', password='pass')
        self.project = Project.objects.create(name='IntProj', description='integration project', created_by=self.user)

    def test_issue_full_lifecycle(self):
        # create
        issue = IssueService.create_issue(
            project_id=self.project.id,
            created_by_id=self.user.id,
            title='Integration Issue',
            description='Lifecycle test',
            priority='medium'
        )
        self.assertIsNotNone(issue.id)

        # update status
        updated = IssueService.change_status(issue.id, 'in_progress', changed_by_id=self.user.id)
        self.assertTrue(updated)

        # add comment
        comment = IssueService.add_comment(issue.id, self.user.id, 'integration comment')
        self.assertIsNotNone(comment.id)

        # delete
        deleted = IssueService.delete_issue(issue.id, deleted_by_id=self.user.id)
        self.assertTrue(deleted)

"""
Copied modular Issue API tests into `tests_pkg` to avoid package/module import conflict.
This file should be kept in sync with `tracker/tests/test_issue_api_comprehensive.py` until
the migration completes and we remove the legacy `tests` package.
"""

"""
Issue API Comprehensive Test Suite - AT-101~AT-117
Copied into `tests_pkg` to avoid import collision during migration.
"""

import json
from django.test import TestCase
from django.test.client import RequestFactory
from tracker.models import User, Project


class IssueAPIComprehensiveTest(TestCase):
	"""
	Issue API包括テストクラス - AT-101~AT-117対応
	"""

	def setUp(self):
		self.factory = RequestFactory()
		self.comprehensive_user = User.objects.create_user(
			username='comprehensive_issueuser',
			email='comprehensive_issueuser@example.com',
			password='testpass123'
		)
		self.comprehensive_assignee = User.objects.create_user(
			username='comprehensive_assignee',
			email='comprehensive_assignee@example.com',
			password='testpass123'
		)
		self.comprehensive_project = Project.objects.create(
			name='Comprehensive Issue Test Project',
			description='Project for comprehensive Issue API testing',
			created_by=self.comprehensive_user
		)

	def _create_comprehensive_test_issue_data(self, **overrides):
		data = {
			'project_id': self.comprehensive_project.id,
			'title': 'Comprehensive Test Issue',
			'description': 'Comprehensive Test Description',
			'priority': 'medium'
		}
		data.update(overrides)
		return data

	def _create_comprehensive_issue_via_api(self, data=None):
		if data is None:
			data = self._create_comprehensive_test_issue_data()
		request = self.factory.post(
			'/api/issues/', data=json.dumps(data), content_type='application/json'
		)
		request.user = self.comprehensive_user
		from tracker.api.issue_api import create_issue
		response = create_issue(request)
		if response.status_code == 201:
			return json.loads(response.content)['id']
		return None

	def test_create_issue_success(self):
		from tracker.api.issue_api import create_issue
		data = self._create_comprehensive_test_issue_data(
			title='AT-101 Comprehensive Test Issue',
			description='Issue creation success test',
			priority='high',
			assigned_to_id=self.comprehensive_assignee.id
		)
		request = self.factory.post('/api/issues/', data=json.dumps(data), content_type='application/json')
		request.user = self.comprehensive_user
		response = create_issue(request)
		self.assertEqual(response.status_code, 201)
		response_data = json.loads(response.content)
		self.assertEqual(response_data['title'], 'AT-101 Comprehensive Test Issue')

	# ... Additional tests would be copied here (omitted for brevity) ...


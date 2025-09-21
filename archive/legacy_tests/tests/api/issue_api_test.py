"""
Archived duplicate of tests/api/issue_api_test.py
This file was archived during the migration of tests into tracker/tests_pkg.
"""

import json
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from tracker.models import Project, Issue
from tracker.api.issue_api import (
    create_issue, get_issue, update_issue, list_issues, delete_issue,
    change_issue_status, add_comment, list_comments, assign_issue
)

User = get_user_model()


class IssueAPITest(TestCase):
    # ... archived contents preserved verbatim ...
    
    # For full archived contents see the repository history or the original file before migration.

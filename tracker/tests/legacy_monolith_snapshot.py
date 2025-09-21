# --- Baseline Test Inventory (2025-09-21) ---
# Total test classes: 38
# Total test methods: 417
# (Counted from tracker/tests.py before migration)


# 2025-09-21 移行開始時点

# --- 以下、元の tests.py 全内容 ---

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.messages.storage.fallback import FallbackStorage
import json
from tracker.models import Project, ProjectMember, Issue, IssueHistory, Comment, Notification, SystemSettings, Statistics
from tracker.services.user_service import UserService
from tracker.services.issue_service import IssueService
from tracker.services.notification_service import NotificationService
from tracker.services.system_settings_service import SystemSettingsService
from tracker.services.statistics_service import StatisticsService
from tracker.api.user_api import create_user, get_user, update_user, list_users, delete_user
from tracker.api.notification_api import list_notifications, mark_notification_read, delete_notification

User = get_user_model()

...existing code...


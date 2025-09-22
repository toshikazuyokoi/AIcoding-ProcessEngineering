from django.test import TestCase, RequestFactory
import json
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware

from tracker.models import Notification
from tracker.services.notification_service import NotificationService
from tracker.api.notification_api import list_notifications, mark_notification_read, delete_notification

User = get_user_model()


class NotificationServiceTest(TestCase):
    def setUp(self):
        # テストデータ作成
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        self.notification_message = "これはテスト通知です"

    def test_create_notification_success(self):
        notification = NotificationService.create_notification(
            self.user.id,
            self.notification_message
        )
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.message, self.notification_message)
        self.assertFalse(notification.is_read)
        self.assertIsNotNone(notification.created_at)

    def test_create_notification_nonexistent_user(self):
        with self.assertRaises(ValidationError):
            NotificationService.create_notification(99999, self.notification_message)

    def test_create_notification_empty_message(self):
        with self.assertRaises(ValidationError):
            NotificationService.create_notification(self.user.id, '   ')

    def test_get_notifications_success(self):
        NotificationService.create_notification(self.user.id, "通知1")
        NotificationService.create_notification(self.user.id, "通知2")
        NotificationService.create_notification(self.user2.id, "他のユーザー通知")

        notifications = NotificationService.get_notifications(self.user.id)
        self.assertEqual(notifications.count(), 2)

        unread_notifications = NotificationService.get_notifications(self.user.id, unread_only=True)
        self.assertEqual(unread_notifications.count(), 2)

    def test_get_notifications_nonexistent_user(self):
        with self.assertRaises(ValidationError):
            NotificationService.get_notifications(99999)

    def test_get_notification_by_id(self):
        notification = NotificationService.create_notification(self.user.id, self.notification_message)
        found_notification = NotificationService.get_notification_by_id(notification.id)
        self.assertEqual(found_notification.id, notification.id)

        not_found = NotificationService.get_notification_by_id(99999)
        self.assertIsNone(not_found)

    def test_mark_as_read_success(self):
        notification = NotificationService.create_notification(self.user.id, self.notification_message)
        updated_notification = NotificationService.mark_as_read(notification.id)
        self.assertTrue(updated_notification.is_read)

        already_read = NotificationService.mark_as_read(notification.id)
        self.assertTrue(already_read.is_read)

    def test_mark_as_read_nonexistent(self):
        with self.assertRaises(Notification.DoesNotExist):
            NotificationService.mark_as_read(99999)

    def test_mark_all_as_read_success(self):
        NotificationService.create_notification(self.user.id, "通知1")
        NotificationService.create_notification(self.user.id, "通知2")
        NotificationService.create_notification(self.user.id, "通知3")

        updated_count = NotificationService.mark_all_as_read(self.user.id)
        self.assertEqual(updated_count, 3)

        unread_count = NotificationService.get_unread_count(self.user.id)
        self.assertEqual(unread_count, 0)

    def test_mark_all_as_read_nonexistent_user(self):
        with self.assertRaises(ValidationError):
            NotificationService.mark_all_as_read(99999)

    def test_delete_notification_success(self):
        notification = NotificationService.create_notification(self.user.id, self.notification_message)
        notification_id = notification.id

        result = NotificationService.delete_notification(notification_id, self.user.id)
        self.assertTrue(result)

        deleted_notification = NotificationService.get_notification_by_id(notification_id)
        self.assertIsNone(deleted_notification)

    def test_delete_notification_permission_denied(self):
        notification = NotificationService.create_notification(self.user.id, self.notification_message)
        with self.assertRaises(ValidationError):
            NotificationService.delete_notification(notification.id, self.user2.id)

    def test_delete_notification_nonexistent(self):
        with self.assertRaises(Notification.DoesNotExist):
            NotificationService.delete_notification(99999)

    def test_get_unread_count(self):
        NotificationService.create_notification(self.user.id, "通知1")
        NotificationService.create_notification(self.user.id, "通知2")
        notification3 = NotificationService.create_notification(self.user.id, "通知3")

        unread_count = NotificationService.get_unread_count(self.user.id)
        self.assertEqual(unread_count, 3)

        NotificationService.mark_as_read(notification3.id)
        unread_count = NotificationService.get_unread_count(self.user.id)
        self.assertEqual(unread_count, 2)

    def test_get_unread_count_nonexistent_user(self):
        with self.assertRaises(ValidationError):
            NotificationService.get_unread_count(99999)

    def test_bulk_create_notifications_success(self):
        user_ids = [self.user.id, self.user2.id]
        message = "一括通知テスト"

        notifications = NotificationService.bulk_create_notifications(user_ids, message)
        self.assertEqual(len(notifications), 2)

        user1_notifications = NotificationService.get_notifications(self.user.id)
        user2_notifications = NotificationService.get_notifications(self.user2.id)
        self.assertEqual(user1_notifications.count(), 1)
        self.assertEqual(user2_notifications.count(), 1)

    def test_bulk_create_notifications_empty_message(self):
        with self.assertRaises(ValidationError):
            NotificationService.bulk_create_notifications([self.user.id], '   ')

    def test_bulk_create_notifications_empty_users(self):
        with self.assertRaises(ValidationError):
            NotificationService.bulk_create_notifications([], "テスト通知")

    def test_bulk_create_notifications_invalid_users(self):
        with self.assertRaises(ValidationError):
            NotificationService.bulk_create_notifications([self.user.id, 99999], "テスト通知")

    def test_get_notification_statistics_user_specific(self):
        NotificationService.create_notification(self.user.id, "通知1")
        notification2 = NotificationService.create_notification(self.user.id, "通知2")
        NotificationService.mark_as_read(notification2.id)

        NotificationService.create_notification(self.user2.id, "通知3")

        stats = NotificationService.get_notification_statistics(self.user.id)
        self.assertEqual(stats['total_notifications'], 2)
        self.assertEqual(stats['unread_notifications'], 1)
        self.assertEqual(stats['read_notifications'], 1)
        self.assertEqual(stats['unread_percentage'], 50.0)

    def test_get_notification_statistics_global(self):
        NotificationService.create_notification(self.user.id, "通知1")
        notification2 = NotificationService.create_notification(self.user.id, "通知2")
        NotificationService.create_notification(self.user2.id, "通知3")
        NotificationService.mark_as_read(notification2.id)

        stats = NotificationService.get_notification_statistics()
        self.assertEqual(stats['total_notifications'], 3)
        self.assertEqual(stats['unread_notifications'], 2)
        self.assertEqual(stats['read_notifications'], 1)
        self.assertAlmostEqual(stats['unread_percentage'], 66.67, places=1)

    def test_get_notification_statistics_nonexistent_user(self):
        with self.assertRaises(ValidationError):
            NotificationService.get_notification_statistics(99999)



class NotificationAPITest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='apiuser', email='apiuser@example.com', password='testpass')
        self.user.is_staff = False
        self.user.save()
        # Create sample notifications
        self.n1 = Notification.objects.create(user=self.user, message='Hello 1')
        self.n2 = Notification.objects.create(user=self.user, message='Hello 2')

    def _attach_session_and_messages(self, request):
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        messages = FallbackStorage(request)
        request._messages = messages

    def test_list_notifications_self(self):
        request = self.factory.get('/api/notifications')
        request.user = self.user
        self._attach_session_and_messages(request)
        response = list_notifications(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)

    def test_list_notifications_unread_only(self):
        request = self.factory.get('/api/notifications?unread_only=true')
        request.user = self.user
        self._attach_session_and_messages(request)
        response = list_notifications(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        self.assertIsInstance(data, list)

    def test_mark_notification_read_owner(self):
        request = self.factory.patch(f'/api/notifications/{self.n2.id}/read')
        request.user = self.user
        self._attach_session_and_messages(request)

        response = mark_notification_read(request, self.n2.id)
        self.assertEqual(response.status_code, 200)
        self.n2.refresh_from_db()
        self.assertTrue(self.n2.is_read)

    def test_mark_notification_read_not_found(self):
        request = self.factory.patch('/api/notifications/99999/read')
        request.user = self.user
        self._attach_session_and_messages(request)

        response = mark_notification_read(request, 99999)
        self.assertEqual(response.status_code, 404)

    def test_mark_notification_read_forbidden(self):
        other = User.objects.create_user(username='other', email='other@example.com', password='pw')
        other.is_staff = False
        other.save()
        other_n = Notification.objects.create(user=other, message='Other msg')

        request = self.factory.patch(f'/api/notifications/{other_n.id}/read')
        request.user = self.user
        self._attach_session_and_messages(request)

        response = mark_notification_read(request, other_n.id)
        self.assertEqual(response.status_code, 403)

    def test_delete_notification_owner(self):
        request = self.factory.delete(f'/api/notifications/{self.n1.id}')
        request.user = self.user
        self._attach_session_and_messages(request)
        response = delete_notification(request, self.n1.id)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Notification.objects.filter(id=self.n1.id).exists())

    def test_delete_notification_admin(self):
        admin = User.objects.create_user(username='admin', email='admin@example.com', password='pw')
        admin.is_staff = True
        admin.save()
        request = self.factory.delete(f'/api/notifications/{self.n2.id}')
        request.user = admin
        self._attach_session_and_messages(request)
        response = delete_notification(request, self.n2.id)
        self.assertEqual(response.status_code, 200)

    def test_delete_notification_forbidden(self):
        other = User.objects.create_user(username='other2', email='other2@example.com', password='pw')
        other_n = Notification.objects.create(user=other, message='Other msg 2')
        request = self.factory.delete(f'/api/notifications/{other_n.id}')
        request.user = self.user
        self._attach_session_and_messages(request)

        response = delete_notification(request, other_n.id)
        self.assertEqual(response.status_code, 403)


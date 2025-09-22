from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class NotificationListUITest(TestCase):
    """Ported: 通知一覧画面UI機能のテストクラス"""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin4',
            email='admin4+ui@example.com',
            password='testpass123',
            is_staff=True
        )

        self.regular_user = User.objects.create_user(
            username='regular4',
            email='regular4+ui@example.com',
            password='testpass123'
        )

        from tracker.models import Notification

        # テスト用通知を作成
        self.read_notification = Notification.objects.create(
            user=self.admin_user,
            message='既読テスト通知です。',
            is_read=True
        )

        self.unread_notification = Notification.objects.create(
            user=self.admin_user,
            message='未読テスト通知です。',
            is_read=False
        )

        # 他ユーザーの通知（表示されないはず）
        self.other_user_notification = Notification.objects.create(
            user=self.regular_user,
            message='他ユーザーの通知です。',
            is_read=False
        )

    def test_notification_list_display(self):
        self.client.force_login(self.admin_user)
        response = self.client.get('/notifications/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '通知一覧')
        self.assertContains(response, '既読テスト通知です。')
        self.assertContains(response, '未読テスト通知です。')
        self.assertNotContains(response, '他ユーザーの通知です。')

        # 統計情報の確認
        self.assertContains(response, '全')
        self.assertContains(response, '未読')

        # フィルターフォームの確認
        self.assertContains(response, 'name="unread_only"')
        self.assertContains(response, 'name="date_from"')
        self.assertContains(response, 'name="date_to"')

    def test_notification_list_unread_filter(self):
        self.client.force_login(self.admin_user)
        response = self.client.get('/notifications/', {'unread_only': 'true'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '未読テスト通知です。')
        self.assertNotContains(response, '既読テスト通知です。')

    def test_notification_mark_as_read(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(f'/notifications/{self.unread_notification.id}/mark-read/')
        self.assertRedirects(response, '/notifications/')

        self.unread_notification.refresh_from_db()
        self.assertTrue(self.unread_notification.is_read)

    def test_notification_mark_read_not_found(self):
        self.client.force_login(self.admin_user)
        response = self.client.post('/notifications/999999/mark-read/')
        self.assertRedirects(response, '/notifications/')

    def test_notification_list_pagination(self):
        self.client.force_login(self.admin_user)
        from tracker.models import Notification
        for i in range(25):
            Notification.objects.create(
                user=self.admin_user,
                message=f'ページネーションテスト通知 {i}',
                is_read=False
            )

        response = self.client.get('/notifications/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '件中')

    def test_notification_list_requires_login(self):
        response = self.client.get('/notifications/')
        self.assertRedirects(response, '/login/?next=/notifications/')

    def test_notification_mark_read_permission(self):
        self.client.force_login(self.regular_user)
        response = self.client.post(f'/notifications/{self.unread_notification.id}/mark-read/')
        self.assertRedirects(response, '/notifications/')

        self.unread_notification.refresh_from_db()
        self.assertFalse(self.unread_notification.is_read)

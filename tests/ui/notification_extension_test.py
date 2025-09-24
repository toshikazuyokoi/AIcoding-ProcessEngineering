from django.test import TestCase
from django.contrib.auth import get_user_model
import json


class NotificationExtensionUITest(TestCase):
    """通知 UI の拡張テスト (UT-501..UT-506)"""

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='notify_user',
            email='notify_ui@example.com',
            password='testpass123'
        )

        from tracker.models import Notification

        # 未読/既読の通知を用意
        self.unread = Notification.objects.create(user=self.user, message='拡張未読通知', is_read=False)
        self.read = Notification.objects.create(user=self.user, message='拡張既読通知', is_read=True)

    def test_unread_count_badge_present(self):
        self.client.force_login(self.user)
        response = self.client.get('/notifications/')
        self.assertEqual(response.status_code, 200)
        # 未読数バッジが存在する
        self.assertContains(response, '未読')
        self.assertContains(response, '拡張未読通知')

    def test_mark_as_read_ajax_returns_json(self):
        self.client.force_login(self.user)
        response = self.client.post(f'/notifications/{self.unread.id}/mark-read/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        # サーバーは JSON or redirect のいずれかを返す実装かもしれないので柔軟に検査
        if response['Content-Type'].startswith('application/json'):
            data = json.loads(response.content)
            self.assertIn('success', data)
            self.assertTrue(data['success'])
        else:
            # 通常の POST 処理はリダイレクトし、既読フラグが立つはず
            self.assertIn(response.status_code, (302, 200))

        from tracker.models import Notification
        self.unread.refresh_from_db()
        self.assertTrue(self.unread.is_read)

    def test_notification_navigation_link(self):
        # 通知からの遷移 - 通知の message がリンク要素を含むか、遷移対象が明示されているかを確認
        self.client.force_login(self.user)
        response = self.client.get('/notifications/')
        self.assertEqual(response.status_code, 200)
        # 期待: notification message が表示され、リンクのある要素（a href）を含む
        self.assertContains(response, '拡張未読通知')
        # ページにリンク要素が含まれているか（詳細遷移など）をざっくり確認
        self.assertContains(response, 'href="')

    def test_unread_filter_edgecase(self):
        # unread_only が空や不正値でも安定して動くことを確認
        self.client.force_login(self.user)
        response = self.client.get('/notifications/', {'unread_only': 'false'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '拡張未読通知')

from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class SystemSettingsUITest(TestCase):
    """Ported: システム設定画面UI機能のテストクラス"""

    def setUp(self):
        User = get_user_model()
        self.admin_user = User.objects.create_user(
            username='admin5',
            email='admin5_settings@example.com',
            password='testpass123',
            is_staff=True
        )

        self.regular_user = User.objects.create_user(
            username='regular5',
            email='regular5_settings@example.com',
            password='testpass123'
        )

        from tracker.models import SystemSettings
        self.initial_settings = SystemSettings.get_settings()

    def test_system_settings_display(self):
        self.client.force_login(self.admin_user)
        response = self.client.get('/settings/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'システム設定')
        self.assertContains(response, 'メンテナンスモード')
        self.assertContains(response, '送信元メールアドレス')

        self.assertContains(response, 'name="maintenance_mode"')
        self.assertContains(response, 'name="email_sender"')
        self.assertContains(response, 'csrf')

        self.assertContains(response, '一般設定')
        self.assertContains(response, 'メール設定')

    def test_system_settings_update_success(self):
        self.client.force_login(self.admin_user)
        response = self.client.post('/settings/', {
            'maintenance_mode': 'on',
            'email_sender': 'admin@example.com'
        })

        self.assertRedirects(response, '/settings/')

        from tracker.models import SystemSettings
        updated_settings = SystemSettings.get_settings()
        self.assertTrue(updated_settings.maintenance_mode)
        self.assertEqual(updated_settings.email_sender, 'admin@example.com')

    def test_system_settings_update_validation_error(self):
        self.client.force_login(self.admin_user)
        response = self.client.post('/settings/', {
            'maintenance_mode': '',
            'email_sender': 'invalid-email'
        })

        self.assertEqual(response.status_code, 200)

    def test_system_settings_boundary_values(self):
        self.client.force_login(self.admin_user)
        response = self.client.post('/settings/', {'email_sender': ''})
        self.assertRedirects(response, '/settings/')

        long_email = 'a' * 50 + '@example.com'
        response = self.client.post('/settings/', {'email_sender': long_email})
        self.assertIn(response.status_code, [200, 302])

    def test_system_settings_requires_admin(self):
        self.client.force_login(self.regular_user)
        response = self.client.get('/settings/')
        self.assertIn(response.status_code, [302, 403])

    def test_system_settings_requires_login(self):
        response = self.client.get('/settings/')
        self.assertRedirects(response, '/login/?next=/settings/')

    def test_system_settings_maintenance_mode_warning(self):
        from tracker.models import SystemSettings
        SystemSettings.update_settings({'maintenance_mode': True})

        self.client.force_login(self.admin_user)
        response = self.client.get('/settings/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '現在メンテナンスモードが有効です')
        self.assertContains(response, 'checked')

    def test_system_settings_form_reset_functionality(self):
        self.client.force_login(self.admin_user)
        response = self.client.get('/settings/')
        self.assertContains(response, 'resetForm()')
        self.assertContains(response, 'リセット')

    def test_system_settings_tab_structure(self):
        self.client.force_login(self.admin_user)
        response = self.client.get('/settings/')
        self.assertContains(response, 'settingsTabs')
        self.assertContains(response, 'general-tab')
        self.assertContains(response, 'email-tab')
        self.assertContains(response, 'security-tab')
        self.assertContains(response, 'nav-link active')

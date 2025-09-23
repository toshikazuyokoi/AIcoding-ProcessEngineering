from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from tracker.services.system_settings_service import SystemSettingsService


class SettingsPageUITest(TestCase):
    """Basic UI tests for system settings page.

    Initial low-risk checks:
    - staff user can access settings page (200)
    - non-staff user is redirected (permission)
    - settings values are rendered on the page
    """

    def setUp(self):
        self.User = get_user_model()
        self.client = Client()

        # staff/admin
        self.admin = self.User.objects.create_user(
            username='ui_admin',
            email='ui_admin@example.com',
            password='secret123',
            is_staff=True,
        )

        # regular user
        self.regular = self.User.objects.create_user(
            username='ui_user',
            email='ui_user@example.com',
            password='secret123',
            is_staff=False,
        )

    def test_settings_page_access_by_staff(self):
        """Staff user should be able to GET the settings page and see current settings."""
        # ensure some known settings exist
        try:
            SystemSettingsService.reset_to_defaults()
        except Exception:
            # service may raise in some edge cases; tests should still proceed
            pass

        self.client.login(username='ui_admin', password='secret123')
        resp = self.client.get('/settings/')
        self.assertIn(resp.status_code, (200,))
        # page should contain a maintenance_mode label or email_sender field
        content = resp.content.decode('utf-8')
        self.assertTrue('maintenance' in content.lower() or 'メール' in content or 'email' in content.lower())

    def test_settings_page_redirect_for_nonstaff(self):
        """Non-staff users should be redirected away from settings page."""
        self.client.login(username='ui_user', password='secret123')
        resp = self.client.get('/settings/')
        # login_required + user_passes_test cause redirect (302)
        self.assertEqual(resp.status_code, 302)

    def test_settings_post_success_updates_db_and_redirects(self):
        """Staff user POST with valid data updates settings and redirects."""
        self.client.login(username='ui_admin', password='secret123')

        resp = self.client.post('/settings/', {'maintenance_mode': 'on', 'email_sender': 'admin@site.test'})
        # expect redirect back to settings
        self.assertEqual(resp.status_code, 302)

        # verify in DB
        from tracker.services.system_settings_service import SystemSettingsService
        settings = SystemSettingsService.get_settings()
        self.assertTrue(settings.maintenance_mode)
        self.assertEqual(settings.email_sender, 'admin@site.test')

    def test_settings_post_invalid_email_shows_error(self):
        """Staff user POST with invalid email should not update and should show error message."""
        self.client.login(username='ui_admin', password='secret123')

        resp = self.client.post('/settings/', {'maintenance_mode': 'on', 'email_sender': 'not-an-email'})
        # view catches exceptions and returns 200 with error message
        self.assertIn(resp.status_code, (200, 302))

        from tracker.services.system_settings_service import SystemSettingsService
        settings = SystemSettingsService.get_settings()
        # should not have been set to invalid email
        self.assertNotEqual(settings.email_sender, 'not-an-email')

    def test_settings_requires_authentication(self):
        resp = self.client.get('/settings/')
        self.assertEqual(resp.status_code, 302)
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

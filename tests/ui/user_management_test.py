import json
from django.test import TestCase
from django.contrib.auth import get_user_model


class UserManagementUITest(TestCase):
    """ユーザー管理UI機能のテストクラス (modular)"""

    def setUp(self):
        User = get_user_model()
        # Create test users with unique emails
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin_ui@example.com',
            password='admin123',
            is_staff=True,
            is_superuser=False
        )

        self.regular_user = User.objects.create_user(
            username='regular',
            email='regular_ui@example.com',
            password='regular123',
            is_staff=False
        )

        self.test_user = User.objects.create_user(
            username='testuser',
            email='test_ui@example.com',
            password='test123',
            is_staff=False
        )

    def test_user_list_requires_staff_permission(self):
        # Regular user cannot access
        self.client.force_login(self.regular_user)
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, 302)  # Redirect due to permission denied

        # Staff user can access
        self.client.force_login(self.admin_user)
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, 200)

    def test_user_list_display(self):
        self.client.force_login(self.admin_user)
        response = self.client.get('/users/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ユーザー管理')
        self.assertContains(response, self.admin_user.username)
        self.assertContains(response, self.regular_user.username)
        self.assertContains(response, self.test_user.username)

    def test_user_create_get(self):
        self.client.force_login(self.admin_user)
        response = self.client.get('/users/add/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '新規ユーザー作成')
        self.assertContains(response, 'ユーザー名')
        self.assertContains(response, 'メールアドレス')

    def test_user_create_success(self):
        self.client.force_login(self.admin_user)

        user_data = {
            'username': 'newuser',
            'email': 'newuser_ui@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'is_active': True,
            'is_staff': False
        }

        response = self.client.post('/users/add/', user_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation

        # Verify user was created
        User = get_user_model()
        new_user = User.objects.get(username='newuser')
        self.assertEqual(new_user.email, 'newuser_ui@example.com')
        self.assertTrue(new_user.is_active)
        self.assertFalse(new_user.is_staff)

    def test_user_create_duplicate_email(self):
        self.client.force_login(self.admin_user)

        user_data = {
            'username': 'duplicate',
            'email': 'admin_ui@example.com',  # Already exists
            'password1': 'newpass123',
            'password2': 'newpass123',
            'is_active': True,
            'is_staff': False
        }

        response = self.client.post('/users/add/', user_data)
        self.assertEqual(response.status_code, 200)  # Form validation error, no redirect
        self.assertContains(response, 'このメールアドレスは既に使用されています')

    def test_user_edit_get_and_success(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(f'/users/{self.test_user.id}/edit/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ユーザー編集')  # header present

        edit_data = {
            'username': 'editeduser',
            'email': 'edited_ui@example.com',
            'first_name': 'Edited',
            'last_name': 'User',
            'is_active': True,
            'is_staff': True
        }

        response = self.client.post(f'/users/{self.test_user.id}/edit/', edit_data)
        self.assertEqual(response.status_code, 302)

        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.username, 'editeduser')
        self.assertEqual(self.test_user.email, 'edited_ui@example.com')

    def test_user_delete_flow(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(f'/users/{self.test_user.id}/delete/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ユーザー削除確認')

        response = self.client.post(f'/users/{self.test_user.id}/delete/')
        self.assertEqual(response.status_code, 302)
        User = get_user_model()
        self.assertFalse(User.objects.filter(id=self.test_user.id).exists())

    def test_user_delete_self_protection(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(f'/users/{self.admin_user.id}/delete/')
        self.assertEqual(response.status_code, 302)
        User = get_user_model()
        self.assertTrue(User.objects.filter(id=self.admin_user.id).exists())

    def test_user_password_reset(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(f'/users/{self.test_user.id}/password-reset/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'パスワードリセット')

        reset_data = {
            'new_password1': 'newpassword123',
            'new_password2': 'newpassword123'
        }
        response = self.client.post(f'/users/{self.test_user.id}/password-reset/', reset_data)
        self.assertEqual(response.status_code, 302)

        self.test_user.refresh_from_db()
        self.assertTrue(self.test_user.check_password('newpassword123'))

    def test_user_search_and_filter(self):
        self.client.force_login(self.admin_user)

        # Search by username
        response = self.client.get('/users/', {'search': 'admin'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.admin_user.username)
        self.assertNotContains(response, self.regular_user.username)

        # Create inactive user and filter
        User = get_user_model()
        inactive_user = User.objects.create_user(
            username='inactive',
            email='inactive_ui@example.com',
            password='inactive123',
            is_active=False
        )
        response = self.client.get('/users/', {'is_active': 'true'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, inactive_user.username)

    def test_user_toggle_active_ajax(self):
        self.client.force_login(self.admin_user)
        original_status = self.test_user.is_active
        response = self.client.post(f'/users/{self.test_user.id}/toggle-active/')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.is_active, not original_status)

    def test_pagination_and_permission_checks(self):
        # Create many users to test pagination
        User = get_user_model()
        for i in range(25):
            User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}_ui@example.com',
                password='password123'
            )

        self.client.force_login(self.admin_user)
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'page-link')

        # Permission checks: regular user should not access user-management URLs
        urls_to_test = [
            '/users/',
            '/users/add/',
            f'/users/{self.test_user.id}/edit/',
            f'/users/{self.test_user.id}/delete/',
            f'/users/{self.test_user.id}/password-reset/',
        ]
        self.client.force_login(self.regular_user)
        for url in urls_to_test:
            response = self.client.get(url)
            self.assertNotEqual(response.status_code, 200, f"Regular user should not access {url}")

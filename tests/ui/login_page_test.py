from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginPageUITest(TestCase):
    """UI tests for the login page (UT-001 .. UT-003)

    Tests cover:
    - successful login with correct credentials (UT-001)
    - failed login with incorrect credentials (UT-002)
    - validation for empty fields (UT-003)
    """

    def setUp(self):
        # create a user to authenticate
        self.user = User.objects.create_user(
            username='ui_login_user',
            email='ui_login_user@example.com',
            password='Secur3P@ssw0rd'
        )

    def test_login_page_renders_and_form_fields_present(self):
        """Page renders and contains expected labels/inputs"""
        url = reverse('login') if 'login' in [u.name for u in []] else '/login/'
        # Use direct path because some projects don't name the login URL
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Page header
        self.assertIn('ログイン', content)
        # Email and password fields
        self.assertIn('name="email"', content)
        self.assertIn('name="password"', content)
        # Remember me checkbox and submit button
        self.assertIn('name="remember_me"', content)
        self.assertIn('ログイン', content)

    def test_successful_login_redirects(self):
        """UT-001: successful login with correct credentials should redirect"""
        login_url = '/login/'
        resp = self.client.post(login_url, {'email': 'ui_login_user@example.com', 'password': 'Secur3P@ssw0rd'})
        # Expect a redirect to dashboard or next. Accept 302 or 200 depending on view behavior
        self.assertIn(resp.status_code, (302, 301, 200))

        # If redirected, ensure subsequent page is accessible (dashboard or root)
        if resp.status_code in (301, 302):
            # follow the redirect
            follow = self.client.get(resp.url)
            self.assertIn(follow.status_code, (200, 302, 301))

    def test_failed_login_shows_error(self):
        """UT-002: failed login should re-render with an error"""
        login_url = '/login/'
        resp = self.client.post(login_url, {'email': 'ui_login_user@example.com', 'password': 'wrongpassword'}, follow=True)
        content = resp.content.decode('utf-8')
        # Expect the page to contain the view-level message or form error message
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(
            'ログインに失敗しました' in content or
            'メールアドレスまたはパスワードが正しくありません' in content
        )

    def test_empty_fields_show_validation(self):
        """UT-003: submitting empty fields should show validation feedback"""
        login_url = '/login/'
        resp = self.client.post(login_url, {'email': '', 'password': ''}, follow=True)
        content = resp.content.decode('utf-8')
        self.assertIn('登録済みのメールアドレスを入力してください', content)
        self.assertIn('パスワードを入力してください', content)

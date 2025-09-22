from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
import json


from tracker.services.system_settings_service import SystemSettingsService


class SystemSettingsAPITest(TestCase):
    """
    SystemSettings API のテストケース
    AT-301 to AT-304 as defined in api-test-design.md
    """
    
    def setUp(self):
        self.factory = RequestFactory()
        self.User = get_user_model()
        
        # テストユーザー作成
        self.admin = self.User.objects.create_user(
            username='admin', 
            email='admin@example.com', 
            password='adminpass123',
            is_staff=True,
            is_superuser=True
        )
        
        self.regular_user = self.User.objects.create_user(
            username='user', 
            email='user@example.com', 
            password='userpass123',
            is_staff=False
        )
    
    def test_get_system_settings_success(self):
        """AT-301: GET正常系 - 設定取得成功"""
        from tracker.api.system_settings_api import system_settings_api
        
        request = self.factory.get('/api/settings/')
        request.user = self.admin  # Staff user
        
        response = system_settings_api(request)
        self.assertEqual(response.status_code, 200)
        
        # レスポンス内容確認
        data = json.loads(response.content)
        self.assertIn('maintenance_mode', data)
        self.assertIn('email_sender', data)
        self.assertIsInstance(data['maintenance_mode'], bool)
        self.assertIsInstance(data['email_sender'], str)
    
    def test_get_system_settings_permission_denied(self):
        """AT-302: GET異常系 - 権限なし"""
        from tracker.api.system_settings_api import system_settings_api
        
        request = self.factory.get('/api/settings/')
        request.user = self.regular_user  # Non-staff user
        
        # @staff_member_required decorator causes redirect for non-staff users
        response = system_settings_api(request)
        self.assertEqual(response.status_code, 302)  # Redirect due to staff_member_required
    
    def test_update_system_settings_success(self):
        """AT-303: PUT正常系 - 設定更新成功"""
        from tracker.api.system_settings_api import system_settings_api
        
        # 更新データ
        update_data = {
            'maintenance_mode': True,
            'email_sender': 'admin@testsite.com'
        }
        
        request = self.factory.put(
            '/api/settings/',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        request.user = self.admin  # Staff user
        
        response = system_settings_api(request)
        self.assertEqual(response.status_code, 200)
        
        # レスポンス内容確認
        data = json.loads(response.content)
        self.assertEqual(data['maintenance_mode'], True)
        self.assertEqual(data['email_sender'], 'admin@testsite.com')
        
        # DB確認
        from tracker.services.system_settings_service import SystemSettingsService
        settings = SystemSettingsService.get_settings()
        self.assertTrue(settings.maintenance_mode)
        self.assertEqual(settings.email_sender, 'admin@testsite.com')
    
    def test_update_system_settings_invalid_data(self):
        """AT-304: PUT異常系 - 無効な値"""
        from tracker.api.system_settings_api import system_settings_api
        
        # 無効なデータ（maintenance_mode should be boolean）
        invalid_data = {
            'maintenance_mode': 'invalid_string',  # Should be boolean
            'email_sender': 'invalid-email'  # Invalid email
        }
        
        request = self.factory.put(
            '/api/settings/',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        request.user = self.admin  # Staff user
        
        response = system_settings_api(request)
        self.assertEqual(response.status_code, 400)
        
        # エラーメッセージ確認
        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Validation error')
    
    def test_system_settings_json_parse_error(self):
        """JSON パースエラーテスト"""
        from tracker.api.system_settings_api import system_settings_api
        
        request = self.factory.put(
            '/api/settings/',
            data='invalid json data',
            content_type='application/json'
        )
        request.user = self.admin
        
        response = system_settings_api(request)
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.content)
        self.assertEqual(data['error'], 'Invalid JSON format')
    
    def test_system_settings_authentication_required(self):
        """認証必須テスト"""
        from tracker.api.system_settings_api import system_settings_api
        
        request = self.factory.get('/api/settings/')
        request.user = AnonymousUser()  # Not authenticated
        
        # @login_required decorator causes redirect for unauthenticated users
        response = system_settings_api(request)
        self.assertEqual(response.status_code, 302)  # Redirect due to login_required

"""
SystemSettings API - システム設定の取得・更新APIコントローラ
"""
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from tracker.services.system_settings_service import SystemSettingsService

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET", "PUT"])
@login_required
@staff_member_required
def system_settings_api(request):
    """
    システム設定API - GET/PUT /api/settings
    管理者権限必須でシステム設定の取得・更新を行う
    """
    try:
        if request.method == 'GET':
            return _get_system_settings(request)
        elif request.method == 'PUT':
            return _update_system_settings(request)
    except Exception as e:
        logger.error(f"SystemSettings API error: {str(e)}")
        return JsonResponse({
            'error': 'Internal server error',
            'details': str(e)
        }, status=500)


def _get_system_settings(request):
    """
    システム設定取得 (GET /api/settings)
    
    Returns:
        JsonResponse: システム設定データ
    """
    try:
        settings_dict = SystemSettingsService.get_settings_dict()
        return JsonResponse(settings_dict, status=200)
    except ValidationError as e:
        return JsonResponse({
            'error': 'Settings retrieval failed',
            'details': str(e)
        }, status=400)
    except Exception as e:
        logger.error(f"Settings retrieval error: {str(e)}")
        return JsonResponse({
            'error': 'Failed to retrieve settings',
            'details': str(e)
        }, status=500)


def _update_system_settings(request):
    """
    システム設定更新 (PUT /api/settings)
    
    Args:
        request: HTTP リクエスト（JSON ボディに設定データ）
        
    Returns:
        JsonResponse: 更新された設定データ
    """
    try:
        # JSON データ解析
        try:
            settings_data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return JsonResponse({
                'error': 'Invalid JSON format',
                'details': str(e)
            }, status=400)
        
        # 設定更新実行
        updated_settings = SystemSettingsService.update_from_dict(settings_data)
        
        return JsonResponse(updated_settings, status=200)
        
    except ValidationError as e:
        return JsonResponse({
            'error': 'Validation error',
            'details': str(e)
        }, status=400)
    except Exception as e:
        logger.error(f"Settings update error: {str(e)}")
        return JsonResponse({
            'error': 'Failed to update settings',
            'details': str(e)
        }, status=500)


def get_system_settings_api_urls():
    """
    SystemSettings API の URL パターンを取得
    
    Returns:
        list: URL パターンのタプルリスト
    """
    from django.urls import path
    
    return [
        path('api/settings', system_settings_api, name='system_settings_api'),
    ]
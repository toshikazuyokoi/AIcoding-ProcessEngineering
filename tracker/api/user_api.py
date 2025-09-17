"""
User API Controller - ユーザー関連APIエンドポイント
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
import json
import logging

from tracker.services.user_service import UserService

User = get_user_model()
logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def create_user(request):
    """
    ユーザー新規作成 API
    POST /api/users
    """
    try:
        # リクエストボディの解析
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON format'
            }, status=400)
        
        # 必須フィールドの確認
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    'error': f'Missing required field: {field}'
                }, status=400)
        
        # ユーザー作成
        try:
            user = UserService.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password']
            )
            
            # レスポンス作成
            response_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'created_at': user.date_joined.isoformat()
            }
            
            return JsonResponse(response_data, status=201)
            
        except ValidationError as e:
            return JsonResponse({
                'error': str(e)
            }, status=400)
            
    except Exception as e:
        logger.error(f"User creation error: {str(e)}")
        return JsonResponse({
            'error': 'Internal server error'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_user(request, user_id):
    """
    ユーザー情報取得 API
    GET /api/users/{id}
    """
    try:
        # ユーザー取得
        user = UserService.get_user_by_id(user_id)
        if user is None:
            return JsonResponse({
                'error': 'User not found'
            }, status=404)
        
        # レスポンス作成
        response_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.date_joined.isoformat(),
            'updated_at': user.last_login.isoformat() if user.last_login else None
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"User retrieval error: {str(e)}")
        return JsonResponse({
            'error': 'Internal server error'
        }, status=500)


@login_required
@csrf_exempt
@require_http_methods(["PUT"])
def update_user(request, user_id):
    """
    ユーザー情報更新 API
    PUT /api/users/{id}
    """
    try:
        # リクエストボディの解析
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON format'
            }, status=400)
        
        # ユーザーの存在確認
        user = UserService.get_user_by_id(user_id)
        if user is None:
            return JsonResponse({
                'error': 'User not found'
            }, status=404)
        
        # 権限チェック（自分自身または管理者のみ）
        if request.user.id != user_id and not request.user.is_staff:
            return JsonResponse({
                'error': 'Permission denied'
            }, status=403)
        
        # ユーザー更新
        try:
            updated_user = UserService.update_user(user_id, **data)
            
            # レスポンス作成
            response_data = {
                'id': updated_user.id,
                'username': updated_user.username,
                'email': updated_user.email,
                'updated_at': updated_user.last_login.isoformat() if updated_user.last_login else None
            }
            
            return JsonResponse(response_data)
            
        except ValidationError as e:
            return JsonResponse({
                'error': str(e)
            }, status=400)
            
    except Exception as e:
        logger.error(f"User update error: {str(e)}")
        return JsonResponse({
            'error': 'Internal server error'
        }, status=500)


@staff_member_required
@require_http_methods(["GET"])
def list_users(request):
    """
    ユーザー一覧取得 API（管理者専用）
    GET /api/users
    """
    try:
        # ユーザー一覧取得
        users = UserService.list_users()
        
        # レスポンス作成
        response_data = []
        for user in users:
            response_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email
            })
        
        return JsonResponse(response_data, safe=False)
        
    except Exception as e:
        logger.error(f"User list error: {str(e)}")
        return JsonResponse({
            'error': 'Internal server error'
        }, status=500)


@staff_member_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_user(request, user_id):
    """
    ユーザー削除 API（管理者専用）
    DELETE /api/users/{id}
    """
    try:
        # ユーザーの存在確認
        user = UserService.get_user_by_id(user_id)
        if user is None:
            return JsonResponse({
                'error': 'User not found'
            }, status=404)
        
        # 自分自身を削除しようとしているかチェック
        if request.user.id == user_id:
            return JsonResponse({
                'error': 'Cannot delete yourself'
            }, status=400)
        
        # ユーザー削除
        try:
            result = UserService.delete_user(user_id)
            if result:
                return JsonResponse({
                    'result': 'success'
                })
            else:
                return JsonResponse({
                    'error': 'User deletion failed'
                }, status=500)
                
        except ValidationError as e:
            return JsonResponse({
                'error': str(e)
            }, status=400)
            
    except Exception as e:
        logger.error(f"User deletion error: {str(e)}")
        return JsonResponse({
            'error': 'Internal server error'
        }, status=500)


# URL設定用の関数マッピング
def get_user_api_urls():
    """
    User API URL設定を返す関数
    urls.pyで使用
    """
    from django.urls import path
    
    return [
        path('users/', create_user, name='create_user'),
        path('users/', list_users, name='list_users'),  # GETとPOSTで分岐
        path('users/<int:user_id>/', get_user, name='get_user'),
        path('users/<int:user_id>/', update_user, name='update_user'),
        path('users/<int:user_id>/', delete_user, name='delete_user'),
    ]


# エラーハンドリング用ヘルパー関数
def handle_api_error(error, default_status=500):
    """
    API エラーレスポンスの統一処理
    
    Args:
        error: エラーオブジェクト
        default_status: デフォルトステータスコード
    
    Returns:
        JsonResponse: エラーレスポンス
    """
    if isinstance(error, ValidationError):
        return JsonResponse({
            'error': str(error)
        }, status=400)
    
    logger.error(f"API Error: {str(error)}")
    return JsonResponse({
        'error': 'Internal server error'
    }, status=default_status)


# リクエストバリデーション用ヘルパー関数
def validate_json_request(request, required_fields=None):
    """
    JSONリクエストのバリデーション
    
    Args:
        request: HTTPリクエスト
        required_fields: 必須フィールドのリスト
    
    Returns:
        tuple: (data, error_response)
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return None, JsonResponse({
            'error': 'Invalid JSON format'
        }, status=400)
    
    if required_fields:
        for field in required_fields:
            if field not in data:
                return None, JsonResponse({
                    'error': f'Missing required field: {field}'
                }, status=400)
    
    return data, None
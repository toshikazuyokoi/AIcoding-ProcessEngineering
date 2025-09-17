"""
NotificationService - 通知管理の業務ロジック
"""
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from tracker.models import Notification

User = get_user_model()


class NotificationService:
    """
    通知管理サービス - 通知の作成・取得・既読化・削除等の業務ロジック
    """

    @classmethod
    def create_notification(cls, user_id, message):
        """
        通知新規作成
        
        Args:
            user_id (int): 通知先ユーザーID
            message (str): 通知メッセージ
            
        Returns:
            Notification: 作成された通知オブジェクト
            
        Raises:
            ValidationError: バリデーションエラー時
        """
        try:
            with transaction.atomic():
                # ユーザーの存在確認
                try:
                    user = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    raise ValidationError("指定されたユーザーが存在しません")
                
                # メッセージのバリデーション
                if not message or not message.strip():
                    raise ValidationError("通知メッセージは必須です")
                
                # 通知作成
                notification = Notification.objects.create(
                    user=user,
                    message=message.strip()
                )
                
                return notification
                
        except Exception as e:
            if isinstance(e, ValidationError):
                raise e
            raise ValidationError(f"通知の作成に失敗しました: {str(e)}")

    @classmethod
    def get_notifications(cls, user_id, unread_only=False):
        """
        ユーザーの通知一覧取得
        
        Args:
            user_id (int): ユーザーID
            unread_only (bool): 未読のみ取得するか
            
        Returns:
            QuerySet: 通知のクエリセット
            
        Raises:
            ValidationError: バリデーションエラー時
        """
        try:
            # ユーザーの存在確認
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise ValidationError("指定されたユーザーが存在しません")
            
            # 通知一覧取得
            return Notification.get_notifications(user, unread_only=unread_only)
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise e
            raise ValidationError(f"通知の取得に失敗しました: {str(e)}")

    @classmethod
    def get_notification_by_id(cls, notification_id):
        """
        ID指定で通知取得
        
        Args:
            notification_id (int): 通知ID
            
        Returns:
            Notification or None: 通知オブジェクト（見つからない場合はNone）
        """
        try:
            return Notification.objects.get(id=notification_id)
        except Notification.DoesNotExist:
            return None

    @classmethod
    def mark_as_read(cls, notification_id):
        """
        通知を既読にする
        
        Args:
            notification_id (int): 通知ID
            
        Returns:
            Notification: 更新された通知オブジェクト
            
        Raises:
            Notification.DoesNotExist: 通知が存在しない場合
            ValidationError: その他のエラー時
        """
        try:
            with transaction.atomic():
                notification = Notification.objects.get(id=notification_id)
                
                # 既に既読の場合はそのまま返却
                if notification.is_read:
                    return notification
                
                # 既読化
                notification.mark_as_read()
                return notification
                
        except Notification.DoesNotExist:
            raise Notification.DoesNotExist(f"ID {notification_id} の通知が見つかりません")
        except Exception as e:
            raise ValidationError(f"通知の既読化に失敗しました: {str(e)}")

    @classmethod
    def mark_all_as_read(cls, user_id):
        """
        ユーザーの全通知を既読にする
        
        Args:
            user_id (int): ユーザーID
            
        Returns:
            int: 更新された通知数
            
        Raises:
            ValidationError: バリデーションエラー時
        """
        try:
            with transaction.atomic():
                # ユーザーの存在確認
                try:
                    user = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    raise ValidationError("指定されたユーザーが存在しません")
                
                # 未読通知を全て既読化
                updated_count = Notification.objects.filter(
                    user=user,
                    is_read=False
                ).update(is_read=True)
                
                return updated_count
                
        except Exception as e:
            if isinstance(e, ValidationError):
                raise e
            raise ValidationError(f"全通知の既読化に失敗しました: {str(e)}")

    @classmethod
    def delete_notification(cls, notification_id, user_id=None):
        """
        通知削除
        
        Args:
            notification_id (int): 通知ID
            user_id (int, optional): ユーザーID（指定時は所有者チェック）
            
        Returns:
            bool: 削除成功時True
            
        Raises:
            Notification.DoesNotExist: 通知が存在しない場合
            ValidationError: 権限エラーやその他のエラー時
        """
        try:
            with transaction.atomic():
                notification = Notification.objects.get(id=notification_id)
                
                # ユーザー指定時は所有者チェック
                if user_id is not None and notification.user_id != user_id:
                    raise ValidationError("この通知を削除する権限がありません")
                
                # 削除実行
                result = notification.delete_notification()
                if not result:
                    raise ValidationError("通知の削除に失敗しました")
                
                return True
                
        except Notification.DoesNotExist:
            raise Notification.DoesNotExist(f"ID {notification_id} の通知が見つかりません")
        except Exception as e:
            if isinstance(e, ValidationError):
                raise e
            raise ValidationError(f"通知の削除に失敗しました: {str(e)}")

    @classmethod
    def get_unread_count(cls, user_id):
        """
        ユーザーの未読通知数取得
        
        Args:
            user_id (int): ユーザーID
            
        Returns:
            int: 未読通知数
            
        Raises:
            ValidationError: バリデーションエラー時
        """
        try:
            # ユーザーの存在確認
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise ValidationError("指定されたユーザーが存在しません")
            
            return Notification.objects.filter(
                user=user,
                is_read=False
            ).count()
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise e
            raise ValidationError(f"未読通知数の取得に失敗しました: {str(e)}")

    @classmethod
    def bulk_create_notifications(cls, user_ids, message):
        """
        複数ユーザーに一括通知作成
        
        Args:
            user_ids (list): ユーザーIDのリスト
            message (str): 通知メッセージ
            
        Returns:
            list: 作成された通知オブジェクトのリスト
            
        Raises:
            ValidationError: バリデーションエラー時
        """
        try:
            with transaction.atomic():
                # メッセージのバリデーション
                if not message or not message.strip():
                    raise ValidationError("通知メッセージは必須です")
                
                # ユーザーIDのリストが空でないことを確認
                if not user_ids:
                    raise ValidationError("通知対象ユーザーが指定されていません")
                
                # ユーザーの存在確認
                valid_users = User.objects.filter(id__in=user_ids)
                if valid_users.count() != len(user_ids):
                    invalid_ids = set(user_ids) - set(valid_users.values_list('id', flat=True))
                    raise ValidationError(f"存在しないユーザーID: {list(invalid_ids)}")
                
                # 通知一括作成
                notifications = []
                for user in valid_users:
                    notifications.append(
                        Notification(user=user, message=message.strip())
                    )
                
                # バルク作成実行
                created_notifications = Notification.objects.bulk_create(notifications)
                return created_notifications
                
        except Exception as e:
            if isinstance(e, ValidationError):
                raise e
            raise ValidationError(f"一括通知の作成に失敗しました: {str(e)}")

    @classmethod
    def get_notification_statistics(cls, user_id=None):
        """
        通知統計取得
        
        Args:
            user_id (int, optional): ユーザーID（指定時はそのユーザーの統計）
            
        Returns:
            dict: 統計情報
        """
        try:
            base_query = Notification.objects
            
            # ユーザー指定時はフィルター
            if user_id is not None:
                try:
                    user = User.objects.get(id=user_id)
                    base_query = base_query.filter(user=user)
                except User.DoesNotExist:
                    raise ValidationError("指定されたユーザーが存在しません")
            
            # 統計情報収集
            total_notifications = base_query.count()
            unread_notifications = base_query.filter(is_read=False).count()
            read_notifications = base_query.filter(is_read=True).count()
            
            statistics = {
                'total_notifications': total_notifications,
                'unread_notifications': unread_notifications,
                'read_notifications': read_notifications,
                'unread_percentage': round(
                    (unread_notifications / total_notifications * 100) if total_notifications > 0 else 0,
                    2
                )
            }
            
            return statistics
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise e
            raise ValidationError(f"通知統計の取得に失敗しました: {str(e)}")
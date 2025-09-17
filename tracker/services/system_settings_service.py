"""
SystemSettingsService - システム設定管理の業務ロジック
"""
from django.db import transaction
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from tracker.models import SystemSettings


class SystemSettingsService:
    """
    システム設定サービス - システム設定の取得・更新等の業務ロジック
    """

    @classmethod
    def get_settings(cls):
        """
        システム設定取得
        
        Returns:
            SystemSettings: システム設定オブジェクト
        """
        try:
            return SystemSettings.get_settings()
        except Exception as e:
            raise ValidationError(f"システム設定の取得に失敗しました: {str(e)}")

    @classmethod
    def update_settings(cls, **settings_data):
        """
        システム設定更新
        
        Args:
            **settings_data: 設定データ（maintenance_mode, email_sender等）
            
        Returns:
            SystemSettings: 更新されたシステム設定オブジェクト
            
        Raises:
            ValidationError: バリデーションエラー時
        """
        try:
            with transaction.atomic():
                # 現在の設定を取得
                settings = SystemSettings.get_settings()
                
                # 各設定項目の更新とバリデーション
                if 'maintenance_mode' in settings_data:
                    maintenance_mode = settings_data['maintenance_mode']
                    if not isinstance(maintenance_mode, bool):
                        raise ValidationError("maintenance_modeはboolean値である必要があります")
                    settings.maintenance_mode = maintenance_mode
                
                if 'email_sender' in settings_data:
                    email_sender = settings_data['email_sender']
                    if email_sender:  # 空文字は許可
                        try:
                            validate_email(email_sender)
                        except ValidationError:
                            raise ValidationError("email_senderは有効なメールアドレス形式である必要があります")
                    settings.email_sender = email_sender
                
                # その他の未知のフィールドチェック
                known_fields = {'maintenance_mode', 'email_sender'}
                unknown_fields = set(settings_data.keys()) - known_fields
                if unknown_fields:
                    raise ValidationError(f"未知の設定項目: {list(unknown_fields)}")
                
                # 保存
                settings.save()
                return settings
                
        except Exception as e:
            if isinstance(e, ValidationError):
                raise e
            raise ValidationError(f"システム設定の更新に失敗しました: {str(e)}")

    @classmethod
    def set_maintenance_mode(cls, enabled):
        """
        メンテナンスモード設定
        
        Args:
            enabled (bool): メンテナンスモードの有効/無効
            
        Returns:
            SystemSettings: 更新されたシステム設定オブジェクト
            
        Raises:
            ValidationError: バリデーションエラー時
        """
        if not isinstance(enabled, bool):
            raise ValidationError("enabledはboolean値である必要があります")
        
        return cls.update_settings(maintenance_mode=enabled)

    @classmethod
    def set_email_sender(cls, email):
        """
        送信元メールアドレス設定
        
        Args:
            email (str): 送信元メールアドレス
            
        Returns:
            SystemSettings: 更新されたシステム設定オブジェクト
            
        Raises:
            ValidationError: バリデーションエラー時
        """
        return cls.update_settings(email_sender=email)

    @classmethod
    def is_maintenance_mode(cls):
        """
        メンテナンスモード状態確認
        
        Returns:
            bool: メンテナンスモードが有効かどうか
        """
        try:
            settings = cls.get_settings()
            return settings.maintenance_mode
        except Exception:
            # エラー時はセーフサイドに倒す（メンテナンスモードとして扱う）
            return True

    @classmethod
    def get_email_sender(cls):
        """
        送信元メールアドレス取得
        
        Returns:
            str: 送信元メールアドレス（設定されていない場合は空文字）
        """
        try:
            settings = cls.get_settings()
            return settings.email_sender
        except Exception:
            return ""

    @classmethod
    def reset_to_defaults(cls):
        """
        設定をデフォルト値にリセット
        
        Returns:
            SystemSettings: リセットされたシステム設定オブジェクト
            
        Raises:
            ValidationError: バリデーションエラー時
        """
        try:
            return cls.update_settings(
                maintenance_mode=False,
                email_sender=""
            )
        except Exception as e:
            raise ValidationError(f"設定のリセットに失敗しました: {str(e)}")

    @classmethod
    def validate_settings(cls, settings_data):
        """
        設定データのバリデーション（更新前チェック用）
        
        Args:
            settings_data (dict): バリデーション対象の設定データ
            
        Returns:
            bool: バリデーション成功時True
            
        Raises:
            ValidationError: バリデーションエラー時
        """
        try:
            # maintenance_modeチェック
            if 'maintenance_mode' in settings_data:
                maintenance_mode = settings_data['maintenance_mode']
                if not isinstance(maintenance_mode, bool):
                    raise ValidationError("maintenance_modeはboolean値である必要があります")
            
            # email_senderチェック
            if 'email_sender' in settings_data:
                email_sender = settings_data['email_sender']
                if email_sender:  # 空文字は許可
                    try:
                        validate_email(email_sender)
                    except ValidationError:
                        raise ValidationError("email_senderは有効なメールアドレス形式である必要があります")
            
            # 未知のフィールドチェック
            known_fields = {'maintenance_mode', 'email_sender'}
            unknown_fields = set(settings_data.keys()) - known_fields
            if unknown_fields:
                raise ValidationError(f"未知の設定項目: {list(unknown_fields)}")
            
            return True
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise e
            raise ValidationError(f"設定データのバリデーションに失敗しました: {str(e)}")

    @classmethod
    def get_settings_dict(cls):
        """
        設定を辞書形式で取得（API レスポンス用）
        
        Returns:
            dict: 設定データの辞書
        """
        try:
            settings = cls.get_settings()
            return {
                'maintenance_mode': settings.maintenance_mode,
                'email_sender': settings.email_sender,
            }
        except Exception as e:
            raise ValidationError(f"設定辞書の取得に失敗しました: {str(e)}")

    @classmethod
    def update_from_dict(cls, settings_dict):
        """
        辞書から設定を更新（API リクエスト処理用）
        
        Args:
            settings_dict (dict): 設定データの辞書
            
        Returns:
            dict: 更新された設定データの辞書
            
        Raises:
            ValidationError: バリデーションエラー時
        """
        try:
            # バリデーション実行
            cls.validate_settings(settings_dict)
            
            # 更新実行
            updated_settings = cls.update_settings(**settings_dict)
            
            # 辞書形式で返却
            return {
                'maintenance_mode': updated_settings.maintenance_mode,
                'email_sender': updated_settings.email_sender,
            }
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise e
            raise ValidationError(f"設定の辞書更新に失敗しました: {str(e)}")
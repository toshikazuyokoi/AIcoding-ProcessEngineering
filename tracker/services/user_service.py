"""
UserService - ユーザー管理の業務ロジック
"""
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from tracker.models import Project, Issue

User = get_user_model()


class UserService:
    """
    ユーザー管理サービス - 登録・更新・削除・認証等の業務ロジック
    """

    @classmethod
    def create_user(cls, username, email, password, **extra_fields):
        """
        ユーザー新規作成
        
        Args:
            username (str): ユーザー名
            email (str): メールアドレス
            password (str): パスワード
            **extra_fields: 追加フィールド (first_name, last_name等)
            
        Returns:
            User: 作成されたユーザーオブジェクト
            
        Raises:
            ValidationError: バリデーションエラー時
        """
        try:
            with transaction.atomic():
                # メールアドレス重複チェック
                if User.objects.filter(email=email).exists():
                    raise ValidationError("このメールアドレスは既に使用されています")
                
                # ユーザー名重複チェック
                if User.objects.filter(username=username).exists():
                    raise ValidationError("このユーザー名は既に使用されています")
                
                # ユーザー作成
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    **extra_fields
                )
                return user
        except Exception as e:
            raise ValidationError(f"ユーザー作成に失敗しました: {str(e)}")

    @classmethod
    def update_user(cls, user_id, **update_data):
        """
        ユーザー情報更新
        
        Args:
            user_id (int): ユーザーID
            **update_data: 更新データ
            
        Returns:
            User: 更新されたユーザーオブジェクト
            
        Raises:
            User.DoesNotExist: ユーザーが存在しない場合
            ValidationError: バリデーションエラー時
        """
        try:
            with transaction.atomic():
                user = User.objects.get(id=user_id)
                
                # メールアドレス変更時の重複チェック
                if 'email' in update_data:
                    new_email = update_data['email']
                    if User.objects.filter(email=new_email).exclude(id=user_id).exists():
                        raise ValidationError("このメールアドレスは既に使用されています")
                
                # ユーザー名変更時の重複チェック
                if 'username' in update_data:
                    new_username = update_data['username']
                    if User.objects.filter(username=new_username).exclude(id=user_id).exists():
                        raise ValidationError("このユーザー名は既に使用されています")
                
                # パスワード変更時のハッシュ化
                if 'password' in update_data:
                    update_data['password'] = make_password(update_data['password'])
                
                # フィールド更新
                for field, value in update_data.items():
                    if hasattr(user, field):
                        setattr(user, field, value)
                
                user.save()
                return user
                
        except User.DoesNotExist:
            raise
        except Exception as e:
            raise ValidationError(f"ユーザー更新に失敗しました: {str(e)}")

    @classmethod
    def delete_user(cls, user_id):
        """
        ユーザー削除（管理者機能）
        
        Args:
            user_id (int): 削除対象ユーザーID
            
        Returns:
            bool: 削除成功時True
            
        Raises:
            User.DoesNotExist: ユーザーが存在しない場合
            ValidationError: 削除不可能な場合
        """
        try:
            with transaction.atomic():
                user = User.objects.get(id=user_id)
                
                # 削除前チェック（必要に応じて）
                # 例: プロジェクト作成者の場合は削除不可等
                created_projects = Project.objects.filter(created_by=user).count()
                if created_projects > 0:
                    raise ValidationError(f"このユーザーは{created_projects}個のプロジェクトを作成しているため削除できません")
                
                user.delete()
                return True
                
        except User.DoesNotExist:
            raise
        except Exception as e:
            raise ValidationError(f"ユーザー削除に失敗しました: {str(e)}")

    @classmethod
    def get_user_by_id(cls, user_id):
        """
        ID指定でユーザー取得
        
        Args:
            user_id (int): ユーザーID
            
        Returns:
            User or None: ユーザーオブジェクト
        """
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @classmethod
    def get_user_by_email(cls, email):
        """
        メールアドレス指定でユーザー取得
        
        Args:
            email (str): メールアドレス
            
        Returns:
            User or None: ユーザーオブジェクト
        """
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    @classmethod
    def list_users(cls, **filters):
        """
        ユーザー一覧取得（管理者機能）
        
        Args:
            **filters: フィルター条件
            
        Returns:
            QuerySet: ユーザーのクエリセット
        """
        return User.objects.filter(**filters).order_by('-date_joined')

    @classmethod
    def authenticate_user(cls, email, password):
        """
        メールアドレス・パスワードによる認証
        
        Args:
            email (str): メールアドレス
            password (str): パスワード
            
        Returns:
            User or None: 認証成功時はUserオブジェクト、失敗時はNone
        """
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
            return None
        except User.DoesNotExist:
            return None

    @classmethod
    def get_user_statistics(cls, user_id):
        """
        ユーザーの統計情報取得
        
        Args:
            user_id (int): ユーザーID
            
        Returns:
            dict: 統計情報
        """
        try:
            user = User.objects.get(id=user_id)
            
            # 作成したプロジェクト数
            created_projects_count = user.created_projects.count()
            
            # 作成したチケット数
            created_issues_count = user.created_issues.count()
            
            # 担当チケット数
            assigned_issues_count = user.assigned_issues.count()
            
            # 参加プロジェクト数
            member_projects_count = user.projectmember_set.count()
            
            return {
                'created_projects_count': created_projects_count,
                'created_issues_count': created_issues_count,
                'assigned_issues_count': assigned_issues_count,
                'member_projects_count': member_projects_count,
                'total_notifications': user.notifications.count(),
                'unread_notifications': user.notifications.filter(is_read=False).count(),
            }
            
        except User.DoesNotExist:
            return None
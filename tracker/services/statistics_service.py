"""
StatisticsService - 統計情報管理の業務ロジック
"""
from django.db import transaction
from django.core.exceptions import ValidationError
from tracker.models import Project, Issue, Statistics


class StatisticsService:
    """
    統計情報サービス - プロジェクト統計・チケット統計等の業務ロジック
    """

    @classmethod
    def get_project_statistics(cls, project_id):
        """
        プロジェクト統計取得
        
        Args:
            project_id (int): プロジェクトID
            
        Returns:
            Statistics or None: 統計オブジェクト（存在しない場合はNone）
            
        Raises:
            ValidationError: バリデーションエラー時
        """
        try:
            # プロジェクトの存在確認
            try:
                Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                return None
            
            # 統計情報取得（Statisticsモデルのget_statisticsを使用）
            return Statistics.get_statistics(project_id)
            
        except Exception as e:
            raise ValidationError(f"プロジェクト統計の取得に失敗しました: {str(e)}")

    @classmethod
    def get_project_statistics_dict(cls, project_id):
        """
        プロジェクト統計を辞書形式で取得（API レスポンス用）
        
        Args:
            project_id (int): プロジェクトID
            
        Returns:
            dict or None: 統計データの辞書（プロジェクトが存在しない場合はNone）
            
        Raises:
            ValidationError: バリデーションエラー時
        """
        try:
            stats = cls.get_project_statistics(project_id)
            if stats is None:
                return None
            
            return {
                'project_id': project_id,
                'total_issues': stats.total_issues,
                'open': stats.open_issues,
                'closed': stats.closed_issues,
                'by_priority': stats.by_priority
            }
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise e
            raise ValidationError(f"プロジェクト統計辞書の取得に失敗しました: {str(e)}")

    @classmethod
    def get_global_statistics(cls):
        """
        全プロジェクトの統計取得
        
        Returns:
            dict: 全体統計データの辞書
            
        Raises:
            ValidationError: バリデーションエラー時
        """
        try:
            # 全Issues統計
            all_issues = Issue.objects.all()
            total_count = all_issues.count()
            
            # status別集計
            open_statuses = ['open', 'in_progress']
            closed_statuses = ['resolved', 'closed']
            open_count = all_issues.filter(status__in=open_statuses).count()
            closed_count = all_issues.filter(status__in=closed_statuses).count()
            
            # priority別集計
            priority_counts = {}
            for priority_choice in Issue.PRIORITY_CHOICES:
                priority_key = priority_choice[0]
                count = all_issues.filter(priority=priority_key).count()
                if count > 0:
                    priority_counts[priority_key] = count
            
            # プロジェクト数
            project_count = Project.objects.count()
            
            return {
                'total_projects': project_count,
                'total_issues': total_count,
                'open': open_count,
                'closed': closed_count,
                'by_priority': priority_counts
            }
            
        except Exception as e:
            raise ValidationError(f"全体統計の取得に失敗しました: {str(e)}")

    @classmethod
    def get_user_statistics(cls, user_id):
        """
        ユーザー関連統計取得
        
        Args:
            user_id (int): ユーザーID
            
        Returns:
            dict: ユーザー統計データの辞書
            
        Raises:
            ValidationError: バリデーションエラー時
        """
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # ユーザーの存在確認
            try:
                User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise ValidationError("指定されたユーザーが存在しません")
            
            # 作成したチケット統計
            created_issues = Issue.objects.filter(created_by_id=user_id)
            created_count = created_issues.count()
            created_open_count = created_issues.filter(status__in=['open', 'in_progress']).count()
            created_closed_count = created_issues.filter(status__in=['resolved', 'closed']).count()
            
            # 担当チケット統計
            assigned_issues = Issue.objects.filter(assigned_to_id=user_id)
            assigned_count = assigned_issues.count()
            assigned_open_count = assigned_issues.filter(status__in=['open', 'in_progress']).count()
            assigned_closed_count = assigned_issues.filter(status__in=['resolved', 'closed']).count()
            
            # コメント数
            from tracker.models import Comment
            comment_count = Comment.objects.filter(user_id=user_id).count()
            
            return {
                'user_id': user_id,
                'created_issues': {
                    'total': created_count,
                    'open': created_open_count,
                    'closed': created_closed_count
                },
                'assigned_issues': {
                    'total': assigned_count,
                    'open': assigned_open_count,
                    'closed': assigned_closed_count
                },
                'comments': comment_count
            }
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise e
            raise ValidationError(f"ユーザー統計の取得に失敗しました: {str(e)}")

    @classmethod
    def get_issue_status_breakdown(cls, project_id=None):
        """
        ステータス別チケット内訳取得
        
        Args:
            project_id (int, optional): プロジェクトID（指定時はそのプロジェクトのみ）
            
        Returns:
            dict: ステータス別内訳
            
        Raises:
            ValidationError: バリデーションエラー時
        """
        try:
            issues_query = Issue.objects.all()
            
            if project_id is not None:
                # プロジェクトの存在確認
                try:
                    Project.objects.get(id=project_id)
                    issues_query = issues_query.filter(project_id=project_id)
                except Project.DoesNotExist:
                    raise ValidationError("指定されたプロジェクトが存在しません")
            
            # ステータス別集計
            status_counts = {}
            for status_choice in Issue.STATUS_CHOICES:
                status_key = status_choice[0]
                count = issues_query.filter(status=status_key).count()
                status_counts[status_key] = count
            
            return status_counts
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise e
            raise ValidationError(f"ステータス別内訳の取得に失敗しました: {str(e)}")

    @classmethod
    def get_issue_priority_breakdown(cls, project_id=None):
        """
        優先度別チケット内訳取得
        
        Args:
            project_id (int, optional): プロジェクトID（指定時はそのプロジェクトのみ）
            
        Returns:
            dict: 優先度別内訳
            
        Raises:
            ValidationError: バリデーションエラー時
        """
        try:
            issues_query = Issue.objects.all()
            
            if project_id is not None:
                # プロジェクトの存在確認
                try:
                    Project.objects.get(id=project_id)
                    issues_query = issues_query.filter(project_id=project_id)
                except Project.DoesNotExist:
                    raise ValidationError("指定されたプロジェクトが存在しません")
            
            # 優先度別集計
            priority_counts = {}
            for priority_choice in Issue.PRIORITY_CHOICES:
                priority_key = priority_choice[0]
                count = issues_query.filter(priority=priority_key).count()
                if count > 0:  # 0件の場合は辞書に含めない
                    priority_counts[priority_key] = count
            
            return priority_counts
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise e
            raise ValidationError(f"優先度別内訳の取得に失敗しました: {str(e)}")

    @classmethod
    def get_recent_activity_statistics(cls, days=30):
        """
        最近の活動統計取得（過去N日間）
        
        Args:
            days (int): 対象日数（デフォルト30日）
            
        Returns:
            dict: 活動統計データの辞書
            
        Raises:
            ValidationError: バリデーションエラー時
        """
        try:
            from datetime import datetime, timedelta
            from django.utils import timezone
            
            # 対象期間の計算
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            # 期間内の新規チケット
            new_issues = Issue.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date
            ).count()
            
            # 期間内の完了チケット
            closed_issues = Issue.objects.filter(
                updated_at__gte=start_date,
                updated_at__lte=end_date,
                status__in=['resolved', 'closed']
            ).count()
            
            # 期間内のコメント数
            from tracker.models import Comment
            new_comments = Comment.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date
            ).count()
            
            return {
                'period_days': days,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'new_issues': new_issues,
                'closed_issues': closed_issues,
                'new_comments': new_comments
            }
            
        except Exception as e:
            raise ValidationError(f"活動統計の取得に失敗しました: {str(e)}")

    @classmethod
    def validate_statistics_request(cls, project_id=None, user_id=None):
        """
        統計リクエストのバリデーション
        
        Args:
            project_id (int, optional): プロジェクトID
            user_id (int, optional): ユーザーID
            
        Returns:
            bool: バリデーション成功時True
            
        Raises:
            ValidationError: バリデーションエラー時
        """
        try:
            # プロジェクトIDが指定されている場合の存在確認
            if project_id is not None:
                try:
                    Project.objects.get(id=project_id)
                except Project.DoesNotExist:
                    raise ValidationError("指定されたプロジェクトが存在しません")
            
            # ユーザーIDが指定されている場合の存在確認
            if user_id is not None:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    User.objects.get(id=user_id)
                except User.DoesNotExist:
                    raise ValidationError("指定されたユーザーが存在しません")
            
            return True
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise e
            raise ValidationError(f"統計リクエストのバリデーションに失敗しました: {str(e)}")
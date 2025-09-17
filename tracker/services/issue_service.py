"""
IssueService - チケット管理の業務ロジック
"""
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from tracker.models import Project, Issue, IssueHistory, Comment

User = get_user_model()


class IssueService:
    """
    チケット管理サービス - 作成・更新・削除・状態変更・担当者変更等の業務ロジック
    """

    @classmethod
    def create_issue(cls, project_id, created_by_id, title, description, 
                    priority='medium', assigned_to_id=None, **extra_fields):
        """
        チケット新規作成
        
        Args:
            project_id (int): プロジェクトID
            created_by_id (int): 作成者ユーザーID
            title (str): チケットタイトル
            description (str): チケット説明
            priority (str): 優先度 (low, medium, high, critical)
            assigned_to_id (int, optional): 担当者ユーザーID
            **extra_fields: 追加フィールド
            
        Returns:
            Issue: 作成されたチケットオブジェクト
            
        Raises:
            ValidationError: バリデーションエラー時
        """
        try:
            with transaction.atomic():
                # プロジェクトの存在確認
                try:
                    project = Project.objects.get(id=project_id)
                except Project.DoesNotExist:
                    raise ValidationError("指定されたプロジェクトが存在しません")
                
                # 作成者の存在確認
                try:
                    created_by = User.objects.get(id=created_by_id)
                except User.DoesNotExist:
                    raise ValidationError("指定された作成者が存在しません")
                
                # 担当者の存在確認（指定されている場合）
                assigned_to = None
                if assigned_to_id:
                    try:
                        assigned_to = User.objects.get(id=assigned_to_id)
                    except User.DoesNotExist:
                        raise ValidationError("指定された担当者が存在しません")
                
                # バリデーション
                if not title or not title.strip():
                    raise ValidationError("タイトルは必須です")
                if not description or not description.strip():
                    raise ValidationError("説明は必須です")
                
                # 優先度チェック
                valid_priorities = dict(Issue.PRIORITY_CHOICES).keys()
                if priority not in valid_priorities:
                    raise ValidationError(f"無効な優先度です: {priority}")
                
                # チケット作成
                issue = Issue.objects.create(
                    project=project,
                    created_by=created_by,
                    assigned_to=assigned_to,
                    title=title.strip(),
                    description=description.strip(),
                    priority=priority,
                    **extra_fields
                )
                
                return issue
                
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f"チケット作成に失敗しました: {str(e)}")

    @classmethod
    def get_issue_by_id(cls, issue_id):
        """
        ID指定でチケット取得
        
        Args:
            issue_id (int): チケットID
            
        Returns:
            Issue or None: チケットオブジェクト
        """
        try:
            return Issue.objects.get(id=issue_id)
        except Issue.DoesNotExist:
            return None

    @classmethod
    def list_issues(cls, project_id=None, assigned_to_id=None, status=None, **filters):
        """
        チケット一覧取得
        
        Args:
            project_id (int, optional): プロジェクトID
            assigned_to_id (int, optional): 担当者ID
            status (str, optional): ステータス
            **filters: 追加フィルター
            
        Returns:
            QuerySet: チケットのクエリセット
        """
        queryset = Issue.objects.all()
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if assigned_to_id:
            queryset = queryset.filter(assigned_to_id=assigned_to_id)
        if status:
            queryset = queryset.filter(status=status)
        
        # 追加フィルター適用
        queryset = queryset.filter(**filters)
        
        return queryset.order_by('-created_at')

    @classmethod
    def update_issue(cls, issue_id, changed_by_id, **update_data):
        """
        チケット情報更新
        
        Args:
            issue_id (int): チケットID
            changed_by_id (int): 変更者ユーザーID
            **update_data: 更新データ
            
        Returns:
            Issue: 更新されたチケットオブジェクト
            
        Raises:
            Issue.DoesNotExist: チケットが存在しない場合
            ValidationError: バリデーションエラー時
        """
        try:
            with transaction.atomic():
                issue = Issue.objects.get(id=issue_id)
                changed_by = User.objects.get(id=changed_by_id)
                
                # 担当者変更時の存在確認
                if 'assigned_to_id' in update_data:
                    assigned_to_id = update_data.pop('assigned_to_id')
                    if assigned_to_id:
                        try:
                            assigned_to = User.objects.get(id=assigned_to_id)
                            update_data['assigned_to'] = assigned_to
                        except User.DoesNotExist:
                            raise ValidationError("指定された担当者が存在しません")
                    else:
                        update_data['assigned_to'] = None
                
                # 優先度チェック
                if 'priority' in update_data:
                    valid_priorities = dict(Issue.PRIORITY_CHOICES).keys()
                    if update_data['priority'] not in valid_priorities:
                        raise ValidationError(f"無効な優先度です: {update_data['priority']}")
                
                # ステータスチェック
                if 'status' in update_data:
                    valid_statuses = dict(Issue.STATUS_CHOICES).keys()
                    if update_data['status'] not in valid_statuses:
                        raise ValidationError(f"無効なステータスです: {update_data['status']}")
                
                # 履歴記録用に変更前の値を保存
                changes = []
                for field, new_value in update_data.items():
                    if hasattr(issue, field):
                        old_value = getattr(issue, field)
                        if str(old_value) != str(new_value):
                            changes.append((field, str(old_value), str(new_value)))
                
                # チケット更新
                for field, value in update_data.items():
                    if hasattr(issue, field):
                        setattr(issue, field, value)
                
                issue.save()
                
                # 履歴記録
                for field_name, old_value, new_value in changes:
                    IssueHistory.objects.create(
                        issue=issue,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=changed_by
                    )
                
                return issue
                
        except Issue.DoesNotExist:
            raise
        except User.DoesNotExist:
            raise ValidationError("指定された変更者が存在しません")
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f"チケット更新に失敗しました: {str(e)}")

    @classmethod
    def change_status(cls, issue_id, new_status, changed_by_id):
        """
        チケット状態変更
        
        Args:
            issue_id (int): チケットID
            new_status (str): 新しいステータス
            changed_by_id (int): 変更者ユーザーID
            
        Returns:
            Issue: 更新されたチケットオブジェクト
            
        Raises:
            Issue.DoesNotExist: チケットが存在しない場合
            ValidationError: バリデーションエラー時
        """
        try:
            with transaction.atomic():
                issue = Issue.objects.get(id=issue_id)
                changed_by = User.objects.get(id=changed_by_id)
                
                # ステータスバリデーション
                valid_statuses = dict(Issue.STATUS_CHOICES).keys()
                if new_status not in valid_statuses:
                    raise ValidationError(f"無効なステータスです: {new_status}")
                
                old_status = issue.status
                if old_status == new_status:
                    return issue  # 変更なしの場合はそのまま返す
                
                # ステータス更新
                issue.status = new_status
                issue.save()
                
                # 履歴記録
                IssueHistory.objects.create(
                    issue=issue,
                    field_name='status',
                    old_value=old_status,
                    new_value=new_status,
                    changed_by=changed_by
                )
                
                return issue
                
        except Issue.DoesNotExist:
            raise
        except User.DoesNotExist:
            raise ValidationError("指定された変更者が存在しません")
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f"ステータス変更に失敗しました: {str(e)}")

    @classmethod
    def assign_issue(cls, issue_id, assigned_to_id, changed_by_id):
        """
        チケット担当者変更
        
        Args:
            issue_id (int): チケットID
            assigned_to_id (int or None): 担当者ユーザーID（Noneで未割当）
            changed_by_id (int): 変更者ユーザーID
            
        Returns:
            Issue: 更新されたチケットオブジェクト
            
        Raises:
            Issue.DoesNotExist: チケットが存在しない場合
            ValidationError: バリデーションエラー時
        """
        try:
            with transaction.atomic():
                issue = Issue.objects.get(id=issue_id)
                changed_by = User.objects.get(id=changed_by_id)
                
                # 担当者の存在確認
                assigned_to = None
                if assigned_to_id:
                    try:
                        assigned_to = User.objects.get(id=assigned_to_id)
                    except User.DoesNotExist:
                        raise ValidationError("指定された担当者が存在しません")
                
                old_assigned = issue.assigned_to
                old_assigned_name = old_assigned.username if old_assigned else "未割当"
                new_assigned_name = assigned_to.username if assigned_to else "未割当"
                
                if old_assigned == assigned_to:
                    return issue  # 変更なしの場合はそのまま返す
                
                # 担当者更新
                issue.assigned_to = assigned_to
                issue.save()
                
                # 履歴記録
                IssueHistory.objects.create(
                    issue=issue,
                    field_name='assigned_to',
                    old_value=old_assigned_name,
                    new_value=new_assigned_name,
                    changed_by=changed_by
                )
                
                return issue
                
        except Issue.DoesNotExist:
            raise
        except User.DoesNotExist:
            raise ValidationError("指定された変更者が存在しません")
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f"担当者変更に失敗しました: {str(e)}")

    @classmethod
    def delete_issue(cls, issue_id, deleted_by_id):
        """
        チケット削除
        
        Args:
            issue_id (int): チケットID
            deleted_by_id (int): 削除者ユーザーID
            
        Returns:
            bool: 削除成功時True
            
        Raises:
            Issue.DoesNotExist: チケットが存在しない場合
            ValidationError: 削除不可能な場合
        """
        try:
            with transaction.atomic():
                issue = Issue.objects.get(id=issue_id)
                deleted_by = User.objects.get(id=deleted_by_id)
                
                # 削除前チェック（必要に応じて）
                # 例: クローズ状態のチケットのみ削除可能等
                
                issue.delete()
                return True
                
        except Issue.DoesNotExist:
            raise
        except User.DoesNotExist:
            raise ValidationError("指定された削除者が存在しません")
        except Exception as e:
            raise ValidationError(f"チケット削除に失敗しました: {str(e)}")

    @classmethod
    def add_comment(cls, issue_id, user_id, content):
        """
        チケットにコメント追加
        
        Args:
            issue_id (int): チケットID
            user_id (int): コメント投稿者ユーザーID
            content (str): コメント内容
            
        Returns:
            Comment: 作成されたコメントオブジェクト
            
        Raises:
            Issue.DoesNotExist: チケットが存在しない場合
            ValidationError: バリデーションエラー時
        """
        try:
            with transaction.atomic():
                issue = Issue.objects.get(id=issue_id)
                user = User.objects.get(id=user_id)
                
                # コメント内容バリデーション
                if not content or not content.strip():
                    raise ValidationError("コメント内容は必須です")
                
                # コメント作成
                comment = Comment.objects.create(
                    issue=issue,
                    user=user,
                    content=content.strip()
                )
                
                return comment
                
        except Issue.DoesNotExist:
            raise
        except User.DoesNotExist:
            raise ValidationError("指定されたユーザーが存在しません")
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f"コメント追加に失敗しました: {str(e)}")

    @classmethod
    def get_issue_history(cls, issue_id):
        """
        チケット履歴取得
        
        Args:
            issue_id (int): チケットID
            
        Returns:
            QuerySet: 履歴のクエリセット
            
        Raises:
            Issue.DoesNotExist: チケットが存在しない場合
        """
        issue = Issue.objects.get(id=issue_id)
        return issue.get_history()

    @classmethod
    def get_issue_comments(cls, issue_id):
        """
        チケットコメント一覧取得
        
        Args:
            issue_id (int): チケットID
            
        Returns:
            QuerySet: コメントのクエリセット
            
        Raises:
            Issue.DoesNotExist: チケットが存在しない場合
        """
        issue = Issue.objects.get(id=issue_id)
        return Comment.objects.filter(issue=issue).order_by('created_at')

    @classmethod
    def get_issue_statistics(cls, project_id=None):
        """
        チケット統計情報取得
        
        Args:
            project_id (int, optional): プロジェクトID（指定時はそのプロジェクトのみ）
            
        Returns:
            dict: 統計情報
        """
        from tracker.models import Statistics
        
        if project_id:
            return Statistics.get_statistics(project_id)
        else:
            # 全体統計
            total = Issue.objects.count()
            status_counts = {}
            for status_choice in Issue.STATUS_CHOICES:
                status = status_choice[0]
                count = Issue.objects.filter(status=status).count()
                if count > 0:
                    status_counts[status] = count
                    
            priority_counts = {}
            for priority_choice in Issue.PRIORITY_CHOICES:
                priority = priority_choice[0]
                count = Issue.objects.filter(priority=priority).count()
                if count > 0:
                    priority_counts[priority] = count
            
            return {
                'total_issues': total,
                'by_status': status_counts,
                'by_priority': priority_counts,
            }
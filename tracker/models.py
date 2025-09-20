from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """
    ユーザーモデル - 認証・プロファイル管理
    """
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    def authenticate_user(self, password):
        """パスワード認証"""
        return self.check_password(password)

    def update_profile(self, profile_data):
        """プロファイル更新"""
        for field, value in profile_data.items():
            if hasattr(self, field):
                setattr(self, field, value)
        self.save()
        return self

    def get_projects(self):
        """参加プロジェクト一覧取得"""
        return self.created_projects.all() | Project.objects.filter(projectmember__user=self)

    def edit_user(self, user_data):
        """ユーザー情報編集"""
        return self.update_profile(user_data)

    def delete_user(self):
        """ユーザー削除"""
        try:
            self.delete()
            return True
        except Exception:
            return False


class Project(models.Model):
    """
    プロジェクトモデル - メンバー・設定管理
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def add_member(self, user, role='member'):
        """メンバー追加"""
        project_member, created = ProjectMember.objects.get_or_create(
            project=self,
            user=user,
            defaults={'role': role}
        )
        return project_member

    def get_members(self):
        """メンバー一覧取得"""
        return self.projectmember_set.all()

    def get_issues(self):
        """チケット一覧取得"""
        return self.issue_set.all()

    def edit_project(self, project_data):
        """プロジェクト情報編集"""
        for field, value in project_data.items():
            if hasattr(self, field):
                setattr(self, field, value)
        self.save()
        return self

    def delete_project(self):
        """プロジェクト削除"""
        try:
            self.delete()
            return True
        except Exception:
            return False


class ProjectMember(models.Model):
    """
    参加者管理 - 権限・ロール管理
    """
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Project Manager'),
        ('member', 'Member'),
        ('viewer', 'Viewer'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'user')
        ordering = ['-joined_at']

    def __str__(self):
        return f"{self.user.username} - {self.project.name} ({self.role})"

    def change_role(self, role):
        """権限変更"""
        if role in dict(self.ROLE_CHOICES):
            self.role = role
            self.save()
            return True
        return False


class Issue(models.Model):
    """
    チケット管理 - 状態・優先度・担当者
    """
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_issues')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_issues')
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.project.name}] {self.title}"

    def update_status(self, status, changed_by=None):
        """状態変更"""
        if status in dict(self.STATUS_CHOICES):
            old_status = self.status
            self.status = status
            self.save()
            
            # 履歴記録
            if changed_by:
                IssueHistory.objects.create(
                    issue=self,
                    field_name='status',
                    old_value=old_status,
                    new_value=status,
                    changed_by=changed_by
                )
            return True
        return False

    def add_comment(self, comment):
        """コメント追加"""
        try:
            comment.issue = self
            comment.save()
            return True
        except Exception:
            return False

    def get_history(self):
        """履歴取得"""
        return self.issuehistory_set.all()

    def edit_issue(self, issue_data, changed_by=None):
        """チケット情報編集"""
        changes = []
        for field, new_value in issue_data.items():
            if hasattr(self, field):
                old_value = getattr(self, field)
                if old_value != new_value:
                    setattr(self, field, new_value)
                    changes.append((field, str(old_value), str(new_value)))
        
        self.save()
        
        # 履歴記録
        if changed_by:
            for field_name, old_value, new_value in changes:
                IssueHistory.objects.create(
                    issue=self,
                    field_name=field_name,
                    old_value=old_value,
                    new_value=new_value,
                    changed_by=changed_by
                )
        
        return self

    def delete_issue(self):
        """チケット削除"""
        try:
            self.delete()
            return True
        except Exception:
            return False


class IssueHistory(models.Model):
    """
    履歴管理 - 変更履歴管理
    """
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.issue.title} - {self.field_name} changed by {self.changed_by.username}"

    def get_changes(self):
        """変更内容取得"""
        return {
            'field': self.field_name,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'changed_by': self.changed_by.username,
            'changed_at': self.changed_at
        }


class Comment(models.Model):
    """
    コメント管理 - チケットへのコメント
    """
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.issue.title}"

    def edit_content(self, content):
        """コメント編集"""
        self.content = content
        self.save()
        return True

    def delete_comment(self):
        """コメント削除"""
        try:
            self.delete()
            return True
        except Exception:
            return False


class Notification(models.Model):
    """
    通知管理 - メール・画面通知
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}..."

    def mark_as_read(self):
        """既読化"""
        self.is_read = True
        self.save()
        return True

    @classmethod
    def get_notifications(cls, user, unread_only=False):
        """通知一覧取得"""
        queryset = cls.objects.filter(user=user)
        if unread_only:
            queryset = queryset.filter(is_read=False)
        return queryset

    def delete_notification(self):
        """通知削除"""
        try:
            self.delete()
            return True
        except Exception:
            return False


class SystemSettings(models.Model):
    """
    システム設定 - メンテナンスモードや送信元メールなどの全体設定
    シングルトン（1レコード）のみを保持する。
    """
    maintenance_mode = models.BooleanField(default=False)
    email_sender = models.EmailField(blank=True, default="")

    class Meta:
        verbose_name = "System Settings"

    def __str__(self):
        return f"SystemSettings(maintenance_mode={self.maintenance_mode}, email_sender='{self.email_sender}')"

    def save(self, *args, **kwargs):
        """常にPK=1で保存し、他のレコードは削除して単一性を担保する"""
        self.pk = 1
        super().save(*args, **kwargs)
        # 念のため他レコードを削除（競合防止の簡易策）
        SystemSettings.objects.exclude(pk=self.pk).delete()
        return None

    @classmethod
    def get_settings(cls):
        """設定オブジェクトを取得（なければ作成）"""
        obj, created = cls.objects.get_or_create(pk=1, defaults={})
        return obj

    @classmethod
    def update_settings(cls, settings_data):
        """設定更新して保存、更新後のオブジェクトを返却する"""
        obj = cls.get_settings()
        changed = False
        for field, value in (settings_data or {}).items():
            if hasattr(obj, field):
                if getattr(obj, field) != value:
                    setattr(obj, field, value)
                    changed = True
        if changed:
            obj.save()
        return obj


class Statistics(models.Model):
    """
    統計情報 - プロジェクトごとのチケット統計
    実際にはテーブルに保存せず、計算結果を返すビュー的なクラス
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    total_issues = models.IntegerField(default=0)
    open_issues = models.IntegerField(default=0, db_column='open')
    closed_issues = models.IntegerField(default=0, db_column='closed')
    by_priority_json = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Statistics"
        verbose_name_plural = "Statistics"

    def __str__(self):
        return f"Statistics(project={self.project.name}, total={self.total_issues}, open={self.open_issues}, closed={self.closed_issues})"

    @property
    def by_priority(self):
        """優先度別集計をdictで返す"""
        return self.by_priority_json or {}

    @by_priority.setter
    def by_priority(self, value):
        """優先度別集計をJSONフィールドに保存"""
        self.by_priority_json = value or {}

    @classmethod
    def get_statistics(cls, project_id):
        """指定プロジェクトの統計情報を計算して返す"""
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return None

        # Issue統計を計算
        issues = Issue.objects.filter(project=project)
        total_count = issues.count()
        
        # status別集計
        open_statuses = ['open', 'in_progress']
        closed_statuses = ['resolved', 'closed']
        open_count = issues.filter(status__in=open_statuses).count()
        closed_count = issues.filter(status__in=closed_statuses).count()
        
        # priority別集計
        priority_counts = {}
        for priority_choice in Issue.PRIORITY_CHOICES:
            priority_key = priority_choice[0]
            count = issues.filter(priority=priority_key).count()
            if count > 0:
                priority_counts[priority_key] = count

        # Statisticsオブジェクトを作成（DBには保存しない）
        stats = cls(
            project=project,
            total_issues=total_count,
            open_issues=open_count,
            closed_issues=closed_count,
            by_priority_json=priority_counts
        )
        return stats

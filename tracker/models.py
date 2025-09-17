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

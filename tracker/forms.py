from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import Issue, Project

User = get_user_model()


class LoginForm(forms.Form):
    email = forms.EmailField(label="メールアドレス", max_length=254)
    password = forms.CharField(label="パスワード", strip=False, widget=forms.PasswordInput)
    remember_me = forms.BooleanField(label="ログイン状態を保持する", required=False, initial=False)

    error_messages = {
        "invalid_login": "メールアドレスまたはパスワードが正しくありません。",
        "inactive": "このアカウントは無効化されています。",
    }

    user = None  # Will hold the authenticated user on successful clean

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        if email and password:
            UserModel = get_user_model()
            try:
                # Look up by email, then authenticate with username since USERNAME_FIELD remains 'username'
                user_obj = UserModel.objects.get(email=email)
                username = user_obj.get_username()
            except UserModel.DoesNotExist:
                raise forms.ValidationError(self.error_messages["invalid_login"], code="invalid_login")

            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError(self.error_messages["invalid_login"], code="invalid_login")
            if not user.is_active:
                raise forms.ValidationError(self.error_messages["inactive"], code="inactive")
            self.user = user
        return cleaned_data

    def get_user(self):
        return self.user


class UserCreateForm(UserCreationForm):
    """ユーザー作成フォーム"""
    username = forms.CharField(
        label="ユーザー名",
        max_length=20,
        min_length=3,
        help_text="3-20文字の英数字で入力してください",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    email = forms.EmailField(
        label="メールアドレス",
        max_length=100,
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    first_name = forms.CharField(
        label="名",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    last_name = forms.CharField(
        label="姓",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    is_active = forms.BooleanField(
        label="アクティブ",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )
    is_staff = forms.BooleanField(
        label="スタッフ権限",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "first_name", "last_name", "password1", "password2", "is_active", "is_staff")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({"class": "form-control"})

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username:
            # Check for alphanumeric only
            if not username.replace("_", "").isalnum():
                raise ValidationError("ユーザー名は英数字とアンダースコアのみ使用できます。")
            # Check uniqueness
            UserModel = get_user_model()
            if UserModel.objects.filter(username=username).exists():
                raise ValidationError("このユーザー名は既に使用されています。")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            UserModel = get_user_model()
            if UserModel.objects.filter(email=email).exists():
                raise ValidationError("このメールアドレスは既に使用されています。")
        return email


class UserEditForm(forms.ModelForm):
    """ユーザー編集フォーム"""
    username = forms.CharField(
        label="ユーザー名",
        max_length=20,
        min_length=3,
        help_text="3-20文字の英数字で入力してください",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    email = forms.EmailField(
        label="メールアドレス",
        max_length=100,
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    first_name = forms.CharField(
        label="名",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    last_name = forms.CharField(
        label="姓",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    is_active = forms.BooleanField(
        label="アクティブ",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )
    is_staff = forms.BooleanField(
        label="スタッフ権限",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "first_name", "last_name", "is_active", "is_staff")

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get("instance")
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username:
            # Check for alphanumeric only
            if not username.replace("_", "").isalnum():
                raise ValidationError("ユーザー名は英数字とアンダースコアのみ使用できます。")
            # Check uniqueness (excluding current user)
            UserModel = get_user_model()
            if UserModel.objects.filter(username=username).exclude(id=self.instance.id if self.instance else None).exists():
                raise ValidationError("このユーザー名は既に使用されています。")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            UserModel = get_user_model()
            if UserModel.objects.filter(email=email).exclude(id=self.instance.id if self.instance else None).exists():
                raise ValidationError("このメールアドレスは既に使用されています。")
        return email


class UserSearchForm(forms.Form):
    """ユーザー検索フォーム"""
    search = forms.CharField(
        label="検索",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "ユーザー名またはメールアドレス"
        })
    )
    is_active = forms.ChoiceField(
        label="ステータス",
        choices=[("", "全て"), ("true", "アクティブ"), ("false", "非アクティブ")],
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )
    is_staff = forms.ChoiceField(
        label="権限",
        choices=[("", "全て"), ("true", "スタッフ"), ("false", "一般")],
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    def filter_queryset(self, queryset):
        """検索条件に基づいてクエリセットをフィルタ"""
        search = self.cleaned_data.get("search")
        is_active = self.cleaned_data.get("is_active")
        is_staff = self.cleaned_data.get("is_staff")

        if search:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(username__icontains=search) | Q(email__icontains=search) |
                Q(first_name__icontains=search) | Q(last_name__icontains=search)
            )

        if is_active:
            queryset = queryset.filter(is_active=(is_active == "true"))

        if is_staff:
            queryset = queryset.filter(is_staff=(is_staff == "true"))

        return queryset


class UserPasswordResetForm(forms.Form):
    """ユーザーパスワードリセットフォーム"""
    new_password1 = forms.CharField(
        label="新しいパスワード",
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        help_text="8文字以上で入力してください"
    )
    new_password2 = forms.CharField(
        label="新しいパスワード（確認）",
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        help_text="確認のため、同じパスワードを入力してください"
    )

    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("パスワードが一致しません。")
        return password2

    def clean_new_password1(self):
        password = self.cleaned_data.get("new_password1")
        if password and len(password) < 8:
            raise ValidationError("パスワードは8文字以上で入力してください。")
        return password


class IssueFilterForm(forms.Form):
    """チケット一覧フィルタフォーム"""
    search = forms.CharField(
        label="検索",
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "タイトルまたは説明を検索"
        })
    )
    
    project = forms.ModelChoiceField(
        label="プロジェクト",
        queryset=Project.objects.all(),
        required=False,
        empty_label="全てのプロジェクト",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    
    status = forms.ChoiceField(
        label="ステータス",
        choices=[("", "全てのステータス")] + Issue.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )
    
    priority = forms.ChoiceField(
        label="優先度",
        choices=[("", "全ての優先度")] + Issue.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )
    
    assigned_to = forms.ModelChoiceField(
        label="担当者",
        queryset=get_user_model().objects.all(),
        required=False,
        empty_label="全ての担当者",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    
    sort_by = forms.ChoiceField(
        label="並び順",
        choices=[
            ("-created_at", "作成日（新しい順）"),
            ("created_at", "作成日（古い順）"),
            ("title", "タイトル（昇順）"),
            ("-title", "タイトル（降順）"),
            ("status", "ステータス"),
            ("priority", "優先度"),
        ],
        initial="-created_at",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    def filter_queryset(self, queryset):
        """検索条件に基づいてクエリセットをフィルタ"""
        search = self.cleaned_data.get("search")
        project = self.cleaned_data.get("project")
        status = self.cleaned_data.get("status")
        priority = self.cleaned_data.get("priority")
        assigned_to = self.cleaned_data.get("assigned_to")
        sort_by = self.cleaned_data.get("sort_by", "-created_at")

        if search:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

        if project:
            queryset = queryset.filter(project=project)

        if status:
            queryset = queryset.filter(status=status)

        if priority:
            queryset = queryset.filter(priority=priority)

        if assigned_to:
            queryset = queryset.filter(assigned_to=assigned_to)

        # ソート適用
        if sort_by:
            # 優先度でのソートは特別な順序が必要
            if sort_by == "priority":
                # critical > high > medium > low の順
                priority_order = ["critical", "high", "medium", "low"]
                queryset = queryset.extra(
                    select={'priority_order': 
                        "CASE priority " +
                        " WHEN 'critical' THEN 1" +
                        " WHEN 'high' THEN 2" +
                        " WHEN 'medium' THEN 3" +
                        " WHEN 'low' THEN 4" +
                        " ELSE 5 END"
                    },
                    order_by=['priority_order']
                )
            else:
                queryset = queryset.order_by(sort_by)

        return queryset


class IssueForm(forms.ModelForm):
    """チケット作成・編集フォーム"""
    
    class Meta:
        model = Issue
        fields = ['title', 'description', 'priority', 'assigned_to', 'due_date', 'project']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'チケットのタイトルを入力してください'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'チケットの詳細説明を入力してください'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'form-select'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'project': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        labels = {
            'title': 'タイトル',
            'description': '説明',
            'priority': '優先度',
            'assigned_to': '担当者',
            'due_date': '締切日',
            'project': 'プロジェクト'
        }
        error_messages = {
            'title': {
                'required': 'この項目は必須です。',
                'max_length': 'タイトルが長すぎます。',
            },
            'description': {
                'required': 'この項目は必須です。',
            },
            'priority': {
                'required': 'この項目は必須です。',
                'invalid_choice': '有効な選択肢を選んでください。',
            },
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # 担当者選択肢をアクティブユーザーのみに制限
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True)
        self.fields['assigned_to'].empty_label = "未割り当て"
        
        # プロジェクト選択肢を制限（現状は全プロジェクト）
        self.fields['project'].queryset = Project.objects.all()
        
        # 必須フィールドをマーク
        self.fields['title'].required = True
        self.fields['description'].required = True
        self.fields['priority'].required = True
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title and len(title.strip()) < 5:
            raise ValidationError('タイトルは5文字以上で入力してください。')
        return title.strip() if title else title
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description and len(description.strip()) < 10:
            raise ValidationError('説明は10文字以上で入力してください。')
        return description.strip() if description else description

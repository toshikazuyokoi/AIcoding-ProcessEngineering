from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError


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

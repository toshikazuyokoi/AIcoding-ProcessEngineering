from django import forms
from django.contrib.auth import authenticate, get_user_model


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

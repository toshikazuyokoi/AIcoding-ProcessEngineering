from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.conf import settings

from .forms import LoginForm


@require_http_methods(["GET", "POST"])
def login_view(request):
	if request.user.is_authenticated:
		return redirect('dashboard')

	form = LoginForm(request.POST or None)
	if request.method == 'POST':
		if form.is_valid():
			user = form.get_user()
			auth_login(request, user)
			# Session expiry handling
			if not form.cleaned_data.get('remember_me'):
				# Browser session only
				request.session.set_expiry(0)
			else:
				# Respect global SESSION_COOKIE_AGE (default) or extend mildly if needed later
				request.session.set_expiry(getattr(settings, 'REMEMBER_ME_AGE', settings.SESSION_COOKIE_AGE))
			messages.success(request, 'ログインしました。')
			return redirect('dashboard')
		else:
			messages.error(request, 'ログインに失敗しました。')

	return render(request, 'login.html', {"form": form})


@login_required
def dashboard_view(request):
	# Placeholder dashboard until Issue #18+ implements real content
	return render(request, 'dashboard.html', {})


@login_required
def logout_view(request):
	auth_logout(request)
	messages.info(request, 'ログアウトしました。')
	return redirect('login')

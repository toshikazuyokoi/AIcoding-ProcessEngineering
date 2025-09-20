from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods, require_POST
from django.conf import settings
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .forms import LoginForm, UserCreateForm, UserEditForm, UserSearchForm, UserPasswordResetForm


def is_staff_user(user):
	"""スタッフユーザー権限チェック"""
	return user.is_staff


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


# User Management Views
@login_required
@user_passes_test(is_staff_user)
def user_list_view(request):
	"""ユーザー一覧表示"""
	UserModel = get_user_model()
	users = UserModel.objects.all().order_by('-date_joined')
	
	# 検索フィルター処理
	search_form = UserSearchForm(request.GET or None)
	if search_form.is_valid():
		users = search_form.filter_queryset(users)
	
	# ページネーション
	paginator = Paginator(users, 20)  # 20 users per page
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	
	context = {
		'page_obj': page_obj,
		'search_form': search_form,
		'total_users': UserModel.objects.count(),
		'active_users': UserModel.objects.filter(is_active=True).count(),
		'staff_users': UserModel.objects.filter(is_staff=True).count(),
	}
	return render(request, 'users/user_list.html', context)


@login_required
@user_passes_test(is_staff_user)
@require_http_methods(["GET", "POST"])
def user_create_view(request):
	"""ユーザー作成"""
	if request.method == 'POST':
		form = UserCreateForm(request.POST)
		if form.is_valid():
			user = form.save()
			messages.success(request, f'ユーザー「{user.username}」を作成しました。')
			return redirect('user_list')
		else:
			messages.error(request, 'ユーザーの作成に失敗しました。')
	else:
		form = UserCreateForm()
	
	context = {'form': form}
	return render(request, 'users/user_create.html', context)


@login_required
@user_passes_test(is_staff_user)
@require_http_methods(["GET", "POST"])
def user_edit_view(request, user_id):
	"""ユーザー編集"""
	UserModel = get_user_model()
	user = get_object_or_404(UserModel, id=user_id)
	
	if request.method == 'POST':
		form = UserEditForm(request.POST, instance=user)
		if form.is_valid():
			user = form.save()
			messages.success(request, f'ユーザー「{user.username}」を更新しました。')
			return redirect('user_list')
		else:
			messages.error(request, 'ユーザーの更新に失敗しました。')
	else:
		form = UserEditForm(instance=user)
	
	context = {'form': form, 'user': user}
	return render(request, 'users/user_edit.html', context)


@login_required
@user_passes_test(is_staff_user)
@require_http_methods(["GET", "POST"])
def user_delete_view(request, user_id):
	"""ユーザー削除"""
	UserModel = get_user_model()
	user = get_object_or_404(UserModel, id=user_id)
	
	# 自分自身は削除できない
	if user.id == request.user.id:
		messages.error(request, '自分自身は削除できません。')
		return redirect('user_list')
	
	# スーパーユーザーは削除できない（安全措置）
	if user.is_superuser:
		messages.error(request, 'スーパーユーザーは削除できません。')
		return redirect('user_list')
	
	if request.method == 'POST':
		username = user.username
		user.delete()
		messages.success(request, f'ユーザー「{username}」を削除しました。')
		return redirect('user_list')
	
	context = {'user': user}
	return render(request, 'users/user_delete_confirm.html', context)


@login_required
@user_passes_test(is_staff_user)
@require_http_methods(["GET", "POST"])
def user_password_reset_view(request, user_id):
	"""ユーザーパスワードリセット"""
	UserModel = get_user_model()
	user = get_object_or_404(UserModel, id=user_id)
	
	if request.method == 'POST':
		form = UserPasswordResetForm(request.POST)
		if form.is_valid():
			user.set_password(form.cleaned_data['new_password1'])
			user.save()
			messages.success(request, f'ユーザー「{user.username}」のパスワードをリセットしました。')
			return redirect('user_list')
		else:
			messages.error(request, 'パスワードのリセットに失敗しました。')
	else:
		form = UserPasswordResetForm()
	
	context = {'form': form, 'user': user}
	return render(request, 'users/user_password_reset.html', context)


@login_required
@user_passes_test(is_staff_user)
@require_POST
def user_toggle_active_view(request, user_id):
	"""ユーザーアクティブ状態切り替え（AJAX）"""
	UserModel = get_user_model()
	user = get_object_or_404(UserModel, id=user_id)
	
	# 自分自身は無効化できない
	if user.id == request.user.id:
		return JsonResponse({'success': False, 'message': '自分自身は無効化できません。'})
	
	# スーパーユーザーは無効化できない（安全措置）
	if user.is_superuser:
		return JsonResponse({'success': False, 'message': 'スーパーユーザーは無効化できません。'})
	
	user.is_active = not user.is_active
	user.save()
	
	status_text = 'アクティブ' if user.is_active else '非アクティブ'
	return JsonResponse({
		'success': True,
		'is_active': user.is_active,
		'message': f'ユーザー「{user.username}」を{status_text}に変更しました。'
	})

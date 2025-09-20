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

from .forms import LoginForm, UserCreateForm, UserEditForm, UserSearchForm, UserPasswordResetForm, IssueFilterForm, IssueForm
from .models import Issue, Comment, Notification


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


# Issue Management Views
@login_required
def issue_list_view(request):
	"""チケット一覧表示"""
	# 基本クエリセット（全ユーザーがアクセス可能）
	issues = Issue.objects.select_related('project', 'created_by', 'assigned_to').all()
	
	# フィルター処理
	filter_form = IssueFilterForm(request.GET or None)
	if filter_form.is_valid():
		issues = filter_form.filter_queryset(issues)
	
	# ページネーション
	paginator = Paginator(issues, 20)  # 20 issues per page
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	
	# 統計情報
	total_issues = Issue.objects.count()
	open_issues = Issue.objects.filter(status__in=['open', 'in_progress']).count()
	closed_issues = Issue.objects.filter(status__in=['resolved', 'closed']).count()
	
	# ステータス別集計
	status_stats = {}
	for status_choice in Issue.STATUS_CHOICES:
		status_key = status_choice[0]
		status_name = status_choice[1]
		count = Issue.objects.filter(status=status_key).count()
		if count > 0:
			status_stats[status_name] = count
	
	# 優先度別集計
	priority_stats = {}
	for priority_choice in Issue.PRIORITY_CHOICES:
		priority_key = priority_choice[0]
		priority_name = priority_choice[1]
		count = Issue.objects.filter(priority=priority_key).count()
		if count > 0:
			priority_stats[priority_name] = count
	
	context = {
		'page_obj': page_obj,
		'filter_form': filter_form,
		'total_issues': total_issues,
		'open_issues': open_issues,
		'closed_issues': closed_issues,
		'status_stats': status_stats,
		'priority_stats': priority_stats,
	}
	return render(request, 'issues/issue_list.html', context)


@login_required
def issue_detail_view(request, issue_id):
	"""チケット詳細表示（SC-005 チケット詳細画面）"""
	try:
		# チケット情報を取得（関連データも含む）
		issue = Issue.objects.select_related(
			'project', 'created_by', 'assigned_to'
		).get(id=issue_id)
		
		# チケットのコメント一覧を取得（作成日順）
		comments = Comment.objects.filter(
			issue=issue
		).select_related('user').order_by('created_at')
		
		context = {
			'issue': issue,
			'comments': comments,
		}
		return render(request, 'issues/issue_detail.html', context)
		
	except Issue.DoesNotExist:
		# チケットが存在しない場合は404エラー
		from django.http import Http404
		raise Http404("チケットが見つかりません。")


@login_required
def issue_create_view(request):
	"""チケット作成画面（SC-006 チケット作成・編集画面）"""
	if request.method == 'POST':
		form = IssueForm(request.POST, user=request.user)
		if form.is_valid():
			# created_by を現在のユーザーに設定
			issue = form.save(commit=False)
			issue.created_by = request.user
			issue.save()
			
			messages.success(request, f'チケット「{issue.title}」を作成しました。')
			return redirect('issue_detail', issue_id=issue.id)
	else:
		form = IssueForm(user=request.user)
	
	context = {
		'form': form,
		'mode': 'create'
	}
	return render(request, 'issues/issue_form.html', context)


@login_required  
def issue_edit_view(request, issue_id):
	"""チケット編集画面（SC-006 チケット作成・編集画面）"""
	try:
		issue = Issue.objects.get(id=issue_id)
		
		if request.method == 'POST':
			form = IssueForm(request.POST, instance=issue, user=request.user)
			if form.is_valid():
				updated_issue = form.save()
				messages.success(request, f'チケット「{updated_issue.title}」を更新しました。')
				return redirect('issue_detail', issue_id=updated_issue.id)
		else:
			form = IssueForm(instance=issue, user=request.user)
		
		context = {
			'form': form,
			'issue': issue,
			'mode': 'edit'
		}
		return render(request, 'issues/issue_form.html', context)
		
	except Issue.DoesNotExist:
		from django.http import Http404
		raise Http404("チケットが見つかりません。")


@login_required
def notification_list_view(request):
	"""通知一覧画面（SC-008 通知一覧画面）"""
	from django.core.paginator import Paginator
	from .services.notification_service import NotificationService
	from .models import Notification
	
	try:
		# フィルター処理
		notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
		
		# 未読フィルター
		unread_only = request.GET.get('unread_only')
		if unread_only == 'true':
			notifications = notifications.filter(is_read=False)
		
		# 日付フィルター（作成日）
		date_from = request.GET.get('date_from')
		date_to = request.GET.get('date_to')
		if date_from:
			from datetime import datetime
			notifications = notifications.filter(created_at__date__gte=datetime.strptime(date_from, '%Y-%m-%d').date())
		if date_to:
			from datetime import datetime
			notifications = notifications.filter(created_at__date__lte=datetime.strptime(date_to, '%Y-%m-%d').date())
		
		# ページネーション
		paginator = Paginator(notifications, 20)  # 20 notifications per page
		page_number = request.GET.get('page')
		page_obj = paginator.get_page(page_number)
		
		# 統計情報
		total_notifications = Notification.objects.filter(user=request.user).count()
		unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()
		read_notifications = total_notifications - unread_notifications
		
		context = {
			'page_obj': page_obj,
			'total_notifications': total_notifications,
			'unread_notifications': unread_notifications,
			'read_notifications': read_notifications,
			'unread_only': unread_only,
			'date_from': date_from,
			'date_to': date_to,
		}
		return render(request, 'notifications/notification_list.html', context)
		
	except Exception as e:
		messages.error(request, f'通知一覧の取得に失敗しました: {str(e)}')
		return redirect('dashboard')


@login_required  
def notification_mark_read_view(request, notification_id):
	"""通知既読化処理"""
	from .services.notification_service import NotificationService
	
	if request.method == 'POST':
		try:
			notification = Notification.objects.get(id=notification_id, user=request.user)
			notification.mark_as_read()
			messages.success(request, '通知を既読にしました。')
		except Notification.DoesNotExist:
			messages.error(request, '通知が見つかりません。')
		except Exception as e:
			messages.error(request, f'既読化に失敗しました: {str(e)}')
	
	return redirect('notification_list')


@login_required
@user_passes_test(is_staff_user)
def system_settings_view(request):
	"""システム設定画面（SC-009 システム設定画面）"""
	from .services.system_settings_service import SystemSettingsService
	from .models import SystemSettings
	
	try:
		if request.method == 'POST':
			# システム設定更新処理
			maintenance_mode = request.POST.get('maintenance_mode') == 'on'
			email_sender = request.POST.get('email_sender', '').strip()
			
			# SystemSettingsService を使用して更新
			try:
				updated_settings = SystemSettingsService.update_settings(
					maintenance_mode=maintenance_mode,
					email_sender=email_sender
				)
				messages.success(request, 'システム設定を更新しました。')
				return redirect('system_settings')  # POST後リダイレクト
			except Exception as e:
				messages.error(request, f'設定の更新に失敗しました: {str(e)}')
				
		# 現在の設定を取得
		current_settings = SystemSettingsService.get_settings()
		
		context = {
			'settings': current_settings,
			'maintenance_mode': current_settings.maintenance_mode,
			'email_sender': current_settings.email_sender,
		}
		return render(request, 'settings/system_settings.html', context)
		
	except Exception as e:
		messages.error(request, f'システム設定の表示に失敗しました: {str(e)}')
		return redirect('dashboard')

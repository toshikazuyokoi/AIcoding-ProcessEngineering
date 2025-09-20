"""
URL configuration for issue_tracker_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from tracker import views as tracker_views

# API imports
from tracker.api.user_api import create_user, get_user, update_user, list_users, delete_user
from tracker.api.issue_api import (
    create_issue, get_issue, update_issue, list_issues, delete_issue,
    change_issue_status, add_comment, list_comments, assign_issue
)
from tracker.api.notification_api import list_notifications, mark_notification_read, delete_notification
from tracker.api.statistics_api import get_project_statistics
from tracker.api.system_settings_api import system_settings_api

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # User API endpoints
    path('api/users/', create_user, name='api_create_user'),  # POST
    path('api/users/', list_users, name='api_list_users'),    # GET (staff only)
    path('api/users/<int:user_id>/', get_user, name='api_get_user'),        # GET
    path('api/users/<int:user_id>/', update_user, name='api_update_user'),   # PUT
    path('api/users/<int:user_id>/', delete_user, name='api_delete_user'),   # DELETE (staff only)
    
    # Issue API endpoints
    path('api/issues/', create_issue, name='api_create_issue'),              # POST
    path('api/issues/', list_issues, name='api_list_issues'),                # GET
    path('api/issues/<int:issue_id>/', get_issue, name='api_get_issue'),     # GET
    path('api/issues/<int:issue_id>/', update_issue, name='api_update_issue'), # PUT
    path('api/issues/<int:issue_id>/', delete_issue, name='api_delete_issue'), # DELETE
    path('api/issues/<int:issue_id>/status/', change_issue_status, name='api_change_issue_status'), # PATCH
    path('api/issues/<int:issue_id>/comments/', add_comment, name='api_add_comment'),               # POST
    path('api/issues/<int:issue_id>/comments/', list_comments, name='api_list_comments'),           # GET
    path('api/issues/<int:issue_id>/assignee/', assign_issue, name='api_assign_issue'),             # PATCH
    
    # Notification API endpoints
    path('api/notifications/', list_notifications, name='api_list_notifications'),                      # GET
    path('api/notifications/<int:notification_id>/read/', mark_notification_read, name='api_mark_notification_read'), # PATCH
    path('api/notifications/<int:notification_id>/', delete_notification, name='api_delete_notification'),            # DELETE
    
    # Statistics API endpoints
    path('api/projects/<int:project_id>/stats/', get_project_statistics, name='api_get_project_statistics'), # GET
    
    # SystemSettings API endpoints
    path('api/settings/', system_settings_api, name='api_system_settings'), # GET, PUT
    
    # UI routes
    path('login/', tracker_views.login_view, name='login'),
    path('logout/', tracker_views.logout_view, name='logout'),
    path('dashboard/', tracker_views.dashboard_view, name='dashboard'),
    
    # Issue Management UI routes
    path('issues/', tracker_views.issue_list_view, name='issue_list'),
    path('issues/new/', tracker_views.issue_create_view, name='issue_create'),
    path('issues/<int:issue_id>/', tracker_views.issue_detail_view, name='issue_detail'),
    path('issues/<int:issue_id>/edit/', tracker_views.issue_edit_view, name='issue_edit'),
    
    # User Management UI routes
    path('users/', tracker_views.user_list_view, name='user_list'),
    path('users/add/', tracker_views.user_create_view, name='user_create'),
    path('users/<int:user_id>/edit/', tracker_views.user_edit_view, name='user_edit'),
    path('users/<int:user_id>/delete/', tracker_views.user_delete_view, name='user_delete'),
    path('users/<int:user_id>/password-reset/', tracker_views.user_password_reset_view, name='user_password_reset'),
    path('users/<int:user_id>/toggle-active/', tracker_views.user_toggle_active_view, name='user_toggle_active'),
    
    # Notification Management UI routes
    path('notifications/', tracker_views.notification_list_view, name='notification_list'),
    path('notifications/<int:notification_id>/mark-read/', tracker_views.notification_mark_read_view, name='notification_mark_read'),
    
    # System Settings UI routes
    path('settings/', tracker_views.system_settings_view, name='system_settings'),
]

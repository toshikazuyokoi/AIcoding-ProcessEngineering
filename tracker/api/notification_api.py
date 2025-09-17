"""
Notification API Controller

Endpoints:
- GET    /api/notifications                → list_notifications
- PATCH  /api/notifications/{id}/read      → mark_notification_read
- DELETE /api/notifications/{id}           → delete_notification

Notes:
- Authentication required for all endpoints
- Users can access/modify only their own notifications
- Staff users can access/modify any user's notifications
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_datetime

from tracker.services.notification_service import NotificationService


def _bool_from_query(value: str) -> bool:
    if value is None:
        return False
    return value.lower() in ("1", "true", "yes", "on")


def _notification_to_dict(notification):
    return {
        "id": notification.id,
        "user_id": notification.user_id,
        "message": notification.message,
        "is_read": notification.is_read,
        "created_at": notification.created_at.isoformat() if getattr(notification, "created_at", None) else None,
        "updated_at": getattr(notification, "updated_at", None).isoformat() if getattr(notification, "updated_at", None) else None,
    }


@login_required
@require_http_methods(["GET"])
def list_notifications(request):
    """
    List notifications for the authenticated user.
    Optional query: unread_only=true|false
    """
    try:
        unread_only = _bool_from_query(request.GET.get("unread_only"))
        notifications = NotificationService.get_notifications(request.user.id, unread_only=unread_only)
        data = [_notification_to_dict(n) for n in notifications]
        return JsonResponse(data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
@require_http_methods(["PATCH"])
def mark_notification_read(request, notification_id: int):
    """
    Mark a notification as read. Only owner or staff can mark.
    """
    try:
        notification = NotificationService.get_notification_by_id(notification_id)
        if not notification:
            return JsonResponse({"error": "Notification not found"}, status=404)

        # Permission: owner or staff
        if not (request.user.is_staff or notification.user_id == request.user.id):
            return JsonResponse({"error": "Permission denied"}, status=403)

        updated = NotificationService.mark_as_read(notification_id)
        return JsonResponse({
            "id": updated.id,
            "is_read": updated.is_read,
            "updated_at": getattr(updated, "updated_at", None).isoformat() if getattr(updated, "updated_at", None) else None,
        }, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
@require_http_methods(["DELETE"])
def delete_notification(request, notification_id: int):
    """
    Delete a notification. Only owner or staff can delete.
    """
    try:
        notification = NotificationService.get_notification_by_id(notification_id)
        if not notification:
            return JsonResponse({"error": "Notification not found"}, status=404)

        # Permission: owner or staff
        if request.user.is_staff:
            NotificationService.delete_notification(notification_id)
        elif notification.user_id == request.user.id:
            NotificationService.delete_notification(notification_id, user_id=request.user.id)
        else:
            return JsonResponse({"error": "Permission denied"}, status=403)

        return JsonResponse({"result": "success"}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

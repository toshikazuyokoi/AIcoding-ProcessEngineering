"""
Issue API Controller - チケット関連APIエンドポイント

Endpoints (per interfaces/design):
- POST   /api/issues                     → create_issue
- GET    /api/issues/{id}                → get_issue
- PUT    /api/issues/{id}                → update_issue
- GET    /api/issues                     → list_issues
- DELETE /api/issues/{id}                → delete_issue
- PATCH  /api/issues/{id}/status         → change_issue_status
- POST   /api/issues/{id}/comments       → add_comment
- GET    /api/issues/{id}/comments       → list_comments
- PATCH  /api/issues/{id}/assignee       → assign_issue (割当)

Notes:
- Authentication required for all endpoints
- Authorization: enforced via IssueService using acting user id
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
import json

from tracker.services.issue_service import IssueService


def _issue_to_dict(issue):
    return {
        "id": issue.id,
        "project_id": issue.project_id,
        "title": issue.title,
        "description": issue.description,
        "priority": getattr(issue, "priority", None),
        "assigned_to": issue.assigned_to_id if getattr(issue, "assigned_to_id", None) else None,
        "status": getattr(issue, "status", None),
        "created_by": getattr(issue, "created_by_id", None),
        "created_at": getattr(issue, "created_at", None).isoformat() if getattr(issue, "created_at", None) else None,
        "updated_at": getattr(issue, "updated_at", None).isoformat() if getattr(issue, "updated_at", None) else None,
    }


def _comment_to_dict(comment):
    return {
        "id": comment.id,
        "issue_id": comment.issue_id,
        "user_id": comment.user_id,
        "content": comment.content,
        "created_at": getattr(comment, "created_at", None).isoformat() if getattr(comment, "created_at", None) else None,
        "updated_at": getattr(comment, "updated_at", None).isoformat() if getattr(comment, "updated_at", None) else None,
    }


def _parse_json(request):
    try:
        return json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return None


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def create_issue(request):
    """
    Create Issue
    POST /api/issues
    Required: project_id, title, description
    Optional: priority, assigned_to_id
    """
    data = _parse_json(request)
    if data is None:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)

    required = ["project_id", "title", "description"]
    for f in required:
        if f not in data:
            return JsonResponse({"error": f"Missing required field: {f}"}, status=400)

    try:
        issue = IssueService.create_issue(
            project_id=data["project_id"],
            created_by_id=request.user.id,
            title=data["title"],
            description=data["description"],
            priority=data.get("priority"),
            assigned_to_id=data.get("assigned_to_id"),
        )
        return JsonResponse(_issue_to_dict(issue), status=201)
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def get_issue(request, issue_id: int):
    issue = IssueService.get_issue_by_id(issue_id)
    if not issue:
        return JsonResponse({"error": "Issue not found"}, status=404)
    return JsonResponse(_issue_to_dict(issue), status=200)


@csrf_exempt
@login_required
@require_http_methods(["PUT"])
def update_issue(request, issue_id: int):
    data = _parse_json(request)
    if data is None:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)

    allowed_fields = {"title", "description", "priority", "assigned_to_id"}
    update_payload = {k: v for k, v in data.items() if k in allowed_fields}

    try:
        # Ensure exists first for 404 semantics
        if not IssueService.get_issue_by_id(issue_id):
            return JsonResponse({"error": "Issue not found"}, status=404)

        updated = IssueService.update_issue(issue_id, request.user.id, **update_payload)
        return JsonResponse(_issue_to_dict(updated), status=200)
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def list_issues(request):
    try:
        project_id = request.GET.get("project_id")
        assigned_to_id = request.GET.get("assigned_to_id")
        kwargs = {}
        if project_id is not None:
            try:
                kwargs["project_id"] = int(project_id)
            except ValueError:
                return JsonResponse({"error": "project_id must be integer"}, status=400)
        if assigned_to_id is not None:
            try:
                kwargs["assigned_to_id"] = int(assigned_to_id)
            except ValueError:
                return JsonResponse({"error": "assigned_to_id must be integer"}, status=400)

        issues = IssueService.list_issues(**kwargs)
        return JsonResponse([_issue_to_dict(i) for i in issues], safe=False, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
@login_required
@require_http_methods(["DELETE"])
def delete_issue(request, issue_id: int):
    try:
        if not IssueService.get_issue_by_id(issue_id):
            return JsonResponse({"error": "Issue not found"}, status=404)

        IssueService.delete_issue(issue_id, request.user.id)
        return JsonResponse({"result": "success"}, status=200)
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
@login_required
@require_http_methods(["PATCH"])
def change_issue_status(request, issue_id: int):
    data = _parse_json(request)
    if data is None:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    status_value = data.get("status")
    if not status_value:
        return JsonResponse({"error": "Missing required field: status"}, status=400)

    try:
        if not IssueService.get_issue_by_id(issue_id):
            return JsonResponse({"error": "Issue not found"}, status=404)

        updated = IssueService.change_status(issue_id, status_value, request.user.id)
        return JsonResponse({"id": updated.id, "status": updated.status}, status=200)
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def add_comment(request, issue_id: int):
    data = _parse_json(request)
    if data is None:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    content = data.get("content")
    if not content:
        return JsonResponse({"error": "Missing required field: content"}, status=400)

    try:
        if not IssueService.get_issue_by_id(issue_id):
            return JsonResponse({"error": "Issue not found"}, status=404)

        comment = IssueService.add_comment(issue_id, request.user.id, content)
        return JsonResponse(_comment_to_dict(comment), status=201)
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def list_comments(request, issue_id: int):
    if not IssueService.get_issue_by_id(issue_id):
        return JsonResponse({"error": "Issue not found"}, status=404)
    comments = IssueService.get_issue_comments(issue_id)
    return JsonResponse([_comment_to_dict(c) for c in comments], safe=False, status=200)


@csrf_exempt
@login_required
@require_http_methods(["PATCH"])
def assign_issue(request, issue_id: int):
    data = _parse_json(request)
    if data is None:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    # assigned_to_id may be None to unassign
    assigned_to_id = data.get("assigned_to_id", None)
    try:
        if not IssueService.get_issue_by_id(issue_id):
            return JsonResponse({"error": "Issue not found"}, status=404)

        updated = IssueService.assign_issue(issue_id, assigned_to_id, request.user.id)
        return JsonResponse({"id": updated.id, "assigned_to": updated.assigned_to_id}, status=200)
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# Optional: URL patterns provider (kept minimal, not wired by default)
def get_issue_api_urls():
    from django.urls import path
    return [
        path("issues", create_issue, name="create_issue"),
        path("issues", list_issues, name="list_issues"),
        path("issues/<int:issue_id>", get_issue, name="get_issue"),
        path("issues/<int:issue_id>", update_issue, name="update_issue"),
        path("issues/<int:issue_id>", delete_issue, name="delete_issue"),
        path("issues/<int:issue_id>/status", change_issue_status, name="change_issue_status"),
        path("issues/<int:issue_id>/comments", add_comment, name="add_comment"),
        path("issues/<int:issue_id>/comments", list_comments, name="list_comments"),
        path("issues/<int:issue_id>/assignee", assign_issue, name="assign_issue"),
    ]

"""
Statistics API Controller

Endpoints:
- GET    /api/projects/{id}/stats       → get_project_statistics

Notes:
- Authentication required for all endpoints
- PM (Project Manager) permissions required for project statistics
- Uses StatisticsService for business logic
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

from tracker.services.statistics_service import StatisticsService
from tracker.models import Project, ProjectMember


def _is_project_member_or_staff(user, project_id):
    """
    Check if user is project member/PM or staff user
    
    Args:
        user: User instance
        project_id (int): Project ID
        
    Returns:
        bool: True if user has access permission
    """
    if user.is_staff:
        return True
    
    try:
        project = Project.objects.get(id=project_id)
        # Check if user is project creator
        if project.created_by == user:
            return True
        
        # Check if user is project member
        return ProjectMember.objects.filter(
            project_id=project_id,
            user=user
        ).exists()
    except Project.DoesNotExist:
        return False


@login_required
@require_http_methods(["GET"])
def get_project_statistics(request, project_id: int):
    """
    Get project statistics.
    Requires PM permission or project membership.
    """
    try:
        # Permission check: PM, project member, or staff
        if not _is_project_member_or_staff(request.user, project_id):
            return JsonResponse({"error": "Permission denied"}, status=403)
        
        # Get statistics using service layer
        statistics = StatisticsService.get_project_statistics_dict(project_id)
        
        if statistics is None:
            return JsonResponse({"error": "Project not found"}, status=404)
        
        return JsonResponse(statistics, status=200)
        
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def get_statistics_api_urls():
    """
    Helper function to get URL patterns for Statistics API
    
    Returns:
        list: URL pattern configurations
    """
    return [
        {
            'name': 'get_project_statistics',
            'path': 'projects/<int:project_id>/stats/',
            'view': get_project_statistics,
            'methods': ['GET']
        }
    ]
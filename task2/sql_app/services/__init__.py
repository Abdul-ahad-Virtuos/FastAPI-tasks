"""
__init__ for services module.
"""
from sql_app.services.user_service import user_service
from sql_app.services.project_service import project_service
from sql_app.services.task_service import task_service
from sql_app.services.tag_service import tag_service, task_assignment_service
from sql_app.services.comment_service import task_comment_service
from sql_app.services.analytics_service import analytics_service

__all__ = [
    "user_service",
    "project_service",
    "task_service",
    "tag_service",
    "task_assignment_service",
    "task_comment_service",
    "analytics_service",
]

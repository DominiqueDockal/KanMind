"""
Django admin configuration for Board, Task, and TaskComment models.

Each model is registered in the admin interface with custom list display fields.
"""

from django.contrib import admin
from .models import Board, Task, TaskComment


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """
    Admin interface options for the Board model.

    Displays:
        - id: Board ID
        - title: Board title
        - owner: Owner of the board
    """
    list_display = ('id', 'title', 'owner')
    

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Admin interface options for the Task model.

    Displays:
        - id: Task ID
        - title: Task title
        - board: Associated board
        - status: Current workflow status
        - priority: Task priority level
    """
    list_display = ('id', 'title', 'board', 'status', 'priority')
    

@admin.register(TaskComment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin interface options for the TaskComment model.

    Displays:
        - id: Comment ID
        - task: Related task
        - author: Comment author
        - created_at: Timestamp of comment creation
    """
    list_display = ('id', 'task', 'author', 'created_at')


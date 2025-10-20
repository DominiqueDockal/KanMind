from django.urls import path
from kanban_app.views import (
    BoardListCreateView, BoardDetailView,
    TaskListCreateView, TaskDetailView,
    TaskAssignedToMeListView, TaskReviewingListView,
    TaskCommentListCreateView, TaskCommentDestroyView
)

urlpatterns = [
    path('boards/', BoardListCreateView.as_view(), name='board-list-create'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),

    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),

    path('tasks/assigned-to-me/', TaskAssignedToMeListView.as_view(), name='task-assigned-to-me'),
    path('tasks/reviewing/', TaskReviewingListView.as_view(), name='task-reviewing'),

    path('tasks/<int:task_id>/comments/', TaskCommentListCreateView.as_view(), name='task-comments'),
    path('tasks/<int:task_id>/comments/<int:comment_id>/', TaskCommentDestroyView.as_view(), name='task-comment-delete'),
]



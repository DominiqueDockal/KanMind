from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from kanban_app.models import Board, Task, TaskComment
from kanban_app.api.serializers import BoardSerializer, TaskSerializer, TaskCommentSerializer
from rest_framework.permissions import IsAuthenticated
from kanban_app.api.permissions import (
    IsBoardMemberOrOwner, IsTaskBoardMemberOrOwner, IsCommentAuthor, IsBoardOwner, IsTaskCreatorOrBoardOwner
)

class BoardListCreateView(generics.ListCreateAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsBoardOwner()]
        return [IsAuthenticated(), IsBoardMemberOrOwner()]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        board_id = self.request.query_params.get("board")
        if board_id:
            qs = qs.filter(board_id=board_id)
        return qs

    def perform_create(self, serializer):
        board = serializer.validated_data['board']
        if self.request.user != board.owner and self.request.user not in board.members.all():
            raise PermissionDenied("Du bist kein Mitglied des Boards.")
        serializer.save()

class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsTaskCreatorOrBoardOwner()]
        return [IsAuthenticated(), IsTaskBoardMemberOrOwner()]

    def get_queryset(self):
        qs = super().get_queryset()
        board_id = self.request.query_params.get("board")
        if board_id:
            qs = qs.filter(board_id=board_id)
        return qs

class TaskAssignedToMeListView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user)

class TaskReviewingListView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)

class TaskCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated, IsTaskBoardMemberOrOwner]

    def get_queryset(self):
        return TaskComment.objects.filter(task_id=self.kwargs["task_id"])

    def perform_create(self, serializer):
        task = Task.objects.get(id=self.kwargs["task_id"])
        board = task.board
        if self.request.user != board.owner and self.request.user not in board.members.all():
            raise PermissionDenied("Du bist kein Mitglied des Boards.")
        serializer.save(
            task=task,
            author=self.request.user
        )

class TaskCommentDestroyView(generics.DestroyAPIView):
    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthor, IsTaskBoardMemberOrOwner]

    def get_queryset(self):
        return TaskComment.objects.filter(task_id=self.kwargs["task_id"], id=self.kwargs["comment_id"])


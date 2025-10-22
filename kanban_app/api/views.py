from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import DestroyAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound

from kanban_app.models import Board, Task, TaskComment
from kanban_app.api.serializers import (
    BoardCreateInputSerializer,
    BoardDetailGetSerializer,
    BoardListSerializer,
    BoardUpdateInputSerializer,
    BoardUpdateResponseSerializer,
    TaskSerializer,
    TaskCommentSerializer,
    TaskUpdateSerializer,
)
from kanban_app.api.permissions import (
    IsBoardMemberForTaskCreate,
    IsBoardOwner,
    IsBoardMemberOrOwner,
    IsTaskBoardMemberOrOwner,
    IsCommentAuthor,
    IsTaskCreatorOrBoardOwner,
)

class BoardListCreateView(generics.ListCreateAPIView):
    queryset = Board.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BoardCreateInputSerializer 
        return BoardListSerializer             
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save()
        output = BoardListSerializer(board)
        return Response(output.data, status=status.HTTP_201_CREATED)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all()
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsBoardOwner()]
        return [IsAuthenticated(), IsBoardMemberOrOwner()]

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return BoardUpdateInputSerializer
        return BoardDetailGetSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object() 
        serializer = BoardUpdateInputSerializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        response_serializer = BoardUpdateResponseSerializer(instance)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated, IsBoardMemberForTaskCreate]
    serializer_class = TaskSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        board_id = self.request.query_params.get("board")
        if board_id:
            qs = qs.filter(board_id=board_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    lookup_field = 'pk'
    
    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsTaskCreatorOrBoardOwner()]
        return [IsAuthenticated(), IsTaskBoardMemberOrOwner()]

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return TaskUpdateSerializer
        return TaskSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        board_id = self.request.query_params.get("board")
        if board_id:
            qs = qs.filter(board_id=board_id)
        return qs
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


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
        task_id = self.kwargs["task_id"]
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise NotFound("Task not found.")
        self.check_object_permissions(self.request, task)
        return TaskComment.objects.filter(task_id=task_id).order_by("created_at")

    def perform_create(self, serializer):
        task_id = self.kwargs["task_id"]
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise NotFound("Task not found.")
        self.check_object_permissions(self.request, task)
        serializer.save(author=self.request.user, task=task)


class TaskCommentDestroyView(DestroyAPIView):
    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthor]

    def get_queryset(self):
        return TaskComment.objects.filter(task_id=self.kwargs["task_id"])

    def get_object(self):
        task_id = self.kwargs.get("task_id")
        comment_id = self.kwargs.get("comment_id")
        
        try:
            comment = TaskComment.objects.get(id=comment_id, task__id=task_id)
            self.check_object_permissions(self.request, comment)
            return comment
        except TaskComment.DoesNotExist:
            raise NotFound(detail="Comment not found or does not belong to this task.")


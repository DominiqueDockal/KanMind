from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import DestroyAPIView
from rest_framework.response import Response

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
    """
    API endpoint for listing and creating boards.

    - GET: Returns all boards where the user is owner or member.
    - POST: Creates a new board and assigns the requesting user as owner.

    Uses BoardListSerializer for GET output,
    BoardCreateInputSerializer for POST input.
    Access restricted to authenticated users.
    """

    queryset = Board.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Get all boards where the current user is owner or member.

        Returns:
            QuerySet of Board instances for the user.
        """
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()
    
    def get_serializer_class(self):
        """
        Select serializer based on request method.

        Returns:
            BoardCreateInputSerializer for POST, BoardListSerializer for GET.
        """
        if self.request.method == 'POST':
            return BoardCreateInputSerializer 
        return BoardListSerializer                  

    def create(self, request, *args, **kwargs):
        """
        Create a new board instance with POST data.

        Returns:
            HTTP 201 response with serialized board data.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save()
        output = BoardListSerializer(board)
        return Response(output.data, status=status.HTTP_201_CREATED)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting boards.

    - GET: Returns board details, including members and tasks.
    - PATCH: Updates board title/members.
    - DELETE: Deletes the board (owner only).

    Uses BoardDetailGetSerializer for output, BoardUpdateInputSerializer for input.
    Permissions depend on the request method.
    """

    queryset = Board.objects.all()
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Return permissions based on request method.

        DELETE requires IsBoardOwner, others require IsBoardMemberOrOwner.
        """
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsBoardOwner()]
        return [IsAuthenticated(), IsBoardMemberOrOwner()]

    def get_serializer_class(self):
        """
        Select serializer based on request method.

        PATCH uses BoardUpdateInputSerializer, others use BoardDetailGetSerializer.
        """
        if self.request.method == 'PATCH':
            return BoardUpdateInputSerializer
        return BoardDetailGetSerializer

    def update(self, request, *args, **kwargs):
        """
        Update board title and/or members.

        Returns:
            HTTP 200 with updated board data via BoardUpdateResponseSerializer.
        """
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
    """
    API endpoint for listing and creating tasks.

    - GET: List all tasks for a board (if board_id is provided).
    - POST: Create new task, only if user is board member or owner.

    Uses TaskSerializer for all operations.
    Access requires authentication and board membership.
    """
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated, IsBoardMemberForTaskCreate]
    serializer_class = TaskSerializer

    def get_queryset(self):
        """
        Get all tasks, optionally filtered by board.

        Returns:
            QuerySet of Task instances.
        """
        qs = super().get_queryset()
        board_id = self.request.query_params.get("board")
        if board_id:
            qs = qs.filter(board_id=board_id)
        return qs

    def perform_create(self, serializer):
        """
        Save new task and set the creator field automatically.

        Args:
            serializer: TaskSerializer instance.
        """
        serializer.save(creator=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting a specific task.

    - GET: Returns task details.
    - PATCH: Updates allowed task fields.
    - DELETE: Removes task (creator or board owner only).

    Serializer and permissions vary by method.
    """
    queryset = Task.objects.all()
    lookup_field = 'pk'
    
    def get_permissions(self):
        """
        Permissions set based on method.

        DELETE uses IsTaskCreatorOrBoardOwner, others use IsTaskBoardMemberOrOwner.
        """
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsTaskCreatorOrBoardOwner()]
        return [IsAuthenticated(), IsTaskBoardMemberOrOwner()]

    def get_serializer_class(self):
        """
        Return TaskUpdateSerializer for PATCH, else TaskSerializer.
        """
        if self.request.method == 'PATCH':
            return TaskUpdateSerializer
        return TaskSerializer

    def get_queryset(self):
        """
        Get tasks, optionally filtered by board.
        """
        qs = super().get_queryset()
        board_id = self.request.query_params.get("board")
        if board_id:
            qs = qs.filter(board_id=board_id)
        return qs
    
    def update(self, request, *args, **kwargs):
        """
        Update task data. Checks object permissions before applying update.
        """
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class TaskAssignedToMeListView(generics.ListAPIView):
    """
    API endpoint to list all tasks assigned to the current user.

    Uses TaskSerializer for output.
    Access is restricted to authenticated users.
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Get all tasks assigned to the current user.

        Returns:
            QuerySet of Task instances.
        """
        return Task.objects.filter(assignee=self.request.user)


class TaskReviewingListView(generics.ListAPIView):
    """
    API endpoint to list all tasks for which the current user is reviewer.

    Uses TaskSerializer for output.
    Access is restricted to authenticated users.
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Get all tasks where current user is reviewer.

        Returns:
            QuerySet of Task instances.
        """
        return Task.objects.filter(reviewer=self.request.user)


class TaskCommentListCreateView(generics.ListCreateAPIView):
    """
    API endpoint to list and create comments for a specific task.

    - GET: Lists all comments for a task (sorted by creation).
    - POST: Creates a new comment for the task, author is request.user.

    Uses TaskCommentSerializer for all operations.
    Access controlled by IsTaskBoardMemberOrOwner.
    """
    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated, IsTaskBoardMemberOrOwner]

    def get_queryset(self):
        """
        Get all comments for the specified task.

        Returns:
            QuerySet of TaskComment instances for the task.
        Raises:
            NotFound: If the task does not exist.
        """
        task_id = self.kwargs["task_id"]
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise NotFound("Task not found.")
        self.check_object_permissions(self.request, task)
        return TaskComment.objects.filter(task_id=task_id).order_by("created_at")

    def perform_create(self, serializer):
        """
        Create and save a comment for a specific task.

        Author is set to request.user, task fetched by task_id.
        Raises:
            NotFound: If the task does not exist.
        """
        task_id = self.kwargs["task_id"]
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise NotFound("Task not found.")
        self.check_object_permissions(self.request, task)
        serializer.save(author=self.request.user, task=task)


class TaskCommentDestroyView(DestroyAPIView):
    """
    API endpoint to delete a specific comment for a task.

    Only the comment author may delete their own comment.
    Uses TaskCommentSerializer for output.
    """
    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthor]

    def get_queryset(self):
        """
        Get all comments for the specified task.

        Returns:
            QuerySet of TaskComment instances.
        """
        return TaskComment.objects.filter(task_id=self.kwargs["task_id"])

    def get_object(self):
        """
        Fetch the comment object by task_id and comment_id.

        Returns:
            Comment instance if found and permission granted.
        Raises:
            NotFound: If the comment doesn't exist or doesn't belong to the task.
        """
        task_id = self.kwargs.get("task_id")
        comment_id = self.kwargs.get("comment_id")
        
        try:
            comment = TaskComment.objects.get(id=comment_id, task__id=task_id)
            self.check_object_permissions(self.request, comment)
            return comment
        except TaskComment.DoesNotExist:
            raise NotFound(detail="Comment not found or does not belong to this task.")



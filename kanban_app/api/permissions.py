from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotFound
from kanban_app.models import Task, Board

class IsBoardMemberForTaskCreate(BasePermission):
    """
    Permission: IsBoardMemberForTaskCreate

    Allows task creation only if the requesting user is the owner or a member of the specified board.
    Raises 404 if the board does not exist, 403 if the user is not a member.

    Used for:
        POST /api/tasks/

    Methods:
        has_permission(request, view): Checks if the user is a board member or owner.
    """
    def has_permission(self, request, view):
        """
        Checks if user is allowed to create a task on the specified board.

        Args:
            request: DRF request object with POST data (must include 'board' field).
            view: DRF view instance.

        Returns:
            bool: True if user is a member or owner, else False.
            
        Raises:
            NotFound: If the specified board does not exist (404).
        """
        board_id = request.data.get('board')
        if not board_id:
            return False
        try:
            board = Board.objects.get(pk=board_id)
        except Board.DoesNotExist:
            raise NotFound(detail="Board not found.")  #hier war 403
        return request.user == board.owner or request.user in board.members.all()

    
class IsBoardOwner(BasePermission):
    """
    Permission: IsBoardOwner

    Allows access only to the board owner.

    Used for:
        DELETE /api/boards/{board_id}/

    Methods:
        has_object_permission(request, view, obj): Checks user == owner.
    """
    def has_object_permission(self, request, view, obj):
        """
        Checks if requesting user is owner of the board.

        Args:
            obj: Board instance.

        Returns:
            bool: True if user is owner, else False.
        """
        return request.user == obj.owner


class IsBoardMemberOrOwner(BasePermission):
    """
    Permission: IsBoardMemberOrOwner

    Allows access to owners and board members.

    Used for:
        GET/PATCH /api/boards/{board_id}/
        GET /api/tasks/{task_id}/...
        Accessing boards in general.

    Methods:
        has_object_permission(request, view, obj): Checks user == owner or board member.
    """
    def has_object_permission(self, request, view, obj):
        """
        Checks if user is board owner or member.

        Args:
            obj: Board instance.

        Returns:
            bool: True if user is owner or member.
        """
        return request.user == obj.owner or request.user in obj.members.all()


class IsTaskBoardMemberOrOwner(BasePermission):
    """
    Permission: IsTaskBoardMemberOrOwner

    Allows access to tasks only if user is a member or owner of the associated board.
    Raises 404 if the task does not exist.

    Used for:
        PATCH /api/tasks/{task_id}/
        GET /api/tasks/{task_id}/comments/
        General access to tasks or task comments.

    Methods:
        has_permission(request, view): Checks if user is allowed for non-object requests.
        has_object_permission(request, view, obj): For object-level checks.
    """
    def has_permission(self, request, view):
        """
        Object-level permission alternative for non-object requests.
        Returns True if no pk provided (list endpoint), otherwise checks board membership/ownership.

        Args:
            request: DRF request.
            view: DRF view.

        Returns:
            bool: True if allowed.
            
        Raises:
            NotFound: If the specified task does not exist (404).
        """
        task_id = view.kwargs.get('pk')
        if not task_id:
            return True
        try:
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            raise NotFound(detail="Task not found.")
        board = task.board
        return request.user == board.owner or request.user in board.members.all()

    def has_object_permission(self, request, view, obj):
        """
        Checks if user is owner or member of the board for the task object.

        Args:
            obj: Task instance.

        Returns:
            bool: True if user is allowed.
        """
        board = obj.board
        return request.user == board.owner or request.user in board.members.all()


class IsCommentAuthor(BasePermission):
    """
    Permission: IsCommentAuthor

    Allows only the comment author to modify or delete their own comment.

    Used for:
        DELETE /api/tasks/{task_id}/comments/{comment_id}/

    Methods:
        has_object_permission(request, view, obj): Checks user == author.
    """
    def has_object_permission(self, request, view, obj):
        """
        Checks if requesting user is the comment author.

        Args:
            obj: TaskComment instance.

        Returns:
            bool: True if user is author, else False.
        """
        return obj.author == request.user


class IsTaskCreatorOrBoardOwner(BasePermission):
    """
    Permission: IsTaskCreatorOrBoardOwner

    Allows access if user is either the creator of the task or the owner of the associated board.

    Used for:
        DELETE /api/tasks/{task_id}/

    Methods:
        has_object_permission(request, view, obj): Checks user == creator or board owner.
    """
    def has_object_permission(self, request, view, obj):
        """
        Checks if user is task creator or board owner.

        Args:
            obj: Task instance.

        Returns:
            bool: True if user is creator or board owner.
        """
        board = obj.board
        return (
            hasattr(obj, "creator") and obj.creator == request.user
        ) or (board.owner == request.user)

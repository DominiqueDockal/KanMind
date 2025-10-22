from rest_framework.permissions import BasePermission
from kanban_app.models import Task, Board


class IsBoardMemberForTaskCreate(BasePermission):
    def has_permission(self, request, view):
        board_id = request.data.get('board')
        if not board_id:
            return False
        try:
            board = Board.objects.get(pk=board_id)
        except Board.DoesNotExist:
            return False
        return request.user == board.owner or request.user in board.members.all()
    

class IsBoardOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner


class IsBoardMemberOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner or request.user in obj.members.all()


class IsTaskBoardMemberOrOwner(BasePermission):
    def has_permission(self, request, view):
        task_id = view.kwargs.get("pk")  
        if not task_id:
            return True
        try:
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            return False
        board = task.board
        return request.user == board.owner or request.user in board.members.all()

    def has_object_permission(self, request, view, obj):
        board = obj.board
        return request.user == board.owner or request.user in board.members.all()


class IsCommentAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsTaskCreatorOrBoardOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        board = obj.board
        return (
            hasattr(obj, "creator") and obj.creator == request.user
        ) or (board.owner == request.user)

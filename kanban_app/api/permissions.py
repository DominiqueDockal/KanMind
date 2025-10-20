from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsBoardMemberOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner or request.user in obj.members.all()

class IsTaskBoardMemberOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        board = obj.board
        return request.user == board.owner or request.user in board.members.all()

class IsTaskAssigneeOrReviewer(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.assignee == request.user or obj.reviewer == request.user

class IsCommentAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user

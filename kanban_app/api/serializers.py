from rest_framework import serializers
from django.contrib.auth import get_user_model
from kanban_app.models import Task, Board, TaskComment

User = get_user_model()

class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "fullname"]

class TaskSerializer(serializers.ModelSerializer):
    assignee = UserShortSerializer(read_only=True)
    reviewer = UserShortSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source="assignee", write_only=True, required=False)
    reviewer_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source="reviewer", write_only=True, required=False)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id", "board", "title", "description",
            "status", "priority", "assignee", "reviewer",
            "due_date", "comments_count", "assignee_id", "reviewer_id"
        ]
        read_only_fields = ["id", "comments_count", "assignee", "reviewer"]

    def validate_status(self, value):
        if value not in dict(Task.STATUS_CHOICES):
            raise serializers.ValidationError("Invalid status.")
        return value

    def validate_priority(self, value):
        if value not in dict(Task.PRIORITY_CHOICES):
            raise serializers.ValidationError("Invalid priority.")
        return value

    def validate(self, attrs):
        board = attrs.get("board") or self.instance.board if self.instance else None
        assignee = attrs.get("assignee")
        reviewer = attrs.get("reviewer")
        member_ids = board.members.values_list("id", flat=True) if board else []
        if assignee and assignee.id not in member_ids:
            raise serializers.ValidationError("Assignee is not a board member.")
        if reviewer and reviewer.id not in member_ids:
            raise serializers.ValidationError("Reviewer is not a board member.")
        return attrs


class BoardMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "fullname"]

class SimpleTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "id", "title", "description", "status", "priority",
            "assignee", "reviewer", "due_date", "comments_count"
        ]

class BoardSerializer(serializers.ModelSerializer):
    members = BoardMemberSerializer(many=True, read_only=True)
    owner_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source="owner", write_only=True, required=False)
    member_ids = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, source="members", write_only=True, required=False)
    tasks = SimpleTaskSerializer(many=True, read_only=True)
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            "id", "title", "members", "owner_id", "member_ids",
            "tasks", "member_count", "ticket_count",
            "tasks_to_do_count", "tasks_high_prio_count"
        ]
        read_only_fields = ["id", "members", "tasks", "member_count",
                            "ticket_count", "tasks_to_do_count", "tasks_high_prio_count"]

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority="high").count()

class TaskCommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.get_full_name()", read_only=True)

    class Meta:
        model = TaskComment
        fields = ["id", "created_at", "author", "content"]
        read_only_fields = ["id", "created_at", "author"]
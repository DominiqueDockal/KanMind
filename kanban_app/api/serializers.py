from django.contrib.auth import get_user_model
from rest_framework import serializers
from kanban_app.models import Task, Board, TaskComment

User = get_user_model()

class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "fullname"]


class BoardListSerializer(serializers.ModelSerializer):
    member_count = serializers.IntegerField(source="members.count", read_only=True)
    ticket_count = serializers.IntegerField(source="tasks.count", read_only=True)
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)
    
    class Meta:
        model = Board
        fields = [
            "id", "title", "member_count",
            "ticket_count", "tasks_to_do_count",
            "tasks_high_prio_count", "owner_id"
        ]
    
    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority="high").count()

    
class BoardUpdateInputSerializer(serializers.ModelSerializer):
    members = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True,
        allow_empty=True
    )
    
    class Meta:
        model = Board
        fields = ['title', 'members']
    
    def validate_members(self, value):
        if value is not None:
            from auth_app.models import User
            existing_ids = set(User.objects.filter(id__in=value).values_list('id', flat=True))
            invalid_ids = set(value) - existing_ids
            if invalid_ids:
                raise serializers.ValidationError(
                    f"User IDs {invalid_ids} do not exist."
                )
        return value
    
    def update(self, instance, validated_data):
        members = validated_data.pop('members', None)
        if 'title' in validated_data:
            instance.title = validated_data['title']
        if members is not None:
            instance.members.set(members)
        instance.save()
        return instance

    
class BoardUpdateResponseSerializer(serializers.ModelSerializer):
    owner_data = serializers.SerializerMethodField()
    members_data = serializers.SerializerMethodField()
    
    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_data', 'members_data']
    
    def get_owner_data(self, obj):
        return UserShortSerializer(obj.owner).data
    
    def get_members_data(self, obj):
        return UserShortSerializer(obj.members.all(), many=True).data


class SimpleTaskSerializer(serializers.ModelSerializer):
    assignee = UserShortSerializer(read_only=True) 
    reviewer = UserShortSerializer(read_only=True) 
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id", "title", "description", "status", "priority",
            "assignee", "reviewer", "due_date", "comments_count"
        ]
    
    def get_comments_count(self, obj):
        return obj.comments.count()


class BoardDetailGetSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)
    members = UserShortSerializer(many=True, read_only=True)
    tasks = SimpleTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']


class BoardCreateInputSerializer(serializers.ModelSerializer):
    members = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True,
        allow_empty=True
    )
    
    class Meta:
        model = Board
        fields = ['title', 'members']
    
    def validate_members(self, value):
        from auth_app.models import User
        existing = set(User.objects.filter(id__in=value).values_list('id', flat=True))
        invalid = set(value) - existing
        if invalid:
            raise serializers.ValidationError(f"User IDs {invalid} do not exist.")
        return value
    
    def create(self, validated_data):
        members = validated_data.pop('members', [])
        board = Board.objects.create(
            owner=self.context['request'].user,
            **validated_data
        )
        board.members.set(members)
        return board


class TaskSerializer(serializers.ModelSerializer):
    assignee = UserShortSerializer(read_only=True)
    reviewer = UserShortSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assignee',
        write_only=True,
        required=False,
        allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='reviewer',
        write_only=True,
        required=False,
        allow_null=True
    )
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id", "board", "title", "description",
            "status", "priority", "assignee", "reviewer",
            "due_date", "comments_count", "assignee_id", "reviewer_id"
        ]
        read_only_fields = [
            "id", "comments_count", "assignee", "reviewer"
        ]
    
    def validate_board(self, value):
        if self.instance and self.instance.board_id != value.id:
            raise serializers.ValidationError("Board cannot be changed.")
        return value

    def get_comments_count(self, obj):
        return obj.comments.count()

    def validate_status(self, value):
        if value not in dict(Task.STATUS_CHOICES):
            raise serializers.ValidationError("Invalid status.")
        return value

    def validate_priority(self, value):
        if value not in dict(Task.PRIORITY_CHOICES):
            raise serializers.ValidationError("Invalid priority.")
        return value
    
    def validate(self, attrs):
        board = attrs.get('board') or self.instance.board
        assignee = attrs.get('assignee')
        reviewer = attrs.get('reviewer')
        
        if assignee:
            if assignee not in board.members.all() and assignee != board.owner:
                raise serializers.ValidationError({
                    'assignee': 'Assignee must be a board member or owner'
                })
        
        if reviewer:
            if reviewer not in board.members.all() and reviewer != board.owner:
                raise serializers.ValidationError({
                    'reviewer': 'Reviewer must be a board member or owner'
                })
        
        return attrs


class TaskUpdateSerializer(serializers.ModelSerializer):
    assignee = UserShortSerializer(read_only=True)
    reviewer = UserShortSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assignee',
        write_only=True,
        required=False,
        allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='reviewer',
        write_only=True,
        required=False,
        allow_null=True
    )
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id", "title", "description",
            "status", "priority", "assignee", "reviewer",
            "due_date", "comments_count", "assignee_id", "reviewer_id"
        ]
        read_only_fields = [
            "id", "comments_count", "assignee", "reviewer"
        ]

    def get_comments_count(self, obj):
        return obj.comments.count()

    def validate_status(self, value):
        if value not in dict(Task.STATUS_CHOICES):
            raise serializers.ValidationError("Invalid status choice.")
        return value

    def validate_priority(self, value):
        if value not in dict(Task.PRIORITY_CHOICES):
            raise serializers.ValidationError("Invalid priority choice.")
        return value

    def validate(self, attrs):
        if 'board' in self.initial_data:
            raise serializers.ValidationError({
                'board': 'Changing the board is not allowed.'
            })

        board = self.instance.board
        assignee = attrs.get('assignee')
        reviewer = attrs.get('reviewer')

        if assignee and assignee not in board.members.all() and assignee != board.owner:
            raise serializers.ValidationError({
                'assignee': 'Assignee must be a member or owner of the board.'
            })
        if reviewer and reviewer not in board.members.all() and reviewer != board.owner:
            raise serializers.ValidationError({
                'reviewer': 'Reviewer must be a member or owner of the board.'
            })
        return attrs


class TaskCommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = TaskComment
        fields = ["id", "created_at", "author", "content"]
        read_only_fields = ["id", "created_at", "author"]

    def get_author(self, obj):
        return obj.author.fullname if obj.author else None


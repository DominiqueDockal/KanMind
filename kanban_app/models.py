from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Board(models.Model):
    """
    Model representing a kanban board.

    Attributes:
        title (str): The title of the board.
        owner (User): The user who owns the board.
        members (User): Users who have access to this board.
    
    Relationships:
        - Each Board can have multiple members (many-to-many).
        - Each Board has an owner (one-to-many).
        - Each Board can have many associated tasks.
    """

    title = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_boards")
    members = models.ManyToManyField(User, related_name="boards")

    def __str__(self):
        """String representation showing board title and its ID."""
        return f"{self.title} (ID: {self.id})"
    
    class Meta:
        verbose_name = "Board"
        verbose_name_plural = "Boards"
        ordering = ["title", "id"]


class Task(models.Model):
    """
    Model representing a task within a board.

    Attributes:
        board (Board): The board this task belongs to.
        title (str): Title of the task.
        creator (User): User who created the task.
        description (str): Optional text description.
        status (str): Workflow status (choices).
        priority (str): Task priority (choices).
        assignee (User): User assigned to the task.
        reviewer (User): User reviewing the task.
        due_date (date): Deadline date.
        created_at, updated_at (datetime): Timestamps.

    Relationships:
        - Each Task belongs to one Board.
        - A Task may be assigned or reviewed by users.
        - Each Task may have many comments.
    """

    STATUS_CHOICES = [
        ("to-do", "To Do"),
        ("in-progress", "In Progress"),
        ("review", "Review"),
        ("done", "Done"),
    ]
    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_tasks", null=True, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="to-do")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="assigned_tasks", null=True, blank=True)
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="reviewing_tasks", null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """String representation showing task title and current status."""
        return f"{self.title} ({self.status})"
    
    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ["due_date", "priority"]


class TaskComment(models.Model):
    """
    Model representing a comment for a task.

    Attributes:
        task (Task): The task the comment belongs to.
        author (User): The user who wrote the comment.
        content (str): The text content of the comment.
        created_at (datetime): Time of creation.
    
    Relationships:
        - Each comment belongs to one task.
        - Each comment is written by a user.
    """

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """String representation shows author and a preview of content."""
        return f"{self.author.fullname}: {self.content[:20]}"
    
    class Meta:
        verbose_name = "Task Comment"
        verbose_name_plural = "Task Comments"
        ordering = ["created_at"]

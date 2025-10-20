# Kanban Backend

Backend API for a Kanban board application built with Django and Django REST Framework.

## Requirements

- Python 3.12+
- pip

## Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/kanban-backend.git
cd kanban-backend
```

2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run migrations
```bash
python manage.py migrate
```

5. Create superuser (optional)
```bash
python manage.py createsuperuser
```

6. Start development server
```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

## Project Structure

```
core/           # Project settings and configuration
authapp/        # Authentication and user management
kanbanapp/      # Kanban boards, tasks, and comments
```

## API Endpoints

### Authentication
- `POST /api/auth/registration/` - Register new user
- `POST /api/auth/login/` - Login and get token

### Boards
- `GET /api/boards/` - List all boards
- `POST /api/boards/` - Create new board
- `GET /api/boards/{id}/` - Get board details
- `PUT /api/boards/{id}/` - Update board
- `DELETE /api/boards/{id}/` - Delete board

### Tasks
- `GET /api/tasks/` - List all tasks
- `POST /api/tasks/` - Create new task
- `GET /api/tasks/{id}/` - Get task details
- `PUT /api/tasks/{id}/` - Update task
- `DELETE /api/tasks/{id}/` - Delete task

### Comments
- `GET /api/tasks/{task_id}/comments/` - List comments
- `POST /api/tasks/{task_id}/comments/` - Add comment
- `DELETE /api/tasks/{task_id}/comments/{id}/` - Delete comment

## CORS Configuration

CORS is configured using `django-cors-headers` to allow frontend integration. For production, update `CORS_ALLOWED_ORIGINS` in `settings.py` with your frontend URL.

## Dependencies

See `requirements.txt` for complete list.

## Notes

- Don't commit `db.sqlite3` to version control
- Keep `SECRET_KEY` and other sensitive data in environment variables
- The project uses token-based authentication

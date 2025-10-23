# KanMind Backend API

Backend API for the KanMind Kanban board application built with Django and Django REST Framework.

## Features

- 🔐 Token-based authentication
- 📋 Board management with member permissions
- ✅ Task management with assignees and reviewers
- 💬 Task comments
- 👥 User management
- 🔒 Role-based access control

## Tech Stack

- Python 3.12+
- Django 5.2.6
- Django REST Framework 3.16.1
- SQLite (development) / PostgreSQL (production ready)
- Token Authentication

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/kanmind-backend.git
cd kanmind-backend
```

### 2. Create and activate virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run migrations
```bash
python manage.py migrate
```

### 5. Create superuser (optional)
```bash
python manage.py createsuperuser
```

### 6. Start development server
```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

## Project Structure

```
KanMind/
├── core/               # Project settings and configuration
├── auth_app/           # Authentication and user management
│   ├── models.py       # Custom User model
│   ├── api/
│   │   ├── views.py    # Registration, Login, Email check
│   │   └── serializers.py
├── kanban_app/         # Kanban boards, tasks, and comments
│   ├── models.py       # Board, Task, TaskComment models
│   ├── api/
│   │   ├── views.py    # Board/Task/Comment views
│   │   ├── serializers.py
│   │   └── permissions.py
└── manage.py
```

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/registration/` | Register new user | No |
| POST | `/api/login/` | Login and get token | No |
| GET | `/api/email-check/?email={email}` | Check if email exists | Yes |

### Boards

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/boards/` | List user's boards | Yes |
| POST | `/api/boards/` | Create new board | Yes |
| GET | `/api/boards/{id}/` | Get board details | Yes |
| PATCH | `/api/boards/{id}/` | Update board | Yes (Member/Owner) |
| DELETE | `/api/boards/{id}/` | Delete board | Yes (Owner only) |

### Tasks

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/tasks/` | List all tasks | Yes |
| POST | `/api/tasks/` | Create new task | Yes (Board member) |
| GET | `/api/tasks/{id}/` | Get task details | Yes |
| PATCH | `/api/tasks/{id}/` | Update task | Yes (Board member) |
| DELETE | `/api/tasks/{id}/` | Delete task | Yes (Creator/Owner) |
| GET | `/api/tasks/assigned-to-me/` | List tasks assigned to user | Yes |
| GET | `/api/tasks/reviewing/` | List tasks user is reviewing | Yes |

### Comments

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/tasks/{task_id}/comments/` | List task comments | Yes (Board member) |
| POST | `/api/tasks/{task_id}/comments/` | Add comment | Yes (Board member) |
| DELETE | `/api/tasks/{task_id}/comments/{id}/` | Delete comment | Yes (Author only) |

## Authentication

This API uses token-based authentication. Include the token in the Authorization header:

```
Authorization: Token your_token_here
```

### Example: Register and Login

**Register:**
```bash
curl -X POST http://127.0.0.1:8000/api/registration/ \
  -H "Content-Type: application/json" \
  -d '{
    "fullname": "John Doe",
    "email": "john@example.com",
    "password": "securepass123",
    "repeated_password": "securepass123"
  }'
```

**Response:**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "fullname": "John Doe",
  "email": "john@example.com",
  "user_id": 1
}
```

**Login:**
```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepass123"
  }'
```

## Usage Examples

### Create a Board
```bash
curl -X POST http://127.0.0.1:8000/api/boards/ \
  -H "Authorization: Token your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Project",
    "members": [2, 3]
  }'
```

### Create a Task
```bash
curl -X POST http://127.0.0.1:8000/api/tasks/ \
  -H "Authorization: Token your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "board": 1,
    "title": "Implement login feature",
    "description": "Add user authentication",
    "status": "to-do",
    "priority": "high",
    "assignee_id": 2,
    "due_date": "2025-10-30"
  }'
```

## Permissions

- **Board Owner**: Can delete board, update settings, manage all tasks
- **Board Member**: Can view board, create/update tasks, add comments
- **Task Creator**: Can delete their own tasks
- **Comment Author**: Can delete their own comments

## Task Status Options

- `to-do` - Not started
- `in-progress` - Work in progress
- `review` - Ready for review
- `done` - Completed

## Task Priority Options

- `low` - Low priority
- `medium` - Medium priority (default)
- `high` - High priority

## CORS Configuration

CORS is configured using `django-cors-headers`. For production, update `CORS_ALLOWED_ORIGINS` in `settings.py`:

```python
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-domain.com",
]
```

## Environment Variables (Production)

Create a `.env` file:

```env
SECRET_KEY=your_secret_key_here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost/dbname
```

## Dependencies

```
Django==5.2.6
djangorestframework==3.16.1
django-cors-headers==4.9.0
```

See `requirements.txt` for complete list.

## Development Notes

- Database: SQLite for development (not committed to Git)
- Authentication: Token-based (DRF Token Authentication)
- User model: Custom user model with email as username
- API Documentation: Available in `/docs` (if added)

## Security Notes

- ⚠️ Keep `SECRET_KEY` secure and use environment variables
- ⚠️ Don't commit `db.sqlite3` to version control
- ⚠️ Set `DEBUG=False` in production
- ⚠️ Configure proper `ALLOWED_HOSTS` in production
- ⚠️ Use HTTPS in production

## Testing

Run tests:
```bash
python manage.py test
```

## License

[Your License Here]

## Contact

[Your Contact Info]

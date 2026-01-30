# Task Management System API

A comprehensive task management system built with FastAPI, SQLAlchemy, and PostgreSQL. Manage projects, tasks, assignments, tags, and track analytics with a production-ready RESTful API.

## Features

### Core Features
- ✅ **User Management**: Create, update, list, and manage users
- ✅ **Project Management**: Organize tasks into projects with ownership tracking
- ✅ **Task Management**: Full CRUD with status, priority, and due date tracking
- ✅ **Multi-User Assignments**: Assign multiple users to tasks with hour allocation
- ✅ **Tags & Categorization**: Tag tasks for better organization and filtering
- ✅ **Comments & Collaboration**: Add comments to tasks for team discussion
- ✅ **Overdue Tracking**: Identify and monitor overdue tasks
- ✅ **Advanced Filtering**: Filter tasks by status, priority, project, assignee
- ✅ **Analytics Dashboard**: Project statistics, user workload, completion trends

### Technical Features
- Async FastAPI with automatic API documentation
- SQLAlchemy ORM with async support
- PostgreSQL with advanced indexing
- Alembic migrations for schema versioning
- Type hints throughout the codebase
- Comprehensive validation with Pydantic
- UUID primary keys across all tables
- Automatic timestamps (created_at, updated_at)
- Connection pooling and optimization
- CORS middleware for cross-origin requests

## Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- pip or conda

### Installation

1. **Clone/Setup Project**
```bash
cd /path/to/task2
source venv/bin/activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
# or if venv is already setup
source venv/bin/activate
```

3. **Configure Database**
Create/verify `.env` file:
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/task_management
SQLALCHEMY_ECHO=False
SQLALCHEMY_POOL_SIZE=10
SQLALCHEMY_MAX_OVERFLOW=20
```

4. **Run Migrations**
```bash
alembic upgrade head
```

5. **Start Application**
```bash
uvicorn main:app --reload
```

Application runs at: `http://localhost:8000`

## API Documentation

### Interactive API Docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## API Endpoints

### Users (`/users`)
```
POST   /                      Create user
GET    /                      List users (paginated)
GET    /{user_id}             Get user details
GET    /email/{email}         Get user by email
GET    /list/active           List active users
PUT    /{user_id}             Update user
DELETE /{user_id}             Delete user
PATCH  /{user_id}/deactivate  Deactivate user
```

### Projects (`/projects`)
```
POST   /                              Create project
GET    /                              List projects (paginated)
GET    /list/active                   List active projects
GET    /{project_id}                  Get project details
GET    /owner/{owner_id}              Get user's projects
GET    /{project_id}/stats            Get project statistics
PUT    /{project_id}                  Update project
DELETE /{project_id}                  Delete project
PATCH  /{project_id}/deactivate       Deactivate project (soft delete)
```

### Tasks (`/tasks`)
```
POST   /                              Create task
GET    /                              List tasks (paginated)
GET    /{task_id}                     Get task with all details
GET    /project/{project_id}          Get project tasks
GET    /assignee/{user_id}            Get user's tasks
GET    /status/{status}               Get tasks by status
GET    /priority/{priority}           Get tasks by priority
GET    /list/overdue                  Get overdue tasks
GET    /list/upcoming                 Get upcoming tasks (7 days)
POST   /filter                        Advanced filtering
PUT    /{task_id}                     Update task
PATCH  /{task_id}/complete            Mark task completed
DELETE /{task_id}                     Delete task
```

**Task Status**: `pending`, `in_progress`, `completed`, `cancelled`, `on_hold`  
**Task Priority**: `low`, `medium`, `high`, `critical`

### Tags (`/tags`)
```
POST   /                              Create tag
GET    /                              List tags (paginated)
GET    /{tag_id}                      Get tag details
GET    /name/{name}                   Get tag by name
PUT    /{tag_id}                      Update tag
DELETE /{tag_id}                      Delete tag
POST   /{tag_id}/attach/{task_id}     Attach tag to task
DELETE /{tag_id}/detach/{task_id}     Detach tag from task
```

### Assignments (`/assignments`)
```
POST   /                              Create assignment (assign user to task)
GET    /task/{task_id}                Get task assignments
GET    /user/{user_id}                Get user assignments
DELETE /task/{task_id}/user/{user_id} Remove assignment
```

### Comments (`/comments`)
```
POST   /                              Create comment
GET    /task/{task_id}                Get task comments
GET    /user/{user_id}                Get user's comments
GET    /{comment_id}                  Get comment details
PUT    /{comment_id}                  Update comment
DELETE /{comment_id}                  Delete comment
```

### Analytics (`/analytics`)
```
GET    /dashboard                     Get task overview dashboard
GET    /project/{project_id}          Get project analytics
GET    /user/{user_id}                Get user workload
GET    /overdue-tasks                 Get all overdue tasks
GET    /completion-trend              Get 30-day completion trend
```

## Example Requests

### 1. Create User
```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "username": "john_doe",
    "full_name": "John Doe"
  }'
```

### 2. Create Project
```bash
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Website Redesign",
    "description": "Redesigning company website",
    "owner_id": "<USER_UUID>"
  }'
```

### 3. Create Task
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Design homepage mockup",
    "description": "Create initial mockup for homepage",
    "project_id": "<PROJECT_UUID>",
    "assigned_to": "<USER_UUID>",
    "status": "in_progress",
    "priority": "high",
    "due_date": "2025-02-15T17:00:00"
  }'
```

### 4. Assign User to Task
```bash
curl -X POST http://localhost:8000/assignments \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "<TASK_UUID>",
    "user_id": "<USER_UUID>",
    "hours_allocated": 8
  }'
```

### 5. Add Comment
```bash
curl -X POST http://localhost:8000/comments \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "<TASK_UUID>",
    "content": "Started working on this task"
  }'
```

### 6. Filter Tasks
```bash
curl -X POST http://localhost:8000/tasks/filter \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "<PROJECT_UUID>",
    "status": "pending",
    "priority": "high",
    "skip": 0,
    "limit": 10
  }'
```

### 7. Get Dashboard
```bash
curl http://localhost:8000/analytics/dashboard
```

### 8. Get Project Analytics
```bash
curl http://localhost:8000/analytics/project/<PROJECT_UUID>
```

## Database Schema

### Tables
- **users**: User accounts with email and username
- **projects**: Project organization with owner tracking
- **tasks**: Tasks with status, priority, and due dates
- **tags**: Tags for categorization
- **task_tags**: Junction table for task-tag relationships
- **task_assignments**: Multi-user assignment tracking
- **task_comments**: Comments on tasks

### Key Features
- UUID primary keys across all tables
- Automatic timestamps (created_at, updated_at)
- Foreign key constraints with cascade delete
- Unique constraints for email, username, tag names
- Composite index on (project_id, status) for dashboard queries
- Check constraint for due_date/completed_at validation

## Project Structure

```
sql_app/
├── db/                    # Database configuration
├── migrations/            # Alembic schema migrations
├── models/                # SQLAlchemy ORM models
├── schemas/               # Pydantic validation schemas
├── services/              # Business logic layer
└── routers/               # API endpoint definitions

main.py                     # FastAPI application
alembic.ini                 # Alembic configuration
.env                        # Environment variables
```

## Configuration

### Environment Variables
```
DATABASE_URL              # PostgreSQL connection URL
SQLALCHEMY_ECHO          # Log SQL queries (True/False)
SQLALCHEMY_POOL_SIZE     # Connection pool size (default: 10)
SQLALCHEMY_MAX_OVERFLOW  # Max connections above pool size (default: 20)
```

### Database Connection
- **Driver**: AsyncPG (async PostgreSQL driver)
- **Pool**: Configurable with pre-ping enabled
- **Timezone**: UTC with timezone support

## Architecture

### Layered Architecture
```
API Routes (FastAPI routers)
    ↓
Services (Business Logic)
    ↓
SQLAlchemy Models (ORM)
    ↓
PostgreSQL Database
```

### Services
- **UserService**: User CRUD and lookups
- **ProjectService**: Project management and statistics
- **TaskService**: Task operations and filtering
- **TagService**: Tag management
- **TaskAssignmentService**: Multi-user assignments
- **TaskCommentService**: Comment management
- **AnalyticsService**: Advanced queries and reporting

## Performance Optimization

### Indexes
- Single-column indexes on foreign keys and filter columns
- Composite index on (project_id, status) for dashboard
- Indexes on due_date, priority, status

### Query Optimization
- Eager loading with `selectinload()` to prevent N+1 queries
- Pagination support with skip/limit
- Batch operations for bulk updates
- Connection pooling with configurable size

### Database Features
- CHECK constraints for business logic
- UNIQUE constraints for data integrity
- CASCADE delete for referential integrity
- Server-side defaults for timestamps

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest

# Run with coverage
pytest --cov=sql_app tests/
```

## Migrations

### Create New Migration
```bash
alembic revision --autogenerate -m "description"
```

### Apply Migrations
```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific version
alembic upgrade <revision>

# Downgrade
alembic downgrade -1
```

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running
- Verify DATABASE_URL in .env
- Check user permissions

### Port Already in Use
```bash
# Use different port
uvicorn main:app --port 8001
```

### Migration Errors
```bash
# Reset and reapply
alembic downgrade base
alembic upgrade head
```

## Production Deployment

### Best Practices
1. Set `SQLALCHEMY_ECHO=False` in production
2. Use environment-specific secrets
3. Enable HTTPS in reverse proxy
4. Set up monitoring and logging
5. Use Gunicorn with multiple workers
6. Configure proper database backups

### Running with Gunicorn
```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

## Contributing

When adding features:
1. Add database model in `models/models.py`
2. Create Alembic migration
3. Add Pydantic schemas in `schemas/`
4. Implement service in `services/`
5. Create API routes in `routers/`
6. Add type hints throughout
7. Update this README if needed

## License

This project is provided as-is for educational and commercial use.

## Support

For issues or questions, please refer to:
- FastAPI Documentation: https://fastapi.tiangolo.com/
- SQLAlchemy Async: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- Alembic: https://alembic.sqlalchemy.org/

## Summary

This is a **complete, production-ready Task Management System** implementing:
- ✅ Full CRUD operations for all entities
- ✅ Advanced filtering and analytics
- ✅ Complex relational database design
- ✅ Async operations throughout
- ✅ Type-safe validation
- ✅ Comprehensive error handling
- ✅ RESTful API design
- ✅ Database optimization
- ✅ Clean code architecture

Start building with the API right away using the interactive docs at `/docs`!

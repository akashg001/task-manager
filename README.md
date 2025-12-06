# Task Manager API

A RESTful API for task management built with Django REST Framework, featuring JWT authentication, role-based access control, and comprehensive test coverage.

## Setup

### 1. Clone Repository
```bash
git clone <repository-url>
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## Run Server
```bash
python manage.py runserver
```
Server runs at: `http://localhost:8000`

## Run Tests
```bash
python manage.py test
```

## API Documentation
**Swagger UI**: http://localhost:8000/api/docs/

---

## API Endpoints

### Authentication

#### Register User
```bash
POST /api/auth/register/

curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "pass123",
    "role": "user"
  }'
```
**Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "john",
    "email": "john@example.com",
    "role": "user",
    "created_at": "2025-12-06T10:30:00Z"
  }
}
```

#### Login
```bash
POST /api/auth/login/

curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "pass123"
  }'
```
**Response:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "john",
    "email": "john@example.com",
    "role": "user"
  }
}
```

---

### Tasks (Authentication Required)

**Set token:** `export TOKEN="your_access_token"`

#### Get All Tasks
```bash
GET /api/tasks/

curl http://localhost:8000/api/tasks/ \
  -H "Authorization: Bearer $TOKEN"
```
**Response:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Task 1",
      "description": "Description",
      "completed": false,
      "created_at": "2025-12-06T11:00:00Z",
      "updated_at": "2025-12-06T11:00:00Z",
      "owner": 1,
      "owner_username": "john"
    }
  ]
}
```

#### Get Task by ID
```bash
GET /api/tasks/{id}/

curl http://localhost:8000/api/tasks/1/ \
  -H "Authorization: Bearer $TOKEN"
```
**Response:**
```json
{
  "id": 1,
  "title": "Task 1",
  "description": "Description",
  "completed": false,
  "created_at": "2025-12-06T11:00:00Z",
  "updated_at": "2025-12-06T11:00:00Z",
  "owner": 1,
  "owner_username": "john"
}
```

#### Create Task
```bash
POST /api/tasks/

curl -X POST http://localhost:8000/api/tasks/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Task",
    "description": "Task description"
  }'
```
**Response:**
```json
{
  "message": "Task created successfully",
  "task": {
    "id": 2,
    "title": "New Task",
    "description": "Task description",
    "completed": false,
    "created_at": "2025-12-06T11:15:00Z",
    "updated_at": "2025-12-06T11:15:00Z",
    "owner": 1,
    "owner_username": "john"
  }
}
```

#### Update Task (Full)
```bash
PUT /api/tasks/{id}/

curl -X PUT http://localhost:8000/api/tasks/1/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Task",
    "description": "New description",
    "completed": true
  }'
```
**Response:**
```json
{
  "message": "Task updated successfully",
  "task": {
    "id": 1,
    "title": "Updated Task",
    "description": "New description",
    "completed": true,
    "created_at": "2025-12-06T11:00:00Z",
    "updated_at": "2025-12-06T11:20:00Z",
    "owner": 1,
    "owner_username": "john"
  }
}
```

#### Update Task (Partial)
```bash
PATCH /api/tasks/{id}/

curl -X PATCH http://localhost:8000/api/tasks/1/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "completed": true
  }'
```
**Response:**
```json
{
  "message": "Task updated successfully",
  "task": {
    "id": 1,
    "title": "Task 1",
    "description": "Description",
    "completed": true,
    "created_at": "2025-12-06T11:00:00Z",
    "updated_at": "2025-12-06T11:25:00Z",
    "owner": 1,
    "owner_username": "john"
  }
}
```

#### Delete Task
```bash
DELETE /api/tasks/{id}/

curl -X DELETE http://localhost:8000/api/tasks/1/ \
  -H "Authorization: Bearer $TOKEN"
```
**Response:**
```json
{
  "message": "Task deleted successfully"
}
```

#### Get Task Statistics
```bash
GET /api/tasks/stats/

curl http://localhost:8000/api/tasks/stats/ \
  -H "Authorization: Bearer $TOKEN"
```
**Response:**
```json
{
  "total": 10,
  "completed": 6,
  "pending": 4
}
```

---

### Filtering & Pagination

#### Filter Completed Tasks
```bash
curl "http://localhost:8000/api/tasks/?completed=true" \
  -H "Authorization: Bearer $TOKEN"
```

#### Filter Pending Tasks
```bash
curl "http://localhost:8000/api/tasks/?completed=false" \
  -H "Authorization: Bearer $TOKEN"
```

#### Search Tasks
```bash
curl "http://localhost:8000/api/tasks/?search=keyword" \
  -H "Authorization: Bearer $TOKEN"
```

#### Pagination
```bash
curl "http://localhost:8000/api/tasks/?page=1&page_size=5" \
  -H "Authorization: Bearer $TOKEN"
```

#### Combined Filters
```bash
curl "http://localhost:8000/api/tasks/?completed=false&search=urgent&ordering=-created_at" \
  -H "Authorization: Bearer $TOKEN"
```

---

### Admin Endpoints (Admin Role Required)

#### Register Admin User
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "admin123",
    "role": "admin"
  }'
```

#### Get All Users
```bash
GET /api/users/

curl http://localhost:8000/api/users/ \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Response:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "john",
      "email": "john@example.com",
      "role": "user",
      "created_at": "2025-12-06T10:30:00Z"
    },
    {
      "id": 2,
      "username": "admin",
      "email": "admin@example.com",
      "role": "admin",
      "created_at": "2025-12-06T11:30:00Z"
    }
  ]
}
```

#### Get User by ID
```bash
GET /api/users/{id}/

curl http://localhost:8000/api/users/1/ \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Response:**
```json
{
  "id": 1,
  "username": "john",
  "email": "john@example.com",
  "role": "user",
  "created_at": "2025-12-06T10:30:00Z"
}
```

---

## Complete Workflow

```bash
# 1. Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"pass123"}'

# 2. Login (save the access token)
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"pass123"}'

# Set token as environment variable
export TOKEN="your_access_token_here"

# 3. Create task
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"My First Task","description":"Task details"}'

# 4. List all tasks
curl http://localhost:8000/api/tasks/ \
  -H "Authorization: Bearer $TOKEN"

# 5. Update task (mark as completed)
curl -X PATCH http://localhost:8000/api/tasks/1/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"completed":true}'

# 6. Get statistics
curl http://localhost:8000/api/tasks/stats/ \
  -H "Authorization: Bearer $TOKEN"

# 7. Delete task
curl -X DELETE http://localhost:8000/api/tasks/1/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## Project Structure

```
task_manager_project/
├── task_manager/           # Project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── tasks/                  # Tasks app
│   ├── __init__.py
│   ├── models.py          # User and Task models
│   ├── serializers.py     # DRF serializers
│   ├── views.py           # API views
│   ├── permissions.py     # Custom permissions
│   ├── urls.py            # App URLs
│   ├── admin.py           # Django admin
│   ├── tests.py           # Unit tests
│   └── migrations/
├── manage.py
├── requirements.txt
├── README.md
└── db.sqlite3             # Database (created after migrations)
```

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Server Error |

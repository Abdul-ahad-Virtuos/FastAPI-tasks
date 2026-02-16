# JWT Authentication FastAPI

Minimal modular JWT authentication implementation in FastAPI.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file (or just use defaults)
cp .env.example .env

# Run the app
python main.py
```

The app will start on `http://localhost:8000`

## API Endpoints

### 1. Register User
```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Password123"}'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Password123"}'
```

Returns:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### 3. Protected Route
```bash
curl -X GET http://localhost:8000/protected \
  -H "Authorization: Bearer <access_token>"
```

## Features

✅ JWT authentication (HS256)  
✅ Password hashing with bcrypt  
✅ Pydantic validation  
✅ Custom logging middleware  
✅ Dependency injection  
✅ Global error handling  
✅ In-memory user storage  
✅ Type hints  
✅ 3 files only + requirements  

## File Structure

- `main.py` - FastAPI app, routes, middleware, dependencies
- `auth.py` - JWT utilities, password hashing, Pydantic schemas
- `config.py` - Configuration and constants
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variables template

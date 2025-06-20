---
applyTo: "**/*api*.py,**/*service*.py,**/*controller*.py"
---
# API Development Guidelines

Apply the [general coding guidelines](./copilot-instructions-general.md) and [Python guidelines](./copilot-instructions-python.md) to all code.

## RESTful API Design Principles

### HTTP Methods
- GET: Retrieve data (idempotent)
- POST: Create new resources
- PUT: Update entire resource (idempotent)
- PATCH: Partial resource updates
- DELETE: Remove resources (idempotent)

### URL Structure
```
/api/v1/resources          # GET (list), POST (create)
/api/v1/resources/{id}     # GET (retrieve), PUT (update), DELETE (remove)
/api/v1/resources/{id}/related  # Nested resources
```

### Status Codes
- 200: OK (successful GET, PUT, PATCH)
- 201: Created (successful POST)
- 204: No Content (successful DELETE)
- 400: Bad Request (client error)
- 401: Unauthorized (authentication required)
- 403: Forbidden (insufficient permissions)
- 404: Not Found (resource doesn't exist)
- 422: Unprocessable Entity (validation error)
- 500: Internal Server Error

## Request/Response Patterns

### Request Validation
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CreateUserRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    age: Optional[int] = Field(None, ge=0, le=150)
    
class UpdateUserRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    age: Optional[int] = Field(None, ge=0, le=150)
```

### Response Models
```python
from typing import List, Optional
from datetime import datetime

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int]
    created_at: datetime
    updated_at: datetime
    
class PaginatedResponse(BaseModel):
    items: List[UserResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[dict] = None
```

### Error Handling
```python
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class APIError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

def handle_api_error(func):
    """Decorator for consistent error handling."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            raise HTTPException(status_code=422, detail=str(e))
        except NotFoundError as e:
            logger.info(f"Resource not found: {e}")
            raise HTTPException(status_code=404, detail=str(e))
        except APIError as e:
            logger.error(f"API error: {e}")
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    return wrapper
```

## FastAPI Patterns

### Dependency Injection
```python
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    user = verify_token(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user
```

### Route Organization
```python
from fastapi import APIRouter, Depends, HTTPException
from typing import List

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: CreateUserRequest,
    db: Session = Depends(get_db)
):
    user = User(**user_data.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

## Authentication & Authorization

### JWT Token Pattern
```python
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, db: Session) -> Optional[User]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        
        user = db.query(User).filter(User.username == username).first()
        return user
    except JWTError:
        return None
```

### Permission Checking
```python
from enum import Enum
from functools import wraps

class Permission(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"

def require_permission(permission: Permission):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if not has_permission(current_user, permission):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

@router.delete("/{user_id}")
@require_permission(Permission.DELETE)
async def delete_user(user_id: int, current_user: User = Depends(get_current_user)):
    # Delete logic here
    pass
```

## Testing APIs

### Test Structure
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db):
    def override_get_db():
        yield db
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

def test_create_user(client):
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "age": 25
    }
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201
    assert response.json()["name"] == user_data["name"]
```

## Documentation
- Use OpenAPI/Swagger documentation
- Provide clear endpoint descriptions
- Include request/response examples
- Document authentication requirements
- Add rate limiting information

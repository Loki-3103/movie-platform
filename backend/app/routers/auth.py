from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.deps import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.core.auth_deps import get_current_user
from app.crud.user import get_user_by_email, get_user_by_username, create_user
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if get_user_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if get_user_by_username(db, payload.username):
        raise HTTPException(status_code=400, detail="Username already taken")

    user = create_user(db, payload.username, payload.email, hash_password(payload.password))
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

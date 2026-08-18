from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database.deps import get_db
from app.core.security import decode_access_token
from app.crud.user import get_user_by_id
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)


def get_current_user(token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        raise credentials_exception

    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise credentials_exception

    user = get_user_by_id(db, int(payload["sub"]))
    if user is None:
        raise credentials_exception
    return user


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


def get_optional_user(token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User | None:
    # Used by endpoints that should work for anonymous visitors (like search)
    # but still personalize/log activity when a valid token is present.
    if token is None:
        return None
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        return None
    return get_user_by_id(db, int(payload["sub"]))

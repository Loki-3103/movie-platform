from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.deps import get_db
from app.core.auth_deps import get_current_admin_user
from app.crud import admin as crud
from app.schemas.admin import AdminUserResponse, AdminStatsResponse
from app.models.user import User

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users", response_model=list[AdminUserResponse])
def list_users(db: Session = Depends(get_db), _admin: User = Depends(get_current_admin_user)):
    return crud.list_all_users(db)


@router.get("/stats", response_model=AdminStatsResponse)
def get_stats(db: Session = Depends(get_db), _admin: User = Depends(get_current_admin_user)):
    return crud.get_platform_stats(db)


@router.delete("/users/{user_id}", status_code=204)
def remove_user(user_id: int, db: Session = Depends(get_db), _admin: User = Depends(get_current_admin_user)):
    deleted = crud.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")

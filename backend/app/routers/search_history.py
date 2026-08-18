from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.deps import get_db
from app.core.auth_deps import get_current_user
from app.crud import interactions as crud
from app.schemas.interactions import SearchHistoryResponse
from app.models.user import User

router = APIRouter(prefix="/api/search-history", tags=["search-history"])


@router.get("", response_model=list[SearchHistoryResponse])
def get_search_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud.list_search_history(db, current_user.id)

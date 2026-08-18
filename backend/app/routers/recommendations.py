from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.deps import get_db
from app.core.auth_deps import get_current_user
from app.services.recommendations import get_recommendations
from app.models.user import User

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("")
async def my_recommendations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await get_recommendations(db, current_user.id)

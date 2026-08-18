from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.deps import get_db
from app.core.auth_deps import get_current_user
from app.crud import interactions as crud
from app.schemas.interactions import RatingRequest, RatingResponse
from app.models.user import User

router = APIRouter(prefix="/api/ratings", tags=["ratings"])


@router.get("", response_model=list[RatingResponse])
def list_my_ratings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud.list_ratings(db, current_user.id)


@router.post("", response_model=RatingResponse)
def rate_movie(payload: RatingRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not 1 <= payload.score <= 10:
        raise HTTPException(status_code=422, detail="Score must be between 1 and 10")
    return crud.upsert_rating(db, current_user.id, payload.tmdb_movie_id, payload.score)

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.deps import get_db
from app.core.auth_deps import get_current_user
from app.crud import interactions as crud
from app.schemas.interactions import ReviewRequest, ReviewResponse
from app.models.user import User

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@router.get("/movie/{tmdb_movie_id}", response_model=list[ReviewResponse])
def list_movie_reviews(tmdb_movie_id: int, db: Session = Depends(get_db)):
    return crud.list_reviews_for_movie(db, tmdb_movie_id)


@router.get("/me", response_model=list[ReviewResponse])
def list_my_reviews(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud.list_reviews_by_user(db, current_user.id)


@router.post("", response_model=ReviewResponse, status_code=201)
def write_review(payload: ReviewRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud.add_review(db, current_user.id, payload.tmdb_movie_id, payload.content)

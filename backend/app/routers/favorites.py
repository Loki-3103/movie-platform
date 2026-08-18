from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.deps import get_db
from app.core.auth_deps import get_current_user
from app.crud import interactions as crud
from app.schemas.interactions import MovieRefRequest, FavoriteResponse
from app.models.user import User

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


@router.get("", response_model=list[FavoriteResponse])
def list_my_favorites(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud.list_favorites(db, current_user.id)


@router.post("", response_model=FavoriteResponse, status_code=201)
def add_favorite(payload: MovieRefRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud.add_favorite(db, current_user.id, payload.tmdb_movie_id, payload.title, payload.poster_path)


@router.delete("/{tmdb_movie_id}", status_code=204)
def remove_favorite(tmdb_movie_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    removed = crud.remove_favorite(db, current_user.id, tmdb_movie_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Favorite not found")

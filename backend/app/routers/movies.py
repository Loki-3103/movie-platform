from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.deps import get_db
from app.core.auth_deps import get_optional_user
from app.services import tmdb
from app.crud.interactions import add_search_history
from app.models.user import User

router = APIRouter(prefix="/api/movies", tags=["movies"])


@router.get("/search")
async def search(
    q: str = Query(..., min_length=1),
    page: int = 1,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    if current_user:
        add_search_history(db, current_user.id, q)
    return await tmdb.search_movies(q, page)


@router.get("/popular")
async def popular(page: int = 1):
    return await tmdb.get_popular(page)


@router.get("/trending")
async def trending(time_window: str = "week"):
    return await tmdb.get_trending(time_window)


@router.get("/top-rated")
async def top_rated(page: int = 1):
    return await tmdb.get_top_rated(page)


@router.get("/upcoming")
async def upcoming(page: int = 1):
    return await tmdb.get_upcoming(page)


@router.get("/genres")
async def genres():
    return await tmdb.get_genres()


@router.get("/{movie_id}")
async def movie_details(movie_id: int):
    return await tmdb.get_movie_details(movie_id)

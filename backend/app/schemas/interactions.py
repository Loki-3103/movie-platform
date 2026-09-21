from datetime import datetime
from pydantic import BaseModel


class MovieRefRequest(BaseModel):
    tmdb_movie_id: int
    title: str
    poster_path: str | None = None


class FavoriteResponse(BaseModel):
    id: int
    tmdb_movie_id: int
    title: str
    poster_path: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class WatchlistResponse(FavoriteResponse):
    pass


class RatingRequest(BaseModel):
    tmdb_movie_id: int
    score: float


class RatingResponse(BaseModel):
    id: int
    tmdb_movie_id: int
    score: float
    created_at: datetime

    class Config:
        from_attributes = True


class RatingWithRecommendationsResponse(RatingResponse):
    """Returned by POST /api/ratings: the saved rating plus a fresh batch of
    recommendations sized by the score (5 movies when the rating is above 5,
    2 movies when it is 5 or below). The count is variable on purpose so the
    UI renders it dynamically without needing special cases."""

    recommendations: list[dict] = []


class ReviewRequest(BaseModel):
    tmdb_movie_id: int
    content: str


class ReviewResponse(BaseModel):
    id: int
    tmdb_movie_id: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class SearchHistoryResponse(BaseModel):
    id: int
    query: str
    created_at: datetime

    class Config:
        from_attributes = True

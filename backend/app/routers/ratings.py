from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.deps import get_db
from app.core.auth_deps import get_current_user
from app.crud import interactions as crud
from app.schemas.interactions import (
    RatingRequest,
    RatingResponse,
    RatingWithRecommendationsResponse,
)
from app.services.recommendations import get_rating_recommendations
from app.models.user import User

router = APIRouter(prefix="/api/ratings", tags=["ratings"])


@router.get("", response_model=list[RatingResponse])
def list_my_ratings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud.list_ratings(db, current_user.id)


@router.post("", response_model=RatingWithRecommendationsResponse)
async def rate_movie(
    payload: RatingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Save the user's rating, then generate post-rating recommendations.

    The recommendation count (5 vs 2) is decided in ONE place - the service
    layer's get_rating_recommendations - by the RATING_THRESHOLD constant, and
    returned to the caller as a normal variable-length list. The endpoint just
    saves the rating and attaches the recommendations to the response.
    """
    if not 1 <= payload.score <= 10:
        raise HTTPException(status_code=422, detail="Score must be between 1 and 10")

    rating = crud.upsert_rating(db, current_user.id, payload.tmdb_movie_id, payload.score)
    recommendations = await get_rating_recommendations(
        db, current_user.id, payload.tmdb_movie_id, payload.score
    )

    data = RatingResponse.model_validate(rating).model_dump()
    data["recommendations"] = recommendations
    return data
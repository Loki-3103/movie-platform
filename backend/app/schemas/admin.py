from datetime import datetime
from pydantic import BaseModel


class AdminUserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AdminStatsResponse(BaseModel):
    total_users: int
    total_favorites: int
    total_watchlist_items: int
    total_ratings: int
    total_reviews: int

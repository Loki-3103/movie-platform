import httpx
from fastapi import HTTPException
from app.core.config import settings

# Single wrapper around TMDb. Every route that needs movie data goes through
# this file. If TMDb's API ever changes, this is the only place we touch.

BASE_URL = settings.tmdb_base_url


async def _get(path: str, params: dict | None = None) -> dict:
    params = params or {}
    params["api_key"] = settings.tmdb_api_key
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{BASE_URL}{path}", params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="TMDb API request failed")
    return response.json()


async def search_movies(query: str, page: int = 1) -> dict:
    return await _get("/search/movie", {"query": query, "page": page})


async def get_popular(page: int = 1) -> dict:
    return await _get("/movie/popular", {"page": page})


async def get_trending(time_window: str = "week") -> dict:
    return await _get(f"/trending/movie/{time_window}")


async def get_top_rated(page: int = 1) -> dict:
    return await _get("/movie/top_rated", {"page": page})


async def get_upcoming(page: int = 1) -> dict:
    return await _get("/movie/upcoming", {"page": page})


async def get_movie_details(movie_id: int) -> dict:
    return await _get(f"/movie/{movie_id}", {"append_to_response": "credits,videos,similar"})


async def get_genres() -> dict:
    return await _get("/genre/movie/list")

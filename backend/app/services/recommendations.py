from collections import Counter, defaultdict
import asyncio

from sqlalchemy.orm import Session

from app.crud.interactions import list_favorites, list_ratings, list_watchlist
from app.services import tmdb

# ---------------------------------------------------------------------------
# Design note (important for interviews):
#
# get_recommendations() is the ONLY function the recommendations router calls,
# and get_rating_recommendations() is the only function the ratings router
# calls. Both run a rule-based scoring strategy right now, but later their
# bodies could be swapped for "call a trained model" without touching any
# router or schema, because their signatures (user -> list of movie dicts)
# stay the same. This is the Strategy pattern - callers don't know or care how
# recommendations are produced internally.
#
# Both functions share the same pipeline:
#   1. Build a "taste profile" from the user's own data (favorites + ratings +
#      watchlist): weighted genre affinity and creator (director / cast)
#      affinity. This is where "user rating patterns" enter the equation.
#   2. Gather candidates from MULTIPLE channels so no single source dominates:
#      TMDb "similar" lists per seed + genre discovery per top genre + a
#      quality-filtered popular list as a safety net.
#   3. Score every candidate on cheap fields (genre overlap, vote_average,
#      vote_count, popularity, how many distinct favorites it is similar to),
#      then re-rank the top candidates using a concurrent credits lookup so
#      director / cast overlap can lift movies "beyond genre".
#   4. Deduplicate aggressively against everything the user has already
#      favorited, rated, or watchlisted.
#   5. Apply a per-genre diversity cap so one genre family can't flood the
#      result.
#   6. Fall back to a quality-filtered popular list whenever anything is
#      empty or short.
# ---------------------------------------------------------------------------

# --- Tunable constants (single source of truth for behavior tweaks) --------

MAX_SEED_MOVIES = 6            # fan-out cap: how many seed details we fetch
MIN_VOTE_COUNT = 20            # ignore candidates with almost no community votes
BASE_FAVORITE_WEIGHT = 0.75    # genre strength for an unrated favorite
RATING_THRESHOLD = 5.0         # ratings strictly above this are "liked"
HIGH_SCORE_RECOMMEND_COUNT = 5  # liked (score > 5)  -> recommend this many
LOW_SCORE_RECOMMEND_COUNT = 2   # not liked (<= 5)   -> recommend this many
DIVERSITY_CAP_RATIO = 0.4      # max share of the list one genre may occupy
RERANK_TOP_K = 12              # how many top candidates get the credits re-rank
TOP_GENRES_FOR_DISCOVERY = 3   # how many of the user's top genres to explore

# Score weights. Genre overlap is the dominant signal (that is the whole point
# of the "For You" page); the quality + popularity terms act as filters so we
# never surface junk; the similarity term rewards movies that several distinct
# favorites already point at.
SCORE_WEIGHTS = {
    "genre": 0.55,
    "quality": 0.25,
    "popularity": 0.10,
    "similarity": 0.10,
}


# ---------------------------------------------------------------------------
# Taste profile
# ---------------------------------------------------------------------------

async def _safe_movie_details(movie_id: int) -> dict:
    """Fetch one movie's details, returning {} on any failure.

    A single movie that was deleted on TMDb (or a transient network error)
    must NOT take down the whole recommendation run for everyone, so errors
    are swallowed here and empty dicts are filtered out by the callers.
    """
    try:
        return await tmdb.get_movie_details(movie_id)
    except Exception:
        return {}


def _build_genre_affinity(seeds: list[dict], ratings_map: dict) -> dict[int, float]:
    """Turn the seed movies into a weighted genre profile.

    Each seed contributes its genres with a strength equal to the user's OWN
    rating of that seed (score/10 so 5..10 maps to 0.5..1.0) or the milder
    BASE_FAVORITE_WEIGHT when the seed is favorited but unrated - this is the
    "user rating patterns" signal. Spreading the seed's strength across all of
    its genres (1 / len(genres)) handles the single-genre vs multi-genre
    asymmetry: a single-genre favorite is a focused, strong signal while a
    multi-genre favorite spreads its influence thinly instead of maxing out
    every genre. Accumulating (not averaging) also means a genre shared by
    several favorites genuinely outweighs one shared by a single favorite.
    The seed count is bounded by MAX_SEED_MOVIES, so values stay sane.
    """
    affinity: dict[int, float] = defaultdict(float)
    for details in seeds:
        genres = details.get("genres", [])
        if not genres:
            continue
        rating = ratings_map.get(details["id"])
        strength = rating / 10.0 if rating else BASE_FAVORITE_WEIGHT
        per_genre = strength / len(genres)
        for genre in genres:
            affinity[genre["id"]] += per_genre
    return dict(affinity)


def _build_creator_affinity(seeds: list[dict]) -> dict:
    """Collect directors and top-billed cast across all seeds.

    This is the "beyond genre" half of the profile. It is used later to
    re-rank the top candidates, so a movie by the same director as (or sharing
    actors with) the user's favorites can beat one that merely shares a genre.
    """
    directors: Counter = Counter()
    cast: Counter = Counter()
    for details in seeds:
        credits = details.get("credits", {})
        for crew in credits.get("crew", []):
            if crew.get("job") == "Director":
                directors[crew["id"]] += 1
        for member in credits.get("cast", [])[:10]:
            cast[member["id"]] += 1
    return {"directors": directors, "cast": cast}


# ---------------------------------------------------------------------------
# Candidate gathering
# ---------------------------------------------------------------------------

def _collect_similar_candidates(
    seeds: list[dict],
    seen: set,
    candidates: dict,
    affinity_counts: Counter,
) -> None:
    """Channel 1: TMDb per-movie "similar" lists.

    A movie that appears in several seeds' similar lists is highly relevant,
    so we count occurrences per candidate as an extra similarity signal that
    later feeds the similarity score component.
    """
    for details in seeds:
        for movie in details.get("similar", {}).get("results", []):
            mid = movie["id"]
            if mid in seen:
                continue
            candidates[mid] = movie
            affinity_counts[mid] += 1


async def _collect_genre_discovery(genre_ids: list[int], seen: set, candidates: dict) -> None:
    """Channel 2: fresh titles inside the user's favorite genres.

    The similar-lists channel cannot propose anything the user has not already
    brushed against, so we also pull popularity-sorted candidates per genre.
    Discovery is a secondary source (does not affect the similarity count),
    and a failed discover call is non-fatal.
    """
    for genre_id in genre_ids:
        try:
            data = await tmdb.discover_movies(genre_ids=[genre_id])
        except Exception:
            continue  # one bad genre should not break the whole request
        for movie in data.get("results", []):
            mid = movie["id"]
            if mid not in seen:
                candidates.setdefault(mid, movie)


# ---------------------------------------------------------------------------
# Scoring + selection
# ---------------------------------------------------------------------------

def _score_candidates(
    candidates: dict,
    affinity: dict[int, float],
    affinity_counts: Counter,
    seed_volume: int,
) -> list[tuple[float, dict]]:
    """Score every candidate on cheap fields already in the raw TMDb result.

    - genre score: sum of the user's affinity for each genre the candidate
      shares -> a movie sharing TWO of the user's favorite genres outscores a
      movie sharing just one (the "multiple genre weighting" from the spec).
    - quality score: vote_average, gated by MIN_VOTE_COUNT so half-voted
      entries can't float to the top (the "rating filter").
    - popularity score: TMDb popularity normalized with a soft cap.
    - similarity score: fraction of seed movies this candidate is "similar to".

    Candidates below MIN_VOTE_COUNT are dropped here, which doubles as the
    low-quality / borderline-data edge-case filter.
    """
    scored: list[tuple[float, dict]] = []
    for mid, movie in candidates.items():
        if movie.get("vote_count", 0) < MIN_VOTE_COUNT:
            continue  # too little community signal to trust the ranking

        genre_score = sum(affinity.get(g, 0.0) for g in movie.get("genre_ids", []))
        quality_score = movie.get("vote_average", 0) / 10
        popularity_score = min(movie.get("popularity", 0) / 100.0, 1.0)
        similarity_score = min(affinity_counts[mid] / float(seed_volume or 1), 1.0)

        total = (
            SCORE_WEIGHTS["genre"] * genre_score
            + SCORE_WEIGHTS["quality"] * quality_score
            + SCORE_WEIGHTS["popularity"] * popularity_score
            + SCORE_WEIGHTS["similarity"] * similarity_score
        )
        movie["_rec_score"] = total
        scored.append((total, movie))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return scored


async def _rerank_with_creators(
    scored: list[tuple[float, dict]],
    creator_affinity: dict,
    rerank_k: int,
) -> None:
    """Re-rank the top candidates using director / cast overlap.

    The cheap scoring pass cannot see credits, so we fetch full details for
    just the top `rerank_k` candidates concurrently and add a creator bonus:
    +0.15 for the same director as a favorite, +0.05 per shared top-billed
    actor (capped at 3). This is the "beyond genre" quality refinement the
    spec asks for, and capping at RERANK_TOP_K keeps TMDb fan-out bounded.
    """
    top = scored[:rerank_k]
    if not top:
        return
    if not creator_affinity["directors"] and not creator_affinity["cast"]:
        return  # nothing to compare against, skip the extra fan-out

    details_list = await asyncio.gather(
        *(_safe_movie_details(int(movie["id"])) for _, movie in top),
        return_exceptions=True,
    )

    for (_, movie), details in zip(top, details_list):
        if not details:
            continue
        credits = details.get("credits", {})
        bonus = 0.0
        director_id = next(
            (c["id"] for c in credits.get("crew", []) if c.get("job") == "Director"),
            None,
        )
        if director_id and creator_affinity["directors"].get(director_id):
            bonus += 0.15
        cast_ids = {c["id"] for c in credits.get("cast", [])[:10]}
        shared = len(cast_ids & set(creator_affinity["cast"].keys()))
        bonus += min(shared, 3) * 0.05
        movie["_rec_score"] = movie["_rec_score"] + bonus

    # The tuple key is now stale; re-sort by the updated in-movie score.
    scored.sort(key=lambda pair: pair[1]["_rec_score"], reverse=True)


def _diversity_bucket(movie: dict, affinity: dict[int, float]) -> int | None:
    """Which genre does this movie represent for the diversity cap?

    We bucket by the genre where the user's affinity is STRONGEST, so a movie
    that shares the user's top genre and an obscure side genre still counts
    against the dominant family that would otherwise flood the page.
    """
    genre_ids = movie.get("genre_ids", [])
    if not genre_ids:
        return None
    return max(genre_ids, key=lambda g: affinity.get(g, 0.0))


def _select_with_diversity(
    scored: list[tuple[float, dict]],
    limit: int,
    affinity: dict[int, float],
    cap_ratio: float = DIVERSITY_CAP_RATIO,
) -> list[dict]:
    """Pick the final list while enforcing a per-genre cap (diversity).

    Walk the scored candidates high-to-low and admit each one unless its genre
    bucket already holds `cap` spots. With the default ratio (0.4) a 20-movie
    page can show at most 40% from the same genre family, guaranteeing the
    user isn't served a wall of the same genre even if they love only one.

    `cap_ratio` is passed through by callers: the post-rating flow passes 1.0
    because THAT requirement is "same genre as the rated movie", not variety -
    within a genre its members are still differentiated by quality, popularity
    and creator overlap.
    """
    cap = max(1, round(limit * cap_ratio))
    used: Counter = Counter()
    picked: list[dict] = []
    for _, movie in scored:
        bucket = _diversity_bucket(movie, affinity)
        if bucket is not None and used[bucket] >= cap:
            continue
        picked.append(movie)
        if bucket is not None:
            used[bucket] += 1
        if len(picked) >= limit:
            break
    return picked


async def _popular_fallback(
    user_seen: set,
    needed: int,
    preferred_genres: set[int] | None = None,
    excluded_genres: set[int] | None = None,
) -> list[dict]:
    """Cold-start / shortfall filler: quality-filtered popular movies the user
    has never favorited, rated, or watchlisted.

    When `preferred_genres` is given, same-genre popular movies are consumed
    first and the pool is only widened (graceful fallback) once that well runs
    dry, so we stay on-theme without ever under-delivering. When
    `excluded_genres` is given (genres that already hit the diversity cap),
    those movies are skipped so the fallback can't undo the diversity work.
    """
    try:
        data = await tmdb.get_popular()
        results = data.get("results", [])
    except Exception:
        return []

    preferred = set(preferred_genres or [])
    excluded = set(excluded_genres or [])

    def allowed(movie: dict) -> bool:
        movie_genres = set(movie.get("genre_ids", []))
        return not (excluded and (movie_genres & excluded))

    pools = [results]
    if preferred:
        pools.insert(0, [m for m in results if preferred & set(m.get("genre_ids", []))])

    filled: list[dict] = []
    added: set[int] = set()
    for movie in (m for pool in pools for m in pool):
        mid = movie["id"]
        if mid in user_seen or mid in added:
            continue
        if not allowed(movie):
            continue
        if movie.get("vote_count", 0) < MIN_VOTE_COUNT:
            continue
        added.add(mid)
        filled.append(movie)
        if len(filled) >= needed:
            break
    return filled


def _saturated_genres(
    picked: list[dict],
    limit: int,
    affinity: dict[int, float],
    cap_ratio: float = DIVERSITY_CAP_RATIO,
) -> set[int]:
    """Which genres already filled their diversity quota in `picked`?

    Used to tell the fallback filler which genres to avoid, so topping the list
    up never re-creates the single-genre wall the diversity cap was meant to
    break up. Must stay in sync with the cap_ratio used by _select_with_diversity.
    """
    cap = max(1, round(limit * cap_ratio))
    counts: Counter = Counter(_diversity_bucket(m, affinity) for m in picked)
    return {g for g, n in counts.items() if g is not None and n >= cap}


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------

async def get_recommendations(db: Session, user_id: int, limit: int = 20) -> list[dict]:
    """Top-level "For You" entry point. Returns up to `limit` movie dicts."""
    favorites = list_favorites(db, user_id)
    ratings = list_ratings(db, user_id)
    watchlist = list_watchlist(db, user_id)

    # Everything the user has already favorited / rated / watchlisted is off
    # the table - this is the dedup rule that keeps the page fresh.
    seen: set[int] = set()
    seen.update(f.tmdb_movie_id for f in favorites)
    seen.update(r.tmdb_movie_id for r in ratings)
    seen.update(w.tmdb_movie_id for w in watchlist)

    ratings_map = {r.tmdb_movie_id: r.score for r in ratings}

    # Seeds: favorites first (strongest signal), then highly-rated movies
    # (>= 7) that are not already seeded. Capped to bound TMDb fan-out.
    seed_ids = [f.tmdb_movie_id for f in favorites]
    seed_ids += [
        r.tmdb_movie_id for r in ratings if r.score >= 7 and r.tmdb_movie_id not in seen
    ]
    seed_ids = list(dict.fromkeys(seed_ids))[:MAX_SEED_MOVIES]

    # Cold start (no favorites and no high ratings yet) -> popular list only.
    if not seed_ids:
        return await _popular_fallback(seen, limit)

    # Fetch seed details concurrently; a failing seed is skipped, not fatal.
    seed_details = [
        d for d in await asyncio.gather(*(_safe_movie_details(i) for i in seed_ids)) if d
    ]

    affinity = _build_genre_affinity(seed_details, ratings_map)
    creator_affinity = _build_creator_affinity(seed_details)

    # Explore the user's strongest genres to keep the page from going stale.
    top_genres = sorted(
        affinity, key=affinity.get, reverse=True
    )[:TOP_GENRES_FOR_DISCOVERY]

    candidates: dict[int, dict] = {}
    affinity_counts: Counter = Counter()

    _collect_similar_candidates(seed_details, seen, candidates, affinity_counts)
    await _collect_genre_discovery(top_genres, seen, candidates)

    # Edge case: favorites exist but nothing matched -> graceful fallback,
    # still biased toward the genres we did manage to learn about.
    if not candidates:
        return await _popular_fallback(seen, limit, set(top_genres))

    scored = _score_candidates(candidates, affinity, affinity_counts, len(seed_details))
    await _rerank_with_creators(scored, creator_affinity, RERANK_TOP_K)

    picked = _select_with_diversity(scored, limit, affinity)

    # Still short (diversity cap or thin matches) -> top up with the popular
    # list, avoiding the genres that already filled their diversity quota.
    if len(picked) < limit:
        picked_ids = {m["id"] for m in picked}
        filler = await _popular_fallback(
            seen | picked_ids,
            limit - len(picked),
            set(top_genres),
            _saturated_genres(picked, limit, affinity),
        )
        picked.extend(filler)

    return picked


async def get_rating_recommendations(
    db: Session,
    user_id: int,
    tmdb_movie_id: int,
    score: float,
) -> list[dict]:
    """Post-rating recommendations.

    Count rules (kept in ONE place so the threshold stays consistent no matter
    who calls it):
      - rating  > RATING_THRESHOLD (5.0) -> HIGH_SCORE_RECOMMEND_COUNT (5) movies
      - rating <= RATING_THRESHOLD (5.0) -> LOW_SCORE_RECOMMEND_COUNT (2) movies
    Candidates are pulled from the rated movie's own genre family (the
    "same genre" rule), the returned list is variable-length by design so a
    fixed UI can render 5 or 2 without special-casing, and the list is topped
    up from a quality-filtered popular list whenever the same-genre well runs
    dry (fallback behavior).
    """
    need = HIGH_SCORE_RECOMMEND_COUNT if score > RATING_THRESHOLD else LOW_SCORE_RECOMMEND_COUNT

    favorites = list_favorites(db, user_id)
    ratings = list_ratings(db, user_id)
    watchlist = list_watchlist(db, user_id)
    ratings_map = {r.tmdb_movie_id: r.score for r in ratings}

    # Dedup: never re-recommend something the user already interacted with.
    seen: set[int] = set()
    seen.update(f.tmdb_movie_id for f in favorites)
    seen.update(r.tmdb_movie_id for r in ratings)
    seen.update(w.tmdb_movie_id for w in watchlist)
    seen.add(tmdb_movie_id)

    details = await _safe_movie_details(tmdb_movie_id)
    if not details:
        return await _popular_fallback(seen, need)

    rated_genres = {g["id"] for g in details.get("genres", [])}
    if not rated_genres:
        # Rare: a movie with no genres in TMDb's data.
        return await _popular_fallback(seen, need)

    # Seeds: the rated movie itself plus the user's OTHER well-liked favorites
    # (rated >= 7), so the profile stays personal and rating-aware while the
    # candidate gate below keeps everything on the rated movie's genre.
    liked_favorites = [
        f.tmdb_movie_id for f in favorites if ratings_map.get(f.tmdb_movie_id, 0) >= 7
    ]
    seed_ids = list(dict.fromkeys([tmdb_movie_id] + liked_favorites))[:MAX_SEED_MOVIES]
    seed_details = [
        d for d in await asyncio.gather(*(_safe_movie_details(i) for i in seed_ids)) if d
    ]

    affinity = _build_genre_affinity(seed_details, ratings_map)
    creator_affinity = _build_creator_affinity(seed_details)

    candidates: dict[int, dict] = {}
    affinity_counts: Counter = Counter()

    # Channel 1: movies similar to the rated movie (and other liked favorites).
    _collect_similar_candidates(seed_details, seen, candidates, affinity_counts)
    # Channel 2: what's popular right now inside the rated movie's genres.
    await _collect_genre_discovery(sorted(rated_genres), seen, candidates)

    # Same-genre gate: only keep candidates sharing a genre with the rated
    # movie, so even though scoring uses a broader profile the final list stays
    # on-theme.
    candidates = {
        mid: movie
        for mid, movie in candidates.items()
        if rated_genres & set(movie.get("genre_ids", []))
    }

    if not candidates:
        # Fallback: nothing unused matched the rated genres -> clean popular
        # list, still preferring the rated movie's genres when possible.
        return await _popular_fallback(seen, need, rated_genres)

    scored = _score_candidates(candidates, affinity, affinity_counts, len(seed_details))
    await _rerank_with_creators(scored, creator_affinity, RERANK_TOP_K)
    # No per-genre diversity cap here: the contract for post-rating recs is
    # "same genre as the rated movie", so the whole list may legitimately come
    # from that one genre (differentiated by quality/creator overlap instead).
    picked = _select_with_diversity(scored, need, affinity, cap_ratio=1.0)

    # Fallback: diversity cap / thin matches -> top up, never under-deliver,
    # but don't let the filler re-saturate a genre that already hit its cap.
    if len(picked) < need:
        picked_ids = {m["id"] for m in picked}
        filler = await _popular_fallback(
            seen | picked_ids,
            need - len(picked),
            rated_genres,
            _saturated_genres(picked, need, affinity, cap_ratio=1.0),
        )
        picked.extend(filler)

    return picked[:need]
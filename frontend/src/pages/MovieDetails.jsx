import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import * as movieService from "../services/movieService";
import * as userService from "../services/userService";
import { useAuth } from "../context/AuthContext";
import MovieCarousel from "../components/MovieCarousel";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage, { getErrorMessage } from "../components/ErrorMessage";

const IMAGE_BASE = "https://image.tmdb.org/t/p/w500";
const BACKDROP_BASE = "https://image.tmdb.org/t/p/original";

export default function MovieDetails() {
  const { id } = useParams();
  const { user } = useAuth();
  const [movie, setMovie] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionError, setActionError] = useState(null);
  const [isFavorite, setIsFavorite] = useState(false);
  const [isInWatchlist, setIsInWatchlist] = useState(false);
  const [myRating, setMyRating] = useState(0);
  const [reviews, setReviews] = useState([]);
  const [reviewText, setReviewText] = useState("");

  useEffect(() => {
    setLoading(true);
    setError(null);
    setReviews([]);
    setMyRating(0);
    setIsFavorite(false);
    setIsInWatchlist(false);
    movieService
      .getMovieDetails(id)
      .then((res) => setMovie(res.data))
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));

    userService
      .getMovieReviews(id)
      .then((res) => setReviews(res.data))
      .catch(() => {});

    if (user) {
      userService.getFavorites().then((res) => setIsFavorite(res.data.some((f) => f.tmdb_movie_id === Number(id)))).catch(() => {});
      userService.getWatchlist().then((res) => setIsInWatchlist(res.data.some((w) => w.tmdb_movie_id === Number(id)))).catch(() => {});
      userService.getMyRatings().then((res) => {
        const existing = res.data.find((r) => r.tmdb_movie_id === Number(id));
        if (existing) setMyRating(existing.score);
      }).catch(() => {});
    }
  }, [id, user]);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} />;

  const trailer = movie.videos?.results?.find((v) => v.type === "Trailer" && v.site === "YouTube");
  const cast = movie.credits?.cast?.slice(0, 10) || [];
  const director = movie.credits?.crew?.find((c) => c.job === "Director");
  const similar = movie.similar?.results?.slice(0, 10) || [];

  const movieRef = { tmdb_movie_id: movie.id, title: movie.title, poster_path: movie.poster_path };

  const runAction = async (action) => {
    setActionError(null);
    try {
      await action();
    } catch (err) {
      setActionError(getErrorMessage(err));
    }
  };

  const toggleFavorite = () =>
    runAction(async () => {
      if (isFavorite) {
        await userService.removeFavorite(movie.id);
      } else {
        await userService.addFavorite(movieRef);
      }
      setIsFavorite(!isFavorite);
    });

  const toggleWatchlist = () =>
    runAction(async () => {
      if (isInWatchlist) {
        await userService.removeFromWatchlist(movie.id);
      } else {
        await userService.addToWatchlist(movieRef);
      }
      setIsInWatchlist(!isInWatchlist);
    });

  const submitRating = (score) =>
    runAction(async () => {
      await userService.rateMovie(movie.id, score);
      setMyRating(score);
    });

  const submitReview = async (e) => {
    e.preventDefault();
    if (!reviewText.trim()) return;
    setActionError(null);
    try {
      const res = await userService.writeReview(movie.id, reviewText.trim());
      setReviews([res.data, ...reviews]);
      setReviewText("");
    } catch (err) {
      setActionError(getErrorMessage(err));
    }
  };

  return (
    <div>
      <div
        className="w-full h-[400px] bg-cover bg-center relative"
        style={{ backgroundImage: movie.backdrop_path ? `url(${BACKDROP_BASE}${movie.backdrop_path})` : "none" }}
      >
        <div className="absolute inset-0 bg-gradient-to-t from-base via-base/70 to-base/30" />
      </div>

      <div className="max-w-7xl mx-auto px-6 -mt-40 relative flex flex-col md:flex-row gap-8">
        <img
          src={movie.poster_path ? `${IMAGE_BASE}${movie.poster_path}` : "https://placehold.co/500x750/16161d/666?text=No+Poster"}
          alt={movie.title}
          className="w-48 rounded-lg shadow-2xl flex-shrink-0"
        />

        <div className="flex-1 pt-4">
          <h1 className="text-3xl font-bold">{movie.title}</h1>
          <p className="text-gray-400 mt-2 text-sm">
            {movie.release_date?.slice(0, 4)} • {movie.runtime} min
            {director && <> • Directed by {director.name}</>}
          </p>
          <div className="flex gap-2 mt-3">
            {movie.genres?.map((g) => (
              <span key={g.id} className="text-xs bg-surface px-3 py-1 rounded-full">{g.name}</span>
            ))}
          </div>

          <p className="mt-4 text-gray-300 max-w-2xl leading-relaxed">{movie.overview}</p>

          {user && (
            <div className="flex flex-wrap items-center gap-3 mt-6">
              <button
                type="button"
                onClick={toggleFavorite}
                className={`px-4 py-2 rounded-full text-sm font-semibold transition-colors ${isFavorite ? "bg-accent text-base" : "bg-surface hover:bg-white/10"}`}
              >
                {isFavorite ? "★ Favorited" : "☆ Add to Favorites"}
              </button>
              <button
                type="button"
                onClick={toggleWatchlist}
                className={`px-4 py-2 rounded-full text-sm font-semibold transition-colors ${isInWatchlist ? "bg-accent text-base" : "bg-surface hover:bg-white/10"}`}
              >
                {isInWatchlist ? "✓ In Watchlist" : "+ Add to Watchlist"}
              </button>
              <div className="flex items-center gap-1 ml-2">
                {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
                  <button
                    type="button"
                    key={n}
                    onClick={() => submitRating(n)}
                    className={`w-6 h-6 text-xs rounded ${n <= myRating ? "bg-accent text-base font-semibold" : "bg-surface hover:bg-white/10"}`}
                  >
                    {n}
                  </button>
                ))}
              </div>
            </div>
          )}
          {actionError && <p className="mt-4 text-red-400 text-sm">{actionError}</p>}
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 mt-12">
        {trailer && (
          <section className="mb-10">
            <h2 className="text-xl font-semibold mb-4">Trailer</h2>
            <div className="aspect-video max-w-3xl">
              <iframe
                className="w-full h-full rounded-lg"
                src={`https://www.youtube.com/embed/${trailer.key}`}
                title="Trailer"
                allowFullScreen
              />
            </div>
          </section>
        )}

        {cast.length > 0 && (
          <section className="mb-10">
            <h2 className="text-xl font-semibold mb-4">Cast</h2>
            <div className="flex gap-4 overflow-x-auto pb-2">
              {cast.map((actor) => (
                <div key={actor.id} className="w-28 flex-shrink-0 text-center">
                  <img
                    src={actor.profile_path ? `${IMAGE_BASE}${actor.profile_path}` : "https://placehold.co/200x300/16161d/666?text=?"}
                    alt={actor.name}
                    className="rounded-lg aspect-[2/3] object-cover mb-1"
                  />
                  <p className="text-xs font-medium">{actor.name}</p>
                  <p className="text-xs text-gray-500">{actor.character}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        <section className="mb-10 max-w-2xl">
          <h2 className="text-xl font-semibold mb-4">Reviews</h2>
          {user && (
            <form onSubmit={submitReview} className="mb-6 flex gap-2">
              <input
                value={reviewText}
                onChange={(e) => setReviewText(e.target.value)}
                placeholder="Write a review..."
                className="flex-1 bg-surface border border-white/10 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-accent"
              />
              <button type="submit" className="bg-accent text-base px-4 py-2 rounded-lg text-sm font-semibold hover:bg-accent-dark transition-colors">
                Post
              </button>
            </form>
          )}
          {reviews.length === 0 ? (
            <p className="text-gray-500 text-sm">No reviews yet.</p>
          ) : (
            <div className="space-y-3">
              {reviews.map((r) => (
                <p key={r.id} className="bg-surface rounded-lg p-3 text-sm text-gray-300">{r.content}</p>
              ))}
            </div>
          )}
        </section>

        <MovieCarousel title="Similar Movies" movies={similar} />
      </div>
    </div>
  );
}
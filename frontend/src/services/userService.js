import api from "./api";

// Favorites
export const getFavorites = () => api.get("/api/favorites");
export const addFavorite = (movie) => api.post("/api/favorites", movie);
export const removeFavorite = (tmdbMovieId) =>
  api.delete(`/api/favorites/${tmdbMovieId}`);

// Watchlist
export const getWatchlist = () => api.get("/api/watchlist");
export const addToWatchlist = (movie) => api.post("/api/watchlist", movie);
export const removeFromWatchlist = (tmdbMovieId) =>
  api.delete(`/api/watchlist/${tmdbMovieId}`);

// Ratings
export const getMyRatings = () => api.get("/api/ratings");
export const rateMovie = (tmdbMovieId, score) =>
  api.post("/api/ratings", { tmdb_movie_id: tmdbMovieId, score });

// Reviews
export const getMovieReviews = (tmdbMovieId) =>
  api.get(`/api/reviews/movie/${tmdbMovieId}`);
export const getMyReviews = () => api.get("/api/reviews/me");
export const writeReview = (tmdbMovieId, content) =>
  api.post("/api/reviews", { tmdb_movie_id: tmdbMovieId, content });

// Search history
export const getSearchHistory = () => api.get("/api/search-history");

// Recommendations
export const getRecommendations = () => api.get("/api/recommendations");

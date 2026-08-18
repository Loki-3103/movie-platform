import api from "./api";

export const searchMovies = (query, page = 1) =>
  api.get("/api/movies/search", { params: { q: query, page } });

export const getPopular = (page = 1) =>
  api.get("/api/movies/popular", { params: { page } });

export const getTrending = (timeWindow = "week") =>
  api.get("/api/movies/trending", { params: { time_window: timeWindow } });

export const getTopRated = (page = 1) =>
  api.get("/api/movies/top-rated", { params: { page } });

export const getUpcoming = (page = 1) =>
  api.get("/api/movies/upcoming", { params: { page } });

export const getMovieDetails = (movieId) => api.get(`/api/movies/${movieId}`);

import { useEffect, useState } from "react";
import * as userService from "../services/userService";
import MovieGrid from "../components/MovieGrid";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage, { getErrorMessage } from "../components/ErrorMessage";

export default function Recommendations() {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = () => {
    setLoading(true);
    setError(null);
    userService
      .getRecommendations()
      .then((res) => setMovies(res.data))
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  return (
    <div className="max-w-7xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-bold mb-2">Recommended For You</h1>
      <p className="text-gray-400 text-sm mb-6">
        Based on your favorites, ratings, and viewing patterns.
      </p>
      {loading ? (
        <LoadingSpinner />
      ) : error ? (
        <ErrorMessage message={error} onRetry={load} />
      ) : (
        <MovieGrid movies={movies} emptyMessage="Rate or favorite a few movies to get personalized recommendations." />
      )}
    </div>
  );
}

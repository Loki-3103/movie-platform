import { useEffect, useState } from "react";
import * as userService from "../services/userService";
import MovieGrid from "../components/MovieGrid";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage, { getErrorMessage } from "../components/ErrorMessage";

export default function Favorites() {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = () => {
    setLoading(true);
    setError(null);
    userService
      .getFavorites()
      .then((res) => setFavorites(res.data))
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  return (
    <div className="max-w-7xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-bold mb-6">My Favorites</h1>
      {loading ? (
        <LoadingSpinner />
      ) : error ? (
        <ErrorMessage message={error} onRetry={load} />
      ) : (
        <MovieGrid movies={favorites} emptyMessage="You haven't favorited any movies yet." />
      )}
    </div>
  );
}

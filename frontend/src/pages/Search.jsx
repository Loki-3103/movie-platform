import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import * as movieService from "../services/movieService";
import MovieGrid from "../components/MovieGrid";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage, { getErrorMessage } from "../components/ErrorMessage";
import SearchBar from "../components/SearchBar";

export default function Search() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get("q") || "";
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!query) return;
    setLoading(true);
    setError(null);
    movieService
      .searchMovies(query)
      .then((res) => setResults(res.data.results))
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  }, [query]);

  return (
    <div className="max-w-7xl mx-auto px-6 py-10">
      <div className="mb-8">
        <SearchBar initialValue={query} />
      </div>

      {query && <h2 className="text-lg text-gray-400 mb-6">Results for "{query}"</h2>}

      {loading ? (
        <LoadingSpinner />
      ) : error ? (
        <ErrorMessage message={error} />
      ) : (
        <MovieGrid movies={results} emptyMessage="No results. Try another search." />
      )}
    </div>
  );
}
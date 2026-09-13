import { useEffect, useState } from "react";
import * as movieService from "../services/movieService";
import MovieCarousel from "../components/MovieCarousel";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage, { getErrorMessage } from "../components/ErrorMessage";
import SearchBar from "../components/SearchBar";

export default function Home() {
  const [data, setData] = useState({ trending: [], popular: [], topRated: [], upcoming: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    Promise.allSettled([
      movieService.getTrending(),
      movieService.getPopular(),
      movieService.getTopRated(),
      movieService.getUpcoming(),
    ]).then((results) => {
      const keys = ["trending", "popular", "topRated", "upcoming"];
      const next = { trending: [], popular: [], topRated: [], upcoming: [] };
      const failed = [];
      results.forEach((result, i) => {
        if (result.status === "fulfilled") {
          next[keys[i]] = result.value.data.results;
        } else {
          failed.push(result.reason);
        }
      });
      setData(next);
      if (failed.length === results.length) {
        setError(getErrorMessage(failed[0]));
      }
      setLoading(false);
    });
  }, []);

  return (
    <div>
      <div className="flex flex-col items-center text-center py-16 px-6">
        <h1 className="text-4xl font-bold mb-3">Discover your next favorite film</h1>
        <p className="text-gray-400 mb-8">Search, track, and get recommendations tailored to you.</p>
        <SearchBar />
      </div>

      <div className="max-w-7xl mx-auto px-6 pb-16">
        {loading ? (
          <LoadingSpinner />
        ) : error ? (
          <ErrorMessage message={error} />
        ) : (
          <>
            <MovieCarousel title="Trending This Week" movies={data.trending} />
            <MovieCarousel title="Popular" movies={data.popular} />
            <MovieCarousel title="Top Rated" movies={data.topRated} />
            <MovieCarousel title="Upcoming" movies={data.upcoming} />
          </>
        )}
      </div>
    </div>
  );
}
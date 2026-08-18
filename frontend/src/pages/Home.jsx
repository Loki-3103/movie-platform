import { useEffect, useState } from "react";
import * as movieService from "../services/movieService";
import MovieCarousel from "../components/MovieCarousel";
import LoadingSpinner from "../components/LoadingSpinner";
import SearchBar from "../components/SearchBar";

export default function Home() {
  const [data, setData] = useState({ trending: [], popular: [], topRated: [], upcoming: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      movieService.getTrending(),
      movieService.getPopular(),
      movieService.getTopRated(),
      movieService.getUpcoming(),
    ])
      .then(([trending, popular, topRated, upcoming]) => {
        setData({
          trending: trending.data.results,
          popular: popular.data.results,
          topRated: topRated.data.results,
          upcoming: upcoming.data.results,
        });
      })
      .finally(() => setLoading(false));
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

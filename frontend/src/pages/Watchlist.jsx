import { useEffect, useState } from "react";
import * as userService from "../services/userService";
import MovieGrid from "../components/MovieGrid";
import LoadingSpinner from "../components/LoadingSpinner";

export default function Watchlist() {
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    userService.getWatchlist().then((res) => setWatchlist(res.data)).finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-bold mb-6">My Watchlist</h1>
      {loading ? <LoadingSpinner /> : <MovieGrid movies={watchlist} emptyMessage="Your watchlist is empty." />}
    </div>
  );
}

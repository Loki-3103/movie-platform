import { useEffect, useState } from "react";
import * as userService from "../services/userService";
import MovieGrid from "../components/MovieGrid";
import LoadingSpinner from "../components/LoadingSpinner";

export default function Favorites() {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    userService.getFavorites().then((res) => setFavorites(res.data)).finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-bold mb-6">My Favorites</h1>
      {loading ? <LoadingSpinner /> : <MovieGrid movies={favorites} emptyMessage="You haven't favorited any movies yet." />}
    </div>
  );
}

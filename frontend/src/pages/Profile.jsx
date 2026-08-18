import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import * as userService from "../services/userService";

export default function Profile() {
  const { user } = useAuth();
  const [stats, setStats] = useState({ favorites: 0, watchlist: 0, ratings: 0, reviews: 0 });

  useEffect(() => {
    Promise.all([
      userService.getFavorites(),
      userService.getWatchlist(),
      userService.getMyRatings(),
      userService.getMyReviews(),
    ]).then(([fav, watch, ratings, reviews]) => {
      setStats({
        favorites: fav.data.length,
        watchlist: watch.data.length,
        ratings: ratings.data.length,
        reviews: reviews.data.length,
      });
    });
  }, []);

  if (!user) return null;

  return (
    <div className="max-w-2xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-bold mb-1">{user.username}</h1>
      <p className="text-gray-400 mb-8">{user.email}</p>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <StatCard label="Favorites" value={stats.favorites} />
        <StatCard label="Watchlist" value={stats.watchlist} />
        <StatCard label="Ratings" value={stats.ratings} />
        <StatCard label="Reviews" value={stats.reviews} />
      </div>
    </div>
  );
}

function StatCard({ label, value }) {
  return (
    <div className="bg-surface rounded-lg p-4 text-center">
      <p className="text-2xl font-bold text-accent">{value}</p>
      <p className="text-xs text-gray-400 mt-1">{label}</p>
    </div>
  );
}

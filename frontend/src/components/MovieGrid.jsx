import MovieCard from "./MovieCard";

export default function MovieGrid({ movies, emptyMessage = "No movies found." }) {
  if (!movies || movies.length === 0) {
    return <p className="text-gray-400 text-center py-16">{emptyMessage}</p>;
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
      {movies.map((movie) => (
        <MovieCard key={movie.id ?? movie.tmdb_movie_id} movie={normalize(movie)} />
      ))}
    </div>
  );
}

// Our stored records (favorites/watchlist) use tmdb_movie_id/title/poster_path,
// while TMDb responses use id/title/poster_path/vote_average. This normalizes
// both shapes so MovieCard doesn't need to know which one it's rendering.
function normalize(movie) {
  if (movie.tmdb_movie_id) {
    return { id: movie.tmdb_movie_id, title: movie.title, poster_path: movie.poster_path, vote_average: 0 };
  }
  return movie;
}

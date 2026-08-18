import { Link } from "react-router-dom";

const IMAGE_BASE = "https://image.tmdb.org/t/p/w500";

export default function MovieCard({ movie }) {
  const posterUrl = movie.poster_path
    ? `${IMAGE_BASE}${movie.poster_path}`
    : "https://placehold.co/500x750/16161d/666?text=No+Poster";

  return (
    <Link
      to={`/movie/${movie.id}`}
      className="group relative rounded-lg overflow-hidden bg-surface shadow-lg transition-transform hover:scale-[1.03]"
    >
      <img src={posterUrl} alt={movie.title} className="w-full aspect-[2/3] object-cover" />
      <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex flex-col justify-end p-3">
        <p className="font-semibold text-sm line-clamp-2">{movie.title}</p>
        {movie.vote_average > 0 && (
          <p className="text-xs text-accent mt-1">★ {movie.vote_average.toFixed(1)}</p>
        )}
      </div>
    </Link>
  );
}

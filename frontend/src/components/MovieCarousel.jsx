import MovieCard from "./MovieCard";

export default function MovieCarousel({ title, movies }) {
  if (!movies || movies.length === 0) return null;

  return (
    <section className="mb-10">
      <h2 className="text-xl font-semibold mb-4">{title}</h2>
      <div className="flex gap-4 overflow-x-auto pb-2 -mx-6 px-6 scrollbar-thin">
        {movies.map((movie) => (
          <div key={movie.id} className="w-40 flex-shrink-0">
            <MovieCard movie={movie} />
          </div>
        ))}
      </div>
    </section>
  );
}

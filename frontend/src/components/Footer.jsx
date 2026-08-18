export default function Footer() {
  return (
    <footer className="border-t border-white/5 mt-20 py-8 text-center text-sm text-gray-500">
      <p>
        ReelFind - movie data powered by{" "}
        <a href="https://www.themoviedb.org/" target="_blank" rel="noreferrer" className="hover:text-accent">
          TMDb
        </a>
      </p>
    </footer>
  );
}

import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function SearchBar({ initialValue = "" }) {
  const [query, setQuery] = useState(initialValue);
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/search?q=${encodeURIComponent(query.trim())}`);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-xl">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search for a movie..."
        className="w-full bg-surface border border-white/10 rounded-full px-5 py-3 text-sm focus:outline-none focus:border-accent transition-colors"
      />
    </form>
  );
}

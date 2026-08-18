import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <nav className="sticky top-0 z-50 bg-surface/80 backdrop-blur border-b border-white/5">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link to="/" className="text-xl font-bold tracking-tight">
          Reel<span className="text-accent">Find</span>
        </Link>

        <div className="flex items-center gap-6 text-sm">
          <Link to="/search" className="hover:text-accent transition-colors">Search</Link>
          {user && (
            <>
              <Link to="/watchlist" className="hover:text-accent transition-colors">Watchlist</Link>
              <Link to="/favorites" className="hover:text-accent transition-colors">Favorites</Link>
              <Link to="/recommendations" className="hover:text-accent transition-colors">For You</Link>
              <Link to="/profile" className="hover:text-accent transition-colors">Profile</Link>
              {user.is_admin && (
                <Link to="/admin" className="hover:text-accent transition-colors">Admin</Link>
              )}
              <button onClick={handleLogout} className="text-gray-400 hover:text-white transition-colors">
                Logout
              </button>
            </>
          )}
          {!user && (
            <>
              <Link to="/login" className="hover:text-accent transition-colors">Login</Link>
              <Link
                to="/register"
                className="bg-accent text-base font-semibold px-4 py-1.5 rounded-full hover:bg-accent-dark transition-colors"
              >
                Sign Up
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}

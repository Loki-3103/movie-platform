import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

export default function Settings() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  if (!user) return null;

  return (
    <div className="max-w-lg mx-auto px-6 py-10">
      <h1 className="text-2xl font-bold mb-6">Settings</h1>

      <div className="bg-surface rounded-lg p-5 space-y-3 mb-6">
        <div>
          <p className="text-xs text-gray-500">Username</p>
          <p>{user.username}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Email</p>
          <p>{user.email}</p>
        </div>
      </div>

      <button
        onClick={handleLogout}
        className="bg-surface hover:bg-white/10 px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors"
      >
        Log Out
      </button>
    </div>
  );
}

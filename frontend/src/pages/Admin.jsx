import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import * as adminService from "../services/adminService";
import LoadingSpinner from "../components/LoadingSpinner";

export default function Admin() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user?.is_admin) return;
    Promise.all([adminService.getStats(), adminService.getAllUsers()]).then(
      ([statsRes, usersRes]) => {
        setStats(statsRes.data);
        setUsers(usersRes.data);
      }
    ).finally(() => setLoading(false));
  }, [user]);

  // Backend enforces this too (403 on /api/admin/*) - this is just UI convenience.
  if (!user?.is_admin) return <Navigate to="/" replace />;

  const handleDelete = async (userId) => {
    if (!confirm("Delete this user and all their data?")) return;
    await adminService.deleteUser(userId);
    setUsers(users.filter((u) => u.id !== userId));
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-bold mb-6">Admin Panel</h1>

      <div className="grid grid-cols-2 sm:grid-cols-5 gap-4 mb-10">
        <StatCard label="Users" value={stats.total_users} />
        <StatCard label="Favorites" value={stats.total_favorites} />
        <StatCard label="Watchlist Items" value={stats.total_watchlist_items} />
        <StatCard label="Ratings" value={stats.total_ratings} />
        <StatCard label="Reviews" value={stats.total_reviews} />
      </div>

      <h2 className="text-lg font-semibold mb-4">Users</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-muted border-b border-border">
              <th className="py-2 pr-4">Username</th>
              <th className="py-2 pr-4">Email</th>
              <th className="py-2 pr-4">Joined</th>
              <th className="py-2 pr-4">Role</th>
              <th className="py-2"></th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className="border-b border-border/50">
                <td className="py-2 pr-4">{u.username}</td>
                <td className="py-2 pr-4 text-muted">{u.email}</td>
                <td className="py-2 pr-4 text-muted">{new Date(u.created_at).toLocaleDateString()}</td>
                <td className="py-2 pr-4">{u.is_admin ? "Admin" : "User"}</td>
                <td className="py-2">
                  {!u.is_admin && (
                    <button onClick={() => handleDelete(u.id)} className="text-danger hover:underline">
                      Delete
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function StatCard({ label, value }) {
  return (
    <div className="bg-surface rounded-lg p-4 text-center">
      <p className="text-2xl font-bold text-accent">{value}</p>
      <p className="text-xs text-muted mt-1">{label}</p>
    </div>
  );
}

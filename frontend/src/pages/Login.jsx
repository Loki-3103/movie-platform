import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await login(email, password);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed");
    }
  };

  return (
    <div className="max-w-sm mx-auto mt-20 px-6">
      <h1 className="text-2xl font-bold mb-6">Log In</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full bg-surface border border-white/10 rounded-lg px-4 py-2.5 focus:outline-none focus:border-accent"
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full bg-surface border border-white/10 rounded-lg px-4 py-2.5 focus:outline-none focus:border-accent"
          required
        />
        {error && <p className="text-accent text-sm">{error}</p>}
        <button type="submit" className="w-full bg-accent text-base py-2.5 rounded-lg font-semibold hover:bg-accent-dark transition-colors">
          Log In
        </button>
      </form>
      <p className="text-sm text-gray-400 mt-4">
        No account? <Link to="/register" className="text-accent hover:underline">Sign up</Link>
      </p>
    </div>
  );
}

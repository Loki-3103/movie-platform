import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await register(username, email, password);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed");
    }
  };

  return (
    <div className="max-w-sm mx-auto mt-20 px-6">
      <h1 className="text-2xl font-bold mb-6">Create Account</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full bg-surface border border-white/10 rounded-lg px-4 py-2.5 focus:outline-none focus:border-accent"
          required
        />
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
          minLength={8}
        />
        {error && <p className="text-accent text-sm">{error}</p>}
        <button type="submit" className="w-full bg-accent text-base py-2.5 rounded-lg font-semibold hover:bg-accent-dark transition-colors">
          Sign Up
        </button>
      </form>
      <p className="text-sm text-gray-400 mt-4">
        Already have an account? <Link to="/login" className="text-accent hover:underline">Log in</Link>
      </p>
    </div>
  );
}

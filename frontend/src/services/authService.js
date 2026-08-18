import api from "./api";

export const register = (username, email, password) =>
  api.post("/api/auth/register", { username, email, password });

export const login = (email, password) =>
  api.post("/api/auth/login", { email, password });

export const getMe = () => api.get("/api/auth/me");

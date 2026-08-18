import api from "./api";

export const getAllUsers = () => api.get("/api/admin/users");
export const getStats = () => api.get("/api/admin/stats");
export const deleteUser = (userId) => api.delete(`/api/admin/users/${userId}`);

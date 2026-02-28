// src/api/http.js
import axios from "axios";

const api = axios.create({
  baseURL:"http://localhost:5000/api",
  timeout: 10000, // 10 seconds
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err?.response?.status === 401) {
      // Clear auth data on unauthorized (token expired/invalid)
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      // Trigger custom event so AuthContext can react (storage event only fires cross-tab)
      window.dispatchEvent(new Event("tokenExpired"));
      // Only redirect if not already on login page
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(err);
  }
);

export default api;

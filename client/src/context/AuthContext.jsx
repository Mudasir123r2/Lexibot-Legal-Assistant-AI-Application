// src/context/AuthContext.jsx
import { createContext, useState, useEffect } from "react";
import api from "../api/http";

// eslint-disable-next-line react-refresh/only-export-components
export const AuthContext = createContext({
  user: null,
  login: async () => {},
  register: async () => {},
  logout: () => {},
  updateUser: () => {},
});

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    // Only set user if both token and user exist
    const token = localStorage.getItem("token");
    const userData = localStorage.getItem("user");
    if (token && userData) {
      try {
        return JSON.parse(userData);
      } catch {
        return null;
      }
    }
    return null;
  });

  // Listen for storage changes (e.g., when token is cleared by 401 interceptor)
  useEffect(() => {
    const handleStorageChange = () => {
      const token = localStorage.getItem("token");
      if (!token && user) {
        setUser(null);
      }
    };

    window.addEventListener("storage", handleStorageChange);
    // Also listen to custom events dispatched by same-window storage changes
    window.addEventListener("tokenExpired", handleStorageChange);

    return () => {
      window.removeEventListener("storage", handleStorageChange);
      window.removeEventListener("tokenExpired", handleStorageChange);
    };
  }, [user]);

  const login = async (email, password) => {
    try {
      const { data } = await api.post("/auth/login", { email, password });
      localStorage.setItem("token", data.token);
      localStorage.setItem("user", JSON.stringify(data.user));
      setUser(data.user);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.response?.data?.message || "Login failed";
      throw new Error(errorMessage); // Throw to allow component to handle
    }
  };

  const register = async (payload) => {
    try {
      const { data } = await api.post("/auth/register", payload);
      return data; // Return response data (contains message)
    } catch (err) {
      throw new Error(err.response?.data?.detail || err.response?.data?.message || "Registration failed");
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
    // Dispatch event so other parts of the app can react
    window.dispatchEvent(new Event("tokenExpired"));
  };

  const updateUser = (userData) => {
    const updatedUser = { ...user, ...userData };
    localStorage.setItem("user", JSON.stringify(updatedUser));
    setUser(updatedUser);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  );
};

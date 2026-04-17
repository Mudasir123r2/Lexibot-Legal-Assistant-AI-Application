import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import PrivateRoute from "./utils/PrivateRoute";
import GuestRoute from "./utils/GuestRoute";
import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import ChatDashboard from "./pages/Dashboard/ChatDashboard";
import CasesDashboard from "./pages/Dashboard/CasesDashboard";
import JudgmentsDashboard from "./pages/Dashboard/JudgmentsDashboard";
import RemindersDashboard from "./pages/Dashboard/RemindersDashboard";
import ProfileDashboard from "./pages/Dashboard/ProfileDashboard";
import AdminDashboard from "./pages/Dashboard/AdminDashboard";
import Home from "./pages/Home";
import ForgotPassword from "./pages/auth/ForgotPassword";
import ResetPassword from "./pages/auth/ResetPassword";
import VerifyEmail from "./pages/auth/VerifyEmail";

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route
            path="/login"
            element={
              <GuestRoute>
                <Login />
              </GuestRoute>
            }
          />
          <Route
            path="/admin-login"
            element={
              <GuestRoute>
                <Login isAdminLogin={true} />
              </GuestRoute>
            }
          />
          <Route
            path="/register"
            element={
              <GuestRoute>
                <Register />
              </GuestRoute>
            }
          />
          <Route path="/verify-email" element={<VerifyEmail />} />
          <Route
            path="/forgot"
            element={
              <GuestRoute>
                <ForgotPassword />
              </GuestRoute>
            }
          />
          <Route
            path="/reset-password"
            element={
              <GuestRoute>
                <ResetPassword />
              </GuestRoute>
            }
          />
          <Route
            path="/chat"
            element={
              <PrivateRoute>
                <ChatDashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/cases"
            element={
              <PrivateRoute roles={["admin", "advocate"]}>
                <CasesDashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/judgments"
            element={
              <PrivateRoute>
                <JudgmentsDashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/judgments/:id"
            element={
              <PrivateRoute>
                <JudgmentsDashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/reminders"
            element={
              <PrivateRoute roles={["admin", "advocate"]}>
                <RemindersDashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <PrivateRoute>
                <ProfileDashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/admin"
            element={
              <PrivateRoute roles={["admin"]}>
                <AdminDashboard />
              </PrivateRoute>
            }
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
}
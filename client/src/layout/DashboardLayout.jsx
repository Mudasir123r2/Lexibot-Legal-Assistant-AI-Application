import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import { useContext, useState, useEffect } from "react";
import { AuthContext } from "../context/AuthContext";
import api from "../api/http";
import { FaBell, FaTimes, FaInbox } from "react-icons/fa";
import { Link } from "react-router-dom";

export default function DashboardLayout({ children }) {
  const { user } = useContext(AuthContext);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);

  useEffect(() => {
    // Only fetch for lawyer/advocate or admin
    const fetchReminders = async () => {
      if (user?.role !== "advocate" && user?.role !== "admin") return;
      try {
        const { data } = await api.get("/reminders");
        if (Array.isArray(data)) {
          const now = new Date();
          const overdueOrDue = data.filter(r => {
            if (r.isCompleted) return false;
            const due = new Date(r.dueDate);
            if (due <= now) return true; // Overdue
            // Due today
            return due.toDateString() === now.toDateString();
          });
          
          // Sort by most urgent/overdue first
          overdueOrDue.sort((a, b) => new Date(a.dueDate) - new Date(b.dueDate));
          setNotifications(overdueOrDue);
        }
      } catch (e) {}
    };

    fetchReminders();

    // Listen for custom event to refetch when reminders change
    window.addEventListener("remindersUpdated", fetchReminders);
    return () => window.removeEventListener("remindersUpdated", fetchReminders);
  }, [user]);

  return (
    <div className="relative min-h-[100dvh] h-[100dvh] bg-[#0a0a0b] text-slate-100 overflow-hidden">
      {/* background mesh */}
      <div className="pointer-events-none absolute inset-0 -z-10">
        <div className="absolute inset-0 bg-[radial-gradient(120%_90%_at_50%_0%,rgba(255,255,255,0.06)_0%,transparent_60%),radial-gradient(90%_70%_at_0%_0%,rgba(99,102,241,0.10)_0%,transparent_60%),radial-gradient(90%_70%_at_100%_0%,rgba(236,72,153,0.10)_0%,transparent_60%)]" />
        <div className="absolute -top-24 -left-24 h-72 w-72 rounded-full bg-gradient-to-tr from-indigo-500/20 via-fuchsia-500/10 to-emerald-400/10 blur-3xl animate-pulse" style={{ animationDuration: '4s' }} />
        <div className="absolute -bottom-24 -right-20 h-96 w-96 rounded-full bg-gradient-to-br from-fuchsia-600/15 to-indigo-600/10 blur-3xl animate-pulse" style={{ animationDuration: '6s' }} />
      </div>

      <div className="flex h-[100dvh] w-full">
        {/* Sticky sidebar */}
        <aside className={`hidden md:block relative sticky top-0 h-[100dvh] shrink-0 overflow-y-auto border-r border-white/10 bg-neutral-900/40 backdrop-blur-xl z-10 transition-all duration-300 ${sidebarCollapsed ? 'w-16' : 'w-64'}`}>
          <Sidebar user={user} isCollapsed={sidebarCollapsed} onToggle={() => setSidebarCollapsed(!sidebarCollapsed)} />
        </aside>

        {/* Main column */}
        <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
          {/* Sticky navbar */}
          <header className="sticky top-0 z-20 shrink-0 border-b border-white/10 bg-neutral-900/40 backdrop-blur-xl shadow-lg">
            <Navbar 
               notifications={notifications} 
               isNotificationsOpen={isNotificationsOpen} 
               setIsNotificationsOpen={setIsNotificationsOpen} 
            />
          </header>

          {/* Notification Banner for Reminders */}
          {notifications.length > 0 && (() => {
            const now = new Date();
            const overdueCount = notifications.filter(n => new Date(n.dueDate) < now).length;
            const dueTodayCount = notifications.length - overdueCount;

            let message = "";
            if (overdueCount > 0 && dueTodayCount > 0) {
              message = `You have ${overdueCount} overdue and ${dueTodayCount} due reminder(s) waiting for you.`;
            } else if (overdueCount > 0) {
              message = `You have ${overdueCount} overdue reminder(s) that need immediate attention.`;
            } else {
              message = `You have ${dueTodayCount} reminder(s) due today.`;
            }

            return (
             <div className="bg-rose-500/20 border-b border-rose-500/50 backdrop-blur-md px-4 py-2.5 flex items-center justify-between shrink-0">
                <div className="flex items-center gap-3">
                   <span className="flex h-2 w-2 relative">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-rose-500"></span>
                   </span>
                   <p className="text-sm font-medium text-rose-200">
                      {message}
                   </p>
                </div>
                <button 
                  onClick={() => setIsNotificationsOpen(true)}
                  className="text-xs bg-rose-500/20 hover:bg-rose-500/40 text-rose-300 px-3 py-1 rounded border border-rose-500/30 transition-colors"
                >
                  View Details
                </button>
             </div>
            );
          })()}

          <main className="flex-1 overflow-y-auto w-full flex flex-col">
            <div className="mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8 py-6 flex-1 flex flex-col">
              <div className="flex-1 flex flex-col">
                {children}
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}

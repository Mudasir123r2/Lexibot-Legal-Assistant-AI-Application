import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { FaBalanceScale, FaBell, FaInbox, FaTimes } from "react-icons/fa";
import { Link } from "react-router-dom";

export default function Navbar({ notifications = [], isNotificationsOpen, setIsNotificationsOpen }) {
  const { user, logout } = useContext(AuthContext);

  return (
    <div className="w-full">
      <nav className="px-4 sm:px-6 lg:px-8 py-3 flex items-center gap-3">
        {/* Brand */}
        <div className="flex items-center gap-2">
          <div className="h-9 w-9 rounded-lg bg-neutral-800 text-indigo-300 flex items-center justify-center ring-1 ring-white/10">
            <FaBalanceScale className="text-base" />
          </div>
          <span className="text-lg font-semibold text-slate-100">LexiBot</span>
        </div>

        {/* Welcome */}
        <div className="ml-3 text-sm sm:text-base text-slate-200 truncate">
          Welcome, {user?.name || "User"}
        </div>

        <div className="ml-auto flex items-center gap-3 sm:gap-4 shrink-0">
          {/* Optional user initials/avatar */}
          <div className="hidden sm:flex items-center justify-center h-9 w-9 rounded-full bg-neutral-800 text-slate-200 ring-1 ring-white/10">
            {(user?.name || "U").split(" ").map(s => s[0]).join("").slice(0, 2).toUpperCase()}
          </div>

          <div className="flex items-center gap-2 sm:gap-3">
             <button
               onClick={logout}
               className="rounded-xl px-3 py-2 sm:px-4 font-semibold text-white shadow-[0_8px_30px_rgba(99,102,241,0.35)]
                          bg-[linear-gradient(135deg,#4338CA_0%,#6D28D9_30%,#7C3AED_55%,#DB2777_100%)]
                          hover:shadow-[0_10px_40px_rgba(236,72,153,0.35)] flex-shrink-0 text-sm sm:text-base"
             >
               Logout
             </button>

             {/* Notifications Dropdown */}
             {user?.role !== "client" && notifications && notifications.length > 0 && (
                <div className="relative shrink-0">
                   <button 
                      onClick={() => setIsNotificationsOpen(!isNotificationsOpen)} 
                      className="bg-neutral-900 border border-white/10 hover:border-rose-500/50 p-2.5 rounded-xl shadow-lg ring-1 ring-black flex items-center gap-2 transition-all group"
                   >
                      <div className="relative">
                         <FaBell className="text-lg text-rose-500 group-hover:scale-110 transition-transform origin-top" />
                         <span className="absolute -top-1.5 -right-1.5 bg-rose-500 text-white text-[9px] grid place-items-center w-3.5 h-3.5 rounded-full font-bold shadow animate-pulse">
                            {notifications.length}
                         </span>
                      </div>
                   </button>

                {isNotificationsOpen && (
                   <div className="absolute top-full mt-3 right-0 w-80 bg-neutral-900/95 backdrop-blur-xl border border-white/10 rounded-2xl shadow-[0_0_40px_rgba(0,0,0,0.5)] overflow-hidden flex flex-col z-[100] transform origin-top-right">
                      <div className="p-4 border-b border-white/5 bg-black/40 flex justify-between items-center">
                         <h3 className="font-bold text-white flex items-center gap-2"><FaInbox className="text-indigo-400" /> Action Required</h3>
                         <button onClick={() => setIsNotificationsOpen(false)} className="text-slate-400 hover:text-white"><FaTimes /></button>
                      </div>
                      <div className="max-h-[350px] overflow-y-auto custom-scrollbar flex flex-col">
                         {notifications.map(notif => (
                            <Link 
                               to="/reminders" 
                               key={notif._id} 
                               className="p-4 border-b border-white/5 hover:bg-white/5 flex flex-col gap-1 transition-colors"
                               onClick={() => setIsNotificationsOpen(false)}
                            >
                               <div className="flex justify-between items-start">
                                  <span className="font-bold text-rose-400 text-sm line-clamp-1">{notif.title}</span>
                                  <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-rose-500/20 text-rose-500 shrink-0">Due</span>
                               </div>
                               <span className="text-xs text-slate-400">{new Date(notif.dueDate).toLocaleDateString()} at {new Date(notif.dueDate).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                            </Link>
                         ))}
                      </div>
                      <div className="p-3 bg-black/40 text-center">
                          <Link to="/reminders" onClick={() => setIsNotificationsOpen(false)} className="text-xs text-indigo-400 hover:text-indigo-300 font-bold uppercase tracking-wider">Open Timeline Dashboard</Link>
                      </div>
                   </div>
                )}
             </div>
          )}
          </div>
        </div>
      </nav>
    </div>
  );
}

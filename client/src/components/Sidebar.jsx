import { NavLink } from "react-router-dom";
import { FaBalanceScale } from "react-icons/fa";
import { FiChevronLeft, FiChevronRight } from "react-icons/fi";

export default function Sidebar({ user, isCollapsed, onToggle }) {
  const links = [
    { path: "/chat", label: "Chat" },
    { path: "/cases", label: "My Cases" },
    { path: "/judgments", label: "Judgments" },
    { path: "/reminders", label: "Reminders" },
    { path: "/profile", label: "Profile" },
  ];
  if (user?.role === "admin") links.push({ path: "/admin", label: "Admin Panel" });

  return (
    <div className={`relative h-[100dvh] flex flex-col transition-all duration-300 ${isCollapsed ? 'w-16' : 'w-64'}`}>
      {/* Brand */}
      <div className={`px-4 py-5 border-b border-white/10 flex items-center ${isCollapsed ? 'justify-center' : 'justify-between'}`}>
        {isCollapsed ? (
          // When collapsed, show only toggle button
          <button
            onClick={onToggle}
            className="h-9 w-9 rounded-lg bg-neutral-800/60 hover:bg-neutral-800 ring-1 ring-white/10 hover:ring-white/20 backdrop-blur-xl flex items-center justify-center text-slate-400 hover:text-white transition-all group"
            title="Expand sidebar"
          >
            <FiChevronRight className="text-base group-hover:scale-110 transition-transform" />
          </button>
        ) : (
          // When expanded, show logo and toggle button
          <>
            <div className="flex items-center gap-2">
              <div className="h-9 w-9 rounded-lg bg-neutral-800 text-indigo-300 flex items-center justify-center ring-1 ring-white/10 shrink-0">
                <FaBalanceScale className="text-base" />
              </div>
              <span className="text-lg font-semibold text-slate-100">LexiBot</span>
            </div>
            
            {/* Toggle Button - In header */}
            <button
              onClick={onToggle}
              className="h-8 w-8 rounded-lg bg-neutral-800/60 hover:bg-neutral-800 ring-1 ring-white/10 hover:ring-white/20 backdrop-blur-xl flex items-center justify-center text-slate-400 hover:text-white transition-all group"
              title="Collapse sidebar"
            >
              <FiChevronLeft className="text-base group-hover:scale-110 transition-transform" />
            </button>
          </>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto px-3 py-4">
        <ul className="space-y-2">
          {links.map((link) => (
            <li key={link.path}>
              <NavLink
                to={link.path}
                title={isCollapsed ? link.label : undefined}
                className={({ isActive }) =>
                  [
                    "block w-full rounded-xl text-sm font-medium transition-colors",
                    "border border-white/10 bg-neutral-900/40 hover:bg-neutral-900/60",
                    isActive
                      ? "text-white bg-gradient-to-r from-indigo-600/30 to-fuchsia-600/20 ring-1 ring-white/10"
                      : "text-slate-300",
                    isCollapsed ? "px-2 py-2.5 text-center" : "px-4 py-2.5"
                  ].join(" ")
                }
              >
                {isCollapsed ? link.label.charAt(0) : link.label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      {/* User footer */}
      <div className={`px-4 py-4 border-t border-white/10 ${isCollapsed ? 'flex justify-center' : ''}`}>
        <div className={`flex items-center gap-3 ${isCollapsed ? 'flex-col gap-2' : ''}`}>
          <div className="h-9 w-9 rounded-full bg-neutral-800 text-slate-200 ring-1 ring-white/10 flex items-center justify-center shrink-0 text-xs">
            {(user?.name || "U").split(" ").map(s => s[0]).join("").slice(0,2).toUpperCase()}
          </div>
          {!isCollapsed && (
            <div className="min-w-0">
              <div className="text-xs font-semibold text-slate-200 truncate">
                {user?.name || "User"}
              </div>
              <div className="text-[11px] text-slate-400 truncate">
                {user?.email || ""}
              </div>
            </div>
          )}
        </div>
      </div>
      
    </div>
  );
}

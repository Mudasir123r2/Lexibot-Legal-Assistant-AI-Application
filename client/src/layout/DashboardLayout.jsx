import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import { useContext, useState } from "react";
import { AuthContext } from "../context/AuthContext";

export default function DashboardLayout({ children }) {
  const { user } = useContext(AuthContext);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

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
            <Navbar />
          </header>

          <main className="flex-1 overflow-y-auto w-full">
            <div className="mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8 py-6 h-full">
              <div className="min-h-full">
                {children}
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}

import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { FaBalanceScale } from "react-icons/fa";

export default function Navbar() {
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

        <div className="ml-auto flex items-center gap-3">
          {/* Optional user initials/avatar */}
          <div className="hidden sm:flex items-center justify-center h-9 w-9 rounded-full bg-neutral-800 text-slate-200 ring-1 ring-white/10">
            {(user?.name || "U").split(" ").map(s => s[0]).join("").slice(0, 2).toUpperCase()}
          </div>

          <button
            onClick={logout}
            className="rounded-xl px-4 py-2 font-semibold text-white shadow-[0_8px_30px_rgba(99,102,241,0.35)]
                       bg-[linear-gradient(135deg,#4338CA_0%,#6D28D9_30%,#7C3AED_55%,#DB2777_100%)]
                       hover:shadow-[0_10px_40px_rgba(236,72,153,0.35)]"
          >
            Logout
          </button>
        </div>
      </nav>
    </div>
  );
}

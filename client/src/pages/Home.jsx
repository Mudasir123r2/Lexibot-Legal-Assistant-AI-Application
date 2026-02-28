// src/pages/Home.jsx
import { Link } from "react-router-dom";
import { FaBalanceScale, FaShieldAlt, FaSearch, FaRegComments, FaMagic } from "react-icons/fa";

export default function Home() {
  return (
    <div className="relative min-h-screen bg-[#0a0a0b] text-slate-100 flex flex-col">
      {/* Background mesh gradients */}
      <div className="pointer-events-none absolute inset-0 -z-10">
        <div className="absolute inset-0 bg-[radial-gradient(120%_90%_at_50%_0%,rgba(255,255,255,0.06)_0%,transparent_60%),radial-gradient(90%_70%_at_0%_0%,rgba(99,102,241,0.10)_0%,transparent_60%),radial-gradient(90%_70%_at_100%_0%,rgba(236,72,153,0.10)_0%,transparent_60%)]" />
        <div className="absolute -top-24 -left-24 h-80 w-80 rounded-full bg-gradient-to-tr from-indigo-500/20 via-fuchsia-500/10 to-emerald-400/10 blur-3xl" />
        <div className="absolute -bottom-24 -right-20 h-96 w-96 rounded-full bg-gradient-to-br from-fuchsia-600/15 to-indigo-600/10 blur-3xl" />
      </div>

      {/* Top Nav */}
      <header className="container mx-auto px-4 py-4 flex items-center gap-3">
        <div className="h-10 w-10 rounded-xl bg-neutral-800 text-indigo-300 flex items-center justify-center ring-1 ring-white/10">
          <FaBalanceScale />
        </div>
        <span className="text-lg font-semibold">LexiBot</span>
        <nav className="ml-auto flex items-center gap-4">
          <Link className="text-slate-300 hover:text-slate-100" to="/login">Login</Link>
          <Link className="text-slate-300 hover:text-slate-100" to="/register">Register</Link>
          <Link className="rounded-lg px-3 py-1.5 text-white bg-[linear-gradient(135deg,#4338CA_0%,#6D28D9_30%,#7C3AED_55%,#DB2777_100%)] hover:opacity-95" to="/chat">
            Open Chat
          </Link>
        </nav>
      </header>

      {/* Main grows to push footer down, eliminating bottom gap */}
      <main className="grow">
        {/* Hero */}
        <section className="container mx-auto px-4 pt-8 pb-12 lg:py-16 grid lg:grid-cols-2 gap-10 items-center">
          <div>
            <h1 className="text-4xl lg:text-5xl font-extrabold leading-tight">
              AI‑Powered Legal Research, Summaries, and Client Guidance
            </h1>
            <p className="mt-4 text-slate-400">
              Retrieve judgments faster, summarize complex rulings into plain English, and guide clients with confidence using AI-powered research.
            </p>
            <div className="mt-6 flex gap-3">
              <Link to="/chat" className="rounded-xl px-5 py-3 font-semibold text-white shadow-[0_8px_30px_rgba(99,102,241,0.35)] bg-[linear-gradient(135deg,#4338CA_0%,#6D28D9_30%,#7C3AED_55%,#DB2777_100%)] hover:shadow-[0_10px_40px_rgba(236,72,153,0.35)]">
                Start Chat
              </Link>
              <Link to="/register" className="rounded-xl px-5 py-3 font-semibold border border-white/15 bg-neutral-900/40 hover:bg-neutral-800/60">
                Create Account
              </Link>
            </div>
          </div>

          {/* Glass highlight panel */}
          <div className="relative">
            <div className="absolute -inset-[2px] rounded-3xl bg-[conic-gradient(from_140deg,rgba(99,102,241,.35),rgba(236,72,153,.35),rgba(16,185,129,.35),rgba(99,102,241,.35))] blur md:blur-md opacity-70" />
            <div className="relative rounded-3xl ring-1 ring-white/10 bg-neutral-900/50 backdrop-blur-xl shadow-[0_10px_40px_rgba(0,0,0,0.6)] p-8">
              <h3 className="text-xl font-bold mb-2">Why LexiBot</h3>
              <p className="text-slate-400">
                Built for advocates and clients to search, summarize, and reason over legal texts with intelligent AI assistance.
              </p>
              <ul className="mt-4 space-y-2 text-sm text-slate-300 list-disc list-inside">
                <li>Intelligent case search and retrieval</li>
                <li>Concise, plain‑language summaries</li>
                <li>Context‑grounded answers with citations</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Features */}
        <section className="container mx-auto px-4 py-10">
          <h2 className="text-2xl font-bold mb-6">Features</h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <FeatureCard icon={<FaSearch />} title="Smart Search" desc="Find relevant judgments and statutes with intelligent search." />
            <FeatureCard icon={<FaMagic />} title="Summaries" desc="Turn lengthy rulings into clear, actionable briefs." />
            <FeatureCard icon={<FaRegComments />} title="Guidance" desc="Step‑by‑step checklists and next‑actions for clients." />
            <FeatureCard icon={<FaShieldAlt />} title="Security" desc="Role‑based access and protected chat history." />
          </div>
        </section>

        {/* Split audience */}
        <section className="container mx-auto px-4 py-10 grid lg:grid-cols-2 gap-6">
          <AudienceCard
            heading="For Advocates"
            bullets={["Rapid precedent lookup", "Grounded summaries for drafting", "Outcome insights with context"]}
            cta="Go to Chat"
            to="/chat"
          />
          <AudienceCard
            heading="For Clients"
            bullets={["Plain‑language answers", "Document checklists", "Clear next steps"]}
            cta="Create Account"
            to="/register"
          />
        </section>

        {/* CTA band (reduced bottom padding to avoid extra space) */}
        <section className="container mx-auto px-4 py-10">
          <div className="relative overflow-hidden rounded-3xl p-[1px] bg-[conic-gradient(from_140deg,rgba(99,102,241,.35),rgba(236,72,153,.35),rgba(16,185,129,.35),rgba(99,102,241,.35))]">
            <div className="rounded-3xl bg-neutral-900/60 backdrop-blur-xl p-8 flex flex-col lg:flex-row items-center justify-between gap-4">
              <div>
                <h3 className="text-xl font-bold">Ready to accelerate legal work?</h3>
                <p className="text-slate-400">Join free and start exploring your legal corpus with AI assistance.</p>
              </div>
              <div className="flex gap-3">
                <Link to="/register" className="rounded-xl px-5 py-3 font-semibold text-white shadow-[0_8px_30px_rgba(99,102,241,0.35)] bg-[linear-gradient(135deg,#4338CA_0%,#6D28D9_30%,#7C3AED_55%,#DB2777_100%)] hover:shadow-[0_10px_40px_rgba(236,72,153,0.35)]">
                  Get Started
                </Link>
                <Link to="/login" className="rounded-xl px-5 py-3 font-semibold border border-white/15 bg-neutral-900/40 hover:bg-neutral-800/60">
                  Sign In
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="container mx-auto px-4 py-8 text-sm text-slate-400">
        <div className="border-t border-white/10 pt-6 flex flex-col lg:flex-row items-center gap-3">
          <span>© {new Date().getFullYear()} LexiBot</span>
          <span className="lg:ml-auto">Built for responsible legal AI.</span>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({ icon, title, desc }) {
  return (
    <div className="group rounded-2xl border border-white/10 bg-neutral-900/40 p-5 backdrop-blur-lg hover:bg-neutral-900/60 transition-colors">
      <div className="h-10 w-10 rounded-lg bg-neutral-800 text-indigo-300 flex items-center justify-center ring-1 ring-white/10 mb-3">
        {icon}
      </div>
      <div className="font-semibold">{title}</div>
      <div className="text-sm text-slate-400 mt-1">{desc}</div>
    </div>
  );
}

function AudienceCard({ heading, bullets, cta, to }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-neutral-900/40 p-6 backdrop-blur-lg">
      <h3 className="text-lg font-bold">{heading}</h3>
      <ul className="mt-3 space-y-2 text-slate-300 list-disc list-inside text-sm">
        {bullets.map((b, i) => <li key={i}>{b}</li>)}
      </ul>
      <Link to={to} className="inline-block mt-5 rounded-xl px-4 py-2.5 font-semibold text-white bg-[linear-gradient(135deg,#4338CA_0%,#6D28D9_30%,#7C3AED_55%,#DB2777_100%)] hover:opacity-95">
        {cta}
      </Link>
    </div>
  );
}

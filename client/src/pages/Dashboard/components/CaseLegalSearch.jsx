import { useState } from "react";
import { FaSearch, FaGavel, FaCalendar, FaFileAlt, FaFilter, FaTimes, FaStar, FaBalanceScale } from "react-icons/fa";
import { FiLoader } from "react-icons/fi";
import api from "../../../api/http";

export default function CaseLegalSearch() {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchMode, setSearchMode] = useState("hybrid"); // semantic, keyword, hybrid
  const [caseType, setCaseType] = useState("");
  const [court, setCourt] = useState("");
  const [yearFrom, setYearFrom] = useState("");
  const [yearTo, setYearTo] = useState("");
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedJudgment, setSelectedJudgment] = useState(null);

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      alert("Please enter a search term");
      return;
    }

    setLoading(true);
    try {
      const payload = {
        query: searchQuery,
        searchMode: searchMode,
        limit: 20,
        ...(caseType && { caseType }),
        ...(court && { court }),
        ...(yearFrom && { yearFrom: parseInt(yearFrom) }),
        ...(yearTo && { yearTo: parseInt(yearTo) })
      };

      const { data } = await api.post("/ai/search", payload);
      setResults(data.results || []);
    } catch (err) {
      console.error("Search error:", err);
      alert("Failed to search judgments. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const fetchJudgmentDetails = async (id) => {
    try {
      const { data } = await api.get(`/judgments/${id}`);
      setSelectedJudgment(data);
    } catch (err) {
      console.error("Error fetching judgment details:", err);
      alert("Failed to load judgment details");
    }
  };

  const clearFilters = () => {
    setSearchQuery("");
    setCaseType("");
    setCourt("");
    setYearFrom("");
    setYearTo("");
    setResults([]);
  };

  const getSearchModeLabel = (mode) => {
    switch(mode) {
      case "semantic": return "AI Semantic";
      case "keyword": return "Keyword";
      case "hybrid": return "Smart Search";
      default: return mode;
    }
  };

  const getRelevanceBadge = (score) => {
    if (score >= 90) return { color: "emerald", label: "Highly Relevant" };
    if (score >= 75) return { color: "blue", label: "Relevant" };
    if (score >= 60) return { color: "amber", label: "Moderate" };
    return { color: "slate", label: "Low" };
  };

  return (
    <div className="relative w-full h-full flex flex-col">
      <div className="mb-6 shrink-0">
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-2xl font-display font-bold text-white mb-2">Legal Case Search</h2>
            <p className="text-slate-400 text-sm">AI-powered semantic search with advanced filters</p>
          </div>
          {results.length > 0 && (
            <button
              onClick={clearFilters}
              className="px-3 py-2 rounded-xl border border-white/10 bg-neutral-800/50 hover:bg-neutral-800 text-slate-300 text-sm flex items-center gap-2"
            >
              <FaTimes /> Clear
            </button>
          )}
        </div>
      </div>

      {/* Search Panel */}
      <div className="rounded-2xl ring-1 ring-white/10 bg-neutral-900/50 backdrop-blur-xl p-6 mb-6 shadow-xl shrink-0">
        <div className="space-y-4">
          {/* Search Mode Selection */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Search Mode</label>
            <div className="grid grid-cols-3 gap-3">
              <button
                onClick={() => setSearchMode("hybrid")}
                className={`px-4 py-2.5 rounded-xl border text-sm font-medium transition-all ${
                  searchMode === "hybrid"
                    ? "bg-gradient-to-r from-indigo-600/40 to-purple-600/40 border-indigo-500/50 text-white shadow-lg"
                    : "bg-neutral-800/50 border-white/10 text-slate-300 hover:bg-neutral-800/70"
                }`}
              >
                <div className="flex items-center justify-center gap-2">
                  <FaStar className="text-xs" />
                  Smart
                </div>
                <div className="text-xs text-slate-400 mt-1">AI + Keywords</div>
              </button>
              <button
                onClick={() => setSearchMode("semantic")}
                className={`px-4 py-2.5 rounded-xl border text-sm font-medium transition-all ${
                  searchMode === "semantic"
                    ? "bg-indigo-600/30 border-indigo-500/50 text-white"
                    : "bg-neutral-800/50 border-white/10 text-slate-300 hover:bg-neutral-800/70"
                }`}
              >
                <div>AI Semantic</div>
                <div className="text-xs text-slate-400 mt-1">Meaning-based</div>
              </button>
              <button
                onClick={() => setSearchMode("keyword")}
                className={`px-4 py-2.5 rounded-xl border text-sm font-medium transition-all ${
                  searchMode === "keyword"
                    ? "bg-indigo-600/30 border-indigo-500/50 text-white"
                    : "bg-neutral-800/50 border-white/10 text-slate-300 hover:bg-neutral-800/70"
                }`}
              >
                <div>Keyword</div>
                <div className="text-xs text-slate-400 mt-1">Exact match</div>
              </button>
            </div>
          </div>

          {/* Search Input */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Search Query</label>
            <div className="relative">
              <FaSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && !loading && handleSearch()}
                placeholder="e.g., divorce custody children, property dispute inheritance..."
                className="w-full pl-12 pr-4 py-3 rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/60"
              />
            </div>
          </div>

          {/* Advanced Filters Toggle */}
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center gap-2 text-sm text-indigo-400 hover:text-indigo-300"
          >
            <FaFilter /> {showAdvanced ? "Hide" : "Show"} Advanced Filters
          </button>

          {/* Advanced Filters */}
          {showAdvanced && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 rounded-xl bg-neutral-800/30 border border-white/5">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Case Type</label>
                <select
                  value={caseType}
                  onChange={(e) => setCaseType(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500/60"
                >
                  <option value="">All Types</option>
                  <option value="Civil">Civil</option>
                  <option value="Criminal">Criminal</option>
                  <option value="Family">Family</option>
                  <option value="Corporate">Corporate</option>
                  <option value="Property">Property</option>
                  <option value="Contract">Contract</option>
                  <option value="Employment">Employment</option>
                  <option value="Constitutional">Constitutional</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Court</label>
                <input
                  type="text"
                  value={court}
                  onChange={(e) => setCourt(e.target.value)}
                  placeholder="e.g., Lahore High Court"
                  className="w-full px-4 py-2.5 rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/60"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Year From</label>
                <input
                  type="number"
                  value={yearFrom}
                  onChange={(e) => setYearFrom(e.target.value)}
                  placeholder="e.g., 2020"
                  min="1900"
                  max={new Date().getFullYear()}
                  className="w-full px-4 py-2.5 rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/60"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Year To</label>
                <input
                  type="number"
                  value={yearTo}
                  onChange={(e) => setYearTo(e.target.value)}
                  placeholder="e.g., 2024"
                  min="1900"
                  max={new Date().getFullYear()}
                  className="w-full px-4 py-2.5 rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/60"
                />
              </div>
            </div>
          )}

          {/* Search Button */}
          <button
            onClick={handleSearch}
            disabled={loading}
            className="w-full px-4 py-3.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg hover:shadow-xl transition-all"
          >
            {loading ? (
              <>
                <FiLoader className="animate-spin" /> Searching...
              </>
            ) : (
              <>
                <FaSearch /> Search {results.length > 0 && `(${results.length} results)`}
              </>
            )}
          </button>
        </div>
      </div>

      {/* Search Results */}
      <div className="flex-1 overflow-y-auto min-h-0">
        {results.length > 0 && (
          <div className="space-y-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-white">
                Found {results.length} {results.length === 1 ? "judgment" : "judgments"}
              </h3>
              <span className="text-sm text-slate-400">Mode: {getSearchModeLabel(searchMode)}</span>
            </div>

            {results.map((judgment, idx) => {
              const relevance = getRelevanceBadge(judgment.relevance_score || 70);
              return (
                <div
                  key={judgment.id || idx}
                  className="rounded-2xl ring-1 ring-white/10 bg-neutral-900/50 backdrop-blur-xl p-5 hover:ring-indigo-500/30 hover:shadow-xl cursor-pointer transition-all animate-fade-in"
                  onClick={() => fetchJudgmentDetails(judgment.id)}
                >
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex-1">
                      <h4 className="text-lg font-semibold text-white mb-1">{judgment.title || "Untitled"}</h4>
                      {judgment.citation && (
                        <p className="text-sm text-slate-400">Citation: {judgment.citation}</p>
                      )}
                    </div>
                    <div className="flex flex-col items-end gap-2">
                      {judgment.case_type && (
                        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/20 text-indigo-400">
                          {judgment.case_type}
                        </span>
                      )}
                      {judgment.relevance_score && (
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold bg-${relevance.color}-500/20 text-${relevance.color}-400 flex items-center gap-1`}>
                          <FaBalanceScale className="text-xs" />
                          {judgment.relevance_score.toFixed(0)}%
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm text-slate-300 mb-3">
                    <div className="flex items-center gap-2">
                      <FaGavel className="text-slate-500" />
                      <span>{judgment.court || "Unknown Court"}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <FaCalendar className="text-slate-500" />
                      <span>{judgment.date ? new Date(judgment.date).toLocaleDateString() : "Date N/A"}</span>
                    </div>
                    {judgment.search_method && (
                      <div className="flex items-center gap-2">
                        <FaStar className="text-slate-500 text-xs" />
                        <span className="capitalize text-xs">{judgment.search_method}</span>
                      </div>
                    )}
                  </div>

                  {judgment.excerpt && (
                    <p className="text-sm text-slate-400 line-clamp-2">{judgment.excerpt}</p>
                  )}

                  {judgment.parties && (
                    <p className="text-xs text-slate-500 mt-2">Parties: {judgment.parties}</p>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {results.length === 0 && !loading && (
          <div className="rounded-2xl ring-1 ring-white/10 bg-neutral-900/50 backdrop-blur-xl p-12 text-center text-slate-400">
            <FaSearch className="text-5xl mx-auto mb-4 opacity-20" />
            <p className="font-medium text-lg">No results yet</p>
            <p className="text-sm mt-2">Enter a search query and click Search to find relevant judgments</p>
            <div className="mt-4 text-xs text-slate-500">
              <p>💡 Try using natural language like:</p>
              <p className="mt-1">"divorce cases involving child custody"</p>
              <p>"property disputes between siblings"</p>
            </div>
          </div>
        )}
      </div>

      {/* Judgment Detail Modal */}
      {selectedJudgment && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-neutral-900 rounded-2xl ring-1 ring-white/10 p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto shadow-2xl">
            <div className="flex justify-between items-start mb-6">
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-white mb-2">{selectedJudgment.title}</h2>
                <p className="text-slate-400">Case No: {selectedJudgment.caseNumber || "N/A"}</p>
              </div>
              <button
                onClick={() => setSelectedJudgment(null)}
                className="px-4 py-2 rounded-xl border border-white/10 bg-neutral-800 hover:bg-neutral-700 text-slate-100 ml-4"
              >
                Close
              </button>
            </div>
            
            <div className="space-y-4 text-sm">
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 rounded-xl bg-neutral-800/50">
                  <span className="text-slate-500 block mb-1">Court</span>
                  <span className="text-slate-200 font-medium">{selectedJudgment.court || "N/A"}</span>
                </div>
                <div className="p-3 rounded-xl bg-neutral-800/50">
                  <span className="text-slate-500 block mb-1">Date</span>
                  <span className="text-slate-200 font-medium">
                    {selectedJudgment.dateOfJudgment ? new Date(selectedJudgment.dateOfJudgment).toLocaleDateString() : "N/A"}
                  </span>
                </div>
                {selectedJudgment.judge && (
                  <div className="p-3 rounded-xl bg-neutral-800/50">
                    <span className="text-slate-500 block mb-1">Judge</span>
                    <span className="text-slate-200 font-medium">{selectedJudgment.judge}</span>
                  </div>
                )}
                {selectedJudgment.caseType && (
                  <div className="p-3 rounded-xl bg-neutral-800/50">
                    <span className="text-slate-500 block mb-1">Case Type</span>
                    <span className="text-slate-200 font-medium">{selectedJudgment.caseType}</span>
                  </div>
                )}
              </div>

              {selectedJudgment.parties && (
                <div className="p-4 rounded-xl bg-neutral-800/50 border border-white/5">
                  <h3 className="font-semibold text-white mb-2 flex items-center gap-2">
                    <FaFileAlt /> Parties
                  </h3>
                  <p className="text-slate-300">{selectedJudgment.parties}</p>
                </div>
              )}

              {selectedJudgment.summary && (
                <div className="p-4 rounded-xl bg-neutral-800/50 border border-white/5">
                  <h3 className="font-semibold text-white mb-3">Summary</h3>
                  <p className="text-slate-300 whitespace-pre-wrap leading-relaxed">{selectedJudgment.summary}</p>
                </div>
              )}

              {selectedJudgment.keyInformation && (
                <div className="p-4 rounded-xl bg-neutral-800/50 border border-white/5">
                  <h3 className="font-semibold text-white mb-3">Key Information</h3>
                  
                  {selectedJudgment.keyInformation.issues && selectedJudgment.keyInformation.issues.length > 0 && (
                    <div className="mb-4">
                      <h4 className="text-slate-400 mb-2 font-medium">Legal Issues:</h4>
                      <ul className="list-disc list-inside text-slate-300 space-y-1">
                        {selectedJudgment.keyInformation.issues.map((issue, i) => (
                          <li key={i}>{issue}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {selectedJudgment.keyInformation.decisions && selectedJudgment.keyInformation.decisions.length > 0 && (
                    <div>
                      <h4 className="text-slate-400 mb-2 font-medium">Decisions:</h4>
                      <ul className="list-disc list-inside text-slate-300 space-y-1">
                        {selectedJudgment.keyInformation.decisions.map((decision, i) => (
                          <li key={i}>{decision}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}


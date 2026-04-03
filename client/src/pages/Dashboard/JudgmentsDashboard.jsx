import DashboardLayout from "../../layout/DashboardLayout";
import { useState, useEffect } from "react";
import { FaSearch, FaCalendar, FaGavel, FaFileAlt, FaRobot } from "react-icons/fa";
import { FiLoader, FiZap } from "react-icons/fi";
import api from "../../api/http";

export default function JudgmentsDashboard() {
  const [judgments, setJudgments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedJudgment, setSelectedJudgment] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [filters, setFilters] = useState({
    caseType: "",
    year: "",
    court: ""
  });
  const [pagination, setPagination] = useState({ page: 1, limit: 10, total: 0 });

  useEffect(() => {
    fetchJudgments();
  }, [searchQuery, filters, pagination.page]);

  const fetchJudgments = async () => {
    try {
      setLoading(true);
      const params = {
        page: pagination.page,
        limit: pagination.limit,
        ...(searchQuery && { search: searchQuery }),
        ...(filters.caseType && { caseType: filters.caseType }),
        ...(filters.year && { year: filters.year }),
        ...(filters.court && { court: filters.court })
      };
      const { data } = await api.get("/judgments/search", { params });
      setJudgments(data.judgments || data);
      if (data.pagination) setPagination(prev => ({ ...prev, total: data.pagination.total }));
    } catch (err) {
      console.error("Error fetching judgments:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchJudgmentDetails = async (id) => {
    try {
      const { data } = await api.get(`/judgments/${id}`);
      setSelectedJudgment({ ...data, aiSummaryLoading: false, aiExtractLoading: false });
    } catch (err) {
      console.error("Error fetching judgment details:", err);
      alert("Failed to load judgment details");
    }
  };

  const handleGenerateSummary = async (judgmentId, fullText) => {
    if (!fullText) return alert("No full text available to summarize.");
    setSelectedJudgment(prev => ({ ...prev, aiSummaryLoading: true }));
    try {
      const { data } = await api.post("/ai/summarize", {
        judgmentId: judgmentId,
        text: fullText
      });
      setSelectedJudgment(prev => ({ ...prev, aiSummaryLoading: false, summary: data.summary || data.response }));
    } catch (err) {
      console.error("Error generating summary", err);
      alert("Failed to generate AI summary.");
      setSelectedJudgment(prev => ({ ...prev, aiSummaryLoading: false }));
    }
  };

  const handleExtractInfo = async (judgmentId, fullText) => {
    if (!fullText) return alert("No full text available to extract from.");
    setSelectedJudgment(prev => ({ ...prev, aiExtractLoading: true }));
    try {
      const { data } = await api.post("/ai/extract", {
        judgmentId: judgmentId,
        text: fullText
      });
      setSelectedJudgment(prev => ({ ...prev, aiExtractLoading: false, keyInformation: data.extractedInfo || data.information }));
    } catch (err) {
      console.error("Error extracting info", err);
      alert("Failed to extract key information using AI.");
      setSelectedJudgment(prev => ({ ...prev, aiExtractLoading: false }));
    }
  };

  if (loading && judgments.length === 0) {
    return (
      <DashboardLayout>
        <div className="min-h-[60dvh] grid place-items-center">
          <FiLoader className="h-12 w-12 text-indigo-500 animate-spin" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="relative">
        <h1 className="text-2xl font-bold text-white mb-6">Legal Judgments</h1>

        {/* Search and Filters */}
        <div className="mb-6 space-y-4">
          <div className="relative">
            <FaSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search by case number, title, or keywords..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setPagination(prev => ({ ...prev, page: 1 }));
              }}
              className="w-full pl-10 pr-4 py-2 rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/60"
            />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <select
              value={filters.caseType}
              onChange={(e) => {
                setFilters({ ...filters, caseType: e.target.value });
                setPagination(prev => ({ ...prev, page: 1 }));
              }}
              className="px-4 py-2 rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500/60"
            >
              <option value="">All Case Types</option>
              <option value="Civil">Civil</option>
              <option value="Criminal">Criminal</option>
              <option value="Family">Family</option>
              <option value="Corporate">Corporate</option>
              <option value="Property">Property</option>
              <option value="Contract">Contract</option>
              <option value="Employment">Employment</option>
            </select>
            <input
              type="number"
              placeholder="Year"
              value={filters.year}
              onChange={(e) => {
                setFilters({ ...filters, year: e.target.value });
                setPagination(prev => ({ ...prev, page: 1 }));
              }}
              className="px-4 py-2 rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/60"
            />
            <input
              type="text"
              placeholder="Court name"
              value={filters.court}
              onChange={(e) => {
                setFilters({ ...filters, court: e.target.value });
                setPagination(prev => ({ ...prev, page: 1 }));
              }}
              className="px-4 py-2 rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/60"
            />
          </div>
        </div>

        {/* Judgments List */}
        <div className="space-y-4">
          {judgments.length === 0 ? (
            <div className="rounded-2xl ring-1 ring-white/10 bg-neutral-900/50 backdrop-blur-xl p-12 text-center text-slate-400">
              <p>No judgments found. Try adjusting your search or filters.</p>
            </div>
          ) : (
            judgments.map((judgment) => (
              <div
                key={judgment._id}
                className="rounded-2xl ring-1 ring-white/10 bg-neutral-900/50 backdrop-blur-xl p-5 hover:ring-white/20 cursor-pointer transition-all"
                onClick={() => fetchJudgmentDetails(judgment._id)}
              >
                <div className="flex justify-between items-start mb-3">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-white mb-1">{judgment.title}</h3>
                    <p className="text-sm text-slate-400">Case No: {judgment.caseNumber}</p>
                  </div>
                  {judgment.caseType && (
                    <span className="px-2 py-1 rounded-full text-xs font-semibold bg-indigo-500/20 text-indigo-400">
                      {judgment.caseType}
                    </span>
                  )}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm text-slate-300">
                  <div className="flex items-center gap-2">
                    <FaGavel className="text-slate-500" />
                    <span>{judgment.court}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <FaCalendar className="text-slate-500" />
                    <span>{new Date(judgment.dateOfJudgment).toLocaleDateString()}</span>
                  </div>
                  {judgment.judge && (
                    <div className="flex items-center gap-2">
                      <FaFileAlt className="text-slate-500" />
                      <span>Judge: {judgment.judge}</span>
                    </div>
                  )}
                </div>
                {judgment.summary && (
                  <p className="mt-3 text-sm text-slate-400 line-clamp-2">{judgment.summary}</p>
                )}
              </div>
            ))
          )}
        </div>

        {/* Pagination */}
        {pagination.total > pagination.limit && (
          <div className="mt-6 flex justify-center gap-2">
            <button
              onClick={() => setPagination(prev => ({ ...prev, page: prev.page - 1 }))}
              disabled={pagination.page === 1}
              className="px-4 py-2 rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <span className="px-4 py-2 text-slate-300">
              Page {pagination.page} of {Math.ceil(pagination.total / pagination.limit)}
            </span>
            <button
              onClick={() => setPagination(prev => ({ ...prev, page: prev.page + 1 }))}
              disabled={pagination.page >= Math.ceil(pagination.total / pagination.limit)}
              className="px-4 py-2 rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        )}

        {/* Judgment Detail Modal */}
        {selectedJudgment && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-neutral-900 rounded-2xl ring-1 ring-white/10 p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h2 className="text-2xl font-bold text-white mb-2">{selectedJudgment.title}</h2>
                  <p className="text-slate-400">Case No: {selectedJudgment.caseNumber}</p>
                </div>
                <button
                  onClick={() => setSelectedJudgment(null)}
                  className="px-4 py-2 rounded-xl border border-white/10 bg-neutral-800 hover:bg-neutral-700 text-slate-100"
                >
                  Close
                </button>
              </div>

              <div className="space-y-4 text-sm">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-slate-500">Court:</span> <span className="text-slate-300 ml-2">{selectedJudgment.court}</span>
                  </div>
                  <div>
                    <span className="text-slate-500">Date:</span> <span className="text-slate-300 ml-2">{new Date(selectedJudgment.dateOfJudgment).toLocaleDateString()}</span>
                  </div>
                  {selectedJudgment.judge && (
                    <div>
                      <span className="text-slate-500">Judge:</span> <span className="text-slate-300 ml-2">{selectedJudgment.judge}</span>
                    </div>
                  )}
                  {selectedJudgment.caseType && (
                    <div>
                      <span className="text-slate-500">Type:</span> <span className="text-slate-300 ml-2">{selectedJudgment.caseType}</span>
                    </div>
                  )}
                </div>

                <div className="flex gap-4 mb-4 border-b border-white/5 pb-4">
                  <button
                    onClick={() => handleGenerateSummary(selectedJudgment._id, selectedJudgment.fullText)}
                    disabled={selectedJudgment.aiSummaryLoading}
                    className="flex items-center gap-2 px-3 py-2 rounded-lg bg-indigo-600/30 text-indigo-300 hover:bg-indigo-600/50 transition-colors text-sm font-medium"
                  >
                    {selectedJudgment.aiSummaryLoading ? <FiLoader className="animate-spin" /> : <FaRobot />}
                    Auto-Generate AI Summary
                  </button>
                  <button
                    onClick={() => handleExtractInfo(selectedJudgment._id, selectedJudgment.fullText)}
                    disabled={selectedJudgment.aiExtractLoading}
                    className="flex items-center gap-2 px-3 py-2 rounded-lg bg-purple-600/30 text-purple-300 hover:bg-purple-600/50 transition-colors text-sm font-medium"
                  >
                    {selectedJudgment.aiExtractLoading ? <FiLoader className="animate-spin" /> : <FiZap />}
                    Extract Key Entities & Deadlines
                  </button>
                </div>

                {selectedJudgment.summary && (
                  <div className="p-4 rounded-xl bg-neutral-800/50 ring-1 ring-indigo-500/20">
                    <h3 className="font-semibold text-white mb-2 flex items-center gap-2">
                      <FaRobot className="text-indigo-400" /> AI Summary
                    </h3>
                    <p className="text-slate-300 whitespace-pre-wrap leading-relaxed">{selectedJudgment.summary}</p>
                  </div>
                )}

                {selectedJudgment.keyInformation && (
                  <div className="p-4 rounded-xl bg-neutral-800/50 ring-1 ring-purple-500/20">
                    <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
                      <FiZap className="text-purple-400" /> Structed Key Information
                    </h3>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {selectedJudgment.keyInformation.parties && selectedJudgment.keyInformation.parties.length > 0 && (
                        <div className="mb-3">
                          <h4 className="text-slate-400 mb-1 text-xs uppercase tracking-wider font-semibold">Parties:</h4>
                          <ul className="list-disc list-inside text-slate-300 text-sm">
                            {selectedJudgment.keyInformation.parties.map((party, i) => (
                              <li key={i}>{party.name || party} {party.role ? `(${party.role})` : ""}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {selectedJudgment.keyInformation.issues && selectedJudgment.keyInformation.issues.length > 0 && (
                        <div className="mb-3">
                          <h4 className="text-slate-400 mb-1 text-xs uppercase tracking-wider font-semibold">Issues / Claims:</h4>
                          <ul className="list-disc list-inside text-slate-300 text-sm">
                            {selectedJudgment.keyInformation.issues.map((issue, i) => (
                              <li key={i}>{issue}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {selectedJudgment.keyInformation.obligations && selectedJudgment.keyInformation.obligations.length > 0 && (
                        <div className="mb-3">
                          <h4 className="text-amber-400/80 mb-1 text-xs uppercase tracking-wider font-semibold">Obligations / Duties:</h4>
                          <ul className="list-disc list-inside text-amber-100/70 text-sm">
                            {selectedJudgment.keyInformation.obligations.map((obl, i) => (
                              <li key={i}>{obl}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {selectedJudgment.keyInformation.deadlines && selectedJudgment.keyInformation.deadlines.length > 0 && (
                        <div className="mb-3">
                          <h4 className="text-rose-400/80 mb-1 text-xs uppercase tracking-wider font-semibold">Decisions / Deadlines:</h4>
                          <ul className="list-disc list-inside text-rose-100/70 text-sm">
                            {selectedJudgment.keyInformation.deadlines.map((dl, i) => (
                              <li key={i}>{dl}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {selectedJudgment.fullText && (
                  <div className="p-4 rounded-xl bg-neutral-800/50">
                    <h3 className="font-semibold text-white mb-2">Full Text</h3>
                    <p className="text-slate-300 whitespace-pre-wrap max-h-[400px] overflow-y-auto">{selectedJudgment.fullText}</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}


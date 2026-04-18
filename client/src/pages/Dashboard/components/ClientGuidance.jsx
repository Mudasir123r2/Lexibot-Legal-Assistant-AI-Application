import { useState } from "react";
import { FiClipboard, FiLoader } from "react-icons/fi";
import { FaBookOpen, FaLightbulb } from "react-icons/fa";
import api from "../../../api/http";

export default function ClientGuidance() {
  const [caseType, setCaseType] = useState("");
  const [situationDescription, setSituationDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!caseType.trim() || !situationDescription.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const { data } = await api.post("/ai/guidance", {
        caseType,
        situationDescription
      });
      setResult(data);
    } catch (err) {
      console.error("Guidance error:", err);
      let errorMessage = "Failed to generate guidance. Please try again.";
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      }
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setCaseType("");
    setSituationDescription("");
    setResult(null);
    setError(null);
  };

  return (
    <div className="w-full h-full flex flex-col overflow-y-auto pb-10">
      {!result && !loading ? (
        <div className="max-w-4xl mx-auto w-full pt-8 px-4">
          <div className="mb-10 text-center">
            <h2 className="text-4xl font-display font-bold text-white mb-4 tracking-tight drop-shadow-lg">
              Client <span className="text-indigo-400">Guidance</span>
            </h2>
            <p className="text-slate-400 text-lg">
              Describe your client's situation to instantly generate procedural pathways, actionable steps, and documentation checklists based on relevant legal patterns.
            </p>
          </div>

          <div className="rounded-2xl ring-1 ring-white/10 bg-neutral-900/50 backdrop-blur-xl p-8 shadow-2xl relative overflow-hidden group">
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 via-transparent to-purple-500/5 opacity-50"></div>
            
            <form onSubmit={handleSubmit} className="relative space-y-6 flex flex-col">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="col-span-1 md:col-span-2">
                  <label className="block text-sm font-semibold text-slate-300 mb-2">
                    Select Legal Area / Case Type
                  </label>
                  <select
                    value={caseType}
                    onChange={(e) => setCaseType(e.target.value)}
                    className="w-full px-5 py-3.5 rounded-xl border border-white/10 bg-neutral-900/80 text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500/60 shadow-inner"
                    required
                  >
                    <option value="" disabled>Select the Type of Case</option>
                    <option value="Family - Divorce/Khula">Family Law - Divorce / Khula</option>
                    <option value="Family - Child Custody">Family Law - Child Custody</option>
                    <option value="Property Dispute">Property / Land Dispute</option>
                    <option value="Contract Breach">Commercial - Breach of Contract</option>
                    <option value="Criminal Defense">Criminal Defense</option>
                    <option value="Other">Other (Describe specifically below)</option>
                  </select>
                </div>

                <div className="col-span-1 md:col-span-2">
                  <label className="block text-sm font-semibold text-slate-300 mb-2 flex justify-between items-center">
                    <span>Situation Description <span className="text-rose-400">*</span></span>
                    <span className="text-xs font-normal text-indigo-400 font-mono">Factual Circumstances</span>
                  </label>
                  <textarea
                    value={situationDescription}
                    onChange={(e) => setSituationDescription(e.target.value)}
                    placeholder="E.g., My client's spouse wants to file for Khula, but they have a joint property and a 4-year-old child..."
                    rows="8"
                    required
                    className="w-full px-5 py-4 rounded-xl border border-white/10 bg-neutral-900/80 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/60 resize-none shadow-inner"
                  />
                </div>
              </div>

              {error && (
                <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-sm flex items-center justify-center font-medium shadow-sm">
                  {error}
                </div>
              )}

              <div className="pt-4 flex justify-end">
                <button
                  type="submit"
                  disabled={loading || !caseType || !situationDescription.trim()}
                  className="w-full md:w-auto px-10 py-4 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold text-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3 shadow-lg shadow-indigo-500/25 transition-all active:scale-[0.98]"
                >
                  <FiClipboard className="text-xl" /> Generate Guidance
                </button>
              </div>
            </form>
          </div>
        </div>
      ) : (
        <div className="max-w-4xl mx-auto w-full pt-8 px-4 flex flex-col">
          <div className="flex items-center justify-between xl:-ml-12 mb-8">
            <button
              onClick={handleReset}
              className="px-5 py-2.5 rounded-xl border border-white/10 bg-neutral-900/50 hover:bg-neutral-800 text-slate-300 font-medium transition-colors flex items-center gap-2 group backdrop-blur-md shadow-sm"
            >
              <span className="group-hover:-translate-x-1 transition-transform">←</span> Back to Editor
            </button>
          </div>

          {loading ? (
            <div className="rounded-2xl ring-1 ring-white/10 bg-neutral-900/50 backdrop-blur-xl p-16 shadow-2xl flex flex-col items-center justify-center min-h-[400px]">
              <FiLoader className="text-6xl text-indigo-500 animate-spin mb-6" />
              <h3 className="text-2xl font-bold text-white mb-2">Formulating Legal Guidance</h3>
              <p className="text-slate-400 text-lg">Cross-referencing core legal principles and developing a procedural pathway...</p>
            </div>
          ) : (
            <div className="rounded-2xl ring-1 ring-white/10 bg-neutral-900/50 backdrop-blur-xl shadow-2xl overflow-hidden flex flex-col">
              <div className="bg-neutral-800/80 px-8 py-6 border-b border-white/10 flex items-center justify-between">
                <h3 className="text-2xl font-bold text-white flex items-center gap-3">
                  <FaLightbulb className="text-indigo-400 text-3xl" /> 
                  Procedural Guidance Summary
                </h3>
                <span className="px-3 py-1 rounded-md bg-indigo-500/20 text-indigo-300 text-sm font-medium border border-indigo-500/20">
                  {result.caseType}
                </span>
              </div>
              
              <div className="p-8">
                  {/* Clean Plain Text Rendering */}
                  <div className="bg-neutral-900/50 rounded-xl p-8 border border-white/5 shadow-inner">
                    <div className="text-slate-300 text-base leading-relaxed whitespace-pre-wrap font-serif">
                       {result.guidance.replace(/\*/g, '')}
                    </div>
                  </div>

                  {/* Reference Sources */}
                  {result.similarCases && result.similarCases.length > 0 && (
                    <div className="mt-8 pt-6 border-t border-white/10">
                      <h4 className="text-sm font-bold text-white mb-4 uppercase tracking-wider flex items-center gap-2">
                        <FaBookOpen className="text-indigo-400" /> Grounded Case Precedents
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {result.similarCases.map((caseRef, idx) => (
                          <div key={idx} className="p-4 rounded-xl border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] transition-colors">
                            <div className="font-semibold text-slate-200 text-sm mb-1">{caseRef.title || caseRef.parties || 'Unnamed Case'}</div>
                            <div className="text-xs text-slate-400 flex flex-wrap gap-2 mb-2">
                              {caseRef.court && <span>🏢 {caseRef.court}</span>}
                              {caseRef.year && <span>📅 {caseRef.year}</span>}
                            </div>
                            {caseRef.citation && (
                              <div className="text-xs text-indigo-400 mt-2 pt-2 border-t border-white/5">
                                Citation: {caseRef.citation}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
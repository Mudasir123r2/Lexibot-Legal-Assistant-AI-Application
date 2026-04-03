import { useState } from "react";
import { FiClipboard, FiLoader, FiList, FiClock, FiAlertCircle } from "react-icons/fi";
import { FaBookOpen } from "react-icons/fa";
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

  return (
    <div className="h-full flex flex-col md:flex-row gap-6 p-4 sm:p-6 overflow-hidden">
      {/* Input Form Column */}
      <div className="w-full md:w-1/3 flex flex-col gap-4 overflow-y-auto pr-2">
        <div className="bg-neutral-900/50 backdrop-blur-xl rounded-2xl p-6 ring-1 ring-white/10 shadow-xl">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 bg-indigo-500/20 rounded-xl">
              <FiClipboard className="text-indigo-400 text-xl" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-white">Client Guidance</h2>
              <p className="text-sm text-slate-400">Generate checklists & timelines</p>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Legal Area / Case Type</label>
              <select
                value={caseType}
                onChange={(e) => setCaseType(e.target.value)}
                className="w-full rounded-xl border border-white/10 bg-neutral-800/50 text-slate-200 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
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

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Situation Description</label>
              <p className="text-xs text-slate-400 mb-2">Describe the specific factual circumstances so the AI can retrieve relevant procedural laws and precedents.</p>
              <textarea
                value={situationDescription}
                onChange={(e) => setSituationDescription(e.target.value)}
                rows={5}
                className="w-full rounded-xl border border-white/10 bg-neutral-800/50 text-slate-200 px-4 py-3 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 resize-none"
                placeholder="E.g., My spouse wants to file for Khula, but we have a joint property and a 4-year-old child..."
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading || !caseType || !situationDescription}
              className="w-full flex items-center justify-center gap-2 rounded-xl py-3 font-semibold text-white shadow-[0_8px_30px_rgba(99,102,241,0.35)]
                         bg-[linear-gradient(135deg,#4338CA_0%,#6D28D9_30%,#7C3AED_55%)] hover:shadow-[0_10px_40px_rgba(99,102,241,0.5)] disabled:opacity-50 transition-all"
            >
              {loading ? <FiLoader className="animate-spin text-lg" /> : <FiList className="text-lg" />}
              {loading ? "Generating Report..." : "Generate Guidance Checklist"}
            </button>
          </form>

          {error && (
            <div className="mt-4 p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm">
              {error}
            </div>
          )}
        </div>
      </div>

      {/* Results Column */}
      <div className="w-full md:w-2/3 flex flex-col overflow-y-auto pr-2">
        {!result && !loading ? (
          <div className="h-full rounded-2xl border border-white/5 border-dashed bg-white/[0.02] flex items-center justify-center text-slate-500 text-center p-8">
            <div>
              <FiClipboard className="text-4xl mx-auto mb-4 opacity-50" />
              <p className="text-lg font-medium text-slate-300">No Guidance Generated Yet</p>
              <p className="text-sm mt-2 max-w-sm">Select a category and describe your clients situation to instantly generate grounded legal pathways, documentation checklists, and procedural timelines based on relevant case law.</p>
            </div>
          </div>
        ) : loading ? (
          <div className="h-full rounded-2xl border border-white/5 bg-neutral-900/30 flex items-center justify-center p-8">
            <div className="text-center">
              <FiLoader className="text-4xl mx-auto mb-4 text-indigo-400 animate-spin" />
              <p className="text-lg font-medium text-slate-300">Researching Database...</p>
              <p className="text-sm text-slate-500 mt-2">Retrieving similar legal cases and formulating a structured timeline.</p>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="bg-neutral-900/50 backdrop-blur-xl rounded-2xl p-6 md:p-8 ring-1 ring-white/10 shadow-xl overflow-hidden animate-fade-in relative group">
              <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-indigo-500 to-purple-500"></div>

              <div className="flex justify-between items-start mb-6">
                <div>
                  <h3 className="text-2xl font-bold text-white mb-2">Procedural Guidance & Checklist</h3>
                  <div className="flex items-center gap-2">
                    <span className="px-2.5 py-1 rounded-md bg-indigo-500/20 text-indigo-300 text-xs font-medium border border-indigo-500/20">
                      {result.caseType}
                    </span>
                  </div>
                </div>
              </div>

              {/* RAG Rendered Markdown/Text Content */}
              <div className="prose prose-invert prose-indigo max-w-none text-slate-300">
                {result.guidance.split('\n').map((paragraph, index) => {
                  const txt = paragraph.trim();
                  if (!txt) return <div key={index} className="h-2"></div>;

                  if (txt.startsWith('Overview') || /^\d+\./.test(txt) || txt.startsWith('#') || txt.includes('Checklist')) {
                    const stripped = txt.replace(/#|\*/g, '').trim();
                    return <h4 key={index} className="text-lg font-bold text-white mt-6 mb-3 flex flex-wrap items-center gap-2">
                      {stripped.includes('Checklist') || stripped.includes('Document') ? <FiList className="text-indigo-400 shrink-0" /> :
                        stripped.includes('Time') || stripped.includes('Step') ? <FiClock className="text-indigo-400 shrink-0" /> :
                          stripped.includes('Important') || stripped.includes('Consideration') ? <FiAlertCircle className="text-rose-400 shrink-0" /> :
                            <FaBookOpen className="text-indigo-400 shrink-0" />}
                      <span>{stripped}</span>
                    </h4>;
                  }

                  if (txt.startsWith('-')) {
                    const content = txt.replace('-', '').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').trim();
                    return <li key={index} className="mb-2 ml-4 list-disc text-slate-300" dangerouslySetInnerHTML={{ __html: content }}></li>
                  }

                  const content = txt.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                  return <p key={index} className="mb-3 leading-relaxed break-words" dangerouslySetInnerHTML={{ __html: content }}></p>;
                })}
              </div>
            </div>

            {/* RAG Reference Sources */}
            {result.similarCases && result.similarCases.length > 0 && (
              <div className="bg-neutral-900/50 backdrop-blur-xl rounded-2xl p-6 ring-1 ring-white/10 shadow-xl animate-fade-in">
                <h4 className="text-sm font-bold text-white mb-4 uppercase tracking-wider flex items-center gap-2">
                  <FaBookOpen className="text-indigo-400" /> Grounded Database References
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {result.similarCases.map((caseRef, idx) => (
                    <div key={idx} className="p-4 rounded-xl border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] transition-colors">
                      <div className="font-semibold text-slate-200 text-sm mb-1">{caseRef.title || caseRef.parties || 'Unnamed Case'}</div>
                      <div className="text-xs text-slate-400 flex flex-wrap gap-2 mb-2">
                        {caseRef.court && <span>🏢 {caseRef.court}</span>}
                        {caseRef.year && <span>📅 {caseRef.year}</span>}
                        {caseRef.citation && <span className="text-indigo-400">{caseRef.citation}</span>}
                      </div>
                      <div className="text-xs text-slate-500 line-clamp-2 mt-2 pt-2 border-t border-white/5">
                        Similarity Score: {Math.round((caseRef.similarity || caseRef.score || 0) * 100)}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

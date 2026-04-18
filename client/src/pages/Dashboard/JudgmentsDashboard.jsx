import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import DashboardLayout from "../../layout/DashboardLayout";
import { FaBookOpen, FaGavel, FaRobot, FaSearch, FaArrowLeft, FaCalendar, FaTimes } from "react-icons/fa";
import { FiLoader, FiFileText } from "react-icons/fi";
import api from "../../api/http";
import ChatTab from "./components/ChatTab";

export default function JudgmentsDashboard() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [findInputText, setFindInputText] = useState("");
  const [filterYear, setFilterYear] = useState("");
  const [filterType, setFilterType] = useState("");
  const [loading, setLoading] = useState(false);
  const [judgments, setJudgments] = useState([]);
  const [selectedJudgment, setSelectedJudgment] = useState(null);
  const [showChatOverlay, setShowChatOverlay] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  // Custom Explain states
  const [pastedText, setPastedText] = useState("");

  const [pagination, setPagination] = useState({
    page: 1,
    limit: 10,
    total: 0
  });

  const handleFindSubmit = async () => {
    if (!findInputText.trim()) return;
    setLoading(true);
    setHasSearched(true);
    setSelectedJudgment(null); // Reset selection
    try {
      const params = {
        query: findInputText,
        page: pagination.page,
        limit: pagination.limit
      };
      if (filterYear) params.year = filterYear;
      if (filterType) params.caseType = filterType;

      console.log("SENDING REQUEST WITH PARAMS:", params);
      const response = await api.get('/judgments/search', { params });
      console.log("RECEIVED RESPONSE:", response.data);

      setJudgments(response.data.judgments);
      setPagination(response.data.pagination);
    } catch (error) {
      console.error("Error searching judgments:", error);
      setJudgments([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (hasSearched) {
      handleFindSubmit();
    }
  }, [pagination.page]);

  useEffect(() => {
    if (id) {
      fetchJudgmentDetails(id);
    } else {
      setSelectedJudgment(null);
    }
  }, [id]);

  const fetchJudgmentDetails = async (judgmentId) => {
    setLoading(true);
    try {
      const response = await api.get(`/judgments/${judgmentId}`);
      setSelectedJudgment({
        ...response.data,
        isCustom: false
      });
    } catch (error) {
      console.error("Error fetching judgment:", error);
      if (error.response && error.response.status === 404) {
        alert("This judgment's ID is outdated. Please refresh your search to get the latest results.");
      } else {
        alert("Failed to load full judgment details. Please check your connection.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleExplainSubmit = () => {
    if (!pastedText.trim()) return;
    setSelectedJudgment({
        title: "User Provided Text",
        content: pastedText,
        isCustom: true
    });
  };

  const renderReadableText = (content) => {
    // Total safety fallback
    let text = typeof content === 'string' ? content : (content?.fullText || content?.content || "");
    if (typeof text !== 'string') text = String(text);

    // Snip everything from JUDGMENT TEXT: onwards
    text = text.split(/(?:\n|^)\s*JUDGMENT TEXT[:\s-]?/i)[0].trim();

    if (!text || text.trim().length === 0) {
      return (
        <div className="flex flex-col items-center justify-center p-20 text-slate-500 border border-white/5 border-dashed rounded-2xl">
           <FiFileText className="text-4xl mb-2 opacity-20"/>
           <p>No document content available to display.</p>
        </div>
      );
    }

    const paragraphs = text.split(/\n+/).filter(p => p.trim().length > 0);
    return paragraphs.map((para, idx) => {
      // Clean any accidental markdown asterisks left by LLM
      const cleanPara = para.replace(/\*/g, '').trim();
      if (!cleanPara) return null;

      // Small title-like paragraphs (ALL CAPS, short)
      const isKnownHeader = /^(CASE TITLE|CITATION|COURT|DATE OF DECISION|JUDGES|LAWYERS|STATUTES|FACTS|ISSUE|REASONING|HOLDING|CONCLUSION)/.test(cleanPara);
      const isColonHeader = cleanPara.length < 60 && cleanPara.endsWith(':') && cleanPara === cleanPara.toUpperCase();
      const isHeader = isKnownHeader || isColonHeader;

      if (isHeader) {
         return (
           <div key={idx} className="w-full mt-6 mb-2">
             <h4 className="text-indigo-300 font-bold tracking-wider text-sm bg-white/5 inline-flex px-3 py-1 rounded-r-md border-l-2 border-indigo-500">
               {cleanPara}
             </h4>
           </div>
         );
      }
      return (
        <p key={idx} className="mb-3 leading-relaxed text-[16px] text-slate-300 font-serif text-justify tracking-wide selection:bg-indigo-500/30">
          {cleanPara}
        </p>
      );
    });
  };

  return (
    <DashboardLayout>
      <div className="relative flex-1 flex flex-col font-sans min-h-0">

        {/* If an ID exists but no judgment is loaded yet, show loading instead of search */}
        {id && !selectedJudgment ? (
          <div className="flex-1 flex flex-col items-center justify-center p-20">
            <FiLoader className="text-5xl text-indigo-500 animate-spin mb-4" />
            <p className="text-slate-400">Loading judgment details...</p>
          </div>
        ) : !selectedJudgment ? (
          <div className="flex-1 flex flex-col items-center justify-start overflow-y-auto w-full max-w-5xl mx-auto py-10 px-4 scrollbar-hide">

            <div className="w-full text-center mb-10">
              <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 tracking-tight drop-shadow-lg">
                Legal <span className="text-indigo-400">Workspace</span>
              </h1>
              <p className="text-slate-400 text-lg max-w-2xl mx-auto">
                Search through our comprehensive legal database or securely paste 
                your own complex legal documents for immediate AI analysis.
              </p>
            </div>

            {/* Premium Search Bar */}
            <div className="w-full relative shadow-2xl group mb-12">
              <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-rose-500 rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-1000"></div>
              <div className="relative flex items-center bg-neutral-900 ring-1 ring-white/10 rounded-2xl overflow-hidden p-2">
                <FaSearch className="text-indigo-400 text-2xl ml-4 mr-2" />
                <input
                  type="text"
                  value={findInputText}
                  onChange={(e) => setFindInputText(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleFindSubmit()}
                  placeholder="Enter keywords, party name, or case details..."
                  className="w-full bg-transparent border-none text-xl text-slate-200 placeholder:text-slate-500 focus:outline-none focus:ring-0 p-4 h-16"
                />
                <button
                  onClick={() => { setPagination(p => ({ ...p, page: 1 })); handleFindSubmit(); }}
                  disabled={!findInputText.trim() || loading}
                  className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-neutral-800 disabled:text-slate-500 text-white px-8 py-3 rounded-xl font-bold text-lg transition-all shadow-lg"
                >
                  {loading && !judgments.length ? "Searching..." : "Search"}
                </button>
              </div>
            </div>

            {/* Filter Bar */}
            <div className="w-full flex flex-col md:flex-row gap-4 mb-10 -mt-6">
               <div className="flex-1 flex items-center bg-neutral-900/50 ring-1 ring-white/5 rounded-xl px-4 py-3 shadow-md">
                 <FaBookOpen className="text-indigo-400 mr-3 text-lg" />
                 <select
                   value={filterType}
                   onChange={e => setFilterType(e.target.value)}
                   className="w-full bg-transparent border-none text-slate-300 focus:outline-none focus:ring-0"
                 >
                   <option value="" className="bg-neutral-900 text-slate-300">All Judgment Types</option>
                   <option value="Civil Appeal" className="bg-neutral-900 text-slate-300">Civil Appeal</option>
                   <option value="Criminal Appeal" className="bg-neutral-900 text-slate-300">Criminal Appeal</option>
                   <option value="Constitution Petition" className="bg-neutral-900 text-slate-300">Constitution Petition</option>
                 </select>
               </div>
               <div className="flex-1 flex items-center bg-neutral-900/50 ring-1 ring-white/5 rounded-xl px-4 py-3 shadow-md">
                 <FaCalendar className="text-indigo-400 mr-3 text-lg" />
                 <select
                   value={filterYear}
                   onChange={e => setFilterYear(e.target.value)}
                   className="w-full bg-transparent border-none text-slate-300 focus:outline-none focus:ring-0"
                 >
                   <option value="" className="bg-neutral-900 text-slate-300">Any Year</option>
                   {Array.from({ length: 80 }, (_, i) => new Date().getFullYear() - i).map(year => (
                     <option key={year} value={year} className="bg-neutral-900 text-slate-300">{year}</option>
                   ))}
                 </select>
               </div>
            </div>

            {/* Custom Paste Section Mini-Banner - HIDDEN 
            <div className="w-full bg-neutral-900/50 rounded-xl p-6 ring-1 ring-white/5 shadow-xl mb-12 flex flex-col md:flex-row gap-6 items-center justify-between border-l-4 border-rose-500">
              <div className="flex-1">
                 <h3 className="text-white font-bold text-lg flex items-center gap-2 mb-1">
                   <FiFileText className="text-rose-400"/> Custom Document Analysis
                 </h3>
                 <p className="text-sm text-slate-400">Have a physical document or unlisted case? Paste your text below to open an isolated AI analysis workspace.</p>
              </div>
              <div className="flex-[2] w-full flex gap-2">
                <input 
                  value={pastedText}
                  onChange={(e) => setPastedText(e.target.value)}
                  placeholder="Paste your legal text here..."
                  className="flex-1 bg-black/40 border border-white/10 rounded-lg p-3 text-slate-300 focus:outline-none focus:ring-1 focus:ring-rose-500 text-sm"
                />
                <button onClick={handleExplainSubmit} disabled={!pastedText.trim() || pastedText.length > 30000} className="bg-rose-600 hover:bg-rose-500 disabled:opacity-50 text-white px-6 py-2 rounded-lg font-bold text-sm transition-all whitespace-nowrap">
                   Analyze Text
                </button>
              </div>
            </div>
            */}

            {/* Results Section */}
            {hasSearched && (
              <div className="w-full flex flex-col gap-4 animate-in fade-in slide-in-from-bottom-6 duration-500">
                <div className="flex items-center justify-between mb-2">
                  <h2 className="text-xl font-bold text-white">Search Results</h2>
                  <span className="text-sm text-slate-400">Found {pagination.total} precedents</span>
                </div>

                {judgments.length === 0 && !loading && (
                    <div className="text-center p-12 bg-neutral-900/40 rounded-2xl border border-white/5 border-dashed">
                      <FaSearch className="text-4xl text-slate-600 mx-auto mb-4" />
                      <h3 className="text-lg font-bold text-slate-300 mb-1">No judgments found</h3>
                      <p className="text-sm text-slate-500">Try modifying your keywords or removing filters.</p>
                    </div>
                )}

                {loading && judgments.length === 0 ? (
                    <div className="flex justify-center p-12"><FiLoader className="text-4xl text-indigo-500 animate-spin" /></div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {judgments.map((judgment) => (
                        <div
                          key={judgment._id}
                          onClick={() => navigate(`/judgments/${judgment._id}`)}
                          className="bg-neutral-900/60 hover:bg-neutral-800 rounded-xl p-5 ring-1 ring-white/10 hover:ring-indigo-500/50 cursor-pointer transition-all duration-200 group flex flex-col shadow-lg"
                        >
                          <h4 className="text-white text-lg font-bold mb-3 leading-snug group-hover:text-indigo-300 transition-colors line-clamp-3">
                            {judgment.title}
                          </h4>
                          <div className="mt-4 pt-4 border-t border-white/10 flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-slate-300 font-medium">
                            <div className="w-full flex flex-col gap-1.5 mb-2">
                               {/* Key IDs */}
                               <div className="flex flex-wrap gap-3">
                                 {judgment.journal && <span className="flex items-center gap-1 text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded"><FiFileText size={12}/> <b>Journal:</b> {judgment.journal}</span>}
                                 {judgment.caseNumber && judgment.caseNumber !== "N/A" && <span className="flex items-center gap-1 text-sky-400 bg-sky-400/10 px-2 py-1 rounded"><FiFileText size={12}/> <b>Appeal No:</b> {judgment.caseNumber}</span>}
                               </div>

                               {/* People / Parties */}
                               {judgment.parties && <span className="flex items-center gap-1.5 text-indigo-300 truncate w-full" title={judgment.parties}><FiFileText className="shrink-0"/> <span className="font-semibold text-slate-400">Parties:</span> {judgment.parties}</span>}
                               {judgment.lawyers && <span className="flex items-center gap-1.5 text-rose-300 line-clamp-1 w-full" title={judgment.lawyers}><FiFileText className="shrink-0"/> <span className="font-semibold text-slate-400">Lawyers:</span> {judgment.lawyers}</span>}

                               {/* Meta Facts */}
                               {judgment.statutes && <span className="flex items-center gap-1.5 text-amber-300 line-clamp-1 w-full" title={judgment.statutes}><FiFileText className="shrink-0"/> <span className="font-semibold text-slate-400">Statutes:</span> {judgment.statutes}</span>}
                            </div>

                            <div className="w-full flex items-center justify-between text-slate-400 border-t border-white/5 pt-2 mt-1">
                               <span className="flex items-center gap-1.5"><FaGavel className="text-slate-500"/> {judgment.court || 'Court N/A'}</span>
                               <span className="flex items-center gap-1.5"><FaCalendar className="text-slate-500"/> {judgment.year && judgment.year !== 'Unknown' ? judgment.year : (judgment.dateOfJudgment ? (isNaN(new Date(judgment.dateOfJudgment)) ? judgment.dateOfJudgment : new Date(judgment.dateOfJudgment).getFullYear()) : 'Year N/A')}</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                )}

                {/* Clean Pagination */}
                {pagination.total > pagination.limit && !loading && (
                  <div className="flex justify-center items-center gap-4 mt-8 mb-10">
                     <button onClick={() => setPagination(p => ({...p, page: p.page - 1}))} disabled={pagination.page===1} className="px-4 py-2 rounded-lg bg-neutral-900 ring-1 ring-white/10 text-sm font-semibold hover:bg-neutral-800 disabled:opacity-30 text-white transition-all">Previous</button>
                     <span className="text-sm font-bold text-slate-400">Page {pagination.page} of {Math.ceil(pagination.total/pagination.limit)}</span>
                     <button onClick={() => setPagination(p => ({...p, page: p.page + 1}))} disabled={pagination.page>=Math.ceil(pagination.total/pagination.limit)} className="px-4 py-2 rounded-lg bg-neutral-900 ring-1 ring-white/10 text-sm font-semibold hover:bg-neutral-800 disabled:opacity-30 text-white transition-all">Next</button>
                  </div>
                )}
              </div>
            )}
          </div>
        ) : (

          /* STATE 2: DEEP ANALYSIS WORKSPACE (SPLIT SCREEN) */
          <div className="fixed inset-0 z-[100] flex flex-col bg-black overflow-hidden opacity-100 animate-fade-in w-screen h-screen">
            {/* Top Bar Navigation */}
            <div className="h-16 shrink-0 bg-neutral-900 ring-1 ring-white/10 px-4 flex items-center justify-between z-10 shadow-md">
               <button 
                 onClick={() => {
                   if (window.history.state && window.history.state.idx > 0) {
                     navigate(-1);
                   } else {
                     navigate('/judgments');
                   }
                 }} 
                 className="flex items-center gap-2 text-sm font-bold text-slate-300 hover:text-white bg-black/40 hover:bg-white/10 px-4 py-2 rounded-lg transition-colors ring-1 ring-white/5"
               >
                 <FaArrowLeft /> Back to Search Results
               </button>
               <div className="flex items-center gap-3">
                  <span className="text-xs font-bold uppercase tracking-widest text-emerald-400 bg-emerald-400/10 px-3 py-1 rounded-full ring-1 ring-emerald-400/30">
                    Analysis Mode Active
                  </span>
               </div>
            </div>

            {/* Split Panels */}
            <div className="flex-1 flex overflow-hidden min-h-0">

               {/* Left: Document Reader (Full Screen) */}
               <div className="flex-1 w-full bg-[#1a1c23] overflow-y-auto p-8 lg:p-12 relative scrollbar-hide">
                  <div className="max-w-5xl mx-auto transition-all duration-300">
                     <h2 className="text-3xl font-bold text-white mb-6 leading-tight pb-6 border-b border-white/10">
                        {selectedJudgment.title}
                     </h2>
                     {!selectedJudgment.isCustom && (
                       <div className="flex flex-col gap-3 text-sm text-slate-400/80 mb-10 bg-neutral-900/50 p-5 rounded-xl ring-1 ring-white/5 shadow-inner">
                         <div className="flex flex-wrap items-center gap-6 pb-3 border-b border-white/5">
                           <span className="flex items-center gap-2 font-medium"><FaGavel className="text-indigo-400" /> Court: <span className="text-slate-300">{selectedJudgment.court || 'N/A'}</span></span>
                           <span className="flex items-center gap-2 font-medium"><FaCalendar className="text-indigo-400" /> Date: <span className="text-slate-300">{selectedJudgment.dateOfJudgment ? (isNaN(new Date(selectedJudgment.dateOfJudgment)) ? selectedJudgment.dateOfJudgment : new Date(selectedJudgment.dateOfJudgment).toLocaleDateString()) : 'N/A'}</span></span>
                           <span className="flex items-center gap-2 font-medium"><FiFileText className="text-indigo-400" /> Ref: <span className="text-slate-300">{selectedJudgment.caseNumber || 'N/A'}</span></span>
                         </div>
                         <div className="flex flex-col gap-4 pt-1">
                           {(selectedJudgment.journal || selectedJudgment.citation) && <span className="flex items-start gap-2 font-medium"><FiFileText className="text-emerald-400 mt-1" /> Journal: <span className="text-slate-300">{selectedJudgment.journal || selectedJudgment.citation}</span></span>}
                           {selectedJudgment.lawyers && <span className="flex items-start gap-2 font-medium"><FiFileText className="text-rose-400 mt-1" /> Lawyers: <span className="text-slate-300 max-w-full leading-relaxed" title="Lawyers">{selectedJudgment.lawyers}</span></span>}
                           {selectedJudgment.statutes && <span className="flex items-start gap-2 font-medium"><FiFileText className="text-amber-400 mt-1" /> Statutes: <span className="text-slate-300 max-w-full leading-relaxed" title="Statutes">{selectedJudgment.statutes}</span></span>}
                         </div>
                       </div>
                     )}

                     <div className="prose prose-invert max-w-none text-slate-300 pb-32">
                        {renderReadableText(selectedJudgment.fullText || selectedJudgment.content)}
                     </div>
                  </div>
               </div>

               {/* Right: LexiBot Chat (Overlay) */}
               {showChatOverlay && (
                 <>
                   {/* Optional blur/dim backdrop */}
                   <div 
                     className="fixed inset-0 z-[110] bg-black/40 backdrop-blur-sm transition-opacity" 
                     onClick={() => setShowChatOverlay(false)}
                   />

                   <div className="fixed right-0 inset-y-0 z-[120] w-full sm:w-1/2 lg:w-1/2 border-l border-white/10 bg-neutral-900/95 shadow-[rgba(0,0,0,0.8)_-20px_0_50px] flex flex-col overflow-hidden animate-slide-in-right">
                     <div className="h-[70px] px-4 border-b border-white/5 bg-black/40 flex items-center shadow-sm shrink-0 backdrop-blur-md">
                       <div className="flex items-center gap-4 w-full">
                         <button 
                           onClick={() => setShowChatOverlay(false)}
                           className="p-2 hover:bg-white/10 rounded-lg text-slate-400 hover:text-white transition-colors"
                           title="Close Chat"
                         >
                           <FaTimes className="text-xl" />
                         </button>
                         <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center ring-2 ring-black shadow-[0_0_10px_rgba(99,102,241,0.5)] shrink-0">
                            <FaRobot className="text-white text-lg" />
                         </div>
                         <div className="flex flex-col">
                           <h3 className="font-bold text-white text-base tracking-wide">LexiBot Assistant</h3>
                           <p className="text-[10px] text-emerald-400 mt-0.5 tracking-wider uppercase font-semibold">
                             Document Context Locked
                           </p>
                         </div>
                       </div>
                     </div>

                     <div className="flex-1 relative min-h-0 bg-[#121318]/90">
                       <div className="absolute inset-0 h-full w-full flex">
                         <ChatTab 
                           hideSidebar={false} 
                           contextData={selectedJudgment ? { 
                             judgmentId: selectedJudgment._id, 
                             title: selectedJudgment.title,
                             explicitTextContext: selectedJudgment.isCustom 
                               ? selectedJudgment.content 
                               : (selectedJudgment.fullText || selectedJudgment.content || null),
                             queryType: "single_document"
                           } : null}
                           selectedDocAvailable={!!selectedJudgment}
                         />
                       </div>
                     </div>
                   </div>
                 </>
               )}

               {/* Floating Action Button */}
               {!showChatOverlay && (
                 <button
                   onClick={() => setShowChatOverlay(true)}
                   className="fixed bottom-8 left-8 z-[150] w-14 h-14 bg-gradient-to-br from-indigo-600 to-purple-700 hover:from-indigo-500 hover:to-purple-600 rounded-full flex items-center justify-center shadow-[0_0_20px_rgba(99,102,241,0.6)] hover:shadow-[0_0_30px_rgba(99,102,241,0.8)] hover:scale-105 transition-all text-white"
                   title="Open LexiBot Assistant"
                 >
                   <FaRobot className="text-2xl" />
                 </button>
               )}

            </div>
          </div>
        )}

      </div>
    </DashboardLayout>
  );
}
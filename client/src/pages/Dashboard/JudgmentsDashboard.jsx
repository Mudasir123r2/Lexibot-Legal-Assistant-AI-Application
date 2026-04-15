import { useState, useEffect } from "react";
import DashboardLayout from "../../layout/DashboardLayout";
import { FaBookOpen, FaGavel, FaRobot, FaSearch, FaArrowLeft, FaCalendar } from "react-icons/fa";
import { FiLoader, FiFileText } from "react-icons/fi";
import api from "../../api/http";
import ChatTab from "./components/ChatTab";

export default function JudgmentsDashboard() {
  const [findInputText, setFindInputText] = useState("");
  const [loading, setLoading] = useState(false);
  const [judgments, setJudgments] = useState([]);
  const [selectedJudgment, setSelectedJudgment] = useState(null);
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
      const response = await api.get('/judgments/search', {
        params: {
          query: findInputText,
          page: pagination.page,
          limit: pagination.limit
        }
      });
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

  const fetchJudgmentDetails = async (id) => {
    setLoading(true);
    try {
      const response = await api.get(`/judgments/${id}`);
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
        
        {/* STATE 1: SEARCH AND DISCOVERY VIEW */}
        {!selectedJudgment ? (
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

            {/* Custom Paste Section Mini-Banner */}
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
                          onClick={() => fetchJudgmentDetails(judgment._id)}
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
                               <span className="flex items-center gap-1.5"><FaCalendar className="text-slate-500"/> {judgment.dateOfJudgment ? (isNaN(new Date(judgment.dateOfJudgment)) ? 'N/A' : new Date(judgment.dateOfJudgment).getFullYear()) : 'Year N/A'}</span>
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
          <div className="flex-1 flex flex-col w-full h-full bg-black overflow-hidden z-[50] opacity-100">
            {/* Top Bar Navigation */}
            <div className="h-16 shrink-0 bg-neutral-900 ring-1 ring-white/10 px-4 flex items-center justify-between z-10 shadow-md">
               <button 
                 onClick={() => setSelectedJudgment(null)} 
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
            <div className="flex-1 flex min-h-0">
               
               {/* Left: Document Reader (70%) */}
               <div className="flex-[7] bg-[#1a1c23] overflow-y-auto p-8 relative scrollbar-hide">
                  <div className="max-w-4xl mx-auto">
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

               {/* Right: LexiBot Chat (30%) */}
               <div className="flex-[3] min-w-[400px] border-l border-white/10 bg-neutral-900/80 flex flex-col shadow-[rgba(0,0,0,0.5)_-10px_0_25px]">
                 <div className="p-4 border-b border-white/5 bg-black/20 flex flex-col items-center justify-center pt-6 pb-6 shadow-sm">
                   <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center ring-4 ring-black shadow-[0_0_15px_rgba(99,102,241,0.5)] mb-3">
                      <FaRobot className="text-white text-xl" />
                   </div>
                   <h3 className="font-bold text-white text-lg tracking-wide">LexiBot</h3>
                   <p className="text-xs text-slate-400 text-center mt-1 max-w-[250px]">
                     Your context is rigidly locked to this exact document. Ask me anything about it.
                   </p>
                 </div>
                 
                 <div className="flex-1 max-h-full overflow-hidden relative">
                   <ChatTab 
                     hideSidebar={true} 
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
          </div>
        )}
        
      </div>
    </DashboardLayout>
  );
}


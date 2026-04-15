import DashboardLayout from "../../layout/DashboardLayout";
import { useState, useEffect } from "react";
import { FaPlus, FaEdit, FaTrash, FaSearch, FaTimes, FaGavel, FaRegClock, FaCheckCircle, FaExclamationCircle } from "react-icons/fa";
import { FiLoader, FiMoreVertical } from "react-icons/fi";
import api from "../../api/http";

export default function CasesDashboard() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Drawer States
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [editingCase, setEditingCase] = useState(null);
  
  const [searchQuery, setSearchQuery] = useState("");
  const [filterType, setFilterType] = useState("all");
  
  const [formData, setFormData] = useState({
    title: "",
    caseType: "Civil",
    description: "",
    filingDate: "",
    hearingDate: "",
    deadline: "",
    plaintiff: "",
    defendant: "",
    status: "Active",
    tags: ""
  });

  useEffect(() => {
    fetchCases();
  }, []);

  const fetchCases = async () => {
    try {
      setLoading(true);
      const { data } = await api.get("/cases");
      setCases(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Error fetching cases:", err);
    } finally {
      setLoading(false);
    }
  };

  const openDrawer = (caseItem = null) => {
    if (caseItem) {
      setEditingCase(caseItem);
      setFormData({
        title: caseItem.title || "",
        caseType: caseItem.caseType || "Civil",
        description: caseItem.description || "",
        status: caseItem.status || "Active",
        filingDate: caseItem.filingDate ? new Date(caseItem.filingDate).toISOString().split("T")[0] : "",
        hearingDate: caseItem.hearingDate ? new Date(caseItem.hearingDate).toISOString().split("T")[0] : "",
        deadline: caseItem.deadline ? new Date(caseItem.deadline).toISOString().split("T")[0] : "",
        plaintiff: caseItem.plaintiff || "",
        defendant: caseItem.defendant || "",
        tags: (caseItem.tags || []).join(", ")
      });
    } else {
      setEditingCase(null);
      setFormData({
        title: "",
        caseType: "Civil",
        description: "",
        status: "Active",
        filingDate: "",
        hearingDate: "",
        deadline: "",
        plaintiff: "",
        defendant: "",
        tags: ""
      });
    }
    setIsDrawerOpen(true);
  };

  const closeDrawer = () => {
    setIsDrawerOpen(false);
    setTimeout(() => {
      setEditingCase(null);
    }, 300); // Wait for transition
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingCase) {
        await api.put(`/cases/${editingCase._id}`, formData);
      } else {
        await api.post("/cases", {
          ...formData,
          tags: formData.tags.split(",").map(t => t.trim()).filter(t => t)
        });
      }
      closeDrawer();
      fetchCases();
    } catch (err) {
      console.error("Error saving case:", err);
      alert(err.response?.data?.message || "Failed to save case");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you critically sure you want to permanently delete this case?")) return;
    try {
      await api.delete(`/cases/${id}`);
      fetchCases();
    } catch (err) {
      console.error("Error deleting case:", err);
      alert("Failed to delete case");
    }
  };

  const filteredCases = cases.filter(c => {
    const matchesSearch = !searchQuery || 
      (c.title || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
      (c.plaintiff || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
      (c.defendant || "").toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = filterType === "all" || c.status === filterType;
    return matchesSearch && matchesFilter;
  });

  const getStatusStyle = (status) => {
    switch(status) {
        case "Active": return "bg-emerald-500/10 text-emerald-400 ring-emerald-500/30";
        case "Pending": return "bg-amber-500/10 text-amber-400 ring-amber-500/30";
        case "Closed": return "bg-slate-500/10 text-slate-400 ring-slate-500/30";
        case "Archived": return "bg-purple-500/10 text-purple-400 ring-purple-500/30";
        default: return "bg-indigo-500/10 text-indigo-400 ring-indigo-500/30";
    }
  };

  return (
    <DashboardLayout>
      <div className="relative w-full h-full flex flex-col px-2 font-sans">
        
        {/* Header Section */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 shrink-0 gap-4">
          <div>
            <h1 className="text-3xl font-bold text-white mb-1 tracking-tight">Legal Matters</h1>
            <p className="text-slate-400 text-sm">Monitor case statuses, schedules, and active litigation profiles</p>
          </div>
          <button
            onClick={() => openDrawer()}
            className="flex items-center gap-2 px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold shadow-[0_0_15px_rgba(79,70,229,0.3)] transition-all"
          >
            <FaPlus /> Open New Matter
          </button>
        </div>

        {/* Toolbar: Search & Filter */}
        <div className="flex flex-col sm:flex-row gap-4 shrink-0 mb-6 bg-neutral-900/40 p-2 rounded-2xl ring-1 ring-white/5">
          <div className="flex-1 relative">
            <FaSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              placeholder="Search by case title, plaintiff, or defendant..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-11 pr-4 py-3 rounded-xl border-none bg-transparent text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500/50"
            />
          </div>
          <div className="w-[1px] bg-white/10 hidden sm:block mx-1"></div>
          <div className="relative pr-2">
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="w-full sm:w-48 px-4 py-3 appearance-none cursor-pointer rounded-xl border-none bg-transparent text-slate-300 font-medium focus:outline-none focus:ring-1 focus:ring-indigo-500/50"
            >
              <option value="all" className="bg-neutral-900">All Statuses</option>
              <option value="Active" className="bg-neutral-900">Active</option>
              <option value="Pending" className="bg-neutral-900">Pending</option>
              <option value="Closed" className="bg-neutral-900">Closed</option>
              <option value="Archived" className="bg-neutral-900">Archived</option>
            </select>
          </div>
        </div>

        {/* Data Table */}
        <div className="flex-1 overflow-auto bg-neutral-900/30 rounded-2xl ring-1 ring-white/10 shadow-xl relative">
          {loading ? (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/20">
              <FiLoader className="h-10 w-10 text-indigo-500 animate-spin mb-4" />
              <p className="text-slate-400 font-medium">Fetching cases...</p>
            </div>
          ) : filteredCases.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full py-20 text-slate-400">
              <FaGavel className="text-6xl text-slate-700 mx-auto mb-4" />
              <p className="text-lg font-bold text-white mb-1">No matters found</p>
              <p className="text-sm">Try adjusting your filters or create a new case.</p>
            </div>
          ) : (
            <table className="w-full text-left border-collapse">
              <thead className="bg-[#1a1c23] sticky top-0 z-10 shadow-sm border-b border-white/10 text-slate-400 text-xs uppercase tracking-wider font-semibold">
                <tr>
                  <th className="px-6 py-4">Case Details</th>
                  <th className="px-6 py-4">Parties</th>
                  <th className="px-6 py-4">Important Dates</th>
                  <th className="px-6 py-4">Status & Type</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {filteredCases.map((c) => (
                  <tr key={c._id} className="hover:bg-white/[0.02] transition-colors group">
                    {/* Case Info */}
                    <td className="px-6 py-4">
                      <div className="font-bold text-white text-base mb-1">{c.title}</div>
                      <div className="text-xs text-slate-500 line-clamp-1 max-w-xs" title={c.description}>
                        {c.description || "No description provided."}
                      </div>
                    </td>
                    
                    {/* Parties */}
                    <td className="px-6 py-4">
                      <div className="flex flex-col text-sm">
                        <span className="text-indigo-300 font-medium whitespace-nowrap"><span className="text-slate-500 mr-2">P:</span>{c.plaintiff || "N/A"}</span>
                        <span className="text-rose-300 font-medium whitespace-nowrap"><span className="text-slate-500 mr-2">D:</span>{c.defendant || "N/A"}</span>
                      </div>
                    </td>
                    
                    {/* Dates */}
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex flex-col gap-1 text-sm text-slate-300">
                        {c.hearingDate ? (
                          <div className="flex items-center gap-2"><FaRegClock className="text-amber-400"/> {new Date(c.hearingDate).toLocaleDateString()}</div>
                        ) : (
                          <div className="text-slate-600 italic text-xs">No active hearing</div>
                        )}
                        <div className="text-xs text-slate-500">Filed: {c.filingDate ? new Date(c.filingDate).toLocaleDateString() : 'Unknown'}</div>
                      </div>
                    </td>
                    
                    {/* Status & Type */}
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex flex-col items-start gap-2">
                        <span className={`px-3 py-1 rounded-full text-xs font-bold ring-1 ${getStatusStyle(c.status)}`}>
                          {c.status}
                        </span>
                        <span className="text-xs font-medium text-slate-400 bg-black/20 px-2 py-0.5 rounded border border-white/5">
                          {c.caseType}
                        </span>
                      </div>
                    </td>
                    
                    {/* Actions */}
                    <td className="px-6 py-4 text-right whitespace-nowrap">
                      <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                         <button onClick={() => openDrawer(c)} className="p-2 text-slate-400 hover:text-indigo-400 hover:bg-indigo-500/10 rounded-lg transition-colors" title="Edit Matter">
                           <FaEdit />
                         </button>
                         <button onClick={() => handleDelete(c._id)} className="p-2 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors" title="Delete Matter">
                           <FaTrash />
                         </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Slide-out Drawer Overlay */}
        <div className={`fixed inset-0 bg-black/60 backdrop-blur-sm z-40 transition-opacity duration-300 ${isDrawerOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'}`} onClick={closeDrawer}></div>
        
        {/* Slide-out Drawer Container */}
        <div className={`fixed top-0 right-0 h-full w-full sm:w-[500px] bg-neutral-900 border-l border-white/10 z-50 transform transition-transform duration-300 ease-in-out shadow-2xl flex flex-col ${isDrawerOpen ? 'translate-x-0' : 'translate-x-full'}`}>
          
          <div className="flex justify-between items-center p-6 border-b border-white/5 bg-black/20 shrink-0">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              {editingCase ? <FaEdit className="text-indigo-400"/> : <FaPlus className="text-indigo-400"/>}
              {editingCase ? "Edit Legal Matter" : "Establish New Matter"}
            </h2>
            <button onClick={closeDrawer} className="p-2 bg-white/5 hover:bg-white/10 text-slate-300 rounded-full transition-colors">
              <FaTimes />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-6 custom-scrollbar">
            <form id="caseForm" onSubmit={handleSubmit} className="space-y-6">
              
              <div className="space-y-4">
                <h3 className="text-xs font-bold uppercase text-slate-500 tracking-wider">Primary Details</h3>
                <div className="space-y-4 bg-black/20 p-4 rounded-xl ring-1 ring-white/5">
                  <div>
                    <label className="block text-sm font-semibold text-slate-300 mb-1.5">Matter Title / Name <span className="text-rose-500">*</span></label>
                    <input type="text" required value={formData.title} onChange={(e) => setFormData({ ...formData, title: e.target.value })} className="w-full px-4 py-2.5 rounded-lg border border-white/10 bg-neutral-900 text-slate-100 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50 placeholder:text-slate-600" placeholder="e.g. Smith Estate Dispute" />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-300 mb-1.5">Description (Summary)</label>
                    <textarea value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} rows="3" className="w-full px-4 py-2.5 rounded-lg border border-white/10 bg-neutral-900 text-slate-100 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50 resize-none placeholder:text-slate-600" placeholder="Brief outline of the case facts..."/>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-xs font-bold uppercase text-slate-500 tracking-wider">Classification</h3>
                <div className="grid grid-cols-2 gap-4 bg-black/20 p-4 rounded-xl ring-1 ring-white/5">
                  <div>
                    <label className="block text-sm font-semibold text-slate-300 mb-1.5">Category</label>
                    <select value={formData.caseType} onChange={(e) => setFormData({ ...formData, caseType: e.target.value })} className="w-full px-4 py-2.5 rounded-lg border border-white/10 bg-neutral-900 text-slate-100 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50">
                      <option value="Civil">Civil</option>
                      <option value="Criminal">Criminal</option>
                      <option value="Family">Family</option>
                      <option value="Corporate">Corporate</option>
                      <option value="Property">Property</option>
                      <option value="Contract">Contract</option>
                      <option value="Employment">Employment</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-300 mb-1.5">Current Status</label>
                    <select value={formData.status} onChange={(e) => setFormData({ ...formData, status: e.target.value })} className="w-full px-4 py-2.5 rounded-lg border border-white/10 bg-neutral-900 text-slate-100 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50">
                      <option value="Active">Active</option>
                      <option value="Pending">Pending</option>
                      <option value="Closed">Closed</option>
                      <option value="Archived">Archived</option>
                    </select>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-xs font-bold uppercase text-slate-500 tracking-wider">Parties Involved</h3>
                <div className="grid grid-cols-2 gap-4 bg-black/20 p-4 rounded-xl ring-1 ring-white/5">
                  <div>
                    <label className="block text-sm font-semibold text-slate-300 mb-1.5 text-indigo-400">Plaintiff</label>
                    <input type="text" value={formData.plaintiff} onChange={(e) => setFormData({ ...formData, plaintiff: e.target.value })} className="w-full px-4 py-2.5 rounded-lg border border-white/10 bg-neutral-900 text-slate-100 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50" placeholder="Full Name or Entity" />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-300 mb-1.5 text-rose-400">Defendant</label>
                    <input type="text" value={formData.defendant} onChange={(e) => setFormData({ ...formData, defendant: e.target.value })} className="w-full px-4 py-2.5 rounded-lg border border-white/10 bg-neutral-900 text-slate-100 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50" placeholder="Full Name or Entity" />
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-xs font-bold uppercase text-slate-500 tracking-wider">Critical Timeline</h3>
                <div className="space-y-4 bg-black/20 p-4 rounded-xl ring-1 ring-white/5">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-semibold text-slate-300 mb-1.5">Filing Date</label>
                      <input type="date" value={formData.filingDate} onChange={(e) => setFormData({ ...formData, filingDate: e.target.value })} className="w-full px-4 py-2.5 rounded-lg border border-white/10 bg-neutral-900 text-slate-100 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50" style={{colorScheme: 'dark'}}/>
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-slate-300 mb-1.5 text-amber-400">Next Hearing</label>
                      <input type="date" value={formData.hearingDate} onChange={(e) => setFormData({ ...formData, hearingDate: e.target.value })} className="w-full px-4 py-2.5 rounded-lg border border-white/10 bg-neutral-900 text-slate-100 focus:outline-none focus:border-amber-500/50 focus:ring-1 focus:ring-amber-500/50" style={{colorScheme: 'dark'}}/>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-300 mb-1.5">Statute Deadline</label>
                    <input type="date" value={formData.deadline} onChange={(e) => setFormData({ ...formData, deadline: e.target.value })} className="w-full px-4 py-2.5 rounded-lg border border-white/10 bg-neutral-900 text-slate-100 focus:outline-none focus:border-rose-500/50 focus:ring-1 focus:ring-rose-500/50" style={{colorScheme: 'dark'}}/>
                  </div>
                </div>
              </div>

            </form>
          </div>

          <div className="p-6 border-t border-white/5 bg-neutral-900 shrink-0 flex gap-4">
             <button type="button" onClick={closeDrawer} className="flex-1 px-4 py-3 rounded-xl border border-white/10 bg-transparent hover:bg-white/5 text-slate-300 font-bold transition-all">
               Cancel
             </button>
             <button type="submit" form="caseForm" className="flex-1 px-4 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold shadow-lg transition-all">
               {editingCase ? "Save Updates" : "Create Matter"}
             </button>
          </div>
          
        </div>

      </div>
    </DashboardLayout>
  );
}

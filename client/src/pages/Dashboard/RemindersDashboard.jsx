import DashboardLayout from "../../layout/DashboardLayout";
import { useState, useEffect } from "react";
import { FaPlus, FaCheckCircle, FaTimes, FaCalendarAlt, FaExclamationCircle, FaRegClock, FaTrash, FaCheck } from "react-icons/fa";
import { FiLoader, FiAlertCircle } from "react-icons/fi";
import api from "../../api/http";

export default function RemindersDashboard() {
  const [reminders, setReminders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cases, setCases] = useState([]);
  
  // Drawer States
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    dueDate: "",
    priority: "medium",
    caseId: ""
  });

  useEffect(() => {
    fetchReminders();
    fetchCases();
  }, []);

  const fetchReminders = async () => {
    try {
      setLoading(true);
      const { data } = await api.get("/reminders");
      setReminders(data);
    } catch (err) {
      console.error("Error fetching reminders:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchCases = async () => {
    try {
      const { data } = await api.get("/cases");
      setCases(data);
    } catch (err) {
      console.error("Error fetching cases:", err);
    }
  };

  const openDrawer = () => {
    setFormData({
      title: "",
      description: "",
      dueDate: "",
      priority: "medium",
      caseId: ""
    });
    setIsDrawerOpen(true);
  };

  const closeDrawer = () => {
    setIsDrawerOpen(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post("/reminders", {
        ...formData,
        caseId: formData.caseId || undefined
      });
      closeDrawer();
      fetchReminders();
    } catch (err) {
      console.error("Error creating reminder:", err);
      alert(err.response?.data?.message || "Failed to create reminder");
    }
  };

  const handleComplete = async (id) => {
    try {
      await api.patch(`/reminders/${id}/complete`);
      fetchReminders();
    } catch (err) {
      console.error("Error completing reminder:", err);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you critically sure you want to permanently delete this reminder?")) return;
    try {
      await api.delete(`/reminders/${id}`);
      fetchReminders();
    } catch (err) {
      console.error("Error deleting reminder:", err);
    }
  };

  const getPriorityStyle = (priority) => {
    switch (priority) {
      case "urgent": return "bg-rose-500 text-white shadow-[0_0_10px_rgba(244,63,94,0.5)]";
      case "high": return "bg-orange-500 text-white";
      case "medium": return "bg-amber-500/20 text-amber-500";
      default: return "bg-blue-500/20 text-blue-400";
    }
  };

  const isOverdue = (dueDate) => {
    return new Date(dueDate) < new Date() && new Date(dueDate).toDateString() !== new Date().toDateString();
  };

  const isDueToday = (dueDate) => {
    return new Date(dueDate).toDateString() === new Date().toDateString();
  };

  const upcomingReminders = reminders.filter(r => !r.isCompleted && (isDueToday(r.dueDate) || isOverdue(r.dueDate)));
  const completedReminders = reminders.filter(r => r.isCompleted);
  const otherReminders = reminders.filter(r => !r.isCompleted && !isDueToday(r.dueDate) && !isOverdue(r.dueDate));

  const stats = {
    overdue: reminders.filter(r => !r.isCompleted && isOverdue(r.dueDate)).length,
    dueToday: reminders.filter(r => !r.isCompleted && isDueToday(r.dueDate)).length,
    active: reminders.filter(r => !r.isCompleted).length
  };

  return (
    <DashboardLayout>
      <div className="relative w-full h-full flex flex-col px-2 font-sans overflow-hidden">
        
        {/* Header Section */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 shrink-0 gap-4">
          <div>
            <h1 className="text-3xl font-bold text-white mb-1 tracking-tight">Timeline Agenda</h1>
            <p className="text-slate-400 text-sm">Manage critical case deadlines, filings, and urgent tasks.</p>
          </div>
          <button
            onClick={() => openDrawer()}
            className="flex items-center gap-2 px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold shadow-[0_0_15px_rgba(79,70,229,0.3)] transition-all"
          >
            <FaPlus /> New Deadline
          </button>
        </div>

        {/* Top Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 shrink-0 mb-8">
           <div className="bg-rose-500/10 rounded-2xl p-6 ring-1 ring-rose-500/20 border border-black backdrop-blur-sm relative overflow-hidden flex items-center justify-between">
              <div className="absolute top-0 right-0 p-4 opacity-10"><FiAlertCircle className="text-8xl text-rose-500" /></div>
              <div>
                <p className="text-rose-400 text-sm font-bold uppercase tracking-wider mb-1">Overdue Items</p>
                <h3 className="text-4xl font-bold text-white">{stats.overdue}</h3>
              </div>
           </div>
           <div className="bg-amber-500/10 rounded-2xl p-6 ring-1 ring-amber-500/20 border border-black backdrop-blur-sm relative overflow-hidden flex items-center justify-between">
              <div className="absolute top-0 right-0 p-4 opacity-10"><FaRegClock className="text-8xl text-amber-500" /></div>
              <div>
                <p className="text-amber-400 text-sm font-bold uppercase tracking-wider mb-1">Due Today</p>
                <h3 className="text-4xl font-bold text-white">{stats.dueToday}</h3>
              </div>
           </div>
           <div className="bg-indigo-500/10 rounded-2xl p-6 ring-1 ring-indigo-500/20 border border-black backdrop-blur-sm relative overflow-hidden flex items-center justify-between">
              <div className="absolute top-0 right-0 p-4 opacity-10"><FaCalendarAlt className="text-8xl text-indigo-500" /></div>
              <div>
                <p className="text-indigo-400 text-sm font-bold uppercase tracking-wider mb-1">Total Active</p>
                <h3 className="text-4xl font-bold text-white">{stats.active}</h3>
              </div>
           </div>
        </div>

        {/* Main List Area */}
        <div className="flex-1 overflow-y-auto min-h-0 pr-2 custom-scrollbar">
          
          {loading ? (
            <div className="flex flex-col items-center justify-center p-20">
              <FiLoader className="h-10 w-10 text-indigo-500 animate-spin mb-4" />
              <p className="text-slate-400 font-medium">Loading agenda...</p>
            </div>
          ) : reminders.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-[50dvh] text-slate-400">
              <FaCheckCircle className="text-6xl text-slate-700 mx-auto mb-4" />
              <p className="text-lg font-bold text-white mb-1">You're all caught up!</p>
              <p className="text-sm">Enjoy your zero-inbox or create a new reminder.</p>
            </div>
          ) : (
            <div className="space-y-10 pb-20">
              
              {/* Critical Urgency List */}
              {upcomingReminders.length > 0 && (
                <div>
                   <h2 className="text-sm font-bold text-rose-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                     <FaExclamationCircle /> Immediate Attention Required
                   </h2>
                   <div className="flex flex-col gap-3">
                     {upcomingReminders.map(r => (
                        <div key={r._id} className="group bg-neutral-900/60 rounded-xl p-4 flex items-center gap-6 ring-1 ring-rose-500/30 hover:ring-rose-500/60 transition-all border-l-4 border-l-rose-500 relative shadow-[0_4px_20px_rgba(244,63,94,0.1)]">
                           <button onClick={() => handleComplete(r._id)} className="w-6 h-6 rounded-full border-2 border-slate-500 flex items-center justify-center hover:bg-emerald-500 hover:border-emerald-500 text-transparent hover:text-white transition-all shrink-0">
                              <FaCheck className="text-xs focus:outline-none" />
                           </button>
                           
                           <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-3 mb-1">
                                <h4 className="text-white font-bold text-lg truncate">{r.title}</h4>
                                <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${getPriorityStyle(r.priority)}`}>{r.priority}</span>
                                {isOverdue(r.dueDate) && <span className="bg-rose-500/20 text-rose-400 px-2.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider">Overdue</span>}
                              </div>
                              <p className="text-slate-400 text-sm truncate">{r.description || "No description provided."}</p>
                           </div>

                           <div className="flex flex-col items-end text-sm whitespace-nowrap shrink-0">
                              <div className={`font-bold ${isOverdue(r.dueDate) ? 'text-rose-400' : 'text-amber-400'}`}>
                                 {new Date(r.dueDate).toLocaleDateString()}
                              </div>
                              {r.caseId && <div className="text-indigo-400 text-xs font-medium">Linked: {r.caseId.title || "Ref Case"}</div>}
                           </div>

                           {/* Hidden actions */}
                           <div className="absolute right-[-10px] opacity-0 group-hover:opacity-100 group-hover:right-4 transition-all bg-neutral-900 p-2 rounded-lg ring-1 ring-white/10 shadow-xl flex gap-1">
                              <button onClick={() => handleDelete(r._id)} className="p-2 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded transition-colors"><FaTrash /></button>
                           </div>
                        </div>
                     ))}
                   </div>
                </div>
              )}

              {/* Standard List */}
              {otherReminders.length > 0 && (
                <div>
                   <h2 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-4">Upcoming Schedule</h2>
                   <div className="flex flex-col gap-3">
                     {otherReminders.map(r => (
                        <div key={r._id} className="group bg-neutral-900/40 rounded-xl p-4 flex items-center gap-6 ring-1 ring-white/5 hover:ring-indigo-500/30 transition-all border-l-4 border-l-transparent hover:border-l-indigo-500 relative">
                           <button onClick={() => handleComplete(r._id)} className="w-6 h-6 rounded-full border-2 border-slate-500 flex items-center justify-center hover:bg-emerald-500 hover:border-emerald-500 text-transparent hover:text-white transition-all shrink-0">
                              <FaCheck className="text-xs" />
                           </button>
                           
                           <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-3 mb-1">
                                <h4 className="text-white font-bold text-base truncate">{r.title}</h4>
                                <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${getPriorityStyle(r.priority)}`}>{r.priority}</span>
                              </div>
                              <p className="text-slate-500 text-sm truncate">{r.description || "No description provided."}</p>
                           </div>

                           <div className="flex flex-col items-end text-sm whitespace-nowrap shrink-0">
                              <div className="text-slate-300 font-medium">
                                 {new Date(r.dueDate).toLocaleDateString()}
                              </div>
                              {r.caseId && <div className="text-indigo-400/70 text-xs">Linked: {r.caseId.title || "Ref Case"}</div>}
                           </div>

                           <div className="absolute right-[-10px] opacity-0 group-hover:opacity-100 group-hover:right-4 transition-all bg-neutral-900 p-2 rounded-lg ring-1 ring-white/10 shadow-xl flex gap-1">
                              <button onClick={() => handleDelete(r._id)} className="p-2 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded transition-colors"><FaTrash /></button>
                           </div>
                        </div>
                     ))}
                   </div>
                </div>
              )}

              {/* Completed List */}
              {completedReminders.length > 0 && (
                <div className="opacity-60">
                   <h2 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-4">Completed Items</h2>
                   <div className="flex flex-col gap-2">
                     {completedReminders.map(r => (
                        <div key={r._id} className="bg-black/20 rounded-xl p-3 flex items-center gap-6 ring-1 ring-white/5 relative group">
                           <div className="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-500 flex items-center justify-center shrink-0">
                              <FaCheck className="text-xs" />
                           </div>
                           
                           <div className="flex-1 min-w-0">
                              <h4 className="text-slate-400 font-medium text-sm line-through truncate">{r.title}</h4>
                           </div>
                           
                           <span className="text-xs text-slate-500 font-medium">
                              Done: {new Date(r.completedAt).toLocaleDateString()}
                           </span>

                           <div className="absolute right-[-10px] opacity-0 group-hover:opacity-100 group-hover:right-2 transition-all flex gap-1 bg-neutral-900 p-1 rounded">
                              <button onClick={() => handleDelete(r._id)} className="p-2 text-slate-500 hover:text-rose-400 transition-colors"><FaTrash /></button>
                           </div>
                        </div>
                     ))}
                   </div>
                </div>
              )}

            </div>
          )}
        </div>

        {/* Slide-out Drawer Overlay */}
        <div className={`fixed inset-0 bg-black/60 backdrop-blur-sm z-40 transition-opacity duration-300 ${isDrawerOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'}`} onClick={closeDrawer}></div>
        
        {/* Slide-out Drawer Container */}
        <div className={`fixed top-0 right-0 h-full w-full sm:w-[450px] bg-neutral-900 border-l border-white/10 z-50 transform transition-transform duration-300 ease-in-out shadow-2xl flex flex-col ${isDrawerOpen ? 'translate-x-0' : 'translate-x-full'}`}>
          
          <div className="flex justify-between items-center p-6 border-b border-white/5 bg-black/20 shrink-0">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <FaCalendarAlt className="text-indigo-400"/> New Deadline
            </h2>
            <button onClick={closeDrawer} className="p-2 bg-white/5 hover:bg-white/10 text-slate-300 rounded-full transition-colors">
              <FaTimes />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-6 custom-scrollbar">
            <form id="reminderForm" onSubmit={handleSubmit} className="space-y-6">
              
              <div>
                 <label className="block text-sm font-semibold text-slate-300 mb-1.5">Action Item <span className="text-rose-500">*</span></label>
                 <input type="text" required value={formData.title} onChange={(e) => setFormData({ ...formData, title: e.target.value })} className="w-full px-4 py-3 rounded-xl border border-white/10 bg-black/20 text-slate-100 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50 placeholder:text-slate-600" placeholder="e.g. File Motion for Discovery" />
              </div>

              <div>
                 <label className="block text-sm font-semibold text-slate-300 mb-1.5">Description</label>
                 <textarea value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} rows="3" className="w-full px-4 py-3 rounded-xl border border-white/10 bg-black/20 text-slate-100 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50 resize-none placeholder:text-slate-600" placeholder="Any special instructions or notes..."/>
              </div>

              <div>
                 <label className="block text-sm font-semibold text-slate-300 mb-1.5">Target Date <span className="text-rose-500">*</span></label>
                 <input type="datetime-local" required value={formData.dueDate} onChange={(e) => setFormData({ ...formData, dueDate: e.target.value })} className="w-full px-4 py-3 rounded-xl border border-white/10 bg-black/20 text-slate-100 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50" style={{colorScheme: 'dark'}}/>
              </div>

              <div>
                 <label className="block text-sm font-semibold text-slate-300 mb-1.5">Urgency Level</label>
                 <div className="grid grid-cols-2 gap-3">
                   {['low', 'medium', 'high', 'urgent'].map(level => (
                      <button 
                        key={level} 
                        type="button" 
                        onClick={() => setFormData({ ...formData, priority: level })} 
                        className={`py-2 px-4 rounded-lg font-bold text-sm capitalize transition-all border ${
                          formData.priority === level 
                            ? 'bg-indigo-600 border-indigo-500 text-white shadow-lg' 
                            : 'bg-black/20 border-white/10 text-slate-400 hover:text-white hover:bg-white/5'
                        }`}
                      >
                        {level}
                      </button>
                   ))}
                 </div>
              </div>

              <div>
                 <label className="block text-sm font-semibold text-slate-300 mb-1.5">Link to Legal Matter</label>
                 <select value={formData.caseId} onChange={(e) => setFormData({ ...formData, caseId: e.target.value })} className="w-full px-4 py-3 rounded-xl border border-white/10 bg-black/20 text-slate-100 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50">
                    <option value="" className="bg-neutral-900">None (General Deadline)</option>
                    {cases.map((caseItem) => (
                      <option key={caseItem._id} value={caseItem._id} className="bg-neutral-900">
                        {caseItem.title}
                      </option>
                    ))}
                 </select>
              </div>

            </form>
          </div>

          <div className="p-6 border-t border-white/5 bg-neutral-900 shrink-0 flex gap-4">
             <button type="button" onClick={closeDrawer} className="flex-1 px-4 py-3 rounded-xl border border-white/10 bg-transparent hover:bg-white/5 text-slate-300 font-bold transition-all">
               Cancel
             </button>
             <button type="submit" form="reminderForm" className="flex-1 px-4 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold shadow-lg transition-all">
               Add to Timeline
             </button>
          </div>
          
        </div>

      </div>
    </DashboardLayout>
  );
}

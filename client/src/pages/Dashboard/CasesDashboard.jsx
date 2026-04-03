import DashboardLayout from "../../layout/DashboardLayout";
import { useState, useEffect } from "react";
import { FaPlus, FaEdit, FaTrash, FaCalendar, FaTag, FaSearch } from "react-icons/fa";
import { FiLoader } from "react-icons/fi";
import api from "../../api/http";

export default function CasesDashboard() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
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
      setShowModal(false);
      setEditingCase(null);
      setFormData({
        title: "",
        caseType: "Civil",
        description: "",
        filingDate: "",
        hearingDate: "",
        deadline: "",
        plaintiff: "",
        defendant: "",
        tags: ""
      });
      fetchCases();
    } catch (err) {
      console.error("Error saving case:", err);
      alert(err.response?.data?.message || "Failed to save case");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this case?")) return;
    try {
      await api.delete(`/cases/${id}`);
      fetchCases();
    } catch (err) {
      console.error("Error deleting case:", err);
      alert("Failed to delete case");
    }
  };

  const handleEdit = (caseItem) => {
    setEditingCase(caseItem);
    setFormData({
      title: caseItem.title || "",
      caseType: caseItem.caseType || "Civil",
      description: caseItem.description || "",
      filingDate: caseItem.filingDate ? new Date(caseItem.filingDate).toISOString().split("T")[0] : "",
      hearingDate: caseItem.hearingDate ? new Date(caseItem.hearingDate).toISOString().split("T")[0] : "",
      deadline: caseItem.deadline ? new Date(caseItem.deadline).toISOString().split("T")[0] : "",
      plaintiff: caseItem.plaintiff || "",
      defendant: caseItem.defendant || "",
      tags: (caseItem.tags || []).join(", ")
    });
    setShowModal(true);
  };

  const filteredCases = cases.filter(c => {
    const matchesSearch = !searchQuery || 
      (c.title || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
      (c.description || "").toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = filterType === "all" || c.status === filterType;
    return matchesSearch && matchesFilter;
  });

  if (loading) {
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
      <div className="relative w-full h-full flex flex-col">
        <div className="flex justify-between items-center mb-6 shrink-0">
          <div>
            <h1 className="text-3xl font-display font-bold text-white mb-2">My Cases</h1>
            <p className="text-slate-400 text-sm">Manage your legal cases and track their progress</p>
          </div>
          <button
            onClick={() => {
              setEditingCase(null);
              setFormData({
                title: "",
                caseType: "Civil",
                description: "",
                filingDate: "",
                hearingDate: "",
                deadline: "",
                plaintiff: "",
                defendant: "",
                tags: ""
              });
              setShowModal(true);
            }}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 text-white font-semibold shadow-lg transition-all hover:shadow-xl"
          >
            <FaPlus /> New Case
          </button>
        </div>

        {/* Search and Filter */}
        <div className="mb-6 flex flex-col sm:flex-row gap-4 shrink-0">
          <div className="flex-1 relative">
            <FaSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search cases..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/60"
            />
          </div>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-4 py-2 rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500/60"
          >
            <option value="all">All Status</option>
            <option value="Active">Active</option>
            <option value="Pending">Pending</option>
            <option value="Closed">Closed</option>
            <option value="Archived">Archived</option>
          </select>
        </div>

        {/* Cases List - Scrollable */}
        <div className="flex-1 overflow-y-auto min-h-0">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredCases.length === 0 ? (
            <div className="col-span-full text-center py-12 text-slate-400 rounded-2xl ring-1 ring-white/10 bg-neutral-900/50 backdrop-blur-xl">
              <FaPlus className="text-4xl mx-auto mb-4 opacity-30" />
              <p className="font-medium">No cases found</p>
              <p className="text-sm mt-2">Create your first case to get started.</p>
            </div>
          ) : (
            filteredCases.map((caseItem) => (
              <div
                key={caseItem._id}
                className="rounded-2xl ring-1 ring-white/10 bg-neutral-900/50 backdrop-blur-xl p-5 hover:ring-white/20 hover:shadow-lg transition-all animate-fade-in"
              >
                <div className="flex justify-between items-start mb-3">
                  <h3 className="text-lg font-semibold text-white">{caseItem.title}</h3>
                  <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                    caseItem.status === "Active" ? "bg-green-500/20 text-green-400" :
                    caseItem.status === "Pending" ? "bg-yellow-500/20 text-yellow-400" :
                    caseItem.status === "Closed" ? "bg-slate-500/20 text-slate-400" :
                    "bg-gray-500/20 text-gray-400"
                  }`}>
                    {caseItem.status}
                  </span>
                </div>
                <div className="space-y-2 text-sm text-slate-300 mb-4">
                  <div className="flex items-center gap-2">
                    <FaTag className="text-slate-500" />
                    <span>{caseItem.caseType}</span>
                  </div>
                  {caseItem.deadline && (
                    <div className="flex items-center gap-2">
                      <FaCalendar className="text-slate-500" />
                      <span>Deadline: {new Date(caseItem.deadline).toLocaleDateString()}</span>
                    </div>
                  )}
                  {caseItem.description && (
                    <p className="text-slate-400 line-clamp-2">{caseItem.description}</p>
                  )}
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleEdit(caseItem)}
                    className="flex-1 px-3 py-2 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-400 text-sm font-medium"
                  >
                    <FaEdit className="inline mr-1" /> Edit
                  </button>
                  <button
                    onClick={() => handleDelete(caseItem._id)}
                    className="px-3 py-2 rounded-lg bg-rose-600/20 hover:bg-rose-600/30 text-rose-400 text-sm font-medium"
                  >
                    <FaTrash />
                  </button>
                </div>
              </div>
            ))
          )}
          </div>
        </div>

        {/* Modal */}
        {showModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-neutral-900 rounded-2xl ring-1 ring-white/10 p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <h2 className="text-xl font-bold text-white mb-4">
                {editingCase ? "Edit Case" : "New Case"}
              </h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">Title *</label>
                  <input
                    type="text"
                    required
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500/60"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1">Case Type</label>
                    <select
                      value={formData.caseType}
                      onChange={(e) => setFormData({ ...formData, caseType: e.target.value })}
                      className="w-full px-3 py-2 rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500/60"
                    >
                      <option value="Civil">Civil</option>
                      <option value="Criminal">Criminal</option>
                      <option value="Family">Family</option>
                      <option value="Corporate">Corporate</option>
                      <option value="Property">Property</option>
                      <option value="Contract">Contract</option>
                      <option value="Employment">Employment</option>
                      <option value="Intellectual Property">Intellectual Property</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1">Filing Date</label>
                    <input
                      type="date"
                      value={formData.filingDate}
                      onChange={(e) => setFormData({ ...formData, filingDate: e.target.value })}
                      className="w-full px-3 py-2 rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500/60"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">Description</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    rows="3"
                    className="w-full px-3 py-2 rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500/60"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1">Plaintiff</label>
                    <input
                      type="text"
                      value={formData.plaintiff}
                      onChange={(e) => setFormData({ ...formData, plaintiff: e.target.value })}
                      className="w-full px-3 py-2 rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500/60"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1">Defendant</label>
                    <input
                      type="text"
                      value={formData.defendant}
                      onChange={(e) => setFormData({ ...formData, defendant: e.target.value })}
                      className="w-full px-3 py-2 rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500/60"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1">Hearing Date</label>
                    <input
                      type="date"
                      value={formData.hearingDate}
                      onChange={(e) => setFormData({ ...formData, hearingDate: e.target.value })}
                      className="w-full px-3 py-2 rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500/60"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1">Deadline</label>
                    <input
                      type="date"
                      value={formData.deadline}
                      onChange={(e) => setFormData({ ...formData, deadline: e.target.value })}
                      className="w-full px-3 py-2 rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500/60"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">Tags (comma-separated)</label>
                  <input
                    type="text"
                    value={formData.tags}
                    onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                    placeholder="e.g., urgent, property, contract"
                    className="w-full px-3 py-2 rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500/60"
                  />
                </div>
                <div className="flex gap-3 pt-4">
                  <button
                    type="submit"
                    className="flex-1 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold"
                  >
                    {editingCase ? "Update" : "Create"} Case
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowModal(false);
                      setEditingCase(null);
                    }}
                    className="px-4 py-2 rounded-xl border border-white/10 bg-neutral-800 hover:bg-neutral-700 text-slate-100 font-semibold"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}


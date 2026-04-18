import { useState } from "react";
import { FaBrain, FaCheckCircle, FaTimesCircle, FaBalanceScale, FaGavel, FaLightbulb, FaExclamationTriangle } from "react-icons/fa";
import { FiLoader, FiThumbsUp, FiThumbsDown } from "react-icons/fi";
import api from "../../../api/http";

export default function OutcomePrediction() {
  const [formData, setFormData] = useState({
    caseDescription: "",
    legalContext: "",
    caseType: "Civil"
  });
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeSection, setActiveSection] = useState("overview");
  const [error, setError] = useState(null);
  const [feedbackGiven, setFeedbackGiven] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    // Validate input - [Missing details] case
    if (!formData.caseDescription.trim()) {
      setError("Please complete all required fields");
      return;
    }

    setLoading(true);
    try {
      const { data } = await api.post("/ai/predict", {
        caseDescription: formData.caseDescription,
        legalContext: formData.legalContext,
        caseType: formData.caseType
      });

      setPrediction(data);
      setActiveSection("overview");
      setFeedbackGiven(false);

      // Save prediction result to user history (handled by backend)
    } catch (err) {
      console.error("Prediction error:", err);
      // [Model error] case
      if (err.response?.status === 500 || err.response?.status === 503) {
        setError("Prediction unavailable. Please try again later.");
      } else if (!navigator.onLine) {
        setError("Unable to connect to server. Please check your internet connection.");
      } else {
        setError(err.response?.data?.detail || "Prediction unavailable. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (isPositive) => {
    setFeedbackGiven(true);
    try {
      await api.post("/feedback", {
        rating: isPositive ? 5 : 2,
        feedbackType: "prediction",
        message: `Prediction feedback: ${isPositive ? 'Accurate/Helpful' : 'Inaccurate/Not helpful'} - Case type: ${formData.caseType}`,
      });
    } catch (err) {
      console.error("Error submitting feedback:", err);
    }
  };

  const handleReset = () => {
    setFormData({
      caseDescription: "",
      legalContext: "",
      caseType: "Civil"
    });
    setPrediction(null);
    setActiveSection("overview");
    setError(null);
    setFeedbackGiven(false);
  };

  const getOutcomeColor = (prediction) => {
    const pred = (prediction || "").toLowerCase();
    if (pred.includes("favorable") || pred.includes("success") || pred.includes("win")) {
      return { bg: "bg-emerald-500/20", text: "text-emerald-400", border: "border-emerald-500/30" };
    } else if (pred.includes("unfavorable") || pred.includes("loss") || pred.includes("dismiss")) {
      return { bg: "bg-rose-500/20", text: "text-rose-400", border: "border-rose-500/30" };
    }
    return { bg: "bg-amber-500/20", text: "text-amber-400", border: "border-amber-500/30" };
  };

  const sections = prediction ? [
    { id: "overview", label: "Overview", icon: FaBalanceScale },
    { id: "analysis", label: "Detailed Analysis", icon: FaGavel },
    { id: "risks", label: "Risks & Recommendations", icon: FaExclamationTriangle },
    { id: "legal", label: "Legal Basis", icon: FaLightbulb },
    { id: "cases", label: "Similar Cases", icon: FaBrain },
  ] : [];

  return (
    <div className="w-full h-full flex flex-col overflow-y-auto pb-10">
      {!prediction && !loading ? (
        <div className="max-w-4xl mx-auto w-full pt-8 px-4">
          <div className="mb-10 text-center">
            <h2 className="text-4xl font-display font-bold text-white mb-4 tracking-tight drop-shadow-lg">
              Case Outcome <span className="text-indigo-400">Prediction</span>
            </h2>
            <p className="text-slate-400 text-lg">
              Provide your case details and receive a professional, AI-powered probable outcome analysis based strictly on Pakistani law and precedent.
            </p>
          </div>

          <div className="rounded-2xl ring-1 ring-white/10 bg-neutral-900/50 backdrop-blur-xl p-8 shadow-2xl relative overflow-hidden group">
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 via-transparent to-purple-500/5 opacity-50"></div>
            
            <form onSubmit={handleSubmit} className="relative space-y-6 flex flex-col">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="col-span-1 md:col-span-2">
                  <label className="block text-sm font-semibold text-slate-300 mb-2">
                    Select Case Category
                  </label>
                  <select
                    value={formData.caseType}
                    onChange={(e) => setFormData({ ...formData, caseType: e.target.value })}
                    className="w-full px-5 py-3.5 rounded-xl border border-white/10 bg-neutral-900/80 text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500/60 shadow-inner"
                  >
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

                <div className="col-span-1 md:col-span-2">
                  <label className="block text-sm font-semibold text-slate-300 mb-2 flex justify-between items-center">
                    <span>Case Description <span className="text-rose-400">*</span></span>
                    <span className="text-xs font-normal text-indigo-400 font-mono">Facts, Parties, Current Status</span>
                  </label>
                  <textarea
                    value={formData.caseDescription}
                    onChange={(e) => setFormData({ ...formData, caseDescription: e.target.value })}
                    placeholder="E.g., I purchased a plot of land 3 years ago and have been living there. Another person has claimed ownership citing old documents..."
                    rows="8"
                    required
                    className="w-full px-5 py-4 rounded-xl border border-white/10 bg-neutral-900/80 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/60 resize-none shadow-inner"
                  />
                </div>

                <div className="col-span-1 md:col-span-2">
                  <label className="block text-sm font-semibold text-slate-300 mb-2">
                    Legal Context (Optional)
                  </label>
                  <textarea
                    value={formData.legalContext}
                    onChange={(e) => setFormData({ ...formData, legalContext: e.target.value })}
                    placeholder="Provide any specific laws, statutes, or existing arguments you are already considering..."
                    rows="4"
                    className="w-full px-5 py-3.5 rounded-xl border border-white/10 bg-neutral-900/80 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/60 resize-none shadow-inner"
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
                  disabled={loading || !formData.caseDescription.trim()}
                  className="w-full md:w-auto px-10 py-4 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold text-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3 shadow-lg shadow-indigo-500/25 transition-all active:scale-[0.98]"
                >
                  <FaBrain className="text-xl" /> Analyze & Predict Outcome
                </button>
              </div>
            </form>
          </div>
        </div>
      ) : (
        <div className="max-w-4xl mx-auto w-full pt-8 px-4 flex flex-col">
          {/* Header Action Bar */}
          <div className="flex items-center justify-between xl:-ml-12 mb-8">
            <button
              onClick={handleReset}
              className="px-5 py-2.5 rounded-xl border border-white/10 bg-neutral-900/50 hover:bg-neutral-800 text-slate-300 font-medium transition-colors flex items-center gap-2 group backdrop-blur-md shadow-sm"
            >
              <span className="group-hover:-translate-x-1 transition-transform">←</span> Back to Editor
            </button>

            {prediction && !loading && (
              <div className="flex items-center gap-3 bg-neutral-900/50 px-4 py-2 rounded-xl border border-white/10 backdrop-blur-md">
                <span className="text-sm font-medium text-slate-300">Rate this prediction:</span>
                {feedbackGiven ? (
                  <span className="text-sm text-emerald-400 font-medium flex items-center gap-1"><FiThumbsUp /> Logged</span>
                ) : (
                  <div className="flex gap-1.5">
                    <button onClick={() => handleFeedback(true)} className="p-1.5 rounded-md bg-neutral-800 hover:bg-emerald-500/20 hover:text-emerald-400 text-slate-400 transition-colors" title="Accurate"><FiThumbsUp /></button>
                    <button onClick={() => handleFeedback(false)} className="p-1.5 rounded-md bg-neutral-800 hover:bg-rose-500/20 hover:text-rose-400 text-slate-400 transition-colors" title="Inaccurate"><FiThumbsDown /></button>
                  </div>
                )}
              </div>
            )}
          </div>

          {loading ? (
            <div className="rounded-2xl ring-1 ring-white/10 bg-neutral-900/50 backdrop-blur-xl p-16 shadow-2xl flex flex-col items-center justify-center min-h-[400px]">
              <FiLoader className="text-6xl text-indigo-500 animate-spin mb-6" />
              <h3 className="text-2xl font-bold text-white mb-2">Analyzing Case Framework</h3>
              <p className="text-slate-400 text-lg">Extracting legal principles, verifying precedence, and calculating probable outcomes...</p>
            </div>
          ) : (
            <div className="rounded-2xl ring-1 ring-white/10 bg-neutral-900/50 backdrop-blur-xl shadow-2xl overflow-hidden flex flex-col">
              <div className="bg-neutral-800/80 px-8 py-6 border-b border-white/10">
                <h3 className="text-2xl font-bold text-white flex items-center gap-3">
                  <FaGavel className="text-indigo-400 text-3xl" /> 
                  Prediction Results
                </h3>
              </div>
              
              <div className="p-8">
                  {/* Since the backend returns a perfectly formatted block in full_analysis/explanation, just pipe it nicely */}
                  <div className="bg-neutral-900/50 rounded-xl p-8 border border-white/5 shadow-inner">
                    <div className="text-slate-300 text-base leading-relaxed whitespace-pre-wrap font-serif">
                       {prediction.full_analysis || prediction.explanation}
                    </div>
                  </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

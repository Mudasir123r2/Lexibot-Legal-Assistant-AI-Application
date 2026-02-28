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
    <div className="relative w-full h-full flex flex-col">
      <div className="mb-6 shrink-0">
        <h2 className="text-2xl font-display font-bold text-white mb-2">Case Outcome Prediction</h2>
        <p className="text-slate-400 text-sm">AI-powered predictions using RAG + LLM analysis of similar cases</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1 min-h-0">
        {/* Input Form */}
        <div className="rounded-2xl ring-1 ring-white/10 bg-neutral-900/50 backdrop-blur-xl p-6 shadow-xl h-fit lg:h-full flex flex-col overflow-y-auto">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <FaBrain className="text-indigo-400" />
            Enter Case Information
          </h3>
          
          <form onSubmit={handleSubmit} className="space-y-4 flex-1 flex flex-col">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Case Type
              </label>
              <select
                value={formData.caseType}
                onChange={(e) => setFormData({ ...formData, caseType: e.target.value })}
                className="w-full px-4 py-2.5 rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500/60"
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

            <div className="flex-1">
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Case Description *
              </label>
              <textarea
                value={formData.caseDescription}
                onChange={(e) => setFormData({ ...formData, caseDescription: e.target.value })}
                placeholder="Describe your case in detail: facts, circumstances, parties involved, key issues, current status, and what you're seeking..."
                rows="8"
                required
                className="w-full px-4 py-2.5 rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/60 resize-none"
              />
              <p className="text-xs text-slate-500 mt-1">💡 Be specific about dates, events, and legal issues for better predictions</p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-sm">
                {error}
              </div>
            )}

            <div className="flex-1">
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Legal Context (Optional)
              </label>
              <textarea
                value={formData.legalContext}
                onChange={(e) => setFormData({ ...formData, legalContext: e.target.value })}
                placeholder="Provide relevant legal context: applicable laws, precedents, statutes, regulations, or specific legal arguments..."
                rows="5"
                className="w-full px-4 py-2.5 rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/60 resize-none"
              />
            </div>

            <div className="flex gap-3 pt-2">
              <button
                type="submit"
                disabled={loading || !formData.caseDescription.trim()}
                className="flex-1 px-4 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg"
              >
                {loading ? (
                  <>
                    <FiLoader className="animate-spin" /> Analyzing...
                  </>
                ) : (
                  <>
                    <FaBrain /> Predict Outcome
                  </>
                )}
              </button>
              <button
                type="button"
                onClick={handleReset}
                className="px-4 py-3 rounded-xl border border-white/10 bg-neutral-800 hover:bg-neutral-700 text-slate-100 font-semibold"
              >
                Reset
              </button>
            </div>
          </form>
        </div>

        {/* Prediction Results */}
        <div className="rounded-2xl ring-1 ring-white/10 bg-neutral-900/50 backdrop-blur-xl shadow-xl h-fit lg:h-full flex flex-col overflow-hidden">
          <div className="p-6 border-b border-white/10 shrink-0 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white">Prediction Results</h3>
            {/* Feedback Option */}
            {prediction && (
              <div className="flex items-center gap-2">
                {feedbackGiven ? (
                  <span className="text-xs text-slate-500">Thanks for your feedback!</span>
                ) : (
                  <>
                    <span className="text-xs text-slate-400">Was this helpful?</span>
                    <button
                      onClick={() => handleFeedback(true)}
                      className="p-1.5 rounded-lg hover:bg-white/10 text-slate-400 hover:text-green-400 transition-colors"
                      title="Helpful"
                    >
                      <FiThumbsUp className="text-sm" />
                    </button>
                    <button
                      onClick={() => handleFeedback(false)}
                      className="p-1.5 rounded-lg hover:bg-white/10 text-slate-400 hover:text-rose-400 transition-colors"
                      title="Not helpful"
                    >
                      <FiThumbsDown className="text-sm" />
                    </button>
                  </>
                )}
              </div>
            )}
          </div>

          {!prediction && !loading && (
            <div className="flex-1 flex items-center justify-center text-slate-400 p-12">
              <div className="text-center">
                <FaBrain className="text-6xl mx-auto mb-4 opacity-20" />
                <p className="font-medium mb-2">No Prediction Yet</p>
                <p className="text-sm">Enter case details and click "Predict Outcome"</p>
                <p className="text-xs mt-2 text-slate-500">Uses AI + similar case analysis</p>
              </div>
            </div>
          )}

          {loading && (
            <div className="flex-1 flex items-center justify-center p-12">
              <div className="text-center">
                <FiLoader className="text-5xl mx-auto mb-4 text-indigo-500 animate-spin" />
                <p className="text-slate-300 font-medium mb-2">Analyzing Your Case...</p>
                <p className="text-sm text-slate-400">Searching similar cases and generating prediction</p>
              </div>
            </div>
          )}

          {prediction && (
            <>
              {/* Section Tabs */}
              <div className="px-6 py-3 border-b border-white/10 shrink-0 overflow-x-auto scrollbar-hide">
                <div className="flex gap-2">
                  {sections.map((section) => {
                    const Icon = section.icon;
                    return (
                      <button
                        key={section.id}
                        onClick={() => setActiveSection(section.id)}
                        className={`px-3 py-2 rounded-lg text-xs font-medium transition-all whitespace-nowrap flex items-center gap-1.5 ${
                          activeSection === section.id
                            ? "bg-indigo-600/30 text-white"
                            : "text-slate-400 hover:text-slate-200 hover:bg-neutral-800/50"
                        }`}
                      >
                        <Icon className="text-xs" />
                        {section.label}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Section Content */}
              <div className="flex-1 overflow-y-auto p-6">
                {activeSection === "overview" && (
                  <div className="space-y-4">
                    {/* Predicted Outcome */}
                    <div className={`p-5 rounded-xl ${getOutcomeColor(prediction.prediction).bg} border ${getOutcomeColor(prediction.prediction).border}`}>
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="font-semibold text-white text-lg">Predicted Outcome</h4>
                        <FaBalanceScale className={`text-2xl ${getOutcomeColor(prediction.prediction).text}`} />
                      </div>
                      <p className={`text-xl font-bold ${getOutcomeColor(prediction.prediction).text} mb-4`}>
                        {prediction.prediction}
                      </p>
                      
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-slate-300">Confidence Level</span>
                          <span className="text-sm font-semibold text-white">{prediction.confidence}%</span>
                        </div>
                        <div className="w-full bg-neutral-800/50 rounded-full h-3 overflow-hidden">
                          <div
                            className={`h-3 rounded-full transition-all ${
                              prediction.confidence >= 70 ? "bg-emerald-500" :
                              prediction.confidence >= 50 ? "bg-amber-500" : "bg-rose-500"
                            }`}
                            style={{ width: `${prediction.confidence}%` }}
                          />
                        </div>
                        <p className="text-xs text-slate-400 mt-2">
                          {prediction.confidence >= 70 ? "High confidence based on strong precedents" :
                           prediction.confidence >= 50 ? "Moderate confidence - outcome may vary" :
                           "Lower confidence - limited similar cases found"}
                        </p>
                      </div>
                    </div>

                    {/* Quick Summary */}
                    {prediction.explanation && (
                      <div className="p-4 rounded-xl bg-neutral-800/50">
                        <h4 className="font-semibold text-white mb-3 flex items-center gap-2">
                          <FaGavel className="text-indigo-400" />
                          Analysis Summary
                        </h4>
                        <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap">{prediction.explanation}</p>
                      </div>
                    )}

                    {/* Confidence Analysis */}
                    {prediction.confidence_analysis && (
                      <div className="p-4 rounded-xl bg-neutral-800/50">
                        <h4 className="font-semibold text-white mb-3">Confidence Analysis</h4>
                        <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap">{prediction.confidence_analysis}</p>
                      </div>
                    )}
                  </div>
                )}

                {activeSection === "analysis" && (
                  <div className="space-y-4">
                    {prediction.full_analysis ? (
                      <div className="p-4 rounded-xl bg-neutral-800/50">
                        <h4 className="font-semibold text-white mb-3 flex items-center gap-2">
                          <FaGavel className="text-indigo-400" />
                          Complete Legal Analysis
                        </h4>
                        <div className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap">{prediction.full_analysis}</div>
                      </div>
                    ) : prediction.explanation && (
                      <div className="p-4 rounded-xl bg-neutral-800/50">
                        <h4 className="font-semibold text-white mb-3">Detailed Reasoning</h4>
                        <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap">{prediction.explanation}</p>
                      </div>
                    )}
                  </div>
                )}

                {activeSection === "risks" && (
                  <div className="space-y-4">
                    {/* Risk Factors */}
                    {prediction.risk_factors && prediction.risk_factors.length > 0 && (
                      <div className="p-4 rounded-xl bg-rose-900/20 border border-rose-500/30">
                        <h4 className="font-semibold text-white mb-3 flex items-center gap-2">
                          <FaTimesCircle className="text-rose-400" />
                          Risk Factors
                        </h4>
                        <ul className="space-y-2.5">
                          {prediction.risk_factors.map((risk, i) => (
                            <li key={i} className="text-slate-300 text-sm flex items-start gap-3">
                              <span className="text-rose-400 font-bold text-lg mt-0.5">•</span>
                              <span className="flex-1">{risk}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Recommendations */}
                    {prediction.recommendations && prediction.recommendations.length > 0 && (
                      <div className="p-4 rounded-xl bg-emerald-900/20 border border-emerald-500/30">
                        <h4 className="font-semibold text-white mb-3 flex items-center gap-2">
                          <FaCheckCircle className="text-emerald-400" />
                          Strategic Recommendations
                        </h4>
                        <ul className="space-y-2.5">
                          {prediction.recommendations.map((rec, i) => (
                            <li key={i} className="text-slate-300 text-sm flex items-start gap-3">
                              <span className="text-emerald-400 font-bold text-lg mt-0.5">✓</span>
                              <span className="flex-1">{rec}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {!prediction.risk_factors?.length && !prediction.recommendations?.length && (
                      <div className="text-center text-slate-400 py-12">
                        <FaExclamationTriangle className="text-4xl mx-auto mb-3 opacity-30" />
                        <p>No specific risks or recommendations available</p>
                      </div>
                    )}
                  </div>
                )}

                {activeSection === "legal" && (
                  <div className="space-y-4">
                    {prediction.legal_basis ? (
                      <div className="p-4 rounded-xl bg-neutral-800/50">
                        <h4 className="font-semibold text-white mb-3 flex items-center gap-2">
                          <FaLightbulb className="text-amber-400" />
                          Legal Basis & Precedents
                        </h4>
                        <div className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap">{prediction.legal_basis}</div>
                      </div>
                    ) : (
                      <div className="text-center text-slate-400 py-12">
                        <FaLightbulb className="text-4xl mx-auto mb-3 opacity-30" />
                        <p>Legal basis information not available</p>
                      </div>
                    )}
                  </div>
                )}

                {activeSection === "cases" && (
                  <div className="space-y-3">
                    {prediction.similarCases && prediction.similarCases.length > 0 ? (
                      <>
                        <p className="text-sm text-slate-400 mb-4">
                          Found {prediction.similarCases.length} similar cases used for this prediction
                        </p>
                        {prediction.similarCases.map((similar, i) => (
                          <div key={i} className="p-4 rounded-xl bg-neutral-800/50 hover:bg-neutral-800/70 transition-colors">
                            <div className="flex items-start justify-between mb-2">
                              <h5 className="text-sm font-semibold text-white">{similar.title || `Case ${i + 1}`}</h5>
                              {similar.similarity && (
                                <span className="px-2 py-1 rounded-full text-xs bg-indigo-500/20 text-indigo-400">
                                  {(similar.similarity * 100).toFixed(0)}% match
                                </span>
                              )}
                            </div>
                            <div className="grid grid-cols-2 gap-2 text-xs text-slate-400">
                              <div>Court: {similar.court || "N/A"}</div>
                              <div>Date: {similar.date || "N/A"}</div>
                              {similar.case_type && <div>Type: {similar.case_type}</div>}
                              {similar.citation && <div>Citation: {similar.citation}</div>}
                            </div>
                            {similar.excerpt && (
                              <p className="text-xs text-slate-500 mt-2 line-clamp-2">{similar.excerpt}</p>
                            )}
                          </div>
                        ))}
                      </>
                    ) : (
                      <div className="text-center text-slate-400 py-12">
                        <FaBrain className="text-4xl mx-auto mb-3 opacity-30" />
                        <p>No similar cases found</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

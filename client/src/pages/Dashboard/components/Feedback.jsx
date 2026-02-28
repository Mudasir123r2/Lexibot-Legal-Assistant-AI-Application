import { useState } from "react";
import { FaStar, FaCheckCircle } from "react-icons/fa";
import api from "../../../api/http";

export default function Feedback() {
  const [formData, setFormData] = useState({
    rating: 0,
    feedbackType: "general",
    message: "",
    contactEmail: ""
  });
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (formData.rating === 0) {
      alert("Please provide a rating");
      return;
    }
    if (!formData.message.trim()) {
      alert("Please provide your feedback");
      return;
    }

    setSubmitting(true);
    try {
      // Submit feedback to backend API
      await api.post("/feedback", formData);
      
      setSubmitted(true);
      
      // Reset form after 3 seconds
      setTimeout(() => {
        setSubmitted(false);
        setFormData({
          rating: 0,
          feedbackType: "general",
          message: "",
          contactEmail: ""
        });
      }, 3000);
    } catch (err) {
      console.error("Feedback submission error:", err);
      alert("Failed to submit feedback. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="relative">
        <div className="rounded-2xl ring-1 ring-white/10 bg-neutral-900/50 backdrop-blur-xl p-12 text-center">
          <FaCheckCircle className="text-6xl text-green-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">Thank You!</h2>
          <p className="text-slate-400">Your feedback has been submitted successfully. We appreciate your input!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-full h-full flex flex-col">
      <div className="mb-6 shrink-0">
        <h2 className="text-2xl font-display font-bold text-white mb-2">Feedback</h2>
        <p className="text-slate-400 text-sm">Share your thoughts and help us improve LexiBot</p>
      </div>

      <div className="rounded-2xl ring-1 ring-white/10 bg-neutral-900/50 backdrop-blur-xl p-6 max-w-2xl mx-auto shadow-xl flex-1 overflow-y-auto">
        <p className="text-slate-300 mb-6">
          We value your feedback! Please share your thoughts, suggestions, or report any issues you've encountered.
          Your input helps us improve LexiBot.
        </p>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Rating */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-3">
              Overall Rating *
            </label>
            <div className="flex gap-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  onClick={() => setFormData({ ...formData, rating: star })}
                  className={`transition-transform hover:scale-110 ${
                    formData.rating >= star ? "text-yellow-400" : "text-slate-500"
                  }`}
                >
                  <FaStar className="text-3xl" />
                </button>
              ))}
            </div>
            <p className="text-xs text-slate-500 mt-2">
              {formData.rating === 0 && "Click a star to rate"}
              {formData.rating === 1 && "Poor"}
              {formData.rating === 2 && "Fair"}
              {formData.rating === 3 && "Good"}
              {formData.rating === 4 && "Very Good"}
              {formData.rating === 5 && "Excellent"}
            </p>
          </div>

          {/* Feedback Type */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Feedback Type
            </label>
            <select
              value={formData.feedbackType}
              onChange={(e) => setFormData({ ...formData, feedbackType: e.target.value })}
              className="w-full px-4 py-2.5 rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500/60"
            >
              <option value="general">General Feedback</option>
              <option value="bug">Bug Report</option>
              <option value="feature">Feature Request</option>
              <option value="improvement">Improvement Suggestion</option>
              <option value="chat">Chat/AI Response</option>
              <option value="search">Search Functionality</option>
              <option value="prediction">Outcome Prediction</option>
              <option value="other">Other</option>
            </select>
          </div>

          {/* Message */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Your Feedback *
            </label>
            <textarea
              value={formData.message}
              onChange={(e) => setFormData({ ...formData, message: e.target.value })}
              placeholder="Please describe your feedback, suggestions, or report any issues you've encountered..."
              rows="6"
              required
              className="w-full px-4 py-2.5 rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/60 resize-none"
            />
          </div>

          {/* Contact Email (Optional) */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Contact Email (Optional)
            </label>
            <input
              type="email"
              value={formData.contactEmail}
              onChange={(e) => setFormData({ ...formData, contactEmail: e.target.value })}
              placeholder="your.email@example.com"
              className="w-full px-4 py-2.5 rounded-xl border border-white/10 bg-neutral-900/60 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/60"
            />
            <p className="text-xs text-slate-500 mt-1">
              Optional: We may contact you if we need more information about your feedback.
            </p>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={submitting || formData.rating === 0 || !formData.message.trim()}
            className="w-full px-4 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? "Submitting..." : "Submit Feedback"}
          </button>
        </form>
      </div>
    </div>
  );
}


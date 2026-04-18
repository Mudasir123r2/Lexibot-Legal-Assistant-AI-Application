import { useState, useRef, useEffect } from "react";
import { FiSend, FiLoader, FiTrash2, FiMessageSquare, FiChevronLeft, FiChevronRight, FiMic, FiMicOff, FiThumbsUp, FiThumbsDown, FiVolume2, FiVolumeX } from "react-icons/fi";
import api from "../../../api/http";

export default function ChatTab({ contextData = null, initialMessage = null, hideSidebar = false, selectedDocAvailable = false, isMainDashboard = false, externalShowHistory, setExternalShowHistory }) {
  const getInitialGreeting = () => {
    if (contextData?.title || contextData?.explicitTextContext) {
        return `I am prepared to assist you with the analysis of this document. Please let me know if you require a summary, extraction of key points, or answers to specific questions regarding this case.`;
    }
    return "Hello! I'm LexiBot, your AI legal assistant. I can help you with:\n\n• Summarizing legal judgments\n• Searching for relevant cases\n• Analyzing case outcomes\n• Providing client guidance and checklists\n• Extracting key information from documents\n\nWhat would you like help with today?";
  };

  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: getInitialGreeting()
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [internalShowHistory, setInternalShowHistory] = useState(false);
  const showHistory = externalShowHistory !== undefined ? externalShowHistory : internalShowHistory;
  const setShowHistory = setExternalShowHistory !== undefined ? setExternalShowHistory : setInternalShowHistory;
  const [isListening, setIsListening] = useState(false);
  const [feedbackGiven, setFeedbackGiven] = useState({});
  const [showCommentInput, setShowCommentInput] = useState({});
  const [feedbackComments, setFeedbackComments] = useState({});
  const [speakingIndex, setSpeakingIndex] = useState(null);
  const listRef = useRef(null);
  const recognitionRef = useRef(null);
  const initializedRef = useRef(false);

  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInput((prev) => prev + (prev ? ' ' : '') + transcript);
        setIsListening(false);
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        if (event.error === 'not-allowed') {
          alert('Microphone access was denied. Please check your browser permissions.');
        } else if (event.error === 'no-speech') {
          // just stop listening
        } else {
          alert(`Microphone error: ${event.error}. Note: Voice input typically requires Google Chrome.`);
        }
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }
  }, []);

  const toggleVoiceInput = () => {
    if (!recognitionRef.current) {
      alert('Voice input is not supported in your browser. Please use Google Chrome or Microsoft Edge.');
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      try {
        recognitionRef.current.start();
        setIsListening(true);
      } catch (e) {
        console.error("Mic start error", e);
        setIsListening(false);
      }
    }
  };

  const toggleSpeech = (text, index) => {
    if (!('speechSynthesis' in window)) {
      alert("Text-to-Speech is not supported in your browser.");
      return;
    }

    // If currently speaking this index, stop
    if (speakingIndex === index) {
      window.speechSynthesis.cancel();
      setSpeakingIndex(null);
      return;
    }

    // Stop anything else currently playing
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US";
    utterance.rate = 1.0;

    utterance.onend = () => setSpeakingIndex(null);
    utterance.onerror = () => setSpeakingIndex(null);

    setSpeakingIndex(index);
    window.speechSynthesis.speak(utterance);
  };

  const handleFeedback = async (messageIndex, isPositive) => {
    // Mark feedback as given for this message
    setFeedbackGiven((prev) => ({ ...prev, [messageIndex]: isPositive ? 'positive' : 'negative' }));

    // Submit initial feedback (thumbs up/down)
    try {
      await api.post("/feedback", {
        rating: isPositive ? 5 : 2,
        feedbackType: "chat",
        message: `Chat response feedback: ${isPositive ? 'Helpful' : 'Not helpful'}`,
      });

      // Show option to add comment
      setShowCommentInput((prev) => ({ ...prev, [messageIndex]: true }));
    } catch (err) {
      console.error("Error submitting feedback:", err);
    }
  };

  const handleSubmitComment = async (messageIndex) => {
    const comment = feedbackComments[messageIndex];
    if (!comment?.trim()) {
      setShowCommentInput((prev) => ({ ...prev, [messageIndex]: false }));
      return;
    }

    try {
      // Submit comment as additional feedback
      await api.post("/feedback", {
        rating: feedbackGiven[messageIndex] === 'positive' ? 5 : 2,
        feedbackType: "chat",
        message: `Additional comment: ${comment}`,
      });

      // Hide comment input after submission
      setShowCommentInput((prev) => ({ ...prev, [messageIndex]: false }));
      setFeedbackComments((prev) => ({ ...prev, [messageIndex]: '' }));
    } catch (err) {
      console.error("Error submitting comment:", err);
    }
  };

  const handleSkipComment = (messageIndex) => {
    // User skips feedback comment - proceed to next interaction
    setShowCommentInput((prev) => ({ ...prev, [messageIndex]: false }));
  };

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
  }, [messages.length]);

  useEffect(() => {
    // Load chat history on mount
    if (!hideSidebar) {
      loadChatHistory();
    }
  }, [hideSidebar]);

  // REMOVED AUTO-INITIALMESSAGE EFFECT

  const loadChatHistory = async () => {
    try {
      const { data } = await api.get("/ai/chat/history?limit=10");
      setSessions(data.sessions || []);
    } catch (err) {
      console.error("Error loading chat history:", err);
    }
  };

  const loadSession = async (sid) => {
    try {
      const { data } = await api.get(`/ai/chat/session/${sid}`);
      setSessionId(sid);
      setMessages(data.messages || []);
      setShowHistory(false);
    } catch (err) {
      console.error("Error loading session:", err);
    }
  };

  const startNewChat = () => {
    setSessionId(null);
    setMessages([
      {
        role: "assistant",
        content: getInitialGreeting()
      },
    ]);
    setShowHistory(false);
  };

  const deleteSession = async (sid, e) => {
    e.stopPropagation();
    if (!window.confirm("Delete this chat session?")) return;

    try {
      await api.delete(`/ai/chat/session/${sid}`);
      setSessions(sessions.filter(s => s.sessionId !== sid));
      if (sessionId === sid) {
        startNewChat();
      }
    } catch (err) {
      console.error("Error deleting session:", err);
    }
  };

  const send = async (textOverride = null) => {
    const textToSend = typeof textOverride === 'string' ? textOverride : input;
    if (!textToSend.trim() || loading) return;

    const userMessage = textToSend.trim();
    setMessages((m) => [...m, { role: "user", content: userMessage }]);
    if (!textOverride) setInput("");
    setLoading(true);

    try {
      const { data } = await api.post("/ai/chat", {
        message: userMessage,
        sessionId: sessionId,
        context: contextData
      });

      // Update sessionId if it's a new chat
      if (!sessionId && data.sessionId) {
        setSessionId(data.sessionId);
      }

      setMessages((m) => [...m, {
        role: "assistant",
        content: typeof data.response === 'string' ? data.response : JSON.stringify(data.response, null, 2),
        timestamp: new Date().toISOString()
      }]);

      // Refresh history to show updated session
      loadChatHistory();
    } catch (err) {
      console.error("Chat error:", err);

      // Determine error type based on error
      let errorMessage = "Sorry, I encountered an error. Please try again.";

      if (!navigator.onLine || err.message?.includes('Network Error') || err.code === 'ERR_NETWORK') {
        errorMessage = "Unable to connect to server. Please check your internet connection and try again.";
      } else if (err.response?.status === 503 || err.response?.status === 500) {
        errorMessage = "Service temporarily down. Please try again in a few moments.";
      } else if (err.response?.data?.detail) {
        errorMessage = typeof err.response.data.detail === 'string' ? err.response.data.detail : JSON.stringify(err.response.data.detail);
      }

      setMessages((m) => [...m, {
        role: "assistant",
        content: errorMessage,
        isError: true
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative w-full h-full flex gap-0">
      {/* Chat History Sidebar */}
      {!hideSidebar && (
        <div className={`relative shrink-0 transition-all duration-300 ${showHistory ? 'w-64' : 'w-0'}`}>
        <div className={`h-full rounded-l-2xl ring-1 ring-white/10 bg-neutral-900/50 backdrop-blur-xl transition-all duration-300 ${showHistory ? 'p-2 opacity-100' : 'p-0 opacity-0'}`}>
          {showHistory && (
            <>
              <div className="flex items-center justify-between mb-3 px-2">
                <h3 className="text-sm font-semibold text-white">Chat History</h3>
              </div>
              <button
                onClick={startNewChat}
                className="w-full mb-2 px-3 py-2 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-400 text-sm font-medium flex items-center justify-center gap-2 transition-colors"
              >
                <FiMessageSquare /> New Chat
              </button>
              <div className="space-y-1 max-h-[calc(100%-80px)] overflow-y-auto">
                {sessions.map((session) => (
                  <div
                    key={session.sessionId}
                    onClick={() => loadSession(session.sessionId)}
                    className={`group px-2 py-2 rounded-lg cursor-pointer flex items-start gap-2 transition-colors ${sessionId === session.sessionId
                        ? 'bg-indigo-600/20 text-white'
                        : 'hover:bg-white/5 text-slate-400 hover:text-white'
                      }`}
                  >
                    <div className="flex-1 min-w-0">
                      <div className="text-xs truncate">{session.lastMessage || "Empty conversation"}</div>
                      <div className="text-[10px] text-slate-500 mt-0.5">
                        {session.messageCount || 0} messages
                      </div>
                    </div>
                    <button
                      onClick={(e) => deleteSession(session.sessionId, e)}
                      className="opacity-0 group-hover:opacity-100 text-rose-400 hover:text-rose-300 transition-opacity"
                    >
                      <FiTrash2 className="text-xs" />
                    </button>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
      )}

      {/* Toggle Button - Draggable Handle Style (Document View) or Top Fixed Button (Main Lexibot Dashboard) */}
      {!hideSidebar && !isMainDashboard && (
        <div className="relative shrink-0 w-8 flex items-center justify-center">
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="absolute top-1/2 -translate-y-1/2 h-24 w-6 rounded-full bg-gradient-to-br from-indigo-600/20 to-indigo-700/20 hover:from-indigo-600/30 hover:to-indigo-700/30 ring-1 ring-white/10 hover:ring-white/20 backdrop-blur-xl flex items-center justify-center text-slate-400 hover:text-white transition-all shadow-lg hover:shadow-xl group cursor-pointer z-10"
            title={showHistory ? "Hide chat history" : "Show chat history"}
          >
            <div className="flex flex-col items-center gap-1">
              {showHistory ? (
                <FiChevronLeft className="text-sm group-hover:scale-110 transition-transform" />
              ) : (
                <FiChevronRight className="text-sm group-hover:scale-110 transition-transform" />
              )}
              <div className="flex flex-col gap-0.5">
                <div className="w-3 h-0.5 rounded-full bg-slate-500 group-hover:bg-slate-300 transition-colors"></div>
                <div className="w-3 h-0.5 rounded-full bg-slate-500 group-hover:bg-slate-300 transition-colors"></div>
                <div className="w-3 h-0.5 rounded-full bg-slate-500 group-hover:bg-slate-300 transition-colors"></div>
              </div>
            </div>
          </button>
        </div>
      )}

      {/* Removed the Main Lexibot Chat Top Fixed Button -- Moved to ChatDashboard Navbar */}


      {/* Chat Panel */}
      <div className="flex-1 min-w-0 h-full flex flex-col">
        <div className="relative rounded-3xl ring-1 ring-white/10 bg-neutral-900/50 backdrop-blur-xl h-full flex flex-col shadow-xl">
          <div className="p-4 sm:p-6 flex-1 flex flex-col min-h-0">
            <div
              ref={listRef}
              className="flex-1 overflow-y-auto pr-2 space-y-4 mb-4"
            >
              {messages.map((m, i) => (
                <div
                  key={i}
                  className={`max-w-[85%] md:max-w-[70%] lg:max-w-[65%] animate-fade-in ${m.role === "user" ? "ml-auto" : ""
                    }`}
                >
                  <div
                    className={`rounded-2xl px-4 py-3 text-sm leading-relaxed border whitespace-pre-wrap shadow-sm ${m.role === "user"
                        ? "bg-gradient-to-br from-indigo-600/90 to-indigo-700/90 text-white border-indigo-500/30"
                        : m.isError
                          ? "bg-rose-900/30 text-rose-200 border-rose-500/30"
                          : "bg-neutral-800/80 text-slate-100 border-white/10 backdrop-blur-sm"
                      }`}
                  >
                    {m.content}
                  </div>
                  {/* Feedback buttons for assistant messages */}
                  {m.role === "assistant" && !m.isError && (
                    <div className="mt-2 ml-1">
                      <div className="flex items-center gap-3">
                        {/* TTS Voice Output Button */}
                        <button
                          onClick={() => toggleSpeech(m.content, i)}
                          className={`p-1.5 rounded-lg flex items-center gap-1.5 text-xs transition-colors ${speakingIndex === i
                              ? "bg-indigo-600/30 text-indigo-300 border border-indigo-500/30"
                              : "bg-white/5 text-slate-400 border border-white/5 hover:bg-white/10 hover:text-slate-200"
                            }`}
                          title={speakingIndex === i ? "Stop speaking" : "Listen to response"}
                        >
                          {speakingIndex === i ? <FiVolumeX className="text-sm animate-pulse" /> : <FiVolume2 className="text-sm" />}
                          {speakingIndex === i ? "Listening" : "Read Aloud"}
                        </button>

                        {/* Divider */}
                        <div className="w-px h-4 bg-white/10"></div>

                        {!feedbackGiven[i] ? (
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-slate-500">Helpful?</span>
                            <button
                              onClick={() => handleFeedback(i, true)}
                              className="p-1 rounded hover:bg-white/10 text-slate-400 hover:text-green-400 transition-colors"
                              title="Helpful"
                            >
                              <FiThumbsUp className="text-sm" />
                            </button>
                            <button
                              onClick={() => handleFeedback(i, false)}
                              className="p-1 rounded hover:bg-white/10 text-slate-400 hover:text-rose-400 transition-colors"
                              title="Not helpful"
                            >
                              <FiThumbsDown className="text-sm" />
                            </button>
                          </div>
                        ) : showCommentInput[i] ? (
                          /* Optional comment input after rating */
                          <div className="space-y-2">
                            <span className="text-xs text-slate-500">
                              {feedbackGiven[i] === 'positive' ? '👍 Thanks!' : '👎 Sorry to hear that.'} Add a comment? (optional)
                            </span>
                            <div className="flex items-center gap-2">
                              <input
                                type="text"
                                value={feedbackComments[i] || ''}
                                onChange={(e) => setFeedbackComments((prev) => ({ ...prev, [i]: e.target.value }))}
                                placeholder="Tell us more..."
                                className="flex-1 px-3 py-1.5 text-xs rounded-lg border border-white/10 bg-neutral-800/50 text-slate-200 placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500/50"
                                onKeyDown={(e) => e.key === "Enter" && handleSubmitComment(i)}
                              />
                              <button
                                onClick={() => handleSubmitComment(i)}
                                className="px-2 py-1.5 text-xs rounded-lg bg-indigo-600/30 text-indigo-300 hover:bg-indigo-600/50 transition-colors"
                              >
                                Submit
                              </button>
                              <button
                                onClick={() => handleSkipComment(i)}
                                className="px-2 py-1.5 text-xs rounded-lg text-slate-400 hover:text-slate-200 transition-colors"
                              >
                                Skip
                              </button>
                            </div>
                          </div>
                        ) : (
                          <span className="text-xs text-slate-500">
                            {feedbackGiven[i] === 'positive' ? '👍 Thanks for your feedback!' : '👎 Thanks, we\'ll improve!'}
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Input bar - Fixed at bottom */}
            <div className="shrink-0 flex flex-col pt-2 border-t border-white/10">
              
              {/* Quick Action Tools */}
              {selectedDocAvailable && (
                 <div className="flex flex-wrap gap-2 mb-2 pb-2">
                    <button onClick={() => send("Summarize this judgment")} disabled={loading} className="px-3 py-1.5 bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 border border-indigo-500/20 rounded-full text-xs font-semibold transition-colors disabled:opacity-50">Summarize</button>
                    <button onClick={() => send("Explain this judgment in simple language")} disabled={loading} className="px-3 py-1.5 bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/20 rounded-full text-xs font-semibold transition-colors disabled:opacity-50">Explain</button>
                    <button onClick={() => send("Extract key points from this document")} disabled={loading} className="px-3 py-1.5 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border border-emerald-500/20 rounded-full text-xs font-semibold transition-colors disabled:opacity-50">Extract key points</button>
                 </div>
              )}

              <div className="flex items-center gap-2 bg-neutral-900/80 border border-white/10 p-1.5 rounded-2xl shadow-inner focus-within:ring-1 focus-within:ring-indigo-500/50 transition-all">
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && !loading && send()}
                  placeholder={isListening ? "Listening..." : "Type or speak your message..."}
                  disabled={loading}
                  className="flex-1 bg-transparent text-slate-100 px-3 py-1.5 text-sm placeholder:text-slate-500 focus:outline-none disabled:opacity-50"
                />
                
                {/* Voice Input Button */}
                <button
                  onClick={toggleVoiceInput}
                  disabled={loading}
                  className={`p-2 rounded-xl transition-all flex items-center justify-center shrink-0 ${isListening
                      ? "bg-rose-500/20 text-rose-400 animate-pulse scale-105"
                      : "bg-white/5 text-slate-400 hover:text-white hover:bg-white/10"
                    } disabled:opacity-50 disabled:hover:scale-100`}
                  title={isListening ? "Stop listening" : "Voice input"}
                >
                  {isListening ? <FiMicOff size={18} /> : <FiMic size={18} />}
                </button>
                
                {/* Send Button */}
                <button
                  onClick={() => send()}
                  disabled={loading || (!input.trim() && !isListening)}
                  className="p-2 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-md hover:shadow-lg transition-all disabled:opacity-50 hover:scale-105 active:scale-95 disabled:hover:scale-100 shrink-0"
                  title="Send message"
                >
                  {loading ? <FiLoader className="animate-spin" size={18} /> : <FiSend size={18} className="translate-y-[-1px] translate-x-[1px]" />}
                </button>
              </div>
            </div>
            {loading && (
              <div className="mt-2 text-xs text-slate-400 flex items-center gap-2">
                <FiLoader className="animate-spin" />
                <span>LexiBot is thinking...</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}


import { useContext, useState } from "react";
import { AuthContext } from "../../context/AuthContext";
import DashboardLayout from "../../layout/DashboardLayout";
import { FaComments, FaSearch, FaBrain, FaCommentDots, FaClipboardList } from "react-icons/fa";
import { FiChevronLeft, FiChevronRight } from "react-icons/fi";
import { useSearchParams } from "react-router-dom";
import ChatTab from "./components/ChatTab";
import OutcomePrediction from "./components/OutcomePrediction";
import Feedback from "./components/Feedback";
import ClientGuidance from "./components/ClientGuidance";

export default function ChatDashboard() {
  const { user } = useContext(AuthContext);
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTab = searchParams.get("tab") || "chat";
  const [showHistory, setShowHistory] = useState(false);

  const allTabs = [
    { id: "chat", label: "Chat", icon: FaComments },
    { id: "prediction", label: "Outcome Prediction", icon: FaBrain },
    { id: "guidance", label: "Client Guidance", icon: FaClipboardList },
    { id: "feedback", label: "Feedback", icon: FaCommentDots },
  ];

  const tabs = allTabs.filter(tab => {
    if (tab.id === "guidance" && user?.role === "advocate") return false;
    return true;
  });

  return (
    <DashboardLayout>
      <div className="relative w-full h-full flex flex-col">
        <div className="mb-6 shrink-0">
          <h1 className="text-3xl font-display font-bold text-white mb-2">LexiBot Assistant</h1>
          <p className="text-slate-400 text-sm">AI-powered legal research and assistance</p>
        </div>

        {/* Internal Navbar/Tabs - Sticky on scroll */}
        <div className="mb-6 shrink-0 sticky top-0 z-10 bg-neutral-950/80 backdrop-blur-xl -mx-6 px-6 py-2">
          <div className="flex items-center justify-between border-b border-white/10 overflow-x-auto scrollbar-hide">
            <div className="flex gap-2">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setSearchParams({ tab: tab.id })}
                    className={`px-4 py-3 flex items-center gap-2 font-medium text-sm transition-all border-b-2 whitespace-nowrap ${
                      isActive
                        ? "text-white border-indigo-500 bg-indigo-500/10 shadow-sm"
                        : "text-slate-400 border-transparent hover:text-slate-200 hover:border-slate-600/50"
                    }`}
                  >
                    <Icon className={isActive ? "text-indigo-400" : ""} />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </div>
            
            {/* Right Side Chat History Toggle */}
            {activeTab === "chat" && (
              <button
                onClick={() => setShowHistory(!showHistory)}
                className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium rounded-lg text-indigo-200 bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/30 transition-colors shrink-0 ml-4 mb-1"
                title={showHistory ? "Hide chat history" : "Show chat history"}
              >
                {showHistory ? <FiChevronLeft className="text-lg" /> : <FiChevronRight className="text-lg" />}
                <span>{showHistory ? "Hide History" : "Chat History"}</span>
              </button>
            )}
          </div>
        </div>

        {/* Tab Content - Takes remaining height */}
        <div className="relative flex-1 min-h-0 overflow-hidden">
          <div className="h-full overflow-y-auto">
            {activeTab === "chat" && <ChatTab isMainDashboard={true} externalShowHistory={showHistory} setExternalShowHistory={setShowHistory} />}
            {activeTab === "prediction" && <OutcomePrediction />}
            {activeTab === "guidance" && user?.role !== "advocate" && <ClientGuidance />}
            {activeTab === "feedback" && <Feedback />}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}

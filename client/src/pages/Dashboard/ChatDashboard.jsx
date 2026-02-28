import DashboardLayout from "../../layout/DashboardLayout";
import { useState } from "react";
import { FaComments, FaSearch, FaBrain, FaCommentDots } from "react-icons/fa";
import ChatTab from "./components/ChatTab";
import CaseLegalSearch from "./components/CaseLegalSearch";
import OutcomePrediction from "./components/OutcomePrediction";
import Feedback from "./components/Feedback";

export default function ChatDashboard() {
  const [activeTab, setActiveTab] = useState("chat");

  const tabs = [
    { id: "chat", label: "Chat", icon: FaComments },
    { id: "search", label: "Case Search", icon: FaSearch },
    { id: "prediction", label: "Outcome Prediction", icon: FaBrain },
    { id: "feedback", label: "Feedback", icon: FaCommentDots },
  ];

  return (
    <DashboardLayout>
      <div className="relative w-full h-full flex flex-col">
        <div className="mb-6 shrink-0">
          <h1 className="text-3xl font-display font-bold text-white mb-2">LexiBot Assistant</h1>
          <p className="text-slate-400 text-sm">AI-powered legal research and assistance</p>
        </div>

        {/* Internal Navbar/Tabs - Sticky on scroll */}
        <div className="mb-6 shrink-0 sticky top-0 z-10 bg-neutral-950/80 backdrop-blur-xl -mx-6 px-6 py-2">
          <div className="flex gap-2 border-b border-white/10 overflow-x-auto scrollbar-hide">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
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
        </div>

        {/* Tab Content - Takes remaining height */}
        <div className="relative flex-1 min-h-0 overflow-hidden">
          <div className="h-full overflow-y-auto">
            {activeTab === "chat" && <ChatTab />}
            {activeTab === "search" && <CaseLegalSearch />}
            {activeTab === "prediction" && <OutcomePrediction />}
            {activeTab === "feedback" && <Feedback />}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}

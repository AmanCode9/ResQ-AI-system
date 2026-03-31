"use client";

import { useState, useEffect } from "react";
import Sidebar from "./components/sidebar";
import IncidentViewer from "./components/IncidentViewer";
import Alerts from "./components/alert";

export interface Incident {
  id: string;
  source: "nlp" | "vision";
  location: string;
  severity: "CRITICAL" | "HIGH" | "MODERATE" | "LOW";
  status: string;
  timestamp: string;
}

export default function Home() {
  const [text, setText] = useState("");
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loadingText, setLoadingText] = useState(false);
  const [loadingVision, setLoadingVision] = useState(false);

  // Seed default incident
  useEffect(() => {
    setIncidents([
      {
        id: "default_seed_001",
        source: "nlp",
        location: "Sector 6",
        severity: "HIGH",
        status: "HIGH PRIORITY ALERT",
        timestamp: new Date().toISOString()
      }
    ]);
  }, []);

  const simulateDelay = (ms: number) => new Promise((res) => setTimeout(res, ms));

  const analyzeText = async () => {
    if (!text.trim()) return;
    setLoadingText(true);
    try {
      await simulateDelay(600);
      const res = await fetch("http://localhost:5000/api/analyze-text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
      });
      const data: Incident = await res.json();
      if (data && data.id) {
        setIncidents((prev) => [data, ...prev]);
        setText("");
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingText(false);
    }
  };

  const analyzeVision = async () => {
    setLoadingVision(true);
    try {
      await simulateDelay(1000);
      const res = await fetch("http://localhost:5000/api/analyze-vision");
      const data: Incident = await res.json();
      if (data && data.id) {
        setIncidents((prev) => [data, ...prev]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingVision(false);
    }
  };

  const activeAlertsCount = incidents.length;
  const lastUpdated = incidents.length > 0 ? new Date(incidents[0].timestamp).toLocaleTimeString() : "--:--:--";

  return (
    <div className="flex h-screen bg-gray-950 text-white overflow-hidden font-sans">
      <Sidebar />

      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Header */}
        <div className="p-5 bg-gray-900 border-b border-gray-800 flex justify-between items-center z-10 shadow-md">
          <div className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-red-400 to-orange-500">
            ResQ-AI Active Operations Room
          </div>
          <div className="flex gap-6 text-sm text-gray-400">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
              System Online
            </div>
            <div>Last Updated: <span className="text-gray-100 font-medium">{lastUpdated}</span></div>
            <div>Active Incidents: <span className="text-gray-100 font-medium">{activeAlertsCount}</span></div>
          </div>
        </div>

        {/* Control Panel */}
        <div className="p-5 bg-gray-950 border-b border-gray-800 shrink-0">
          <div className="flex max-w-4xl gap-3">
            <div className="flex-1 relative">
              <input
                value={text}
                onChange={(e) => setText(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && analyzeText()}
                placeholder="Intercepted transmission (e.g. 'Need help at Sector 6 immediately!')"
                className="w-full p-3 pl-4 rounded-lg bg-gray-900 border border-gray-700 focus:outline-none focus:border-red-500 focus:ring-1 focus:ring-red-500 transition-all text-sm placeholder-gray-500"
              />
            </div>
            <button
              onClick={analyzeText}
              disabled={loadingText}
              className="px-6 py-3 bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white rounded-lg font-medium transition-all shadow-lg shadow-red-900/20 active:scale-95 flex items-center gap-2 min-w-[150px] justify-center"
            >
              {loadingText ? (
                <span className="flex items-center gap-2"><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div> Parsing...</span>
              ) : "Analyze Comms"}
            </button>
            <button
              onClick={analyzeVision}
              disabled={loadingVision}
              className="px-6 py-3 bg-slate-800 hover:bg-slate-700 border border-slate-600 disabled:opacity-50 text-white rounded-lg font-medium transition-all shadow-lg active:scale-95 flex items-center gap-2 min-w-[150px] justify-center"
            >
              {loadingVision ? (
                <span className="flex items-center gap-2"><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div> Scanning...</span>
              ) : "Run UAV Vision Sentinel"}
            </button>
          </div>
        </div>

        {/* Main Content Area: Incident Viewer + Alerts */}
        <div className="flex flex-1 overflow-hidden relative">
          <div className="flex-1 relative bg-gray-950 p-6 flex flex-col justify-center items-center shadow-inner">
            {incidents.length > 0 ? (
              <IncidentViewer incident={incidents[0]} />
            ) : (
              <div className="text-gray-500 italic">Awaiting interceptions...</div>
            )}
          </div>
          
          <Alerts incidents={incidents} />
        </div>
      </div>
    </div>
  );
}
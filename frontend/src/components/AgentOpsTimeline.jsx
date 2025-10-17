import React from "react";

const PIPELINE = [
  {
    id: "sense",
    title: "Master Agent • Orchestrate",
    highlight: "Listens to streaming health data and dispatches the right workers in 18-second micro-cycles.",
    details: "Cycle 27 • Live • Last anomaly scan 12s ago",
    accent: "#00eaff"
  },
  {
    id: "analyze",
    title: "Data Analysis → Diagnosis",
    highlight: "Correlates telemetry, DTC codes & history to forecast failures before they happen.",
    details: "4 high-priority issues escalated this hour",
    accent: "#60a5fa"
  },
  {
    id: "engage",
    title: "Customer Engagement",
    highlight: "Chat + voice concierge briefs owners with empathetic language and recommended actions.",
    details: "Avg. conversion 82% • 12 proactive outreaches today",
    accent: "#f97316"
  },
  {
    id: "schedule",
    title: "Scheduling • Service Ops",
    highlight: "Optimizes center capacity, balances bays, and locks in appointments across the fleet.",
    details: "5 slots remaining for Friday • 2 walk-ins rerouted",
    accent: "#34d399"
  },
  {
    id: "feedback",
    title: "Feedback → Manufacturing Loop",
    highlight: "Closed-loop RCA/CAPA updates design teams with recurring defect intelligence.",
    details: "3 new CAPA tickets pushed • Turnaround 6h",
    accent: "#a855f7"
  }
];

export default function AgentOpsTimeline(){
  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-5">
        <h4 className="section-heading">Agentic Orchestration</h4>
        <span className="pill">Live Demo</span>
      </div>
      <div className="space-y-5">
        {PIPELINE.map((step, index)=>(
          <div key={step.id} className="relative pl-6">
            <span className="absolute left-0 top-2 h-3 w-3 rounded-full" style={{background: step.accent, boxShadow: `0 0 12px ${step.accent}66`}} />
            {index !== PIPELINE.length - 1 && (
              <span className="absolute left-[5px] top-5 h-full w-[1px] bg-white/10" />
            )}
            <p className="text-sm font-semibold text-white/85">{step.title}</p>
            <p className="text-sm text-white/60 leading-relaxed">{step.highlight}</p>
            <p className="text-xs uppercase tracking-[0.3em] text-white/30">{step.details}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

import React from "react";

const SCENARIOS = [
  {
    title: "Urgent Failure Escalation",
    emphasis: "Engine temp spike on Fleet Unit 07",
    narrative: "Master Agent triggered a red alert, voice concierge patched the owner in under 45 seconds, and a field technician was dispatched.",
    resolution: "Status: Cooling protocol active • ETA to resolution 14 min",
    tone: "#f87171"
  },
  {
    title: "Appointment Declined",
    emphasis: "Owner rescheduled due to travel",
    narrative: "Scheduling Agent rerouted the bay to another vehicle, while Customer Engagement promises a concierge pickup next Tuesday.",
    resolution: "Status: Follow-up reminder queued • Satisfaction nudge in 12h",
    tone: "#fbbf24"
  },
  {
    title: "Multi-Vehicle Fleet Sync",
    emphasis: "Five vans require staggered servicing",
    narrative: "Capacity model forecasted workload and auto-built a rolling schedule across North & South branches to avoid downtime.",
    resolution: "Status: 3 confirmed, 2 pending voice confirmation",
    tone: "#34d399"
  }
];

export default function EdgeCaseDeck(){
  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-4">
        <h4 className="section-heading">Edge Cases in Motion</h4>
        <span className="pill">Real Scenarios</span>
      </div>
      <div className="grid gap-4">
        {SCENARIOS.map((item, idx)=>(
          <div
            key={idx}
            className="rounded-2xl border border-white/10 p-4"
            style={{ background: "rgba(255,255,255,0.04)" }}
          >
            <p className="text-xs uppercase tracking-[0.35em] text-white/40 mb-2">{item.title}</p>
            <p className="text-sm font-semibold text-white/85" style={{color:item.tone}}>{item.emphasis}</p>
            <p className="text-sm text-white/65 mt-1 leading-relaxed">{item.narrative}</p>
            <p className="text-xs text-white/45 mt-2">{item.resolution}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

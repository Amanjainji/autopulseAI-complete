import React from "react";

const EVENTS = [
  {
    time: "22:18:02",
    actor: "VoiceAgent",
    action: "Outbound call blocked",
    anomaly: 0.95,
    rationale: "Attempted voice render outside approved time block."
  },
  {
    time: "22:19:44",
    actor: "SchedulingAgent",
    action: "Telemetry access denied",
    anomaly: 0.82,
    rationale: "UEBA policy prevented cross-domain data pull."
  }
];

export default function UEBASecurityCard(){
  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-3">
        <h4 className="section-heading">UEBA Watchtower</h4>
        <span className="badge-accent">Adaptive Shield</span>
      </div>
      <p className="text-sm text-white/70 leading-relaxed">
        UEBA establishes behavior baselines for every agent and flags anomalies before they become incidents. Think of it as a
        co-pilot auditing autonomy: if the Scheduling Agent ever touches telematics, it is quarantined instantly.
      </p>
      <div className="mt-4 space-y-3">
        {EVENTS.map((item, idx)=>(
          <div key={idx} className="rounded-xl border border-white/10 px-3 py-2" style={{background:"rgba(255,255,255,0.03)"}}>
            <div className="flex items-center justify-between text-xs uppercase tracking-[0.28em] text-white/40">
              <span>{item.time}</span>
              <span>Score {item.anomaly.toFixed(2)}</span>
            </div>
            <div className="mt-1 text-sm font-semibold text-white/85">{item.actor} — {item.action}</div>
            <div className="text-xs text-white/50 mt-1">{item.rationale}</div>
          </div>
        ))}
      </div>
      <div className="mt-4 text-xs text-white/35 uppercase tracking-[0.3em]">
        Continuous verification • Policy enforcement • Zero trust for agentic AI
      </div>
    </div>
  );
}

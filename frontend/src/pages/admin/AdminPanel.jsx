import React, { useEffect, useMemo, useState } from "react";
import Navbar from "../../components/Navbar.jsx";
import PageLoader from "../../components/PageLoader.jsx";
import api from "../../lib/api.js";
import { listRegisteredUsers, registerUserProfile } from "../../lib/session.js";

const CASE_FEED = [
  {
    id: "CASE-4821",
    customer: "Aman Jain",
    vehicle: "Mahindra Scorpio N",
    priority: "critical",
    summary: "Engine temperature spikes flagged by DataAnalysis agent.",
    aiResponse:
      "Scheduling Agent proposed 18 Oct, 08:30 slot at Indiranagar workshop.",
    origin: "voice concierge",
    updatedAt: new Date().toISOString(),
  },
  {
    id: "CASE-4735",
    customer: "Neha Menon",
    vehicle: "Tata Nexon EV",
    priority: "high",
    summary:
      "Battery cycling degradation detected; chatbot recommended charging audit.",
    aiResponse:
      "Customer Engagement Agent shared preventive checklist and pushed app notification.",
    origin: "web chat",
    updatedAt: new Date(Date.now() - 3600_000).toISOString(),
  },
];

export default function AdminPanel() {
  const [llm, setLLM] = useState({ enabled: false, provider: "", model: "" });
  const [stats, setStats] = useState(null);
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [roster, setRoster] = useState(listRegisteredUsers());
  const [form, setForm] = useState({
    name: "",
    email: "",
    phone: "",
    commodity: "",
    channel: "call",
  });
  const [issuedCode, setIssuedCode] = useState(null);
  const [status, setStatus] = useState({ tone: "info", text: "" });

  const cases = useMemo(() => CASE_FEED, []);

  const refresh = async () => {
    setLoading(true);
    try {
      const [statusRes, dashRes, appointmentRes] = await Promise.all([
        api.get("/admin/models/status").catch(() => ({ data: llm })),
        api.get("/dashboard").catch(() => ({ data: null })),
        api.get("/appointments").catch(() => ({ data: { appointments: [] } })),
      ]);
      setLLM(statusRes.data || llm);
      setStats(dashRes.data);
      setAppointments(appointmentRes.data?.appointments || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const enableClaude = async () => {
    try {
      await api.post("/admin/models/enable_claude");
      refresh();
    } catch {}
  };
  const disableLLM = async () => {
    try {
      await api.post("/admin/models/disable_llm");
      refresh();
    } catch {}
  };

  const registerUser = () => {
    if (!form.name || !form.email) {
      setStatus({ tone: "error", text: "Please provide name and email." });
      return;
    }
    const record = registerUserProfile({
      name: form.name,
      email: form.email,
      phone: form.phone,
      commodity: form.commodity || "Fleet maintenance",
      channel: form.channel,
    });
    setRoster(listRegisteredUsers());
    setIssuedCode(record.accessCode);
    setStatus({
      tone: "success",
      text: `New user onboarded. Access code ${record.accessCode} issued.`,
    });
    setForm({ name: "", email: "", phone: "", commodity: "", channel: "call" });
  };

  const formatDate = (value) => new Date(value).toLocaleString();

  return (
    <div className="min-h-screen text-white bg-[rgba(6,10,18,1)]">
      <Navbar />
      <div className="relative max-w-7xl mx-auto p-8 space-y-8">
        {loading && <PageLoader label="Fetching live system status..." />}

        <header className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-white/40">
              Admin Control Center
            </p>
            <h1 className="text-3xl font-semibold tracking-tight mt-2">
              AI orchestration &amp; human oversight
            </h1>
            <p className="text-white/60 text-sm mt-3 max-w-2xl">
              Review agent activity, register new users, and step in with manual
              guidance whenever cases require a human concierge.
            </p>
          </div>
          <div className="flex flex-wrap gap-3 text-sm">
            <button className="btn-primary" onClick={enableClaude}>
              Enable Claude
            </button>
            <button className="btn-ghost" onClick={disableLLM}>
              Disable LLM
            </button>
          </div>
        </header>

        <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="card p-5">
            <p className="text-xs uppercase tracking-[0.3em] text-white/40">
              LLM Provider
            </p>
            <h3 className="mt-2 text-lg font-semibold">
              {llm.provider || "Offline"}
            </h3>
            <p className="text-sm text-white/60">Model: {llm.model || "--"}</p>
            <p
              className={`text-xs mt-2 ${
                llm.enabled ? "text-emerald-300" : "text-white/40"
              }`}
            >
              {llm.enabled ? "Active" : "Suspended"}
            </p>
          </div>
          <div className="card p-5">
            <p className="text-xs uppercase tracking-[0.3em] text-white/40">
              Fleet Coverage
            </p>
            <h3 className="mt-2 text-lg font-semibold">
              {stats?.system_overview?.total_vehicles ?? "--"} vehicles
            </h3>
            <p className="text-sm text-white/60">
              {stats?.components?.worker_agents ?? 6} worker agents online
            </p>
          </div>
          <div className="card p-5">
            <p className="text-xs uppercase tracking-[0.3em] text-white/40">
              Active Cases
            </p>
            <h3 className="mt-2 text-lg font-semibold">
              {appointments.length}
            </h3>
            <p className="text-sm text-white/60">
              Last sync • {formatDate(Date.now())}
            </p>
          </div>
        </section>

        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 card p-6 space-y-5">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold">User directory</h2>
                <p className="text-sm text-white/60">
                  Drivers, fleet managers, and concierge agents with valid
                  access codes.
                </p>
              </div>
              <span className="pill bg-white/5 text-white/70">
                {roster.length} records
              </span>
            </div>
            <div className="space-y-3 max-h-72 overflow-y-auto pr-2">
              {roster.map((entry) => (
                <div
                  key={`${entry.id}-${entry.accessCode}`}
                  className="flex flex-col md:flex-row md:items-center justify-between gap-3 p-4 border border-white/10 rounded-xl bg-white/3"
                >
                  <div>
                    <p className="font-semibold text-white">{entry.name}</p>
                    <p className="text-xs uppercase tracking-[0.3em] text-white/40">
                      {entry.id}
                    </p>
                    <p className="text-sm text-white/60">{entry.email}</p>
                    <p className="text-xs text-white/40">
                      Channel: {entry.channel?.toUpperCase?.() || entry.channel}{" "}
                      • {formatDate(entry.createdAt)}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-white/60">{entry.commodity}</p>
                    <span className="pill bg-[var(--accent)]/15 text-[var(--accent)] mt-2 inline-block">
                      {entry.accessCode}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="card p-6 space-y-4">
            <div>
              <h2 className="text-xl font-semibold">Register new user</h2>
              <p className="text-sm text-white/60">
                Capture contact, commodity, and preferred channel. An access
                code is generated instantly.
              </p>
            </div>
            <input
              className="input"
              placeholder="Full name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
            <input
              className="input"
              placeholder="Work email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
            <input
              className="input"
              placeholder="Contact number"
              value={form.phone}
              onChange={(e) => setForm({ ...form, phone: e.target.value })}
            />
            <input
              className="input"
              placeholder="Commodity or business unit"
              value={form.commodity}
              onChange={(e) => setForm({ ...form, commodity: e.target.value })}
            />
            <select
              className="input"
              value={form.channel}
              onChange={(e) => setForm({ ...form, channel: e.target.value })}
            >
              <option value="call">Voice concierge</option>
              <option value="chat">Chat assistant</option>
              <option value="web">Web portal</option>
            </select>
            {status.text && (
              <div
                className={`text-sm ${
                  status.tone === "error"
                    ? "text-red-300"
                    : status.tone === "success"
                    ? "text-emerald-300"
                    : "text-white/60"
                }`}
              >
                {status.text}
              </div>
            )}
            <button className="btn-primary w-full" onClick={registerUser}>
              Generate access code
            </button>
            {issuedCode && (
              <div className="p-4 rounded-xl bg-white/5 border border-white/10 text-center">
                <p className="text-xs text-white/60">
                  Share this code with the user
                </p>
                <p className="text-2xl font-semibold text-[var(--accent)] mt-1">
                  {issuedCode}
                </p>
              </div>
            )}
          </div>
        </section>

        <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">Service activity</h2>
              <span className="pill bg-white/5 text-white/70">Live feed</span>
            </div>
            <div className="space-y-3 max-h-72 overflow-y-auto pr-2">
              {appointments.length === 0 && (
                <p className="text-white/60 text-sm">
                  No scheduled appointments yet. New bookings via chat, voice,
                  or web will appear here instantly.
                </p>
              )}
              {appointments.map((item) => (
                <div
                  key={item.id}
                  className="p-4 border border-white/10 rounded-xl bg-white/3 flex justify-between items-start gap-3"
                >
                  <div>
                    <p className="font-semibold text-white">
                      {item.customer_id}
                    </p>
                    <p className="text-sm text-white/60">{item.service_type}</p>
                    <p className="text-xs text-white/40">
                      {item.appointment_date} • {item.appointment_time}
                    </p>
                  </div>
                  <div className="text-right text-xs text-white/50">
                    <div className="pill bg-[var(--accent)]/15 text-[var(--accent)]">
                      {item.priority?.toUpperCase?.() || item.priority}
                    </div>
                    <div className="mt-2">
                      Technician {item.assigned_technician || "--"}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="card p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">AI case intelligence</h2>
              <span className="pill bg-white/5 text-white/70">
                Agent transcripts
              </span>
            </div>
            <div className="space-y-3 max-h-72 overflow-y-auto pr-2">
              {cases.map((record) => (
                <div
                  key={record.id}
                  className="p-4 border border-white/10 rounded-xl bg-white/3"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-semibold text-white">
                        {record.customer}
                      </p>
                      <p className="text-sm text-white/60">{record.vehicle}</p>
                    </div>
                    <span
                      className={`pill ${
                        record.priority === "critical"
                          ? "bg-red-500/20 text-red-300"
                          : "bg-amber-500/20 text-amber-300"
                      }`}
                    >
                      {record.priority.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-sm text-white/70 mt-3">{record.summary}</p>
                  <p className="text-sm text-[var(--accent)] mt-2">
                    {record.aiResponse}
                  </p>
                  <p className="text-xs text-white/40 mt-3">
                    Origin: {record.origin.toUpperCase()} •{" "}
                    {formatDate(record.updatedAt)}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

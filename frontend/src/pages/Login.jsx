import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../lib/api.js";
import {
  seedAccessDirectory,
  listRegisteredUsers,
  validateUserLogin,
  validateAdminLogin,
  clearSession
} from "../lib/session.js";
import PageLoader from "../components/PageLoader.jsx";

export default function Login(){
  const [mode, setMode] = useState("user");
  const [identifier, setIdentifier] = useState("");
  const [secret, setSecret] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState({ tone: "info", text: "" });
  const [showDirectory, setShowDirectory] = useState(false);
  const navigate = useNavigate();

  useEffect(()=>{
    try{ seedAccessDirectory(); }catch{}
    clearSession();
  },[]);

  const directory = useMemo(()=> listRegisteredUsers(), [showDirectory, mode]);

  const submit = async ()=>{
    if(!identifier || !secret){
      setMessage({ tone: "error", text: "Please enter all required details." });
      return;
    }
    setBusy(true);
    setMessage({ tone: "info", text: "Authenticating with command center..." });
    try{
      if(mode === "user"){
        const match = validateUserLogin({ identifier, code: secret.toUpperCase() });
        if(match){
          localStorage.setItem("token", `demo-${match.accessCode}`);
          setMessage({ tone: "success", text: `Welcome back, ${match.name}. Redirecting to your vehicle workspace.` });
          setTimeout(()=> navigate("/dashboard"), 650);
          return;
        }
        setMessage({ tone: "error", text: "The access code does not match our records. Contact your service advisor." });
      }else{
        const admin = validateAdminLogin({ email: identifier, code: secret.toUpperCase() });
        if(admin){
          localStorage.setItem("token", "admin-session");
          setMessage({ tone: "success", text: "Administrator session established. Opening control console." });
          setTimeout(()=> navigate("/admin"), 650);
          return;
        }
        setMessage({ tone: "error", text: "Invalid administrator credentials." });
      }
    }finally{
      setBusy(false);
    }
  };

  const quickDemoLogin = async ()=>{
    try{
      setBusy(true);
      const res = await api.post("/api/login", { email: "demo@autopulse.in", password: "demo" });
      localStorage.setItem("token", res.data.access_token);
      navigate("/dashboard");
    }catch{
      setBusy(false);
      setMessage({ tone: "error", text: "Demo login is currently unavailable." });
    }
  };

  return (
    <div className="min-h-screen grid lg:grid-cols-2 text-white">
      <aside className="relative hidden lg:flex flex-col justify-between bg-[radial-gradient(circle_at_top,_rgba(38,162,255,0.18),_rgba(4,10,24,0.92))] p-12 border-r border-white/10">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-white/40">AutoPulse Command Network</p>
          <h1 className="mt-6 text-4xl font-semibold leading-tight">Secure access for mobility leaders &amp; service concierge teams.</h1>
          <p className="mt-4 text-white/60 max-w-lg">One login orchestrates predictive maintenance, customer outreach, and real-time insights. Choose your console to continue.</p>
        </div>
        <div className="space-y-3">
          <div className="text-sm text-white/60 uppercase tracking-[0.35em]">Trusted by</div>
          <div className="flex flex-wrap gap-3 text-sm text-white/50">
            <span className="px-4 py-2 rounded-full bg-white/5">Mahindra Mobility</span>
            <span className="px-4 py-2 rounded-full bg-white/5">EV Fleet Ops</span>
            <span className="px-4 py-2 rounded-full bg-white/5">Autonomous Concierge</span>
          </div>
        </div>
      </aside>

      <main className="relative flex items-center justify-center bg-[rgba(6,10,18,1)]">
        {busy && <PageLoader label={mode === "admin" ? "Validating admin credentials..." : "Authenticating access code..."} />}
        <div className="w-full max-w-lg px-8 py-12">
          <div className="flex items-center justify-between mb-8">
            <div>
              <p className="text-xs uppercase tracking-[0.35em] text-white/40">Select Console</p>
              <h2 className="text-3xl font-semibold tracking-tight mt-2">Sign in to AutoPulse</h2>
            </div>
            <button onClick={quickDemoLogin} className="btn-ghost text-xs uppercase tracking-[0.3em]">Demo login</button>
          </div>

          <div className="flex gap-2 mb-8">
            {[{ key: "user", label: "Driver / Fleet" }, { key: "admin", label: "Admin Console" }].map(option => (
              <button
                key={option.key}
                onClick={()=>{ setMode(option.key); setMessage({ tone: "info", text: "" }); }}
                className={`flex-1 px-4 py-3 rounded-xl border transition ${mode === option.key ? "border-[var(--accent)] bg-[var(--accent)]/10 text-white" : "border-white/15 bg-white/5 text-white/60 hover:text-white"}`}
              >
                <span className="text-sm font-semibold">{option.label}</span>
              </button>
            ))}
          </div>

          <div className="space-y-4">
            <div>
              <label className="text-xs uppercase tracking-[0.3em] text-white/40">{mode === "admin" ? "Official Email" : "Registered Email / Mobile / ID"}</label>
              <input
                value={identifier}
                onChange={e=>setIdentifier(e.target.value)}
                placeholder={mode === "admin" ? "admin@autopulse.in" : "amaan.jain@autopulse.in"}
                className="w-full input mt-2"
              />
            </div>
            <div>
              <label className="text-xs uppercase tracking-[0.3em] text-white/40">{mode === "admin" ? "Administrator Code" : "Secure Access Code"}</label>
              <input
                value={secret}
                onChange={e=>setSecret(e.target.value.toUpperCase())}
                placeholder={mode === "admin" ? "ADMIN-8845" : "SCORP-4721"}
                className="w-full input mt-2"
              />
            </div>
            {message.text && (
              <div className={`text-sm ${message.tone === "error" ? "text-red-300" : message.tone === "success" ? "text-emerald-300" : "text-white/60"}`}>
                {message.text}
              </div>
            )}
            <button onClick={submit} className="w-full btn-primary py-3 text-base font-semibold" disabled={busy}>
              {mode === "admin" ? "Enter Admin Console" : "Launch Driver Workspace"}
            </button>
          </div>

          <div className="mt-10 flex items-center justify-between text-sm text-white/60">
            <button onClick={()=>navigate("/signup")}>Need to request access?</button>
            <button onClick={()=>setShowDirectory(v=>!v)} className="text-[var(--accent)]">View latest access codes</button>
          </div>

          {showDirectory && (
            <div className="mt-6 p-4 bg-white/5 border border-white/10 rounded-xl text-sm text-white/80 max-h-48 overflow-y-auto">
              <div className="text-xs uppercase tracking-[0.3em] text-white/40 mb-3">Recently issued codes</div>
              <div className="space-y-3">
                {directory.map(entry => (
                  <div key={`${entry.id}-${entry.accessCode}`} className="flex items-start justify-between gap-3">
                    <div>
                      <div className="font-semibold text-white">{entry.name}</div>
                      <div className="text-white/60">{entry.commodity}</div>
                      <div className="text-xs text-white/40">{typeof entry.channel === "string" ? entry.channel.toUpperCase() : entry.channel} • {new Date(entry.createdAt).toLocaleString()}</div>
                    </div>
                    <span className="pill bg-[var(--accent)]/20 text-[var(--accent)]">{entry.accessCode}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

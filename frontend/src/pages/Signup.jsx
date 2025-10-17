import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registerUserProfile } from "../lib/session.js";

export default function Signup(){
  const [form, setForm] = useState({
    name: "",
    phone: "",
    email: "",
    commodity: "",
    vehicle: ""
  });
  const [issuedCode, setIssuedCode] = useState(null);
  const [status, setStatus] = useState({ tone: "info", text: "" });
  const navigate = useNavigate();

  const handleChange = (key) => (event) => {
    setForm(prev => ({ ...prev, [key]: event.target.value }));
  };

  const submit = ()=>{
    if(!form.name || !form.phone || !form.email){
      setStatus({ tone: "error", text: "Please provide your name, contact number, and email." });
      return;
    }
    const record = registerUserProfile({
      name: form.name,
      phone: form.phone,
      email: form.email,
      commodity: form.commodity || `${form.vehicle || "Vehicle"} | Customer fleet`,
      channel: "self-service"
    });
    setIssuedCode(record.accessCode);
    setStatus({ tone: "success", text: `Access request logged. Your concierge code is ${record.accessCode}.` });
    setTimeout(()=> navigate("/login"), 1600);
  };

  return (
    <div className="min-h-screen bg-[rgba(7,12,18,1)] text-white">
      <div className="max-w-5xl mx-auto grid md:grid-cols-2 gap-10 px-8 py-16">
        <div className="space-y-6">
          <p className="text-xs uppercase tracking-[0.35em] text-white/40">Request Access</p>
          <h1 className="text-4xl font-semibold leading-tight">Set up your driver workspace.</h1>
          <p className="text-white/60 text-sm leading-relaxed">Provide a few details and your concierge access code will be generated instantly. Share this code with drivers or fleet managers who need to log in via chat, voice concierge, or service booking.</p>
          <div className="grid grid-cols-2 gap-4 text-sm text-white/70">
            <div className="p-4 rounded-xl border border-white/10 bg-white/5">
              <div className="text-3xl font-semibold text-white">28</div>
              <div className="text-xs uppercase tracking-[0.35em] text-white/40 mt-2">Active Fleets</div>
            </div>
            <div className="p-4 rounded-xl border border-white/10 bg-white/5">
              <div className="text-3xl font-semibold text-white">94%</div>
              <div className="text-xs uppercase tracking-[0.35em] text-white/40 mt-2">Service Satisfaction</div>
            </div>
            <div className="col-span-2 p-4 rounded-xl border border-[var(--accent)]/40 bg-[var(--accent)]/10 text-sm text-white/80">
              Concierge support will confirm every request within 24 hours and share onboarding best practices for your drivers.
            </div>
          </div>
        </div>

        <div className="card p-8 space-y-5">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-white/40">Applicant details</p>
            <h2 className="text-2xl font-semibold mt-2">Create your access record</h2>
          </div>
          <input value={form.name} onChange={handleChange("name") } placeholder="Full name" className="w-full input" />
          <input value={form.phone} onChange={handleChange("phone") } placeholder="Contact number" className="w-full input" />
          <input value={form.email} onChange={handleChange("email") } placeholder="Work email" className="w-full input" />
          <input value={form.vehicle} onChange={handleChange("vehicle") } placeholder="Primary vehicle / fleet" className="w-full input" />
          <textarea value={form.commodity} onChange={handleChange("commodity") } placeholder="Commodity or service category (e.g., Electric SUV program, Fleet concierge)" className="w-full input min-h-[96px]" />
          {status.text && (
            <div className={`text-sm ${status.tone === "error" ? "text-red-300" : status.tone === "success" ? "text-emerald-300" : "text-white/60"}`}>
              {status.text}
            </div>
          )}
          <button onClick={submit} className="btn-primary w-full py-3 text-base font-semibold">Generate Access Code</button>
          {issuedCode && (
            <div className="p-4 rounded-xl bg-white/5 border border-white/10 text-center">
              <p className="text-sm text-white/60">Use this code on the login screen:</p>
              <p className="text-2xl font-semibold text-[var(--accent)] mt-1">{issuedCode}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

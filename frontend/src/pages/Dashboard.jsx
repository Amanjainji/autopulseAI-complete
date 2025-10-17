import React, { Suspense, lazy, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Navbar from "../components/Navbar.jsx";
import Sidebar from "../components/Sidebar.jsx";
import api from "../lib/api.js";
import useTelemetry from "../lib/useTelemetry.js";
import PageLoader from "../components/PageLoader.jsx";

const VehicleCard = lazy(() => import("../components/VehicleCard.jsx"));
const HealthGraph = lazy(() => import("../components/HealthGraph.jsx"));
const DonutChart = lazy(() => import("../components/DonutChart.jsx"));
const Car3D = lazy(() => import("../components/Car3D.jsx"));
const NotificationPanel = lazy(() => import("../components/NotificationPanel.jsx"));
const ChatWidget = lazy(() => import("../components/ChatWidget.jsx"));
const FooterNav = lazy(() => import("../components/FooterNav.jsx"));

export default function Dashboard(){
  const [vehicle, setVehicle] = useState(null);
  const [customer, setCustomer] = useState(null);
  const [voiceStatus, setVoiceStatus] = useState({ state: "idle", message: "" });
  const [loading, setLoading] = useState(true);
  const { telemetry, status } = useTelemetry(vehicle?.id || vehicle?.vehicle_id || "V1000");

  useEffect(()=>{
    const load = async ()=>{
      try{
        const [vres, ures] = await Promise.all([
          api.get("/api/vehicle"),
          api.get("/api/user")
        ]);
        const vehicles = Array.isArray(vres.data) ? vres.data : (vres.data?.vehicles || []);
        const users = Array.isArray(ures.data) ? ures.data : (ures.data?.customers || []);
        const firstVehicle = vehicles[0] || { id: "V1000", model: "Demo Model", model_number: "DEMO-1", vin: "VIN-DEMO" };
        const owner = users.find((u)=>u.vehicle_id === (firstVehicle.id || firstVehicle.vehicle_id)) || users[0] || null;
        setVehicle(firstVehicle);
        if(owner){
          setCustomer(owner);
          sessionStorage.setItem("autopulse.primaryCustomer", JSON.stringify(owner));
        }
        sessionStorage.setItem("autopulse.primaryVehicle", JSON.stringify(firstVehicle));
      }catch(err){
        console.error("Failed to load dashboard data", err);
        const fallbackVehicle = { id: "V1000", model: "Demo Model", model_number: "DEMO-1", vin: "VIN-DEMO" };
        setVehicle(fallbackVehicle);
  const fallbackCustomer = { id: "CUST-001", name: "Amaan Jain", phone: "+91-98765-43210" };
        setCustomer(fallbackCustomer);
        sessionStorage.setItem("autopulse.primaryVehicle", JSON.stringify(fallbackVehicle));
        sessionStorage.setItem("autopulse.primaryCustomer", JSON.stringify(fallbackCustomer));
      }
      finally{
        setLoading(false);
      }
    };
    load();
  },[]);

  const handleVoiceCall = async ()=>{
    if(!customer){
      setVoiceStatus({ state: "error", message: "Customer contact unavailable" });
      return;
    }
    const vehicleId = vehicle?.id || vehicle?.vehicle_id;
    setVoiceStatus({ state: "pending", message: "Dialing via AI concierge..." });
    try{
      const response = await api.post("/api/voice/outbound", {
        customer_id: customer.id || "CUST-001",
        customer_name: customer.name || "AutoPulse Driver",
        phone: customer.phone || "",
        message: `We detected a maintenance insight on your ${vehicle?.model || "vehicle"}. Let's confirm the recommended action.`,
        metadata: {
          vehicle_id: vehicleId,
          vehicle_model: vehicle?.model,
          prediction_id: telemetry?.prediction_id,
          priority: telemetry?.priority || "medium"
        }
      });
      const provider = response.data?.provider === "twilio" ? "Twilio" : "offline";
      setVoiceStatus({ state: "success", message: `Call initiated (${provider} mode).` });
    }catch(error){
      console.error("Voice call failed", error);
      setVoiceStatus({ state: "error", message: "Voice agent currently unavailable." });
    }
  };

  return (
    <div className="min-h-screen text-white">
      <Navbar />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-8">
          <div className="relative min-h-[640px]">
            {loading && <PageLoader label="Stitching live telemetry" />}
            <div className="max-w-7xl mx-auto space-y-8">
            <section className="flex flex-wrap justify-between gap-6">
              <div>
                <h1 className="text-3xl font-semibold tracking-tight accent-underline">Command Center</h1>
                <p className="text-sm text-white/60 mt-2 uppercase tracking-[0.35em]">Real-time Vehicle Intelligence | Service Demand Forecast</p>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="metric-tile">
                  <span className="metric-label">Telemetry</span>
                  <span className="metric-value text-white/85">{status === "online" ? "Live" : "Offline"}</span>
                </div>
                <div className="metric-tile">
                  <span className="metric-label">Predictions</span>
                  <span className="metric-value text-white/85">{vehicle ? "Active" : "--"}</span>
                </div>
                <div className="metric-tile">
                  <span className="metric-label">Engagement</span>
                  <span className="metric-value text-white/85">+87%</span>
                </div>
                <div className="metric-tile">
                  <span className="metric-label">Load Index</span>
                  <span className="metric-value text-white/85">62%</span>
                </div>
              </div>
            </section>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="col-span-2 space-y-6">
                <Suspense fallback={<div className="card p-6 animate-pulse bg-white/5 min-h-[220px]" />}>
                  <VehicleCard vehicle={vehicle} customer={customer} />
                </Suspense>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <Suspense fallback={<div className="h-56 rounded-3xl border border-white/10 bg-white/5 animate-pulse" />}>
                    <Car3D />
                  </Suspense>
                  <Suspense fallback={<div className="card p-6 animate-pulse bg-white/5 min-h-[180px]" />}>
                    <HealthGraph data={null} />
                  </Suspense>
                  <Suspense fallback={<div className="card p-6 animate-pulse bg-white/5 min-h-[180px]" />}>
                    <DonutChart value={76} />
                  </Suspense>
                </div>
                <div className="card p-6">
                  <div className="flex justify-between items-center mb-4">
                    <h4 className="section-heading">Realtime Sensor Snapshot</h4>
                    <span className="badge-status" style={{color: status === "online" ? "#34d399" : "#f87171", background: status === "online" ? "#34d3991a" : "#f871711a"}}>
                      <span className="h-2 w-2 rounded-full" style={{background: status === "online" ? "#34d399" : "#f87171"}} />
                      {status.toUpperCase()}
                    </span>
                  </div>
                  {status === "online" && telemetry ? (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="metric-tile">
                        <span className="metric-label">Speed</span>
                        <span className="metric-value text-white/85">{telemetry.speed ?? "--"} km/h</span>
                      </div>
                      <div className="metric-tile">
                        <span className="metric-label">Engine Temp</span>
                        <span className="metric-value text-white/85">{telemetry.engine_temp ?? "--"} °C</span>
                      </div>
                      <div className="metric-tile">
                        <span className="metric-label">Battery</span>
                        <span className="metric-value text-white/85">{telemetry.battery_voltage ?? "--"} V</span>
                      </div>
                    </div>
                  ) : (
                    <div className="p-4 text-sm text-white/60 bg-white/5 rounded-lg border border-white/10">
                      Disconnected / Offline — no live telemetry
                    </div>
                  )}
                </div>
              </div>

              <aside className="space-y-6">
                <div className="card p-6">
                  <h4 className="section-heading mb-4">Quick Actions</h4>
                  <div className="flex flex-col gap-3">
                    <Link to="/service" className="btn-primary justify-between">
                      <span>Book Service</span>
                      <span className="text-xs uppercase tracking-[0.35em]">AI Assisted</span>
                    </Link>
                    <Link to="/profile" className="btn-ghost justify-between">
                      <span>Owner Profile</span>
                      <span className="text-xs uppercase tracking-[0.35em] text-white/50">Telemetry</span>
                    </Link>
                    <button type="button" onClick={handleVoiceCall} className="btn-ghost justify-between">
                      <span>Voice Concierge</span>
                      <span className="text-xs uppercase tracking-[0.35em] text-white/50">
                        {voiceStatus.state === "pending" ? "Dialing" : "Call Owner"}
                      </span>
                    </button>
                  </div>
                  {voiceStatus.message && (
                    <div className={`mt-3 text-xs ${voiceStatus.state === "error" ? "text-red-300" : "text-white/60"}`}>
                      {voiceStatus.message}
                    </div>
                  )}
                </div>
                <div className="card p-6">
                  <h4 className="section-heading mb-4">Model Insights</h4>
                  <div className="space-y-4 text-sm text-white/70">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-semibold text-white/90">Brake Pad Wear</p>
                        <p className="text-xs uppercase tracking-[0.4em] text-white/40">12% recurring</p>
                      </div>
                      <span className="badge-accent">Priority</span>
                    </div>
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-semibold text-white/90">Battery Cycling</p>
                        <p className="text-xs uppercase tracking-[0.4em] text-white/40">8% recurring</p>
                      </div>
                      <span className="pill">CAPA Active</span>
                    </div>
                    <p className="text-xs text-white/50">
                      RCA feeds recommendations back to manufacturing for continuous quality improvements.
                    </p>
                  </div>
                </div>
                <Suspense fallback={<div className="card p-6 animate-pulse bg-white/5 min-h-[220px]" />}>
                  <NotificationPanel />
                </Suspense>
              </aside>
            </div>
            </div>
          </div>
        </main>
      </div>
      <Suspense fallback={<div className="fixed bottom-4 right-4 h-16 w-16 rounded-full bg-white/10 animate-pulse" />}>
        <ChatWidget customer={customer} />
      </Suspense>
      <Suspense fallback={<div className="h-16" />}>
        <FooterNav />
      </Suspense>
    </div>
  );
}

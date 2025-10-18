import { useEffect, useMemo, useState } from "react";
import Navbar from "../components/Navbar.jsx";
import Sidebar from "../components/Sidebar.jsx";
import { motion } from "framer-motion";
import api from "../lib/api.js";
import PageLoader from "../components/PageLoader.jsx";

export default function Profile() {
  // 1-5. useState Hooks
  const [user, setUser] = useState(null);
  const [vehicle, setVehicle] = useState(null);
  const [serviceHistory, setServiceHistory] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true); // 6. useEffect Hook

  useEffect(() => {
    const load = async () => {
      try {
        const userRes = await api.get("/api/user");
        const users = Array.isArray(userRes.data)
          ? userRes.data
          : userRes.data?.customers || [];
        const currentUser = users[0] || {
          id: "CUST001",
          name: "Aman Jain",
          phone: "+91-98765-43210",
          email: "aman.jain@example.com",
          vehicle_id: "VEH001",
        };
        setUser(currentUser);
        const vehRes = await api.get(`/vehicle/${currentUser.vehicle_id}`);
        if (vehRes.data?.vehicle) {
          setVehicle(vehRes.data.vehicle);
          setPredictions(vehRes.data.predictions || []);
          setServiceHistory(vehRes.data.service_history || []);
        }
      } catch (e) {
        console.error("Failed to load profile:", e);
        const fallbackUser = {
          id: "CUST001",
          name: "Aman Jain",
          phone: "+91-98765-43210",
          email: "aman.jain@example.com",
          vehicle_id: "VEH001",
        };
        setUser(fallbackUser);
        setVehicle({
          id: "VEH001",
          model: "Mahindra Scorpio N",
          model_number: "SCN-2024",
          vin: "MA1TD2JPXM4C12345",
          registration_number: "KA 01 MJ 4721",
          purchase_date: "12 Jan 2023",
          warranty_expiry: "12 Jan 2026",
          mileage: 18420,
          health_status: "good",
          health_score: 92,
        });
        setPredictions([
          {
            predicted_issue: "Brake pad wear trending high",
            failure_probability: 68,
            confidence_score: 81,
            parts_at_risk: "Front axle brake assembly",
            recommended_action: "Schedule brake inspection within 200 km",
            priority: "high",
          },
          {
            predicted_issue: "Tyre pressure variance detected",
            failure_probability: 34,
            confidence_score: 72,
            parts_at_risk: "Rear right tyre",
            recommended_action: "Equalize tyre pressure at next fuel stop",
            priority: "medium",
          },
        ]);
        setServiceHistory([
          {
            service_type: "60-Point Preventive Inspection",
            service_date: "04 Oct 2024",
            status: "Completed",
            technician: "Arjun Patel",
            parts_replaced: "Cabin filter",
            cost: "1899",
            customer_rating: 5,
          },
          {
            service_type: "Connected Diagnostics",
            service_date: "22 Aug 2024",
            status: "Completed",
            technician: "Latika Rao",
            parts_replaced: "Diagnostic scan",
            cost: "1299",
            customer_rating: 4,
          },
          {
            service_type: "Brake Pad Replacement",
            service_date: "28 Oct 2025",
            status: "Scheduled",
            technician: "Pending assignment",
            parts_replaced: "--",
            cost: null,
            customer_rating: null,
          },
        ]);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const logout = () => {
    localStorage.removeItem("token");
    window.location.href = "/login";
  };

  // --- START OF MOVED LOGIC / HOOKS ---

  // Standard calculation that must be done before the useMemo that relies on it.
  const reliabilityScore =
    vehicle?.health_score ??
    (vehicle?.health_status === "excellent"
      ? 97
      : vehicle?.health_status === "good"
      ? 92
      : 78);

  // 7. useMemo Hook
  const completedServices = useMemo(
    () =>
      serviceHistory.filter((item) =>
        item.status?.toLowerCase?.().includes("complete")
      ).length,
    [serviceHistory]
  );

  // 8. useMemo Hook
  const scheduledVisit = useMemo(
    () =>
      serviceHistory.find((item) => {
        const status = item.status?.toLowerCase?.() || "";
        return (
          status.includes("scheduled") ||
          status.includes("upcoming") ||
          status.includes("pending")
        );
      }),
    [serviceHistory]
  );

  // 9. useMemo Hook
  const highPriorityAlerts = useMemo(
    () =>
      predictions.filter((item) => ["critical", "high"].includes(item.priority))
        .length,
    [predictions]
  );

  // 10. useMemo Hook
  const overviewMetrics = useMemo(
    () => [
      {
        label: "Reliability score",
        value: `${reliabilityScore}%`,
        caption: "AI-estimated uptime over last 30 days",
      },
      {
        label: "Services completed",
        value: completedServices,
        caption: `${serviceHistory.length} total visits logged`,
      },
      {
        label: "High-priority alerts",
        value: highPriorityAlerts,
        caption: highPriorityAlerts
          ? "Review advisor recommendations"
          : "All clear this week",
      },
    ],
    [
      reliabilityScore,
      completedServices,
      highPriorityAlerts,
      serviceHistory.length,
    ]
  );

  const upcomingVisitSummary = scheduledVisit
    ? `${scheduledVisit.service_date} • ${scheduledVisit.service_type}`
    : "No upcoming visits scheduled";

  // --- END OF MOVED LOGIC / HOOKS ---

  // The conditional return MUST come AFTER all hooks are called.
  if (loading) {
    return (
      <div className="min-h-screen bg-[rgba(6,10,18,1)] text-white relative">
                <Navbar />
                <PageLoader label="Loading driver profile intelligence" />     {" "}
      </div>
    );
  }

  return (
    <div className="min-h-screen text-white">
            <Navbar />     {" "}
      <div className="flex">
                <Sidebar />       {" "}
        <main className="flex-1 p-8">
                   {" "}
          <div className="max-w-5xl mx-auto space-y-6">
                       {" "}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="card p-6 space-y-6"
            >
                           {" "}
              <div className="flex flex-col gap-6 md:flex-row md:items-start md:justify-between">
                               {" "}
                <div className="flex gap-4">
                                   {" "}
                  <div className="w-20 h-20 rounded-full bg-gradient-to-tr from-slate-700 to-slate-900 border border-subtle flex items-center justify-center text-3xl font-semibold">
                                        {user?.name?.charAt(0) || "A"}         
                           {" "}
                  </div>
                                   {" "}
                  <div>
                                       {" "}
                    <h2 className="text-2xl font-semibold">
                      {user?.name || "Aman Jain"}
                    </h2>
                                       {" "}
                    <p className="text-xs uppercase tracking-[0.35em] text-white/40 mt-1">
                      Fleet Experience Lead
                    </p>
                                       {" "}
                    <div className="mt-3 space-y-1 text-sm text-white/70">
                                           {" "}
                      <p>Customer ID • {user?.id || "CUST001"}</p>             
                              <p>📞 {user?.phone || "+91-98765-43210"}</p>     
                                     {" "}
                      <p>✉️ {user?.email || "aman.jain@example.com"}</p>       
                                 {" "}
                    </div>
                                     {" "}
                  </div>
                                 {" "}
                </div>
                               {" "}
                <div className="flex flex-col items-end gap-3 text-right">
                                   {" "}
                  <div className="text-xs uppercase tracking-[0.28em] text-white/40">
                    Next concierge touchpoint
                  </div>
                                   {" "}
                  <div className="text-sm text-white/70">
                    {upcomingVisitSummary}
                  </div>
                                   {" "}
                  <button onClick={logout} className="btn-ghost text-sm !px-5">
                    Sign out
                  </button>
                                 {" "}
                </div>
                             {" "}
              </div>
                           {" "}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                               {" "}
                {overviewMetrics.map((metric) => (
                  <div
                    key={metric.label}
                    className="rounded-2xl border border-white/10 bg-white/3 p-4"
                  >
                                       {" "}
                    <p className="text-xs uppercase tracking-[0.3em] text-white/40">
                      {metric.label}
                    </p>
                                       {" "}
                    <p className="mt-2 text-2xl font-semibold text-white">
                      {metric.value}
                    </p>
                                       {" "}
                    <p className="mt-2 text-xs text-white/60">
                      {metric.caption}
                    </p>
                                     {" "}
                  </div>
                ))}
                             {" "}
              </div>
                         {" "}
            </motion.div>
                       {" "}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="card p-6 space-y-4"
            >
                           {" "}
              <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                               {" "}
                <div>
                                   {" "}
                  <h3 className="text-xl font-semibold">
                    🚗 Connected Vehicle
                  </h3>
                                   {" "}
                  <p className="text-sm text-white/60">
                    Mahindra fleet asset monitored by AutoPulse digital twin.
                  </p>
                                 {" "}
                </div>
                               {" "}
                {vehicle && (
                  <div className="flex items-center gap-3">
                                       {" "}
                    <span className="pill bg-white/5 text-white/70">
                      Health •{" "}
                      {vehicle.health_status?.replace(/_/g, " ") ?? "--"}
                    </span>
                                       {" "}
                    <span className="rounded-full border border-[var(--accent)]/30 bg-[var(--accent)]/10 px-4 py-2 text-sm font-semibold text-[var(--accent)]">
                      {reliabilityScore}% uptime
                    </span>
                                     {" "}
                  </div>
                )}
                             {" "}
              </div>
                           {" "}
              {vehicle ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                   {" "}
                  <div>
                    <label className="text-xs text-white/60 uppercase">
                      Model
                    </label>
                    <div className="text-white font-medium">
                      {vehicle.model}
                    </div>
                  </div>
                                   {" "}
                  <div>
                    <label className="text-xs text-white/60 uppercase">
                      Model Number
                    </label>
                    <div className="text-white font-medium">
                      {vehicle.model_number}
                    </div>
                  </div>
                                   {" "}
                  <div>
                    <label className="text-xs text-white/60 uppercase">
                      VIN
                    </label>
                    <div className="text-white font-medium">{vehicle.vin}</div>
                  </div>
                                   {" "}
                  <div>
                    <label className="text-xs text-white/60 uppercase">
                      Registration
                    </label>
                    <div className="text-white font-medium">
                      {vehicle.registration_number}
                    </div>
                  </div>
                                   {" "}
                  <div>
                    <label className="text-xs text-white/60 uppercase">
                      Purchase Date
                    </label>
                    <div className="text-white font-medium">
                      {vehicle.purchase_date}
                    </div>
                  </div>
                                   {" "}
                  <div>
                    <label className="text-xs text-white/60 uppercase">
                      Warranty Expiry
                    </label>
                    <div className="text-white font-medium">
                      {vehicle.warranty_expiry}
                    </div>
                  </div>
                                   {" "}
                  <div>
                    <label className="text-xs text-white/60 uppercase">
                      Mileage
                    </label>
                    <div className="text-white font-medium">
                      {vehicle.mileage?.toLocaleString()} km
                    </div>
                  </div>
                                   {" "}
                  <div>
                    <label className="text-xs text-white/60 uppercase">
                      Health Status
                    </label>
                    <div
                      className={`font-medium ${
                        vehicle.health_status === "excellent"
                          ? "text-green-400"
                          : vehicle.health_status === "good"
                          ? "text-blue-400"
                          : vehicle.health_status === "needs_attention"
                          ? "text-yellow-400"
                          : "text-red-400"
                      }`}
                    >
                      {vehicle.health_status?.replace(/_/g, " ").toUpperCase()}
                    </div>
                  </div>
                                 {" "}
                </div>
              ) : (
                <div className="text-white/60 text-sm">
                  No vehicle information available.
                </div>
              )}
                         {" "}
            </motion.div>
                       {" "}
            {predictions.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="card p-6"
              >
                               {" "}
                <h3 className="text-xl font-semibold mb-4">
                  🔮 AI Predictions & Maintenance Alerts
                </h3>
                               {" "}
                <div className="space-y-3">
                                   {" "}
                  {predictions.slice(0, 5).map((pred, idx) => (
                    <div
                      key={idx}
                      className="p-4 bg-white/5 rounded-lg border-l-4"
                      style={{
                        borderColor:
                          pred.priority === "critical"
                            ? "#ef4444"
                            : pred.priority === "high"
                            ? "#f59e0b"
                            : "#3b82f6",
                      }}
                    >
                                           {" "}
                      <div className="flex justify-between items-start">
                                               {" "}
                        <div>
                                                   {" "}
                          <div className="font-medium text-white">
                            {pred.predicted_issue}
                          </div>
                                                   {" "}
                          <div className="text-sm text-white/70 mt-1">
                            Failure Probability: {pred.failure_probability}% |
                            Confidence: {pred.confidence_score}%
                          </div>
                                                   {" "}
                          <div className="text-xs text-white/60 mt-1">
                            Parts at Risk: {pred.parts_at_risk}
                          </div>
                                                   {" "}
                          <div className="text-xs text-accent mt-1">
                            💡 {pred.recommended_action}
                          </div>
                                                 {" "}
                        </div>
                                               {" "}
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-medium ${
                            pred.priority === "critical"
                              ? "bg-red-500/20 text-red-400"
                              : pred.priority === "high"
                              ? "bg-yellow-500/20 text-yellow-400"
                              : "bg-blue-500/20 text-blue-400"
                          }`}
                        >
                          {pred.priority?.toUpperCase()}
                        </span>
                                             {" "}
                      </div>
                                         {" "}
                    </div>
                  ))}
                                 {" "}
                </div>
                             {" "}
              </motion.div>
            )}
                       {" "}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="card p-6"
            >
                           {" "}
              <h3 className="text-xl font-semibold mb-4">🔧 Service History</h3>
                           {" "}
              {serviceHistory.length > 0 ? (
                <div className="space-y-3">
                                   {" "}
                  {serviceHistory.slice(0, 10).map((service, idx) => (
                    <div
                      key={idx}
                      className="p-4 bg-white/5 rounded-lg flex justify-between items-start gap-4 border border-white/10"
                    >
                                           {" "}
                      <div>
                                               {" "}
                        <div className="font-medium text-white">
                          {service.service_type}
                        </div>
                                               {" "}
                        <div className="text-sm text-white/70 mt-1">
                          {service.service_date}
                        </div>
                                               {" "}
                        {service.technician && (
                          <div className="text-xs text-white/60 mt-1">
                            Technician: {service.technician}
                          </div>
                        )}
                                               {" "}
                        {service.parts_replaced && (
                          <div className="text-xs text-white/60">
                            Parts: {service.parts_replaced}
                          </div>
                        )}
                                             {" "}
                      </div>
                                           {" "}
                      <div className="text-right">
                                               {" "}
                        <div className="flex items-center justify-end gap-3">
                                                   {" "}
                          <span
                            className={`pill ${
                              service.status
                                ?.toLowerCase?.()
                                .includes("complete")
                                ? "bg-emerald-500/20 text-emerald-300"
                                : service.status
                                    ?.toLowerCase?.()
                                    .includes("schedule")
                                ? "bg-amber-500/20 text-amber-300"
                                : "bg-white/10 text-white/70"
                            }`}
                          >
                                                        {service.status}       
                                             {" "}
                          </span>
                                                   {" "}
                          {service.cost && (
                            <div className="text-white font-medium">
                              ₹{service.cost}
                            </div>
                          )}
                                                 {" "}
                        </div>
                                               {" "}
                        {service.customer_rating && (
                          <div className="text-yellow-400 text-sm mt-1">
                            {"⭐".repeat(service.customer_rating)}
                          </div>
                        )}
                                             {" "}
                      </div>
                                         {" "}
                    </div>
                  ))}
                                 {" "}
                </div>
              ) : (
                <div className="text-white/60 text-sm">
                  No service history available.
                </div>
              )}
                         {" "}
            </motion.div>
                       {" "}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="card p-6"
            >
                           {" "}
              <h3 className="text-xl font-semibold mb-4">⚡ Quick Actions</h3> 
                         {" "}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                               {" "}
                <a
                  href="/service"
                  className="p-4 bg-gradient-to-br from-[var(--accent)]/20 to-[var(--accent)]/5 rounded-lg border border-[var(--accent)]/30 hover:border-[var(--accent)] transition text-center"
                >
                  <div className="font-medium">Schedule Service</div>
                  <div className="text-xs text-white/70 mt-1">
                    Book your next appointment
                  </div>
                </a>
                               {" "}
                <a
                  href="/dashboard#telemetry"
                  className="p-4 bg-white/5 rounded-lg border border-subtle hover:border-white/20 transition text-center"
                >
                  <div className="font-medium">Live Telemetry</div>
                  <div className="text-xs text-white/70 mt-1">
                    View real-time sensor data
                  </div>
                </a>
                               {" "}
                <a
                  href="/dashboard#insights"
                  className="p-4 bg-white/5 rounded-lg border border-subtle hover:border-white/20 transition text-center"
                >
                  <div className="font-medium">Check New Models</div>
                  <div className="text-xs text-white/70 mt-1">
                    Explore latest vehicles
                  </div>
                </a>
                             {" "}
              </div>
                         {" "}
            </motion.div>
                     {" "}
          </div>
                 {" "}
        </main>
             {" "}
      </div>
         {" "}
    </div>
  );
}

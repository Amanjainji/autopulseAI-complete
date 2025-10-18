import React, { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import Navbar from "../components/Navbar.jsx";
import PageLoader from "../components/PageLoader.jsx";
import api from "../lib/api.js";

export default function ServiceBooking() {
  const [vehicle, setVehicle] = useState(null);
  const [customer, setCustomer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [status, setStatus] = useState({ type: "idle", message: "" });
  const [date, setDate] = useState(() => {
    try {
      return new Date(Date.now() + 24 * 60 * 60 * 1000)
        .toISOString()
        .split("T")[0];
    } catch {
      return "";
    }
  });
  const [time, setTime] = useState("10:00");

  useEffect(() => {
    const cachedVehicle = sessionStorage.getItem("autopulse.primaryVehicle");
    const cachedCustomer = sessionStorage.getItem("autopulse.primaryCustomer");
    if (cachedVehicle) {
      try {
        setVehicle(JSON.parse(cachedVehicle));
      } catch {}
    }
    if (cachedCustomer) {
      try {
        setCustomer(JSON.parse(cachedCustomer));
      } catch {}
    }

    const load = async () => {
      try {
        const [vres, ures] = await Promise.all([
          api.get("/api/vehicle"),
          api.get("/api/user"),
        ]);
        const vehicles = Array.isArray(vres.data)
          ? vres.data
          : vres.data?.vehicles || [];
        const users = Array.isArray(ures.data)
          ? ures.data
          : ures.data?.customers || [];
        const activeVehicle = vehicles[0] || vehicle;
        const owner =
          users.find(
            (u) =>
              u.vehicle_id === (activeVehicle?.id || activeVehicle?.vehicle_id)
          ) ||
          users[0] ||
          customer;
        if (activeVehicle) {
          setVehicle(activeVehicle);
          sessionStorage.setItem(
            "autopulse.primaryVehicle",
            JSON.stringify(activeVehicle)
          );
        }
        if (owner) {
          setCustomer(owner);
          sessionStorage.setItem(
            "autopulse.primaryCustomer",
            JSON.stringify(owner)
          );
        }
      } catch (err) {
        console.error("Failed to load booking context", err);
        if (!vehicle) {
          const fallbackVehicle = {
            id: "V1000",
            model: "Demo Model",
            model_number: "DEMO-1",
          };
          setVehicle(fallbackVehicle);
          sessionStorage.setItem(
            "autopulse.primaryVehicle",
            JSON.stringify(fallbackVehicle)
          );
        }
        if (!customer) {
          const fallbackCustomer = {
            id: "CUST-001",
            name: "Aman Jain",
            phone: "+91-98765-43210",
          };
          setCustomer(fallbackCustomer);
          sessionStorage.setItem(
            "autopulse.primaryCustomer",
            JSON.stringify(fallbackCustomer)
          );
        }
      } finally {
        setLoading(false);
      }
    };
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const book = async () => {
    if (!vehicle || !customer) {
      setStatus({
        type: "error",
        message: "Missing vehicle or customer context.",
      });
      return;
    }
    if (!date || !time) {
      setStatus({
        type: "error",
        message: "Select a preferred date and time.",
      });
      return;
    }

    setSubmitting(true);
    setStatus({ type: "pending", message: "Confirming your slot..." });
    try {
      const slotId = `${date}T${time}`;
      const response = await api.post("/api/service/schedule", {
        vehicle_id: vehicle.id || vehicle.vehicle_id,
        slot_id: slotId,
        user_id: customer.id || customer.customer_id || "CUST-001",
      });
      const appointmentId = response.data?.appointment?.id;
      setStatus({
        type: "success",
        message: appointmentId
          ? `Appointment confirmed (Ref: ${appointmentId}).`
          : "Appointment confirmed.",
      });
    } catch (err) {
      console.error("Failed to schedule service", err);
      setStatus({
        type: "error",
        message: "Unable to schedule service right now. Please try again.",
      });
    } finally {
      setSubmitting(false);
    }
  };

  const slotOptions = useMemo(
    () => [
      { label: "Factory recommended", value: "09:00" },
      { label: "Avoid peak", value: "11:30" },
      { label: "End-of-day", value: "16:00" },
    ],
    []
  );

  const conciergeHighlights = useMemo(
    () => [
      {
        icon: "🛡️",
        title: "Predictive maintenance",
        description:
          "Digital twin flagged brake wear from last 600 km. We’ll run a 35-point safety sweep.",
      },
      {
        icon: "🔋",
        title: "Energy efficiency reset",
        description:
          "Battery conditioning and software calibration to recover up to 8% range.",
      },
      {
        icon: "🤝",
        title: "Concierge assurance",
        description:
          "Dedicated advisor will confirm pickup logistics 2 hours before the slot.",
      },
    ],
    []
  );

  const timeline = useMemo(
    () => [
      {
        step: "Submit request",
        detail: "Select your preferred slot and confirm.",
        status: "done",
      },
      {
        step: "Advisor review",
        detail: "AI routes the case to the best-fit workshop.",
        status: submitting ? "current" : "pending",
      },
      {
        step: "Technician dispatch",
        detail: "Crew prepares parts and tools before arrival.",
        status: "pending",
      },
    ],
    [submitting]
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-[rgba(6,10,18,1)] text-white relative">
        <Navbar />
        <PageLoader label="Preparing concierge scheduling" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[rgba(6,10,18,1)] text-white">
      <Navbar />
      <main className="max-w-5xl mx-auto px-6 py-10 space-y-8">
        <motion.section
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="card p-6 md:p-8 relative overflow-hidden"
        >
          <div
            className="absolute inset-0 pointer-events-none"
            style={{
              background:
                "radial-gradient(circle at top right, rgba(45,212,191,0.18), transparent 45%)",
            }}
          />
          <div className="relative flex flex-col gap-6 md:flex-row md:items-start md:justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.35em] text-white/40">
                Concierge Scheduling
              </p>
              <h1 className="mt-2 text-3xl font-semibold tracking-tight">
                Reserve your predictive maintenance slot
              </h1>
              <p className="mt-3 text-sm text-white/70 max-w-xl">
                AutoPulse cross-checks workshop load, technician skills, and
                availability to secure the fastest service window for your fleet
                asset.
              </p>
            </div>
            {vehicle && (
              <div className="rounded-2xl border border-white/10 bg-white/5 px-5 py-4 text-sm text-white/70 min-w-[220px]">
                <div className="text-xs uppercase tracking-[0.28em] text-white/40">
                  Vehicle Context
                </div>
                <div className="mt-2 text-lg font-semibold text-white">
                  {vehicle.model}
                </div>
                <div>{vehicle.model_number}</div>
                <div className="text-white/40 mt-2">
                  Asset #{vehicle.id || vehicle.vehicle_id}
                </div>
              </div>
            )}
          </div>
        </motion.section>

        <div className="relative min-h-[420px]">
          {submitting && <PageLoader label="Locking your service bay" />}
          <div className="grid gap-6 lg:grid-cols-[1.7fr,1fr]">
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 }}
              className="card p-6 space-y-6"
            >
              {customer && (
                <div className="flex flex-col gap-1 text-sm text-white/70">
                  <div className="text-xs uppercase tracking-[0.3em] text-white/40">
                    Request on behalf of
                  </div>
                  <div className="text-lg font-semibold text-white">
                    {customer.name}
                  </div>
                  <div className="flex flex-wrap gap-4 text-xs">
                    {customer.phone && (
                      <span className="pill bg-white/5 text-white/60">
                        📞 {customer.phone}
                      </span>
                    )}
                    {customer.email && (
                      <span className="pill bg-white/5 text-white/60">
                        ✉️ {customer.email}
                      </span>
                    )}
                    <span className="pill bg-[var(--accent)]/15 text-[var(--accent)]">
                      Access code verified
                    </span>
                  </div>
                </div>
              )}

              <div className="space-y-4">
                <div>
                  <label className="text-xs uppercase tracking-[0.3em] text-white/40">
                    Preferred date
                  </label>
                  <input
                    type="date"
                    min={date}
                    value={date}
                    onChange={(e) => setDate(e.target.value)}
                    className="input mt-2"
                  />
                </div>

                <div className="space-y-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <label className="text-xs uppercase tracking-[0.3em] text-white/40">
                      Recommended slots
                    </label>
                    <span className="text-xs text-white/50">All times IST</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {slotOptions.map((option) => (
                      <button
                        key={option.value}
                        type="button"
                        onClick={() => setTime(option.value)}
                        className={`px-4 py-2 rounded-full border transition ${
                          time === option.value
                            ? "border-[var(--accent)] bg-[var(--accent)]/15 text-white"
                            : "border-white/10 bg-white/5 text-white/70 hover:text-white"
                        }`}
                      >
                        <div className="text-sm font-semibold">
                          {option.value}
                        </div>
                        <div className="text-[10px] uppercase tracking-[0.3em] text-white/40 mt-1">
                          {option.label}
                        </div>
                      </button>
                    ))}
                  </div>
                  <select
                    value={time}
                    onChange={(e) => setTime(e.target.value)}
                    className="input"
                  >
                    <option value="08:30">08:30</option>
                    <option value="09:00">09:00</option>
                    <option value="10:00">10:00</option>
                    <option value="11:30">11:30</option>
                    <option value="13:00">13:00</option>
                    <option value="14:30">14:30</option>
                    <option value="16:00">16:00</option>
                  </select>
                </div>

                <div className="space-y-3">
                  <label className="text-xs uppercase tracking-[0.3em] text-white/40">
                    Notes for advisor
                  </label>
                  <textarea
                    className="input min-h-[120px]"
                    placeholder="Example: Please arrange doorstep pickup, check brake noise above 60 km/h."
                  />
                </div>
              </div>

              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div
                  className={`text-xs ${
                    status.type === "error"
                      ? "text-red-300"
                      : status.type === "success"
                      ? "text-emerald-300"
                      : "text-white/60"
                  }`}
                >
                  {status.message ||
                    "We reserve a live technician before confirming."}
                </div>
                <button
                  onClick={book}
                  className="btn-primary whitespace-nowrap"
                  disabled={submitting}
                >
                  {submitting ? "Confirming..." : "Confirm booking"}
                </button>
              </div>
            </motion.div>

            <motion.aside
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.12 }}
              className="space-y-6"
            >
              <div className="card p-5 space-y-4">
                <h3 className="text-lg font-semibold">
                  Why this visit matters
                </h3>
                <div className="space-y-3 text-sm text-white/70">
                  {conciergeHighlights.map((item) => (
                    <div
                      key={item.title}
                      className="rounded-xl border border-white/10 bg-white/5 p-3"
                    >
                      <div className="flex items-start gap-3">
                        <span className="text-xl">{item.icon}</span>
                        <div>
                          <p className="font-semibold text-white">
                            {item.title}
                          </p>
                          <p className="text-xs text-white/60 mt-1 leading-relaxed">
                            {item.description}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="card p-5 space-y-4">
                <h3 className="text-lg font-semibold">Concierge playbook</h3>
                <div className="space-y-3 text-sm text-white/70">
                  {timeline.map((entry) => (
                    <div key={entry.step} className="flex gap-3 items-start">
                      <span
                        className={`mt-0.5 h-2.5 w-2.5 rounded-full ${
                          entry.status === "done"
                            ? "bg-emerald-300"
                            : entry.status === "current"
                            ? "bg-[var(--accent)]"
                            : "bg-white/20"
                        }`}
                      />
                      <div>
                        <p className="font-medium text-white">{entry.step}</p>
                        <p className="text-xs text-white/60 mt-1">
                          {entry.detail}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.aside>
          </div>
        </div>
      </main>
    </div>
  );
}

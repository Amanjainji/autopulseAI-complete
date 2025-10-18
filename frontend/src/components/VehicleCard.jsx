import { Link } from "react-router-dom";

const HEALTH_MAP = {
  excellent: { label: "Excellent", tone: "#22d3ee" },
  good: { label: "Stable", tone: "#34d399" },
  needs_attention: { label: "Needs Attention", tone: "#fbbf24" },
  critical: { label: "Critical", tone: "#f87171" },
};

export default function VehicleCard({ vehicle, customer }) {
  const healthKey = (vehicle?.health_status || "good").toLowerCase();
  const health = HEALTH_MAP[healthKey] || HEALTH_MAP.good;

  return (
    <div className="card card-hero p-6 overflow-hidden">
           {" "}
      <div className="absolute -right-24 -top-20 h-56 w-56 rounded-full border border-[var(--accent)]/20 bg-[var(--accent-soft)] blur-3xl opacity-40" />
           {" "}
      <div className="flex items-start gap-6 relative">
               {" "}
        <div
          className="w-64 h-40 flex-shrink-0 rounded-2xl surface-grid border border-white/10"
          style={{
            // Set the image URL
            backgroundImage:
              "url('https://imgs.search.brave.com/q1-X6IuFcTG8CVX7_D7gmxLj8N_7gHWoNYWL7EuoBY8/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9tZWRp/YS56aWdjZG4uY29t/L21lZGlhL2NvbnRl/bnQvMjAyMi9NYXkv/MTY2NzIwMjI4MS1h/bGwtbmV3X3Njb3Jw/aW8tbl9waWNfMDIu/anBnP3RyPXctOTMw')",
            // Ensure it covers the area
            backgroundSize: "cover",
            // Center it
            backgroundPosition: "center",
            // Stop it from repeating (for a cleaner look)
            backgroundRepeat: "no-repeat",
          }}
        >
          <div className="absolute bottom-3 left-4 text-xs uppercase tracking-[0.4em] text-white/40">
            Fleet
          </div>
          <div className="absolute top-3 right-4 text-sm font-semibold text-white/70">
            {vehicle?.registration_number || "AUTO-001"}
          </div>
        </div>
        <div className="flex-1 space-y-4">
          <div className="flex flex-wrap items-center gap-4">
            <div>
              <h3 className="text-2xl font-semibold tracking-tight text-white">
                {vehicle?.model || vehicle?.model_name || "Model Name"}
              </h3>
              <p className="text-sm text-white/60 uppercase tracking-[0.35em]">
                {vehicle?.model_number || "PX-000"}
              </p>
            </div>
            <span
              className="badge-status"
              style={{ color: health.tone, background: `${health.tone}1a` }}
            >
              <span
                className="h-2 w-2 rounded-full"
                style={{ background: health.tone }}
              />
              {health.label}
            </span>
            <div className="pill">VIN {vehicle?.vin || "VIN000"}</div>
          </div>

          {customer && (
            <div className="flex flex-wrap items-center gap-2 text-sm text-white/70">
              <span className="pill">Owner</span>
              <span className="font-medium text-white/85">{customer.name}</span>
              {customer.phone && (
                <span className="text-white/50">• {customer.phone}</span>
              )}
              {customer.email && (
                <span className="text-white/40">• {customer.email}</span>
              )}
            </div>
          )}

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="metric-tile">
              <span className="metric-label">Mileage</span>
              <span className="metric-value">
                {vehicle?.mileage
                  ? `${vehicle.mileage.toLocaleString()} km`
                  : "—"}
              </span>
            </div>
            <div className="metric-tile">
              <span className="metric-label">Last Service</span>
              <span className="metric-value text-white/80">
                {vehicle?.last_service_date || "N/A"}
              </span>
            </div>
            <div className="metric-tile">
              <span className="metric-label">Next Due</span>
              <span className="metric-value text-white/80">
                {vehicle?.next_service_due || "Not set"}
              </span>
            </div>
            <div className="metric-tile">
              <span className="metric-label">Warranty</span>
              <span className="metric-value text-white/80">
                {vehicle?.warranty_expiry || "N/A"}
              </span>
            </div>
          </div>

          <div className="flex flex-wrap gap-3">
            <Link to="/service" className="btn-primary">
              <span>Schedule Service</span>
            </Link>
            <Link to="/profile#history" className="btn-ghost">
              <span>Maintenance History</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

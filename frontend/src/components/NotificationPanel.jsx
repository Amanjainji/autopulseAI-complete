export default function NotificationPanel({ notifications = [] }){
  const notifs = notifications.length ? notifications : [
    { id: 1, level: "critical", title: "High engine temp", message: "Engine temp 105°C detected", time: "2m ago" },
    { id: 2, level: "info", title: "Service due", message: "Scheduled service due in 5 days", time: "1d ago" }
  ];
  return (
    <div className="card p-4">
      <h4 className="text-sm text-white/80 mb-3">Notifications</h4>
      <div className="flex flex-col gap-3">
        {notifs.map(n => (
          <div key={n.id} className="p-3 rounded bg-white/5">
            <div className="flex justify-between items-start">
              <div>
                <div className="text-sm font-semibold text-white">{n.title}</div>
                <div className="text-xs text-white/70">{n.message}</div>
              </div>
              <div className="text-xs text-white/50">{n.time}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

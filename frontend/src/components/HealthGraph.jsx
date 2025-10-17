import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function HealthGraph({ data }){
  const d = data || [
    { name: "Jan", value: 80 },
    { name: "Feb", value: 78 },
    { name: "Mar", value: 82 },
    { name: "Apr", value: 75 },
    { name: "May", value: 85 },
  ];
  return (
    <div className="card p-4">
      <h4 className="text-sm text-white/80 mb-2">Maintenance Trend</h4>
      <div style={{ width: "100%", height: 180 }}>
        <ResponsiveContainer>
          <LineChart data={d}>
            <XAxis dataKey="name" stroke="#8b96a3" />
            <YAxis stroke="#8b96a3" />
            <Tooltip />
            <Line type="monotone" dataKey="value" stroke="var(--accent)" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

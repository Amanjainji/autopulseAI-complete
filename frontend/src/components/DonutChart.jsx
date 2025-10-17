import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";

export default function DonutChart({ value = 72, color = "#00b4ff" }){
  const data = [
    { name: "Health", value },
    { name: "Remaining", value: Math.max(0, 100 - value) },
  ];
  const COLORS = [color, "#1f2630"];
  return (
    <div className="card p-4">
      <h4 className="text-sm text-white/80 mb-2">Overall Health</h4>
      <div style={{ width: "100%", height: 180 }}>
        <ResponsiveContainer>
          <PieChart>
            <Pie data={data} innerRadius={55} outerRadius={80} dataKey="value" startAngle={90} endAngle={-270}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} strokeWidth={0} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { SEVERITY_LABELS } from "../../lib/formatters";
import type { AIAnalysisResult, DiseaseSeverity } from "../../api/types";

const BAR_COLOR: Record<DiseaseSeverity, string> = {
  NonDemented: "#2F7D5B",
  VeryMildDemented: "#C68A1E",
  MildDemented: "#C2650A",
  ModerateDemented: "#B0301F",
};

export function ClassProbabilityChart({ result }: { result: AIAnalysisResult }) {
  const data = (Object.entries(result.class_probabilities) as [DiseaseSeverity, number][]).map(
    ([key, value]) => ({
      key,
      label: SEVERITY_LABELS[key],
      value: Math.round(value * 1000) / 10,
    })
  );

  return (
    <div className="h-56 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ left: 8, right: 24 }}>
          <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#DCE6E8" />
          <XAxis type="number" domain={[0, 100]} tickFormatter={(v) => `${v}%`} tick={{ fontSize: 12 }} />
          <YAxis type="category" dataKey="label" width={90} tick={{ fontSize: 12 }} />
          <Tooltip formatter={(value) => [`${value}%`, "Probability"]} />
          <Bar dataKey="value" radius={[0, 4, 4, 0]}>
            {data.map((entry) => (
              <Cell key={entry.key} fill={BAR_COLOR[entry.key]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

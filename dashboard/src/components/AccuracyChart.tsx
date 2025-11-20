import React from "react";
import { RunRecord } from "../types";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

interface Props {
  records: RunRecord[];
}

export const AccuracyChart: React.FC<Props> = ({ records }) => {
  // モデルごとに色を分ける
  const llms = Array.from(new Set(records.map((r) => r.llm_name)));
  const colors = ["#8884d8", "#82ca9d", "#ffc658", "#ff7300", "#0088FE"];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={records} margin={{ top: 10, right: 30, left: 0, bottom: 30 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey="created_at"
          tickFormatter={(value) => new Date(value).toLocaleDateString()}
        />
        <YAxis />
        <Tooltip
          labelFormatter={(label) => new Date(label).toLocaleString()}
        />
        <Legend />
        {llms.map((llm, idx) => (
          <Line
            key={llm}
            type="monotone"
            dataKey={(row: RunRecord) =>
              row.llm_name === llm ? row.accuracy_test : undefined
            }
            name={`${llm} (test)`}
            stroke={colors[idx % colors.length]}
            connectNulls
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
};

export default AccuracyChart;
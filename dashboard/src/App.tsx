import React, { useEffect, useState } from "react";
import { fetchRecords } from "./utils/fetchCsv";
import { RunRecord } from "./types";
import { AccuracyChart } from "./components/AccuracyChart";
import { RecordTable } from "./components/RecordTable";
import { RecordDetail } from "./components/RecordDetail";

export const App: React.FC = () => {
  const [records, setRecords] = useState<RunRecord[]>([]);
  const [selected, setSelected] = useState<RunRecord | null>(null);

  useEffect(() => {
    fetchRecords().then(setRecords).catch(console.error);
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h1>ML Run Records Dashboard</h1>
      <AccuracyChart records={records} />
      <RecordTable records={records} onSelect={setSelected} />
      <RecordDetail record={selected} onClose={() => setSelected(null)} />
    </div>
  );
};

export default App;
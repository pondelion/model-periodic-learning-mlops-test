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

  useEffect(() => {
    if (records.length > 0 && !selected) {
      console.log("setSelectedRecord(records[0])");
      setSelected(records[0]);
    }
// eslint-disable-next-line react-hooks/exhaustive-deps
  }, [records]);

  return (
    <div style={{ padding: 20 }}>
      <h1>ML Run Records Dashboard</h1>
      <AccuracyChart records={records} />
      <div>click table record to view details</div>
      <RecordTable records={records} onSelect={setSelected} />
      <RecordDetail record={selected} onClose={() => setSelected(null)} />
    </div>
  );
};

export default App;
import React, { useEffect, useState } from 'react';
import { RunRecord } from '../types';
import AccuracyChart from './AccuracyChart';
import RecordTable from './RecordTable';
import Papa from 'papaparse';

const CSV_URL =
  "https://storage.googleapis.com/model-periodic-learn-test/db/model_eval_results.csv?t=" +
  Date.now();

const Dashboard: React.FC = () => {
  const [records, setRecords] = useState<RunRecord[]>([]);
  const [selectedRecord, setSelectedRecord] = useState<RunRecord | null>(null);

  useEffect(() => {
    fetch(CSV_URL)
      .then(res => res.text())
      .then(csvText => {
        const parsed = Papa.parse(csvText, { header: true, skipEmptyLines: true });
        const data: RunRecord[] = parsed.data.map((r: any) => ({
          id: Number(r.id),
          llm_name: r.llm_name,
          dataset_summary_code: r.dataset_summary_code,
          dataset_summary: r.dataset_summary,
          train_code: r.train_code,
          model_name: r.model_name,
          model_path: r.model_path,
          accuracy_val: Number(r.accuracy_val),
          accuracy_test: Number(r.accuracy_test),
          created_at: r.created_at, // Date変換はChart/Table内で行う
        }));
        setRecords(data);
      });
  }, []);

  return (
    <div className="dashboard-container">
      <h1>Run Records Dashboard</h1>
      <AccuracyChart records={records} />
      <RecordTable
        records={records}
        onSelect={(record) => setSelectedRecord(record)}
        />
    </div>
  );
};

export default Dashboard;
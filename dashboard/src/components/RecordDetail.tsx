import React from "react";
import { RunRecord } from "../types";

interface Props {
  record: RunRecord | null;
  onClose: () => void;
}

export const RecordDetail: React.FC<Props> = ({ record, onClose }) => {
  if (!record) return null;

  return (
    <div style={{ border: "1px solid #ccc", padding: 10, marginTop: 10 }}>
      <button onClick={onClose}>Close</button>
      <h3>Record Detail: {record.id}</h3>
      <p><strong>Model:</strong> {record.model_name}</p>
      <p><strong>LLM:</strong> {record.llm_name}</p>
      <p><strong>Dataset Code:</strong> {record.dataset_summary_code}</p>
      <p><strong>Dataset Summary:</strong> {record.dataset_summary}</p>
      <p><strong>Train Code:</strong></p>
      <pre style={{ whiteSpace: "pre-wrap" }}>{record.train_code}</pre>
      <p><strong>Accuracy Val:</strong> {record.accuracy_val}</p>
      <p><strong>Accuracy Test:</strong> {record.accuracy_test}</p>
      <p><strong>Created At:</strong> {new Date(record.created_at).toLocaleString()}</p>
    </div>
  );
};

export default RecordDetail;
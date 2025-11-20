import React from "react";
import ReactMarkdown from "react-markdown";
import { RunRecord } from "../types";

interface Props {
  record: RunRecord | null;
  onClose: () => void;
}

export const RecordDetail: React.FC<Props> = ({ record, onClose }) => {
  if (!record) return null;

  const codeStyle = {
    backgroundColor: "#f5f5f5",
    padding: "10px",
    borderRadius: "4px",
    fontFamily: "monospace",
    overflowX: "auto" as "auto", // ← 型を明示的にキャスト
  };

  return (
    <div style={{ border: "1px solid #ccc", padding: 10, marginTop: 10 }}>
      <button onClick={onClose}>Close</button>
      <h3 style={{ color: "#2c3e50" }}>Record Detail: {record.id}</h3>

      <p>
        <strong style={{ color: "#1f77b4" }}>LLM:</strong> {record.llm_name}
      </p>
      <p>
        <strong style={{ color: "#1f77b4" }}>Model:</strong>
        <div style={codeStyle}>
          <ReactMarkdown children={`\`\`\`\n${record.model_name}\n\`\`\``} />
        </div>
      </p>
      <p>
        <strong style={{ color: "#1f77b4" }}>Dataset Code:</strong>
        <div style={codeStyle}>
          <ReactMarkdown children={`\`\`\`python\n${record.dataset_summary_code}\n\`\`\``} />
        </div>
      </p>
      <p>
        <strong style={{ color: "#1f77b4" }}>Dataset Summary:</strong>
        <div style={codeStyle}>
          <ReactMarkdown children={`\`\`\`\n${record.dataset_summary}\n\`\`\``} />
        </div>
      </p>
      <p>
        <strong style={{ color: "#1f77b4" }}>Train Code:</strong>
      </p>
        <div style={codeStyle}>
          <ReactMarkdown children={`\`\`\`python\n${record.train_code}\n\`\`\``} />
        </div>
      <p>
        <strong style={{ color: "#1f77b4" }}>Accuracy Val:</strong> {record.accuracy_val}
      </p>
      <p>
        <strong style={{ color: "#1f77b4" }}>Accuracy Test:</strong> {record.accuracy_test}
      </p>
      <p>
        <strong style={{ color: "#1f77b4" }}>Created At:</strong> {new Date(record.created_at).toLocaleString()}
      </p>
    </div>
  );
};

export default RecordDetail;
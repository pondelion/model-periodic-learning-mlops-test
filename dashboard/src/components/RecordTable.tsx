import React, { useState } from "react";
import { RunRecord } from "../types";

interface Props {
  records: RunRecord[];
  onSelect: (record: RunRecord) => void;
}

type SortKey = keyof RunRecord;

export const RecordTable: React.FC<Props> = ({ records, onSelect }) => {
  const [sortKey, setSortKey] = useState<SortKey>("id");
  const [sortAsc, setSortAsc] = useState(true);

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortAsc(!sortAsc);
    } else {
      setSortKey(key);
      setSortAsc(true);
    }
  };

  const sortedRecords = [...records].sort((a, b) => {
    const valA = a[sortKey];
    const valB = b[sortKey];

    if (valA == null) return 1;
    if (valB == null) return -1;

    // 日付文字列の場合は Date に変換して比較
    if (sortKey === "created_at") {
      const dateA = new Date(valA as string).getTime();
      const dateB = new Date(valB as string).getTime();
      return sortAsc ? dateA - dateB : dateB - dateA;
    }

    if (typeof valA === "string" && typeof valB === "string") {
      return sortAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
    }

    // 数値として比較
    return sortAsc ? (valA as number) - (valB as number) : (valB as number) - (valA as number);
  });

  return (
    <div style={{ maxHeight: 400, overflowY: "auto" }}>
      <table>
        <thead>
          <tr>
            <th onClick={() => handleSort("id")}>ID</th>
            <th onClick={() => handleSort("llm_name")}>LLM Name</th>
            <th onClick={() => handleSort("accuracy_val")}>Val Accuracy</th>
            <th onClick={() => handleSort("accuracy_test")}>Test Accuracy</th>
            <th onClick={() => handleSort("created_at")}>Created At</th>
          </tr>
        </thead>
        <tbody>
          {sortedRecords.map((r) => (
            <tr
              key={r.id}
              onClick={() => onSelect(r)}
              style={{ cursor: "pointer" }}
            >
              <td>{r.id}</td>
              <td>{r.llm_name}</td>
              <td>{r.accuracy_val}</td>
              <td>{r.accuracy_test}</td>
              <td>{new Date(r.created_at).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default RecordTable;
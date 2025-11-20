import { CSV_URL } from "../constants";
import { RunRecord } from "../types";
import Papa from "papaparse";

export async function fetchRecords(): Promise<RunRecord[]> {
  return new Promise((resolve, reject) => {
    Papa.parse<RunRecord>(CSV_URL, {
      download: true,
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        const data = results.data.map((row) => ({
          ...row,
          accuracy_val: parseFloat(row.accuracy_val as unknown as string),
          accuracy_test: parseFloat(row.accuracy_test as unknown as string),
          created_at: new Date(row.created_at).toISOString(),
        }));
        resolve(data);
      },
      error: (err) => reject(err),
    });
  });
}
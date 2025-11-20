export interface RunRecord {
  id: number;
  llm_name: string;
  dataset_summary_code: string;
  dataset_summary: string;
  train_code: string;
  model_name: string;
  model_path: string;
  accuracy_val: number;
  accuracy_test: number;
  created_at: string; // CSV読み込み時は string
}
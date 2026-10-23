import type { AnalyzeRequest, AnalyzeResponse } from "./types";
import { apiFetch } from "../../utils/apiClient";

export async function analyzeDiagnosticCase(
  payload: AnalyzeRequest
): Promise<AnalyzeResponse> {
  const response = await apiFetch("/analyze", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Analyze request failed with status ${response.status}`);
  }

  return (await response.json()) as AnalyzeResponse;
}

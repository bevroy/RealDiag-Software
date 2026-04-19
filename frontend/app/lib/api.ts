import type { AnalyzeRequest, AnalyzeResponse } from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "https://realdiag-software.onrender.com";

export async function analyzeDiagnosticCase(
  payload: AnalyzeRequest
): Promise<AnalyzeResponse> {
  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Analyze request failed with status ${response.status}`);
  }

  return (await response.json()) as AnalyzeResponse;
}

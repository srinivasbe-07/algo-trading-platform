import type { BacktestDetail, BacktestParams } from "../types";

// The backend base URL. Override at build time with VITE_API_BASE if needed.
const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

export async function runBacktest(params: BacktestParams): Promise<BacktestDetail> {
  const url = new URL(`${API_BASE}/backtest/detail`);
  url.searchParams.set("fast", String(params.fast));
  url.searchParams.set("slow", String(params.slow));
  url.searchParams.set("quantity", String(params.quantity));

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Backtest request failed: ${response.status} ${response.statusText}`);
  }
  return (await response.json()) as BacktestDetail;
}

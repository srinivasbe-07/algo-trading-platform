import type { BacktestDetail, BacktestParams } from "../types";
import { serviceUrls } from "./config";

const API_BASE = serviceUrls.backtest;

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

import type { EquityPoint } from "../types";
import { serviceUrls } from "./config";
import { postJson } from "./http";

export interface RunParams {
  fast: number;
  slow: number;
  quantity: number;
}

export interface PaperResult {
  starting_equity: number;
  final_equity: number;
  realized_pnl: number;
  orders_submitted: number;
  orders_filled: number;
  orders_rejected: number;
  return_pct: number;
  positions: Record<string, number>;
  equity_curve: EquityPoint[];
}

function withParams(base: string, p: RunParams): string {
  const url = new URL(base);
  url.searchParams.set("fast", String(p.fast));
  url.searchParams.set("slow", String(p.slow));
  url.searchParams.set("quantity", String(p.quantity));
  return url.toString();
}

export const runPaper = (p: RunParams): Promise<PaperResult> =>
  postJson<PaperResult>(withParams(`${serviceUrls.paper}/paper/run`, p));

export { withParams };

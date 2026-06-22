import { serviceUrls } from "./config";
import { getJson, postJson } from "./http";

export interface RiskState {
  equity: number;
  realized_pnl: number;
  kill_switch: boolean;
  kill_reason: string | null;
  positions: Record<string, number>;
  paused_strategies: string[];
}

export const getRiskState = (): Promise<RiskState> =>
  getJson<RiskState>(`${serviceUrls.risk}/risk/state`);

export const tripKill = (reason: string): Promise<unknown> =>
  postJson(`${serviceUrls.risk}/risk/kill`, { reason });

export const resetKill = (): Promise<unknown> => postJson(`${serviceUrls.risk}/risk/reset`);

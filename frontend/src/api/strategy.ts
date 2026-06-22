import { serviceUrls } from "./config";
import { getJson, postJson } from "./http";

export interface StrategyInput {
  name: string;
  instrument: string;
  fast: number;
  slow: number;
  quantity: number;
}

export interface Strategy extends StrategyInput {
  id: string;
  type: string;
  max_position: number;
  daily_loss: number;
}

export const createStrategy = (input: StrategyInput): Promise<Strategy> =>
  postJson<Strategy>(`${serviceUrls.strategy}/strategies`, input);

export const listStrategies = (): Promise<Strategy[]> =>
  getJson<Strategy[]>(`${serviceUrls.strategy}/strategies`);

export async function deleteStrategy(id: string): Promise<void> {
  const res = await fetch(`${serviceUrls.strategy}/strategies/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error(`Delete failed: ${res.status}`);
}

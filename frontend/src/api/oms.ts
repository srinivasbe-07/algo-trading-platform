import { serviceUrls } from "./config";
import { getJson } from "./http";

export interface ManagedOrder {
  id: string;
  order: { symbol: string; side: string; quantity: number; order_type: string };
  status: string;
  filled_quantity: number;
  avg_fill_price: number;
}

export interface PositionsResponse {
  positions: Record<string, number>;
  realized_pnl: number;
}

export const listOrders = (): Promise<ManagedOrder[]> =>
  getJson<ManagedOrder[]>(`${serviceUrls.oms}/orders`);

export const getPositions = (): Promise<PositionsResponse> =>
  getJson<PositionsResponse>(`${serviceUrls.oms}/positions`);

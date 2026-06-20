export interface Metrics {
  initial_equity: number;
  final_equity: number;
  total_return_pct: number;
  cagr_pct: number;
  sharpe: number;
  sortino: number;
  max_drawdown_pct: number;
  num_trades: number;
  win_rate_pct: number;
  profit_factor: number;
}

export interface BarPoint {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
}

export interface EquityPoint {
  time: string;
  value: number;
}

export interface TradePoint {
  time: string;
  side: "BUY" | "SELL";
  price: number;
}

export interface BacktestDetail {
  metrics: Metrics;
  bars: BarPoint[];
  equity: EquityPoint[];
  trades: TradePoint[];
}

export interface BacktestParams {
  fast: number;
  slow: number;
  quantity: number;
}

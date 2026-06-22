// Base URL per backend service. Each service runs on its own port for now;
// a single API Gateway will unify these later. Override any with a VITE_*_URL.
export const serviceUrls = {
  backtest: import.meta.env.VITE_BACKTEST_URL ?? "http://localhost:8000",
  paper: import.meta.env.VITE_PAPER_URL ?? "http://localhost:8001",
  live: import.meta.env.VITE_LIVE_URL ?? "http://localhost:8002",
  risk: import.meta.env.VITE_RISK_URL ?? "http://localhost:8003",
  oms: import.meta.env.VITE_OMS_URL ?? "http://localhost:8004",
  broker: import.meta.env.VITE_BROKER_URL ?? "http://localhost:8005",
  strategy: import.meta.env.VITE_STRATEGY_URL ?? "http://localhost:8006",
} as const;

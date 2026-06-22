/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_BACKTEST_URL?: string;
  readonly VITE_PAPER_URL?: string;
  readonly VITE_LIVE_URL?: string;
  readonly VITE_RISK_URL?: string;
  readonly VITE_OMS_URL?: string;
  readonly VITE_BROKER_URL?: string;
}

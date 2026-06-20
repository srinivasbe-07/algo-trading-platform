import { afterEach, describe, expect, it, vi } from "vitest";
import type { BacktestDetail } from "../types";
import { runBacktest } from "./backtest";

afterEach(() => vi.unstubAllGlobals());

const payload: BacktestDetail = {
  metrics: {
    initial_equity: 1_000_000,
    final_equity: 1_009_703,
    total_return_pct: 0.97,
    cagr_pct: 0.82,
    sharpe: 0.32,
    sortino: 0.29,
    max_drawdown_pct: -2.68,
    num_trades: 18,
    win_rate_pct: 44.44,
    profit_factor: 1.69,
  },
  bars: [],
  equity: [],
  trades: [],
};

describe("runBacktest", () => {
  it("returns parsed data on a successful response", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: true, json: () => Promise.resolve(payload) }),
    );
    const data = await runBacktest({ fast: 10, slow: 20, quantity: 50 });
    expect(data.metrics.num_trades).toBe(18);
  });

  it("throws when the response is not ok", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false, status: 500, statusText: "Server Error" }),
    );
    await expect(runBacktest({ fast: 10, slow: 20, quantity: 50 })).rejects.toThrow(
      /Backtest request failed/,
    );
  });
});

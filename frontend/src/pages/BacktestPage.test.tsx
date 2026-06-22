import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { BacktestDetail } from "../types";

vi.mock("../api/backtest");
vi.mock("../components/PriceChart", () => ({ PriceChart: () => null }));
vi.mock("../components/EquityChart", () => ({ EquityChart: () => null }));

import { runBacktest } from "../api/backtest";
import { BacktestPage } from "./BacktestPage";

const mockRun = vi.mocked(runBacktest);

const detail: BacktestDetail = {
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

afterEach(() => vi.clearAllMocks());

describe("BacktestPage", () => {
  it("runs a backtest and renders metrics", async () => {
    mockRun.mockResolvedValue(detail);
    render(<BacktestPage />);
    fireEvent.change(screen.getByLabelText("Fast MA"), { target: { value: "8" } });
    fireEvent.click(screen.getByText("Run backtest"));
    await waitFor(() => expect(screen.getByText("0.97%")).toBeDefined());
    expect(mockRun).toHaveBeenCalledWith({ fast: 8, slow: 20, quantity: 50 });
  });

  it("shows an error when the request fails", async () => {
    mockRun.mockRejectedValue(new Error("network down"));
    render(<BacktestPage />);
    fireEvent.click(screen.getByText("Run backtest"));
    await waitFor(() => expect(screen.getByText(/network down/)).toBeDefined());
  });
});

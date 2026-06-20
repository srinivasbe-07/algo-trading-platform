import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MetricsCards } from "./MetricsCards";
import type { Metrics } from "../types";

const sample: Metrics = {
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
};

describe("MetricsCards", () => {
  it("renders key metrics", () => {
    render(<MetricsCards metrics={sample} />);
    expect(screen.getByText("0.97%")).toBeDefined();
    expect(screen.getByText("18")).toBeDefined();
    expect(screen.getByText("Sharpe")).toBeDefined();
  });
});

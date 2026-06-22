import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("../api/risk");
vi.mock("../api/oms");
vi.mock("../api/broker");

import { getBrokerInfo } from "../api/broker";
import { getPositions, listOrders } from "../api/oms";
import { getRiskState } from "../api/risk";
import { DashboardPage } from "./DashboardPage";

afterEach(() => {
  vi.clearAllMocks();
});

describe("DashboardPage", () => {
  it("composes risk, positions, orders, and broker", async () => {
    vi.mocked(getRiskState).mockResolvedValue({
      equity: 1_013_216,
      realized_pnl: 13216,
      kill_switch: false,
      kill_reason: null,
      positions: { NIFTY: 50 },
      paused_strategies: [],
    });
    vi.mocked(getPositions).mockResolvedValue({
      positions: { NIFTY: 50, TCS: 0 },
      realized_pnl: 13216,
    });
    vi.mocked(listOrders).mockResolvedValue([
      {
        id: "1",
        order: { symbol: "NIFTY", side: "BUY", quantity: 50, order_type: "MARKET" },
        status: "FILLED",
        filled_quantity: 50,
        avg_fill_price: 20000,
      },
    ]);
    vi.mocked(getBrokerInfo).mockResolvedValue({ broker: "zerodha-kite", dry_run: true });

    render(<DashboardPage />);
    await waitFor(() => expect(screen.getByText("zerodha-kite")).toBeDefined());
    expect(screen.getByText("₹13,216")).toBeDefined(); // realized P&L
    expect(screen.getByText("FILLED")).toBeDefined(); // recent order
    expect(screen.getByText("1")).toBeDefined(); // one open position (NIFTY; TCS is 0)
  });
});

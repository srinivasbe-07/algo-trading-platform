import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("../api/oms");

import { getPositions, listOrders } from "../api/oms";
import { OrdersPage } from "./OrdersPage";

afterEach(() => {
  vi.clearAllMocks();
});

describe("OrdersPage", () => {
  it("renders orders and positions", async () => {
    vi.mocked(listOrders).mockResolvedValue([
      {
        id: "1",
        order: { symbol: "NIFTY", side: "BUY", quantity: 50, order_type: "MARKET" },
        status: "FILLED",
        filled_quantity: 50,
        avg_fill_price: 20000,
      },
    ]);
    vi.mocked(getPositions).mockResolvedValue({ positions: { NIFTY: 50 }, realized_pnl: 10 });
    render(<OrdersPage />);
    await waitFor(() => expect(screen.getByText("FILLED")).toBeDefined());
    expect(screen.getAllByText("NIFTY").length).toBeGreaterThan(0);
  });
});

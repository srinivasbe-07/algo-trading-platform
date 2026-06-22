import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("../api/live");
vi.mock("../components/EquityChart", () => ({ EquityChart: () => null }));

import { runLive } from "../api/live";
import { LivePage } from "./LivePage";

afterEach(() => {
  vi.clearAllMocks();
});

describe("LivePage", () => {
  it("runs a live dry-run and shows broker + reconciliation", async () => {
    vi.mocked(runLive).mockResolvedValue({
      broker: "zerodha-kite",
      reconciled: true,
      discrepancies: [],
      starting_equity: 1_000_000,
      final_equity: 1_016_633,
      realized_pnl: 16633,
      orders_submitted: 18,
      orders_filled: 18,
      orders_rejected: 0,
      return_pct: 1.66,
      positions: { NIFTY: 0 },
      equity_curve: [],
    });
    render(<LivePage />);
    fireEvent.click(screen.getByText("Run live (dry-run)"));
    await waitFor(() => expect(screen.getByText("zerodha-kite")).toBeDefined());
    expect(screen.getByText("reconciled ✓")).toBeDefined();
  });
});

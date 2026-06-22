import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("../api/paper");
vi.mock("../components/EquityChart", () => ({ EquityChart: () => null }));

import { runPaper } from "../api/paper";
import { PaperPage } from "./PaperPage";

afterEach(() => {
  vi.clearAllMocks();
});

describe("PaperPage", () => {
  it("runs a paper session and shows the summary", async () => {
    vi.mocked(runPaper).mockResolvedValue({
      starting_equity: 1_000_000,
      final_equity: 1_004_674,
      realized_pnl: 4674,
      orders_submitted: 18,
      orders_filled: 18,
      orders_rejected: 0,
      return_pct: 0.47,
      positions: { NIFTY: 0 },
      equity_curve: [],
    });
    render(<PaperPage />);
    fireEvent.click(screen.getByText("Run paper session"));
    await waitFor(() => expect(screen.getByText("0.47%")).toBeDefined());
  });
});

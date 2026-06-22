import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("../api/paper");
vi.mock("../api/live");

import { runLive } from "../api/live";
import { runPaper } from "../api/paper";
import type { Strategy } from "../api/strategy";
import { DeployDialog } from "./DeployDialog";

afterEach(() => {
  vi.clearAllMocks();
});

const strategy: Strategy = {
  id: "1",
  name: "Nifty MA",
  type: "ma_crossover",
  instrument: "NIFTY",
  fast: 10,
  slow: 20,
  quantity: 50,
  max_position: 200,
  daily_loss: 50000,
};

const paperResult = {
  starting_equity: 1_000_000,
  final_equity: 1_004_674,
  realized_pnl: 4674,
  orders_submitted: 18,
  orders_filled: 18,
  orders_rejected: 0,
  return_pct: 0.47,
  positions: {},
  equity_curve: [],
};

describe("DeployDialog", () => {
  it("deploys to paper by default", async () => {
    vi.mocked(runPaper).mockResolvedValue(paperResult);
    render(<DeployDialog strategy={strategy} onClose={() => {}} />);
    fireEvent.click(screen.getByText("Deploy"));
    await waitFor(() =>
      expect(runPaper).toHaveBeenCalledWith({ fast: 10, slow: 20, quantity: 50 }),
    );
  });

  it("switches to live and deploys", async () => {
    vi.mocked(runLive).mockResolvedValue({
      ...paperResult,
      broker: "zerodha-kite",
      reconciled: true,
      discrepancies: [],
    });
    render(<DeployDialog strategy={strategy} onClose={() => {}} />);
    fireEvent.click(screen.getByText("Live (dry-run)"));
    fireEvent.click(screen.getByText("Deploy"));
    await waitFor(() => expect(runLive).toHaveBeenCalled());
  });
});

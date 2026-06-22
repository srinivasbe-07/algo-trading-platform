import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("../api/risk");

import { getRiskState, resetKill, tripKill } from "../api/risk";
import { RiskPage } from "./RiskPage";

const mockState = vi.mocked(getRiskState);
const mockKill = vi.mocked(tripKill);
const mockReset = vi.mocked(resetKill);

afterEach(() => {
  vi.clearAllMocks();
});

const state = {
  equity: 1_000_000,
  realized_pnl: 13216,
  kill_switch: false,
  kill_reason: null,
  positions: { NIFTY: 50 },
  paused_strategies: [],
};

describe("RiskPage", () => {
  it("renders risk state and positions", async () => {
    mockState.mockResolvedValue(state);
    render(<RiskPage />);
    await waitFor(() => expect(screen.getByText("off")).toBeDefined());
    expect(screen.getByText("NIFTY")).toBeDefined();
  });

  it("trips the kill-switch on click", async () => {
    mockState.mockResolvedValue(state);
    mockKill.mockResolvedValue({});
    render(<RiskPage />);
    await waitFor(() => expect(screen.getByText("Trip kill-switch")).toBeDefined());
    fireEvent.click(screen.getByText("Trip kill-switch"));
    await waitFor(() => expect(mockKill).toHaveBeenCalledWith("manual"));
  });

  it("resets the kill-switch on click", async () => {
    mockState.mockResolvedValue(state);
    mockReset.mockResolvedValue({});
    render(<RiskPage />);
    await waitFor(() => expect(screen.getByText("Reset")).toBeDefined());
    fireEvent.click(screen.getByText("Reset"));
    await waitFor(() => expect(mockReset).toHaveBeenCalled());
  });
});

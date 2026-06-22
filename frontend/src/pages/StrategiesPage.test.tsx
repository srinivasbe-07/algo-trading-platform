import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("../api/strategy");
vi.mock("../components/DeployDialog", () => ({ DeployDialog: () => <div>deploy-dialog</div> }));

import { createStrategy, listStrategies } from "../api/strategy";
import { StrategiesPage } from "./StrategiesPage";

afterEach(() => {
  vi.clearAllMocks();
});

const saved = {
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

describe("StrategiesPage", () => {
  it("lists saved strategies", async () => {
    vi.mocked(listStrategies).mockResolvedValue([saved]);
    render(<StrategiesPage />);
    await waitFor(() => expect(screen.getByText("Nifty MA")).toBeDefined());
  });

  it("creates a strategy on save", async () => {
    vi.mocked(listStrategies).mockResolvedValue([]);
    vi.mocked(createStrategy).mockResolvedValue(saved);
    render(<StrategiesPage />);
    await waitFor(() => expect(screen.getByText("Save strategy")).toBeDefined());
    fireEvent.change(screen.getByLabelText("Name"), { target: { value: "Nifty MA" } });
    fireEvent.click(screen.getByText("Save strategy"));
    await waitFor(() =>
      expect(createStrategy).toHaveBeenCalledWith(
        expect.objectContaining({ name: "Nifty MA", fast: 10, slow: 20, quantity: 50 }),
      ),
    );
  });

  it("validates the name", async () => {
    vi.mocked(listStrategies).mockResolvedValue([]);
    render(<StrategiesPage />);
    await waitFor(() => expect(screen.getByText("Save strategy")).toBeDefined());
    fireEvent.click(screen.getByText("Save strategy"));
    await waitFor(() => expect(screen.getByText("Name is required.")).toBeDefined());
  });
});

import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("../api/broker");

import { getBrokerInfo, listBrokers } from "../api/broker";
import { BrokersPage } from "./BrokersPage";

afterEach(() => {
  vi.clearAllMocks();
});

describe("BrokersPage", () => {
  it("renders the active broker and the list", async () => {
    vi.mocked(getBrokerInfo).mockResolvedValue({ broker: "zerodha-kite", dry_run: true });
    vi.mocked(listBrokers).mockResolvedValue({
      available_brokers: ["zerodha-kite", "fyers", "dhan"],
    });
    render(<BrokersPage />);
    await waitFor(() => expect(screen.getByText("dry-run")).toBeDefined());
    expect(screen.getByText("fyers")).toBeDefined();
  });
});

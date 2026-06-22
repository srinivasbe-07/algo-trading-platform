import { describe, expect, it } from "vitest";
import { serviceUrls } from "./config";

describe("serviceUrls", () => {
  it("provides a base URL for every service", () => {
    for (const key of ["backtest", "paper", "live", "risk", "oms", "broker"] as const) {
      expect(serviceUrls[key]).toMatch(/^https?:\/\//);
    }
  });
});

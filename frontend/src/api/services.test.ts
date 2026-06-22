import { afterEach, describe, expect, it, vi } from "vitest";
import { getBrokerInfo, listBrokers } from "./broker";
import { getPositions, listOrders } from "./oms";
import { getRiskState, resetKill, tripKill } from "./risk";

afterEach(() => {
  vi.unstubAllGlobals();
});

function stub(payload: unknown, ok = true) {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok,
      status: ok ? 200 : 500,
      statusText: "x",
      json: () => Promise.resolve(payload),
    }),
  );
}

describe("service API clients", () => {
  it("getRiskState parses the state", async () => {
    stub({
      equity: 1,
      realized_pnl: 0,
      kill_switch: false,
      kill_reason: null,
      positions: {},
      paused_strategies: [],
    });
    expect((await getRiskState()).kill_switch).toBe(false);
  });

  it("tripKill and resetKill POST", async () => {
    stub({ status: "ok" });
    await tripKill("manual");
    await resetKill();
    expect(fetch).toHaveBeenCalledTimes(2);
  });

  it("listOrders and getPositions parse", async () => {
    stub([
      {
        id: "1",
        order: { symbol: "NIFTY", side: "BUY", quantity: 50, order_type: "MARKET" },
        status: "FILLED",
        filled_quantity: 50,
        avg_fill_price: 100,
      },
    ]);
    expect((await listOrders())[0].order.symbol).toBe("NIFTY");
    stub({ positions: { NIFTY: 50 }, realized_pnl: 10 });
    expect((await getPositions()).positions.NIFTY).toBe(50);
  });

  it("broker info and list parse", async () => {
    stub({ broker: "zerodha-kite", dry_run: true });
    expect((await getBrokerInfo()).broker).toBe("zerodha-kite");
    stub({ available_brokers: ["zerodha-kite", "fyers"] });
    expect((await listBrokers()).available_brokers).toContain("fyers");
  });

  it("throws on a non-ok response", async () => {
    stub({}, false);
    await expect(getRiskState()).rejects.toThrow(/Request failed/);
  });
});

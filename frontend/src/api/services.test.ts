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

import { runPaper } from "./paper";
import { runLive } from "./live";

describe("run endpoints", () => {
  it("runPaper posts with params and parses", async () => {
    stub({
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
    const r = await runPaper({ fast: 10, slow: 20, quantity: 50 });
    expect(r.orders_filled).toBe(18);
  });

  it("runLive parses broker + reconciliation", async () => {
    stub({
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
    const r = await runLive({ fast: 10, slow: 20, quantity: 50 });
    expect(r.broker).toBe("zerodha-kite");
    expect(r.reconciled).toBe(true);
  });
});

import { createStrategy, deleteStrategy, listStrategies } from "./strategy";

describe("strategy API", () => {
  it("create and list parse", async () => {
    stub({
      id: "abc",
      name: "MA",
      type: "ma_crossover",
      instrument: "NIFTY",
      fast: 10,
      slow: 20,
      quantity: 50,
      max_position: 200,
      daily_loss: 50000,
    });
    expect(
      (await createStrategy({ name: "MA", instrument: "NIFTY", fast: 10, slow: 20, quantity: 50 }))
        .id,
    ).toBe("abc");
    stub([
      {
        id: "abc",
        name: "MA",
        type: "ma_crossover",
        instrument: "NIFTY",
        fast: 10,
        slow: 20,
        quantity: 50,
        max_position: 200,
        daily_loss: 50000,
      },
    ]);
    expect((await listStrategies())[0].name).toBe("MA");
  });

  it("delete resolves on ok and throws on error", async () => {
    stub({ status: "deleted" });
    await deleteStrategy("abc");
    stub({}, false);
    await expect(deleteStrategy("x")).rejects.toThrow(/Delete failed/);
  });
});

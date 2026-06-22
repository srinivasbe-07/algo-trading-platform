import { useState, type ChangeEvent } from "react";
import { runBacktest } from "../api/backtest";
import { EquityChart } from "../components/EquityChart";
import { MetricsCards } from "../components/MetricsCards";
import { PriceChart } from "../components/PriceChart";
import type { BacktestDetail, BacktestParams } from "../types";

export function BacktestPage() {
  const [params, setParams] = useState<BacktestParams>({ fast: 10, slow: 20, quantity: 50 });
  const [data, setData] = useState<BacktestDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const update = (key: keyof BacktestParams) => (e: ChangeEvent<HTMLInputElement>) =>
    setParams((p) => ({ ...p, [key]: Number(e.target.value) }));

  const onRun = async () => {
    setLoading(true);
    setError(null);
    try {
      setData(await runBacktest(params));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Backtest</h1>
      <p className="sub">MA-crossover strategy on bundled Nifty sample data</p>

      <div className="panel">
        <div className="form">
          <div className="field">
            <label htmlFor="fast">Fast MA</label>
            <input id="fast" type="number" min={1} value={params.fast} onChange={update("fast")} />
          </div>
          <div className="field">
            <label htmlFor="slow">Slow MA</label>
            <input id="slow" type="number" min={2} value={params.slow} onChange={update("slow")} />
          </div>
          <div className="field">
            <label htmlFor="qty">Quantity</label>
            <input
              id="qty"
              type="number"
              min={1}
              value={params.quantity}
              onChange={update("quantity")}
            />
          </div>
          <button onClick={onRun} disabled={loading}>
            {loading ? "Running…" : "Run backtest"}
          </button>
        </div>
        {error && <p className="error">{error} — is the backtest API running?</p>}
      </div>

      {data && (
        <>
          <div className="panel">
            <MetricsCards metrics={data.metrics} />
          </div>
          <div className="panel">
            <p className="chart-title">Price &amp; trade signals</p>
            <PriceChart bars={data.bars} trades={data.trades} />
          </div>
          <div className="panel">
            <p className="chart-title">Equity curve</p>
            <EquityChart equity={data.equity} />
          </div>
        </>
      )}
    </div>
  );
}

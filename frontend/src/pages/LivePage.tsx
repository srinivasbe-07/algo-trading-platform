import { useState, type ChangeEvent } from "react";
import { runLive, type LiveResult } from "../api/live";
import type { RunParams } from "../api/paper";
import { EquityChart } from "../components/EquityChart";

const inr = (n: number) => n.toLocaleString("en-IN", { maximumFractionDigits: 0 });

export function LivePage() {
  const [params, setParams] = useState<RunParams>({ fast: 10, slow: 20, quantity: 50 });
  const [result, setResult] = useState<LiveResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const upd = (key: keyof RunParams) => (e: ChangeEvent<HTMLInputElement>) =>
    setParams((p) => ({ ...p, [key]: Number(e.target.value) }));

  const onRun = async () => {
    setLoading(true);
    setError(null);
    try {
      setResult(await runLive(params));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Live</h1>
      <p className="sub">Live (dry-run) session through the broker gateway, with reconciliation</p>

      <div className="panel">
        <div className="form">
          <div className="field">
            <label htmlFor="l-fast">Fast MA</label>
            <input id="l-fast" type="number" min={1} value={params.fast} onChange={upd("fast")} />
          </div>
          <div className="field">
            <label htmlFor="l-slow">Slow MA</label>
            <input id="l-slow" type="number" min={2} value={params.slow} onChange={upd("slow")} />
          </div>
          <div className="field">
            <label htmlFor="l-qty">Quantity</label>
            <input
              id="l-qty"
              type="number"
              min={1}
              value={params.quantity}
              onChange={upd("quantity")}
            />
          </div>
          <button onClick={onRun} disabled={loading}>
            {loading ? "Running…" : "Run live (dry-run)"}
          </button>
        </div>
        {error && <p className="error">{error} — is the live-engine API running?</p>}
      </div>

      {result && (
        <>
          <div className="panel">
            <p>
              Broker: <strong>{result.broker}</strong>{" "}
              <span className={"badge"}>
                {result.reconciled ? "reconciled ✓" : "drift — check positions"}
              </span>
            </p>
            <div className="cards">
              <div className="card">
                <div className="k">Return</div>
                <div className={"v " + (result.return_pct >= 0 ? "pos" : "neg")}>
                  {result.return_pct.toFixed(2)}%
                </div>
              </div>
              <div className="card">
                <div className="k">Final equity</div>
                <div className="v">₹{inr(result.final_equity)}</div>
              </div>
              <div className="card">
                <div className="k">Filled</div>
                <div className="v">{result.orders_filled}</div>
              </div>
              <div className="card">
                <div className="k">Rejected</div>
                <div className={"v " + (result.orders_rejected ? "neg" : "")}>
                  {result.orders_rejected}
                </div>
              </div>
            </div>
          </div>
          <div className="panel">
            <p className="chart-title">Equity curve</p>
            <EquityChart equity={result.equity_curve} />
          </div>
        </>
      )}
    </div>
  );
}

import { useState, type ChangeEvent } from "react";
import { runPaper, type PaperResult, type RunParams } from "../api/paper";
import { EquityChart } from "../components/EquityChart";

const inr = (n: number) => n.toLocaleString("en-IN", { maximumFractionDigits: 0 });

export function PaperPage() {
  const [params, setParams] = useState<RunParams>({ fast: 10, slow: 20, quantity: 50 });
  const [result, setResult] = useState<PaperResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const upd = (key: keyof RunParams) => (e: ChangeEvent<HTMLInputElement>) =>
    setParams((p) => ({ ...p, [key]: Number(e.target.value) }));

  const onRun = async () => {
    setLoading(true);
    setError(null);
    try {
      setResult(await runPaper(params));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Paper</h1>
      <p className="sub">Run a strategy in real time through Risk → OMS → simulated broker</p>

      <div className="panel">
        <div className="form">
          <div className="field">
            <label htmlFor="p-fast">Fast MA</label>
            <input id="p-fast" type="number" min={1} value={params.fast} onChange={upd("fast")} />
          </div>
          <div className="field">
            <label htmlFor="p-slow">Slow MA</label>
            <input id="p-slow" type="number" min={2} value={params.slow} onChange={upd("slow")} />
          </div>
          <div className="field">
            <label htmlFor="p-qty">Quantity</label>
            <input
              id="p-qty"
              type="number"
              min={1}
              value={params.quantity}
              onChange={upd("quantity")}
            />
          </div>
          <button onClick={onRun} disabled={loading}>
            {loading ? "Running…" : "Run paper session"}
          </button>
        </div>
        {error && <p className="error">{error} — is the paper-trade API running?</p>}
      </div>

      {result && (
        <>
          <div className="panel">
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

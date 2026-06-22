import { getRiskState, resetKill, tripKill } from "../api/risk";
import { useFetch } from "../hooks/useFetch";

const inr = (n: number) => n.toLocaleString("en-IN", { maximumFractionDigits: 0 });

export function RiskPage() {
  const { data, loading, error, reload } = useFetch(getRiskState);

  const onKill = async () => {
    await tripKill("manual");
    reload();
  };
  const onReset = async () => {
    await resetKill();
    reload();
  };

  return (
    <div>
      <h1>Risk</h1>
      <p className="sub">Live risk state and controls</p>
      {loading && <p>Loading…</p>}
      {error && <p className="error">{error} — is the risk-engine API running?</p>}
      {data && (
        <>
          <div className="panel">
            <div className="cards">
              <div className="card">
                <div className="k">Equity</div>
                <div className="v">₹{inr(data.equity)}</div>
              </div>
              <div className="card">
                <div className="k">Realized P&amp;L</div>
                <div className={"v " + (data.realized_pnl >= 0 ? "pos" : "neg")}>
                  ₹{inr(data.realized_pnl)}
                </div>
              </div>
              <div className="card">
                <div className="k">Kill-switch</div>
                <div className={"v " + (data.kill_switch ? "neg" : "pos")}>
                  {data.kill_switch ? "ON" : "off"}
                </div>
              </div>
            </div>
            <div style={{ marginTop: 14, display: "flex", gap: 8 }}>
              <button onClick={onKill}>Trip kill-switch</button>
              <button onClick={onReset}>Reset</button>
              <button onClick={reload}>Refresh</button>
            </div>
            {data.kill_reason && <p className="sub">Reason: {data.kill_reason}</p>}
          </div>

          <div className="panel">
            <p className="chart-title">Positions</p>
            {Object.keys(data.positions).length === 0 ? (
              <p className="sub">No open positions.</p>
            ) : (
              <table className="tbl">
                <thead>
                  <tr>
                    <th>Symbol</th>
                    <th>Quantity</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(data.positions).map(([sym, qty]) => (
                    <tr key={sym}>
                      <td>{sym}</td>
                      <td>{qty}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}
    </div>
  );
}

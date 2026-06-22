import { getBrokerInfo } from "../api/broker";
import { getPositions, listOrders } from "../api/oms";
import { getRiskState } from "../api/risk";
import { useFetch } from "../hooks/useFetch";

const inr = (n: number) => n.toLocaleString("en-IN", { maximumFractionDigits: 0 });

export function DashboardPage() {
  const risk = useFetch(getRiskState);
  const positions = useFetch(getPositions);
  const orders = useFetch(listOrders);
  const broker = useFetch(getBrokerInfo);

  const openCount = positions.data
    ? Object.values(positions.data.positions).filter((q) => q !== 0).length
    : null;
  const recent = orders.data ? [...orders.data].slice(-5).reverse() : [];

  return (
    <div>
      <h1>Dashboard</h1>
      <p className="sub">Overview of your trading</p>

      {broker.data && (
        <p>
          Broker: <strong>{broker.data.broker}</strong>{" "}
          <span className="badge">{broker.data.dry_run ? "dry-run" : "live"}</span>
        </p>
      )}

      <div className="panel">
        <div className="cards">
          <div className="card">
            <div className="k">Realized P&amp;L</div>
            <div className={"v " + (risk.data && risk.data.realized_pnl >= 0 ? "pos" : "neg")}>
              {risk.data ? `₹${inr(risk.data.realized_pnl)}` : "—"}
            </div>
          </div>
          <div className="card">
            <div className="k">Equity</div>
            <div className="v">{risk.data ? `₹${inr(risk.data.equity)}` : "—"}</div>
          </div>
          <div className="card">
            <div className="k">Open positions</div>
            <div className="v">{openCount ?? "—"}</div>
          </div>
          <div className="card">
            <div className="k">Kill-switch</div>
            <div className={"v " + (risk.data?.kill_switch ? "neg" : "pos")}>
              {risk.data ? (risk.data.kill_switch ? "ON" : "off") : "—"}
            </div>
          </div>
        </div>
        {risk.error && (
          <p className="error">Risk engine unreachable — start it with “python run.py risk”.</p>
        )}
      </div>

      <div className="panel">
        <p className="chart-title">Recent orders</p>
        {orders.error && (
          <p className="error">OMS unreachable — start it with “python run.py oms”.</p>
        )}
        {orders.data &&
          (recent.length === 0 ? (
            <p className="sub">No orders yet.</p>
          ) : (
            <table className="tbl">
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Side</th>
                  <th>Qty</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {recent.map((o) => (
                  <tr key={o.id}>
                    <td>{o.order.symbol}</td>
                    <td>{o.order.side}</td>
                    <td>{o.order.quantity}</td>
                    <td>{o.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ))}
      </div>
    </div>
  );
}

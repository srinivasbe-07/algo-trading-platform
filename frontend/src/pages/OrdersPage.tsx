import { getPositions, listOrders } from "../api/oms";
import { useFetch } from "../hooks/useFetch";

export function OrdersPage() {
  const orders = useFetch(listOrders);
  const positions = useFetch(getPositions);

  return (
    <div>
      <h1>Orders</h1>
      <p className="sub">The order book and current positions</p>

      <div className="panel">
        <p className="chart-title">Orders</p>
        {orders.loading && <p>Loading…</p>}
        {orders.error && <p className="error">{orders.error} — is the OMS API running?</p>}
        {orders.data &&
          (orders.data.length === 0 ? (
            <p className="sub">No orders yet.</p>
          ) : (
            <table className="tbl">
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Side</th>
                  <th>Qty</th>
                  <th>Filled</th>
                  <th>Avg price</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {orders.data.map((o) => (
                  <tr key={o.id}>
                    <td>{o.order.symbol}</td>
                    <td>{o.order.side}</td>
                    <td>{o.order.quantity}</td>
                    <td>{o.filled_quantity}</td>
                    <td>{o.avg_fill_price.toFixed(2)}</td>
                    <td>{o.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ))}
      </div>

      <div className="panel">
        <p className="chart-title">Positions</p>
        {positions.data &&
          (Object.keys(positions.data.positions).length === 0 ? (
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
                {Object.entries(positions.data.positions).map(([sym, qty]) => (
                  <tr key={sym}>
                    <td>{sym}</td>
                    <td>{qty}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ))}
      </div>
    </div>
  );
}

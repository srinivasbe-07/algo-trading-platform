import { getBrokerInfo, listBrokers } from "../api/broker";
import { useFetch } from "../hooks/useFetch";

export function BrokersPage() {
  const info = useFetch(getBrokerInfo);
  const list = useFetch(listBrokers);

  return (
    <div>
      <h1>Brokers</h1>
      <p className="sub">Connected brokers and the active adapter</p>

      <div className="panel">
        {info.error && <p className="error">{info.error} — is the broker-gateway API running?</p>}
        {info.data && (
          <p>
            Active broker: <strong>{info.data.broker}</strong>{" "}
            <span className="badge">{info.data.dry_run ? "dry-run" : "live"}</span>
          </p>
        )}
        {list.data && (
          <table className="tbl">
            <thead>
              <tr>
                <th>Broker</th>
                <th>Active</th>
              </tr>
            </thead>
            <tbody>
              {list.data.available_brokers.map((b) => (
                <tr key={b}>
                  <td>{b}</td>
                  <td>{info.data?.broker === b ? "✓" : ""}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

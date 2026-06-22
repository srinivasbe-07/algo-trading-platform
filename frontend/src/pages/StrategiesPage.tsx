import { useState, type ChangeEvent } from "react";
import { createStrategy, deleteStrategy, listStrategies, type Strategy } from "../api/strategy";
import { DeployDialog } from "../components/DeployDialog";
import { useFetch } from "../hooks/useFetch";

const blank = { name: "", instrument: "NIFTY", fast: 10, slow: 20, quantity: 50 };

export function StrategiesPage() {
  const { data, error, reload } = useFetch(listStrategies);
  const [form, setForm] = useState(blank);
  const [deploying, setDeploying] = useState<Strategy | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);

  const upd =
    (key: keyof typeof blank, numeric = false) =>
    (e: ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
      setForm((f) => ({ ...f, [key]: numeric ? Number(e.target.value) : e.target.value }));

  const onSave = async () => {
    setSaveError(null);
    if (!form.name.trim()) {
      setSaveError("Name is required.");
      return;
    }
    try {
      await createStrategy(form);
      setForm(blank);
      reload();
    } catch (e) {
      setSaveError(e instanceof Error ? e.message : "Save failed");
    }
  };

  const onDelete = async (id: string) => {
    await deleteStrategy(id);
    reload();
  };

  return (
    <div>
      <h1>Strategies</h1>
      <p className="sub">Create a strategy, then deploy it to paper or live</p>

      <div className="panel">
        <div className="form">
          <div className="field">
            <label htmlFor="s-name">Name</label>
            <input id="s-name" type="text" value={form.name} onChange={upd("name")} />
          </div>
          <div className="field">
            <label htmlFor="s-inst">Instrument</label>
            <select id="s-inst" value={form.instrument} onChange={upd("instrument")}>
              <option>NIFTY</option>
              <option>BANKNIFTY</option>
              <option>FINNIFTY</option>
            </select>
          </div>
          <div className="field">
            <label htmlFor="s-fast">Fast MA</label>
            <input
              id="s-fast"
              type="number"
              min={1}
              value={form.fast}
              onChange={upd("fast", true)}
            />
          </div>
          <div className="field">
            <label htmlFor="s-slow">Slow MA</label>
            <input
              id="s-slow"
              type="number"
              min={2}
              value={form.slow}
              onChange={upd("slow", true)}
            />
          </div>
          <div className="field">
            <label htmlFor="s-qty">Quantity</label>
            <input
              id="s-qty"
              type="number"
              min={1}
              value={form.quantity}
              onChange={upd("quantity", true)}
            />
          </div>
          <button onClick={onSave}>Save strategy</button>
        </div>
        {saveError && <p className="error">{saveError}</p>}
      </div>

      <div className="panel">
        <p className="chart-title">Saved strategies</p>
        {error && <p className="error">{error} — start it with “python run.py strategy”.</p>}
        {data &&
          (data.length === 0 ? (
            <p className="sub">No strategies yet — create one above.</p>
          ) : (
            <table className="tbl">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Instrument</th>
                  <th>Signal</th>
                  <th>Qty</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {data.map((s) => (
                  <tr key={s.id}>
                    <td>{s.name}</td>
                    <td>{s.instrument}</td>
                    <td>
                      {s.fast}/{s.slow}
                    </td>
                    <td>{s.quantity}</td>
                    <td style={{ textAlign: "right" }}>
                      <button onClick={() => setDeploying(s)}>Deploy</button>{" "}
                      <button onClick={() => onDelete(s.id)}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ))}
      </div>

      {deploying && <DeployDialog strategy={deploying} onClose={() => setDeploying(null)} />}
    </div>
  );
}

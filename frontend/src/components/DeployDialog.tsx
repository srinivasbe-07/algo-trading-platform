import { useState } from "react";
import { runLive } from "../api/live";
import { runPaper } from "../api/paper";
import type { Strategy } from "../api/strategy";

export function DeployDialog({ strategy, onClose }: { strategy: Strategy; onClose: () => void }) {
  const [mode, setMode] = useState<"paper" | "live">("paper");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const params = { fast: strategy.fast, slow: strategy.slow, quantity: strategy.quantity };

  const onDeploy = async () => {
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      if (mode === "paper") {
        const r = await runPaper(params);
        setResult(`Paper: ${r.orders_filled} filled · return ${r.return_pct.toFixed(2)}%`);
      } else {
        const r = await runLive(params);
        setResult(
          `Live (dry-run) on ${r.broker}: ${r.orders_filled} filled · reconciled ${r.reconciled ? "✓" : "✗"}`,
        );
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Deploy failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Deploy {strategy.name}</h2>
        <p className="sub">Choose how to run it.</p>
        <div style={{ display: "flex", gap: 8, marginBottom: 14 }}>
          <button
            onClick={() => setMode("paper")}
            style={mode === "paper" ? { borderColor: "var(--accent)" } : undefined}
          >
            Paper trade
          </button>
          <button
            onClick={() => setMode("live")}
            style={mode === "live" ? { borderColor: "var(--accent)" } : undefined}
          >
            Live (dry-run)
          </button>
        </div>
        <p className="sub">
          {mode === "paper"
            ? "Simulated broker — no money at risk."
            : "Routes through the broker gateway (dry-run). Broker is set server-side."}
        </p>
        {result && <p className="pos">{result}</p>}
        {error && <p className="error">{error}</p>}
        <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 14 }}>
          <button onClick={onClose}>Close</button>
          <button onClick={onDeploy} disabled={busy} style={{ borderColor: "var(--accent)" }}>
            {busy ? "Deploying…" : "Deploy"}
          </button>
        </div>
      </div>
    </div>
  );
}

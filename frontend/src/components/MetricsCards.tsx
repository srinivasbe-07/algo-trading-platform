import type { Metrics } from "../types";

function Card({ label, value, tone }: { label: string; value: string; tone?: "pos" | "neg" }) {
  return (
    <div className="card">
      <div className="k">{label}</div>
      <div className={`v ${tone ?? ""}`}>{value}</div>
    </div>
  );
}

export function MetricsCards({ metrics }: { metrics: Metrics }) {
  const tone = (n: number): "pos" | "neg" => (n >= 0 ? "pos" : "neg");
  return (
    <div className="cards">
      <Card
        label="Total return"
        value={`${metrics.total_return_pct.toFixed(2)}%`}
        tone={tone(metrics.total_return_pct)}
      />
      <Card label="CAGR" value={`${metrics.cagr_pct.toFixed(2)}%`} tone={tone(metrics.cagr_pct)} />
      <Card label="Sharpe" value={metrics.sharpe.toFixed(2)} />
      <Card label="Sortino" value={metrics.sortino.toFixed(2)} />
      <Card label="Max drawdown" value={`${metrics.max_drawdown_pct.toFixed(2)}%`} tone="neg" />
      <Card label="Win rate" value={`${metrics.win_rate_pct.toFixed(1)}%`} />
      <Card label="Profit factor" value={metrics.profit_factor.toFixed(2)} />
      <Card label="Trades" value={String(metrics.num_trades)} />
      <Card
        label="Final equity"
        value={metrics.final_equity.toLocaleString("en-IN", { maximumFractionDigits: 0 })}
      />
    </div>
  );
}

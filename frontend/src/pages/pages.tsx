import { Placeholder } from "./Placeholder";

export const Dashboard = () => (
  <Placeholder
    title="Dashboard"
    description="P&L, positions, active strategies, equity curve, recent orders."
  />
);
export const Strategies = () => (
  <Placeholder title="Strategies" description="Create, configure, and manage your strategies." />
);
export const Paper = () => (
  <Placeholder
    title="Paper"
    description="Run strategies in real time against a simulated broker."
  />
);
export const Live = () => (
  <Placeholder
    title="Live"
    description="Live (dry-run) sessions through the broker gateway, with reconciliation."
  />
);
export const Simulator = () => (
  <Placeholder
    title="Simulator"
    description="Options chain, greeks, payoff, and the time-step simulator."
  />
);

import { NavLink, Outlet } from "react-router-dom";

const NAV: { to: string; label: string; end?: boolean }[] = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/strategies", label: "Strategies" },
  { to: "/backtest", label: "Backtest" },
  { to: "/paper", label: "Paper" },
  { to: "/live", label: "Live" },
  { to: "/simulator", label: "Simulator" },
  { to: "/risk", label: "Risk" },
  { to: "/orders", label: "Orders" },
  { to: "/brokers", label: "Brokers" },
];

export function AppShell() {
  return (
    <div className="shell">
      <nav className="sidebar" aria-label="Main navigation">
        <div className="brand">AlgoDesk</div>
        {NAV.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) => "navlink" + (isActive ? " active" : "")}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="main-col">
        <header className="topbar">
          <span className="pill">Zerodha · dry-run</span>
          <button className="killbtn" type="button">
            Kill-switch
          </button>
        </header>
        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

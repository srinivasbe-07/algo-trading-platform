import { Route, Routes } from "react-router-dom";
import { AppShell } from "./AppShell";
import { BacktestPage } from "./pages/BacktestPage";
import { BrokersPage } from "./pages/BrokersPage";
import { DashboardPage } from "./pages/DashboardPage";
import { LivePage } from "./pages/LivePage";
import { OrdersPage } from "./pages/OrdersPage";
import { PaperPage } from "./pages/PaperPage";
import { RiskPage } from "./pages/RiskPage";
import { StrategiesPage } from "./pages/StrategiesPage";
import { Simulator } from "./pages/pages";

export function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<DashboardPage />} />
        <Route path="strategies" element={<StrategiesPage />} />
        <Route path="backtest" element={<BacktestPage />} />
        <Route path="paper" element={<PaperPage />} />
        <Route path="live" element={<LivePage />} />
        <Route path="simulator" element={<Simulator />} />
        <Route path="risk" element={<RiskPage />} />
        <Route path="orders" element={<OrdersPage />} />
        <Route path="brokers" element={<BrokersPage />} />
      </Route>
    </Routes>
  );
}

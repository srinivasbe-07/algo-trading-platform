import { Route, Routes } from "react-router-dom";
import { AppShell } from "./AppShell";
import { BacktestPage } from "./pages/BacktestPage";
import { BrokersPage } from "./pages/BrokersPage";
import { LivePage } from "./pages/LivePage";
import { OrdersPage } from "./pages/OrdersPage";
import { PaperPage } from "./pages/PaperPage";
import { RiskPage } from "./pages/RiskPage";
import { Dashboard, Simulator, Strategies } from "./pages/pages";

export function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<Dashboard />} />
        <Route path="strategies" element={<Strategies />} />
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

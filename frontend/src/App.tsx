import { Route, Routes } from "react-router-dom";
import { AppShell } from "./AppShell";
import { BacktestPage } from "./pages/BacktestPage";
import {
  Brokers,
  Dashboard,
  Live,
  Orders,
  Paper,
  Risk,
  Simulator,
  Strategies,
} from "./pages/pages";

export function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<Dashboard />} />
        <Route path="strategies" element={<Strategies />} />
        <Route path="backtest" element={<BacktestPage />} />
        <Route path="paper" element={<Paper />} />
        <Route path="live" element={<Live />} />
        <Route path="simulator" element={<Simulator />} />
        <Route path="risk" element={<Risk />} />
        <Route path="orders" element={<Orders />} />
        <Route path="brokers" element={<Brokers />} />
      </Route>
    </Routes>
  );
}

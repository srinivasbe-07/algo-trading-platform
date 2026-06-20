# frontend

React + Vite + TypeScript dashboard for the Algo Trading Platform (Phase 1).

The first screen is the **Backtest Dashboard**: choose strategy parameters, run a
backtest against the backend, and view metrics, a price chart with buy/sell
markers, and the equity curve. Charts use TradingView's open-source
[Lightweight Charts](https://github.com/tradingview/lightweight-charts).

## Run locally

```bash
# 1. Start the backend (in the repo root, venv active):
uvicorn backtest_engine.main:app --reload --app-dir services/backtest-service

# 2. In another terminal, start the frontend:
cd frontend
npm install
npm run dev
# open http://localhost:5173
```

Configure a different API URL with `VITE_API_BASE` (defaults to http://localhost:8000).

## Structure

```
frontend/
  src/
    api/         API client (talks to the backend)
    components/  MetricsCards, PriceChart, EquityChart
    App.tsx      the dashboard page
    types.ts     shared TypeScript types
```

## Scripts

- `npm run dev` — dev server
- `npm run build` — typecheck + production build
- `npm run typecheck` — types only
- `npm run lint` — ESLint
- `npm test` — Vitest

## Quality gate (CI parity with the backend)

Every push runs the same rigor as the Python services:

- **ESLint** (`npm run lint`) — code quality / likely bugs
- **Prettier** (`npm run format:check`) — consistent formatting
- **TypeScript** (`npm run typecheck`) — types + syntax
- **Build** (`npm run build`) — production bundle compiles
- **Vitest + coverage** (`npm run test:coverage`) — tests with an enforced
  threshold (canvas chart wrappers are excluded as they are not unit-tested)
- **npm audit** — dependency vulnerability scan (fails on high+)

Dependabot also watches the npm dependencies for updates.

Run the whole gate locally:

```bash
npm run lint && npm run format:check && npm run typecheck && npm run build && npm run test:coverage
```

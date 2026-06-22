# AlgoDesk — UX design & UI implementation tracker

_Finalized UX design and the plan to implement it. Mockups live in `docs/ux/`
(open `docs/ux/index.html` in a browser). UI implementation starts the next session._

## 1. Overview

The platform UI is a single React app (the existing `frontend/`) organised as a
left-nav cockpit. Each module is a feature page that talks to backend services
over their APIs. Most screens map onto APIs we have already built; the options
simulator needs a new backend module (see section 4).

Navigation modules: Dashboard · Strategies · Backtest · Paper · Live · Simulator ·
Risk · Orders · Brokers.

## 2. Screens (finalized design)

| # | Screen | File | Purpose |
|---|--------|------|---------|
| 1 | Dashboard | `ux/01-dashboard.html` | Cockpit: P&L, open positions, active strategies, win rate, equity curve, recent orders. Active broker + global kill-switch in the header. |
| 2 | Strategy builder | `ux/02-strategy-builder.html` | Create/configure a strategy (type, instrument, params, position & risk). Actions: Backtest, Save, Deploy. |
| 3 | Deploy dialog | `ux/03-deploy-dialog.html` | Opens from Deploy. Choose Paper or Live, pick a broker from the connected list. Live shows a warning + starts in dry-run until credentials are confirmed. Every order is risk-checked. |
| 4 | Options simulator | `ux/04-options-simulator.html` | Pick from-date + expiry → load option chain with price **and greeks** per strike → select legs. The position area is **tabbed**: **Payoff** (expiry + value-now/T+0 curve) and **Legs** (per-leg table: strike, entry price, current price, current P&L + total). Step through time (Prev/Next at 5m/15m/30m/1h/1d) and both tabs + P&L + DTE + theta update live. |

Screens still to design before/while building: Backtest (restyle of the existing
dashboard into the shell), Paper, Live, Risk panel, Orders/Positions, Brokers,
and the options multi-leg builder (strategy templates: straddle, iron condor…).

## 3. Screen → backend API mapping

| Screen | Backend API | Status |
|--------|-------------|--------|
| Backtest | `backtest-service` `/backtest/detail` | API ready |
| Paper | `paper-trade` `/paper/run` | API ready |
| Live | `live-engine` `/live/run` (+ reconciliation) | API ready |
| Risk | `risk-engine` `/risk/state`, `/risk/kill`, `/risk/reset` | API ready |
| Orders / Positions | `oms` `/orders`, `/positions` | API ready |
| Brokers | `broker-gateway` `/broker/list`, `/broker/info` | API ready |
| Deploy (paper) | paper-trade pipeline | API ready |
| Deploy (live) | live-engine + broker-gateway (adapter = chosen broker) | API ready (dry-run) |
| Strategy builder | new `strategy-service` (registry/persistence) | **to build** |
| Options simulator | new `options` module (chain + Black-Scholes + payoff) | **to build** (see §4) |

## 4. Backend dependencies for the options simulator

The simulator is the one screen that needs significant new backend work:

1. **Option-chain data** — given underlying + expiry, all strikes with call/put
   LTP, IV, OI. For historical "from date" simulation, intraday snapshots of the
   chain over time (vendor: TrueData / GFDL / NSE archives). This historical data
   is the real gating dependency.
2. **Black-Scholes engine** — theoretical price + greeks (Δ, Γ, Θ, Vega), and
   repricing each leg as time steps forward (the Prev/Next simulation).
3. **Multi-leg payoff/simulation math** — combine legs into expiry payoff (exact)
   and T+0 value (Black-Scholes), breakevens, max P&L, net greeks.

The pricing/payoff math is pure, testable computation we can build now (running
on theoretical prices). Real historical option prices come later when a data
source is in place.

## 5. UI implementation plan (phased)

- **UI-0 — App shell & routing.** Left nav, routes, shared layout, theme,
  per-service API client base URLs (API Gateway later). Restyle the existing
  backtest page into the shell.
- **UI-1 — Read-only monitors.** Risk panel, Orders/Positions, Brokers list.
  Pure GET endpoints; quick wins.
- **UI-2 — Run screens.** Paper and Live pages (run + equity curve + summary +
  reconciliation). Strategy builder form.
- **UI-3 — Deploy flow.** Deploy dialog wired to paper/live engines + broker pick.
- **UI-4 — Strategy service.** Backend registry/persistence so saved strategies
  are real; wire builder to it.
- **UI-5 — Options module.** Black-Scholes engine + payoff API + the simulator UI
  (theoretical prices first; historical data later).

Each UI page follows the same quality bar as the rest of the repo: TypeScript,
ESLint, Prettier, Vitest with coverage, all gated in CI.

## 6. Build tracker

| Item | Type | Status | Notes |
|------|------|--------|-------|
| App shell + routing | frontend | ☑ done | UI-0 — React Router, sidebar nav, per-service API config, placeholder pages |
| Dashboard (composed) | frontend | ☑ done | UI-3 — composes risk + OMS + broker (P&L, positions, kill-switch, recent orders) |
| Backtest page (restyle) | frontend | ☑ done | moved into the shell at /backtest |
| Risk panel | frontend | ☑ done | UI-1 — `/risk/state` + kill/reset |
| Orders / Positions | frontend | ☑ done | UI-1 — `/orders`, `/positions` |
| Brokers page | frontend | ☑ done | UI-1 — `/broker/list`, `/broker/info` |
| Paper page | frontend | ☑ done | UI-2 — `/paper/run` + equity curve |
| Live page | frontend | ☑ done | UI-2 — `/live/run` + reconciliation |
| Strategy builder UI | frontend | ☐ todo | needs strategy-service |
| Deploy dialog | frontend | ☐ todo | paper/live + broker |
| strategy-service | backend | ☐ todo | registry/persistence |
| options Black-Scholes engine | backend | ☐ todo | pricing + greeks |
| options payoff/sim API | backend | ☐ todo | multi-leg + time step |
| options simulator UI | frontend | ☐ todo | chain + scrubber |
| historical option-chain data | data | ☐ todo | vendor/source TBD |
| API Gateway (single entry) | backend | ☐ later | unify service URLs |

_Update the Status column (☐ todo → ◐ in progress → ☑ done) as we build._

## 7. Open decisions

- Connectivity: per-service URLs now vs. API Gateway first (recommended: per-service now).
- Options prices: theoretical (Black-Scholes) first; pick a historical data vendor later.
- Strategy persistence store: Postgres (already in docker-compose) when strategy-service is built.

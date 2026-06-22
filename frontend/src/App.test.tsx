import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { App } from "./App";

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  );
}

describe("App shell + routing", () => {
  it("renders the sidebar nav", () => {
    renderAt("/");
    expect(screen.getByRole("navigation", { name: "Main navigation" })).toBeDefined();
    expect(screen.getByRole("link", { name: "Backtest" })).toBeDefined();
  });

  it.each([
    ["/", "Dashboard"],
    ["/strategies", "Strategies"],
    ["/backtest", "Backtest"],
    ["/paper", "Paper"],
    ["/live", "Live"],
    ["/simulator", "Simulator"],
    ["/risk", "Risk"],
    ["/orders", "Orders"],
    ["/brokers", "Brokers"],
  ])("routes %s to its page heading %s", (path, title) => {
    renderAt(path);
    expect(screen.getByRole("heading", { name: title })).toBeDefined();
  });
});

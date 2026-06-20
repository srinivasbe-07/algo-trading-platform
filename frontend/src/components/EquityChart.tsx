import { AreaSeriesPartialOptions, ColorType, createChart, UTCTimestamp } from "lightweight-charts";
import { useEffect, useRef } from "react";
import type { EquityPoint } from "../types";

const toTime = (iso: string): UTCTimestamp => (Date.parse(iso) / 1000) as UTCTimestamp;

const areaOptions: AreaSeriesPartialOptions = {
  lineColor: "#2e75b6",
  topColor: "rgba(46, 117, 182, 0.4)",
  bottomColor: "rgba(46, 117, 182, 0.02)",
  lineWidth: 2,
};

export function EquityChart({ equity }: { equity: EquityPoint[] }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current) return;
    const chart = createChart(ref.current, {
      height: 240,
      layout: { background: { type: ColorType.Solid, color: "#0d1117" }, textColor: "#9aa6b2" },
      grid: { vertLines: { color: "#1c232c" }, horzLines: { color: "#1c232c" } },
      timeScale: { borderColor: "#2b333d" },
      rightPriceScale: { borderColor: "#2b333d" },
    });
    const series = chart.addAreaSeries(areaOptions);
    series.setData(equity.map((e) => ({ time: toTime(e.time), value: e.value })));
    chart.timeScale().fitContent();

    const onResize = () => chart.applyOptions({ width: ref.current?.clientWidth });
    onResize();
    window.addEventListener("resize", onResize);
    return () => {
      window.removeEventListener("resize", onResize);
      chart.remove();
    };
  }, [equity]);

  return <div ref={ref} />;
}

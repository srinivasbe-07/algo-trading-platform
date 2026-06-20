import {
  CandlestickSeriesPartialOptions,
  ColorType,
  createChart,
  IChartApi,
  SeriesMarker,
  Time,
  UTCTimestamp,
} from "lightweight-charts";
import { useEffect, useRef } from "react";
import type { BarPoint, TradePoint } from "../types";

const toTime = (iso: string): UTCTimestamp => (Date.parse(iso) / 1000) as UTCTimestamp;

const candleOptions: CandlestickSeriesPartialOptions = {
  upColor: "#26a69a",
  downColor: "#ef5350",
  borderVisible: false,
  wickUpColor: "#26a69a",
  wickDownColor: "#ef5350",
};

export function PriceChart({ bars, trades }: { bars: BarPoint[]; trades: TradePoint[] }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current) return;
    const chart: IChartApi = createChart(ref.current, {
      height: 320,
      layout: { background: { type: ColorType.Solid, color: "#0d1117" }, textColor: "#9aa6b2" },
      grid: { vertLines: { color: "#1c232c" }, horzLines: { color: "#1c232c" } },
      timeScale: { timeVisible: false, borderColor: "#2b333d" },
      rightPriceScale: { borderColor: "#2b333d" },
    });

    const series = chart.addCandlestickSeries(candleOptions);
    series.setData(
      bars.map((b) => ({
        time: toTime(b.time),
        open: b.open,
        high: b.high,
        low: b.low,
        close: b.close,
      })),
    );

    const markers: SeriesMarker<Time>[] = trades.map((t) => ({
      time: toTime(t.time),
      position: t.side === "BUY" ? "belowBar" : "aboveBar",
      color: t.side === "BUY" ? "#26a69a" : "#ef5350",
      shape: t.side === "BUY" ? "arrowUp" : "arrowDown",
      text: t.side,
    }));
    series.setMarkers(markers);
    chart.timeScale().fitContent();

    const onResize = () => chart.applyOptions({ width: ref.current?.clientWidth });
    onResize();
    window.addEventListener("resize", onResize);
    return () => {
      window.removeEventListener("resize", onResize);
      chart.remove();
    };
  }, [bars, trades]);

  return <div ref={ref} />;
}

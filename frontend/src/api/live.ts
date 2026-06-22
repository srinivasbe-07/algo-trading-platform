import { serviceUrls } from "./config";
import { postJson } from "./http";
import { withParams, type PaperResult, type RunParams } from "./paper";

export interface Discrepancy {
  symbol: string;
  internal: number;
  broker: number;
}

export interface LiveResult extends PaperResult {
  broker: string;
  reconciled: boolean;
  discrepancies: Discrepancy[];
}

export const runLive = (p: RunParams): Promise<LiveResult> =>
  postJson<LiveResult>(withParams(`${serviceUrls.live}/live/run`, p));

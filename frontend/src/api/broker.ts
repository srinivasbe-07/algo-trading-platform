import { serviceUrls } from "./config";
import { getJson } from "./http";

export interface BrokerInfo {
  broker: string;
  dry_run: boolean;
}

export interface BrokerList {
  available_brokers: string[];
}

export const getBrokerInfo = (): Promise<BrokerInfo> =>
  getJson<BrokerInfo>(`${serviceUrls.broker}/broker/info`);

export const listBrokers = (): Promise<BrokerList> =>
  getJson<BrokerList>(`${serviceUrls.broker}/broker/list`);

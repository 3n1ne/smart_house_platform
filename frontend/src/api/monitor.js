import client from "./client";


export function fetchMonitorOverview() {
  return client.get("/monitor/overview");
}

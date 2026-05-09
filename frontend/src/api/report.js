import client from "./client";


export function fetchReportOverview() {
  return client.get("/reports/overview");
}

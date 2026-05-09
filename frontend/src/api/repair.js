import client from "./client";


export function createRepair(data) {
  return client.post("/repairs", data);
}


export function fetchMyRepairs(params) {
  return client.get("/repairs/mine", { params });
}


export function updateRepairStatus(repairId, data) {
  return client.patch(`/repairs/${repairId}/status`, data);
}

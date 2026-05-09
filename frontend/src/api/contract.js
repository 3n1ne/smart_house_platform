import client from "./client";


export function createContract(data) {
  return client.post("/contracts", data);
}


export function fetchMyContracts(params) {
  return client.get("/contracts/mine", { params });
}


export function signContract(contractId) {
  return client.patch(`/contracts/${contractId}/sign`);
}


export function updateContractStatus(contractId, data) {
  return client.patch(`/contracts/${contractId}/status`, data);
}

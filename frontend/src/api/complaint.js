import client from "./client";


export function createComplaint(data) {
  return client.post("/complaints", data);
}


export function fetchMyComplaints(params) {
  return client.get("/complaints/mine", { params });
}


export function updateComplaintStatus(complaintId, data) {
  return client.patch(`/complaints/${complaintId}/status`, data);
}

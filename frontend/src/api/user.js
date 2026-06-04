import client from "./client";


export function fetchUsers(params) {
  return client.get("/users", { params });
}


export function fetchRentalHistory() {
  return client.get("/users/rental-history");
}


export function updateUserStatus(userId, data) {
  return client.patch(`/users/${userId}/status`, data);
}

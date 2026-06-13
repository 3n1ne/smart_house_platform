import client from "./client";


export function fetchUsers(params) {
  return client.get("/users", { params });
}


export function fetchProfile() {
  return client.get("/users/profile");
}


export function updateProfile(data) {
  return client.put("/users/profile", data);
}


export function fetchRentalHistory() {
  return client.get("/users/rental-history");
}


export function updateUserStatus(userId, data) {
  return client.patch(`/users/${userId}/status`, data);
}

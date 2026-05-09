import client from "./client";


export function fetchUsers(params) {
  return client.get("/users", { params });
}


export function updateUserStatus(userId, data) {
  return client.patch(`/users/${userId}/status`, data);
}

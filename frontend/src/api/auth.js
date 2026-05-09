import client from "./client";


export function register(data) {
  return client.post("/auth/register", data);
}


export function login(data) {
  return client.post("/auth/login", data);
}


export function fetchCurrentUser() {
  return client.get("/auth/me");
}


export function logout() {
  return client.post("/auth/logout");
}

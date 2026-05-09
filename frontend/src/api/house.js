import client from "./client";


export function fetchMyHouses(params) {
  return client.get("/houses/mine", { params });
}


export function fetchHouseList(params) {
  return client.get("/houses", { params });
}


export function fetchHouseDetail(houseId) {
  return client.get(`/houses/${houseId}`);
}


export function createHouse(data) {
  return client.post("/houses", data);
}


export function updateHouse(houseId, data) {
  return client.put(`/houses/${houseId}`, data);
}


export function updateHouseStatus(houseId, data) {
  return client.patch(`/houses/${houseId}/status`, data);
}


export function deleteHouse(houseId) {
  return client.delete(`/houses/${houseId}`);
}


export function addHouseMedia(houseId, data) {
  return client.post(`/houses/${houseId}/media`, data);
}


export function deleteHouseMedia(houseId, mediaId) {
  return client.delete(`/houses/${houseId}/media/${mediaId}`);
}

import client from "./client";


export function fetchSearchRegions(params) {
  return client.get("/search/regions", { params });
}


export function fetchSearchLayouts(params) {
  return client.get("/search/layouts", { params });
}


export function fetchSearchRecommendations(params) {
  return client.get("/search/recommendations", { params });
}

import client from "./client";


export function fetchPublishedNews(params) {
  return client.get("/news", { params });
}


export function fetchMyNews(params) {
  return client.get("/news/mine", { params });
}


export function createNews(data) {
  return client.post("/news", data);
}


export function updateNews(newsId, data) {
  return client.put(`/news/${newsId}`, data);
}


export function updateNewsStatus(newsId, data) {
  return client.patch(`/news/${newsId}/status`, data);
}


export function deleteNews(newsId) {
  return client.delete(`/news/${newsId}`);
}

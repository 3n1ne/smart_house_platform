import axios from "axios";


export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";


const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});


client.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    const apiData = error.response?.data;
    const apiMessage = apiData?.message;
    const fallbackMessage = error.message || "请求失败";
    const normalizedError = new Error(apiMessage || fallbackMessage);
    normalizedError.code = apiData?.code;
    normalizedError.errors = apiData?.errors;
    normalizedError.status = error.response?.status;
    return Promise.reject(normalizedError);
  }
);


export default client;

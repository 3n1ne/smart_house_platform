import axios from "axios";


const client = axios.create({
  baseURL: "/api",
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
    const apiMessage = error.response?.data?.message;
    const fallbackMessage = error.message || "请求失败";
    return Promise.reject(new Error(apiMessage || fallbackMessage));
  }
);


export default client;

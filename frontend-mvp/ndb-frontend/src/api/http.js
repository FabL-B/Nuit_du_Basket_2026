import axios from "axios";

export const http = axios.create({
  baseURL: "", // même domaine que l’API => /api/public/...
  timeout: 15_000,
});

function normalizeError(err) {
  if (err.response) {
    return {
      type: "http",
      status: err.response.status,
      data: err.response.data,
      message: `HTTP ${err.response.status}`,
    };
  }
  if (err.request) {
    return { type: "network", message: "Network error" };
  }
  return { type: "unknown", message: err.message || "Unknown error" };
}

http.interceptors.response.use(
  (res) => res,
  (err) => Promise.reject(normalizeError(err))
);

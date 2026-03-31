import axios from "axios";

export const adminHttp = axios.create({
  baseURL: "",
  timeout: 15000,
  withCredentials: true,
  xsrfCookieName: "csrftoken",
  xsrfHeaderName: "X-CSRFToken",
});

function normalizeError(err) {
  if (err.response) {
    return {
      status: err.response.status,
      data: err.response.data,
      message: `HTTP ${err.response.status}`,
    };
  }
  if (err.request) return { message: "Network error" };
  return { message: err.message || "Unknown error" };
}

adminHttp.interceptors.response.use(
  (res) => res,
  (err) => Promise.reject(normalizeError(err))
);

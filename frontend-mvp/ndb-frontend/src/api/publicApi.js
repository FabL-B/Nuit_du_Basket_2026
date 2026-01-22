import { http } from "./http";

export const publicApi = {
  editions: () => http.get("/api/public/editions/").then((r) => r.data),

  planning: (params = {}) =>
    http.get("/api/public/planning/", { params }).then((r) => r.data),

  groupes: (params = {}) =>
    http.get("/api/public/groupes/", { params }).then((r) => r.data),

  groupeDetail: (id) =>
    http.get(`/api/public/groupes/${id}/`).then((r) => r.data),

  groupeClassement: (id) =>
    http.get(`/api/public/groupes/${id}/classement/`).then((r) => r.data),

  terrains: (params = {}) =>
    http.get("/api/public/terrains/", { params }).then((r) => r.data),

  equipeDetail: (id) =>
    http.get(`/api/public/equipes/${id}/`).then((r) => r.data),

  // Optionnel plus tard :
  // equipes: (params={}) => http.get("/api/public/equipes/", {params}).then(r=>r.data),
  // equipeDetail: (id) => http.get(`/api/public/equipes/${id}/`).then(r=>r.data),
  // resultats: (params={}) => http.get("/api/public/resultats/", {params}).then(r=>r.data),
};

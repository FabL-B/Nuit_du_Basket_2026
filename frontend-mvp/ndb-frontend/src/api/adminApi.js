import { adminHttp } from "./adminHttp";

export const adminApi = {
  editions: (params = {}) =>
    adminHttp.get("/api/admin/editions/", { params }).then((r) => r.data),

  createEdition: (payload) =>
    adminHttp.post("/api/admin/editions/", payload).then((r) => r.data),
  
  deleteEquipe: (id) =>
    adminHttp.delete(`/api/admin/equipes/${id}/`).then((r) => r.data),

  createEquipe: (payload) =>
    adminHttp.post("/api/admin/equipes/", payload).then((r) => r.data),

  deleteJoueur: (id) =>
    adminHttp.delete(`/api/admin/joueurs/${id}/`).then((r) => r.data),

  createJoueur: (payload) =>
    adminHttp.post("/api/admin/joueurs/", payload).then((r) => r.data),

  createPhaseGlobale: (payload) =>
    adminHttp.post("/api/admin/phases-globales/", payload).then((r) => r.data),

  phasesGlobales: (params = {}) =>
    adminHttp.get("/api/admin/phases-globales/", { params }).then((r) => r.data),

  sousPhases: (params = {}) =>
    adminHttp.get("/api/admin/sous-phases/", { params }).then((r) => r.data),

  genererSousPhases: (phaseGlobaleId) =>
    adminHttp.post(`/api/admin/phases-globales/${phaseGlobaleId}/generer-sous-phases/`).then((r) => r.data),

  genererGroupesPhase1: (sousPhaseId) =>
    adminHttp.post(`/api/admin/sous-phases/${sousPhaseId}/generer-groupes-phase1/`).then((r) => r.data),

  genererMatchsPhase: (phaseGlobaleId) =>
    adminHttp.post(`/api/admin/phases-globales/${phaseGlobaleId}/generer-matchs/`).then((r) => r.data),
  
  genererPlanningPhase: (phaseGlobaleId) =>
    adminHttp
      .post(`/api/admin/phases-globales/${phaseGlobaleId}/generer-planning/`)
      .then((r) => r.data),

  feuilleMatch: (matchId) =>
    adminHttp.post(`/api/admin/matchs/${matchId}/feuille/`).then((r) => r.data),

  saisirScore: (matchId, payload) =>
    adminHttp.post(`/api/admin/matchs/${matchId}/score/`, payload).then((r) => r.data),

  validerScore: (matchId) =>
    adminHttp.post(`/api/admin/matchs/${matchId}/score/valider/`).then((r) => r.data),

  cloturerPhase: (phaseGlobaleId) =>
    adminHttp.post(`/api/admin/phases-globales/${phaseGlobaleId}/cloturer/`).then((r) => r.data),

  phase2Preview: (phaseGlobaleId) =>
    adminHttp.get(`/api/admin/phases-globales/${phaseGlobaleId}/phase2-preview/`).then((r) => r.data),

  phase2Generer: (phaseGlobaleId) =>
    adminHttp.post(`/api/admin/phases-globales/${phaseGlobaleId}/phase2-generer/`).then((r) => r.data),



  groupes: (params = {}) =>
    adminHttp.get("/api/admin/groupes/", { params }).then((r) => r.data),

  tournois: (params = {}) =>
    adminHttp.get("/api/admin/tournois/", { params }).then((r) => r.data),

  editionStats: (id, params = {}) =>
    adminHttp.get(`/api/admin/editions/${id}/stats/`, { params }).then((r) => r.data),

  planning: (params = {}) =>
    adminHttp.get("/api/admin/planning/", { params }).then((r) => r.data),

  planningGenerer: (payload) =>
    adminHttp.post("/api/admin/planning/generer/", payload).then((r) => r.data),

  matchs: (params = {}) =>
    adminHttp.get("/api/admin/matchs/", { params }).then((r) => r.data),

  matchDetail: (id) =>
    adminHttp.get(`/api/admin/matchs/${id}/`).then((r) => r.data),

  matchScore: (id, payload) =>
    adminHttp.post(`/api/admin/matchs/${id}/score/`, payload).then((r) => r.data),

  matchValiderScore: (id) =>
    adminHttp.post(`/api/admin/matchs/${id}/score/valider/`).then((r) => r.data),

  matchForfait: (id, payload) =>
    adminHttp.post(`/api/admin/matchs/${id}/forfait/`, payload).then((r) => r.data),

  equipes: (params = {}) =>
    adminHttp.get("/api/admin/equipes/", { params }).then((r) => r.data),

  equipeDetail: (id) =>
    adminHttp.get(`/api/admin/equipes/${id}/`).then((r) => r.data),

  equipePatch: (id, payload) =>
    adminHttp.patch(`/api/admin/equipes/${id}/`, payload).then((r) => r.data),

  joueurs: (params = {}) =>
    adminHttp.get("/api/admin/joueurs/", { params }).then((r) => r.data),

  joueurPatch: (id, payload) =>
    adminHttp.patch(`/api/admin/joueurs/${id}/`, payload).then((r) => r.data),

  swapEquipes: (payload) =>
    adminHttp.post("/api/admin/groupes/swap-equipes/", payload).then((r) => r.data),
};

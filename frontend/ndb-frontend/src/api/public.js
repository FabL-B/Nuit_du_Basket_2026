const BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function fetchEditions() {
  const response = await fetch(`${BASE_URL}/api/public/editions/`);

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  return response.json();
}

export async function fetchPlanning(params) {
  const query = new URLSearchParams(params).toString();
  const response = await fetch(
    `${BASE_URL}/api/public/planning/?${query}`
  );

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  return response.json();
}

export async function fetchResultats(params) {
  const query = new URLSearchParams(params).toString();
  const response = await fetch(`${BASE_URL}/api/public/resultats/?${query}`);

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  return response.json();
}

export async function fetchTournois(params) {
  const query = new URLSearchParams(params).toString();
  const res = await fetch(`${BASE_URL}/api/public/tournois/?${query}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function fetchGroupes(params) {
  const query = new URLSearchParams(params).toString();
  const res = await fetch(`${BASE_URL}/api/public/groupes/?${query}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function fetchTerrains(params) {
  const query = new URLSearchParams(params).toString();
  const res = await fetch(`${BASE_URL}/api/public/terrains/?${query}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

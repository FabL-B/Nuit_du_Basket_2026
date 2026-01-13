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

export function cleanParams(obj) {
  const out = {};
  for (const [k, v] of Object.entries(obj || {})) {
    if (v === undefined || v === null || v === "") continue;
    out[k] = v;
  }
  return out;
}

export function getSearchParams(searchParams, keys) {
  const out = {};
  for (const k of keys) {
    const v = searchParams.get(k);
    if (v !== null) out[k] = v;
  }
  return out;
}

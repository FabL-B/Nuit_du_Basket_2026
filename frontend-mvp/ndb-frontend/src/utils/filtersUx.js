export function resetSearchParams(setSp) {
  setSp(new URLSearchParams(), { replace: true });
}

export function removeParam(sp, setSp, key) {
  const next = new URLSearchParams(sp);
  next.delete(key);
  setSp(next, { replace: true });
}
